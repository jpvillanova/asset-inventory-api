import os
import tempfile

import pytest

# Configura um banco SQLite temporário ANTES de importar a aplicação,
# para que engine e startup usem esse banco isolado.
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_URL"] = "sqlite:///" + _db_path.replace("\\", "/")
os.environ["SECRET_KEY"] = "test-secret"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, select  # noqa: E402

from app.auth import hash_password  # noqa: E402
from app.database import engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Role, User  # noqa: E402


@pytest.fixture(scope="session")
def client():
    # O "with" dispara os eventos de startup (cria tabelas e semeia o admin).
    with TestClient(app) as test_client:
        with Session(engine) as session:
            if not session.exec(select(User).where(User.username == "auditor")).first():
                session.add(
                    User(
                        username="auditor",
                        hashed_password=hash_password("auditor123"),
                        role=Role.auditor,
                    )
                )
                session.commit()
        yield test_client

    os.close(_db_fd)
    try:
        os.remove(_db_path)
    except OSError:
        pass


def token_for(client: TestClient, username: str, password: str) -> str:
    resp = client.post("/auth/token", data={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture
def admin_headers(client):
    return {"Authorization": f"Bearer {token_for(client, 'admin', 'admin123')}"}


@pytest.fixture
def auditor_headers(client):
    return {"Authorization": f"Bearer {token_for(client, 'auditor', 'auditor123')}"}
