"""Simplified operator UI focused on the canonical model."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def operator_console() -> str:
    """Render a source-first operator console around canonical records."""
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Canonical Gift Console</title>
  <style>
    :root {
      --bg: #f3f6fb;
      --bg-2: #ffffff;
      --panel: rgba(255, 255, 255, 0.94);
      --ink: #172033;
      --muted: #647085;
      --line: #d8e1ee;
      --accent: #1b5fc6;
      --accent-2: #0f8a7b;
      --accent-3: #4457a6;
      --danger: #9a3e34;
      --shadow: 0 22px 44px rgba(18, 38, 63, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(27,95,198,0.12), transparent 28%),
        radial-gradient(circle at top right, rgba(15,138,123,0.10), transparent 24%),
        linear-gradient(180deg, #f8fbff 0%, var(--bg) 100%);
    }
    .shell {
      max-width: 1320px;
      margin: 0 auto;
      padding: 28px 20px 40px;
    }
    .hero, .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(6px);
    }
    .hero {
      padding: 28px;
      margin-bottom: 20px;
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 20px;
      align-items: end;
    }
    h1 {
      margin: 0 0 10px;
      font-size: clamp(2.3rem, 6vw, 4.5rem);
      line-height: 0.96;
      letter-spacing: -0.04em;
    }
    .hero p, .meta, label, small, .muted { color: var(--muted); }
    .meta {
      display: flex;
      gap: 14px;
      flex-wrap: wrap;
      font-size: 0.92rem;
      margin-top: 14px;
    }
    .hero-stats {
      display: grid;
      gap: 12px;
    }
    .stat {
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 14px 16px;
      background: rgba(247, 250, 255, 0.92);
    }
    .stat strong {
      display: block;
      color: var(--accent);
      font-size: 1.35rem;
      margin-top: 4px;
    }
    .grid {
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 20px;
      align-items: start;
    }
    .panel {
      padding: 20px;
    }
    .panel h2 {
      margin: 0 0 10px;
      font-size: 1.3rem;
    }
    .subhead {
      margin: -4px 0 16px;
      color: var(--muted);
      font-size: 0.92rem;
    }
    .stack { display: grid; gap: 12px; }
    .row { display: grid; gap: 8px; }
    input, select, button {
      font: inherit;
    }
    input, select {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px 14px;
      background: #ffffff;
      color: var(--ink);
    }
    .actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    button {
      border: 0;
      border-radius: 999px;
      padding: 11px 18px;
      background: var(--accent);
      color: white;
      cursor: pointer;
      transition: transform 140ms ease, opacity 140ms ease, background 140ms ease;
    }
    button.alt { background: var(--accent-2); }
    button.ghost {
      background: transparent;
      border: 1px solid var(--line);
      color: var(--accent);
    }
    button.info { background: var(--accent-3); }
    button:hover { transform: translateY(-1px); }
    button:disabled { opacity: 0.55; cursor: default; transform: none; }
    .chips {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .chip {
      font-size: 0.8rem;
      padding: 4px 9px;
      border-radius: 999px;
      background: #edf3fb;
      color: var(--ink);
    }
    .chip.ok { background: rgba(15,138,123,0.12); color: var(--accent-2); }
    .chip.warn { background: rgba(68,87,166,0.12); color: var(--accent-3); }
    .chip.bad { background: rgba(154,62,52,0.12); color: var(--danger); }
    .chip.info { background: rgba(27,95,198,0.12); color: var(--accent); }
    .detail-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }
    .detail {
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 12px 13px;
      background: rgba(248, 251, 255, 0.96);
    }
    .detail strong {
      display: block;
      font-size: 0.8rem;
      color: var(--muted);
      margin-bottom: 5px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .detail span {
      display: block;
      font-size: 1rem;
    }
    .banner {
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 14px 16px;
      background: linear-gradient(135deg, rgba(27,95,198,0.08), rgba(15,138,123,0.08));
    }
    .banner code {
      display: inline-block;
      margin-top: 6px;
      padding: 3px 6px;
      border-radius: 8px;
      background: rgba(255,255,255,0.55);
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.82rem;
    }
    .toolbar {
      display: grid;
      grid-template-columns: 180px 180px 1fr;
      gap: 12px;
      margin-bottom: 14px;
    }
    .table-wrap {
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: rgba(255,255,255,0.98);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 1120px;
    }
    th, td {
      padding: 12px 14px;
      text-align: left;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
      font-size: 0.92rem;
    }
    th {
      position: sticky;
      top: 0;
      z-index: 1;
      background: #f6f9fe;
    }
    .summary-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }
    .summary-card {
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 14px 16px;
      background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
    }
    .summary-card strong {
      display: block;
      margin-top: 6px;
      font-size: 1.35rem;
      color: var(--accent);
    }
    .source-data {
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 14px;
      margin-bottom: 16px;
    }
    .insight-panel {
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px;
      background: rgba(248, 251, 255, 0.92);
    }
    .insight-panel h3 {
      margin: 0 0 6px;
      font-size: 1rem;
    }
    .source-list {
      display: grid;
      gap: 10px;
      margin-top: 12px;
    }
    .source-list-item {
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 12px;
      background: #fff;
    }
    .source-list-item strong {
      display: block;
      margin-bottom: 6px;
    }
    .source-list-item small {
      display: block;
      margin-top: 6px;
    }
    .sort-button {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 0;
      border: 0;
      background: transparent;
      color: inherit;
      font: inherit;
      font-weight: inherit;
      cursor: pointer;
    }
    .sort-button:hover {
      transform: none;
      color: var(--accent);
    }
    .sort-arrow {
      font-size: 0.8rem;
      color: var(--muted);
    }
    .empty {
      padding: 18px;
      color: var(--muted);
    }
    pre {
      margin: 0;
      border-radius: 16px;
      padding: 14px;
      background: #172033;
      color: #f5f8fd;
      font-size: 0.85rem;
      min-height: 100px;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
    }
    @media (max-width: 980px) {
      .hero, .grid, .toolbar, .detail-grid, .summary-grid, .source-data { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <div>
        <div class="chip ok">Canonical Operator View</div>
        <h1>Gift Intake Canonical Console</h1>
        <p>Choose a source, review the latest data shape, and inspect canonical gift records without leaving the operator console.</p>
        <div class="meta">
          <span>Swagger: <a href="/docs">/docs</a></span>
          <span>OpenAPI: <a href="/openapi.json">/openapi.json</a></span>
          <span>Health: <a href="/api/v1/health">/api/v1/health</a></span>
        </div>
      </div>
        <div class="hero-stats">
          <div class="stat">
          <span class="muted">Normalized target</span>
          <strong>One shared model</strong>
          <small>Source-specific spillover stays in <code>extra_metadata</code>.</small>
          </div>
          <div class="stat">
          <span class="muted">Operator workflow</span>
          <strong>Select, inspect, act</strong>
          <small>Source-level controls and canonical review stay on one screen.</small>
          </div>
        </div>
      </section>

    <section class="grid">
      <div class="panel">
        <h2>Source Control</h2>
        <div class="subhead">Pick an existing source, run sync actions, and monitor the latest sync timing and status.</div>
        <div class="stack">
          <div class="row">
            <label for="source_selector">Active source</label>
            <select id="source_selector"></select>
          </div>
          <div class="detail-grid">
            <div class="detail"><strong>System</strong><span id="detail_system">-</span></div>
            <div class="detail"><strong>Mode</strong><span id="detail_mode">-</span></div>
            <div class="detail"><strong>Schedule</strong><span id="detail_schedule">-</span></div>
            <div class="detail"><strong>Last sync</strong><span id="detail_last_sync">-</span></div>
            <div class="detail"><strong>Last status</strong><span id="detail_last_status">-</span></div>
            <div class="detail"><strong>Last records</strong><span id="detail_last_records">-</span></div>
          </div>
          <div class="chips" id="source_chips"></div>
          <div class="actions">
            <button id="test_btn" class="ghost">Test connection</button>
            <button id="paid_btn">Paid activities</button>
            <button id="supporters_btn" class="alt">Supporters</button>
            <button id="full_btn" class="info">Full sync</button>
          </div>
          <div class="actions">
            <button id="refresh_btn" class="ghost">Refresh</button>
            <button id="run_due_btn" class="ghost">Run scheduled sources now</button>
          </div>
          <div class="banner" id="source_note">
            Choose a source to enable sync actions and filter the canonical table.
          </div>
          <div class="banner" id="integration_note">
            Integration details appear here for the selected source.
          </div>
          <div class="stack" id="tabular_upload_tools" style="display:none;">
            <div class="row">
              <label for="tabular_import_file">Canonical CSV / XLSX upload</label>
              <input id="tabular_import_file" type="file" accept=".csv,.tsv,.xlsx" />
            </div>
            <div class="actions">
              <button id="tabular_import_btn" class="alt">Upload and normalize</button>
            </div>
            <small>Uploads a CSV, TSV, or XLSX file to OpenAI for canonical gift extraction, then saves the normalized rows into the selected source.</small>
          </div>
          <div class="stack" id="everyorg_tools" style="display:none;">
            <div class="row">
              <label for="everyorg_import_file">Every.org dashboard CSV</label>
              <input id="everyorg_import_file" type="file" accept=".csv,text/csv" />
            </div>
            <div class="actions">
              <button id="everyorg_import_btn" class="alt">Import dashboard CSV</button>
            </div>
            <small>Every.org historical donation ingestion is available through the dashboard CSV import route.</small>
          </div>
          <pre id="console"></pre>
        </div>
      </div>

      <div class="panel">
        <h2>Canonical Records</h2>
        <div class="subhead">The right side is source-aware: choose a source to see its canonical data footprint, recent records, and filtered table.</div>
        <div class="summary-grid">
          <div class="summary-card">
            <span class="muted">Selected source</span>
            <strong id="summary_source_name">All sources</strong>
            <small id="summary_source_note">No source filter applied.</small>
          </div>
          <div class="summary-card">
            <span class="muted">Canonical records</span>
            <strong id="summary_record_count">0</strong>
            <small id="summary_gift_count">0 gift rows</small>
          </div>
          <div class="summary-card">
            <span class="muted">Raw objects</span>
            <strong id="summary_raw_count">0</strong>
            <small id="summary_raw_types">No raw objects loaded</small>
          </div>
          <div class="summary-card">
            <span class="muted">Latest canonical date</span>
            <strong id="summary_latest_date">-</strong>
            <small id="summary_latest_amount">No amount tracked yet</small>
          </div>
        </div>
        <div class="source-data">
          <div class="insight-panel">
            <h3>Selected Source Overview</h3>
            <div class="muted" id="source_overview_text">Pick a source to review its canonical footprint and recent normalized records.</div>
            <div class="source-list" id="recent_records_list"></div>
          </div>
          <div class="insight-panel">
            <h3>Data Coverage</h3>
            <div class="source-list" id="source_metrics_list"></div>
          </div>
        </div>
        <div class="toolbar">
          <div class="row">
            <label for="record_type_filter">Record type</label>
            <select id="record_type_filter">
              <option value="">All types</option>
              <option value="gift">Gift</option>
              <option value="supporter">Supporter</option>
            </select>
          </div>
          <div class="row">
            <label for="record_status_filter">Status</label>
            <select id="record_status_filter">
              <option value="">All statuses</option>
              <option value="succeeded">Succeeded</option>
              <option value="failed">Failed</option>
              <option value="active">Active</option>
              <option value="pending">Pending</option>
            </select>
          </div>
          <div class="row">
            <label for="record_search">Search</label>
            <input id="record_search" placeholder="Name, email, campaign, related entity..." />
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Source</th>
                <th>Type</th>
                <th>Record ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Campaign</th>
                <th>Related</th>
                <th>Team</th>
                <th>Amount</th>
                <th><button id="date_sort_btn" class="sort-button" type="button">Date <span id="date_sort_arrow" class="sort-arrow">↓</span></button></th>
                <th>Reference</th>
                <th>Metadata</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody id="records_body"></tbody>
          </table>
        </div>
      </div>
    </section>
  </div>

  <script>
    const consoleEl = document.getElementById("console");
    const sourceSelectorEl = document.getElementById("source_selector");
    const recordsBody = document.getElementById("records_body");
    const sourceChipsEl = document.getElementById("source_chips");
    const sourceNoteEl = document.getElementById("source_note");
    const integrationNoteEl = document.getElementById("integration_note");
    const everyOrgToolsEl = document.getElementById("everyorg_tools");
    const everyOrgImportFileEl = document.getElementById("everyorg_import_file");
    const tabularUploadToolsEl = document.getElementById("tabular_upload_tools");
    const tabularImportFileEl = document.getElementById("tabular_import_file");
    const detailSystemEl = document.getElementById("detail_system");
    const detailModeEl = document.getElementById("detail_mode");
    const detailScheduleEl = document.getElementById("detail_schedule");
    const detailLastSyncEl = document.getElementById("detail_last_sync");
    const detailLastStatusEl = document.getElementById("detail_last_status");
    const detailLastRecordsEl = document.getElementById("detail_last_records");
    const summarySourceNameEl = document.getElementById("summary_source_name");
    const summarySourceNoteEl = document.getElementById("summary_source_note");
    const summaryRecordCountEl = document.getElementById("summary_record_count");
    const summaryGiftCountEl = document.getElementById("summary_gift_count");
    const summaryRawCountEl = document.getElementById("summary_raw_count");
    const summaryRawTypesEl = document.getElementById("summary_raw_types");
    const summaryLatestDateEl = document.getElementById("summary_latest_date");
    const summaryLatestAmountEl = document.getElementById("summary_latest_amount");
    const sourceOverviewTextEl = document.getElementById("source_overview_text");
    const recentRecordsListEl = document.getElementById("recent_records_list");
    const sourceMetricsListEl = document.getElementById("source_metrics_list");
    const recordTypeFilterEl = document.getElementById("record_type_filter");
    const recordStatusFilterEl = document.getElementById("record_status_filter");
    const recordSearchEl = document.getElementById("record_search");
    const dateSortButtonEl = document.getElementById("date_sort_btn");
    const dateSortArrowEl = document.getElementById("date_sort_arrow");
    const actionButtons = {
      test: document.getElementById("test_btn"),
      paid: document.getElementById("paid_btn"),
      supporters: document.getElementById("supporters_btn"),
      full: document.getElementById("full_btn"),
    };
    const defaultActionLabels = {
      test: "Test connection",
      paid: "Paid activities",
      supporters: "Supporters",
      full: "Full sync",
    };

    let state = {
      sources: [],
      runs: [],
      rawObjects: [],
      records: [],
      selectedSourceId: "",
      recordDateSortDirection: "desc",
    };

    function print(label, data) {
      const block = typeof data === "string" ? data : JSON.stringify(data, null, 2);
      consoleEl.textContent = `[${new Date().toLocaleTimeString()}] ${label}\\n${block}\\n\\n` + consoleEl.textContent;
    }

    function statusChip(status) {
      const tone = status === "completed" || status === "succeeded" || status === "enabled" || status === "active" ? "ok"
        : status === "failed" || status === "disabled" ? "bad"
        : "warn";
      return `<span class="chip ${tone}">${status || "n/a"}</span>`;
    }

    function formatDateTime(value) {
      if (!value) return "-";
      try {
        return new Date(value).toLocaleString();
      } catch (_) {
        return value;
      }
    }

    async function request(url, options = {}) {
      const response = await fetch(url, {
        headers: { "Content-Type": "application/json", ...(options.headers || {}) },
        ...options,
      });
      const text = await response.text();
      let body = text;
      try { body = text ? JSON.parse(text) : {}; } catch (_) {}
      if (!response.ok) {
        print(`Request failed: ${url}`, body);
        throw new Error(typeof body === "string" ? body : JSON.stringify(body));
      }
      return body;
    }

    function selectedSource() {
      return state.sources.find((item) => String(item.id) === String(state.selectedSourceId)) || null;
    }

    function latestRunForSource(sourceId) {
      return state.runs
        .filter((run) => String(run.source_id) === String(sourceId))
        .sort((a, b) => new Date(b.started_at || b.created_at || 0) - new Date(a.started_at || a.created_at || 0))[0] || null;
    }

    function extraMetadataSummary(item) {
      const extra = item.extra_metadata || {};
      const keys = Object.keys(extra).filter((key) => extra[key] !== null && extra[key] !== undefined && extra[key] !== "");
      return keys.slice(0, 3).join(", ");
    }

    function sourceIdByRawObject(rawObjectId) {
      const raw = state.rawObjects.find((item) => item.id === rawObjectId);
      return raw ? String(raw.source_id) : null;
    }

    function parseRecordDate(item) {
      const rawValue = item.record_date || item.gift_date || "";
      const parsed = rawValue ? new Date(rawValue) : null;
      const timestamp = parsed && !Number.isNaN(parsed.getTime()) ? parsed.getTime() : null;
      return { rawValue, timestamp };
    }

    function recordsForSource(source) {
      if (!source) return state.records.slice();
      return state.records.filter((item) => sourceIdByRawObject(item.raw_object_id) === String(source.id));
    }

    function rawObjectsForSource(source) {
      if (!source) return state.rawObjects.slice();
      return state.rawObjects.filter((item) => String(item.source_id) === String(source.id));
    }

    function formatAmount(item) {
      if (item.amount === null || item.amount === undefined || item.amount === "") return "No amount";
      return `${item.amount} ${item.currency || ""}`.trim();
    }

    function filteredRecords() {
      const src = selectedSource();
      const typeFilter = recordTypeFilterEl.value;
      const statusFilter = recordStatusFilterEl.value;
      const search = recordSearchEl.value.trim().toLowerCase();
      const items = state.records.filter((item) => {
        const sourceMatch = src ? sourceIdByRawObject(item.raw_object_id) === String(src.id) : true;
        const typeMatch = typeFilter ? item.record_type === typeFilter : true;
        const statusMatch = statusFilter ? item.status === statusFilter : true;
        const haystack = [
          item.source_system,
          item.source_record_id,
          item.primary_name,
          item.primary_email,
          item.campaign_name,
          item.challenge_name,
          item.related_entity_name,
          item.team_name,
          item.receipt_number,
        ].filter(Boolean).join(" ").toLowerCase();
        const searchMatch = search ? haystack.includes(search) : true;
        return sourceMatch && typeMatch && statusMatch && searchMatch;
      });
      const direction = state.recordDateSortDirection === "asc" ? 1 : -1;
      return items.slice().sort((left, right) => {
        const leftDate = parseRecordDate(left);
        const rightDate = parseRecordDate(right);
        if (leftDate.timestamp !== null && rightDate.timestamp !== null && leftDate.timestamp !== rightDate.timestamp) {
          return (leftDate.timestamp - rightDate.timestamp) * direction;
        }
        if (leftDate.timestamp !== null && rightDate.timestamp === null) return -1;
        if (leftDate.timestamp === null && rightDate.timestamp !== null) return 1;
        return String(left.source_record_id || left.gift_id || "").localeCompare(String(right.source_record_id || right.gift_id || ""));
      });
    }

    function renderDateSortState() {
      dateSortArrowEl.textContent = state.recordDateSortDirection === "asc" ? "↑" : "↓";
      dateSortButtonEl.setAttribute(
        "aria-label",
        state.recordDateSortDirection === "asc" ? "Date sorted ascending. Click to sort descending." : "Date sorted descending. Click to sort ascending.",
      );
    }

    function renderSourceSelector() {
      if (!state.sources.length) {
        sourceSelectorEl.innerHTML = `<option value="">No sources available</option>`;
        state.selectedSourceId = "";
        return;
      }
      if (state.selectedSourceId && !state.sources.find((item) => String(item.id) === String(state.selectedSourceId))) {
        state.selectedSourceId = "";
      }
      sourceSelectorEl.innerHTML = [`<option value="" ${!state.selectedSourceId ? "selected" : ""}>All sources (canonical view)</option>`]
        .concat(state.sources.map((source) => `
        <option value="${source.id}" ${String(source.id) === String(state.selectedSourceId) ? "selected" : ""}>
          ${source.source_name} (${source.source_system})
        </option>
      `)).join("");
    }

    function renderSourceInsights() {
      const source = selectedSource();
      const sourceRecords = recordsForSource(source);
      const sourceRawObjects = rawObjectsForSource(source);
      const giftRecords = sourceRecords.filter((item) => item.record_type === "gift");
      const datedRecords = sourceRecords
        .map((item) => ({ item, date: parseRecordDate(item) }))
        .filter((entry) => entry.date.timestamp !== null)
        .sort((left, right) => right.date.timestamp - left.date.timestamp);
      const latestRecord = datedRecords[0] ? datedRecords[0].item : null;
      const rawTypeCounts = sourceRawObjects.reduce((acc, item) => {
        const key = item.external_object_type || "unknown";
        acc[key] = (acc[key] || 0) + 1;
        return acc;
      }, {});
      const rawTypeSummary = Object.entries(rawTypeCounts)
        .sort((left, right) => right[1] - left[1])
        .slice(0, 3)
        .map(([key, count]) => `${key}: ${count}`)
        .join(" · ");
      const latestRun = source ? latestRunForSource(source.id) : state.runs
        .slice()
        .sort((a, b) => new Date(b.started_at || b.created_at || 0) - new Date(a.started_at || a.created_at || 0))[0] || null;

      summarySourceNameEl.textContent = source ? source.source_name : "All sources";
      summarySourceNoteEl.textContent = source
        ? `${source.source_system} · ${source.enabled ? "enabled" : "disabled"} · ${source.acquisition_mode || "manual"}`
        : "Cross-source canonical review.";
      summaryRecordCountEl.textContent = String(sourceRecords.length);
      summaryGiftCountEl.textContent = `${giftRecords.length} gift rows`;
      summaryRawCountEl.textContent = String(sourceRawObjects.length);
      summaryRawTypesEl.textContent = rawTypeSummary || "No raw objects loaded";
      summaryLatestDateEl.textContent = latestRecord ? formatDateTime(latestRecord.record_date || latestRecord.gift_date) : "-";
      summaryLatestAmountEl.textContent = latestRecord ? formatAmount(latestRecord) : "No amount tracked yet";

      sourceOverviewTextEl.textContent = source
        ? `Showing canonical records and raw lineage for ${source.source_name}. The table below is filtered to this source, and sync actions on the left apply only here.`
        : "Showing the cross-source view. Select a source on the left to narrow the canonical table and inspect source-specific data coverage.";

      const recentRecords = sourceRecords
        .slice()
        .sort((left, right) => {
          const leftDate = parseRecordDate(left);
          const rightDate = parseRecordDate(right);
          return (rightDate.timestamp || 0) - (leftDate.timestamp || 0);
        })
        .slice(0, 4);
      if (!recentRecords.length) {
        recentRecordsListEl.innerHTML = `<div class="source-list-item"><strong>No canonical records yet</strong><small>Run a sync or import for the selected source to populate this panel.</small></div>`;
      } else {
        recentRecordsListEl.innerHTML = recentRecords.map((item) => `
          <div class="source-list-item">
            <strong>${item.primary_name || item.donor_name || item.source_record_id || "Unnamed record"}</strong>
            <div class="chips">
              <span class="chip info">${item.record_type || "record"}</span>
              <span class="chip">${formatAmount(item)}</span>
              <span class="chip warn">${item.record_date || item.gift_date || "No date"}</span>
            </div>
            <small>${item.primary_email || item.donor_email || item.campaign_name || item.receipt_number || "No contact or campaign value"}</small>
          </div>
        `).join("");
      }

      const metrics = [
        {
          label: "Latest run",
          value: latestRun ? formatDateTime(latestRun.completed_at || latestRun.started_at || latestRun.created_at) : "No run yet",
          detail: latestRun ? `${latestRun.status || "n/a"} · ${latestRun.records_fetched_count || 0} fetched` : "Run the source to populate this metric.",
        },
        {
          label: "Statuses",
          value: sourceRecords.length ? `${new Set(sourceRecords.map((item) => item.status).filter(Boolean)).size} active values` : "No statuses",
          detail: sourceRecords.length ? sourceRecords.map((item) => item.status).filter(Boolean).slice(0, 3).join(" · ") || "No status values" : "No canonical rows yet.",
        },
        {
          label: "Coverage",
          value: `${giftRecords.length}/${sourceRecords.length || 0} gift records`,
          detail: `${sourceRawObjects.length} raw objects retained for audit.`,
        },
      ];
      sourceMetricsListEl.innerHTML = metrics.map((metric) => `
        <div class="source-list-item">
          <strong>${metric.label}</strong>
          <div>${metric.value}</div>
          <small>${metric.detail}</small>
        </div>
      `).join("");
    }

    function renderSourceDetails() {
      const source = selectedSource();
      const run = source ? latestRunForSource(source.id) : null;
      if (!source) {
        actionButtons.test.textContent = defaultActionLabels.test;
        actionButtons.paid.textContent = defaultActionLabels.paid;
        actionButtons.supporters.textContent = defaultActionLabels.supporters;
        actionButtons.full.textContent = defaultActionLabels.full;
        const latestRun = state.runs
          .slice()
          .sort((a, b) => new Date(b.started_at || b.created_at || 0) - new Date(a.started_at || a.created_at || 0))[0] || null;
        detailSystemEl.textContent = "all";
        detailModeEl.textContent = "canonical / mixed";
        detailScheduleEl.textContent = `${state.sources.length} sources`;
        detailLastSyncEl.textContent = latestRun ? formatDateTime(latestRun.completed_at || latestRun.started_at || latestRun.created_at) : "No sync yet";
        detailLastStatusEl.innerHTML = latestRun ? statusChip(latestRun.status) : "-";
        detailLastRecordsEl.textContent = `${state.records.length} records loaded`;
        sourceChipsEl.innerHTML = `
          <span class="chip ok">all sources</span>
          <span class="chip">${state.sources.length} configured</span>
          <span class="chip info">${state.records.length} canonical records</span>
        `;
        sourceNoteEl.textContent = "Canonical table across every source. Select a specific source only when you want source-specific actions or details.";
        integrationNoteEl.textContent = "The table on the right is the single shared model. Source selection is optional and only acts as a filter.";
        everyOrgToolsEl.style.display = "none";
        tabularUploadToolsEl.style.display = "none";
        Object.values(actionButtons).forEach((btn) => { btn.disabled = true; });
        return;
      }

      detailSystemEl.textContent = source.source_system || "-";
      detailModeEl.textContent = `${source.acquisition_mode || "-"} / ${source.auth_type || "-"}`;
      actionButtons.test.textContent = defaultActionLabels.test;
      actionButtons.paid.textContent = defaultActionLabels.paid;
      actionButtons.supporters.textContent = defaultActionLabels.supporters;
      actionButtons.full.textContent = defaultActionLabels.full;
      detailScheduleEl.textContent = source.schedule || "manual";
      detailLastSyncEl.textContent = run ? formatDateTime(run.completed_at || run.started_at || run.created_at) : "No sync yet";
      detailLastStatusEl.innerHTML = run ? statusChip(run.status) : "-";
      detailLastRecordsEl.textContent = run ? `${run.records_fetched_count || 0} records, ${run.duplicates_detected_count || 0} duplicates` : "-";
      sourceChipsEl.innerHTML = `
        <span class="chip ok">${source.source_system}</span>
        <span class="chip">${source.enabled ? "enabled" : "disabled"}</span>
        <span class="chip warn">${source.schedule || "manual"}</span>
        <span class="chip info">updated ${formatDateTime(source.updated_at)}</span>
      `;

      const isWebhookOnly = source.acquisition_mode === "webhook";
      actionButtons.test.disabled = false;
      actionButtons.paid.disabled = isWebhookOnly || source.source_system !== "onecause";
      actionButtons.supporters.disabled = isWebhookOnly || source.source_system !== "onecause";
      actionButtons.full.disabled = isWebhookOnly;
      sourceNoteEl.innerHTML = isWebhookOnly
        ? "This source is webhook-driven. Manual OneCause sync actions are disabled."
        : `Selected source <strong>${source.source_name}</strong>. Sync actions run against this source only.`;
      tabularUploadToolsEl.style.display = isWebhookOnly ? "none" : "grid";

      if (source.source_system === "everyorg") {
        everyOrgToolsEl.style.display = "grid";
        integrationNoteEl.innerHTML = `
          Every.org uses webhook-first ingestion for live donations and dashboard CSV import for historical donations.
          <br />
          <code>POST /api/v1/webhooks/everyorg/${source.id}?token=&lt;configured webhook token&gt;</code>
          <br />
          <code>POST /api/v1/everyorg/dashboard/sources/${source.id}/imports/donations</code>
        `;
      } else if (source.source_system === "pledge") {
        everyOrgToolsEl.style.display = "none";
        actionButtons.full.textContent = "Pull donations";
        integrationNoteEl.innerHTML = `
          Pledge uses API-based historic donation pulls through the shared canonical model.
          <br />
          <code>POST /api/v1/sources/${source.id}/test</code>
          <br />
          <code>POST /api/v1/sources/${source.id}/trigger</code>
        `;
      } else if (source.source_system === "gmail") {
        everyOrgToolsEl.style.display = "none";
        actionButtons.full.textContent = "Poll mailbox";
        integrationNoteEl.innerHTML = `
          Gmail uses mailbox polling through the generic trigger endpoint. Matching gift emails and supported attachments are normalized into the shared model.
          <br />
          <code>POST /api/v1/sources/${source.id}/test</code>
          <br />
          <code>POST /api/v1/sources/${source.id}/trigger</code>
        `;
      } else {
        everyOrgToolsEl.style.display = "none";
        integrationNoteEl.innerHTML = `
          OneCause uses authenticated sync endpoints from this console.
          <br />
          <code>POST /api/v1/sources/${source.id}/sync/onecause/paid-activities</code>
          <br />
          <code>POST /api/v1/sources/${source.id}/sync/onecause/supporters</code>
        `;
      }
    }

    function renderRecords() {
      const items = filteredRecords();
      renderDateSortState();
      if (!items.length) {
        recordsBody.innerHTML = `<tr><td colspan="13" class="empty">No canonical records match the selected source or filters.</td></tr>`;
        return;
      }
      recordsBody.innerHTML = items.map((item) => `
        <tr>
          <td>${item.source_system || ""}</td>
          <td>${item.record_type || ""}</td>
          <td>${item.source_record_id || item.gift_id || ""}</td>
          <td>${item.primary_name || item.donor_name || item.participant_name || ""}</td>
          <td>${item.primary_email || item.donor_email || ""}</td>
          <td>${item.campaign_name || item.challenge_name || item.campaign_id || item.challenge_id || ""}</td>
          <td>${item.related_entity_name || item.participant_name || item.related_entity_id || item.participant_id || ""}</td>
          <td>${item.team_name || item.team_id || ""}</td>
          <td>${item.amount || ""} ${item.currency || ""}</td>
          <td>${item.record_date || item.gift_date || ""}</td>
          <td>${item.receipt_number || ""}</td>
          <td>${extraMetadataSummary(item)}</td>
          <td>${statusChip(item.status || "")}</td>
        </tr>
      `).join("");
    }

    let refreshTimer = null;

    async function loadAll({ silent = false } = {}) {
      const [sources, runs, rawObjects, records] = await Promise.all([
        request("/api/v1/sources"),
        request("/api/v1/ingestion-runs?limit=500"),
        request("/api/v1/raw-objects?limit=500"),
        request("/api/v1/normalized/records?limit=500"),
      ]);
      state.sources = sources.items || [];
      state.runs = runs.items || [];
      state.rawObjects = rawObjects.items || [];
      state.records = records.items || [];
      renderSourceSelector();
      renderSourceDetails();
      renderSourceInsights();
      renderRecords();
      if (!silent) {
        print("Loaded operator state", {
          sources: state.sources.length,
          runs: state.runs.length,
          raw_objects: state.rawObjects.length,
          records: state.records.length,
        });
      }
    }

    function startAutoRefresh() {
      if (refreshTimer) clearInterval(refreshTimer);
      refreshTimer = setInterval(() => {
        loadAll({ silent: true }).catch((error) => print("Auto refresh failed", String(error)));
      }, 15000);
    }

    async function runAction(action) {
      const source = selectedSource();
      if (!source) {
        print("Action blocked", "No source selected.");
        return;
      }
      const routeMap = {
        test: `/api/v1/sources/${source.id}/test`,
        paid: `/api/v1/sources/${source.id}/sync/onecause/paid-activities`,
        supporters: `/api/v1/sources/${source.id}/sync/onecause/supporters`,
        full: `/api/v1/sources/${source.id}/trigger`,
      };
      const url = routeMap[action];
      const options = action === "full"
        ? { method: "POST", body: JSON.stringify({ run_type: "incremental", trigger_type: "manual" }) }
        : { method: "POST" };
      const data = await request(url, options);
      print(`${action} result`, data);
      await loadAll();
    }

    async function importEveryOrgDashboardCsv() {
      const source = selectedSource();
      const file = everyOrgImportFileEl.files && everyOrgImportFileEl.files[0];
      if (!source || source.source_system !== "everyorg") {
        print("Every.org import blocked", "Select an Every.org source first.");
        return;
      }
      if (!file) {
        print("Every.org import blocked", "Choose a dashboard CSV file first.");
        return;
      }
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`/api/v1/everyorg/dashboard/sources/${source.id}/imports/donations`, {
        method: "POST",
        body: formData,
      });
      const text = await response.text();
      let body = text;
      try { body = text ? JSON.parse(text) : {}; } catch (_) {}
      if (!response.ok) {
        print("Every.org dashboard import failed", body);
        throw new Error(typeof body === "string" ? body : JSON.stringify(body));
      }
      print("Every.org dashboard import completed", body);
      await loadAll();
    }

    async function importCanonicalTabularFile() {
      const source = selectedSource();
      const file = tabularImportFileEl.files && tabularImportFileEl.files[0];
      if (!source) {
        print("Tabular import blocked", "Select a source first.");
        return;
      }
      if (!file) {
        print("Tabular import blocked", "Choose a CSV, TSV, or XLSX file first.");
        return;
      }
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`/api/v1/files/sources/${source.id}/imports/canonical`, {
        method: "POST",
        body: formData,
      });
      const text = await response.text();
      let body = text;
      try { body = text ? JSON.parse(text) : {}; } catch (_) {}
      if (!response.ok) {
        print("Canonical file import failed", body);
        throw new Error(typeof body === "string" ? body : JSON.stringify(body));
      }
      print("Canonical file import completed", body);
      await loadAll();
    }

    sourceSelectorEl.addEventListener("change", () => {
      state.selectedSourceId = sourceSelectorEl.value;
      renderSourceDetails();
      renderSourceInsights();
      renderRecords();
    });
    dateSortButtonEl.addEventListener("click", () => {
      state.recordDateSortDirection = state.recordDateSortDirection === "asc" ? "desc" : "asc";
      renderRecords();
    });
    recordTypeFilterEl.addEventListener("change", renderRecords);
    recordStatusFilterEl.addEventListener("change", renderRecords);
    recordSearchEl.addEventListener("input", renderRecords);
    actionButtons.test.addEventListener("click", () => runAction("test").catch((error) => print("Test failed", String(error))));
    actionButtons.paid.addEventListener("click", () => runAction("paid").catch((error) => print("Paid activities failed", String(error))));
    actionButtons.supporters.addEventListener("click", () => runAction("supporters").catch((error) => print("Supporters failed", String(error))));
    actionButtons.full.addEventListener("click", () => runAction("full").catch((error) => print("Full sync failed", String(error))));
    document.getElementById("everyorg_import_btn").addEventListener("click", () => importEveryOrgDashboardCsv().catch((error) => print("Every.org import failed", String(error))));
    document.getElementById("tabular_import_btn").addEventListener("click", () => importCanonicalTabularFile().catch((error) => print("Canonical import failed", String(error))));
    document.getElementById("refresh_btn").addEventListener("click", () => loadAll().catch((error) => print("Refresh failed", String(error))));
    document.getElementById("run_due_btn").addEventListener("click", async () => {
      try {
        const data = await request("/api/v1/scheduler/run-due?force=true", { method: "POST" });
        print("Scheduler run", data);
        await loadAll();
      } catch (error) {
        print("Scheduler failed", String(error));
      }
    });

    document.addEventListener("visibilitychange", () => {
      if (!document.hidden) {
        loadAll({ silent: true }).catch((error) => print("Visibility refresh failed", String(error)));
      }
    });

    startAutoRefresh();
    loadAll().catch((error) => print("Initial load failed", String(error)));
  </script>
</body>
</html>"""
