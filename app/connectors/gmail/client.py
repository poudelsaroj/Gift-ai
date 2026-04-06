"""HTTP client for Gmail API requests."""

from __future__ import annotations

from typing import Any

import httpx

from app.connectors.gmail.schemas import GmailConfig


class GmailAPIClient:
    """Thin wrapper around Gmail REST calls."""

    def __init__(self, config: GmailConfig) -> None:
        self.config = config
        self.base_url = config.api_base_url.rstrip("/")
        self._access_token = (
            config.access_token.get_secret_value() if config.access_token is not None else None
        )

    def get_profile(self) -> dict[str, Any]:
        """Fetch the authenticated mailbox profile."""
        return self._request_json("GET", f"/users/{self.config.user_id}/profile")

    def list_messages(
        self,
        *,
        page_token: str | None = None,
        max_results: int | None = None,
    ) -> dict[str, Any]:
        """List matching Gmail messages."""
        params: dict[str, Any] = {"maxResults": max_results or self.config.page_size}
        if self.config.query:
            params["q"] = self.config.query
        if self.config.label_ids:
            params["labelIds"] = self.config.label_ids
        if page_token:
            params["pageToken"] = page_token
        return self._request_json("GET", f"/users/{self.config.user_id}/messages", params=params)

    def get_message(self, message_id: str, *, format_: str = "full") -> dict[str, Any]:
        """Fetch a Gmail message payload."""
        return self._request_json(
            "GET",
            f"/users/{self.config.user_id}/messages/{message_id}",
            params={"format": format_},
        )

    def get_attachment(self, message_id: str, attachment_id: str) -> dict[str, Any]:
        """Fetch a Gmail attachment body."""
        return self._request_json(
            "GET",
            f"/users/{self.config.user_id}/messages/{message_id}/attachments/{attachment_id}",
        )

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        content: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        with httpx.Client(timeout=30.0) as client:
            response = self._send_request(
                client,
                method=method,
                path=path,
                params=params,
                content=content,
                token=self._get_access_token(),
            )
            if response.status_code == 401 and self._can_refresh_token():
                self._access_token = None
                response = self._send_request(
                    client,
                    method=method,
                    path=path,
                    params=params,
                    content=content,
                    token=self._get_access_token(),
                )
            response.raise_for_status()
            return response.json()

    def _send_request(
        self,
        client: httpx.Client,
        *,
        method: str,
        path: str,
        token: str,
        params: dict[str, Any] | None = None,
        content: dict[str, Any] | None = None,
    ) -> httpx.Response:
        return client.request(
            method,
            f"{self.base_url}{path}",
            headers={"Authorization": f"Bearer {token}"},
            params=params,
            json=content,
        )

    def _get_access_token(self) -> str:
        if self._access_token:
            return self._access_token

        refresh_token = self._secret_value(self.config.refresh_token)
        client_id = self._secret_value(self.config.client_id)
        client_secret = self._secret_value(self.config.client_secret)
        if not refresh_token or not client_id or not client_secret:
            raise ValueError("No Gmail access token is available.")

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                self.config.token_url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )
            response.raise_for_status()
            payload = response.json()
        token = payload.get("access_token")
        if not isinstance(token, str) or not token:
            raise ValueError("Gmail token refresh did not return access_token.")
        self._access_token = token
        return token

    def _can_refresh_token(self) -> bool:
        return all(
            [
                self._secret_value(self.config.refresh_token),
                self._secret_value(self.config.client_id),
                self._secret_value(self.config.client_secret),
            ]
        )

    def _secret_value(self, value: Any) -> str | None:
        if value is None:
            return None
        return value.get_secret_value()
