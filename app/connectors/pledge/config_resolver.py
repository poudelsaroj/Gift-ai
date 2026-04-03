"""Helpers to resolve Pledge config defaults from environment settings."""

from typing import Any

from app.core.config import Settings


def resolve_pledge_config(
    config: dict[str, Any],
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Fill missing Pledge connector config fields from environment settings."""
    settings = settings or Settings()
    resolved = dict(config)

    if not resolved.get("api_base_url"):
        resolved["api_base_url"] = settings.pledge_api_base_url
    if not resolved.get("api_key") and settings.pledge_api_key:
        resolved["api_key"] = settings.pledge_api_key

    resolved.setdefault("page_size", 100)
    resolved.setdefault("request_timeout_seconds", settings.default_request_timeout_seconds)
    resolved.setdefault("auth_header_name", "Authorization")
    resolved.setdefault("auth_scheme", "Bearer")
    resolved.setdefault("donations_endpoint", "/v1/donations")
    resolved.setdefault("organizations_endpoint", "/v1/organizations")
    resolved.setdefault("enabled_object_types", ["donations"])
    return resolved

