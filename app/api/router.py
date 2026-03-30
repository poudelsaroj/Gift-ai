"""Aggregate API router."""

from fastapi import APIRouter

from app.api.routes import health, ingestion_runs, normalized, raw_objects, scheduler, sources, ui

api_router = APIRouter()
api_router.include_router(ui.router)
api_router.include_router(health.router, tags=["health"])
api_router.include_router(sources.router, tags=["sources"])
api_router.include_router(ingestion_runs.router, tags=["ingestion-runs"])
api_router.include_router(raw_objects.router, tags=["raw-objects"])
api_router.include_router(normalized.router, tags=["normalized"])
api_router.include_router(scheduler.router, tags=["scheduler"])
