"""Operator-console API routes and backend launch page."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.schemas.operator_console import OperatorConsoleStateRead, OperatorRecordRead
from app.services.operator_console_service import OperatorConsoleService

router = APIRouter()
operator_console_service = OperatorConsoleService()


@router.get("/api/v1/ui/console-state", response_model=OperatorConsoleStateRead)
def get_console_state(db: Session = Depends(get_db)) -> OperatorConsoleStateRead:
    """Return operator-console sources, summaries, and recent runs."""
    return operator_console_service.get_console_state(db)


@router.get("/api/v1/ui/records", response_model=list[OperatorRecordRead])
def list_operator_records(
    db: Session = Depends(get_db),
    source_id: int | None = Query(default=None),
    record_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=250, ge=1, le=1000),
) -> list[OperatorRecordRead]:
    """Return canonical records enriched with source context for the UI."""
    return operator_console_service.list_records(
        db,
        source_id=source_id,
        record_type=record_type,
        status=status,
        search=search,
        limit=limit,
    )


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def operator_console_home() -> str:
    """Render a minimal backend launch page for the separate operator frontend."""
    settings = get_settings()
    frontend_url = settings.frontend_app_url.rstrip("/")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Gift Ingestion Platform</title>
  <style>
    :root {{
      --bg: #f4f1e8;
      --surface: rgba(255, 253, 248, 0.94);
      --ink: #172033;
      --muted: #627085;
      --line: #d9d0c1;
      --primary: #155bb8;
      --secondary: #1f7a69;
      --shadow: 0 28px 80px rgba(17, 29, 43, 0.12);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 24px;
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(21,91,184,0.10), transparent 28%),
        radial-gradient(circle at bottom right, rgba(31,122,105,0.10), transparent 24%),
        var(--bg);
    }}
    .card {{
      width: min(860px, 100%);
      padding: 32px;
      border: 1px solid var(--line);
      border-radius: 28px;
      background: var(--surface);
      box-shadow: var(--shadow);
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: clamp(2.5rem, 6vw, 4.6rem);
      line-height: 0.94;
      letter-spacing: -0.04em;
    }}
    p, li {{
      color: var(--muted);
      font-size: 1rem;
      line-height: 1.6;
    }}
    .eyebrow {{
      display: inline-block;
      margin-bottom: 12px;
      font-size: 0.76rem;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--primary);
    }}
    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin: 24px 0 18px;
    }}
    a.button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 12px 18px;
      border-radius: 999px;
      text-decoration: none;
      font-weight: 600;
    }}
    a.primary {{ background: var(--primary); color: white; }}
    a.secondary {{
      color: var(--secondary);
      border: 1px solid var(--line);
      background: white;
    }}
    code {{
      padding: 2px 6px;
      border-radius: 8px;
      background: rgba(21,91,184,0.08);
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      color: var(--ink);
    }}
    ul {{
      margin: 20px 0 0;
      padding-left: 18px;
    }}
  </style>
</head>
<body>
  <main class="card">
    <span class="eyebrow">FastAPI Backend</span>
    <h1>Gift Ingestion Platform</h1>
    <p>
      The production operator UI is now a separate Next.js frontend. FastAPI remains the backend
      for ingestion, normalization, source actions, scheduler runs, and operator-console APIs.
    </p>
    <div class="actions">
      <a class="button primary" href="{frontend_url}" target="_blank" rel="noreferrer">Open Operator Console</a>
      <a class="button secondary" href="/docs" target="_blank" rel="noreferrer">Open Swagger</a>
      <a class="button secondary" href="/openapi.json" target="_blank" rel="noreferrer">Open OpenAPI</a>
    </div>
    <ul>
      <li>Frontend URL: <code>{frontend_url}</code></li>
      <li>Console API state: <code>/api/v1/ui/console-state</code></li>
      <li>Console API records: <code>/api/v1/ui/records</code></li>
      <li>Health check: <code>/api/v1/health</code></li>
    </ul>
  </main>
</body>
</html>"""
