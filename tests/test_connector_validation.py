"""Connector validation tests."""

import pytest

from app.connectors.onecause.connector import OneCauseConnector


def test_onecause_validation_requires_required_fields() -> None:
    with pytest.raises(Exception):
        OneCauseConnector({"api_base_url": "https://api.onecause.example"}).validate_config()

