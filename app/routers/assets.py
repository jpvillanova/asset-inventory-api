"""Rotas de ativos, com controle de acesso por papel (RBAC)."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlmodel import Session

from app import crud
from app.auth import get_current_user, require_roles
from app.database import get_session
from app.models import Role, User
from app.schemas import AssetCreate, AssetPage, AssetRead, AssetUpdate

router = APIRouter(prefix="/assets", tags=["assets"])

# Leitura: qualquer usuário autenticado (inclusive auditor).
AnyUser = Depends(get_current_user)
# Escrita: apenas admin.
AdminOnly = Depends(require_roles(Role.admin))


@router.get("", response_model=AssetPage)
def list_assets(
    category: Optional[str] = None,
    q: Optional[str] = Query(default=None, description="Busca por nome (parcial)."),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
    _: User = AnyUser,
):
    total, items = crud.list_assets(session, category=category, q=q, limit=limit, offset=offset)
    return AssetPage(total=total, limit=limit, offset=offset, items=items)


@router.get("/export", response_class=Response)
def export_assets(session: Session = Depends(get_session), _: User = AnyUser):
    csv_data = crud.export_csv(session)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=assets.csv"},
    )


@router.get("/{asset_id}", response_model=AssetRead)
def get_asset(asset_id: int, session: Session = Depends(get_session), _: User = AnyUser):
    asset = crud.get_asset(session, asset_id)
    if not asset:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ativo não encontrado")
    return asset


@router.post("", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(
    data: AssetCreate, session: Session = Depends(get_session), _: User = AdminOnly
):
    return crud.create_asset(session, data)


@router.put("/{asset_id}", response_model=AssetRead)
def update_asset(
    asset_id: int,
    data: AssetUpdate,
    session: Session = Depends(get_session),
    _: User = AdminOnly,
):
    asset = crud.get_asset(session, asset_id)
    if not asset:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ativo não encontrado")
    return crud.update_asset(session, asset, data)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: int, session: Session = Depends(get_session), _: User = AdminOnly
):
    asset = crud.get_asset(session, asset_id)
    if not asset:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ativo não encontrado")
    crud.delete_asset(session, asset)
