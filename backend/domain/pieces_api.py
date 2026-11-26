from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.audit import record
from core.db import transaction
from core.records import scan
from domain import pieces_service as service
from domain.pieces_model import pieces
from domain.pieces_schemas import Receive

router = APIRouter()

@router.get('/pieces')
def list_pieces(user=Depends(actor)):
    with transaction() as conn:
        return scan(conn, pieces)


@router.post('/pieces/receive')
def receive(data: Receive, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.receive(conn, user, data)
        record(conn, user, 'pieces.receive')
        return output
