from sqlalchemy import select

from core.queueing import submit, result
from core.records import get, insert, need, scan, update
from domain.pieces_model import pieces
from domain.bench_steps_model import bench_steps
from domain.lead_windows_model import lead_windows
from domain.promise_tickets_model import promise_tickets


def fit_window(conn, user, data):
    from domain.jewel_scope import scope_for
    piece = get(conn,pieces,data.piece,lock=True)
    need(0 <= data.backlog <= 24,'当前排队单数须在 0–24')
    detail,signature = scope_for(conn,piece)
    need(detail,'先登记至少一道工序')
    minutes = sum(row['minutes'] for row in detail)
    need(minutes <= 360,'工台分钟超过历史支持范围')
    return submit(user,{'piece':piece['code'],'signature':signature,'minutes':minutes,
                        'mass':piece['mass_g'],'stones':piece['stone_count'],'backlog':data.backlog})


def save_window(conn, user, data):
    from domain.jewel_scope import scope_for
    outcome = result(user,data.token)
    fit_input,model = outcome['input'],outcome['result']
    piece = get(conn,pieces,fit_input['piece'],lock=True)
    _,signature = scope_for(conn,piece)
    need(signature == fit_input['signature'],'工序变更，旧区间无法归档')
    return insert(conn,lead_windows,code=data.code,piece=piece['code'],signature=signature,
                  backlog=fit_input['backlog'],lower_days=model['lower_days'],upper_days=model['upper_days'],
                  coverage=model['coverage'],evidence=model)
