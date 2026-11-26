from sqlalchemy import select

from core.queueing import submit, result
from core.records import get, insert, need, scan, update
from domain.pieces_model import pieces
from domain.bench_steps_model import bench_steps
from domain.lead_windows_model import lead_windows
from domain.promise_tickets_model import promise_tickets


def receive(conn, user, data):
    from datetime import date
    try:
        arrived = date.fromisoformat(data.arrived).isoformat()
    except ValueError:
        need(False,'签收日需要 YYYY-MM-DD')
    need(0.1 <= data.mass_g <= 40 and 0 <= data.stone_count <= 8,'总重或贵重石数量超出登记范围')
    return insert(conn,pieces,**(data.model_dump() | {'arrived':arrived}))
