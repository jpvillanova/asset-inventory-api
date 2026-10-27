"""Modelos de dados (SQLModel = SQLAlchemy + Pydantic)."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class Role(str, Enum):
    """Papéis para controle de acesso (RBAC)."""

    admin = "admin"      # acesso total (criar/editar/remover ativos e usuários)
    auditor = "auditor"  # somente leitura (auditoria/compliance)
    user = "user"        # leitura e criação de ativos


class AssetStatus(str, Enum):
    em_uso = "em_uso"
    em_estoque = "em_estoque"
    manutencao = "manutencao"
    descartado = "descartado"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    role: Role = Field(default=Role.user)


class Asset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    category: str = Field(index=True)
    serial_number: Optional[str] = Field(default=None, index=True)
    status: AssetStatus = Field(default=AssetStatus.em_estoque)
    owner: Optional[str] = Field(default=None, description="Responsável pelo ativo")
    location: Optional[str] = None
    # URL para ativos web (usada pelo security-headers-scanner).
    url: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityScan(SQLModel, table=True):
    """Resultado de uma varredura de segurança de um ativo web.

    Populado pela integração com o `security-headers-scanner`, formando uma
    trilha de postura de segurança ao longo do tempo (útil para GRC).
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    asset_id: int = Field(foreign_key="asset.id", index=True)
    grade: str
    score: int
    max_score: int
    details: str = Field(default="", description="JSON com os achados da varredura")
    scanned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
