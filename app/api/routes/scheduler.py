"""Scheduler endpoints."""

from fastapi import APIRouter

from app.services.scheduler_service import SchedulerService

router = APIRouter(prefix="/api/v1/scheduler")
scheduler_service = SchedulerService()


@router.post("/run-due")
def run_due_sources() -> dict[str, int]:
    """Run all due scheduled sources once."""
    started = scheduler_service.run_due_sources()
    return {"started": started}

