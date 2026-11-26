from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.audit import record
from core.db import transaction
from core.records import scan
from domain import completion_service as service
from domain.completion_model import completions
from domain.completion_schemas import RecordCompletion

router = APIRouter()

@router.get('/completions')
def list_completions(user=Depends(actor)):
    with transaction() as conn:
        return scan(conn, completions)


@router.post('/completions/record')
def record_completion(data: RecordCompletion, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.record_completion(conn, user, data)
        record(conn, user, 'completions.record')
        return output
