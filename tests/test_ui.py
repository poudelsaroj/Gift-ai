"""UI smoke tests."""

from fastapi.testclient import TestClient


def test_operator_console_renders(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Gift Ingestion Console" in response.text
    assert "/api/v1/sources" in response.text
    assert "Recent Runs" in response.text
    assert "Recent Raw Objects" in response.text
    assert "Normalized Gifts" in response.text
    assert "Normalized Supporters" in response.text
