"""Testes das varreduras de segurança, paginação, busca e export CSV."""

import json


def _create_web_asset(client, admin_headers, name="Site Corporativo"):
    resp = client.post(
        "/assets",
        json={"name": name, "category": "web", "url": "https://example.com"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def test_scan_lifecycle(client, admin_headers):
    asset_id = _create_web_asset(client, admin_headers)

    # admin registra uma varredura
    payload = {
        "grade": "B",
        "score": 14,
        "max_score": 18,
        "details": json.dumps({"missing": ["Content-Security-Policy"]}),
    }
    created = client.post(f"/assets/{asset_id}/scans", json=payload, headers=admin_headers)
    assert created.status_code == 201
    assert created.json()["grade"] == "B"

    # histórico
    history = client.get(f"/assets/{asset_id}/scans", headers=admin_headers)
    assert history.status_code == 200
    assert len(history.json()) == 1

    # última varredura
    latest = client.get(f"/assets/{asset_id}/scans/latest", headers=admin_headers)
    assert latest.status_code == 200
    assert latest.json()["score"] == 14


def test_auditor_cannot_push_scan(client, admin_headers, auditor_headers):
    asset_id = _create_web_asset(client, admin_headers, name="Portal")
    resp = client.post(
        f"/assets/{asset_id}/scans",
        json={"grade": "A", "score": 18, "max_score": 18},
        headers=auditor_headers,
    )
    assert resp.status_code == 403


def test_scan_on_missing_asset_404(client, admin_headers):
    resp = client.post(
        "/assets/999999/scans",
        json={"grade": "A", "score": 18, "max_score": 18},
        headers=admin_headers,
    )
    assert resp.status_code == 404


def test_pagination(client, admin_headers):
    for i in range(5):
        client.post(
            "/assets",
            json={"name": f"Cabo {i}", "category": "cabo"},
            headers=admin_headers,
        )
    resp = client.get("/assets", params={"category": "cabo", "limit": 2}, headers=admin_headers)
    body = resp.json()
    assert body["total"] == 5
    assert len(body["items"]) == 2
    assert body["limit"] == 2


def test_search_by_name(client, admin_headers):
    client.post(
        "/assets",
        json={"name": "Servidor Rack XYZ", "category": "servidor"},
        headers=admin_headers,
    )
    resp = client.get("/assets", params={"q": "rack xyz"}, headers=admin_headers)
    assert resp.json()["total"] >= 1


def test_csv_export(client, admin_headers):
    resp = client.get("/assets/export", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert resp.text.splitlines()[0].startswith("id,name,category")
