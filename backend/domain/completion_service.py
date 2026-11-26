from collections import defaultdict
from datetime import date, datetime, timezone
import json

from sqlalchemy import select, text

from core.queueing import broker
from core.records import get, insert, need, scan, update
from domain.calibration import band_of, build
from domain.completion_model import completions
from domain.lead_windows_model import lead_windows
from domain.promise_tickets_model import promise_tickets

PUBLICATION_LOCK = 108812


def hold_publication_lock(conn):
    """签票、更正完工日与归档估算共用一把锁：并发时先落账的一方算数。"""
    conn.execute(text(f'SELECT pg_advisory_xact_lock({PUBLICATION_LOCK})'))


def _chain_depth(ticket, index):
    depth, seen = 0, {ticket['code']}
    current = ticket
    while current['previous'] and current['previous'] in index and current['previous'] not in seen:
        seen.add(current['previous'])
        current = index[current['previous']]
        depth += 1
    return depth


def last_tickets(tickets):
    """每件饰件修订链的末端票；同件只认这一张。"""
    index = {ticket['code']: ticket for ticket in tickets}
    grouped = defaultdict(list)
    for ticket in tickets:
        grouped[ticket['piece']].append(ticket)

    def key(ticket):
        # 现行票就是链的末端；理论上每件至多一张，缺现行票时退回按链深度取。
        return (ticket['state'] == '现行', _chain_depth(ticket, index), ticket['code'])

    return {piece: max(rows, key=key) for piece, rows in grouped.items()}


def _duration(ticket, completed_day):
    start = date.fromisoformat(ticket['start_day'])
    done = date.fromisoformat(completed_day)
    return (done - start).days + 1


def raw_upper(estimate):
    evidence = estimate['evidence'] or {}
    return int(evidence.get('raw_upper_days', evidence.get('upper_days', estimate['upper_days'])))


def model_raw_upper(model):
    """worker 结果里保留的模型原始上限；避免二次叠加校准偏移。"""
    return int(model.get('raw_upper_days', model.get('upper_days') or 0))


def samples(conn):
    """所有可用于校准的完工样本（每件饰件只取最后一张票）。"""
    tickets = scan(conn, promise_tickets)
    estimates = {row['code']: row for row in scan(conn, lead_windows)}
    recorded = {row['ticket']: row for row in scan(conn, completions)}
    rows = []
    for piece, ticket in last_tickets(tickets).items():
        record = recorded.get(ticket['code'])
        estimate = estimates.get(ticket['estimate'])
        if record is None or estimate is None:
            continue
        try:
            duration = _duration(ticket, record['completed_day'])
        except ValueError:
            continue
        rows.append({'piece': piece, 'ticket': ticket['code'], 'completed_day': record['completed_day'],
                     'duration': duration, 'raw_upper_days': raw_upper(estimate),
                     'backlog': estimate['backlog'], 'bucket': band_of(estimate['backlog'])})
    return rows


def snapshot_for(conn, backlog):
    bucket = band_of(backlog)
    return build(bucket, [row for row in samples(conn) if row['bucket'] == bucket])


def calibrated_upper(estimate, snapshot):
    """在原上限（模型原始输出）上叠加本档偏移，且不低于 P20。"""
    return max(estimate['lower_days'], raw_upper(estimate) + snapshot['delta_days'])


def calibrated_result(conn, fit_input, model):
    """把原模型结果与本档完工校准合并；只校准上限。归档时按最新样本重算偏移。"""
    snapshot = snapshot_for(conn, fit_input['backlog'])
    evidence = dict(model)
    raw = model_raw_upper(model)
    evidence['raw_upper_days'] = raw
    evidence['upper_days'] = max(model['lower_days'], raw + snapshot['delta_days'])
    evidence['calibration'] = snapshot
    return evidence, snapshot


def _bucket_tokens(bucket):
    """本档仍在排队的计算令牌，补录/更正后一律作废。"""
    tokens = []
    for key in broker.scan_iter(match='compute:*', count=200):
        raw = broker.get(key)
        if raw is None:
            continue
        try:
            record = json.loads(raw)
        except ValueError:
            continue
        if record.get('status') != 'queued':
            continue
        backlog = (record.get('input') or {}).get('backlog')
        if backlog is None or band_of(backlog) != bucket:
            continue
        record['status'] = 'stale'
        record['detail'] = '本档完工记录已变更，请重新估算'
        broker.set(key, json.dumps(record), ex=86400)
        tokens.append(key.removeprefix('compute:'))
    return tokens


def invalidate_unsigned(conn, bucket):
    """本档已归档但尚未签票的估算：就地按最新完工记录重算。"""
    signed = {row['estimate'] for row in scan(conn, promise_tickets)}
    recomputed = []
    for estimate in scan(conn, lead_windows):
        if estimate['code'] in signed or band_of(estimate['backlog']) != bucket:
            continue
        evidence = dict(estimate['evidence'] or {})
        snapshot = snapshot_for(conn, estimate['backlog'])
        upper = calibrated_upper(estimate, snapshot)
        evidence['raw_upper_days'] = raw_upper(estimate)
        evidence['upper_days'] = upper
        evidence['calibration'] = snapshot
        update(conn, lead_windows, estimate['code'], upper_days=upper, evidence=evidence)
        recomputed.append(estimate['code'])
    return recomputed


