"""Helpers to resolve OneCause config defaults from environment settings."""

from typing import Any

from app.core.config import Settings


def resolve_onecause_config(
    config: dict[str, Any],
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Fill missing OneCause connector config fields from environment settings."""
    settings = settings or Settings()
    resolved = dict(config)
    auth_mode = resolved.get("auth_mode")
    if not auth_mode:
        auth_mode = "api_key" if settings.onecause_api_key else "access_token"
        resolved["auth_mode"] = auth_mode

    if not resolved.get("api_base_url"):
        resolved["api_base_url"] = settings.onecause_api_base_url or settings.onecause_default_base_url
    if auth_mode == "api_key" and not resolved.get("api_key") and settings.onecause_api_key:
        resolved["api_key"] = settings.onecause_api_key
    if auth_mode == "access_token" and not resolved.get("api_key") and settings.onecause_access_token:
        resolved["api_key"] = settings.onecause_access_token
    if auth_mode == "api_key" and not resolved.get("organization_id") and settings.onecause_organization_id:
        resolved["organization_id"] = settings.onecause_organization_id
    if auth_mode == "access_token" and not resolved.get("client_id") and settings.onecause_client_id:
        resolved["client_id"] = settings.onecause_client_id
    if auth_mode == "access_token" and not resolved.get("organization_id") and settings.onecause_client_id:
        resolved["organization_id"] = settings.onecause_client_id
    if auth_mode == "access_token" and not resolved.get("challenge_id") and settings.onecause_challenge_id:
        resolved["challenge_id"] = settings.onecause_challenge_id

    resolved.setdefault("page_size", 100)
    resolved.setdefault(
        "enabled_object_types",
        ["paid_activities", "supporters", "events", "fundraising_pages"],
    )
    resolved.setdefault("fetch_window_strategy", "updated_at")
    resolved.setdefault("timezone", "UTC")
    resolved.setdefault("request_timeout_seconds", settings.default_request_timeout_seconds)
    if auth_mode == "access_token":
        resolved.setdefault("auth_header_name", "x-access-token")
        resolved.setdefault("test_endpoint", "/api/clients/{organization_id}/admin-details")
        resolved.setdefault(
            "endpoint_templates",
            {
                "paid_activities": "/api/clients/{organization_id}/donations",
                "supporters": "/api/clients/{organization_id}/participants",
                "events": "/api/clients/{organization_id}/details",
                "fundraising_pages": "/api/challenge-page",
            },
        )
        resolved.setdefault(
            "list_key_overrides",
            {
                "paid_activities": "__root__",
                "supporters": "__root__",
                "events": "eventList",
                "fundraising_pages": "__root__",
            },
        )
    else:
        resolved.setdefault("auth_header_name", "X-API-Key")
        resolved.setdefault("test_endpoint", "/organizations/{organization_id}/events")
        resolved.setdefault(
            "endpoint_templates",
            {
                "paid_activities": "/organizations/{organization_id}/paid-activities",
                "supporters": "/organizations/{organization_id}/supporters",
                "events": "/organizations/{organization_id}/events",
                "fundraising_pages": "/organizations/{organization_id}/fundraising-pages",
            },
        )
        resolved.setdefault(
            "list_key_overrides",
            {
                "paid_activities": "paidActivities",
                "supporters": "supporters",
                "events": "events",
                "fundraising_pages": "fundraisingPages",
            },
        )
    resolved.setdefault("incremental_param_start", "updated_after")
    resolved.setdefault("incremental_param_end", "updated_before")
    resolved.setdefault("pagination_param_page", "page")
    resolved.setdefault("pagination_param_page_size", "page_size")
    if "cookie" in {key.lower() for key in resolved}:
        raise ValueError("Cookie-based OneCause authentication is not supported.")
    return resolved
