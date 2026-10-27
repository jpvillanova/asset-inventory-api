"""Ponto de entrada da API de Inventário de Ativos de TI."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session, select

from app.auth import hash_password
from app.database import create_db_and_tables, engine
from app.models import Role, User
from app.routers import assets, auth, scans


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    seed_admin()
    yield


app = FastAPI(
    title="Asset Inventory API",
    description="API REST para inventário de ativos de TI com autenticação JWT e RBAC.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(assets.router)
app.include_router(scans.router)


def seed_admin() -> None:
    """Cria um usuário admin inicial se nenhum usuário existir."""
    with Session(engine) as session:
        if session.exec(select(User)).first():
            return
        admin = User(
            username=os.getenv("ADMIN_USERNAME", "admin"),
            hashed_password=hash_password(os.getenv("ADMIN_PASSWORD", "admin123")),
            role=Role.admin,
        )
        session.add(admin)
        session.commit()


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}
