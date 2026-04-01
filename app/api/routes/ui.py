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
      <h2>Every.org Public Profiles</h2>
      <div class="subhead">Live public nonprofit data fetched from Every.org for each configured Every.org source.</div>
      <div class="list" id="everyorg_profiles"></div>
    </section>

    <section class="panel" style="margin-top:20px;">
      <h2>Every.org Dashboard Import</h2>
      <div class="subhead">Historical donation backfill from the Every.org admin Download CSV. This is the reliable path for past dashboard donations because the public docs do not expose a historical donations list endpoint.</div>
      <div class="stack">
        <div class="row">
          <label for="everyorg_import_source">Every.org source</label>
          <select id="everyorg_import_source"></select>
        </div>
        <div class="row">
          <label for="everyorg_import_file">Dashboard donations CSV</label>
          <input id="everyorg_import_file" type="file" accept=".csv,text/csv" />
        </div>
        <div class="actions">
          <button id="everyorg_import_btn">Import dashboard CSV</button>
        </div>
      </div>
    </section>

    <section class="wide-grid">
      <div class="panel">
        <h2>Every.org Key Demo</h2>
        <div class="subhead">Docs-aligned demo routes that use EVERYORG_PUBLIC_KEY for public GET requests and BOTH keys for privileged POST requests.</div>
        <div class="stack">
          <div class="card" id="everyorg_demo_status"></div>
          <div class="row">
            <label for="everyorg_search_term">Search nonprofits</label>
            <input id="everyorg_search_term" value="education" />
          </div>
          <div class="row">
            <label for="everyorg_search_cause">Cause filter (optional)</label>
            <input id="everyorg_search_cause" placeholder="education, health, animals..." />
          </div>
          <div class="row">
            <label for="everyorg_search_take">Take</label>
            <input id="everyorg_search_take" type="number" min="1" max="50" value="5" />
          </div>
          <div class="actions">
            <button id="everyorg_search_btn">Search</button>
            <button id="everyorg_browse_btn" class="ghost">Browse Cause</button>
            <button id="everyorg_config_btn" class="ghost">Refresh Key Status</button>
          </div>
          <div class="list" id="everyorg_demo_results"></div>
        </div>
      </div>

      <div class="panel">
        <h2>Every.org Direct Endpoints</h2>
        <div class="subhead">Use identifiers from search results to fetch nonprofit and fundraiser data. Fundraiser creation is server-side only and uses HTTP Basic Auth with the public/private key pair.</div>
        <div class="stack">
          <div class="row">
            <label for="everyorg_identifier">Nonprofit identifier</label>
            <input id="everyorg_identifier" placeholder="slug, EIN, or nonprofit id" />
          </div>
          <div class="actions">
            <button id="everyorg_nonprofit_btn">Get nonprofit</button>
          </div>
          <div class="row">
            <label for="everyorg_fundraiser_nonprofit">Fundraiser nonprofit identifier</label>
            <input id="everyorg_fundraiser_nonprofit" placeholder="nonprofit slug or id" />
          </div>
          <div class="row">
            <label for="everyorg_fundraiser_identifier">Fundraiser identifier</label>
            <input id="everyorg_fundraiser_identifier" placeholder="fundraiser slug or id" />
          </div>
          <div class="actions">
            <button id="everyorg_fundraiser_btn" class="ghost">Get fundraiser</button>
            <button id="everyorg_raised_btn" class="ghost">Get raised</button>
          </div>
          <div class="row">
            <label for="everyorg_create_payload">Create fundraiser JSON</label>
            <textarea id="everyorg_create_payload">{
  "nonprofitId": "",
  "title": "Gift AI Demo Fundraiser",
  "description": "Demo fundraiser created from the Gift Ingestion Console.",
  "currency": "USD",
  "goal": 100000
}</textarea>
          </div>
          <div class="actions">
            <button id="everyorg_create_btn" class="alt">Create fundraiser</button>
          </div>
          <pre id="everyorg_demo_output"></pre>
        </div>
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
    const everyOrgProfilesEl = document.getElementById("everyorg_profiles");
    const everyOrgImportSourceEl = document.getElementById("everyorg_import_source");
    const everyOrgImportFileEl = document.getElementById("everyorg_import_file");
    const everyOrgDemoStatusEl = document.getElementById("everyorg_demo_status");
    const everyOrgDemoResultsEl = document.getElementById("everyorg_demo_results");
    const everyOrgDemoOutputEl = document.getElementById("everyorg_demo_output");
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
      if (source.acquisition_mode === "webhook") {
        return `
          <div class="muted">Webhook-only source. Data appears here after Every.org posts to the webhook URL.</div>
        `;
      }
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
      renderEveryOrgImportSources();
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

    function renderEveryOrgProfiles(items) {
      if (!items.length) {
        everyOrgProfilesEl.innerHTML = `<div class="card"><p class="muted">No Every.org sources yet.</p></div>`;
        return;
      }
      everyOrgProfilesEl.innerHTML = items.map((item) => {
        if (item.error) {
          return `
            <article class="card">
              <h3>${item.source_name}</h3>
              <div class="chips">
                <span class="chip bad">profile unavailable</span>
              </div>
              <div class="muted">${item.error}</div>
            </article>
          `;
        }
        const nonprofit = item.nonprofit || {};
        return `
          <article class="card">
            <h3>${nonprofit.name || item.source_name}</h3>
            <div class="chips">
              <span class="chip ok">${nonprofit.primarySlug || ""}</span>
              <span class="chip">${nonprofit.ein || "no ein"}</span>
              <span class="chip ${nonprofit.donationsEnabled ? "ok" : "warn"}">${nonprofit.donationsEnabled ? "donations enabled" : "donations disabled"}</span>
            </div>
            <div class="muted">Every.org ID: ${nonprofit.id || "n/a"}</div>
            <div class="muted">Location: ${nonprofit.locationAddress || "n/a"}</div>
            <div class="muted">Website: ${nonprofit.websiteUrl ? `<a href="${nonprofit.websiteUrl}" target="_blank" rel="noreferrer">${nonprofit.websiteUrl}</a>` : "n/a"}</div>
            <div class="muted">Profile: ${nonprofit.profileUrl ? `<a href="${nonprofit.profileUrl}" target="_blank" rel="noreferrer">${nonprofit.profileUrl}</a>` : "n/a"}</div>
            <p>${nonprofit.description || ""}</p>
          </article>
        `;
      }).join("");
    }

    function renderEveryOrgImportSources() {
      const everyOrgSources = Array.from(sourceIndex.values()).filter((source) => source.source_system === "everyorg");
      if (!everyOrgSources.length) {
        everyOrgImportSourceEl.innerHTML = `<option value="">No Every.org sources</option>`;
        everyOrgImportSourceEl.disabled = true;
        return;
      }
      everyOrgImportSourceEl.disabled = false;
      everyOrgImportSourceEl.innerHTML = everyOrgSources.map((source) => `
        <option value="${source.id}">${source.source_name} (#${source.id})</option>
      `).join("");
    }

    function everyOrgNonprofitsFromPayload(payload) {
      if (Array.isArray(payload?.nonprofits)) return payload.nonprofits;
      if (Array.isArray(payload?.data?.nonprofits)) return payload.data.nonprofits;
      const nonprofit = payload?.nonprofit || payload?.data?.nonprofit;
      return nonprofit ? [nonprofit] : [];
    }

    function renderEveryOrgDemoConfig(config) {
      everyOrgDemoStatusEl.innerHTML = `
        <div class="chips">
          <span class="chip ${config.public_key_configured ? "ok" : "bad"}">public key ${config.public_key_configured ? "configured" : "missing"}</span>
          <span class="chip ${config.private_key_configured ? "ok" : "warn"}">private key ${config.private_key_configured ? "configured" : "missing"}</span>
        </div>
        <div class="muted">Base URL: ${config.public_api_base_url}</div>
        <div class="muted">Per Every.org docs, public key auth covers public GET routes and the public/private pair is used for privileged POST routes.</div>
      `;
    }

    function renderEveryOrgDemoResults(payload) {
      const nonprofits = everyOrgNonprofitsFromPayload(payload);
      if (!nonprofits.length) {
        everyOrgDemoResultsEl.innerHTML = `<div class="card"><p class="muted">No nonprofit results yet.</p></div>`;
        return;
      }
      everyOrgDemoResultsEl.innerHTML = nonprofits.map((nonprofit) => `
        <article class="card">
          <h3>${nonprofit.name || nonprofit.primarySlug || nonprofit.slug || nonprofit.id || "Every.org nonprofit"}</h3>
          <div class="chips">
            <span class="chip ok">${nonprofit.primarySlug || nonprofit.slug || "no slug"}</span>
            <span class="chip">${nonprofit.ein || "no ein"}</span>
            <span class="chip ${nonprofit.donationsEnabled ? "ok" : "warn"}">${nonprofit.donationsEnabled ? "donations enabled" : "donations status n/a"}</span>
          </div>
          <div class="muted">ID: ${nonprofit.id || "n/a"}</div>
          <div class="muted">Location: ${nonprofit.locationAddress || nonprofit.location || "n/a"}</div>
          <div class="muted">Profile: ${nonprofit.profileUrl ? `<a href="${nonprofit.profileUrl}" target="_blank" rel="noreferrer">${nonprofit.profileUrl}</a>` : "n/a"}</div>
          <div class="muted">Website: ${nonprofit.websiteUrl ? `<a href="${nonprofit.websiteUrl}" target="_blank" rel="noreferrer">${nonprofit.websiteUrl}</a>` : "n/a"}</div>
          <p>${nonprofit.description || ""}</p>
        </article>
      `).join("");
    }

    function renderEveryOrgDemoOutput(payload) {
      everyOrgDemoOutputEl.textContent = JSON.stringify(payload, null, 2);
    }

    async function loadSources() {
      const data = await request("/api/v1/sources");
      renderSources(data.items);
      await loadEveryOrgProfiles();
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

    async function loadEveryOrgProfiles() {
      const everyOrgSources = Array.from(sourceIndex.values()).filter((source) => source.source_system === "everyorg");
      if (!everyOrgSources.length) {
        renderEveryOrgProfiles([]);
        return;
      }
      const profiles = await Promise.all(everyOrgSources.map(async (source) => {
        try {
          const data = await request(`/api/v1/everyorg/sources/${source.id}/nonprofit`);
          return {
            source_name: source.source_name,
            nonprofit: data.nonprofit,
          };
        } catch (error) {
          return {
            source_name: source.source_name,
            error: String(error),
          };
        }
      }));
      renderEveryOrgProfiles(profiles);
    }

    async function loadEveryOrgDemoConfig() {
      const data = await request("/api/v1/everyorg/demo/config");
      renderEveryOrgDemoConfig(data);
      print("Every.org demo config", data);
    }

    async function runEveryOrgSearch() {
      const searchTerm = document.getElementById("everyorg_search_term").value.trim();
      if (!searchTerm) {
        print("Every.org search", "Search term is required.");
        return;
      }
      const take = document.getElementById("everyorg_search_take").value.trim() || "5";
      const cause = document.getElementById("everyorg_search_cause").value.trim();
      const suffix = cause ? `?take=${encodeURIComponent(take)}&cause=${encodeURIComponent(cause)}` : `?take=${encodeURIComponent(take)}`;
      const data = await request(`/api/v1/everyorg/demo/search/${encodeURIComponent(searchTerm)}${suffix}`);
      renderEveryOrgDemoResults(data);
      renderEveryOrgDemoOutput(data);
      print(`Every.org search: ${searchTerm}`, data);
    }

    async function runEveryOrgBrowse() {
      const cause = document.getElementById("everyorg_search_cause").value.trim() || document.getElementById("everyorg_search_term").value.trim();
      if (!cause) {
        print("Every.org browse", "Cause is required.");
        return;
      }
      const take = document.getElementById("everyorg_search_take").value.trim() || "5";
      const data = await request(`/api/v1/everyorg/demo/browse/${encodeURIComponent(cause)}?take=${encodeURIComponent(take)}`);
      renderEveryOrgDemoResults(data);
      renderEveryOrgDemoOutput(data);
      print(`Every.org browse: ${cause}`, data);
    }

    async function runEveryOrgNonprofitLookup() {
      const identifier = document.getElementById("everyorg_identifier").value.trim();
      if (!identifier) {
        print("Every.org nonprofit", "Nonprofit identifier is required.");
        return;
      }
      const data = await request(`/api/v1/everyorg/demo/nonprofit/${encodeURIComponent(identifier)}`);
      renderEveryOrgDemoResults(data);
      renderEveryOrgDemoOutput(data);
      print(`Every.org nonprofit: ${identifier}`, data);
    }

    async function runEveryOrgFundraiserDetails(pathSuffix = "") {
      const nonprofitIdentifier = document.getElementById("everyorg_fundraiser_nonprofit").value.trim();
      const fundraiserIdentifier = document.getElementById("everyorg_fundraiser_identifier").value.trim();
      if (!nonprofitIdentifier || !fundraiserIdentifier) {
        print("Every.org fundraiser", "Both fundraiser identifiers are required.");
        return;
      }
      const data = await request(`/api/v1/everyorg/demo/fundraisers/${encodeURIComponent(nonprofitIdentifier)}/${encodeURIComponent(fundraiserIdentifier)}${pathSuffix}`);
      renderEveryOrgDemoOutput(data);
      print(`Every.org fundraiser${pathSuffix || ""}: ${nonprofitIdentifier}/${fundraiserIdentifier}`, data);
    }

    async function runEveryOrgCreateFundraiser() {
      let payload = {};
      try {
        payload = JSON.parse(document.getElementById("everyorg_create_payload").value || "{}");
      } catch (error) {
        print("Invalid fundraiser JSON", String(error));
        return;
      }
      const data = await request("/api/v1/everyorg/demo/fundraiser", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      renderEveryOrgDemoOutput(data);
      print("Every.org fundraiser created", data);
    }

    async function importEveryOrgDashboardCsv() {
      const sourceId = everyOrgImportSourceEl.value;
      const file = everyOrgImportFileEl.files && everyOrgImportFileEl.files[0];
      if (!sourceId) {
        print("Every.org dashboard import", "Choose an Every.org source first.");
        return;
      }
      if (!file) {
        print("Every.org dashboard import", "Choose a CSV file from the Every.org dashboard download.");
        return;
      }
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`/api/v1/everyorg/dashboard/sources/${sourceId}/imports/donations`, {
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
      await Promise.all([loadRuns(), loadRawObjects(), loadGifts(), loadSupporters()]);
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
    document.getElementById("refresh_btn").addEventListener("click", () => Promise.all([loadSources(), loadRuns(), loadRawObjects(), loadGifts(), loadSupporters(), loadEveryOrgDemoConfig()]).catch((error) => print("Refresh failed", String(error))));
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
    document.getElementById("everyorg_search_btn").addEventListener("click", () => runEveryOrgSearch().catch((error) => print("Every.org search failed", String(error))));
    document.getElementById("everyorg_browse_btn").addEventListener("click", () => runEveryOrgBrowse().catch((error) => print("Every.org browse failed", String(error))));
    document.getElementById("everyorg_config_btn").addEventListener("click", () => loadEveryOrgDemoConfig().catch((error) => print("Every.org config failed", String(error))));
    document.getElementById("everyorg_import_btn").addEventListener("click", () => importEveryOrgDashboardCsv().catch((error) => print("Every.org dashboard import failed", String(error))));
    document.getElementById("everyorg_nonprofit_btn").addEventListener("click", () => runEveryOrgNonprofitLookup().catch((error) => print("Every.org nonprofit failed", String(error))));
    document.getElementById("everyorg_fundraiser_btn").addEventListener("click", () => runEveryOrgFundraiserDetails().catch((error) => print("Every.org fundraiser failed", String(error))));
    document.getElementById("everyorg_raised_btn").addEventListener("click", () => runEveryOrgFundraiserDetails("/raised").catch((error) => print("Every.org fundraiser raised failed", String(error))));
    document.getElementById("everyorg_create_btn").addEventListener("click", () => runEveryOrgCreateFundraiser().catch((error) => print("Every.org create fundraiser failed", String(error))));

    Promise.all([loadSources(), loadRuns(), loadRawObjects(), loadGifts(), loadSupporters(), loadEveryOrgDemoConfig()]).catch((error) => print("Initial load failed", String(error)));
  </script>
</body>
</html>"""
