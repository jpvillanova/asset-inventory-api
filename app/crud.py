"""Operações de acesso a dados dos ativos e varreduras de segurança."""

import csv
import io
from typing import List, Optional, Tuple

from sqlmodel import Session, func, select

from app.models import Asset, SecurityScan
from app.schemas import AssetCreate, AssetUpdate, SecurityScanCreate


def _filtered(statement, category: Optional[str], q: Optional[str]):
    if category:
        statement = statement.where(Asset.category == category)
    if q:
        statement = statement.where(Asset.name.ilike(f"%{q}%"))  # type: ignore[attr-defined]
    return statement


def list_assets(
    session: Session,
    category: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Tuple[int, List[Asset]]:
    total = session.exec(_filtered(select(func.count(Asset.id)), category, q)).one()
    statement = _filtered(select(Asset), category, q).offset(offset).limit(limit)
    items = list(session.exec(statement).all())
    return total, items


def get_asset(session: Session, asset_id: int) -> Optional[Asset]:
    return session.get(Asset, asset_id)


def create_asset(session: Session, data: AssetCreate) -> Asset:
    asset = Asset.model_validate(data)
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset


def update_asset(session: Session, asset: Asset, data: AssetUpdate) -> Asset:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(asset, field, value)
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset


def delete_asset(session: Session, asset: Asset) -> None:
    session.delete(asset)
    session.commit()


def export_csv(session: Session) -> str:
    """Exporta todos os ativos em CSV (relatório para auditoria/compliance)."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        ["id", "name", "category", "serial_number", "status", "owner", "location", "url"]
    )
    for a in session.exec(select(Asset)).all():
        writer.writerow(
            [a.id, a.name, a.category, a.serial_number or "", a.status.value,
             a.owner or "", a.location or "", a.url or ""]
        )
    return buffer.getvalue()


# --- Varreduras de segurança ----------------------------------------------
def create_scan(session: Session, asset_id: int, data: SecurityScanCreate) -> SecurityScan:
    scan = SecurityScan(asset_id=asset_id, **data.model_dump())
    session.add(scan)
    session.commit()
    session.refresh(scan)
    return scan


def list_scans(session: Session, asset_id: int) -> List[SecurityScan]:
    statement = (
        select(SecurityScan)
        .where(SecurityScan.asset_id == asset_id)
        .order_by(SecurityScan.scanned_at.desc())  # type: ignore[attr-defined]
    )
    return list(session.exec(statement).all())


def latest_scan(session: Session, asset_id: int) -> Optional[SecurityScan]:
    scans = list_scans(session, asset_id)
    return scans[0] if scans else None
