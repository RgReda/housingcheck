from __future__ import annotations

from fastapi.testclient import TestClient

def test_get_indices(client: TestClient):
    response = client.get("/api/indices")
    assert response.status_code == 200
    data = response.json()
    assert any(item["code"] == "MASI" for item in data)


def test_get_valeur_detail(client: TestClient):
    response = client.get("/api/valeurs/CSE:ATW")
    assert response.status_code == 200
    detail = response.json()
    assert detail["ticker"] == "CSE:ATW"
    assert "cours" in detail


def test_create_alert(client: TestClient):
    payload = {
        "cible": "CSE:ATW",
        "condition": "prix",
        "seuil": 450,
        "canal": "email",
        "cooldown_minutes": 30,
    }
    response = client.post("/api/alertes", json=payload)
    assert response.status_code == 200
    created = response.json()
    assert created["cible"] == "CSE:ATW"
