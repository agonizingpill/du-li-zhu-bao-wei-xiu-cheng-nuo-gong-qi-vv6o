from datetime import date, datetime, timedelta, timezone

from domain.calibration import build
from domain.completion_model import completions
from domain.pieces_model import pieces
from domain.bench_steps_model import bench_steps
from domain.lead_windows_model import lead_windows
from domain.promise_tickets_model import promise_tickets

# 已完成的历史饰件：每件对应一张（修订链末端的）承诺票和一条完工记录。
# raw_upper_days 是当时签票所依据的模型上限。
HISTORY = [
    ('H-01', 'CARD-H1', 'EST-H1', 6, 'BENCH-A', 8, 7),
    ('H-02', 'CARD-H2', 'EST-H2', 7, 'BENCH-B', 8, 8),
    ('H-03', 'CARD-H3', 'EST-H3', 8, 'BENCH-A', 8, 10),
    ('H-04', 'CARD-H4', 'EST-H4', 9, 'BENCH-B', 8, 11),
    ('H-05', 'CARD-H5', 'EST-H5', 10, 'BENCH-A', 8, 9),
    ('H-06', 'CARD-H6', 'EST-H6', 11, 'BENCH-B', 8, 10),
    ('H-07', 'CARD-H7', 'EST-H7', 6, 'BENCH-A', 8, 8),
]

BASE_MODEL = {'algorithm': 'QuantileRegressor', 'quantiles': [0.2, 0.8], 'seed': 1088,
              'train_rows': 110, 'held_rows': 30, 'coverage': 0.6,
              'p20_pinball': 1.1932, 'p80_pinball': 1.7805, 'crossing_rows': 0,
              'input_sha256': '0000000000000000000000000000000000000000000000000000000000000000'}


def _history_rows():
    pieces_rows, steps_rows, tickets_rows, estimates, done_rows, samples = [], [], [], [], [], []
    start = date(2026, 10, 5)
    for index, (piece, ticket, estimate, backlog, bench, raw, duration) in enumerate(HISTORY):
        completed = start + timedelta(days=index)
        started = completed - timedelta(days=duration - 1)
        pieces_rows.append({'code': piece, 'description': f'历史维修件 {piece}', 'mass_g': round(4 + index * .6, 2),
                            'stone_count': index % 3, 'seal': f'BAG-H{index:02d}', 'arrived': started.isoformat()})
        steps_rows.append({'code': f'OP-H{index + 1}', 'piece': piece, 'operation': '抛光',
                           'minutes': 30 + index * 10, 'first_witness': None, 'second_witness': None})
        tickets_rows.append({'code': ticket, 'piece': piece, 'estimate': estimate, 'bench': bench,
                             'start_day': started.isoformat(), 'end_day': (started + timedelta(days=raw - 1)).isoformat(),
                             'state': '现行', 'previous': None, 'reason': None})
        estimates.append({'code': estimate, 'piece': piece, 'backlog': backlog, 'signature': 'seed',
                          'lower_days': 4, 'upper_days': raw, 'coverage': BASE_MODEL['coverage'],
                          'evidence': dict(BASE_MODEL, lower_days=4, upper_days=raw, raw_upper_days=raw)})
        done_rows.append({'code': f'DONE-H{index + 1}', 'piece': piece, 'ticket': ticket,
                          'completed_day': completed.isoformat(),
                          'recorded_at': datetime.combine(completed, datetime.min.time(), timezone.utc)})
        samples.append({'piece': piece, 'ticket': ticket, 'completed_day': completed.isoformat(),
                        'duration': duration, 'raw_upper_days': raw})
    return pieces_rows, steps_rows, tickets_rows, estimates, done_rows, samples


HISTORY_PIECES, HISTORY_STEPS, HISTORY_TICKETS, HISTORY_ESTIMATES, HISTORY_DONE, HISTORY_SAMPLES = _history_rows()

# EST-001：按本档 7 条完工记录校准后的上限（8 → 11 天）。
SNAPSHOT = build('B6-11', HISTORY_SAMPLES)
EST_001 = dict(BASE_MODEL, lower_days=4, raw_upper_days=8,
               upper_days=max(4, 8 + SNAPSHOT['delta_days']), calibration=SNAPSHOT)

FIXTURES = [
    (pieces, [{'code': 'JW-001',
  'description': '椭圆戒面 · 爪位松动',
  'mass_g': 5.6,
  'stone_count': 1,
  'seal': 'BAG-892A',
  'arrived': '2026-11-24'},
 {'code': 'JW-002',
  'description': '素银细镯 · 单面划痕',
  'mass_g': 9.2,
  'stone_count': 0,
  'seal': 'BAG-893B',
  'arrived': '2026-11-24'}] + HISTORY_PIECES),
    (bench_steps, [{'code': 'OP-001',
  'piece': 'JW-001',
  'operation': '镶石拆装',
  'minutes': 85,
  'first_witness': None,
  'second_witness': None},
 {'code': 'OP-002',
  'piece': 'JW-001',
  'operation': '抛光',
  'minutes': 30,
  'first_witness': None,
  'second_witness': None},
 {'code': 'OP-003',
  'piece': 'JW-002',
  'operation': '抛光',
  'minutes': 45,
  'first_witness': None,
  'second_witness': None}] + HISTORY_STEPS),
    (lead_windows, HISTORY_ESTIMATES + [{'code': 'EST-001', 'piece': 'JW-001', 'backlog': 6, 'signature': 'seed',
                                        'lower_days': 4, 'upper_days': EST_001['upper_days'],
                                        'coverage': BASE_MODEL['coverage'], 'evidence': EST_001}]),
    (promise_tickets, HISTORY_TICKETS),
    (completions, HISTORY_DONE),
]
