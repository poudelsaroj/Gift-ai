"""OneCause connector config schema."""

from typing import Any, Literal

from pydantic import BaseModel, Field, SecretStr, model_validator


class OneCauseConfig(BaseModel):
    """Typed OneCause source config."""

    api_base_url: str
    auth_mode: Literal["api_key", "access_token"] = "api_key"
    api_key: SecretStr
    organization_id: str | None = None
    client_id: str | None = None
    challenge_id: str | None = None
    page_size: int = 100
    initial_sync_start: str | None = None
    enabled_object_types: list[str] = Field(
        default_factory=lambda: ["paid_activities", "supporters", "events", "fundraising_pages"]
    )
    fetch_window_strategy: str = "updated_at"
    timezone: str = "UTC"
    request_timeout_seconds: int = 30
    auth_header_name: str = "X-API-Key"
    org_id_header_name: str | None = None
    test_endpoint: str = "/organizations/{organization_id}/events"
    endpoint_templates: dict[str, str] = Field(
        default_factory=lambda: {
            "paid_activities": "/organizations/{organization_id}/paid-activities",
            "supporters": "/organizations/{organization_id}/supporters",
            "events": "/organizations/{organization_id}/events",
            "fundraising_pages": "/organizations/{organization_id}/fundraising-pages",
        }
    )
    incremental_param_start: str = "updated_after"
    incremental_param_end: str = "updated_before"
    pagination_param_page: str = "page"
    pagination_param_page_size: str = "page_size"
    list_key_overrides: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_identifier(self) -> "OneCauseConfig":
        """Validate auth mode and identifier requirements."""
        if self.auth_mode == "api_key":
            if not self.organization_id:
                raise ValueError("organization_id is required when auth_mode=api_key.")
        if self.auth_mode == "access_token":
            if not self.client_id and not self.organization_id:
                raise ValueError("client_id is required when auth_mode=access_token.")
            if not self.challenge_id:
                raise ValueError("challenge_id is required when auth_mode=access_token.")
            if not self.client_id and self.organization_id:
                self.client_id = self.organization_id
            if not self.organization_id and self.client_id:
                self.organization_id = self.client_id
            if self.org_id_header_name:
                raise ValueError("org_id_header_name is not supported for auth_mode=access_token.")
        return self

    def redacted_dict(self) -> dict[str, Any]:
        """Return a config dict safe for logs."""
        data = self.model_dump()
        data["api_key"] = "***REDACTED***"
        return data
