"""HTTP client for Every.org API."""

from __future__ import annotations

import json
from typing import Any

import httpx

from app.connectors.everyorg.schemas import EveryOrgConfig


class EveryOrgAPIClient:
    """Small client for Every.org API requests."""

    def __init__(self, config: EveryOrgConfig) -> None:
        self.config = config
        self.base_url = config.public_api_base_url.rstrip("/")

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Issue a GET request and return parsed JSON."""
        if not self.config.public_key:
            raise ValueError("EVERYORG_PUBLIC_KEY is required for public Every.org requests.")
        query = {"apiKey": self.config.public_key}
        if params:
            query.update(params)
        with httpx.Client(timeout=30.0) as client:
            response = client.get(f"{self.base_url}{path}", params=query)
            response.raise_for_status()
            return response.json()

    def post_private(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Issue a private-key-authenticated POST request and return parsed JSON."""
        if not self.config.public_key or not self.config.private_key:
            raise ValueError(
                "EVERYORG_PUBLIC_KEY and EVERYORG_PRIVATE_KEY "
                "are required for private Every.org requests."
            )
        with httpx.Client(
            timeout=30.0,
            auth=(self.config.public_key, self.config.private_key),
        ) as client:
            response = client.post(
                f"{self.base_url}{path}",
                headers={"Content-Type": "application/json"},
                content=json.dumps(payload),
            )
            response.raise_for_status()
            return response.json()
