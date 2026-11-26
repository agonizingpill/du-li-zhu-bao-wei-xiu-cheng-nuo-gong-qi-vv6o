from sqlalchemy import select

from core.queueing import submit, result
from core.records import get, insert, need, scan, update
from domain.pieces_model import pieces
from domain.bench_steps_model import bench_steps
from domain.lead_windows_model import lead_windows
from domain.promise_tickets_model import promise_tickets


def add_operation(conn, user, data):
    piece = get(conn,pieces,data.piece,lock=True)
    need(data.operation in {'镶石拆装','抛光','整形'} and 10 <= data.minutes <= 180,'工序或工台分钟无效')
    need(not any(row['piece'] == piece['code'] and row['operation'] == data.operation for row in scan(conn,bench_steps)),
         '一件饰件的同类工序只能登记一次')
    need(not any(row['piece'] == piece['code'] and row['state'] == '现行' for row in scan(conn,promise_tickets)),
         '已签发的工艺清单不能改动')
    return insert(conn,bench_steps,**data.model_dump())


def witness_stone(conn, user, data):
    row = get(conn,bench_steps,data.task)
    piece = get(conn,pieces,row['piece'],lock=True)
    row = get(conn,bench_steps,data.task,lock=True)
    need(row['operation'] == '镶石拆装' and piece['stone_count'] > 0,'仅贵重石拆装需要双见证')
    need(piece['seal'] == data.seal,'收件封签不一致')
    actor = user['sub']
    need(actor not in {row['first_witness'],row['second_witness']},'同一账号不能作两次见证')
    need(row['second_witness'] is None,'工序已经完成双见证')
    if row['first_witness'] is None:
        return update(conn,bench_steps,data.task,first_witness=actor)
    return update(conn,bench_steps,data.task,second_witness=actor)
