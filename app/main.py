"""FastAPI application entrypoint."""

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.services.scheduler_service import SchedulerService

settings = get_settings()
configure_logging(settings.log_level)
scheduler_service = SchedulerService(settings.scheduler_poll_seconds)

app = FastAPI(title=settings.app_name)
app.include_router(api_router)


@app.on_event("startup")
def start_scheduler() -> None:
    """Start the in-process scheduler when enabled."""
    if settings.enable_inprocess_scheduler:
        scheduler_service.start()
