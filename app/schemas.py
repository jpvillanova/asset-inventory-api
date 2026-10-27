"""Schemas de entrada/saída da API (separados das tabelas do banco)."""

from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel

from app.models import AssetStatus, Role


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(SQLModel):
    id: int
    username: str
    role: Role


class AssetCreate(SQLModel):
    name: str
    category: str
    serial_number: Optional[str] = None
    status: AssetStatus = AssetStatus.em_estoque
    owner: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None


class AssetUpdate(SQLModel):
    """Todos os campos opcionais — atualização parcial (PATCH-like)."""

    name: Optional[str] = None
    category: Optional[str] = None
    serial_number: Optional[str] = None
    status: Optional[AssetStatus] = None
    owner: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None


class AssetRead(SQLModel):
    id: int
    name: str
    category: str
    serial_number: Optional[str]
    status: AssetStatus
    owner: Optional[str]
    location: Optional[str]
    url: Optional[str]


class AssetPage(SQLModel):
    """Resposta paginada da listagem de ativos."""

    total: int
    limit: int
    offset: int
    items: List[AssetRead]


class SecurityScanCreate(SQLModel):
    grade: str
    score: int
    max_score: int
    details: Optional[str] = None


class SecurityScanRead(SQLModel):
    id: int
    asset_id: int
    grade: str
    score: int
    max_score: int
    scanned_at: datetime
