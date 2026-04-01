"""Typed configuration and webhook payload schemas for Every.org."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EveryOrgConfig(BaseModel):
    """Supported Every.org source configuration."""

    model_config = ConfigDict(extra="ignore")

    public_api_base_url: str = "https://partners.every.org"
    webhook_token: str | None = Field(default=None, min_length=8)
    webhook_kind: Literal["nonprofit", "partner"] = "nonprofit"
    nonprofit_slug: str | None = None
    public_key: str | None = None
    private_key: str | None = None

    @model_validator(mode="after")
    def validate_key_pair(self) -> "EveryOrgConfig":
        """Require a valid Every.org config shape."""
        if self.private_key and not self.public_key:
            raise ValueError("public_key is required when private_key is configured")
        if not self.webhook_token and not (self.public_key and self.nonprofit_slug):
            raise ValueError(
                "Either webhook_token or both public_key and nonprofit_slug are required."
            )
        return self


class EveryOrgNonprofitRef(BaseModel):
    """Every.org nonprofit metadata embedded in donation webhooks."""

    model_config = ConfigDict(extra="allow")

    slug: str
    ein: str | None = None
    name: str


class EveryOrgFundraiserRef(BaseModel):
    """Every.org fundraiser metadata embedded in donation webhooks."""

    model_config = ConfigDict(extra="allow")

    id: str
    title: str
    slug: str


class EveryOrgDonationWebhookPayload(BaseModel):
    """Every.org donation webhook payload."""

    model_config = ConfigDict(extra="allow")

    chargeId: str
    partnerDonationId: str | None = None
    partnerMetadata: dict[str, Any] | None = None
    designation: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    email: str | None = None
    toNonprofit: EveryOrgNonprofitRef
    amount: str
    netAmount: str | None = None
    currency: str
    frequency: str
    donationDate: str
    publicTestimony: str | None = None
    privateNote: str | None = None
    fromFundraiser: EveryOrgFundraiserRef | None = None
    paymentMethod: str | None = None
