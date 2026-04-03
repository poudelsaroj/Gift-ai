"""Pledge connector tests."""

import httpx

from app.connectors.base.types import FetchRequest
from app.connectors.pledge.connector import PledgeConnector


def base_config() -> dict:
    return {
        "api_base_url": "https://api.pledge.example",
        "api_key": "pledge-secret",
        "page_size": 50,
    }


def handler(request: httpx.Request) -> httpx.Response:
    if request.url.path.endswith("/v1/donations"):
        return httpx.Response(
            200,
            json={
                "page": 1,
                "per": 50,
                "next": None,
                "total_count": 1,
                "results": [
                    {
                        "id": "don_123",
                        "amount": "42.50",
                        "currency": "USD",
                        "created_at": "2026-04-01T12:00:00Z",
                        "payment_method": "card",
                        "reference": "pledge-ref-1",
                        "donor": {
                            "name": "Sam Example",
                            "email": "sam@example.org",
                        },
                        "organization": {
                            "id": "org_1",
                            "name": "Les Turner ALS Foundation",
                            "ngo_id": "36-2916466",
                            "profile_url": "https://www.pledge.to/organizations/36-2916466/les-turner-als-foundation",
                        },
                        "fundraiser": {
                            "id": "fun_1",
                            "title": "Spring Giving",
                        },
                    }
                ],
            },
        )
    if request.url.path.endswith("/v1/organizations"):
        return httpx.Response(200, json={"page": 1, "per": 1, "total_count": 1, "results": []})
    return httpx.Response(404, json={"detail": "not found"})


def test_pledge_test_connection(monkeypatch) -> None:
    transport = httpx.MockTransport(handler)
    original_client = httpx.Client

    class MockClient:
        def __init__(self, *args, **kwargs):
            self.client = original_client(transport=transport)

        def __enter__(self):
            return self.client

        def __exit__(self, exc_type, exc, tb):
            self.client.close()

    monkeypatch.setattr("app.connectors.pledge.client.httpx.Client", MockClient)
    connector = PledgeConnector(base_config())
    response = connector.test_connection()
    assert response["ok"] is True
    assert response["test_endpoint"] == "/v1/donations"
    assert response["total_count"] == 1


def test_pledge_fetch(monkeypatch) -> None:
    transport = httpx.MockTransport(handler)
    original_client = httpx.Client

    class MockClient:
        def __init__(self, *args, **kwargs):
            self.client = original_client(transport=transport)

        def __enter__(self):
            return self.client

        def __exit__(self, exc_type, exc, tb):
            self.client.close()

    monkeypatch.setattr("app.connectors.pledge.client.httpx.Client", MockClient)
    connector = PledgeConnector(base_config())
    result = connector.fetch(FetchRequest(run_type="incremental", trigger_type="manual"))
    assert len(result.items) == 1
    assert result.items[0].object_type == "donations"
    assert result.items[0].external_object_id == "don_123"
    assert result.items[0].external_parent_id == "fun_1"
    assert "donations" in result.cursor_state
