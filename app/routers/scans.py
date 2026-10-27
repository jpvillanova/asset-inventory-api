"""Rotas de varreduras de segurança por ativo.

Formam a ponte com o `security-headers-scanner`: o scanner envia (POST) o
resultado da auditoria de cabeçalhos, e a API guarda o histórico de postura.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app import crud
from app.auth import get_current_user, require_roles
from app.database import get_session
from app.models import Role, User
from app.schemas import SecurityScanCreate, SecurityScanRead

router = APIRouter(prefix="/assets/{asset_id}/scans", tags=["security-scans"])

AnyUser = Depends(get_current_user)
AdminOnly = Depends(require_roles(Role.admin))


def _ensure_asset(session: Session, asset_id: int):
    asset = crud.get_asset(session, asset_id)
    if not asset:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ativo não encontrado")
    return asset


@router.post("", response_model=SecurityScanRead, status_code=status.HTTP_201_CREATED)
def create_scan(
    asset_id: int,
    data: SecurityScanCreate,
    session: Session = Depends(get_session),
    _: User = AdminOnly,
):
    _ensure_asset(session, asset_id)
    return crud.create_scan(session, asset_id, data)


@router.get("", response_model=List[SecurityScanRead])
def list_scans(asset_id: int, session: Session = Depends(get_session), _: User = AnyUser):
    _ensure_asset(session, asset_id)
    return crud.list_scans(session, asset_id)


@router.get("/latest", response_model=SecurityScanRead)
def latest_scan(asset_id: int, session: Session = Depends(get_session), _: User = AnyUser):
    _ensure_asset(session, asset_id)
    scan = crud.latest_scan(session, asset_id)
    if not scan:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nenhuma varredura registrada")
    return scan
