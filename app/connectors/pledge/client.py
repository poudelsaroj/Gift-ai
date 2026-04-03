"""Low-level Pledge API client."""

from typing import Any

import httpx

from app.connectors.pledge.schemas import PledgeConfig


class PledgeAPIClient:
    """Thin wrapper around httpx for Pledge requests."""

    def __init__(self, config: PledgeConfig) -> None:
        self.config = config

    def _headers(self) -> dict[str, str]:
        token = self.config.api_key.get_secret_value()
        if self.config.auth_scheme:
            return {self.config.auth_header_name: f"{self.config.auth_scheme} {token}"}
        return {self.config.auth_header_name: token}

    def get(self, endpoint_or_url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Perform a GET request and return parsed JSON."""
        if endpoint_or_url.startswith("http://") or endpoint_or_url.startswith("https://"):
            url = endpoint_or_url
        else:
            url = f"{self.config.api_base_url.rstrip('/')}{endpoint_or_url}"
        with httpx.Client(timeout=self.config.request_timeout_seconds) as client:
            response = client.get(url, headers=self._headers(), params=params)
            response.raise_for_status()
            return response.json()

