from datetime import date, timedelta
from hashlib import sha256
import json

from core.records import get, insert, need, scan, update
from domain.bench_steps_model import bench_steps
from domain.lead_windows_model import lead_windows
from domain.pieces_model import pieces
from domain.promise_tickets_model import promise_tickets

BENCHES = {'BENCH-A', 'BENCH-B'}


def scope_for(conn,piece):
    operations = [row for row in scan(conn,bench_steps) if row['piece']==piece['code']]
    payload = [[row['code'],row['operation'],row['minutes']] for row in operations]
    return operations,sha256(json.dumps(payload,ensure_ascii=False).encode()).hexdigest()


def issue_ticket(conn,data,previous=None,reason=None):
    # 签票、更正完工日与归档估算共用一把事务锁：并发时先落账的一方算数。
    from domain.completion_service import hold_publication_lock
    hold_publication_lock(conn)
    estimate = get(conn,lead_windows,data.estimate,lock=True)
    piece = get(conn,pieces,estimate['piece'],lock=True)
    operations,signature = scope_for(conn,piece)
    need(signature == estimate['signature'],'工序已经变化，须刷新估算')
    for row in operations:
        if piece['stone_count'] and row['operation']=='镶石拆装':
            first,second = row['first_witness'],row['second_witness']
            need(first and second and first != second,'贵重石拆装需要两名不同账号见证')
    tickets = scan(conn,promise_tickets)
    active = next((row for row in tickets if row['piece']==piece['code'] and row['state']=='现行'),None)
    if previous:
        need(active and active['code']==previous,'请选择该饰件当前承诺票')
        need(reason and len(reason.strip())>=5,'重排须说明具体原因')
    else:
        need(active is None,'饰件已有现行承诺')
    need(not any(row['estimate']==data.estimate for row in tickets),'同一估算凭证只允许签发一次')
    need(data.bench in BENCHES,'请选择存在的金工工台')
    try:
        start = date.fromisoformat(data.start_day)
        # 上限已含完工校准；用校准后的上限折成闭区间，已签日期不变。
        end = start + timedelta(days=estimate['upper_days']-1)
    except (OverflowError, ValueError):
        need(False,'开工日需要合法的 YYYY-MM-DD')
    beginning,ending = start.isoformat(),end.isoformat()
    need(beginning>=piece['arrived'],'开工日不能早于签收日')
    clashes = [row for row in tickets if row['bench']==data.bench and row['state']=='现行'
               and row['code']!=previous and row['start_day']<=ending and row['end_day']>=beginning]
    need(not clashes,'工台日期重叠，请更换日期或工台')
    if active:
        update(conn,promise_tickets,active['code'],state='已修订')
    return insert(conn,promise_tickets,code=data.code,piece=piece['code'],estimate=data.estimate,
                  bench=data.bench,start_day=beginning,end_day=ending,state='现行',previous=previous,reason=reason)
