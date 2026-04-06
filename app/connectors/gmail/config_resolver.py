"""Helpers to resolve Gmail config defaults from environment settings."""

from __future__ import annotations

from typing import Any

from app.core.config import Settings


def resolve_gmail_config(
    config: dict[str, Any],
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Fill missing Gmail connector config fields from environment settings."""
    settings = settings or Settings()
    resolved = dict(config)

    if not resolved.get("api_base_url"):
        resolved["api_base_url"] = settings.gmail_api_base_url
    if not resolved.get("user_id"):
        resolved["user_id"] = settings.gmail_user_id
    if not resolved.get("access_token") and settings.gmail_access_token:
        resolved["access_token"] = settings.gmail_access_token
    if not resolved.get("refresh_token") and settings.gmail_refresh_token:
        resolved["refresh_token"] = settings.gmail_refresh_token
    if not resolved.get("client_id") and settings.gmail_client_id:
        resolved["client_id"] = settings.gmail_client_id
    if not resolved.get("client_secret") and settings.gmail_client_secret:
        resolved["client_secret"] = settings.gmail_client_secret
    if not resolved.get("token_url"):
        resolved["token_url"] = settings.gmail_token_url
    if not resolved.get("query") and settings.gmail_query:
        resolved["query"] = settings.gmail_query
    if not resolved.get("label_ids") and settings.gmail_label_ids:
        resolved["label_ids"] = [
            item.strip() for item in settings.gmail_label_ids.split(",") if item.strip()
        ]

    resolved.setdefault("page_size", 25)
    resolved.setdefault("max_messages_per_sync", 100)
    resolved.setdefault("process_attachments", True)
    resolved.setdefault("max_attachment_bytes", settings.gmail_attachment_max_bytes)
    resolved.setdefault("body_preference", "plain_text")
    resolved.setdefault(
        "enabled_object_types",
        ["email_message", "email_attachment", "gift_extract"],
    )
    resolved.setdefault(
        "attachment_extensions",
        [".csv", ".xlsx", ".xls", ".pdf", ".txt", ".tsv"],
    )
    return resolved
