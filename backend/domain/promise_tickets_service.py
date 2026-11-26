from sqlalchemy import select

from core.queueing import submit, result
from core.records import get, insert, need, scan, update
from domain.pieces_model import pieces
from domain.bench_steps_model import bench_steps
from domain.lead_windows_model import lead_windows
from domain.promise_tickets_model import promise_tickets


def issue_ticket(conn, user, data):
    from domain.jewel_scope import issue_ticket
    return issue_ticket(conn,data)


def revise_ticket(conn, user, data):
    from domain.jewel_scope import issue_ticket
    return issue_ticket(conn,data,previous=data.previous,reason=data.reason)
