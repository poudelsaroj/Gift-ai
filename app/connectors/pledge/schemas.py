"""Pledge connector config schema."""

from pydantic import BaseModel, Field, SecretStr


class PledgeConfig(BaseModel):
    """Typed Pledge source config."""

    api_base_url: str = "https://api.pledge.to"
    api_key: SecretStr
    page_size: int = 100
    request_timeout_seconds: int = 30
    auth_header_name: str = "Authorization"
    auth_scheme: str = "Bearer"
    donations_endpoint: str = "/v1/donations"
    organizations_endpoint: str = "/v1/organizations"
    enabled_object_types: list[str] = Field(default_factory=lambda: ["donations"])

