"""Gmail connector config schema."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator


class GmailConfig(BaseModel):
    """Typed Gmail source config."""

    model_config = ConfigDict(extra="ignore")

    api_base_url: str = "https://gmail.googleapis.com/gmail/v1"
    user_id: str = "me"
    access_token: SecretStr | None = None
    refresh_token: SecretStr | None = None
    client_id: SecretStr | None = None
    client_secret: SecretStr | None = None
    token_url: str = "https://oauth2.googleapis.com/token"
    query: str | None = None
    label_ids: list[str] = Field(default_factory=list)
    page_size: int = Field(default=25, ge=1, le=100)
    max_messages_per_sync: int = Field(default=100, ge=1, le=500)
    process_attachments: bool = True
    max_attachment_bytes: int = Field(default=5000000, ge=1024, le=25000000)
    body_preference: Literal["plain_text", "html_then_text"] = "plain_text"
    enabled_object_types: list[str] = Field(
        default_factory=lambda: ["email_message", "email_attachment", "gift_extract"]
    )
    attachment_extensions: list[str] = Field(
        default_factory=lambda: [".csv", ".xlsx", ".xls", ".pdf", ".txt", ".tsv"]
    )
    gift_keywords: list[str] = Field(
        default_factory=lambda: [
            "donation",
            "gift",
            "grant",
            "contribution",
            "receipt",
            "pledge",
            "matching gift",
            "charitable",
            "fundraiser",
            "payment",
        ]
    )

    @model_validator(mode="after")
    def validate_auth(self) -> GmailConfig:
        """Require either a bearer token or refresh-token credentials."""
        if self.access_token:
            return self
        if self.refresh_token and self.client_id and self.client_secret:
            return self
        raise ValueError(
            "Provide access_token or the refresh_token/client_id/client_secret trio for Gmail."
        )
