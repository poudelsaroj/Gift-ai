"""Key-based Every.org demo endpoints."""

from __future__ import annotations

from typing import Annotated, Any

import httpx
from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel

from app.connectors.everyorg.client import EveryOrgAPIClient
from app.connectors.everyorg.schemas import EveryOrgConfig
from app.core.config import get_settings

router = APIRouter(prefix="/api/v1/everyorg/demo")


class EveryOrgDemoConfigResponse(BaseModel):
    """Key availability for the Every.org demo flows."""

    public_key_configured: bool
    private_key_configured: bool
    public_api_base_url: str


def _build_client() -> EveryOrgAPIClient:
    settings = get_settings()
    config = EveryOrgConfig.model_construct(
        public_api_base_url=settings.everyorg_public_api_base_url,
        public_key=settings.everyorg_public_key,
        private_key=settings.everyorg_private_key,
        nonprofit_slug=settings.everyorg_nonprofit_slug,
        webhook_token=settings.everyorg_webhook_token,
        webhook_kind=settings.everyorg_webhook_kind or "nonprofit",
    )
    return EveryOrgAPIClient(config)


def _raise_upstream_http_error(exc: httpx.HTTPStatusError) -> None:
    detail: Any
    try:
        detail = exc.response.json()
    except ValueError:
        detail = exc.response.text or str(exc)
    raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc


def _raise_validation_error(exc: Exception) -> None:
    raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/config", response_model=EveryOrgDemoConfigResponse)
def get_everyorg_demo_config() -> EveryOrgDemoConfigResponse:
    """Report whether the Every.org demo has the needed keys configured."""
    settings = get_settings()
    return EveryOrgDemoConfigResponse(
        public_key_configured=bool(settings.everyorg_public_key),
        private_key_configured=bool(settings.everyorg_private_key),
        public_api_base_url=settings.everyorg_public_api_base_url,
    )


@router.get("/nonprofit/{identifier}")
def get_nonprofit(identifier: str) -> dict[str, Any]:
    """Fetch nonprofit details using EVERYORG_PUBLIC_KEY."""
    try:
        return _build_client().get(f"/v0.2/nonprofit/{identifier}")
    except httpx.HTTPStatusError as exc:
        _raise_upstream_http_error(exc)
    except Exception as exc:
        _raise_validation_error(exc)


@router.get("/search/{search_term}")
def search_nonprofits(
    search_term: str,
    take: int | None = Query(default=None, ge=1, le=50),
    cause: str | None = Query(default=None),
    page: int | None = Query(default=None, ge=1),
) -> dict[str, Any]:
    """Search nonprofits using EVERYORG_PUBLIC_KEY."""
    params: dict[str, Any] = {}
    if take is not None:
        params["take"] = take
    if cause:
        params["cause"] = cause
    if page is not None:
        params["page"] = page
    try:
        return _build_client().get(f"/v0.2/search/{search_term}", params=params or None)
    except httpx.HTTPStatusError as exc:
        _raise_upstream_http_error(exc)
    except Exception as exc:
        _raise_validation_error(exc)


@router.get("/browse/{cause}")
def browse_nonprofits(
    cause: str,
    take: int | None = Query(default=None, ge=1, le=50),
    page: int | None = Query(default=None, ge=1),
) -> dict[str, Any]:
    """Browse nonprofits by cause using EVERYORG_PUBLIC_KEY."""
    params: dict[str, Any] = {}
    if take is not None:
        params["take"] = take
    if page is not None:
        params["page"] = page
    try:
        return _build_client().get(f"/v0.2/browse/{cause}", params=params or None)
    except httpx.HTTPStatusError as exc:
        _raise_upstream_http_error(exc)
    except Exception as exc:
        _raise_validation_error(exc)


@router.get("/fundraisers/{nonprofit_identifier}/{fundraiser_identifier}")
def get_fundraiser(nonprofit_identifier: str, fundraiser_identifier: str) -> dict[str, Any]:
    """Fetch fundraiser details using EVERYORG_PUBLIC_KEY."""
    try:
        return _build_client().get(
            f"/v0.2/nonprofit/{nonprofit_identifier}/fundraiser/{fundraiser_identifier}"
        )
    except httpx.HTTPStatusError as exc:
        _raise_upstream_http_error(exc)
    except Exception as exc:
        _raise_validation_error(exc)


@router.get("/fundraisers/{nonprofit_identifier}/{fundraiser_identifier}/raised")
def get_fundraiser_raised(nonprofit_identifier: str, fundraiser_identifier: str) -> dict[str, Any]:
    """Fetch fundraiser raised totals using EVERYORG_PUBLIC_KEY."""
    try:
        return _build_client().get(
            f"/v0.2/nonprofit/{nonprofit_identifier}/fundraiser/{fundraiser_identifier}/raised"
        )
    except httpx.HTTPStatusError as exc:
        _raise_upstream_http_error(exc)
    except Exception as exc:
        _raise_validation_error(exc)


@router.post("/fundraiser")
def create_fundraiser(payload: Annotated[dict[str, Any], Body(...)]) -> dict[str, Any]:
    """Create a fundraiser using EVERYORG_PUBLIC_KEY + EVERYORG_PRIVATE_KEY."""
    try:
        return _build_client().post_private("/v0.2/fundraiser", payload)
    except httpx.HTTPStatusError as exc:
        _raise_upstream_http_error(exc)
    except Exception as exc:
        _raise_validation_error(exc)