def _resolve_ticket(conn, data):
    last = last_tickets(scan(conn, promise_tickets)).get(data.piece)
    if data.ticket:
        ticket = get(conn, promise_tickets, data.ticket, lock=True)
        need(ticket['piece'] == data.piece, '承诺票不属于该饰件')
        # 同件只认最后一张票：被修订取代的旧票不再承接完工记录。
        need(last is not None and last['code'] == ticket['code'], '该承诺票已被后续票取代，请登记最后一张')
        return ticket
    need(last is not None, '该饰件没有可登记的承诺票')
    return get(conn, promise_tickets, last['code'], lock=True)


def _completion_code(conn, piece, ticket_code):
    """每张票一条完工记录；未指定编号时按票号稳定生成，补录与更正都落在同一条。"""
    for row in scan(conn, completions):
        if row['ticket'] == ticket_code:
            return row['code']
    return f'DONE-{ticket_code}'


def record_completion(conn, user, data):
    hold_publication_lock(conn)
    ticket = _resolve_ticket(conn, data)
    try:
        completed = date.fromisoformat(data.completed_day).isoformat()
    except ValueError:
        need(False, '完工日需要合法的 YYYY-MM-DD')
    need(completed >= ticket['start_day'], '完工日不能早于开工日')
    code = data.code or _completion_code(conn, ticket['piece'], ticket['code'])
    existing = conn.execute(select(completions).where(completions.c.code == code)).mappings().first()
    if existing:
        need(existing['ticket'] == ticket['code'] and existing['piece'] == ticket['piece'],
             '更正须沿用原承诺票和饰件')
        update(conn, completions, code, completed_day=completed,
               recorded_at=datetime.now(timezone.utc))
        action = '更正'
    else:
        need(not any(row['ticket'] == ticket['code'] for row in scan(conn, completions)),
             '该承诺票已有完工记录，请直接更正')
        insert(conn, completions, code=code, piece=ticket['piece'], ticket=ticket['code'],
               completed_day=completed, recorded_at=datetime.now(timezone.utc))
        action = '补录'
    estimate = get(conn, lead_windows, ticket['estimate'])
    bucket = band_of(estimate['backlog'])
    stale_tokens = _bucket_tokens(bucket)
    recomputed = invalidate_unsigned(conn, bucket)
    return {'code': code, 'piece': ticket['piece'], 'ticket': ticket['code'],
            'completed_day': completed, 'action': action, 'bucket': bucket,
            'stale_tokens': len(stale_tokens), 'recomputed_estimates': recomputed}


def ticket_traces(conn):
    """承诺票页面：每张票签发时所用估算的分档、样本与上限。"""
    estimates = {row['code']: row for row in scan(conn, lead_windows)}
    traces = []
    for ticket in scan(conn, promise_tickets):
        estimate = estimates.get(ticket['estimate'])
        if estimate is None:
            continue
        evidence = estimate['evidence'] or {}
        calibration = evidence.get('calibration') or {}
        traces.append({
            'ticket': ticket['code'], 'piece': ticket['piece'], 'estimate': ticket['estimate'],
            'bench': ticket['bench'], 'state': ticket['state'],
            'start_day': ticket['start_day'], 'end_day': ticket['end_day'],
            'lower_days': estimate['lower_days'], 'upper_days': estimate['upper_days'],
            'raw_upper_days': raw_upper(estimate),
            'bucket': calibration.get('bucket') or band_of(estimate['backlog']),
            'delta_days': calibration.get('delta_days', 0),
            'applied': calibration.get('applied', False),
            'reason': calibration.get('reason', '未使用完工校准'),
            'sample_count': calibration.get('sample_count', 0),
            'calibration_rows': calibration.get('calibration_rows', 0),
            'validation_rows': calibration.get('validation_rows', 0),
            'old_overrun': calibration.get('old_overrun'),
            'new_overrun': calibration.get('new_overrun'),
            'old_pinball': calibration.get('old_pinball'),
            'new_pinball': calibration.get('new_pinball'),
            'samples': calibration.get('samples', []),
        })
    return traces


def finalize(conn, fit_input, model):
    """worker 计算完成后落库前调用：按提交时的完工样本校准，样本已变则作废。"""
    hold_publication_lock(conn)
    snapshot = snapshot_for(conn, fit_input['backlog'])
    if fit_input.get('calibration_key') and fit_input['calibration_key'] != snapshot['key']:
        return None, '本档完工记录已变更，请重新估算'
    evidence = dict(model)
    raw = model_raw_upper(model)
    evidence['raw_upper_days'] = raw
    evidence['upper_days'] = max(model['lower_days'], raw + snapshot['delta_days'])
    evidence['calibration'] = snapshot
    return evidence, None
