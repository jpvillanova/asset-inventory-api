"""Configuração do banco de dados e dependência de sessão."""

import os
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./inventory.db")

# check_same_thread=False é necessário para SQLite com múltiplas requisições.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
