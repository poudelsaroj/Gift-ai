"""Source API tests."""

from fastapi.testclient import TestClient


def onecause_payload() -> dict:
    return {
        "source_name": "OneCause Primary",
        "source_system": "onecause",
        "acquisition_mode": "api",
        "auth_type": "api_key",
        "enabled": True,
        "config_json": {
            "api_base_url": "https://api.onecause.example",
            "api_key": "secret-key",
            "organization_id": "org-123",
            "enabled_object_types": ["paid_activities"],
        },
    }


def test_create_source(client: TestClient) -> None:
    response = client.post("/api/v1/sources", json=onecause_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["source_name"] == "OneCause Primary"
    assert body["source_system"] == "onecause"


def test_create_source_uses_env_defaults(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("ONECAUSE_API_BASE_URL", "https://api.onecause.example")
    monkeypatch.setenv("ONECAUSE_API_KEY", "env-secret")
    monkeypatch.setenv("ONECAUSE_ORGANIZATION_ID", "env-org")

    payload = {
        "source_name": "OneCause Env Defaults",
        "source_system": "onecause",
        "acquisition_mode": "api",
        "auth_type": "api_key",
        "enabled": True,
        "config_json": {},
    }
    response = client.post("/api/v1/sources", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["config_json"]["api_base_url"] == "https://api.onecause.example"
    assert body["config_json"]["organization_id"] == "env-org"
    assert body["config_json"]["api_key"] == "***REDACTED***"


def test_create_source_access_token_defaults(client: TestClient, monkeypatch) -> None:
    monkeypatch.delenv("ONECAUSE_API_KEY", raising=False)
    monkeypatch.delenv("ONECAUSE_ORGANIZATION_ID", raising=False)
    monkeypatch.setenv("ONECAUSE_API_BASE_URL", "https://p2p.onecause.com")
    monkeypatch.setenv("ONECAUSE_CLIENT_ID", "client-123")
    monkeypatch.setenv("ONECAUSE_ACCESS_TOKEN", "portal-token")

    payload = {
        "source_name": "OneCause Portal Fallback",
        "source_system": "onecause",
        "acquisition_mode": "api",
        "auth_type": "access_token",
        "enabled": True,
        "config_json": {"auth_mode": "access_token"},
    }
    response = client.post("/api/v1/sources", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["config_json"]["auth_mode"] == "access_token"
    assert body["config_json"]["client_id"] == "client-123"
    assert body["config_json"]["auth_header_name"] == "x-access-token"



def test_update_source(client: TestClient) -> None:
    created = client.post("/api/v1/sources", json=onecause_payload()).json()
    response = client.patch(
        f"/api/v1/sources/{created['id']}",
        json={"source_name": "OneCause Updated", "enabled": False},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["source_name"] == "OneCause Updated"
    assert body["enabled"] is False
