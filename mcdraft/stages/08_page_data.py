latest_results_gw = (
    dashboard_target_gw
    if dashboard_game_state in ("upcoming", "live")
    else (result_gameweeks[-1] if result_gameweeks else None)
)


latest_totw_gw = (
    finished_gws[-1]
    if finished_gws
    else None
)


# ============================================================
# CSS
# ============================================================

css = r"""
:root {
    --bg: #070b14;
    --bg-secondary: #0b1120;
    --card: #111827;
    --card-hover: #172033;
    --border: #263244;
    --border-light: #334155;
    --text: #e5e7eb;
    --muted: #94a3b8;
    --muted-dark: #64748b;
    --accent: #38bdf8;
    --accent-dark: #0284c7;
    --green: #4ade80;
    --red: #f87171;
    --gold: #facc15;
}

* {
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
}

body {
    margin: 0;
    padding: 0;
    background: var(--bg);
    color: var(--text);
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Arial,
        sans-serif;
    min-height: 100vh;
}

button,
input {
    font-family: inherit;
}

.app-shell {
    min-height: 100vh;
}


/* ============================================================
   HEADER
   ============================================================ */

.header {
    background:
        linear-gradient(
            135deg,
            #0f172a,
            #111827
        );
    border-bottom: 1px solid var(--border);
    padding: 24px 32px 0;
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(16px);
}

.header-top {
    max-width: 1500px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    padding-bottom: 20px;
}

.logo {
    font-size: 25px;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.5px;
}

.logo span {
    color: var(--accent);
}

.header-meta {
    color: var(--muted);
    font-size: 13px;
    text-align: right;
}

.global-search-wrap { position:relative; flex:1; max-width:520px; margin-left:auto; }
.global-search-input { width:100%; background:var(--bg-secondary); color:var(--text); border:1px solid var(--border-light); border-radius:10px; padding:11px 14px; font-size:14px; }
.global-search-input:focus { outline:2px solid var(--accent); outline-offset:1px; }
.global-search-results { display:none; position:absolute; top:calc(100% + 7px); left:0; right:0; background:var(--card); border:1px solid var(--border-light); border-radius:12px; box-shadow:0 16px 45px rgba(0,0,0,.4); max-height:360px; overflow:auto; z-index:500; }
.global-search-results.active { display:block; }
.global-search-result { display:flex; justify-content:space-between; gap:14px; padding:11px 13px; cursor:pointer; border-bottom:1px solid var(--border); }
.global-search-result:last-child { border-bottom:none; }
.global-search-result:hover { background:var(--card-hover); }
.global-search-result strong { color:var(--text); font-size:13px; }
.global-search-result span { color:var(--muted); font-size:11px; text-align:right; }
.search-hit { outline:2px solid var(--accent); outline-offset:3px; transition:outline .2s ease; }
.global-search-tabs { display:flex; gap:5px; padding-top:6px; }
.global-search-tab { border:1px solid var(--border); background:var(--bg-secondary); color:var(--muted); border-radius:999px; padding:5px 9px; font-size:10px; font-weight:800; cursor:pointer; }
.global-search-tab.active { color:var(--text); border-color:var(--accent); background:var(--card-hover); }
.analytics-average-toggle { display:inline-flex; align-items:center; gap:8px; margin-top:12px; color:var(--muted); font-size:12px; font-weight:800; cursor:pointer; }
.analytics-average-marker { display:none; position:absolute; top:-2px; bottom:-2px; width:2px; background:#f8fafc; opacity:.75; z-index:3; }
.analytics-bar-track { position:relative; }
.analytics-average-delta,.analytics-average-key,.analytics-average-series { display:none; }
#page-analytics.show-league-average .analytics-average-marker,
#page-analytics.show-league-average .analytics-average-delta,
#page-analytics.show-league-average .analytics-average-key { display:block; }
#page-analytics.show-league-average .analytics-average-series { display:block; fill:none; stroke:#f8fafc; stroke-width:3; stroke-dasharray:8 6; opacity:.85; }
.analytics-average-key { color:var(--muted); font-size:11px; margin-top:8px; }
.analytics-average-delta { color:var(--muted); font-size:10px; white-space:nowrap; }
.motm-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:12px; }
.motm-card { border:1px solid var(--border); background:var(--bg-secondary); border-radius:12px; padding:15px; }
.motm-card h3 { margin:5px 0 6px; }
.motm-card p { margin:7px 0 0; color:var(--muted); font-size:12px; }
.motm-stat { font-weight:800; color:#e2e8f0; font-size:12px; }
.archetype-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.archetype-card{border:1px solid var(--border);background:var(--bg-secondary);border-radius:12px;padding:14px}
.archetype-card span{display:inline-flex;font-size:10px;font-weight:900;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);background:rgba(56,189,248,.09);border:1px solid rgba(56,189,248,.22);border-radius:999px;padding:4px 8px;margin-bottom:8px}
.archetype-card strong{display:block;color:var(--text);font-size:15px}.archetype-card p{margin:5px 0 0;color:var(--muted);font-size:12px;line-height:1.45}
.record-chase-summary{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px}.record-chase-summary span{background:var(--bg-secondary);border:1px solid var(--border);border-radius:999px;padding:7px 10px;color:var(--muted);font-size:11px}.record-chase-summary strong{color:var(--text)}
.record-chase-list{display:flex;flex-direction:column;gap:7px}.record-chase-row{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:10px 12px;border:1px solid var(--border);border-radius:10px;background:var(--bg-secondary)}.record-chase-row strong,.record-chase-row span,.record-chase-row b,.record-chase-row small{display:block}.record-chase-row span,.record-chase-row small{color:var(--muted);font-size:11px}.record-chase-row b{color:var(--text);text-align:right}.record-chase-row small{text-align:right}
.share-card-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.share-card{position:relative;min-height:155px;padding:16px;border:1px solid var(--border-light);border-radius:14px;background:linear-gradient(145deg,#0f172a,#172033);overflow:hidden}.share-card:after{content:'';position:absolute;width:80px;height:80px;border-radius:50%;background:rgba(56,189,248,.08);right:-24px;top:-24px}.share-card h3{font-size:18px;margin:7px 0}.share-card p{color:var(--muted);font-size:12px;min-height:34px}.share-card-button{border:1px solid var(--border-light);background:var(--card);color:var(--text);border-radius:8px;padding:7px 10px;font-weight:800;cursor:pointer}.share-card-button:hover{border-color:var(--accent);color:var(--text)}
@media(max-width:900px){.share-card-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.archetype-grid{grid-template-columns:1fr}}
@media(max-width:560px){.share-card-grid{grid-template-columns:1fr}}
.milestone-list { display:flex; flex-direction:column; gap:8px; max-height:520px; overflow:auto; }
.milestone-row { display:grid; grid-template-columns:58px 1fr; gap:10px; align-items:start; padding:10px 12px; border:1px solid var(--border); border-radius:10px; background:var(--bg-secondary); }
.milestone-gw { color:var(--accent); font-weight:900; font-size:12px; }
.milestone-row strong,.milestone-row span,.milestone-row small { display:block; }
.milestone-row span { color:#e2e8f0; font-weight:800; }
.milestone-row small { color:var(--muted); margin-top:2px; }
.season-slider-head { display:flex; justify-content:space-between; gap:12px; align-items:flex-start; }
.season-slider-head h2 { margin-bottom:4px; }
.season-gw-slider { width:100%; accent-color:var(--accent); margin:10px 0 16px; }
.season-slider-summary { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin-bottom:14px; }
.season-slider-summary div { background:var(--bg-secondary); border:1px solid var(--border); border-radius:10px; padding:10px; }
.season-slider-summary span,.season-slider-summary strong { display:block; }
.season-slider-summary span { color:var(--muted); font-size:10px; text-transform:uppercase; letter-spacing:.05em; }
.season-slider-summary strong { margin-top:3px; }


.nav {
    max-width: 1500px;
    margin: 0 auto;
    display: flex;
    gap: 4px;
    overflow-x: auto;
}

.nav-button {
    background: transparent;
    border: none;
    color: var(--muted);
    padding: 13px 20px;
    cursor: pointer;
    border-radius: 8px 8px 0 0;
    font-size: 14px;
    font-weight: 600;
    white-space: nowrap;
    transition:
        background 0.15s ease,
        color 0.15s ease;
}

.nav-button:hover {
    background: var(--card-hover);
    color: var(--text);
}

.nav-button.active {
    background: var(--card);
    color: var(--text);
    box-shadow:
        inset 0 -3px 0 var(--accent);
}


/* ============================================================
   MAIN
   ============================================================ */

.main {
    max-width: 1500px;
    margin: 0 auto;
    padding: 30px;
}

.page {
    display: none;
    animation: pageIn 0.2s ease;
}

.page.active {
    display: block;
}

@keyframes pageIn {
    from {
        opacity: 0;
        transform: translateY(5px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.page-heading {
    margin-bottom: 25px;
}

.page-heading h1 {
    margin: 0 0 6px;
    font-size: 30px;
    color: var(--text);
}

.page-heading p {
    margin: 0;
    color: var(--muted);
}


/* ============================================================
   CARDS
   ============================================================ */

.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 24px;
    overflow: hidden;
}

.card h2 {
    margin: 0 0 18px;
    font-size: 19px;
    color: var(--text);
}

.card h3 {
    margin: 0 0 15px;
    color: var(--text);
}

.card-description {
    color: var(--muted);
    font-size: 14px;
    margin: -8px 0 18px;
}

.notice {
    background: var(--card-hover);
    border-left: 4px solid var(--accent);
    padding: 14px;
    border-radius: 8px;
    color: var(--muted);
    margin: 10px 0;
}

.confidence-badge {
    display:inline-flex; align-items:center; gap:5px; margin-top:5px; padding:3px 8px;
    border-radius:999px; font-size:10px; font-weight:800; letter-spacing:.02em;
    border:1px solid rgba(255,255,255,.12); white-space:nowrap;
}
.confidence-very-low { background:rgba(239,68,68,.12); }
.confidence-low { background:rgba(245,158,11,.12); }
.confidence-moderate { background:rgba(234,179,8,.12); }
.confidence-good { background:rgba(34,197,94,.12); }
.confidence-high { background:rgba(16,185,129,.18); }


.muted {
    color: var(--muted);
}

.positive {
    color: var(--green) !important;
}

.negative {
    color: var(--red) !important;
}


/* ============================================================
   DASHBOARD GRID
   ============================================================ */

.dashboard-grid {
    display: grid;
    grid-template-columns:
        repeat(
            2,
            minmax(0, 1fr)
        );
    gap: 24px;
}

.dashboard-grid .full {
    grid-column: 1 / -1;
}


/* ============================================================
   TABLES
   ============================================================ */

.table-wrap {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 600px;
}

th,
td {
    padding: 11px 13px;
    text-align: left;
    border-bottom: 1px solid #1f2937;
}

th {
    background: var(--card-hover);
    color: #cbd5e1;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    position: sticky;
    top: 0;
}

td {
    font-size: 14px;
}

tbody tr:hover {
    background: var(--card-hover);
}

.rank-cell {
    color: var(--muted-dark);
    width: 50px;
}

.manager-name {
    font-weight: 650;
    color: var(--text);
}


/* ============================================================
   MINI STAT CARDS
   ============================================================ */

.stats-grid {
    display: grid;
    grid-template-columns:
        repeat(
            auto-fit,
            minmax(
                220px,
                1fr
            )
        );
    gap: 14px;
}

.stat-card {
    background: var(--card-hover);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px;
    min-height: 135px;
}

.stat-label {
    color: var(--muted);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
}

.stat-value {
    color: var(--text);
    font-size: 21px;
    font-weight: 750;
    margin-bottom: 7px;
}

.stat-description {
    color: var(--muted-dark);
    font-size: 13px;
}


/* ============================================================
   TOP PLAYER CARDS
   ============================================================ */

.top-player-grid {
    display: grid;
    grid-template-columns:
        repeat(
            auto-fit,
            minmax(
                180px,
                1fr
            )
        );
    gap: 12px;
}

.top-player-card {
    background: var(--card-hover);
    border: 1px solid var(--border);
    border-radius: 11px;
    padding: 15px;
}

.top-player-rank {
    color: var(--accent);
    font-size: 12px;
    font-weight: 700;
}

.top-player-name {
    color: var(--text);
    font-size: 16px;
    font-weight: 700;
    margin: 5px 0 10px;
}

.top-player-stat {
    color: var(--muted);
    font-size: 12px;
    margin-top: 3px;
}


/* ============================================================
   PHASE 1 COMPONENTS
   ============================================================ */

.rank-up { color: var(--green); font-weight: 800; }
.rank-down { color: var(--red); font-weight: 800; }
.rank-flat { color: var(--muted-dark); font-weight: 700; }

.form-badges {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
}

.form-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    font-size: 10px;
    font-weight: 800;
    border: 1px solid var(--border-light);
}

.form-w { background: rgba(74,222,128,.16); color: var(--green); }
.form-d { background: rgba(250,204,21,.16); color: var(--gold); }
.form-l { background: rgba(248,113,113,.16); color: var(--red); }

.my-team-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.35fr) minmax(280px, .65fr);
    gap: 18px;
}

.my-team-hero {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    align-items: flex-start;
    margin-bottom: 18px;
}

.eyebrow {
    color: var(--accent);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .8px;
}

.my-team-name {
    color: var(--text);
    font-size: 28px;
    font-weight: 800;
    margin: 4px 0 10px;
}

.my-team-rank { text-align: right; }
.my-team-rank span { display: block; font-size: 30px; font-weight: 850; color: var(--text); }
.my-team-rank small { color: var(--muted); }

.compact-stats { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.compact-stats .stat-card { min-height: 105px; padding: 14px; }
.compact-stats .stat-value { font-size: 20px; }

.squad-card {
    background: var(--card-hover);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
}

.squad-card h3 { margin-bottom: 12px; }
.squad-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.squad-heading { color: var(--accent); font-size: 11px; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; }
.squad-row { display: flex; justify-content: space-between; gap: 8px; padding: 7px 0; border-bottom: 1px solid var(--border); font-size: 12px; }
.squad-row b { color: var(--text); }
.bench-row { color: var(--muted); }


.manager-style-card {
    margin-top: 14px;
    background: var(--card-hover);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 15px;
}
.manager-style-header { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; margin-bottom:12px; }
.manager-style-header h3 { margin:3px 0 0; color:var(--text); font-size:16px; }
.manager-style-tags { display:flex; flex-wrap:wrap; justify-content:flex-end; gap:6px; }
.manager-style-tag {
    display:inline-flex; align-items:center;
    border:1px solid rgba(96,165,250,.35);
    background:rgba(96,165,250,.10);
    color:#bfdbfe;
    border-radius:999px;
    padding:5px 8px;
    font-size:10px;
    font-weight:800;
    letter-spacing:.2px;
}
.manager-style-explainer { display:grid; grid-template-columns:minmax(100px,.28fr) 1fr; gap:10px; padding:7px 0; border-top:1px solid var(--border); font-size:11px; }
.manager-style-explainer b { color:var(--text); }
.manager-style-explainer span { color:var(--muted); line-height:1.45; }
.manager-style-metrics { display:flex; flex-wrap:wrap; gap:8px 14px; margin-top:10px; padding-top:10px; border-top:1px solid var(--border); color:var(--muted); font-size:10px; }
.manager-style-metrics b { color:var(--accent); }

.gw-summary-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 10px;
}

.summary-stat {
    background: var(--card-hover);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 13px;
    min-width: 0;
}

.summary-stat span { display: block; color: var(--muted); font-size: 10px; text-transform: uppercase; letter-spacing: .5px; }
.summary-stat strong { display: block; color: var(--text); font-size: 14px; margin: 6px 0 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.summary-stat b { color: var(--accent); font-size: 17px; }

.manager-profile-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
    gap: 14px;
}

.manager-profile-card {
    background: var(--card-hover);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 15px;
}

.manager-profile-top { display: flex; justify-content: space-between; gap: 12px; }
.manager-profile-rank { color: var(--accent); font-size: 11px; font-weight: 800; }
.manager-profile-name { color: var(--text); font-size: 17px; font-weight: 750; margin: 3px 0 8px; }
.manager-profile-points { color: var(--text); font-size: 22px; font-weight: 850; text-align: right; }
.manager-profile-points small { display: block; color: var(--muted); font-size: 10px; font-weight: 500; }

.mini-chart {
    height: 65px;
    display: flex;
    align-items: flex-end;
    gap: 4px;
    margin: 14px 0;
    padding-bottom: 4px;
    border-bottom: 1px solid var(--border-light);
}

.mini-bar {
    flex: 1;
    min-width: 3px;
    max-width: 12px;
    background: var(--accent);
    border-radius: 3px 3px 0 0;
    opacity: .75;
}

.manager-profile-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; color: var(--muted); font-size: 11px; }
.manager-profile-stats b { color: var(--text); }

.key-player-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border);
    font-size: 12px;
}

.key-player-label {
    color: var(--muted);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .4px;
    font-size: 10px;
}

.key-player-name {
    color: var(--text);
    font-weight: 700;
}

.key-player-points {
    color: var(--accent);
    font-weight: 700;
}

.records-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px;
}

.record-card { background: var(--card-hover); border: 1px solid var(--border); border-radius: 11px; padding: 15px; }
.record-label { color: var(--muted); font-size: 10px; text-transform: uppercase; letter-spacing: .5px; }
.record-value { color: var(--text); font-size: 17px; font-weight: 800; margin: 7px 0 4px; }
.record-detail { color: var(--muted-dark); font-size: 12px; }

/* ============================================================
   MY TEAM SELECTOR
   ============================================================ */
.my-team-selector-row { display:flex; justify-content:space-between; align-items:flex-end; gap:18px; margin-bottom:18px; }
.my-team-selector-row h2 { margin-bottom:4px; }
.my-team-selector-row .card-description { margin-bottom:0; }
.my-team-select-wrap { display:flex; flex-direction:column; gap:6px; min-width:230px; }
.my-team-select-wrap span { color:var(--muted); font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:.5px; }
#my-team-select, #club-explorer-select { background:var(--card-hover); color:var(--text); border:1px solid var(--border-light); border-radius:8px; padding:10px 12px; font-size:14px; min-width:230px; cursor:pointer; }
#my-team-select:focus, #club-explorer-select:focus { outline:2px solid var(--accent); outline-offset:2px; }

.squad-gw-heading {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 12px;
}

.squad-gw-heading b {
    color: var(--text);
}

.cap-badge {
    display: inline-block;
    background: var(--accent);
    color: #0f1626;
    font-size: 9px;
    font-weight: 800;
    border-radius: 4px;
    padding: 1px 4px;
    margin-left: 4px;
    vertical-align: middle;
}

.cap-badge.vc {
    background: var(--muted);
    color: #0f1626;
}


/* ============================================================
   TRANSFER LISTS
   ============================================================ */

.recent-transfers-scroll {
    max-height: 330px;
    overflow-y: auto;
    overscroll-behavior: contain;
}

.transfer-history-scroll {
    max-height: 520px;
    overflow-y: auto;
    overscroll-behavior: contain;
}

.recent-transfers-scroll thead th,
.transfer-history-scroll thead th {
    position: sticky;
    top: 0;
    z-index: 2;
    background: var(--card);
}

/* ============================================================
   MOBILE TREND CHARTS (H2H points / rank / gw scores)
   ============================================================ */

.trend-chart-card {
    display: flex;
    flex-direction: column;
    gap: 14px;
}

.chip-row {
    display: flex;
    gap: 7px;
    overflow-x: auto;
    padding-bottom: 4px;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: thin;
}

.chip-row::-webkit-scrollbar {
    height: 5px;
}

.chip-row::-webkit-scrollbar-thumb {
    background: var(--border-light);
    border-radius: 4px;
}

.chart-chip-action {
    flex: none;
    background: var(--bg-secondary);
    color: var(--muted);
    border: 1px solid var(--border-light);
    border-radius: 999px;
    padding: 7px 13px;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    white-space: nowrap;
}

.chart-chip-action:hover {
    color: var(--text);
    border-color: var(--accent);
}

.chart-chip-action.active {
    background: rgba(56, 189, 248, 0.16);
    color: var(--accent);
    border-color: var(--accent);
}

.chart-chip {
    flex: none;
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: var(--card-hover);
    color: var(--muted);
    border: 1px solid var(--border-light);
    border-radius: 999px;
    padding: 7px 13px 7px 10px;
    font-size: 12px;
    font-weight: 650;
    cursor: pointer;
    white-space: nowrap;
    opacity: 0.55;
    transition: opacity 0.15s ease, border-color 0.15s ease;
}

.chart-chip::before {
    content: "";
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: var(--chip-color, var(--accent));
    flex: none;
}

.chart-chip.active {
    opacity: 1;
    color: var(--text);
    border-color: var(--chip-color, var(--accent));
}

.trend-chart-svg-wrap {
    width: 100%;
    touch-action: pan-y;
}

.trend-chart-svg-wrap svg {
    width: 100%;
    height: auto;
    display: block;
    overflow: visible;
}

.trend-chart-line {
    fill: none;
    stroke-width: 3.5;
    stroke-linejoin: round;
    stroke-linecap: round;
    transition: opacity 0.15s ease;
}

.trend-chart-dot {
    transition: opacity 0.15s ease;
}

.trend-chart-hit {
    fill: transparent;
    cursor: pointer;
}

.trend-chart-hit-band {
    fill: var(--accent);
    opacity: 0;
}

.trend-chart-hit-band.selected {
    opacity: 0.08;
}

.trend-chart-gridline {
    stroke: var(--border);
    stroke-width: 1;
}

.trend-chart-axis-label {
    fill: var(--muted-dark);
    font-size: 11px;
}

.trend-chart-end-label {
    font-size: 11px;
    font-weight: 800;
}

.trend-chart-empty {
    color: var(--muted);
    font-size: 13px;
    padding: 20px 0;
    text-align: center;
}

.trend-readout {
    background: var(--card-hover);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px 16px;
}

.trend-readout-heading {
    color: var(--accent);
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 10px;
}

.trend-readout-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 7px 0;
    border-bottom: 1px solid var(--border);
    font-size: 13px;
}

.trend-readout-row:last-child {
    border-bottom: none;
}

.trend-readout-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex: none;
}

.trend-readout-name {
    flex: 1;
    color: var(--text);
    font-weight: 650;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.trend-readout-value {
    color: var(--text);
    font-weight: 800;
    font-size: 14px;
    min-width: 30px;
    text-align: right;
}

.trend-readout-delta {
    min-width: 42px;
    text-align: right;
    font-size: 11px;
    font-weight: 700;
}

.trend-readout-delta.up { color: var(--green); }
.trend-readout-delta.down { color: var(--red); }
.trend-readout-delta.flat { color: var(--muted-dark); }

/* ============================================================
   RESULTS
   ============================================================ */

.results-container {
    position: relative;
}

.results-title,
.totw-summary {

    text-align: center;

    color: var(--muted);

    font-size: 13px;

    margin-bottom: 12px;

}


.totw-title {
    text-align: center;
    font-size: 20px;
    font-weight: 750;
    color: var(--text);
    margin-bottom: 18px;
}

.fixtures-list {
    display: flex;
    flex-direction: column;
    gap: 9px;
}

.fixture {
    display: grid;
    grid-template-columns:
        1fr
        55px
        1fr;
    align-items: center;
    background: var(--card-hover);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 13px 18px;
}

.fixture-team {
    display: flex;
    align-items: center;
    gap: 14px;
    font-size: 14px;
}

.fixture-team:first-child {
    justify-content: flex-end;
    text-align: right;
}

.fixture-team:last-child {
    justify-content: flex-start;
    text-align: left;
}

.fixture-score {
    font-size: 19px;
    font-weight: 800;
    min-width: 25px;
}

.fixture-vs {
    text-align: center;
    color: var(--muted-dark);
    font-size: 11px;
    font-weight: 700;
}

.fixture-team.winner {
    color: var(--text);
    font-weight: 750;
}

.fixture-team.loser {
    color: var(--muted-dark);
}

.fixture-team.draw {
    color: var(--text);
}


.power-formula {
    margin-bottom: 14px;
    padding: 12px 14px;
    border-radius: 12px;
    background: rgba(127, 127, 127, 0.08);
    line-height: 1.5;
    font-size: 0.92rem;
}
.storyline-card p, .season-story p { line-height: 1.65; margin: 10px 0 0; }
.season-summary-list { display: grid; gap: 14px; }
.season-story {
    display: grid;
    grid-template-columns: 72px 1fr;
    gap: 16px;
    padding: 18px 0;
    border-bottom: 1px solid rgba(127,127,127,.18);
}
.season-story:last-child { border-bottom: 0; }
.season-story-gw { font-weight: 800; font-size: 1.05rem; align-self: start; }

.results-navigation,
.totw-navigation {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 18px;
    margin-top: 20px;
}

.results-button,
.totw-button {
    background: var(--card-hover);
    color: var(--text);
    border: 1px solid var(--border-light);
    border-radius: 8px;
    padding: 9px 16px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 600;
    transition:
        background 0.15s ease,
        transform 0.15s ease;
}

.results-button:hover,
.totw-button:hover {
    background: #253149;
    transform: translateY(-1px);
}

.results-button:disabled,
.totw-button:disabled {
    opacity: 0.3;
    cursor: not-allowed;
    transform: none;
}

.results-gw-display,
.totw-gw-display {
    min-width: 75px;
    text-align: center;
    color: var(--text);
    font-weight: 750;
}



.fixture-clickable { cursor:pointer; transition:border-color .15s ease, transform .15s ease, background .15s ease; }
.fixture-clickable:hover,.fixture-clickable:focus-visible { border-color:var(--border-light); background:#1b263b; outline:none; transform:translateY(-1px); }
.fixture-vs small { display:inline-block; margin-top:3px; font-size:9px; color:var(--muted); }
.fixture-detail-overlay { position:fixed; inset:0; z-index:10000; background:rgba(3,7,18,.88); padding:24px; overflow:auto; }
.fixture-detail-overlay[hidden],.fixture-detail-panel[hidden] { display:none; }
.fixture-detail-dialog { position:relative; width:min(1180px,100%); margin:0 auto; background:var(--card); border:1px solid var(--border-light); border-radius:16px; padding:26px; }
.fixture-detail-close { position:absolute; right:14px; top:12px; border:0; background:transparent; color:var(--text); font-size:30px; cursor:pointer; line-height:1; }
.fixture-detail-scoreline { display:grid; grid-template-columns:1fr auto 1fr; align-items:center; gap:18px; padding:4px 42px 20px 0; }
.fixture-detail-scoreline>div:first-child,.fixture-detail-scoreline>div:last-child { display:flex; align-items:baseline; gap:12px; font-size:18px; }
.fixture-detail-scoreline>div:last-child { justify-content:flex-end; }
.fixture-detail-scoreline span { font-size:30px; font-weight:850; color:var(--text); }
.fixture-detail-state { color:var(--muted); font-size:12px; font-weight:750; text-align:center; }
.fixture-xi-grid { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:18px; }
.fixture-xi-heading { display:flex; justify-content:space-between; align-items:baseline; gap:12px; margin-bottom:9px; }
.fixture-xi-heading strong { color:var(--text); font-size:16px; }
.fixture-xi-heading span { color:var(--muted); font-size:12px; }
.fixture-xi-pitch { min-height:390px; padding:24px 12px; gap:20px; }
.fixture-xi-chip { min-width:84px; padding:8px 9px; }
.fixture-player-state { display:inline-block; margin-left:3px; font-size:8px; font-weight:850; letter-spacing:.04em; }
.fixture-player-state-live { color:#dc2626; }.fixture-player-state-to-play { color:#2563eb; }.fixture-player-state-ft { color:#64748b; }
@media (max-width:820px) {
  .fixture-detail-overlay{padding:10px}.fixture-detail-dialog{padding:18px 12px}.fixture-xi-grid{grid-template-columns:1fr;gap:26px}
  .fixture-detail-scoreline{padding-right:34px;gap:8px}.fixture-detail-scoreline strong{font-size:13px}.fixture-detail-scoreline span{font-size:24px}.fixture-xi-pitch{min-height:360px}
}

/* ============================================================
   TEAM OF THE WEEK
   ============================================================ */

.pitch {
    background:
        linear-gradient(
            #166534,
            #15803d
        );
    border-radius: 13px;
    padding: 30px 20px;
    display: flex;
    flex-direction: column;
    gap: 25px;
    min-height: 440px;
    justify-content: center;
    position: relative;
    overflow: hidden;
}

.pitch::before {
    content: "";
    position: absolute;
    left: 8%;
    right: 8%;
    top: 50%;
    border-top: 2px solid rgba(
        255,
        255,
        255,
        0.2
    );
}

.pitch::after {
    content: "";
    position: absolute;
    width: 130px;
    height: 65px;
    border: 2px solid rgba(
        255,
        255,
        255,
        0.2
    );
    border-bottom: none;
    left: 50%;
    transform: translateX(-50%);
    bottom: 0;
}

.row {
    display: flex;
    justify-content: center;
    gap: 15px;
    flex-wrap: wrap;
    position: relative;
    z-index: 2;
}

.chip {
    background: rgba(
        255,
        255,
        255,
        0.96
    );
    color: #111827;
    border-radius: 10px;
    padding: 9px 13px;
    text-align: center;
    min-width: 105px;
    box-shadow:
        0 4px 12px rgba(
            0,
            0,
            0,
            0.25
        );
    transition:
        transform 0.15s ease;
}

.chip:hover {
    transform: translateY(-3px);
}

.chip-name {
    font-weight: 750;
}

.chip-sub {
    font-size: 11px;
    color: #475569;
    margin-top: 3px;
}


/* ============================================================
   SEARCH
   ============================================================ */

.player-search-box {
    width: 100%;
    background: var(--bg-secondary);
    color: var(--text);
    border: 1px solid var(--border-light);
    border-radius: 9px;
    padding: 13px;
    font-size: 15px;
    outline: none;
    margin-bottom: 18px;
}

.player-search-box:focus {
    border-color: var(--accent);
    box-shadow:
        0 0 0 2px rgba(
            56,
            189,
            248,
            0.12
        );
}

.player-search-results {
    display: none;
}

.player-history-card {
    background: var(--card-hover);
    border: 1px solid var(--border);
    border-radius: 11px;
    padding: 16px;
    margin-bottom: 14px;
}

.player-history-title {
    font-size: 19px;
    font-weight: 750;
    color: var(--text);
    margin-bottom: 7px;
}

.player-meta {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 14px;
}

.player-stat-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 14px;
}

.player-stat-chip {
    background: #0f1626;
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 12px;
    color: var(--muted);
}

.player-stat-chip b {
    color: var(--text);
    margin-right: 4px;
}

.player-history-chart-heading {
    color: var(--muted);
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .5px;
    margin-bottom: 8px;
}

.player-gw-chart-wrap {
    margin-bottom: 16px;
}

.trend-chart-bar {
    fill: var(--accent);
    opacity: 0.85;
}


/* ============================================================
   PLOTLY / CHARTS
   ============================================================ */

.js-plotly-plot,
.plotly,
.plot-container,
.svg-container {
    width: 100% !important;
    max-width: 100% !important;
}

.js-plotly-plot {
    min-width: 0;
}

/* Prevent Plotly's default inline width from creating a horizontal
   page scroll on narrow screens. */
.card .js-plotly-plot {
    overflow: hidden;
}

/* ============================================================
   PLAYER DIRECTORY / FILTERS
   ============================================================ */

.player-directory-heading {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
}

.player-directory-count {
    color: var(--muted);
    font-size: 12px;
    font-weight: 700;
    white-space: nowrap;
    padding-top: 4px;
}

.player-filter-grid {
    display: grid;
    grid-template-columns: 2fr repeat(4, minmax(130px, 1fr));
    gap: 9px;
    margin-bottom: 16px;
}

.player-filter {
    width: 100%;
    box-sizing: border-box;
    background: var(--bg-secondary);
    color: var(--text);
    border: 1px solid var(--border-light);
    border-radius: 9px;
    padding: 12px;
    font-size: 13px;
    outline: none;
}

.player-filter:focus {
    border-color: var(--accent);
}

.player-directory-results {
    display: flex;
    flex-direction: column;
    gap: 9px;
}

.player-directory-card {
    background: var(--card-hover);
    border: 1px solid var(--border);
    border-radius: 11px;
    padding: 13px;
    display: grid;
    grid-template-columns: minmax(160px, 1fr) auto auto;
    gap: 12px;
    align-items: center;
}

.player-directory-name {
    color: var(--text);
    font-size: 15px;
    font-weight: 800;
}

.player-directory-meta {
    color: var(--muted);
    font-size: 11px;
    margin-top: 4px;
}

.player-directory-meta .free-agent {
    color: var(--green);
    font-weight: 800;
}

.player-directory-stats {
    display: flex;
    align-items: center;
    gap: 10px;
}

.player-directory-stats div {
    min-width: 38px;
    text-align: center;
}

.player-directory-stats b,
.player-directory-stats span {
    display: block;
}

.player-directory-stats b {
    color: var(--text);
    font-size: 14px;
}

.player-directory-stats span {
    color: var(--muted-dark);
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: .4px;
}

.fixture-run-strip{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}.fixture-chip{display:inline-flex;align-items:center;gap:5px;padding:5px 8px;border-radius:999px;font-size:11px;font-weight:700;border:1px solid rgba(255,255,255,.12)}.fixture-chip .fixture-gw{opacity:.7;font-size:10px}.fixture-diff-1{background:rgba(34,197,94,.22);border-color:rgba(34,197,94,.55)}.fixture-diff-2{background:rgba(132,204,22,.18);border-color:rgba(132,204,22,.45)}.fixture-diff-3{background:rgba(234,179,8,.16);border-color:rgba(234,179,8,.4)}.fixture-diff-4{background:rgba(249,115,22,.18);border-color:rgba(249,115,22,.5)}.fixture-diff-5{background:rgba(239,68,68,.18);border-color:rgba(239,68,68,.5)}.fixture-chip.fixture-blank{background:rgba(148,163,184,.12);border-color:rgba(148,163,184,.3);opacity:.8}.fixture-run-heading{font-size:11px;text-transform:uppercase;letter-spacing:.06em;opacity:.65;margin-top:10px}

.player-details-button {
    background: transparent;
    color: var(--accent);
    border: 1px solid var(--border-light);
    border-radius: 7px;
    padding: 7px 10px;
    font-size: 11px;
    font-weight: 800;
    cursor: pointer;
}

.player-details-button:hover {
    background: rgba(56, 189, 248, 0.08);
}

.player-details {
    grid-column: 1 / -1;
    padding-top: 12px;
    border-top: 1px solid var(--border);
}

.player-details .player-gw-table {
    overflow-x: auto;
}

.player-details .player-gw-table table {
    min-width: 420px;
}

/* ============================================================
   FREE AGENTS / H2H
   ============================================================ */

.free-agent-list,
.h2h-record-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.free-agent-row,
.h2h-record-row {
    background: var(--card-hover);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 11px 12px;
}

.free-agent-row {
    display: grid;
    grid-template-columns: minmax(140px, 1fr) minmax(190px, 1.3fr) auto;
    gap: 12px;
    align-items: center;
}

.free-agent-name,
.h2h-opponent {
    color: var(--text);
    font-size: 13px;
    font-weight: 800;
}

.free-agent-meta {
    color: var(--muted);
    font-size: 10px;
    margin-top: 3px;
}

.free-agent-comparison {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
}

.free-agent-label {
    width: 100%;
    color: var(--muted);
    font-size: 10px;
}

.upgrade-positive,
.upgrade-neutral {
    border-radius: 999px;
    padding: 4px 7px;
    font-size: 10px;
    font-weight: 800;
}

.upgrade-positive {
    color: var(--green);
    background: rgba(34, 197, 94, 0.09);
}

.upgrade-neutral {
    color: var(--muted);
    background: rgba(148, 163, 184, 0.08);
}

.free-agent-stats {
    display: grid;
    grid-template-columns: auto auto;
    gap: 0 7px;
    min-width: 54px;
    text-align: right;
}

.free-agent-stats b {
    color: var(--text);
    font-size: 13px;
}

.free-agent-stats span {
    color: var(--muted-dark);
    font-size: 9px;
}

.h2h-record-row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto auto auto;
    gap: 10px;
    align-items: center;
}

.h2h-record-summary {
    font-size: 11px;
    font-weight: 800;
    white-space: nowrap;
}

.h2h-positive { color: var(--green); }
.h2h-negative { color: var(--red); }
.h2h-neutral { color: var(--muted); }

.h2h-record-score {
    color: var(--text);
    font-size: 12px;
    font-weight: 800;
    min-width: 55px;
    text-align: right;
}

.h2h-record-played {
    color: var(--muted-dark);
    font-size: 10px;
    min-width: 55px;
    text-align: right;
}

/* ============================================================
   TRADES
   ============================================================ */

.trades-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.trade-card {
    background: var(--card-hover);
    border: 1px solid var(--border);
    border-radius: 11px;
    padding: 14px;
}

.trade-card-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 12px;
}

.trade-managers {
    color: var(--text);
    font-size: 14px;
    font-weight: 800;
}

.trade-managers span {
    color: var(--accent);
    margin: 0 5px;
}

.trade-meta {
    color: var(--muted-dark);
    font-size: 10px;
    margin-top: 4px;
}

.trade-status {
    border-radius: 999px;
    padding: 5px 8px;
    font-size: 9px;
    font-weight: 900;
    text-transform: uppercase;
}

.trade-status-complete {
    color: var(--green);
    background: rgba(34, 197, 94, 0.09);
}

.trade-status-other {
    color: var(--muted);
    background: rgba(148, 163, 184, 0.08);
}

.trade-exchange {
    display: grid;
    grid-template-columns: 1fr 35px 1fr;
    gap: 10px;
    align-items: center;
}

.trade-side {
    background: #0f1626;
    border: 1px solid var(--border);
    border-radius: 9px;
    padding: 10px;
}

.trade-side-label {
    color: var(--muted-dark);
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: .4px;
    font-weight: 800;
    margin-bottom: 5px;
}

.trade-players {
    color: var(--text);
    font-size: 12px;
    font-weight: 750;
}


.gw-story {
    margin-bottom: 18px;
    padding: 18px;
    border: 1px solid var(--border);
    border-radius: 16px;
    background: rgba(255,255,255,0.025);
}

.gw-story .eyebrow { margin-bottom: 8px; }
.gw-story-copy { font-size: 15px; line-height: 1.7; }
.gw-story-copy p { margin: 0 0 10px 0; }
.gw-story-copy p:last-child { margin-bottom: 0; }

.trade-grade {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
}
.trade-grade-title {
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .08em;
    margin-bottom: 10px;
}
.trade-grade-title span {
    font-weight: 500;
    opacity: .65;
    text-transform: none;
    letter-spacing: 0;
}
.trade-grade-grid {
    display: grid;
    grid-template-columns: 1fr minmax(150px, .8fr) 1fr;
    gap: 12px;
    align-items: stretch;
}
.trade-grade-grid > div {
    padding: 12px;
    border-radius: 12px;
    background: rgba(255,255,255,0.03);
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.trade-grade-grid b { font-size: 27px; line-height: 1; }
.trade-grade-grid span { font-size: 12px; opacity: .72; }
.trade-grade-verdict { text-align: center; justify-content: center; }
@media (max-width: 700px) { .trade-grade-grid { grid-template-columns: 1fr; } }

.trade-arrow {
    color: var(--accent);
    text-align: center;
    font-size: 18px;
}


/* ============================================================
   LIGHT / DARK THEME
   ============================================================ */
.theme-control { display:flex; align-items:center; flex:0 0 auto; }
.theme-toggle {
    display:inline-flex; align-items:center; gap:8px;
    border:1px solid var(--border-light); background:var(--bg-secondary); color:var(--text);
    border-radius:999px; padding:9px 12px; font-weight:800; font-size:12px; cursor:pointer;
    box-shadow:0 4px 14px rgba(0,0,0,.16); transition:background .2s ease,border-color .2s ease,color .2s ease,transform .2s ease;
}
.theme-toggle:hover { border-color:var(--accent); transform:translateY(-1px); }
.theme-toggle:focus-visible { outline:2px solid var(--accent); outline-offset:2px; }
.theme-toggle-icon { font-size:15px; line-height:1; }

body[data-theme="light"] {
    --bg:#f3f6fb;
    --bg-secondary:#ffffff;
    --card:#ffffff;
    --card-hover:#f1f5f9;
    --border:#d9e2ec;
    --border-light:#c5d1df;
    --text:#172033;
    --muted:#5f6f82;
    --muted-dark:#8290a3;
    --accent:#0284c7;
    --accent-dark:#0369a1;
    --green:#15803d;
    --red:#dc2626;
    --gold:#b77900;
    color-scheme:light;
}
body[data-theme="dark"] { color-scheme:dark; }

body[data-theme="light"] .header {
    background:linear-gradient(135deg,rgba(255,255,255,.97),rgba(241,245,249,.97));
    box-shadow:0 8px 24px rgba(15,23,42,.06);
}
body[data-theme="light"] .logo,
body[data-theme="light"] h1,
body[data-theme="light"] h2,
body[data-theme="light"] h3,
body[data-theme="light"] h4,
body[data-theme="light"] strong,
body[data-theme="light"] b { color:var(--text); }
body[data-theme="light"] .logo span { color:var(--accent); }
body[data-theme="light"] .global-search-input,
body[data-theme="light"] .global-search-results,
body[data-theme="light"] .global-search-tab,
body[data-theme="light"] .motm-card,
body[data-theme="light"] .archetype-card,
body[data-theme="light"] .record-chase-summary span,
body[data-theme="light"] .record-chase-row,
body[data-theme="light"] .milestone-row,
body[data-theme="light"] .season-slider-summary div,
body[data-theme="light"] .record-card,
body[data-theme="light"] #my-team-select,
body[data-theme="light"] #club-explorer-select,
body[data-theme="light"] .player-filter,
body[data-theme="light"] select,
body[data-theme="light"] input,
body[data-theme="light"] textarea {
    background:#fff;
    color:var(--text);
    border-color:var(--border-light);
}
body[data-theme="light"] .global-search-result:hover,
body[data-theme="light"] .global-search-tab.active,
body[data-theme="light"] .nav-button:hover,
body[data-theme="light"] .fixture-clickable:hover,
body[data-theme="light"] .fixture-clickable:focus-visible { background:#edf4fb; }
body[data-theme="light"] .nav-button.active { color:var(--text); }
body[data-theme="light"] .global-search-result strong,
body[data-theme="light"] .global-search-tab.active,
body[data-theme="light"] .share-card-button:hover { color:var(--text); }
body[data-theme="light"] .global-search-tab.active { color:var(--accent-dark); }
body[data-theme="light"] .share-card {
    background:linear-gradient(145deg,#ffffff,#f1f5f9);
    box-shadow:0 8px 24px rgba(15,23,42,.05);
}
body[data-theme="light"] .share-card-button { background:#fff; color:var(--text); }
body[data-theme="light"] .fixture-detail-overlay { background:rgba(15,23,42,.55); }
body[data-theme="light"] .fixture-detail-close { color:var(--text); }
body[data-theme="light"] .analytics-average-marker { background:#334155; }
body[data-theme="light"] #page-analytics.show-league-average .analytics-average-series { stroke:#334155; }
body[data-theme="light"] .trade-grade-grid > div { background:rgba(15,23,42,.035); }
body[data-theme="light"] .theme-toggle { box-shadow:0 3px 12px rgba(15,23,42,.08); }

/* Strong light-mode component pass: older dashboard modules used semi-opaque navy surfaces. */
body[data-theme="light"] .river-panel,
body[data-theme="light"] .passport-detail,
body[data-theme="light"] .war-room-card,
body[data-theme="light"] .war-room-player-card,
body[data-theme="light"] .analytics-pie-hole {
    background:#ffffff !important;
    color:var(--text) !important;
    border-color:var(--border) !important;
    box-shadow:0 5px 18px rgba(15,23,42,.06);
}
body[data-theme="light"] .war-room-player-card small,
body[data-theme="light"] .war-room-player-card .wr-proj,
body[data-theme="light"] .analytics-pie-hole strong,
body[data-theme="light"] .analytics-pie-legend-row strong,
body[data-theme="light"] .pedigree-identity h3,
body[data-theme="light"] .pedigree-stars span,
body[data-theme="light"] .pedigree-unit>b {
    color:var(--text) !important;
}
body[data-theme="light"] .war-room-player-card small { color:var(--muted) !important; }
body[data-theme="light"] .card,
body[data-theme="light"] .record-card,
body[data-theme="light"] .manager-profile-card,
body[data-theme="light"] .top-player-card,
body[data-theme="light"] .player-directory-card,
body[data-theme="light"] .position-need-card,
body[data-theme="light"] .trade-sim-player,
body[data-theme="light"] .trade-sim-breakdown>div,
body[data-theme="light"] .passport-owner-chip,
body[data-theme="light"] .passport-metrics div,
body[data-theme="light"] .passport-stint,
body[data-theme="light"] .passport-transactions li,
body[data-theme="light"] .passport-mover-list li,
body[data-theme="light"] .war-room-side,
body[data-theme="light"] .war-room-prob div,
body[data-theme="light"] .war-room-pos,
body[data-theme="light"] .war-room-bench,
body[data-theme="light"] .war-room-player-detail,
body[data-theme="light"] .war-room-player-detail-grid div,
body[data-theme="light"] .war-room-player-news,
body[data-theme="light"] .war-room-player-fixture,
body[data-theme="light"] .war-room-flag,
body[data-theme="light"] .war-room-upgrade {
    background:#ffffff !important;
    color:var(--text) !important;
    border-color:var(--border) !important;
}
body[data-theme="light"] .nav-button,
body[data-theme="light"] .transfer-subtab,
body[data-theme="light"] .analytics-subtab,
body[data-theme="light"] .matrix-group-chip,
body[data-theme="light"] .totw-button,
body[data-theme="light"] .chart-chip {
    background:#f8fafc;
    color:var(--muted);
    border-color:var(--border);
}
body[data-theme="light"] .nav-button:hover,
body[data-theme="light"] .transfer-subtab:hover,
body[data-theme="light"] .analytics-subtab:hover,
body[data-theme="light"] .matrix-group-chip:hover,
body[data-theme="light"] .totw-button:hover,
body[data-theme="light"] .chart-chip:hover { background:#eef4fa; color:var(--text); }
body[data-theme="light"] .nav-button.active,
body[data-theme="light"] .transfer-subtab.active,
body[data-theme="light"] .analytics-subtab.active,
body[data-theme="light"] .matrix-group-chip.active,
body[data-theme="light"] .chart-chip.active {
    background:#e2f2fb !important;
    color:#075985 !important;
    border-color:#38bdf8 !important;
}
body[data-theme="light"] table { color:var(--text); }
body[data-theme="light"] th { color:#475569; background:#f8fafc; }
body[data-theme="light"] td { color:#243244; }
body[data-theme="light"] tr:hover td { background:#f8fbff; }
body[data-theme="light"] .notice,
body[data-theme="light"] .fixture-detail-panel,
body[data-theme="light"] .player-directory-controls,
body[data-theme="light"] .analytics-chart-card {
    color:var(--text);
}
body[data-theme="light"] input::placeholder,
body[data-theme="light"] textarea::placeholder { color:#8492a6; opacity:1; }

/* Common dark utility panels that pre-date CSS variables. */
body[data-theme="light"] [style*="background:var(--bg-secondary)"],
body[data-theme="light"] [style*="background: var(--bg-secondary)"],
body[data-theme="light"] [style*="background:var(--card)"],
body[data-theme="light"] [style*="background: var(--card)"],
body[data-theme="light"] [style*="background:var(--card-hover)"],
body[data-theme="light"] [style*="background: var(--card-hover)"],
body[data-theme="light"] [style*="background:var(--bg-secondary)"],
body[data-theme="light"] [style*="background: var(--bg-secondary)"] { background:#fff !important; color:var(--text) !important; }
body[data-theme="light"] [style*="color:var(--text)"],
body[data-theme="light"] [style*="color: var(--text)"],
body[data-theme="light"] [style*="color:var(--text)"],
body[data-theme="light"] [style*="color: var(--text)"] { color:var(--text) !important; }

@media(max-width:900px){
    .theme-control { order:2; }
    .header-meta { order:2; margin-left:auto; }
}
@media(max-width:600px){
    .theme-control { order:2; }
    .header-meta { order:2; margin-left:0; }
    .theme-toggle { padding:7px 10px; font-size:11px; }
}

/* ============================================================
   MOBILE
   ============================================================ */

@media (
    max-width: 900px
) {
    .global-search-wrap { order:3; width:100%; max-width:none; margin-left:0; }
    .header-top { flex-wrap:wrap; }
    .my-team-selector-row { flex-direction:column; align-items:stretch; }
    .my-team-select-wrap, #my-team-select, #club-explorer-select { width:100%; min-width:0; box-sizing:border-box; }


    .dashboard-grid {
        grid-template-columns: 1fr;
    }

    .dashboard-grid .full {
        grid-column: auto;
    }

    .header {
        padding:
            18px
            18px
            0;
    }

    .header-top {
        align-items: flex-start;
        flex-direction: column;
        padding-bottom: 15px;
    }

    .header-meta {
        text-align: left;
    }

    .main {
        padding: 18px;
    }

    .page-heading h1 {
        font-size: 25px;
    }

}

@media (
    max-width: 600px
) {

    .my-team-grid { grid-template-columns: 1fr; }
    .compact-stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .my-team-name { font-size: 22px; }
    .my-team-rank span { font-size: 24px; }
    .squad-columns { grid-template-columns: 1fr; }
    .gw-summary-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .summary-stat:last-child { grid-column: 1 / -1; }
    .manager-profile-grid { grid-template-columns: 1fr; }


    body {
        overflow-x: hidden;
    }

    .header {
        padding: 12px 10px 0;
    }

    .header-top {
        padding: 0 4px 10px;
        gap: 7px;
    }

    .logo {
        font-size: 19px;
    }

    .header-meta {
        font-size: 11px;
    }

    .nav {
        gap: 2px;
        margin: 0 -10px;
        padding: 0 10px;
        scrollbar-width: none;
    }

    .nav::-webkit-scrollbar {
        display: none;
    }

    .nav-button {
        padding: 11px 14px;
        font-size: 12px;
    }

    .main {
        padding: 12px 10px 24px;
    }

    .page-heading {
        margin-bottom: 15px;
    }

    .page-heading h1 {
        font-size: 22px;
    }

    .page-heading p {
        font-size: 12px;
        line-height: 1.45;
    }

    .card {
        padding: 12px;
        margin-bottom: 12px;
        border-radius: 11px;
    }

    .card h2 {
        font-size: 16px;
        margin-bottom: 12px;
    }

    .trend-readout-row {
        font-size: 12px;
    }

    .trend-readout-value {
        font-size: 13px;
    }

    /* Plotly needs explicit mobile dimensions because charts on hidden
       pages can otherwise calculate their width as zero. */
    .card .js-plotly-plot {
        width: 100% !important;
        height: 310px !important;
    }

    .card .js-plotly-plot .plotly {
        width: 100% !important;
        height: 100% !important;
    }

    .fixture {
        grid-template-columns:
            minmax(0, 1fr)
            30px
            minmax(0, 1fr);
        padding: 9px 7px;
    }

    .fixture-team {
        gap: 6px;
        font-size: 11px;
        min-width: 0;
    }

    .fixture-manager {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .fixture-score {
        font-size: 16px;
        min-width: 20px;
    }

    .fixture-vs {
        font-size: 9px;
    }

    .results-navigation,
    .totw-navigation {
        gap: 8px;
        margin-top: 12px;
    }

    .results-button,
    .totw-button {
        padding: 8px 10px;
        font-size: 11px;
    }

    .results-gw-display,
    .totw-gw-display {
        min-width: 50px;
        font-size: 12px;
    }

    .chip {
        min-width: 70px;
        max-width: 90px;
        padding: 7px 5px;
        border-radius: 8px;
    }

    .chip-name {
        font-size: 11px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .chip-sub {
        font-size: 9px;
    }

    .pitch {
        min-height: 380px;
        padding: 20px 4px;
        gap: 19px;
    }

    .row {
        gap: 5px;
    }

    .stats-grid {
        grid-template-columns: 1fr 1fr;
        gap: 8px;
    }

    .stat-card {
        min-height: 105px;
        padding: 12px;
    }

    .stat-label {
        font-size: 9px;
        margin-bottom: 8px;
    }

    .stat-value {
        font-size: 15px;
        overflow-wrap: anywhere;
    }

    .stat-description {
        font-size: 10px;
    }

    .top-player-grid {
        grid-template-columns: 1fr 1fr;
        gap: 7px;
    }

    .top-player-card {
        padding: 11px;
    }

    .top-player-name {
        font-size: 13px;
        overflow-wrap: anywhere;
    }

    .top-player-stat {
        font-size: 10px;
    }

    .table-wrap {
        margin: 0 -4px;
        padding: 0 4px;
        -webkit-overflow-scrolling: touch;
    }

    table {
        min-width: 540px;
    }

    th,
    td {
        padding: 8px 9px;
        font-size: 11px;
    }

    th {
        font-size: 9px;
    }

    .player-search-box {
        padding: 11px;
        font-size: 14px;
    }

    .player-filter-grid {
        grid-template-columns: 1fr 1fr;
    }

    .player-filter-grid .player-search-box {
        grid-column: 1 / -1;
    }

    .player-directory-heading {
        gap: 8px;
    }

    .player-directory-card {
        grid-template-columns: 1fr auto;
    }

    .player-directory-stats {
        grid-column: 1 / -1;
        justify-content: space-between;
    }

    .player-details-button {
        justify-self: end;
    }

    .free-agent-row {
        grid-template-columns: 1fr auto;
    }

    .free-agent-comparison {
        grid-column: 1 / -1;
    }

    .h2h-record-row {
        grid-template-columns: minmax(0, 1fr) auto;
    }

    .trade-card-top {
        flex-direction: column;
    }

    .trade-exchange {
        grid-template-columns: 1fr;
    }

    .trade-arrow {
        transform: rotate(90deg);
    }

}


/* v46 — Matrix Lab: responsive quadrants, existing owner palette, shared filter. */
.matrix-intro{margin-bottom:14px;display:flex;align-items:center;justify-content:space-between;gap:20px}
.matrix-intro h2{margin:0 0 5px;font-size:18px}
.matrix-intro .card-description{max-width:820px;margin:0}
.matrix-group-controls{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 17px}
.matrix-group-chip{border:1px solid var(--border);background:#131f32;color:#b7c7de;border-radius:99px;padding:9px 12px;cursor:pointer;font-size:11px;font-weight:850;transition:border-color .12s,background .12s}
.matrix-group-chip.active{color:var(--text);background:#20344c;border-color:var(--accent);box-shadow:inset 0 0 0 1px var(--accent)}
.matrix-group-chip span{color:var(--accent);margin-left:5px;font-weight:800}
.matrix-card{min-width:0;display:flex;flex-direction:column;gap:9px}
.matrix-card[hidden],.matrix-empty[hidden]{display:none!important}
.matrix-card-top{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
.matrix-card-top h2{font-size:15px;line-height:1.35;margin:5px 0 0}
.matrix-category{color:var(--accent);font-size:9px;letter-spacing:.12em;font-weight:900;text-transform:uppercase}
.matrix-visible-count{white-space:nowrap;color:var(--muted);font-size:10px;font-weight:800}
.matrix-plot-wrap{width:100%;margin-top:auto}
.matrix-svg{width:100%;height:auto;display:block;overflow:visible}
.matrix-gridline{stroke:#334155;stroke-opacity:.6;stroke-width:.75}
.matrix-median{stroke:#e2e8f0;stroke-dasharray:5 5;stroke-width:1;stroke-opacity:.62}
.matrix-tick{fill:#94a3b8;font-size:11px}
.matrix-axis-label{fill:#b8c5d6;font-size:12px;font-weight:800}
.matrix-quadrant-label{fill:#94a3b8;font-size:10px;font-weight:850;opacity:.8;paint-order:stroke;stroke:#111827;stroke-width:3px;stroke-linejoin:round;pointer-events:none}

/* v47 — readable, chart-specific quadrant key; positions remain correct on reverse-X axes. */
.matrix-quadrant-label{font-size:10.5px;fill:#b0c5da;opacity:.92}
.matrix-quadrant-key{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:5px 10px;margin-top:0;padding:6px 9px;border:1px solid #293d52;background:#111f31;border-radius:9px}
.matrix-quad-key{min-width:0;color:#cad8e9;font-size:10.5px;line-height:1.3;font-weight:650;display:flex;align-items:flex-start;gap:6px}
.matrix-quad-key b{flex:0 0 auto;color:#79c5e6;font-size:13px;line-height:1.0}
@media(max-width:460px){.matrix-quadrant-key{gap:7px 8px;padding:7px}.matrix-quad-key{font-size:10px}}

.matrix-manager-point{cursor:crosshair;outline:none}
.matrix-dot{transition:opacity .12s,r .12s;opacity:.88}
.matrix-dot-label{display:none;fill:#f8fafc;font-size:12px;font-weight:850;paint-order:stroke;stroke:#0b1220;stroke-width:4px;stroke-linejoin:round;pointer-events:none}
.matrix-manager-point:hover .matrix-dot,.matrix-manager-point:focus .matrix-dot{opacity:1;r:10;stroke:#fff;stroke-width:2.5px}
.matrix-manager-point:hover .matrix-dot-label,.matrix-manager-point:focus .matrix-dot-label,.matrix-card.matrix-focus-labels .matrix-dot-label{display:block}
.matrix-meta{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;font-size:10px;color:var(--muted)}
.matrix-empty{background:#152234;border:1px dashed var(--border);border-radius:10px;padding:12px;color:var(--muted);font-size:12px}
@media(max-width:800px){.matrix-intro{align-items:flex-start;flex-direction:column}.matrix-grid{grid-template-columns:1fr}}
@media(max-width:460px){.matrix-group-controls{gap:6px}.matrix-group-chip{padding:7px 9px}.matrix-meta{font-size:9px}}

.analytics-chart-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:18px; }

.transfer-subtabs { display:flex; gap:8px; margin:0 0 20px; overflow-x:auto; padding-bottom:3px; }
.transfer-subtab { border:1px solid var(--border); background:var(--bg-secondary); color:var(--muted); border-radius:10px; padding:10px 14px; cursor:pointer; font-weight:800; white-space:nowrap; }
.transfer-subtab.active { color:var(--text); border-color:var(--accent); background:var(--card-hover); box-shadow:inset 0 -2px 0 var(--accent); }
.transfer-subpanel { display:none; } .transfer-subpanel.active { display:block; }


/* FPL injury watch: responsive cards in Players and My Team */
.injury-list-grid {display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,310px),1fr));gap:12px;margin-top:12px}
.injury-medical-card{padding:15px;border:1px solid var(--border,#53606b);border-radius:13px;background:var(--card-bg,rgba(120,130,145,.065));min-width:0}
.injury-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap}
.injury-head strong{display:block;font-size:1.05rem}.injury-head small{display:block;opacity:.7;margin-top:4px}.injury-medical-card p{margin:12px 0;font-size:.92rem;line-height:1.5}
.injury-actions{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:12px;font-size:.83rem}
.planner-availability-warning{color:#f1ae59;font-weight:750;font-size:.73rem}

/* My Team: Five-GW Squad Planner */
.planner-stat-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:14px 0 22px}
.planner-stat{background:var(--surface-2,#152033);border:1px solid var(--border-light);border-radius:10px;padding:14px;display:flex;flex-direction:column;gap:5px}
.planner-stat small{color:var(--muted);font-size:11px;font-weight:700;text-transform:uppercase}
.planner-stat strong{font-size:27px;color:var(--text,#fff)}
.planner-stat span{font-size:12px;color:var(--muted)}
.planner-chart{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:9px;margin:12px 0 26px}
.planner-chart-week{display:flex;align-items:center;flex-direction:column;min-width:0;background:var(--surface-2,#152033);color:inherit;border:1px solid var(--border-light);border-radius:10px;padding:10px 5px;cursor:pointer;gap:5px}
.planner-chart-week.active{border-color:var(--accent);background:rgba(52,211,153,.08)}
.planner-chart-week:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.planner-chart-val{font-size:17px;font-weight:800}.planner-chart-week small{font-size:10px;color:var(--muted);max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.planner-bar-area{height:130px;display:flex;align-items:end;width:65%;max-width:66px}
.planner-chart-bar{background:var(--accent,#32bd9b);width:100%;border-radius:5px 5px 1px 1px;min-height:5px}
.planner-week-heading{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}.planner-week-flags{display:flex;gap:5px;flex-wrap:wrap}
.planner-pos-pills{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 17px}.planner-pos-pills span{font-size:11px;border:1px solid var(--border-light);padding:5px 9px;border-radius:20px}
.planner-squad-columns{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:16px}.planner-squad-columns>div{min-width:0}
.planner-player{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.1fr) 40px;align-items:center;gap:8px;border-bottom:1px solid var(--border-light);padding:8px 2px;font-size:12px}
.planner-player>div:first-child{min-width:0}.planner-player small{display:block;color:var(--muted);font-size:10px}.planner-player strong{text-align:right}
.planner-player-fixtures{display:flex;justify-content:flex-end;gap:3px;flex-wrap:wrap}
.planner-fx{border-radius:5px;padding:3px 5px;font-weight:700;font-size:10px;background:#856324;color:var(--text)}
.planner-fx.diff-1,.planner-fx.diff-2{background:#216f50}.planner-fx.diff-4,.planner-fx.diff-5{background:#93382f}.planner-fx.planner-blank{background:#475569}
@media(max-width:760px){.planner-stat-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.planner-stat{padding:9px}.planner-stat strong{font-size:21px}.planner-squad-columns{grid-template-columns:1fr}.planner-chart{gap:5px}.planner-chart-week{padding:9px 2px}.planner-chart-week small{font-size:9px}.planner-player{grid-template-columns:minmax(0,1fr) minmax(0,1fr) 30px}}
@media(max-width:410px){.planner-stat-grid{gap:6px}.planner-stat small{font-size:9px}.planner-stat strong{font-size:18px}}
.myteam-position-need-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:14px}
.position-need-card{border:1px solid var(--border);border-radius:12px;padding:13px;background:var(--bg-secondary);position:relative;overflow:hidden}
.position-need-card:before{content:"";position:absolute;inset:0;opacity:.12;pointer-events:none;background:var(--need-colour,#64748b)}
.position-need-top{display:flex;justify-content:space-between;gap:8px;align-items:center;position:relative}
.position-need-pos{font-size:12px;font-weight:900;letter-spacing:.08em}.position-need-score{font-size:22px;font-weight:900}
.position-need-label{font-size:11px;font-weight:850;margin-top:5px;position:relative}.position-need-meta{font-size:10px;color:var(--muted);margin-top:5px;position:relative}
.position-need-track{height:7px;border-radius:999px;background:var(--bg-secondary);border:1px solid var(--border);overflow:hidden;margin-top:10px;position:relative}
.position-need-fill{height:100%;border-radius:999px;background:var(--need-colour,#64748b)}
@media(max-width:720px){.myteam-position-need-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
.trade-sim-player.position-match{animation:positionPulse 1s ease-in-out 2}
.trade-sim-player.position-match .trade-sim-position{background:var(--accent);color:#07111f}
@keyframes positionPulse{0%,100%{transform:translateX(0)}50%{transform:translateX(3px)}}
.trade-sim-head { display:flex; justify-content:space-between; gap:16px; align-items:flex-start; } .trade-sim-score{text-align:right;min-width:110px}.trade-sim-score span{display:block;color:var(--muted);font-size:11px;text-transform:uppercase}.trade-sim-score b{font-size:28px}
.trade-sim-manager-row{display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:end;margin:18px 0}.trade-sim-manager-row label{font-size:12px;color:var(--muted);font-weight:800}.trade-sim-manager-row select{width:100%;margin-top:6px;background:var(--bg-secondary);border:1px solid var(--border);color:var(--text);border-radius:9px;padding:10px}.trade-sim-versus{font-size:22px;padding-bottom:9px}.trade-sim-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.trade-sim-roster{display:grid;gap:7px}.trade-sim-player{display:grid;grid-template-columns:auto 1fr auto;gap:9px;align-items:center;padding:9px 10px;border:1px solid var(--border);border-radius:9px;background:var(--bg-secondary);cursor:pointer}.trade-sim-player small{display:block;color:var(--muted);margin-top:2px}.trade-sim-position{appearance:none;border:0;background:rgba(96,165,250,.12);color:var(--accent);font:inherit;font-size:10px;font-weight:900;padding:2px 6px;border-radius:999px;cursor:pointer;margin-right:3px}.trade-sim-position:hover{background:rgba(96,165,250,.22)}.trade-sim-player.position-match{border-color:var(--accent);box-shadow:0 0 0 2px rgba(96,165,250,.18);background:rgba(96,165,250,.08)}.trade-sim-player-value{text-align:right}.trade-sim-player-value b{display:block}.trade-sim-player-value span{font-size:10px;color:var(--muted)}.trade-sim-result{margin-top:16px}.trade-sim-result.valid{border-color:#2f855a}.trade-sim-result.invalid{border-color:#b45309}.trade-sim-summary{margin-top:14px;padding-top:12px;border-top:1px solid var(--border)}.trade-sim-summary p{margin:7px 0 0;color:var(--muted);line-height:1.55}.trade-sim-breakdown{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:10px}.trade-sim-breakdown>div{background:var(--bg-secondary);border:1px solid var(--border);border-radius:9px;padding:10px}.positive-text{color:#86efac}.negative-text{color:#fca5a5}@media(max-width:720px){.trade-sim-manager-row,.trade-sim-grid,.trade-sim-breakdown{grid-template-columns:1fr}.trade-sim-versus{text-align:center;padding:0}}

.time-machine-intro { margin-top:16px; }
.time-machine-grid { margin-top:14px; }
.time-machine-card { min-width:0; }
.time-machine-svg-wrap { width:100%; overflow-x:auto; }
.time-machine-svg { display:block; width:100%; min-width:620px; height:auto; }
.time-machine-legend { display:flex; flex-wrap:wrap; gap:7px 12px; margin-top:8px; }
.time-machine-key { display:inline-flex; align-items:center; gap:6px; color:var(--muted); font-size:11px; font-weight:700; }
.time-machine-key i { width:9px; height:9px; border-radius:999px; display:inline-block; }

.analytics-subtabs { display:flex; gap:8px; margin:0 0 20px; overflow-x:auto; padding-bottom:3px; }
.analytics-subtab { border:1px solid var(--border); background:var(--bg-secondary); color:var(--muted); border-radius:10px; padding:10px 14px; cursor:pointer; font-weight:800; white-space:nowrap; }
.analytics-subtab span { color:var(--accent); margin-left:5px; font-size:11px; }
.analytics-subtab.active { color:var(--text); border-color:var(--accent); background:var(--card-hover); box-shadow:inset 0 -2px 0 var(--accent); }
.player-subpage,.myteam-subpage,.draft-centre-subpage { display:none; }
.player-subpage.active,.myteam-subpage.active,.draft-centre-subpage.active { display:block; }
.analytics-subpage { display:none; }
.analytics-subpage.active { display:block; }
.overview-subpage { display:none; }
.overview-subpage.active { display:block; }
.overview-tabs { margin-top:16px; }
.analytics-axis-title { color:var(--muted-dark); font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:.45px; }
.analytics-axis-y { margin:0 0 8px 112px; }
.analytics-axis-x { text-align:center; margin-top:9px; }
.analytics-svg-axis-title { fill:#94a3b8; font-size:10px; font-weight:800; }
.analytics-chart-card { min-width:0; }
.analytics-manager-filter-card { margin-bottom:18px; }
.analytics-manager-filter-head { display:flex; align-items:flex-start; justify-content:space-between; gap:14px; }
.analytics-manager-filter-head h2 { margin-bottom:4px; }
.analytics-manager-chip-row { display:flex; flex-wrap:wrap; gap:7px; margin-top:12px; }
.analytics-manager-hidden { display:none !important; }
.analytics-manager-filter-card[hidden] { display:none !important; }
.analytics-player-summary { display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:10px; margin:0 0 15px; }
.analytics-player-summary p { margin:0; max-width:760px; }
#analytics-manager-chips .chart-chip.active { border-color:var(--chip-color,var(--accent)); box-shadow:inset 0 0 0 1px var(--chip-color,var(--accent)); }
.analytics-player-bar[hidden],.analytics-player-chart-empty[hidden],.analytics-player-dot[hidden] { display:none !important; }
.analytics-player-dot { cursor:crosshair; outline:none; }
.analytics-player-dot circle { opacity:.78; transition:opacity .13s,r .13s; }
.analytics-player-dot:hover circle,.analytics-player-dot:focus circle { opacity:1; stroke:white; stroke-width:2.4; r:8; }
.analytics-player-dot-label { display:none; pointer-events:none; paint-order:stroke; stroke:#0b1220; stroke-width:3px; stroke-linejoin:round; fill:#f8fafc; font-weight:850; }
.analytics-player-dot:hover .analytics-player-dot-label,.analytics-player-dot:focus .analytics-player-dot-label { display:block; }
.analytics-player-scatter.owner-filtered .analytics-player-dot-label { display:block; font-size:9px; }
.analytics-player-scatter.owner-filtered .analytics-player-circle { opacity:1; r:7; }

.analytics-bar-chart { display:flex; flex-direction:column; gap:9px; margin-top:14px; }
.analytics-bar-row { display:grid; grid-template-columns:minmax(100px,160px) minmax(80px,1fr) 58px; gap:10px; align-items:center; }
.analytics-bar-label { font-size:12px; font-weight:750; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.analytics-bar-track { height:9px; border-radius:999px; background:var(--bg-secondary); border:1px solid var(--border); overflow:hidden; }
.analytics-bar-fill { height:100%; border-radius:999px; background:linear-gradient(90deg,var(--accent-dark),var(--accent)); }
.analytics-manager-swatch{display:inline-block;width:9px;height:9px;border-radius:50%;flex:0 0 9px;margin-right:6px;vertical-align:1px}.analytics-pie-layout{display:grid;grid-template-columns:minmax(180px,240px) 1fr;gap:22px;align-items:center;margin-top:14px}.analytics-pie{width:min(220px,70vw);aspect-ratio:1;border-radius:50%;position:relative;margin:auto;box-shadow:inset 0 0 0 1px rgba(255,255,255,.06)}.analytics-pie-hole{position:absolute;inset:28%;border-radius:50%;background:var(--card);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;box-shadow:0 0 0 1px var(--border)}.analytics-pie-hole strong{font-size:22px;color:var(--text)}.analytics-pie-hole span{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}.analytics-pie-legend{display:grid;gap:7px}.analytics-pie-legend-row{display:grid;grid-template-columns:auto minmax(0,1fr) auto auto;gap:7px;align-items:center;font-size:11px}.analytics-pie-legend-row strong{color:var(--text)}.analytics-pie-legend-row small{color:var(--muted);min-width:42px;text-align:right}.analytics-pie-name{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--muted)}
.analytics-bar-value { text-align:right; font-size:12px; font-weight:800; }
.analytics-dual-chart { display:flex; flex-direction:column; gap:12px; margin-top:14px; }
.analytics-dual-row { display:grid; grid-template-columns:minmax(100px,150px) 1fr; gap:12px; align-items:center; }
.analytics-dual-bars { display:flex; flex-direction:column; gap:5px; }
.analytics-dual-series { display:grid; grid-template-columns:118px 1fr 42px; gap:8px; align-items:center; font-size:10px; color:var(--muted); }
.analytics-dual-series strong { color:var(--text); text-align:right; font-size:11px; }
.analytics-bar-fill-secondary { opacity:.5; }
.analytics-insight-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; margin-top:12px; }
.analytics-insight { border:1px solid var(--border); background:var(--bg-secondary); border-radius:12px; padding:14px; display:flex; flex-direction:column; gap:5px; }
.analytics-insight span { color:var(--accent); text-transform:uppercase; font-size:10px; font-weight:900; letter-spacing:.08em; }
.analytics-insight strong { font-size:14px; line-height:1.45; }
.analytics-insight small { color:var(--muted); }
.fixture-planner-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }
.fixture-week-block { margin:20px 0; }
.fixture-week-block h3 { color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.09em; }
.fixture-planner-card { border:1px solid var(--border); border-radius:14px; background:var(--bg-secondary); padding:15px; }
.fixture-rivalry-banner { margin:-4px 0 10px; text-align:center; font-size:11px; font-weight:900; color:var(--gold); text-transform:uppercase; letter-spacing:.08em; }
.fixture-planner-gw { color:var(--muted); text-align:center; font-size:10px; font-weight:900; }
.fixture-planner-match { display:grid; grid-template-columns:1fr auto 1fr; gap:10px; align-items:center; text-align:center; margin:8px 0 12px; }
.fixture-planner-match span { color:var(--muted); font-size:11px; }
.fixture-difficulty-row { display:flex; justify-content:center; flex-wrap:wrap; gap:8px; }
.fixture-difficulty-pill,.fixture-run-cell { border-radius:9px; padding:7px 9px; font-size:10px; font-weight:850; border:1px solid rgba(255,255,255,.08); }
.fixture-diff-soft { background:rgba(74,222,128,.13); }
.fixture-diff-kind { background:rgba(163,230,53,.11); }
.fixture-diff-medium { background:rgba(250,204,21,.11); }
.fixture-diff-hard { background:rgba(251,146,60,.13); }
.fixture-diff-brutal { background:rgba(248,113,113,.16); }
.fixture-run-cell { min-width:110px; display:flex; flex-direction:column; gap:3px; }
.fixture-run-cell span { color:var(--muted); font-size:9px; }
.trade-target-list { display:flex; flex-direction:column; gap:11px; }
.trade-target-row { border:1px solid var(--border); border-radius:13px; background:var(--bg-secondary); padding:14px; display:grid; grid-template-columns:minmax(150px,1.2fr) minmax(160px,1fr) auto; gap:14px; align-items:center; }
.trade-target-name { font-size:15px; font-weight:900; }
.trade-target-meta,.trade-target-reason { color:var(--muted); font-size:11px; margin-top:3px; }
.trade-target-scores { display:flex; gap:8px; flex-wrap:wrap; }
.trade-target-score { border:1px solid var(--border); border-radius:9px; padding:6px 8px; font-size:10px; }
.trade-target-score b { display:block; font-size:15px; color:var(--accent); }
.trade-target-offer { text-align:right; font-size:11px; }
.trade-target-offer b { display:block; color:var(--text); }
@media (max-width:760px) { .analytics-chart-grid,.analytics-insight-grid,.fixture-planner-grid{grid-template-columns:1fr;} .analytics-bar-row{grid-template-columns:100px minmax(70px,1fr) 50px;} .analytics-dual-row{grid-template-columns:1fr;} .analytics-dual-series{grid-template-columns:100px 1fr 38px;} .trade-target-row{grid-template-columns:1fr;} .trade-target-offer{text-align:left;} .analytics-pie-layout{grid-template-columns:1fr}.analytics-pie-legend{margin-top:4px} }

.future-fixtures-container { margin-top: 12px; }
.future-fixture-slide { display: none; }
.future-fixture-row { display:grid; grid-template-columns:minmax(0,1fr) 110px minmax(0,1fr); gap:12px; align-items:center; padding:13px 6px; border-bottom:1px solid var(--border); }
.future-fixture-row:last-child { border-bottom:0; }
.future-fixture-team { font-weight:800; }
.future-fixture-team.home { text-align:right; }
.future-fixture-v { text-align:center; font-weight:900; color:var(--muted); }
.fixture-derby { margin-top:4px; font-size:10px; line-height:1.15; text-transform:uppercase; letter-spacing:.08em; color:var(--text); }

.future-fixture-unified .fixture-team { justify-content:center; }
.future-fixture-unified .fixture-manager { font-weight:800; }
.unified-derby { grid-column:1 / -1; text-align:center; margin-bottom:8px; font-size:12px; letter-spacing:.08em; text-transform:uppercase; }
.storyline-latest p { font-size:16px; line-height:1.8; }
.season-story p { font-size:15px; line-height:1.75; }
@media (max-width:620px) { .future-fixture-row { grid-template-columns:minmax(0,1fr) 78px minmax(0,1fr); gap:8px; } .future-fixture-team{font-size:13px;} .fixture-derby{font-size:8px;} }


/* Dedicated Club Explorer and all-player squad-fit scouting */
.club-explorer-panel{display:none}.club-explorer-panel.active{display:block}
.season-summary-subpage{display:none}.season-summary-subpage.active{display:block}
.club-stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(125px,1fr));gap:10px;margin:14px 0}
.club-stat-card{padding:12px;border:1px solid var(--border,#334155);border-radius:10px;display:flex;flex-direction:column;gap:5px}
.club-stat-card span{font-size:.76rem;opacity:.75}.club-stat-card b{font-size:1.3rem}
.club-gw-bars{display:flex;align-items:flex-end;gap:7px;overflow-x:auto;padding:16px 8px;border-bottom:1px solid var(--border,#334155);min-height:190px}
.club-gw-bar-wrap{display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:5px;min-width:29px;font-size:.74rem}
.club-gw-bar{width:24px;background:#3b82f6;border-radius:5px 5px 0 0}
.scout-action{display:flex;align-items:center;justify-content:flex-end;min-width:145px}
@media(max-width:620px){.scout-action{min-width:0;justify-content:flex-start}.club-stat-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
"""


# ============================================================
# JAVASCRIPT
# ============================================================

