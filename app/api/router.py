"""Aggregate API router."""

from fastapi import APIRouter

from app.api.routes import (
    everyorg_dashboard,
    everyorg_demo,
    everyorg_public,
    everyorg_webhooks,
    file_imports,
    health,
    ingestion_runs,
    normalized,
    pledge_imports,
    raw_objects,
    scheduler,
    sources,
    ui,
)

api_router = APIRouter()
api_router.include_router(ui.router)
api_router.include_router(health.router, tags=["health"])
api_router.include_router(everyorg_dashboard.router, tags=["everyorg-dashboard"])
api_router.include_router(everyorg_demo.router, tags=["everyorg-demo"])
api_router.include_router(everyorg_public.router, tags=["everyorg-public"])
api_router.include_router(everyorg_webhooks.router, tags=["everyorg-webhooks"])
api_router.include_router(file_imports.router, tags=["file-imports"])
api_router.include_router(pledge_imports.router, tags=["pledge-imports"])
api_router.include_router(sources.router, tags=["sources"])
api_router.include_router(ingestion_runs.router, tags=["ingestion-runs"])
api_router.include_router(raw_objects.router, tags=["raw-objects"])
api_router.include_router(normalized.router, tags=["normalized"])
api_router.include_router(scheduler.router, tags=["scheduler"])
