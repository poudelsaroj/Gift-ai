"""Helpers to resolve Every.org config defaults from environment settings."""

from typing import Any

from app.core.config import Settings


def resolve_everyorg_config(
    config: dict[str, Any],
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Fill missing Every.org connector config fields from environment settings."""
    settings = settings or Settings()
    resolved = dict(config)

    if not resolved.get("public_api_base_url"):
        resolved["public_api_base_url"] = settings.everyorg_public_api_base_url
    if not resolved.get("public_key") and settings.everyorg_public_key:
        resolved["public_key"] = settings.everyorg_public_key
    if not resolved.get("private_key") and settings.everyorg_private_key:
        resolved["private_key"] = settings.everyorg_private_key
    if not resolved.get("webhook_token") and settings.everyorg_webhook_token:
        resolved["webhook_token"] = settings.everyorg_webhook_token
    if not resolved.get("webhook_kind") and settings.everyorg_webhook_kind:
        resolved["webhook_kind"] = settings.everyorg_webhook_kind
    if not resolved.get("nonprofit_slug") and settings.everyorg_nonprofit_slug:
        resolved["nonprofit_slug"] = settings.everyorg_nonprofit_slug

    return resolved
