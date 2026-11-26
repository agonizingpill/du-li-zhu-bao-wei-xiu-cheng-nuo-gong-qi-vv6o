from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.audit import record
from core.db import transaction
from core.records import scan
from domain import lead_windows_service as service
from domain.lead_windows_model import lead_windows
from domain.lead_windows_schemas import FitWindow, SaveWindow

router = APIRouter()

@router.get('/lead_windows')
def list_lead_windows(user=Depends(actor)):
    with transaction() as conn:
        return scan(conn, lead_windows)


@router.post('/lead_windows/fit-window')
def fit_window(data: FitWindow, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.fit_window(conn, user, data)
        record(conn, user, 'lead_windows.fit_window')
        return output


@router.post('/lead_windows/save-window')
def save_window(data: SaveWindow, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.save_window(conn, user, data)
        record(conn, user, 'lead_windows.save_window')
        return output
