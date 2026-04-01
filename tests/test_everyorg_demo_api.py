"""Every.org key-based demo API tests."""

from __future__ import annotations

import base64
import json

import httpx
from fastapi.testclient import TestClient

from app.core.config import get_settings


def test_everyorg_demo_config_reports_key_availability(
    client: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setenv("EVERYORG_PUBLIC_API_BASE_URL", "https://partners.every.org")
    monkeypatch.setenv("EVERYORG_PUBLIC_KEY", "pk_test_demo")
    monkeypatch.setenv("EVERYORG_PRIVATE_KEY", "sk_test_demo")
    get_settings.cache_clear()

    response = client.get("/api/v1/everyorg/demo/config")

    assert response.status_code == 200
    assert response.json() == {
        "public_key_configured": True,
        "private_key_configured": True,
        "public_api_base_url": "https://partners.every.org",
    }


def test_everyorg_demo_nonprofit_uses_public_key(
    client: TestClient,
    monkeypatch,
) -> None:
    captured: dict[str, str] = {}
    transport = httpx.MockTransport(
        lambda request: (
            captured.update(
                {
                    "path": request.url.path,
                    "apiKey": request.url.params.get("apiKey", ""),
                }
            )
            or httpx.Response(
                200,
                json={"data": {"nonprofit": {"id": "np-1", "name": "Demo Org"}}},
            )
        )
    )
    original_client = httpx.Client

    class MockClient:
        def __init__(self, *args, **kwargs):
            self.client = original_client(transport=transport)

        def __enter__(self):
            return self.client

        def __exit__(self, exc_type, exc, tb):
            self.client.close()

    monkeypatch.setenv("EVERYORG_PUBLIC_KEY", "pk_test_demo")
    get_settings.cache_clear()
    monkeypatch.setattr("app.connectors.everyorg.client.httpx.Client", MockClient)

    response = client.get("/api/v1/everyorg/demo/nonprofit/demo-org")

    assert response.status_code == 200
    assert response.json()["data"]["nonprofit"]["name"] == "Demo Org"
    assert captured == {
        "path": "/v0.2/nonprofit/demo-org",
        "apiKey": "pk_test_demo",
    }


def test_everyorg_demo_create_fundraiser_uses_basic_auth(
    client: TestClient,
    monkeypatch,
) -> None:
    captured: dict[str, str] = {}
    transport = httpx.MockTransport(
        lambda request: (
            captured.update(
                {
                    "path": request.url.path,
                    "authorization": request.headers.get("Authorization", ""),
                    "body": request.content.decode(),
                }
            )
            or httpx.Response(200, json={"fundraiser": {"id": "fr-1"}})
        )
    )
    original_client = httpx.Client

    class MockClient:
        def __init__(self, *args, **kwargs):
            self.client = original_client(
                transport=transport,
                auth=kwargs.get("auth"),
            )

        def __enter__(self):
            return self.client

        def __exit__(self, exc_type, exc, tb):
            self.client.close()

    monkeypatch.setenv("EVERYORG_PUBLIC_KEY", "pk_test_demo")
    monkeypatch.setenv("EVERYORG_PRIVATE_KEY", "sk_test_demo")
    get_settings.cache_clear()
    monkeypatch.setattr("app.connectors.everyorg.client.httpx.Client", MockClient)

    payload = {"nonprofitId": "np-1", "title": "Gift Demo"}
    response = client.post("/api/v1/everyorg/demo/fundraiser", json=payload)

    assert response.status_code == 200
    assert response.json()["fundraiser"]["id"] == "fr-1"
    assert captured["path"] == "/v0.2/fundraiser"
    assert json.loads(captured["body"]) == payload
    scheme, token = captured["authorization"].split(" ", 1)
    assert scheme == "Basic"
    assert base64.b64decode(token).decode() == "pk_test_demo:sk_test_demo"
