"""UI smoke tests."""

from fastapi.testclient import TestClient


def test_operator_console_renders(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Gift Intake Canonical Console" in response.text
    assert "Source Control" in response.text
    assert "Canonical Records" in response.text
    assert "extra_metadata" in response.text
    assert "Active source" in response.text
    assert "Test connection" in response.text
    assert "Run scheduled sources now" in response.text
    assert "Canonical CSV / XLSX upload" in response.text
    assert "Upload and normalize" in response.text
    assert "Every.org dashboard CSV" in response.text
    assert "Integration details appear here" in response.text
