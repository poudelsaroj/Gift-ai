"""Settings management."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="local", alias="APP_ENV")
    app_name: str = Field(default="gift-ingestion-backend", alias="APP_NAME")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    database_url: str = Field(
        default="postgresql+psycopg://gift_user:gift_pass@localhost:5432/gift_ingestion",
        alias="DATABASE_URL",
    )
    raw_storage_root: str = Field(default="./raw_storage", alias="RAW_STORAGE_ROOT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    default_request_timeout_seconds: int = Field(
        default=30,
        alias="DEFAULT_REQUEST_TIMEOUT_SECONDS",
    )
    onecause_default_base_url: str = Field(
        default="https://api.onecause.com",
        alias="ONECAUSE_DEFAULT_BASE_URL",
    )
    onecause_portal_url: str | None = Field(default=None, alias="ONECAUSE_PORTAL_URL")
    onecause_portal_username: str | None = Field(default=None, alias="ONECAUSE_PORTAL_USERNAME")
    onecause_portal_password: str | None = Field(default=None, alias="ONECAUSE_PORTAL_PASSWORD")
    onecause_docs_url: str | None = Field(default=None, alias="ONECAUSE_DOCS_URL")
    onecause_docs_username: str | None = Field(default=None, alias="ONECAUSE_DOCS_USERNAME")
    onecause_docs_password: str | None = Field(default=None, alias="ONECAUSE_DOCS_PASSWORD")
    onecause_api_base_url: str | None = Field(default=None, alias="ONECAUSE_API_BASE_URL")
    onecause_api_key: str | None = Field(default=None, alias="ONECAUSE_API_KEY")
    onecause_organization_id: str | None = Field(default=None, alias="ONECAUSE_ORGANIZATION_ID")
    onecause_client_id: str | None = Field(default=None, alias="ONECAUSE_CLIENT_ID")
    onecause_access_token: str | None = Field(default=None, alias="ONECAUSE_ACCESS_TOKEN")
    onecause_challenge_id: str | None = Field(default=None, alias="ONECAUSE_CHALLENGE_ID")
    pledge_api_base_url: str = Field(default="https://api.pledge.to", alias="PLEDGE_API_BASE_URL")
    pledge_api_key: str | None = Field(default=None, alias="PLEDGE_API_KEY")
    everyorg_public_api_base_url: str = Field(
        default="https://partners.every.org",
        alias="EVERYORG_PUBLIC_API_BASE_URL",
    )
    everyorg_public_key: str | None = Field(default=None, alias="EVERYORG_PUBLIC_KEY")
    everyorg_private_key: str | None = Field(default=None, alias="EVERYORG_PRIVATE_KEY")
    everyorg_webhook_token: str | None = Field(default=None, alias="EVERYORG_WEBHOOK_TOKEN")
    everyorg_webhook_kind: str | None = Field(default=None, alias="EVERYORG_WEBHOOK_KIND")
    everyorg_nonprofit_slug: str | None = Field(default=None, alias="EVERYORG_NONPROFIT_SLUG")
    enable_inprocess_scheduler: bool = Field(default=True, alias="ENABLE_INPROCESS_SCHEDULER")
    scheduler_poll_seconds: int = Field(default=60, alias="SCHEDULER_POLL_SECONDS")


@lru_cache
def get_settings() -> Settings:
    """Return cached settings."""
    return Settings()
