"""Low-level OneCause API client."""

from typing import Any

import httpx

from app.connectors.onecause.schemas import OneCauseConfig


class OneCauseAPIClient:
    """Thin wrapper around httpx for OneCause requests."""

    def __init__(self, config: OneCauseConfig) -> None:
        self.config = config

    def _headers(self) -> dict[str, str]:
        headers = {self.config.auth_header_name: self.config.api_key.get_secret_value()}
        if self.config.org_id_header_name:
            headers[self.config.org_id_header_name] = self.config.organization_id
        return headers

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Perform a GET request and return parsed JSON."""
        url = f"{self.config.api_base_url.rstrip('/')}{endpoint}"
        with httpx.Client(timeout=self.config.request_timeout_seconds) as client:
            response = client.get(url, headers=self._headers(), params=params)
            response.raise_for_status()
            return response.json()

