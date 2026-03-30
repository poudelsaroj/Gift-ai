"""Simple operator UI."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def operator_console() -> str:
    """Render a small operator console for source and sync workflows."""
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Gift Ingestion Console</title>
  <style>
    :root {
      --bg: #f4efe7;
      --panel: #fffaf4;
      --ink: #1e2a2a;
      --muted: #5f6b6b;
      --accent: #0d6b63;
      --accent-2: #d98b3a;
      --line: #dbcdbb;
      --danger: #9e3d2d;
      --shadow: 0 18px 50px rgba(45, 34, 22, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(217,139,58,0.16), transparent 28%),
        radial-gradient(circle at top right, rgba(13,107,99,0.14), transparent 26%),
        linear-gradient(180deg, #f7f1e8 0%, var(--bg) 100%);
    }
    .shell {
      max-width: 1180px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }
    .hero {
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 20px;
      align-items: end;
      margin-bottom: 24px;
    }
    .hero-card, .panel {
      background: rgba(255,250,244,0.92);
      border: 1px solid var(--line);
      border-radius: 22px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(8px);
    }
    .hero-card {
      padding: 28px;
    }
    h1 {
      margin: 0 0 10px;
      font-size: clamp(2.2rem, 6vw, 4.4rem);
      line-height: 0.95;
      letter-spacing: -0.04em;
    }
    .hero p, .meta, label, small { color: var(--muted); }
    .meta {
      display: flex;
      gap: 14px;
      flex-wrap: wrap;
      font-size: 0.92rem;
      margin-top: 16px;
    }
    .hero-stats {
      padding: 24px;
      display: grid;
      gap: 14px;
    }
    .banner {
      margin-top: 18px;
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px 18px;
      background: linear-gradient(135deg, rgba(13,107,99,0.08), rgba(217,139,58,0.12));
    }
    .stat {
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 14px 16px;
      background: rgba(255,255,255,0.45);
    }
    .stat strong {
      display: block;
      font-size: 1.8rem;
      color: var(--accent);
    }
    .grid {
      display: grid;
      grid-template-columns: 380px 1fr;
      gap: 20px;
    }
    .wide-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-top: 20px;
    }
    .triple-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 20px;
      margin-top: 20px;
    }
    .panel {
      padding: 20px;
    }
    .panel h2 {
      margin: 0 0 12px;
      font-size: 1.3rem;
    }
    .subhead {
      margin: -4px 0 14px;
      color: var(--muted);
      font-size: 0.92rem;
    }
    .stack { display: grid; gap: 12px; }
    .row { display: grid; gap: 8px; }
    input, select, textarea, button {
      font: inherit;
    }
    input, select, textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px 14px;
      background: #fffdf9;
      color: var(--ink);
    }
    textarea {
      min-height: 118px;
      resize: vertical;
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
      transition: transform 160ms ease, opacity 160ms ease, background 160ms ease;
    }
    button.alt { background: var(--accent-2); }
    button.ghost {
      background: transparent;
      color: var(--accent);
      border: 1px solid var(--line);
    }
    button:hover { transform: translateY(-1px); }
    button:disabled { opacity: 0.6; cursor: default; transform: none; }
    .list {
      display: grid;
      gap: 12px;
      max-height: 640px;
      overflow: auto;
      padding-right: 4px;
    }
    .table-wrap {
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: rgba(255,255,255,0.45);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 720px;
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
      background: #f8f1e6;
      z-index: 1;
    }
    .card {
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px;
      background: rgba(255,255,255,0.54);
    }
    .card h3 {
      margin: 0 0 6px;
      font-size: 1.1rem;
    }
    .chips {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin: 8px 0 12px;
    }
    .chip {
      font-size: 0.8rem;
      padding: 4px 9px;
      border-radius: 999px;
      background: #efe6d8;
      color: var(--ink);
    }
    .chip.ok { background: rgba(13,107,99,0.14); color: var(--accent); }
    .chip.warn { background: rgba(217,139,58,0.18); color: #915400; }
    .chip.bad { background: rgba(158,61,45,0.12); color: var(--danger); }
    .chip.info { background: rgba(40,80,120,0.12); color: #295275; }
    pre {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      border-radius: 14px;
      padding: 14px;
      background: #1f2626;
      color: #f9f4eb;
      font-size: 0.88rem;
      min-height: 120px;
      overflow: auto;
    }
    .muted { color: var(--muted); }
    @media (max-width: 980px) {
      .hero, .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <div class="hero-card">
        <div class="chip ok">Single-Organization Phase 1</div>
        <h1>Gift Ingestion Console</h1>
        <p>Create sources, validate OneCause connectivity, trigger syncs, and inspect recent runs without leaving the browser.</p>
        <div class="meta">
          <span>Swagger: <a href="/docs">/docs</a></span>
          <span>OpenAPI: <a href="/openapi.json">/openapi.json</a></span>
          <span>Health: <a href="/api/v1/health">/api/v1/health</a></span>
        </div>
        <div class="banner">
          <strong>Portal v1 vs v2</strong>
          <div class="muted">These are local source revisions in this app, not official OneCause products. `Portal v1` was the first guessed portal mapping. `Portal v2` is the HAR-backed source that uses `donations` and `participants` correctly.</div>
        </div>
      </div>
      <div class="hero-stats">
        <div class="stat">
          <span class="muted">Recommended OneCause mode</span>
          <strong>API Key</strong>
          <small>Use access-token mode only when official API credentials are unavailable.</small>
        </div>
        <div class="stat">
          <span class="muted">Raw lineage</span>
          <strong>Preserved</strong>
          <small>Payloads remain addressable by source, date, run, object type, and object id.</small>
        </div>
      </div>
    </section>

    <section class="grid">
      <div class="panel">
        <h2>Create OneCause Source</h2>
        <div class="stack">
          <div class="row">
            <label for="source_name">Source name</label>
            <input id="source_name" value="OneCause Primary" />
          </div>
          <div class="row">
            <label for="auth_mode">Auth mode</label>
            <select id="auth_mode">
              <option value="api_key">API key</option>
              <option value="access_token">Access token fallback</option>
            </select>
          </div>
          <div class="row">
            <label for="schedule">Schedule</label>
            <select id="schedule">
              <option value="">Manual only</option>
              <option value="daily">Daily</option>
              <option value="hourly">Hourly</option>
              <option value="every_6_hours">Every 6 hours</option>
            </select>
          </div>
          <div class="row">
            <label for="config_json">Config JSON override</label>
            <textarea id="config_json">{}</textarea>
          </div>
          <div class="actions">
            <button id="create_btn">Create source</button>
            <button id="refresh_btn" class="ghost">Refresh list</button>
            <button id="run_due_btn" class="ghost">Run due schedules</button>
          </div>
          <small>Leave config empty to use `.env` defaults. Explicit values here override `.env`.</small>
        </div>
      </div>

      <div class="panel">
        <h2>Sources</h2>
        <div class="subhead">Use `Portal v2` or any source marked <code>HAR-backed</code>. Legacy portal sources should be ignored or disabled.</div>
        <div class="list" id="sources_list"></div>
      </div>
    </section>

    <section class="wide-grid">
      <div class="panel">
        <h2>Recent Runs</h2>
        <div class="subhead">Operator run history with status, fetched counts, and duplicate counts.</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Run</th>
                <th>Source</th>
                <th>Status</th>
                <th>Trigger</th>
                <th>Objects</th>
                <th>Records</th>
                <th>Duplicates</th>
              </tr>
            </thead>
            <tbody id="runs_body"></tbody>
          </table>
        </div>
      </div>

      <div class="panel">
        <h2>Recent Raw Objects</h2>
        <div class="subhead">Stored raw payload lineage. Open payload links for the exact JSON that was fetched.</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Source</th>
                <th>Type</th>
                <th>External ID</th>
                <th>Fetched</th>
                <th>Duplicate</th>
                <th>Payload</th>
              </tr>
            </thead>
            <tbody id="raw_body"></tbody>
          </table>
        </div>
      </div>
    </section>

    <section class="panel" style="margin-top:20px;">
      <h2>Normalized Gifts</h2>
      <div class="subhead">Donation transactions normalized from OneCause `donations`. Donor is the giver. Supporter attribution lives in the raw payload and supporter table.</div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Gift ID</th>
              <th>Donor</th>
              <th>Challenge</th>
              <th>Amount</th>
              <th>Date</th>
              <th>Payment</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody id="gifts_body"></tbody>
        </table>
      </div>
    </section>

    <section class="panel" style="margin-top:20px;">
      <h2>Normalized Supporters</h2>
      <div class="subhead">Supporters are OneCause participants or fundraisers. They are not automatically donors.</div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Supporter</th>
              <th>Team</th>
              <th>Donation Total</th>
              <th>Donation Count</th>
              <th>Event IDs</th>
              <th>Accepted At</th>
            </tr>
          </thead>
          <tbody id="supporters_body"></tbody>
        </table>
      </div>
    </section>

    <section class="panel" style="margin-top:20px;">
      <h2>Console Output</h2>
      <pre id="console"></pre>
    </section>
  </div>

  <script>
    const consoleEl = document.getElementById("console");
    const listEl = document.getElementById("sources_list");
    const runsBody = document.getElementById("runs_body");
    const rawBody = document.getElementById("raw_body");
    const giftsBody = document.getElementById("gifts_body");
    const supportersBody = document.getElementById("supporters_body");
    let sourceIndex = new Map();

    function sourceLabel(source) {
      const cfg = source.config_json || {};
      const templates = cfg.endpoint_templates || {};
      const isHarBacked = templates.paid_activities && templates.paid_activities.includes("/donations");
      if (isHarBacked) return "HAR-backed";
      return "Legacy";
    }

    function formatDateTime(value) {
      if (!value) return "";
      try {
        return new Date(value).toLocaleString();
      } catch (_) {
        return value;
      }
    }

    function statusChip(status) {
      const tone = status === "completed" || status === "succeeded" || status === "enabled" ? "ok"
        : status === "failed" || status === "disabled" ? "bad"
        : "warn";
      return `<span class="chip ${tone}">${status}</span>`;
    }

    function print(label, data) {
      const block = typeof data === "string" ? data : JSON.stringify(data, null, 2);
      consoleEl.textContent = `[${new Date().toLocaleTimeString()}] ${label}\\n${block}\\n\\n` + consoleEl.textContent;
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

    function sourceActions(source) {
      return `
        <div class="actions">
          <button data-action="test" data-id="${source.id}" class="ghost">Test</button>
          <button data-action="paid" data-id="${source.id}">Paid activities</button>
          <button data-action="supporters" data-id="${source.id}" class="alt">Supporters</button>
          <button data-action="full" data-id="${source.id}" class="ghost">Full sync</button>
        </div>
      `;
    }

    function renderSources(items) {
      sourceIndex = new Map(items.map((source) => [source.id, source]));
      if (!items.length) {
        listEl.innerHTML = `<div class="card"><p class="muted">No sources yet.</p></div>`;
        return;
      }
      listEl.innerHTML = items.map((source) => `
        <article class="card">
          <h3>${source.source_name}</h3>
          <div class="chips">
            <span class="chip ok">${source.source_system}</span>
            <span class="chip">${source.acquisition_mode}</span>
            <span class="chip ${source.enabled ? "ok" : "bad"}">${source.enabled ? "enabled" : "disabled"}</span>
            <span class="chip warn">${source.schedule || "manual"}</span>
            <span class="chip info">${sourceLabel(source)}</span>
          </div>
          <div class="muted">Source ID: ${source.id}</div>
          <div class="muted">Auth: ${source.auth_type} | Client: ${source.config_json?.client_id || source.config_json?.organization_id || "n/a"}</div>
          <div class="muted">Challenge: ${source.config_json?.challenge_id || "n/a"}</div>
          <div class="muted">Updated: ${source.updated_at}</div>
          ${sourceActions(source)}
        </article>
      `).join("");
    }

    function renderRuns(items) {
      if (!items.length) {
        runsBody.innerHTML = `<tr><td colspan="6" class="muted">No runs yet.</td></tr>`;
        return;
      }
      runsBody.innerHTML = items.map((run) => `
        <tr>
          <td>${run.id}</td>
          <td>${sourceIndex.get(run.source_id)?.source_name || run.source_id}</td>
          <td>${statusChip(run.status)}</td>
          <td>${run.trigger_type}</td>
          <td>${(run.metadata_json?.fetched_object_types || []).join(", ")}</td>
          <td>${run.records_fetched_count}</td>
          <td>${run.duplicates_detected_count}</td>
        </tr>
      `).join("");
    }

    function renderRawObjects(items) {
      if (!items.length) {
        rawBody.innerHTML = `<tr><td colspan="6" class="muted">No raw objects yet.</td></tr>`;
        return;
      }
      rawBody.innerHTML = items.slice(0, 20).map((item) => `
        <tr>
          <td>${item.id}</td>
          <td>${sourceIndex.get(item.source_id)?.source_name || item.source_id}</td>
          <td>${item.external_object_type}</td>
          <td>${item.external_object_id || ""}</td>
          <td>${formatDateTime(item.fetched_at)}</td>
          <td>${statusChip(item.duplicate_status)}</td>
          <td><a href="/api/v1/raw-objects/${item.id}/payload" target="_blank" rel="noreferrer">view</a></td>
        </tr>
      `).join("");
    }

    function renderGifts(items) {
      if (!items.length) {
        giftsBody.innerHTML = `<tr><td colspan="6" class="muted">No normalized gifts yet.</td></tr>`;
        return;
      }
      giftsBody.innerHTML = items.slice(0, 20).map((item) => `
        <tr>
          <td>${item.gift_id || ""}</td>
          <td>${item.donor_name || ""}</td>
          <td>${item.memo || ""}</td>
          <td>${item.amount || ""} ${item.currency || ""}</td>
          <td>${item.gift_date || ""}</td>
          <td>${item.payment_type || ""}</td>
          <td>${statusChip(item.status || "")}</td>
        </tr>
      `).join("");
    }

    function renderSupporters(items) {
      if (!items.length) {
        supportersBody.innerHTML = `<tr><td colspan="6" class="muted">No normalized supporters yet.</td></tr>`;
        return;
      }
      supportersBody.innerHTML = items.slice(0, 20).map((item) => `
        <tr>
          <td>${item.supporter_name || ""}</td>
          <td>${item.team_name || ""}</td>
          <td>${item.donation_amount || ""}</td>
          <td>${item.donation_count || ""}</td>
          <td>${item.event_ids || item.event_id || ""}</td>
          <td>${formatDateTime(item.accepted)}</td>
        </tr>
      `).join("");
    }

    async function loadSources() {
      const data = await request("/api/v1/sources");
      renderSources(data.items);
      print("Loaded sources", data);
    }

    async function loadRuns() {
      const data = await request("/api/v1/ingestion-runs");
      renderRuns(data.items);
    }

    async function loadRawObjects() {
      const data = await request("/api/v1/raw-objects");
      renderRawObjects(data.items);
    }

    async function loadGifts() {
      const data = await request("/api/v1/normalized/gifts");
      renderGifts(data.items);
    }

    async function loadSupporters() {
      const data = await request("/api/v1/normalized/supporters");
      renderSupporters(data.items);
    }

    async function createSource() {
      const sourceName = document.getElementById("source_name").value.trim();
      const authMode = document.getElementById("auth_mode").value;
      let configJson = {};
      try {
        configJson = JSON.parse(document.getElementById("config_json").value || "{}");
      } catch (error) {
        print("Invalid JSON", String(error));
        return;
      }
      configJson.auth_mode = authMode;
      const payload = {
        source_name: sourceName,
        source_system: "onecause",
        acquisition_mode: "api",
        auth_type: authMode,
        enabled: true,
        schedule: document.getElementById("schedule").value || null,
        config_json: configJson,
      };
      const data = await request("/api/v1/sources", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      print("Source created", data);
      await loadSources();
      await loadRuns();
      await loadRawObjects();
      await loadGifts();
      await loadSupporters();
    }

    async function runAction(action, id) {
      const map = {
        test: { url: `/api/v1/sources/${id}/test`, method: "POST" },
        paid: { url: `/api/v1/sources/${id}/sync/onecause/paid-activities`, method: "POST" },
        supporters: { url: `/api/v1/sources/${id}/sync/onecause/supporters`, method: "POST" },
        full: { url: `/api/v1/sources/${id}/sync/onecause/full`, method: "POST" },
      };
      const cfg = map[action];
      const data = await request(cfg.url, { method: cfg.method });
      print(`${action} result for source ${id}`, data);
      await loadSources();
      await loadRuns();
      await loadRawObjects();
      await loadGifts();
      await loadSupporters();
    }

    document.getElementById("create_btn").addEventListener("click", () => createSource().catch((error) => print("Create failed", String(error))));
    document.getElementById("refresh_btn").addEventListener("click", () => Promise.all([loadSources(), loadRuns(), loadRawObjects(), loadGifts(), loadSupporters()]).catch((error) => print("Refresh failed", String(error))));
    document.getElementById("run_due_btn").addEventListener("click", async () => {
      try {
        const data = await request("/api/v1/scheduler/run-due", { method: "POST" });
        print("Scheduler run", data);
        await Promise.all([loadSources(), loadRuns(), loadRawObjects(), loadGifts(), loadSupporters()]);
      } catch (error) {
        print("Scheduler failed", String(error));
      }
    });
    listEl.addEventListener("click", (event) => {
      const btn = event.target.closest("button[data-action]");
      if (!btn) return;
      runAction(btn.dataset.action, btn.dataset.id).catch((error) => print("Action failed", String(error)));
    });

    Promise.all([loadSources(), loadRuns(), loadRawObjects(), loadGifts(), loadSupporters()]).catch((error) => print("Initial load failed", String(error)));
  </script>
</body>
</html>"""
