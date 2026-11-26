from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.audit import record
from core.db import transaction
from core.records import scan
from domain import bench_steps_service as service
from domain.bench_steps_model import bench_steps
from domain.bench_steps_schemas import AddOperation, WitnessStone

router = APIRouter()

@router.get('/bench_steps')
def list_bench_steps(user=Depends(actor)):
    with transaction() as conn:
        return scan(conn, bench_steps)


@router.post('/bench_steps/add-operation')
def add_operation(data: AddOperation, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.add_operation(conn, user, data)
        record(conn, user, 'bench_steps.add_operation')
        return output


@router.post('/bench_steps/witness-stone')
def witness_stone(data: WitnessStone, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.witness_stone(conn, user, data)
        record(conn, user, 'bench_steps.witness_stone')
        return output
