"""Testes de API: autenticação, CRUD e regras de RBAC."""


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_login_wrong_password(client):
    resp = client.post("/auth/token", data={"username": "admin", "password": "errado"})
    assert resp.status_code == 401


def test_list_requires_authentication(client):
    assert client.get("/assets").status_code == 401


def test_admin_can_create_asset(client, admin_headers):
    payload = {"name": "Notebook Dell", "category": "notebook", "serial_number": "SN-001"}
    resp = client.post("/assets", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Notebook Dell"
    assert body["status"] == "em_estoque"
    assert "id" in body


def test_auditor_can_read_but_not_write(client, auditor_headers):
    # leitura permitida
    assert client.get("/assets", headers=auditor_headers).status_code == 200
    # escrita bloqueada (403)
    resp = client.post(
        "/assets",
        json={"name": "Switch", "category": "rede"},
        headers=auditor_headers,
    )
    assert resp.status_code == 403


def test_update_and_delete_flow(client, admin_headers):
    created = client.post(
        "/assets",
        json={"name": "Monitor LG", "category": "monitor"},
        headers=admin_headers,
    ).json()
    asset_id = created["id"]

    # update parcial
    upd = client.put(
        f"/assets/{asset_id}",
        json={"status": "em_uso", "owner": "joao"},
        headers=admin_headers,
    )
    assert upd.status_code == 200
    assert upd.json()["status"] == "em_uso"
    assert upd.json()["owner"] == "joao"

    # delete
    assert client.delete(f"/assets/{asset_id}", headers=admin_headers).status_code == 204
    # agora deve dar 404
    assert client.get(f"/assets/{asset_id}", headers=admin_headers).status_code == 404


def test_filter_by_category(client, admin_headers):
    client.post(
        "/assets",
        json={"name": "Impressora", "category": "impressora"},
        headers=admin_headers,
    )
    resp = client.get("/assets", params={"category": "impressora"}, headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    assert all(a["category"] == "impressora" for a in body["items"])
