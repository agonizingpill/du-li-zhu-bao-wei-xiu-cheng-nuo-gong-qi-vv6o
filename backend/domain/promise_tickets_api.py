from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.audit import record
from core.db import transaction
from core.records import scan
from domain import promise_tickets_service as service
from domain.promise_tickets_model import promise_tickets
from domain.promise_tickets_schemas import IssueTicket, ReviseTicket

router = APIRouter()

@router.get('/promise_tickets')
def list_promise_tickets(user=Depends(actor)):
    with transaction() as conn:
        return scan(conn, promise_tickets)


@router.post('/promise_tickets/issue-ticket')
def issue_ticket(data: IssueTicket, user=Depends(actor)):
    allow(user, ('reviewer',))
    with transaction() as conn:
        output = service.issue_ticket(conn, user, data)
        record(conn, user, 'promise_tickets.issue_ticket')
        return output


@router.post('/promise_tickets/revise-ticket')
def revise_ticket(data: ReviseTicket, user=Depends(actor)):
    allow(user, ('reviewer',))
    with transaction() as conn:
        output = service.revise_ticket(conn, user, data)
        record(conn, user, 'promise_tickets.revise_ticket')
        return output
