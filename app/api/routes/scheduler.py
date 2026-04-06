"""Scheduler endpoints."""

from fastapi import APIRouter, HTTPException, Query

from app.services.scheduler_service import SchedulerService

router = APIRouter(prefix="/api/v1/scheduler")
scheduler_service = SchedulerService()


@router.post("/run-due")
def run_due_sources(force: bool = Query(default=False)) -> dict[str, int | bool]:
    """Run scheduled sources once, optionally bypassing the due-time check."""
    try:
        started = scheduler_service.run_due_sources(force=force)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"started": started, "force": force}

