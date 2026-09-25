river_passport_css = r'''
.river-passport-card { display:flex; flex-direction:column; gap:16px; }
.river-passport-head { display:flex; justify-content:space-between; gap:16px; align-items:flex-start; flex-wrap:wrap; }
.river-passport-tools { display:flex; gap:12px; flex-wrap:wrap; align-items:flex-end; }
.river-passport-tools label { display:flex; flex-direction:column; gap:6px; color:var(--muted); font-weight:700; min-width:240px; }
.river-passport-tools input { background:var(--bg-secondary); color:var(--text); border:1px solid var(--border); border-radius:10px; padding:10px 12px; }
.river-passport-buttons { display:flex; gap:8px; flex-wrap:wrap; }
.river-passport-layout { display:grid; grid-template-columns:minmax(0,1.7fr) minmax(300px,1fr); gap:18px; align-items:start; }
.river-panel, .passport-detail { background:rgba(15,23,42,.45); border:1px solid var(--border); border-radius:18px; padding:16px; }
.passport-detail h3 { margin:0 0 6px; }
.passport-detail p { color:var(--muted); }
.transfer-river-chart { min-height:480px; }
.river-legend { margin-top:10px; }
.passport-hero { display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; margin-bottom:12px; }
.passport-owner-chip { display:inline-flex; align-items:center; gap:8px; background:var(--bg-secondary); border:1px solid var(--border); border-radius:999px; padding:6px 10px; font-weight:700; }
.passport-owner-chip i { width:12px; height:12px; border-radius:999px; display:inline-block; }
.passport-metrics { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin:12px 0 14px; }
.passport-metrics div { background:var(--bg-secondary); border:1px solid var(--border); border-radius:14px; padding:12px; }
.passport-metrics strong { display:block; font-size:20px; }
.passport-metrics small { color:var(--muted); }
.passport-section { margin-top:14px; }
.passport-section h4 { margin:0 0 8px; }
.passport-stints { display:flex; flex-direction:column; gap:8px; }
.passport-stint { display:flex; justify-content:space-between; gap:12px; background:var(--bg-secondary); border:1px solid var(--border); border-radius:12px; padding:10px 12px; flex-wrap:wrap; }
.passport-table { width:100%; border-collapse:collapse; }
.passport-table th, .passport-table td { padding:8px 10px; border-bottom:1px solid rgba(148,163,184,.18); text-align:left; }
.passport-table th { color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.04em; }
.passport-transactions { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:8px; }
.passport-transactions li { background:var(--bg-secondary); border:1px solid var(--border); border-radius:12px; padding:10px 12px; }
.passport-transactions b { color:var(--text); }
.passport-mover-list { list-style:none; margin:10px 0 0; padding:0; display:flex; flex-direction:column; gap:8px; }
.passport-mover-list li { display:flex; justify-content:space-between; gap:10px; padding:10px 12px; background:var(--bg-secondary); border:1px solid var(--border); border-radius:12px; }
.passport-mover-list button { background:none; border:none; color:inherit; text-align:left; width:100%; cursor:pointer; display:flex; justify-content:space-between; gap:10px; }
.passport-mover-list small { color:var(--muted); display:block; }
@media (max-width: 980px) {
  .river-passport-layout { grid-template-columns:1fr; }
  .passport-metrics { grid-template-columns:repeat(2,minmax(0,1fr)); }
}
@media (max-width: 640px) {
  .passport-metrics { grid-template-columns:1fr 1fr; }
  .transfer-river-chart { min-height:380px; }
}
'''

relationship_css = r"""

/* v48 — Player Relationship Graph */
.relationship-intro{margin-bottom:18px;min-width:0}
.relationship-eyebrow{display:block;font-size:10px;letter-spacing:.13em;text-transform:uppercase;font-weight:900;color:var(--accent);margin-bottom:9px}
.relationship-intro h2{font-size:24px;margin:0 0 9px}.relationship-intro .card-description{max-width:950px;line-height:1.6;margin-bottom:18px}
.relationship-mode-controls{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px}
.relationship-mode{background:rgba(128,145,168,.10);color:var(--text);border:1px solid var(--border);padding:10px 13px;border-radius:10px;font-size:12px;font-weight:800;cursor:pointer}
.relationship-mode.active{border-color:var(--accent);background:rgba(56,189,248,.17);box-shadow:inset 0 -2px 0 var(--accent)}
.relationship-controls{display:flex;align-items:end;flex-wrap:wrap;gap:10px;margin-bottom:14px}
.relationship-controls>label{font-size:11px;font-weight:850;color:var(--muted);display:flex;flex-direction:column;gap:6px;min-width:125px;flex:1 1 160px}
.relationship-controls input[type=search],.relationship-controls select{width:100%;min-width:0;background:var(--bg);border:1px solid var(--border);border-radius:9px;color:var(--text);padding:10px;font-size:12px;min-height:41px}
.relationship-controls>label:has(input[type=search]){flex:2 1 220px}
.relationship-controls>.relationship-check{flex:0 1 122px;display:flex;flex-direction:row;align-items:center;padding:10px 0;color:var(--text);line-height:1.3}
.relationship-check input{accent-color:var(--accent);width:15px;height:15px}
.relationship-reset{background:#22334a;border:1px solid var(--border);color:var(--text);border-radius:9px;padding:11px;min-height:41px;cursor:pointer;font-weight:800}
.relationship-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px;margin:12px 0 15px}
.relationship-stats>div{border:1px solid var(--border);border-radius:11px;background:rgba(128,145,168,.065);padding:12px 13px;display:flex;flex-direction:column;gap:4px}
.relationship-stats strong{font-size:22px;font-weight:950;line-height:1.2}.relationship-stats span{font-size:11px;color:var(--muted)}
.relationship-main{display:grid;grid-template-columns:minmax(0,3fr) minmax(255px,1fr);gap:12px;align-items:start}
.relationship-graph-panel{min-width:0;border:1px solid var(--border);border-radius:13px;overflow:hidden;background:radial-gradient(ellipse at 50% 50%,rgba(56,189,248,.035),transparent 60%),rgba(8,16,30,.60)}
.relationship-graph-toolbar{display:flex;justify-content:space-between;gap:10px;align-items:center;padding:10px 13px;border-bottom:1px solid var(--border);color:var(--muted);font-size:11px;font-weight:800}
.relationship-graph-toolbar>div{display:flex;gap:5px}.relationship-graph-toolbar button{background:rgba(128,145,168,.12);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:6px 10px;cursor:pointer;white-space:nowrap}
#relationship-svg{width:100%;height:auto;display:block;aspect-ratio:960/590;touch-action:pan-y;min-height:220px}
.relationship-link{stroke-linecap:round;stroke-opacity:.37;pointer-events:stroke}.relationship-link-current{stroke:#60a5fa}.relationship-link-history{stroke:#34d399}.relationship-link-trade{stroke:#fb923c}
.relationship-node{cursor:pointer;outline:none}.relationship-node circle{stroke:#e2e8f0;stroke-opacity:.92;stroke-width:1.6;transition:stroke-width .15s,stroke-opacity .15s}
.relationship-node:hover circle,.relationship-node:focus circle,.relationship-node.focused circle{stroke:#fff;stroke-width:3.2;stroke-opacity:1}
.relationship-node text{fill:#e9f1ff;stroke:#071322;stroke-width:2.4px;paint-order:stroke;stroke-linejoin:round;font-size:10.5px;font-weight:800;pointer-events:none;text-shadow:0 1px 3px #071322}
.relationship-node.focused text{font-size:13px}.relationship-node:focus-visible{outline:2px solid var(--accent)}
.relationship-legend{display:flex;gap:8px 14px;flex-wrap:wrap;padding:10px 13px;border-top:1px solid var(--border);color:var(--muted);font-size:10px}
.relationship-legend span{display:inline-flex;align-items:center;gap:5px}.relationship-legend i{height:8px;width:8px;border-radius:50%;display:inline-block}
.relationship-detail{border:1px solid var(--border);border-radius:13px;padding:15px;min-width:0;background:rgba(128,145,168,.045);max-height:700px;overflow-y:auto}
.relationship-detail h3{margin:6px 0 6px;font-size:19px}.relationship-detail h4{margin:17px 0 10px;font-size:12px;letter-spacing:.04em;text-transform:uppercase}.relationship-detail p{font-size:12px;color:var(--muted);line-height:1.5}
.relationship-detail-owner{display:flex;align-items:center;gap:8px;font-size:11px;font-weight:900;color:var(--muted)}.relationship-avatar{height:10px;width:10px;border-radius:50%;flex:0 0 auto;display:inline-block}
.relationship-detail-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;margin:14px 0}
.relationship-detail-metrics>div{border:1px solid var(--border);padding:9px;border-radius:9px;min-width:0}.relationship-detail-metrics strong{font-size:18px;display:block}.relationship-detail-metrics small{font-size:10px;color:var(--muted);display:block}
.relationship-neighbour{display:flex;width:100%;align-items:center;gap:9px;text-align:left;background:rgba(128,145,168,.035);border:0;border-bottom:1px solid var(--border);padding:9px 0;cursor:pointer;color:var(--text);font:inherit}
.relationship-neighbour:hover,.relationship-neighbour:focus-visible{background:rgba(128,145,168,.14);outline-offset:2px}.relationship-neighbour>span:nth-child(2){flex:1;min-width:0}.relationship-neighbour b{font-size:11px;display:block}.relationship-neighbour small{color:var(--muted);display:block;font-size:10px;line-height:1.35;padding-top:3px}.relationship-arrow{font-size:17px;color:var(--accent)}
.relationship-trade-list{padding-left:15px;margin:0}.relationship-trade-list li{font-size:11px;line-height:1.5;color:var(--muted);margin-bottom:9px}.relationship-trade-list b{color:var(--text)}
.relationship-footnote{font-size:11px;color:var(--muted);line-height:1.5;margin:13px 0 0}
#relationship-empty:not([hidden]){margin:0 12px 10px;padding:10px;font-size:11px}
@media(max-width:1050px){.relationship-main{grid-template-columns:minmax(0,1fr)}.relationship-detail{max-height:390px}.relationship-stats{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:650px){.relationship-intro h2{font-size:20px}.relationship-mode-controls{gap:5px}.relationship-mode{flex:1 1 45%;font-size:10px;padding:9px 5px}.relationship-controls>label{flex:1 1 46%}.relationship-controls>label:has(input[type=search]){flex:1 1 100%}.relationship-stats strong{font-size:18px}.relationship-graph-toolbar{font-size:10px}.relationship-legend{font-size:9px}}

"""

war_room_css = r'''
.war-room-shell{display:flex;flex-direction:column;gap:16px}
.war-room-hero{display:flex;justify-content:space-between;gap:18px;align-items:flex-start;flex-wrap:wrap}
.war-room-manager-select{display:flex;flex-direction:column;gap:6px;color:var(--muted);font-weight:800;min-width:230px}
.war-room-manager-select select{background:var(--bg-secondary);color:var(--text);border:1px solid var(--border);border-radius:10px;padding:10px 12px}
.war-room-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.war-room-card{background:rgba(15,23,42,.45);border:1px solid var(--border);border-radius:16px;padding:15px}
.war-room-card.full{grid-column:1/-1}
.war-room-matchup{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);gap:14px;align-items:center;text-align:center}
.war-room-side{background:var(--bg-secondary);border:1px solid var(--border);border-radius:14px;padding:14px}
.war-room-side h3{margin:0 0 6px;font-size:16px}.war-room-side strong{font-size:28px;display:block}.war-room-side small{color:var(--muted)}
.war-room-vs{font-weight:900;color:var(--muted)}
.war-room-prob{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:12px}
.war-room-prob div{background:var(--bg-secondary);border:1px solid var(--border);border-radius:12px;padding:10px;text-align:center}.war-room-prob strong{display:block;font-size:20px}.war-room-prob small{color:var(--muted)}
.war-room-pos-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.war-room-pos{background:var(--bg-secondary);border:1px solid var(--border);border-radius:12px;padding:12px}.war-room-pos b{display:block;margin-bottom:7px}.war-room-pos .edge{font-size:18px;font-weight:900}.war-room-pos .positive{color:#34d399}.war-room-pos .negative{color:#f87171}.war-room-pos small{color:var(--muted)}
.war-room-xi{display:grid;grid-template-columns:1fr 1fr;gap:18px}.war-room-xi-col h3{margin-top:0}
.war-room-pitch-wrap{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px;align-items:start}
.war-room-team-panel{min-width:0}
.war-room-pitch{position:relative;min-height:560px;border-radius:18px;padding:20px 12px;background:linear-gradient(180deg,rgba(21,94,59,.92),rgba(20,83,45,.96));border:2px solid rgba(255,255,255,.18);overflow:hidden;box-shadow:inset 0 0 0 1px rgba(255,255,255,.04)}
.war-room-pitch:before{content:'';position:absolute;inset:7% 4%;border:2px solid rgba(255,255,255,.28);border-radius:2px;pointer-events:none}.war-room-pitch:after{content:'';position:absolute;left:4%;right:4%;top:50%;border-top:2px solid rgba(255,255,255,.28);pointer-events:none}
.war-room-formation{position:relative;z-index:1;display:flex;flex-direction:column;justify-content:space-between;min-height:520px}
.war-room-line{display:flex;justify-content:center;gap:10px;align-items:center;min-height:100px}
.war-room-player-card{width:min(118px,24%);min-width:74px;background:rgba(15,23,42,.91);border:1px solid rgba(255,255,255,.2);border-radius:12px;color:var(--text);padding:8px 7px;cursor:pointer;text-align:center;box-shadow:0 6px 16px rgba(0,0,0,.22);transition:transform .12s,border-color .12s}
.war-room-player-card:hover,.war-room-player-card:focus{transform:translateY(-3px);border-color:#7dd3fc;outline:none}.war-room-player-card b{display:block;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.war-room-player-card small{display:block;color:#b8c5d6;font-size:10px;margin-top:2px}.war-room-player-card .wr-proj{font-size:15px;font-weight:900;color:var(--text);margin-top:4px}.war-room-player-card .wr-risk{display:inline-block;margin-top:4px;padding:2px 5px;border-radius:999px;font-size:9px;font-weight:850;background:#334155}.war-room-player-card .wr-risk.medium{background:#92400e}.war-room-player-card .wr-risk.high{background:#991b1b}
.war-room-bench{margin-top:12px;background:var(--bg-secondary);border:1px solid var(--border);border-radius:14px;padding:11px}.war-room-bench h4{margin:0 0 9px}.war-room-bench-list{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}.war-room-bench .war-room-player-card{width:100%;min-width:0;padding:7px 5px}
.war-room-player-detail{margin-top:16px;background:var(--bg-secondary);border:1px solid var(--border);border-radius:16px;padding:16px}.war-room-player-detail[hidden]{display:none}.war-room-player-detail-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin-top:12px}.war-room-player-detail-grid div{background:var(--card);border:1px solid rgba(148,163,184,.18);border-radius:12px;padding:10px}.war-room-player-detail-grid strong{display:block;font-size:18px}.war-room-player-detail-grid small{color:var(--muted)}.war-room-player-news{margin-top:12px;padding:10px 12px;border-left:3px solid #f59e0b;background:var(--card);border-radius:8px}.war-room-player-fixtures{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.war-room-player-fixture{background:var(--card);border:1px solid var(--border);border-radius:999px;padding:6px 9px;font-size:11px}
.war-room-flags{display:flex;flex-direction:column;gap:8px}.war-room-flag{background:var(--bg-secondary);border:1px solid var(--border);border-radius:12px;padding:10px 12px}.war-room-flag b{display:block}.war-room-flag small{color:var(--muted)}
.war-room-keys{margin:0;padding-left:20px}.war-room-keys li{margin:7px 0}
.war-room-upgrades{display:flex;flex-direction:column;gap:8px}.war-room-upgrade{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;background:var(--bg-secondary);border:1px solid var(--border);border-radius:12px;padding:11px 12px}.war-room-upgrade small{display:block;color:var(--muted)}.war-room-upgrade strong{font-size:18px;color:#34d399}
@media(max-width:900px){.war-room-grid{grid-template-columns:1fr}.war-room-card.full{grid-column:auto}.war-room-pos-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.war-room-xi{grid-template-columns:1fr}.war-room-matchup{grid-template-columns:1fr}.war-room-vs{padding:2px 0}.war-room-pitch-wrap{grid-template-columns:1fr}.war-room-player-detail-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:520px){.war-room-pitch{min-height:500px;padding:12px 7px}.war-room-formation{min-height:470px}.war-room-line{gap:5px;min-height:90px}.war-room-player-card{min-width:62px;padding:6px 4px}.war-room-player-card b{font-size:10px}.war-room-player-card .wr-proj{font-size:13px}.war-room-bench-list{grid-template-columns:repeat(2,minmax(0,1fr))}.war-room-player-detail-grid{grid-template-columns:1fr 1fr}}
'''


wi_css = r'''
.wi-shell{display:flex;flex-direction:column;gap:16px;min-width:0}
.wi-intro{display:flex;flex-direction:column;gap:15px}
.wi-intro h2{font-size:24px;margin:5px 0 1px}
.wi-intro .card-description{max-width:1080px;line-height:1.6}
.wi-controls{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.wi-controls label{display:flex;flex-direction:column;gap:6px;font-weight:780;font-size:12px;color:var(--muted)}
.wi-controls select{background:#0e1a2c;border:1px solid var(--border);border-radius:10px;padding:11px;color:var(--text);min-width:0;width:100%}
.wi-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.wi-stats div{background:#0c1a2d;border:1px solid #30445c;border-radius:12px;padding:13px;min-width:0}
.wi-stats strong{display:block;font-size:24px;font-variant-numeric:tabular-nums;line-height:1.25;color:#e5f5ff}
.wi-stats span{display:block;font-size:11px;color:var(--muted);margin-top:4px}
.wi-priority{display:flex;gap:6px;flex-wrap:wrap}
.wi-queue-team{display:flex;gap:7px;align-items:center;border:1px solid #31465e;border-left:4px solid var(--wi-team);background:#102137;border-radius:8px;padding:8px 10px;color:#d5e5f7;font-size:11px;min-width:0}
.wi-queue-team strong{color:var(--wi-team);font-variant-numeric:tabular-nums}
.wi-queue-team span{white-space:nowrap}
.wi-queue-team.mine{border-color:#eab308;background:#4a381a;color:var(--text)}
.wi-queue-team.mine b{font-size:9px;color:#fde68a}
.wi-notice{border:1px solid #30435c;background:#132339;border-radius:9px;color:#bbd0e6;font-size:11px;line-height:1.6;padding:12px}
.wi-notice span{display:inline-block;margin:2px 3px;padding:2px 6px;background:#233851;border-left:3px solid var(--wi-team);border-radius:5px}
.wi-grid{display:grid;grid-template-columns:minmax(0,1.65fr) minmax(300px,1fr);gap:16px;align-items:start}
.wi-heading{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
.wi-heading h2,.wi-ladder-card h2{margin:0 0 4px}
.wi-chip-row{display:flex;gap:14px;flex-wrap:wrap;margin:12px 0}
.wi-toggle{display:flex;gap:7px;align-items:center;font-size:11px;color:#b9d0e9}
.wi-target-scroll{max-height:790px;overflow:auto;overscroll-behavior:contain;display:flex;flex-direction:column;gap:9px;padding-right:4px}
.wi-target{border:1px solid #30445a;border-left:3px solid var(--wi-team);border-radius:12px;background:#101e32;padding:13px;min-width:0}
.wi-target-head{display:flex;align-items:start;justify-content:space-between;gap:8px;flex-wrap:wrap}
.wi-target-head strong{display:block;font-size:16px}
.wi-target-head small{color:var(--muted);display:block;margin-top:4px;font-size:11px}
.wi-risk{font-size:10px;font-weight:900;padding:5px 8px;border-radius:7px;white-space:nowrap}
.wi-risk.crowded{background:#532323;color:#ffb5a9}
.wi-risk.possible{background:#504021;color:#ffdfa0}
.wi-risk.clear{background:#13402c;color:#8beec4}
.wi-target-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:12px 0}
.wi-target-metrics>div{background:#0a1728;border-radius:8px;padding:9px;min-width:0}
.wi-target-metrics b{display:block;font-size:17px;font-variant-numeric:tabular-nums}
.wi-target-metrics b.wi-gain{color:#4ade80}
.wi-target-metrics small{display:block;color:var(--muted);font-size:10px;line-height:1.4;margin-top:2px}
.wi-drop,.wi-fix{margin:7px 0;color:#c5d6ec;font-size:11px;line-height:1.6}
.wi-fix{color:var(--muted)}.wi-flag{color:#facc15}
.wi-target-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:12px}
.wi-target-actions .relationship-reset{font-size:11px;min-height:32px}
.wi-target-actions details{flex:1 1 170px;font-size:11px;color:#a9c6e1}
.wi-target-actions summary{cursor:pointer}
.wi-contenders{display:flex;flex-direction:column;gap:5px;background:#0b1728;border-radius:10px;padding:10px;margin-top:6px;min-width:250px}
.wi-contender{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;border-bottom:1px solid #2d435a;padding:5px 0;font-size:10px}
.wi-contender span:first-child{font-weight:750}.wi-contender i{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--wi-team);margin-right:6px}
.wi-ladder-card{position:sticky;top:12px}.wi-ladder{display:flex;flex-direction:column;gap:7px;margin:14px 0;max-height:510px;overflow:auto}
.wi-ladder-empty{border:1px dashed #455b76;border-radius:10px;padding:16px;color:var(--muted);font-size:12px}
.wi-ladder-row{display:flex;gap:9px;align-items:center;border:1px solid #30435e;border-radius:10px;background:#0e1d30;padding:10px;min-width:0}
.wi-claim-num{display:flex;flex:0 0 28px;align-items:center;justify-content:center;height:28px;border-radius:50%;background:#254768;color:#a3daff;font-weight:900}
.wi-claim-body{flex:1;min-width:0}.wi-claim-body b{display:block;font-size:12px}.wi-claim-body small{display:block;color:var(--muted);font-size:10px;line-height:1.5}
.wi-claim-buttons{display:flex;gap:2px}.wi-claim-buttons button{background:#1c3048;border:1px solid #39516c;border-radius:7px;color:#f8fafc;width:24px;height:27px;cursor:pointer}.wi-claim-buttons button:disabled{opacity:.25;cursor:default}
.wi-ladder-actions{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}.wi-ladder-actions button{font-size:11px}
.wi-how{margin-top:12px;color:var(--muted);font-size:11px;line-height:1.65}.wi-how h3{font-size:12px;color:#e7f3ff}
@media(max-width:1080px){.wi-grid{grid-template-columns:1fr}.wi-ladder-card{position:static}.wi-ladder{max-height:none}}
@media(max-width:720px){.wi-controls{grid-template-columns:repeat(2,minmax(0,1fr))}.wi-stats{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:480px){.wi-controls{grid-template-columns:1fr 1fr;gap:8px}.wi-controls select{font-size:12px;padding:9px}.wi-target-metrics{gap:4px}.wi-target-metrics b{font-size:15px}.wi-target{padding:10px}}
.wi-search{flex:1 1 190px;min-width:130px;background:#0f1d30;color:var(--text);border:1px solid var(--border);padding:9px 12px;border-radius:9px}
.wi-assumed{display:flex;gap:6px;align-items:center;flex-wrap:wrap;font-size:11px;color:var(--muted);margin:2px 0 9px}
.wi-assumed:empty{display:none}.wi-assumed button{border:1px solid #664c3a;background:#342a25;color:#ffd5b9;border-radius:8px;padding:6px 9px;cursor:pointer}
'''

simulator_css = r"""
/* v53 — scenario-based Monte Carlo season simulator. */
.simulator-shell{display:flex;flex-direction:column;gap:17px;min-width:0}
.sim-hero{display:flex;justify-content:space-between;align-items:flex-start;gap:18px;flex-wrap:wrap}
.sim-hero h2{font-size:25px;margin:6px 0 8px}
.sim-hero p{max-width:850px}
.sim-status-puck{font-weight:850;font-size:12px;color:#67e8f9;background:#0b3043;border:1px solid #235269;border-radius:30px;padding:10px 14px;white-space:normal;max-width:320px}
.sim-controls-card{display:flex;flex-direction:column;gap:16px}
.sim-controls-grid{display:grid;grid-template-columns:minmax(180px,1.2fr) minmax(150px,1fr) minmax(150px,1fr) auto;gap:12px;align-items:end}
.sim-controls-grid label{color:var(--muted);font-size:12px;font-weight:800;display:flex;flex-direction:column;gap:7px}
.sim-controls-grid select{color:var(--text);background:var(--bg-secondary);border:1px solid var(--border);border-radius:10px;padding:11px 12px;font-size:13px;width:100%;min-width:0}
.sim-run-button{background:#0e7490;border:1px solid #38bdf8;border-radius:11px;color:var(--text);font-weight:900;padding:11px 17px;cursor:pointer;white-space:nowrap;min-height:43px}
.sim-run-button:disabled{opacity:.6;cursor:wait}
.sim-custom-controls{display:flex;justify-content:space-between;align-items:center;gap:18px;padding:14px;background:#111d30;border-radius:12px;border:1px solid #283c52}
.sim-custom-controls p{margin:5px 0 0;max-width:690px}
.sim-custom-controls label{display:flex;flex-direction:column;gap:6px;text-align:center;min-width:230px}
.sim-custom-controls input{accent-color:#38bdf8;width:100%}
.sim-custom-controls b{font-size:14px;color:#67e8f9}
.sim-scenario-switcher{display:flex;gap:8px;overflow-x:auto;padding:2px 0 8px;scrollbar-width:thin}
.sim-scenario-chip{flex:0 0 auto;border:1px solid var(--border);background:#122035;color:#b7c6dd;border-radius:12px;text-align:left;padding:12px 14px;cursor:pointer;min-width:145px;max-width:215px}
.sim-scenario-chip.active{border-color:#38bdf8;background:#18354b;box-shadow:inset 0 -3px 0 #38bdf8;color:#f8fafc}
.sim-scenario-chip strong{font-size:12px;display:block}
.sim-scenario-chip small{font-size:10px;color:#95aac2;display:block;margin-top:5px;line-height:1.4}
.sim-model-note{font-size:11px;color:var(--muted);line-height:1.65}
.sim-metric-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}
.sim-metric{border:1px solid var(--border);border-radius:15px;padding:15px;background:#13223a;min-width:0}
.sim-metric .label{display:block;font-size:11px;color:#9eb1c9;margin-bottom:7px;font-weight:750}
.sim-metric .value{display:block;font-size:26px;font-weight:900;color:#f8fafc;letter-spacing:-.03em;white-space:nowrap}
.sim-metric .delta{display:block;font-size:11px;color:#93c5fd;margin-top:5px}
.sim-dual-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:17px}
.sim-chart-card{min-width:0}
.sim-chart-card h2{font-size:16px;margin:0 0 7px}
.sim-chart-card svg{display:block;width:100%;height:auto;overflow:visible}
.sim-svg-label{fill:#9db4d1;font:11px sans-serif}
.sim-svg-axis{stroke:#425570;stroke-width:1}
.sim-svg-grid{stroke:#314156;stroke-width:.7;stroke-dasharray:4 4}
.sim-chart-legend{display:flex;gap:16px;flex-wrap:wrap;margin-top:10px;font-size:11px;color:var(--muted)}
.sim-chart-legend i{display:inline-block;width:12px;height:9px;margin-right:5px;border-radius:2px}
.sim-section-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;margin-bottom:12px}
.sim-section-head h2{margin:0 0 6px}
.sim-table-wrap{width:100%;overflow-x:auto;scrollbar-width:thin}
.sim-table{border-collapse:collapse;width:100%;font-size:12px;white-space:nowrap}
.sim-table th{color:#9cb2cb;font-size:11px;text-transform:uppercase;letter-spacing:.04em;text-align:right;padding:12px 10px;border-bottom:1px solid #35445b}
.sim-table th:first-child,.sim-table td:first-child{text-align:left;position:sticky;left:0;background:var(--card-bg,#111c2c);z-index:1}
.sim-table td{text-align:right;padding:12px 10px;border-bottom:1px solid rgba(148,163,184,.14)}
.sim-table tbody tr:hover td{background:#172b42}
.sim-table tr.selected td{background:#1c3850}
.sim-table .sim-scenario-name{font-weight:850;display:block}
.sim-table .sim-subtext{display:block;color:var(--muted);font-size:10px;white-space:normal;max-width:240px;margin-top:3px}
.sim-table .sim-heat{font-weight:850;min-width:39px;text-align:center;padding:9px 4px;border:1px solid #172235;font-size:10px}
.sim-manager-name{font-weight:850;display:flex;align-items:center;gap:7px}
.sim-manager-name i{width:8px;height:8px;border-radius:99px;flex:0 0 auto}
.sim-method-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px}
.sim-method-grid>div{border:1px solid var(--border);background:#112034;padding:13px;border-radius:12px}
.sim-method-grid b{color:#c7e5f7;font-size:13px}
.sim-method-grid p{font-size:12px;line-height:1.55;color:var(--muted);margin:7px 0 0}
.sim-loading{padding:35px;text-align:center;color:#9cb2cb;font-size:13px}
.sim-empty{padding:22px;color:var(--muted);border:1px dashed var(--border);border-radius:12px}
@media(max-width:1120px){.sim-controls-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.sim-metric-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:760px){.sim-dual-grid{grid-template-columns:1fr}.sim-method-grid{grid-template-columns:1fr}.sim-custom-controls{flex-direction:column;align-items:stretch}.sim-custom-controls label{min-width:0}.sim-metric-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.sim-hero h2{font-size:20px}}
@media(max-width:490px){.sim-controls-grid{grid-template-columns:1fr}.sim-metric .value{font-size:23px}.sim-scenario-chip{min-width:140px}}

/* v54 — All-manager trajectory filters and stackable custom simulations. */
.sim-trajectory-card{min-width:0}
.sim-dual-grid:has(.sim-trajectory-card){grid-template-columns:minmax(0,1fr)}
.sim-team-filter{display:flex;flex-direction:column;gap:10px;margin:13px 0 9px}
.sim-team-presets,.sim-team-chips{display:flex;gap:7px;flex-wrap:wrap;align-items:center}
.sim-team-presets button{border:1px solid #374960;background:#0c1829;color:#cce0f6;border-radius:999px;padding:7px 11px;font-size:11px;font-weight:850;cursor:pointer}
.sim-team-presets button:hover{border-color:#38bdf8}
.sim-team-chip{display:inline-flex;align-items:center;gap:6px;border:1px solid #35445a;background:#132238;color:#a1b8d0;border-radius:999px;padding:7px 10px;font-size:10.5px;font-weight:750;cursor:pointer;opacity:.65}
.sim-team-chip.active{color:#f8fafc;border-color:var(--sim-team-color);opacity:1;background:#19304a}
.sim-team-chip i{display:inline-block;background:var(--sim-team-color);width:8px;height:8px;border-radius:999px}
.sim-band-toggle{display:flex;align-items:center;gap:7px;color:#b4c6d9;font-size:11px;margin-bottom:12px}
.sim-band-toggle input{accent-color:#38bdf8}
.sim-trajectory-line{transition:stroke-width .2s,opacity .2s}
.sim-trajectory-line:hover{stroke-width:5;opacity:1}
.sim-trajectory-key{display:flex;flex-wrap:wrap;gap:9px 15px;margin:7px 0;font-size:10.5px;color:#c5d8eb}
.sim-trajectory-key span{display:inline-flex;align-items:center;gap:5px}
.sim-trajectory-key i{display:inline-block;width:9px;height:9px;border-radius:999px}
.sim-trajectory-key b{font-variant-numeric:tabular-nums;color:#f8fafc}
.sim-builder-card{display:flex;flex-direction:column;gap:15px}
.sim-builder-count{font-size:12px;font-weight:850;color:#67e8f9;border:1px solid #286076;border-radius:999px;background:#102d43;padding:9px 12px}
.sim-builder-controls{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.sim-builder-trade-controls{grid-template-columns:repeat(4,minmax(0,1fr))}
.sim-builder-controls label{min-width:0;color:#9db4d1;font-size:11px;font-weight:800;display:flex;flex-direction:column;gap:7px}
.sim-builder-controls input,.sim-builder-controls select{width:100%;min-width:0;border-radius:10px;border:1px solid #405069;background:#0b1a2d;padding:10px 12px;color:#f8fafc;font-size:12px}
.sim-builder-type-panel{padding:15px;border-radius:13px;background:#101e31;border:1px solid #2d4158}
.sim-builder-type-panel[hidden]{display:none!important}
.sim-helper-note{font-size:11px;line-height:1.5;color:#8ba3bb;margin:10px 0 0}
.sim-builder-actions{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.sim-builder-actions button{padding:10px 14px;min-height:40px;border-radius:10px;color:#f8fafc;font-size:12px;font-weight:850;cursor:pointer}
.sim-build-add{background:#124637;border:1px solid #379775}
.sim-build-run{background:#0e7490;border:1px solid #38bdf8}
.sim-build-clear{background:#293041;border:1px solid #53637a}
.sim-builder-feedback{font-size:12px;color:#79d7b4;min-height:13px}
.sim-builder-feedback.error{color:#fca5a5}
.sim-build-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
.sim-build-placeholder{border:1px dashed #3c4c64;border-radius:12px;padding:15px;color:#92a9c1;font-size:12px;grid-column:1/-1}
.sim-build-move{display:grid;grid-template-columns:auto 1fr auto;gap:10px;align-items:start;border-radius:12px;border:1px solid #385167;background:#16273c;padding:12px}
.sim-build-index{display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;background:#0c5a66;color:var(--text);font-size:11px;font-weight:850}
.sim-build-move strong{font-size:11px;color:#eff8ff}
.sim-build-move p{font-size:11px;line-height:1.5;margin:5px 0 0;color:#a9c3d9}
.sim-build-move button{border:0;background:#37252b;color:#fecaca;font-size:17px;font-weight:900;width:24px;height:24px;border-radius:7px;cursor:pointer}
.sim-custom-effects h4{margin:0 0 9px;font-size:12px}
.sim-custom-impact-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px}
.sim-custom-impact-grid>div{display:flex;gap:6px;flex-wrap:wrap;align-items:center;padding:10px 12px;border-radius:11px;border:1px solid #334c63;background:#0c2035;font-size:11px}
.sim-custom-impact-grid i{width:8px;height:8px;border-radius:50%}
.sim-custom-impact-grid strong{flex:1 1 100px}
.sim-custom-impact-grid span{font-weight:850}
.sim-custom-impact-grid span.positive{color:#67e8b6}
.sim-custom-impact-grid span.negative{color:#fda4af}
.sim-custom-impact-grid small{flex:1 1 100%;color:#91a9c3}
@media(max-width:980px){.sim-builder-trade-controls{grid-template-columns:repeat(2,minmax(0,1fr))}.sim-build-list{grid-template-columns:1fr}}
@media(max-width:560px){.sim-builder-controls,.sim-builder-trade-controls{grid-template-columns:1fr}.sim-trajectory-key{font-size:10px}}
.sim-save-variant-row{display:flex;align-items:end;gap:10px;flex-wrap:wrap;border-top:1px solid #31445b;padding-top:14px}
.sim-save-variant-row label{display:flex;flex-direction:column;gap:6px;color:#9db4d1;font-size:11px;font-weight:800;min-width:220px;flex:1 1 260px}
.sim-save-variant-row input{background:#0b1a2d;border:1px solid #405069;border-radius:10px;color:#f8fafc;padding:10px 12px;font-size:12px}
.sim-save-variant{border:1px solid #9b8ffb;background:#30376b;border-radius:10px;color:#f8fafc;font-size:12px;font-weight:850;padding:11px 14px;cursor:pointer}
.sim-save-variant-row .sim-helper-note{flex:1 1 230px;margin:0 0 3px}
.sim-saved-variants{display:flex;flex-wrap:wrap;gap:9px}
.sim-saved-caption{flex-basis:100%;font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:#a6bbd1;font-weight:900}
.sim-saved-item{display:flex;align-items:center;gap:8px;background:#171f3f;border:1px solid #52578a;border-radius:12px;padding:10px 12px}
.sim-saved-item span{display:flex;flex-direction:column;gap:5px;max-width:210px}
.sim-saved-item strong{font-size:11px;color:#e9e9ff}
.sim-saved-item small{font-size:10px;color:#a4aed5}
.sim-saved-item button{background:#313a6d;border:1px solid #5b68a3;border-radius:8px;padding:7px 9px;color:#eff2ff;cursor:pointer;font-size:11px;font-weight:800}

"""

javascript = r"""
// Accessible chart inspection: taps and keyboard activation work without hover.
function mcdraftShowChartInspector(detail,card,source){
    if(!detail)return;
    let box=document.getElementById('mcdraft-chart-inspector');
    if(!box){
        box=document.createElement('aside');box.id='mcdraft-chart-inspector';
        box.className='mcdraft-chart-inspector';box.setAttribute('role','status');
        box.setAttribute('aria-live','polite');
        const head=document.createElement('div');head.className='mcdraft-chart-inspector-head';
        const h=document.createElement('strong');h.className='mcdraft-chart-inspector-title';
        const close=document.createElement('button');close.type='button';close.textContent='×';
        close.setAttribute('aria-label','Close chart details');
        close.onclick=()=>{box.hidden=true;document.querySelectorAll('.mcdraft-chart-selected').forEach(el=>el.classList.remove('mcdraft-chart-selected'));};
        head.append(h,close);
        const body=document.createElement('p');body.className='mcdraft-chart-inspector-value';
        box.append(head,body);document.body.append(box);
    }
    document.querySelectorAll('.mcdraft-chart-selected').forEach(el=>el.classList.remove('mcdraft-chart-selected'));
    if(source)source.classList.add('mcdraft-chart-selected');
    const title=card?.querySelector('h2')?.textContent?.trim()||'Chart details';
    box.querySelector('.mcdraft-chart-inspector-title').textContent=title;
    box.querySelector('.mcdraft-chart-inspector-value').textContent=detail;
    box.hidden=false;
}
function mcdraftChartDetail(el){
    if(el.dataset?.chartDetail)return el.dataset.chartDetail;
    if(el.matches('.analytics-bar-row')){
        const label=el.querySelector('.analytics-bar-label')?.textContent?.trim();
        const value=el.querySelector('.analytics-bar-value')?.textContent?.trim();
        return label&&value?label+' · '+value:null;
    }
    if(el.matches('.analytics-player-dot,.matrix-manager-point')){
        return el.getAttribute('aria-label');
    }
    if(el.matches('circle,rect,path')){
        return el.querySelector('title')?.textContent||el.parentElement?.getAttribute('aria-label')||null;
    }
    return null;
}
document.addEventListener('click',function(event){
    const pie=event.target.closest?.('.analytics-pie');
    if(pie && pie.closest('.analytics-pie-card')){
        // CSS conic-gradient starts at 12 o'clock and proceeds clockwise.
        const bounds=pie.getBoundingClientRect();
        const dx=event.clientX-(bounds.left+bounds.width/2),
              dy=event.clientY-(bounds.top+bounds.height/2);
        const pct=(((Math.atan2(dx,-dy)*180/Math.PI)+360)%360)/3.6;
        const legend=Array.from(pie.closest('.analytics-pie-card').querySelectorAll('[data-pie-start]'))
            .find(item=>pct>=Number(item.dataset.pieStart)&&pct<Number(item.dataset.pieEnd)+.0001);
        if(legend){legend.click();return;}
    }
    const target=event.target.closest?.('[data-chart-detail],.analytics-chart-card .analytics-bar-row,.analytics-chart-card svg circle,.analytics-player-dot,.matrix-manager-point,.rating-lab-trend circle,.time-machine-svg circle');
    if(!target)return;
    const card=target.closest('.analytics-chart-card,.rating-lab-trend-card,.rating-lab-hist-card');
    if(!card)return;
    const detail=mcdraftChartDetail(target);
    if(detail)mcdraftShowChartInspector(detail,card,target);
});
document.addEventListener('keydown',function(event){
    if(event.key!=='Enter'&&event.key!==' ')return;
    const target=event.target.closest?.('[data-chart-detail],.analytics-chart-card .analytics-bar-row,.analytics-chart-card svg circle,.rating-lab-trend circle,.matrix-manager-point');
    if(!target)return;
    event.preventDefault();target.click();
});

// Cup filter only changes highlighting; actual bracket progression is Python-side.
function filterCupTeams(){
    const control=document.getElementById('cup-team-filter');
    if(!control)return;
    const team=control.value;
    document.querySelectorAll('.cup-tie').forEach(tie=>{
        const inTie=!!team&&(tie.dataset.cupTeams||'').split('|').includes(team);
        tie.classList.toggle('cup-dim',!!team&&!inTie);
        tie.classList.toggle('cup-highlight',!!team&&inTie);
    });
}

/* ============================================================
   MY TEAM SELECTOR
   ============================================================ */

// My Team vulnerability snapshot (current roster; every axis is exposure).
const SQUAD_VULNERABILITY_DATA = __SQUAD_VULNERABILITY_DATA__;
const VULNERABILITY_COLOURS={low:'#29a57b',moderate:'#d2a34a',high:'#e17e42',critical:'#dd5364'};
let vulnerabilitySelectedAxis='';
let vulnerabilityCompareLeague=true;
function vulnerabilityLevel(score){
 if(score===null||score===undefined)return {label:'Unscored',key:'low'};
 return score<25?{label:'Low',key:'low'}:score<50?{label:'Moderate',key:'moderate'}:score<75?{label:'High',key:'high'}:{label:'Very high',key:'critical'};
}
function vulnerabilityAxisDetail(key){
 vulnerabilitySelectedAxis=key;
 const manager=currentMyTeamManager(),record=SQUAD_VULNERABILITY_DATA[manager],axis=(record?.axes||[]).find(a=>a.key===key);
 const panel=document.getElementById('myteam-vulnerability-detail');if(!panel||!axis)return;
 const label=vulnerabilityLevel(axis.score);
 panel.innerHTML='<div class="vuln-detail-head"><div><span class="vuln-eyebrow">Selected exposure</span><h3>'+escapePlayerHTML(axis.label)+'</h3></div><span class="vuln-risk-badge vuln-'+label.key+'">'+(axis.score===null?'N/A':Math.round(axis.score)+'/100')+' · '+label.label+'</span></div>'+
 '<p>'+escapePlayerHTML(axis.summary)+'</p><div class="vuln-driver-list">'+(axis.drivers||[]).map(s=>'<div>'+escapePlayerHTML(s)+'</div>').join('')+'</div>';
 document.querySelectorAll('.vuln-axis-button').forEach(btn=>btn.setAttribute('aria-pressed',String(btn.dataset.axis===key)));
 document.querySelectorAll('.vuln-radar-point').forEach(dot=>dot.classList.toggle('selected',dot.dataset.axis===key));
}
function toggleVulnerabilityComparison(){vulnerabilityCompareLeague=!vulnerabilityCompareLeague;renderMyTeamVulnerability();}
function renderMyTeamVulnerability(){
 const root=document.getElementById('myteam-vulnerability');if(!root)return;
 const manager=currentMyTeamManager(),record=SQUAD_VULNERABILITY_DATA[manager];
 if(!record||!record.axes?.length){root.innerHTML='<div class="notice">'+escapePlayerHTML(record?.warning||'No current squad data available.')+'</div>';return;}
 const axes=record.axes,n=axes.length,cx=180,cy=170,r=103;
 const point=(i,amount)=>{const angle=2*Math.PI*i/n-Math.PI/2;return [(cx+r*amount*Math.cos(angle)).toFixed(1),(cy+r*amount*Math.sin(angle)).toFixed(1)].join(',');};
 const mean=axes.map((a,i)=>{const nums=Object.values(SQUAD_VULNERABILITY_DATA).map(team=>team.axes?.[i]?.score).filter(v=>Number.isFinite(v));return nums.length?nums.reduce((s,v)=>s+v,0)/nums.length:50;});
 const poly=(values)=>values.map((v,i)=>point(i,Math.max(0,Math.min(100,Number(v)||0))/100)).join(' ');
 let svg='<svg class="vuln-radar" viewBox="0 0 360 350" role="group" aria-label="'+escapePlayerHTML(manager)+' squad vulnerability radar, higher means more risk">';
 [0.25,0.50,0.75,1].forEach(level=>svg+='<polygon class="vuln-grid" points="'+axes.map((_,i)=>point(i,level)).join(' ')+'"/>');
 axes.forEach((a,i)=>svg+='<line class="vuln-axis-line" x1="'+cx+'" y1="'+cy+'" x2="'+point(i,1).replace(',', '" y2="')+'"/>');
 if(vulnerabilityCompareLeague)svg+='<polygon class="vuln-league-area" points="'+poly(mean)+'"/>';
 svg+='<polygon class="vuln-squad-area" points="'+poly(axes.map(a=>a.score===null?50:a.score))+'"/>';
 const short=['Star reliance','Medical','Positional cover','Club stacking','Fixtures','Two-star shock'];
 axes.forEach((a,i)=>{
  const value=a.score===null?50:a.score,xy=point(i,value/100).split(',');
  const angle=2*Math.PI*i/n-Math.PI/2,lx=cx+143*Math.cos(angle),ly=cy+136*Math.sin(angle);
  svg+='<text class="vuln-label" x="'+lx.toFixed(1)+'" y="'+(ly+4).toFixed(1)+'" text-anchor="middle">'+short[i]+'</text>';
  svg+='<g role="button" tabindex="0" class="vuln-radar-point'+(a.key===vulnerabilitySelectedAxis?' selected':'')+'" data-axis="'+a.key+'" aria-label="'+escapePlayerHTML(a.label)+': '+(a.score===null?'not available':Math.round(a.score)+'/100')+'; tap for details" onclick="vulnerabilityAxisDetail(\''+a.key+'\')" onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();vulnerabilityAxisDetail(\''+a.key+'\');}">'+
   '<circle class="vuln-touch-target" cx="'+xy[0]+'" cy="'+xy[1]+'" r="18"/><circle class="vuln-dot" cx="'+xy[0]+'" cy="'+xy[1]+'" r="5"/>'+
   '<title>'+escapePlayerHTML(a.label)+': '+(a.score===null?'N/A':Math.round(a.score)+'/100')+'</title></g>';
 });
 svg+='</svg>';
 const badge=vulnerabilityLevel(record.overall),scoreText=record.overall===null?'—':Math.round(record.overall);
 const legend='<div class="vuln-legend"><span><i class="vuln-squad-swatch"></i>Selected squad</span>'+
 (vulnerabilityCompareLeague?'<span><i class="vuln-league-swatch"></i>League average</span>':'')+'</div>';
 const buttons=axes.map(a=>{const level=vulnerabilityLevel(a.score);return '<button type="button" class="vuln-axis-button" data-axis="'+a.key+'" aria-pressed="'+String(a.key===vulnerabilitySelectedAxis)+'" onclick="vulnerabilityAxisDetail(\''+a.key+'\')"><span><i class="vuln-axis-dot vuln-'+level.key+'"></i>'+escapePlayerHTML(a.label)+'</span><strong>'+(a.score===null?'N/A':Math.round(a.score)+'/100')+'</strong><small>'+level.label+' exposure</small></button>';}).join('');
 root.innerHTML='<div class="vuln-head"><div class="vuln-overall"><span>Overall vulnerability</span><strong>'+scoreText+'<small>/100</small></strong><span class="vuln-risk-badge vuln-'+badge.key+'">'+badge.label+' exposure</span></div><div class="vuln-meta">GW'+record.as_of_gw+' · Current roster<br>Higher numbers mean MORE risk</div></div>'+
 '<div class="vuln-layout"><div class="vuln-visual">'+svg+legend+'<button type="button" class="vuln-compare" onclick="toggleVulnerabilityComparison()" aria-pressed="'+String(vulnerabilityCompareLeague)+'">'+(vulnerabilityCompareLeague?'Hide':'Show')+' league average</button></div><div class="vuln-axes">'+buttons+'</div></div>'+
 '<div class="vuln-detail" id="myteam-vulnerability-detail" aria-live="polite"></div>'+
 '<p class="vuln-footnote">Based on the current Draft roster and the dashboard’s next-GW projection, FPL availability, legal formations and next five PL fixtures. The scores are modelled exposure, not injury forecasts or win probabilities.</p>';
 if(!axes.some(a=>a.key===vulnerabilitySelectedAxis))vulnerabilitySelectedAxis=[...axes].filter(a=>a.available).sort((a,b)=>(b.score||0)-(a.score||0))[0]?.key||axes[0].key;
 vulnerabilityAxisDetail(vulnerabilitySelectedAxis);
}

const defaultMyTeamIndex = __DEFAULT_MY_TEAM_INDEX__;
const myTeamStorageKey = "fpl-draft-my-team";

function changeMyTeam() {
    const select = document.getElementById("my-team-select");
    if (!select) return;

    const selectedIndex = Number(select.value);

    document.querySelectorAll(".my-team-card").forEach(function(card) {
        const cardIndex = Number(card.dataset.managerIndex);
        card.style.display = cardIndex === selectedIndex ? "block" : "none";
    });

    try {
        localStorage.setItem(myTeamStorageKey, String(selectedIndex));
    } catch (e) {
        // localStorage may be unavailable in private/restricted browsers.
    }

    renderMyTeamSquad();
    renderMyTeamRadar();
    renderMyTeamVulnerability();
    renderFiveGWPlanner();
    renderMyTeamStatsCharts();
    renderMyTeamPositionNeeds();
    renderMyTeamFreeAgents();
    renderMyTeamTradeTargets();
    renderMyTeamSellHigh();
    if (typeof renderPlayerScout === 'function') renderPlayerScout();
    renderMyTeamH2H();
}


function initialiseMyTeam() {
    const select = document.getElementById("my-team-select");
    if (!select) return;

    let selectedIndex = defaultMyTeamIndex;

    try {
        const saved = localStorage.getItem(myTeamStorageKey);
        if (saved !== null && Number.isInteger(Number(saved))) {
            const candidate = Number(saved);
            if (candidate >= 0 && candidate < select.options.length) {
                selectedIndex = candidate;
            }
        }
    } catch (e) {
        // Fall back to the default team.
    }

    select.value = String(selectedIndex);
    changeMyTeam();
}

/* ============================================================
   GLOBAL SEARCH
   ============================================================ */
const GLOBAL_PAGES=[['Overview','overview'],['My Team','myteam'],['Gameweeks','gameweeks'],['Fixtures','fixtures'],['Players','players'],['Clubs','clubs'],['Transfers','transfers'],['Analytics','analytics'],['Draft Centre','draft-centre'],['Season Summary','season-summary']];

function ensureSearchTargetId(el, idx){
    if(!el.id) el.id='global-search-target-'+idx;
    return el.id;
}

function buildDashboardSearchIndex(){
    const results=[];
    GLOBAL_PAGES.forEach(r=>results.push({type:'page',label:r[0],value:r[1],meta:'Page'}));
    (MANAGER_ORDER||[]).forEach(m=>results.push({type:'manager',label:m,value:m,meta:'Manager'}));
    Object.values(CLUB_EXPLORER_DATA||{}).forEach(c=>results.push({type:'club',label:c.name,value:String(c.id),meta:'Premier League club'}));
    (playerSearchData||[]).forEach(p=>results.push({type:'player',label:p.name,value:String(p.id),meta:(p.position||'')+' · '+(p.team||'')}));
    document.querySelectorAll('#page-players .player-page-tab').forEach(btn=>{
        const label=(btn.textContent||'').trim();
        const m=(btn.getAttribute('onclick')||'').match(/showPlayerSubtab\('([^']+)'/);
        if(label&&m)results.push({type:'player-subtab',label:label,value:m[1],meta:'Players section'});
    });

    let idx=0;
    document.querySelectorAll('#page-season-summary .season-summary-tab').forEach(btn=>{
        const label=(btn.textContent||'').trim();
        const m=(btn.getAttribute('onclick')||'').match(/showSeasonSummarySubtab\('([^']+)'/);
        if(label&&m)results.push({type:'season-subtab',label:label,value:m[1],meta:'Season Summary section'});
    });
    document.querySelectorAll('#page-analytics .analytics-subtab').forEach(btn=>{
        const label=(btn.textContent||'').replace(/\s+\d+\s*$/,'').trim();
        const m=(btn.getAttribute('onclick')||'').match(/showAnalyticsSubtab\('([^']+)'/);
        if(label&&m) results.push({type:'analytics-subtab',label:label,value:m[1],meta:'Analytics section'});
    });

    document.querySelectorAll('.page .card h2, .page .card h3').forEach(h=>{
        const label=(h.textContent||'').trim();
        if(!label) return;
        const card=h.closest('.card');
        const page=h.closest('.page');
        if(!card||!page) return;
        const pageName=(page.id||'').replace(/^page-/,'');
        const targetId=ensureSearchTargetId(card,idx++);
        const sub=card.closest('.analytics-subpage');
        const seasonSub=card.closest('.season-summary-subpage');
        const playerSub=card.closest('.player-subpage');
        const analyticsSub=sub ? (sub.id||'').replace(/^analytics-sub-/,'') : (seasonSub ? (seasonSub.id||'').replace(/^season-summary-sub-/,'') : (playerSub ? (playerSub.id||'').replace(/^player-sub-/,'') : ''));
        results.push({type:'section',label:label,value:targetId,page:pageName,subtab:analyticsSub,meta:(pageName==='analytics'?'Analytics chart/section':'Section')});
    });
    return results;
}

function globalSearchSelect(type,value,label,pageName,subtab){
    const box=document.getElementById('global-search-results'),input=document.getElementById('global-search');
    if(box){box.classList.remove('active');box.innerHTML='';} if(input)input.value='';
    if(type==='page'){showPage(value);return;}
    if(type==='manager'){showPage('myteam');const select=document.getElementById('my-team-select');if(select){for(let i=0;i<select.options.length;i++){if(select.options[i].text===label){select.value=String(i);changeMyTeam();break;}}}return;}
    if(type==='player'){showPage('players');showPlayerSubtab('directory',document.querySelectorAll('.player-page-tab')[1]);const p=document.getElementById('player-search');if(p){p.value=label;filterPlayers();}return;}
    if(type==='player-subtab'){
        showPage('players');
        const btn=Array.from(document.querySelectorAll('.player-page-tab')).find(b=>(b.getAttribute('onclick')||'').includes("'"+value+"'"));
        showPlayerSubtab(value,btn||null);return;
    }
    if(type==='club'){showPage('clubs');const sel=document.getElementById('club-explorer-select');if(sel){sel.value=String(value);renderClubExplorer();}showClubSubtab('overview',document.querySelector('.club-explorer-tab'));return;}
    if(type==='season-subtab'){showPage('season-summary');const btn=Array.from(document.querySelectorAll('.season-summary-tab')).find(b=>(b.getAttribute('onclick')||'').includes("'"+value+"'"));showSeasonSummarySubtab(value,btn||null);return;}
    if(type==='analytics-subtab'){
        showPage('analytics');
        const btn=Array.from(document.querySelectorAll('#page-analytics .analytics-subtab')).find(b=>(b.getAttribute('onclick')||'').includes("'"+value+"'"));
        showAnalyticsSubtab(value,btn||null);
        return;
    }
    if(type==='section'){
        showPage(pageName||'overview');
        if((pageName||'overview')==='overview' && typeof showOverviewSubtab==='function') showOverviewSubtab('intelligence',document.querySelectorAll('.overview-tab')[1]);
        if(pageName==='season-summary'&&subtab){
            const btn=Array.from(document.querySelectorAll('.season-summary-tab')).find(b=>(b.getAttribute('onclick')||'').includes("'"+subtab+"'"));
            showSeasonSummarySubtab(subtab,btn||null);
        }
        if(pageName==='players'&&subtab){
            const btn=Array.from(document.querySelectorAll('.player-page-tab')).find(b=>(b.getAttribute('onclick')||'').includes("'"+subtab+"'"));
            showPlayerSubtab(subtab,btn||null);
        }
        if(pageName==='analytics'&&subtab){
            const btn=Array.from(document.querySelectorAll('#page-analytics .analytics-subtab')).find(b=>(b.getAttribute('onclick')||'').includes("'"+subtab+"'"));
            showAnalyticsSubtab(subtab,btn||null);
        }
        setTimeout(()=>{const el=document.getElementById(value); if(el){el.scrollIntoView({behavior:'smooth',block:'start'}); el.classList.add('search-hit'); setTimeout(()=>el.classList.remove('search-hit'),1600);}},60);
    }
}

function runGlobalSearch(){
    const input=document.getElementById('global-search'),box=document.getElementById('global-search-results'); if(!input||!box)return;
    const q=input.value.trim().toLowerCase(); if(!q){box.classList.remove('active');box.innerHTML='';return;}
    const results=buildDashboardSearchIndex().filter(r=>((r.label||'')+' '+(r.meta||'')).toLowerCase().includes(q));
    const seen=new Set();
    const visible=[];
    for(const r of results){const key=r.type+'|'+r.label+'|'+(r.page||'')+'|'+(r.subtab||''); if(seen.has(key))continue; seen.add(key); visible.push(r); if(visible.length>=18)break;}
    const esc=t=>String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    box.innerHTML=visible.length?visible.map(r=>'<div class="global-search-result" data-type="'+esc(r.type)+'" data-value="'+esc(r.value)+'" data-label="'+esc(r.label)+'" data-page="'+esc(r.page||'')+'" data-subtab="'+esc(r.subtab||'')+'"><strong>'+esc(r.label)+'</strong><span>'+esc(r.meta)+'</span></div>').join(''):'<div class="global-search-result"><strong>No matches</strong><span>Try a chart, player, manager, page or section</span></div>';
    box.classList.add('active');
    box.querySelectorAll('[data-type]').forEach(el=>el.addEventListener('click',()=>globalSearchSelect(el.dataset.type,el.dataset.value,el.dataset.label,el.dataset.page,el.dataset.subtab)));
}
document.addEventListener('click',event=>{const wrap=document.querySelector('.global-search-wrap'),box=document.getElementById('global-search-results');if(wrap&&box&&!wrap.contains(event.target))box.classList.remove('active');});

/* ============================================================
   PAGE NAVIGATION
   ============================================================ */

const navButtons =
    document.querySelectorAll(
        ".nav-button"
    );

const pages =
    document.querySelectorAll(
        ".page"
    );


function resizeCharts() {

    if (typeof Plotly === "undefined") {
        return;
    }

    document
        .querySelectorAll(".js-plotly-plot")
        .forEach(function(chart) {

            try {
                Plotly.Plots.resize(chart);
            } catch (error) {
                /* Ignore charts that are not ready yet. */
            }

        });

}


// Player Analytics uses the exact same Manager-filter state and chip controls
// as the rest of Analytics. A separate Free agents chip only affects players.
const analyticsManagerState = { visible: new Set(), includeFreeAgents: true };

function applyPlayerAnalyticsFilter(){
    const page=document.getElementById('page-analytics');
    if(!page) return;
    const selected=analyticsManagerState.visible;
    const includeFreeAgents=analyticsManagerState.includeFreeAgents;
    const allOwners=selected.size===MANAGER_ORDER.length && includeFreeAgents;
    const onlyOneOwner=(selected.size===1 && !includeFreeAgents) ||
                       (selected.size===0 && includeFreeAgents);
    function selectedOwner(owner){
        return selected.has(owner) || (owner==='Free agents' && includeFreeAgents);
    }
    page.querySelectorAll('.analytics-player-scatter').forEach(function(card){
        let shown=0;
        // Labels for every dot are useful for one team, but messy for Top 5.
        card.classList.toggle('owner-filtered',onlyOneOwner);
        card.querySelectorAll('.analytics-player-dot').forEach(function(dot){
            const visible=selectedOwner(dot.getAttribute('data-player-owner'));
            dot.hidden=!visible;
            dot.setAttribute('aria-hidden',String(!visible));
            if(visible) shown++;
        });
        const empty=card.querySelector('.analytics-player-chart-empty');
        if(empty) empty.hidden=shown!==0;
    });
    page.querySelectorAll('.analytics-player-bar-card').forEach(function(card){
        const cap=Math.max(1,Number(card.getAttribute('data-player-limit')||20));
        const matching=Array.from(card.querySelectorAll('.analytics-player-bar')).filter(function(row){
            return selectedOwner(row.getAttribute('data-player-owner'));
        });
        const visible=matching.slice(0,cap);
        const scale=Math.max(1,...visible.map(function(row){return Math.abs(Number(row.getAttribute('data-player-value'))||0);}));
        card.querySelectorAll('.analytics-player-bar').forEach(function(row){row.hidden=!visible.includes(row);});
        visible.forEach(function(row){
            const fill=row.querySelector('.analytics-bar-fill');
            if(fill) fill.style.width=Math.max(2,Math.abs(Number(row.getAttribute('data-player-value'))||0)/scale*100).toFixed(1)+'%';
        });
        const empty=card.querySelector('.analytics-player-chart-empty');
        if(empty) empty.hidden=matching.length!==0;
    });
    // Recalculate positional totals using precisely the same owner selection.
    page.querySelectorAll('.analytics-player-position-card').forEach(function(card){
        const totals={'GKP':0,'DEF':0,'MID':0,'FWD':0};
        let shown=0;
        card.querySelectorAll('.analytics-position-player').forEach(function(record){
            if(!selectedOwner(record.getAttribute('data-player-owner'))) return;
            const pos=record.getAttribute('data-player-position');
            if(Object.hasOwn(totals,pos)) totals[pos]+=Number(record.getAttribute('data-player-points'))||0;
            shown++;
        });
        const maximum=Math.max(1,...Object.values(totals));
        card.querySelectorAll('[data-player-position].analytics-bar-row').forEach(function(row){
            const pos=row.getAttribute('data-player-position');
            const total=totals[pos]||0;
            const fill=row.querySelector('.analytics-bar-fill');
            if(fill){
                fill.style.width=(total>0 ? Math.max(2,total/maximum*100) : 0).toFixed(1)+'%';
                const singleOwner=selected.size===1 && !includeFreeAgents ? Array.from(selected)[0] : null;
                fill.style.background=singleOwner ? (MANAGER_COLORS[singleOwner]||'') :
                    (selected.size===0 && includeFreeAgents ? '#64748b' : '');
            }
            const value=row.querySelector('.analytics-bar-value');
            if(value) value.textContent=total.toFixed(0);
        });
        const empty=card.querySelector('.analytics-player-chart-empty');
        if(empty) empty.hidden=shown!==0;
    });
    const count=document.getElementById('analytics-player-count');
    if(count){
        const roster=Array.from(page.querySelectorAll('.analytics-player-bar, .analytics-player-dot'));
        const owned=new Set(roster.filter(function(el){return selectedOwner(el.getAttribute('data-player-owner'));})
            .map(function(el){return el.getAttribute('data-player-id');}));
        count.textContent=owned.size+' players in charts'+(allOwners?' (all owners)':'');
    }
}

async function shareMcDraftCard(button){
    const text=(button && button.dataset && button.dataset.shareText) ? button.dataset.shareText : '';
    if(!text) return;
    try{
        if(navigator.share){ await navigator.share({title:'McDraft 26/27',text:text}); return; }
        if(navigator.clipboard){ await navigator.clipboard.writeText(text); const old=button.textContent; button.textContent='Copied!'; setTimeout(()=>button.textContent=old,1300); return; }
    }catch(err){ if(err && err.name==='AbortError') return; }
    window.prompt('Copy this McDraft card:',text);
}

function initAnalyticsManagerFilter() {
    analyticsManagerState.visible = new Set(MANAGER_ORDER);
    analyticsManagerState.includeFreeAgents = true;
    renderAnalyticsManagerChips();
    applyAnalyticsManagerFilter();
    setMatrixGroup(matrixSelectedGroup);
}

function setAnalyticsManagerPreset(preset) {
    if (preset === "top5") {
        analyticsManagerState.visible = new Set(MANAGER_ORDER.slice(0, Math.min(5, MANAGER_ORDER.length)));
        analyticsManagerState.includeFreeAgents = false;
    } else if (preset === "all") {
        analyticsManagerState.visible = new Set(MANAGER_ORDER);
        analyticsManagerState.includeFreeAgents = true;
    } else if (preset === "none") {
        analyticsManagerState.visible = new Set();
        analyticsManagerState.includeFreeAgents = false;
    }
    renderAnalyticsManagerChips();
    applyAnalyticsManagerFilter();
}

function toggleAnalyticsManager(manager) {
    if (analyticsManagerState.visible.has(manager)) analyticsManagerState.visible.delete(manager);
    else analyticsManagerState.visible.add(manager);
    renderAnalyticsManagerChips();
    applyAnalyticsManagerFilter();
}

function toggleAnalyticsFreeAgents() {
    analyticsManagerState.includeFreeAgents = !analyticsManagerState.includeFreeAgents;
    renderAnalyticsManagerChips();
    applyAnalyticsManagerFilter();
}

function renderAnalyticsManagerChips() {
    const container = document.getElementById("analytics-manager-chips");
    if (!container) return;
    container.innerHTML = "";
    [["Top 5","top5"],["All","all"],["None","none"]].forEach(function(pair) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "chart-chip-action";
        button.textContent = pair[0];
        button.addEventListener("click", function(){ setAnalyticsManagerPreset(pair[1]); });
        container.appendChild(button);
    });
    MANAGER_ORDER.forEach(function(manager) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "chart-chip" + (analyticsManagerState.visible.has(manager) ? " active" : "");
        button.style.setProperty("--chip-color", MANAGER_COLORS[manager]);
        button.textContent = manager;
        button.setAttribute('aria-pressed',String(analyticsManagerState.visible.has(manager)));
        button.addEventListener("click", function(){ toggleAnalyticsManager(manager); });
        container.appendChild(button);
    });
    const freeAgents = document.createElement('button');
    freeAgents.type = 'button';
    freeAgents.className = 'chart-chip' + (analyticsManagerState.includeFreeAgents ? ' active' : '');
    freeAgents.style.setProperty('--chip-color','#64748b');
    freeAgents.textContent = 'Free agents';
    freeAgents.title = 'Include free agents in Player Analytics and Player Relationships';
    freeAgents.setAttribute('aria-pressed',String(analyticsManagerState.includeFreeAgents));
    freeAgents.addEventListener('click',toggleAnalyticsFreeAgents);
    container.appendChild(freeAgents);
    const count = document.getElementById("analytics-manager-count");
    if (count) count.textContent = analyticsManagerState.visible.size + " of " + MANAGER_ORDER.length +
        " managers selected" + (analyticsManagerState.includeFreeAgents ? ' · free agents included in player views' : '');
}

function applyAnalyticsManagerFilter() {
    document.querySelectorAll("#page-analytics [data-analytics-manager]").forEach(function(el) {
        const manager = el.getAttribute("data-analytics-manager");
        el.classList.toggle("analytics-manager-hidden", !analyticsManagerState.visible.has(manager));
    });
    applyPlayerAnalyticsFilter();
    refreshMatrixManagerState();
    renderPlayerRelationshipGraph();
    renderTransferRiverPassport();
    if(document.getElementById('analytics-sub-ratings')?.classList.contains('active')) ratingLabRender();
}

function toggleAnalyticsLeagueAverage(enabled) {
    const page=document.getElementById('page-analytics');
    if(page) page.classList.toggle('show-league-average', !!enabled);
}


// v46 — category controls do not replace the existing shared manager chips.
let matrixSelectedGroup='Form & Quality';
function setMatrixGroup(group){
    const page=document.getElementById('analytics-sub-matrices');
    if(!page)return;
    matrixSelectedGroup=group;
    page.querySelectorAll('.matrix-group-chip').forEach(function(btn){
        const active=btn.getAttribute('data-matrix-group-button')===group;
        btn.classList.toggle('active',active);
        btn.setAttribute('aria-pressed',String(active));
    });
    page.querySelectorAll('.matrix-card').forEach(function(card){
        card.hidden=(group!=='All' && card.getAttribute('data-matrix-group')!==group);
    });
}
function refreshMatrixManagerState(){
    const page=document.getElementById('analytics-sub-matrices');
    if(!page)return;
    const selected=analyticsManagerState.visible;
    page.querySelectorAll('.matrix-card').forEach(function(card){
        let available=0, visible=0;
        card.querySelectorAll('.matrix-manager-point').forEach(function(dot){
            available++;
            if(selected.has(dot.getAttribute('data-analytics-manager')))visible++;
        });
        const count=card.querySelector('.matrix-visible-count');
        if(count)count.textContent=visible+' / '+available+' teams';
        const empty=card.querySelector('.matrix-empty');
        if(empty)empty.hidden=visible>0 || available===0;
        card.classList.toggle('matrix-focus-labels',visible>0 && visible<=2);
    });
    const summary=document.getElementById('matrix-manager-summary');
    if(summary)summary.textContent=selected.size+' of '+MANAGER_ORDER.length+' managers selected';
}

const SEASON_TIMELINE_DATA = __SEASON_TIMELINE_DATA__;
function renderSeasonTimeline(index) {
    const data=SEASON_TIMELINE_DATA||[]; if(!data.length)return;
    const i=Math.max(0,Math.min(data.length-1,Number(index)||0)), snap=data[i];
    const label=document.getElementById('season-slider-label'); if(label)label.textContent='GW'+snap.gw;
    const summary=document.getElementById('season-slider-summary');
    if(summary) summary.innerHTML='<div><span>Leader</span><strong>'+snap.leader+'</strong></div><div><span>GW high</span><strong>'+snap.high_score+'</strong></div><div><span>GW average</span><strong>'+Number(snap.average_score).toFixed(1)+'</strong></div>';
    const wrap=document.getElementById('season-slider-table'); if(!wrap)return;
    wrap.innerHTML='<table><thead><tr><th>#</th><th>Manager</th><th>Record</th><th>LP</th><th>PF</th><th>PA</th><th>GW'+snap.gw+'</th></tr></thead><tbody>'+snap.rows.map(r=>'<tr><td>'+r.rank+'</td><td class="manager-name">'+r.manager+'</td><td>'+r.record+'</td><td><strong>'+r.league_points+'</strong></td><td>'+r.pf+'</td><td>'+r.pa+'</td><td>'+r.gw_score+'</td></tr>').join('')+'</tbody></table>';
}

const MANAGER_WAR_ROOM = __MANAGER_WAR_ROOM__;

function initManagerWarRoom(){
  const select=document.getElementById('war-room-manager');
  if(!select)return;
  if(!select.dataset.ready){
    select.innerHTML=MANAGER_ORDER.map(m=>'<option value="'+escapePlayerHTML(m)+'">'+escapePlayerHTML(m)+'</option>').join('');
    const mine=document.getElementById('my-team-selector');
    if(mine && MANAGER_ORDER.includes(mine.options[mine.selectedIndex]?.text)) select.value=mine.options[mine.selectedIndex].text;
    else if(MANAGER_ORDER.includes('Kamararama FC')) select.value='Kamararama FC';
    select.dataset.ready='1';
  }
  renderManagerWarRoom();
}
function warRoomRisk(player){
  const a=Number(player?.availability ?? 1), status=String(player?.status||'a');
  if(status!=='a' || a<0.6) return {label:'High risk',cls:'high'};
  if(a<0.85) return {label:'Monitor',cls:'medium'};
  return {label:'Available',cls:''};
}
function warRoomPlayerCard(player,side){
  const risk=warRoomRisk(player);
  return '<button type="button" class="war-room-player-card" onclick="showWarRoomPlayer('+Number(player.id)+',\''+side+'\')" title="Open '+escapePlayerHTML(player.name)+' details">'+
    '<b>'+escapePlayerHTML(player.name)+'</b><small>'+escapePlayerHTML(player.position||'—')+' · '+escapePlayerHTML(player.club||'—')+'</small><div class="wr-proj">'+Number(player.projection||0).toFixed(1)+' pts</div><span class="wr-risk '+risk.cls+'">'+risk.label+'</span></button>';
}
function warRoomFormation(rows,bench,formation,side,teamName){
  const groups={GKP:[],DEF:[],MID:[],FWD:[]};
  (rows||[]).forEach(p=>{if(groups[p.position])groups[p.position].push(p)});
  const line=pos=>'<div class="war-room-line war-room-line-'+pos.toLowerCase()+'">'+groups[pos].map(p=>warRoomPlayerCard(p,side)).join('')+'</div>';
  const benchHtml=(bench||[]).slice(0,4).map(p=>warRoomPlayerCard(p,side)).join('');
  return '<div class="war-room-team-panel"><h3>'+escapePlayerHTML(teamName)+' · '+escapePlayerHTML(formation||'—')+'</h3><div class="war-room-pitch"><div class="war-room-formation">'+line('FWD')+line('MID')+line('DEF')+line('GKP')+'</div></div><div class="war-room-bench"><h4>Bench</h4><div class="war-room-bench-list">'+(benchHtml||'<div class="muted">No bench available.</div>')+'</div></div></div>';
}
function warRoomFlagRows(rows){
  return (rows||[]).map(p=>'<div class="war-room-flag"><b>'+escapePlayerHTML(p.name)+'</b><small>'+escapePlayerHTML(p.position||'—')+' · '+Math.round(Number(p.availability||0)*100)+'% availability'+(p.news?' · '+escapePlayerHTML(p.news):'')+'</small></div>').join('')||'<div class="notice">No major availability flags in the captured squad.</div>';
}
function showWarRoomPlayer(playerId,side){
  const select=document.getElementById('war-room-manager'),detail=document.getElementById('war-room-player-detail');
  if(!select||!detail)return;
  const data=MANAGER_WAR_ROOM[select.value];if(!data)return;
  const team=side==='opponent'?data.opponent_team:data.you;
  const player=[...(team.starters||[]),...(team.bench||[])].find(p=>Number(p.id)===Number(playerId));
  if(!player)return;
  const risk=warRoomRisk(player),fixtures=(player.fixtures||[]);
  const fixtureHtml=fixtures.length?fixtures.map(f=>'<span class="war-room-player-fixture">'+(f.home?'vs ':'@ ')+escapePlayerHTML(f.opponent||'—')+' · FDR '+escapePlayerHTML(f.difficulty||'—')+'</span>').join(''):'<span class="muted">No PL fixture captured for this gameweek.</span>';
  detail.hidden=false;
  detail.innerHTML='<div class="passport-hero"><div><span class="relationship-eyebrow">PLAYER INTELLIGENCE</span><h3>'+escapePlayerHTML(player.name)+'</h3><p>'+escapePlayerHTML(player.club||'—')+' · '+escapePlayerHTML(player.position||'—')+' · '+escapePlayerHTML(side==='opponent'?data.opponent:select.value)+'</p></div><span class="wr-risk '+risk.cls+'">'+risk.label+'</span></div>'+
    '<div class="war-room-player-detail-grid"><div><strong>'+Number(player.projection||0).toFixed(1)+'</strong><small>Projected points</small></div><div><strong>'+Math.round(Number(player.availability||0)*100)+'%</strong><small>Availability</small></div><div><strong>'+Number(player.importance||0).toFixed(0)+'/100</strong><small>Importance · '+escapePlayerHTML(player.importance_label||'—')+'</small></div><div><strong>'+Number(player.replacement_gap||0).toFixed(1)+'</strong><small>Replacement gap</small></div><div><strong>'+fixtures.length+'</strong><small>PL fixture'+(fixtures.length===1?'':'s')+'</small></div></div>'+
    '<div class="passport-section"><h4>Who are they playing?</h4><div class="war-room-player-fixtures">'+fixtureHtml+'</div></div>'+
    (player.news?'<div class="war-room-player-news"><b>FPL availability news</b><br>'+escapePlayerHTML(player.news)+'</div>':'<div class="war-room-player-news"><b>Availability</b><br>No current FPL injury/suspension news captured.</div>');
  detail.scrollIntoView({behavior:'smooth',block:'nearest'});
}
function initManagerWarRoom(){
  const select=document.getElementById('war-room-manager');
  if(!select)return;
  if(!select.options.length){
    select.innerHTML=MANAGER_ORDER.map(m=>'<option value="'+escapePlayerHTML(m)+'">'+escapePlayerHTML(m)+'</option>').join('');
    const preferred=(typeof MY_TEAM_DEFAULT_MANAGER!=='undefined'&&MY_TEAM_DEFAULT_MANAGER)||MANAGER_ORDER[0];
    if(MANAGER_WAR_ROOM[preferred])select.value=preferred;
  }
  renderManagerWarRoom();
}
function renderManagerWarRoom(){
  const select=document.getElementById('war-room-manager'),wrap=document.getElementById('war-room-content');
  if(!select||!wrap)return;
  const manager=select.value||MANAGER_ORDER[0],data=MANAGER_WAR_ROOM[manager];
  if(!data||data.warning){wrap.innerHTML='<div class="card"><div class="notice">'+escapePlayerHTML(data?.warning||'No War Room data available.')+'</div></div>';return;}
  const opp=data.opponent,odds=data.odds;
  const probs=odds?'<div class="war-room-prob"><div><strong>'+Number(odds.you_win).toFixed(1)+'%</strong><small>'+escapePlayerHTML(manager)+' win</small></div><div><strong>'+Number(odds.draw).toFixed(1)+'%</strong><small>Draw</small></div><div><strong>'+Number(odds.opponent_win).toFixed(1)+'%</strong><small>'+escapePlayerHTML(opp)+' win</small></div></div><p class="card-description">Modelled score range: '+Number(odds.you_low).toFixed(0)+'–'+Number(odds.you_high).toFixed(0)+' vs '+Number(odds.opponent_low).toFixed(0)+'–'+Number(odds.opponent_high).toFixed(0)+' · confidence '+escapePlayerHTML(odds.confidence||'—')+'.</p>':'<p class="card-description">Pre-game fixture probabilities are only shown when this is the dashboard’s next unplayed prediction gameweek.</p>';
  const pos=(data.positional||[]).map(r=>{const e=Number(r.edge||0);return '<div class="war-room-pos"><b>'+escapePlayerHTML(r.position)+'</b><div class="edge '+(e>0?'positive':e<0?'negative':'')+'">'+(e>0?'+':'')+e.toFixed(1)+'</div><small>'+Number(r.you||0).toFixed(1)+' vs '+Number(r.opponent||0).toFixed(1)+' projected</small></div>'}).join('');
  const upgrades=(data.upgrades||[]).map(r=>'<div class="war-room-upgrade"><div><b>'+escapePlayerHTML(r.in_name)+' in · '+escapePlayerHTML(r.out_name)+' out</b><small>'+escapePlayerHTML(r.position)+' · '+Number(r.incoming_projection||0).toFixed(1)+' vs '+Number(r.outgoing_projection||0).toFixed(1)+' individual projection</small></div><strong>+'+Number(r.gain||0).toFixed(1)+'</strong></div>').join('')||'<div class="notice">No free-agent move improves the projected optimal XI by more than 0.1 points right now.</div>';
  wrap.innerHTML='<div class="war-room-grid">'+
    '<div class="war-room-card full"><div class="war-room-matchup"><div class="war-room-side"><h3>'+escapePlayerHTML(manager)+'</h3><strong>'+Number(data.you.xi||0).toFixed(1)+'</strong><small>projected XI · '+escapePlayerHTML(data.you.formation||'—')+'</small></div><div class="war-room-vs">GW'+data.gw+'<br>VS</div><div class="war-room-side"><h3>'+escapePlayerHTML(opp)+'</h3><strong>'+Number(data.opponent_team.xi||0).toFixed(1)+'</strong><small>projected XI · '+escapePlayerHTML(data.opponent_team.formation||'—')+'</small></div></div>'+probs+'</div>'+
    '<div class="war-room-card full"><h2>Projected Matchup</h2><p class="card-description">Both optimal projected XIs in formation. Click any player card for opponent, availability risk, projected points and importance to their team.</p><div class="war-room-pitch-wrap">'+warRoomFormation(data.you.starters,data.you.bench,data.you.formation,'you',manager)+warRoomFormation(data.opponent_team.starters,data.opponent_team.bench,data.opponent_team.formation,'opponent',opp)+'</div><div id="war-room-player-detail" class="war-room-player-detail" hidden></div></div>'+
    '<div class="war-room-card full"><h2>Positional Battle</h2><p class="card-description">Projected starting-XI contribution by position. Positive edge means your side projects higher.</p><div class="war-room-pos-grid">'+pos+'</div></div>'+
    '<div class="war-room-card"><h2>Matchup Keys</h2><ul class="war-room-keys">'+(data.keys||[]).map(k=>'<li>'+escapePlayerHTML(k)+'</li>').join('')+'</ul></div>'+
    '<div class="war-room-card"><h2>Availability Watch</h2><h3>'+escapePlayerHTML(manager)+'</h3><div class="war-room-flags">'+warRoomFlagRows(data.you.flags)+'</div><h3>'+escapePlayerHTML(opp)+'</h3><div class="war-room-flags">'+warRoomFlagRows(data.opponent_team.flags)+'</div></div>'+
    '<div class="war-room-card full"><h2>Best Next-GW Waiver Improvements</h2><p class="card-description">Like-for-like free agents ranked by improvement to your optimal projected XI for GW'+data.gw+' only. This does not account for waiver priority or moves made after the dashboard refresh.</p><div class="war-room-upgrades">'+upgrades+'</div></div>'+
    '</div>';
}

function showOverviewSubtab(name, button) {
    document.querySelectorAll('.overview-subpage').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.overview-tab').forEach(el => { el.classList.remove('active'); el.setAttribute('aria-selected','false'); });
    const target = document.getElementById('overview-sub-' + name);
    if (target) target.classList.add('active');
    if (button) { button.classList.add('active'); button.setAttribute('aria-selected','true'); }
    // Charts are initially inside a hidden subpage. Draw them after the tab
    // becomes visible so responsive width measurement is accurate on mobile.
    if (name === 'intelligence') {
        requestAnimationFrame(() => {
            if (typeof trendState !== 'undefined' && typeof renderTrendChart === 'function') {
                ['h2h','rank','cumulative','scores'].forEach(key => {
                    if (trendState[key]) renderTrendChart(key);
                });
            }
        });
    }
}

const INJURY_LIST = __INJURY_LIST__;
const FPL_AVAILABILITY_LABELS = {i:'Injured', s:'Suspended', d:'Doubtful', u:'Unavailable', n:'Not eligible', a:'Available / news'};
function availabilityBadge(row){
  const status = row.status || row.availability?.status || 'a';
  const chance = row.chance_next !== undefined ? row.chance_next : row.availability?.chance_next;
  const badge = '<span class="badge" style="background:'+(status==='a'?'#1d5c48':status==='d'?'#845c18':'#813c3c')+';color:var(--text)">'+escapePlayerHTML(FPL_AVAILABILITY_LABELS[status]||'Flagged')+'</span>';
  return badge+(chance!==null && chance!==undefined ? ' <span class="badge">FPL next GW: '+Number(chance)+'%</span>' : ' <span class="badge">No official probability</span>');
}
function renderInjuryList(){
  const wrap=document.getElementById('injury-list-results');if(!wrap)return;
  const search=(document.getElementById('injury-search')?.value||'').trim().toLowerCase();
  const status=document.getElementById('injury-status-filter')?.value||'';
  const owner=document.getElementById('injury-ownership-filter')?.value||'';
  let rows=INJURY_LIST.filter(p=>(!search||(p.name+' '+p.team+' '+p.fantasy_team).toLowerCase().includes(search)) && (!status||p.status===status) && (!owner||(owner==='Owned'?p.fantasy_team!=='Free Agent':p.fantasy_team==='Free Agent')));
  const priority={s:0,i:1,u:2,n:3,d:4,a:5};
  rows.sort((a,b)=>(priority[a.status]??6)-(priority[b.status]??6)||Number(a.availability_next)-Number(b.availability_next)||String(a.name).localeCompare(String(b.name)));
  document.getElementById('injury-count').textContent=rows.length+' flagged players';
  wrap.innerHTML=rows.length?'<div class="injury-list-grid">'+rows.map(p=>'<div class="injury-medical-card"><div class="injury-head"><div><strong>'+escapePlayerHTML(p.name)+'</strong><small>'+escapePlayerHTML(p.position+' · '+p.team+' · '+p.fantasy_team)+'</small></div>'+availabilityBadge(p)+'</div><p>'+escapePlayerHTML(p.news||'No further details provided by FPL.')+'</p>'+fixtureRunHTML(p.next_fixtures,true)+'<div class="injury-actions"><span>'+Number(p.projected_remaining_points||0).toFixed(1)+' remaining projected pts (availability-adjusted)</span><button type="button" class="results-button" onclick="openScoutFreeAgent('+Number(p.id)+')">Player details →</button></div></div>').join('')+'</div>':'<div class="notice">No players match those filters.</div>';
}
function renderMyTeamMedical(){
 const wrap=document.getElementById('myteam-medical-results');if(!wrap)return;
 const manager=currentMyTeamManager();const rows=INJURY_LIST.filter(p=>p.fantasy_team===manager);
 if(!rows.length){wrap.innerHTML='<div class="notice">No official FPL injury or suspension flags for this squad at the last refresh.</div>';return;}
 wrap.innerHTML='<div class="injury-list-grid">'+rows.map(p=>'<div class="injury-medical-card"><div class="injury-head"><div><strong>'+escapePlayerHTML(p.name)+'</strong><small>'+escapePlayerHTML(p.position+' · '+p.team)+'</small></div>'+availabilityBadge(p)+'</div><p>'+escapePlayerHTML(p.news||'No further details provided by FPL.')+'</p>'+fixtureRunHTML(p.next_fixtures,true)+'<div class="injury-actions"><span>Estimated availability next GW: '+Math.round(Number(p.availability_next||0)*100)+'%</span><button type="button" class="results-button" onclick="openPlannerFromMedical()">Check planner →</button></div></div>').join('')+'</div>';
}

function openPlannerFromMedical(){
    const btn=Array.from(document.querySelectorAll('.myteam-tab')).find(el=>(el.textContent||'').trim()==='Five-GW Planner');
    showMyTeamSubtab('planner',btn||null);
}

function showPlayerSubtab(name, button) {
    document.querySelectorAll('.player-subpage').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.player-page-tab').forEach(el => el.classList.remove('active'));
    const target=document.getElementById('player-sub-'+name); if(target) target.classList.add('active');
    if(button) button.classList.add('active');
    if(name==='directory' && typeof filterPlayers==='function') requestAnimationFrame(filterPlayers);
    if(name==='injuries') requestAnimationFrame(renderInjuryList);
    if(name==='availability') requestAnimationFrame(healthAnalyticsRender);
}

function showMyTeamSubtab(name, button) {
    document.querySelectorAll('.myteam-subpage').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.myteam-tab').forEach(el => el.classList.remove('active'));
    const target=document.getElementById('myteam-sub-'+name); if(target) target.classList.add('active');
    if(button) button.classList.add('active');
    if(name==='planner' && typeof renderFiveGWPlanner==='function') requestAnimationFrame(renderFiveGWPlanner);
    if(name==='medical') requestAnimationFrame(renderMyTeamMedical);
    if(name==='scout' && typeof renderPlayerScout==='function') requestAnimationFrame(renderPlayerScout);
    if(name==='stats' && typeof renderMyTeamStatsCharts==='function') requestAnimationFrame(renderMyTeamStatsCharts);
    if(name==='targets') requestAnimationFrame(()=>{
        if(typeof renderMyTeamPositionNeeds==='function') renderMyTeamPositionNeeds();
        if(typeof renderMyTeamFreeAgents==='function') renderMyTeamFreeAgents();
        if(typeof renderMyTeamTradeTargets==='function') renderMyTeamTradeTargets();
        if(typeof renderMyTeamSellHigh==='function') renderMyTeamSellHigh();
    });
}


function showSeasonSummarySubtab(name, button){
    document.querySelectorAll('.season-summary-subpage').forEach(p=>p.classList.remove('active'));
    document.querySelectorAll('.season-summary-tab').forEach(t=>{t.classList.remove('active');t.setAttribute('aria-selected','false');});
    const panel=document.getElementById('season-summary-sub-'+name);
    if(panel)panel.classList.add('active');
    if(button){button.classList.add('active');button.setAttribute('aria-selected','true');}
    if(name==='evolution' && (SEASON_TIMELINE_DATA||[]).length) requestAnimationFrame(()=>{
        const slider=document.getElementById('season-gw-slider');
        renderSeasonTimeline(slider?slider.value:SEASON_TIMELINE_DATA.length-1);
    });
}

function showClubSubtab(name, button){
    document.querySelectorAll('.club-explorer-panel').forEach(p=>p.classList.remove('active'));
    document.querySelectorAll('.club-explorer-tab').forEach(t=>t.classList.remove('active'));
    const panel=document.getElementById('club-sub-'+name);
    if(panel)panel.classList.add('active');
    if(button)button.classList.add('active');
}

function showDraftCentreSubtab(name, button) {
    document.querySelectorAll('.draft-centre-subpage').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.draft-centre-tab').forEach(el => el.classList.remove('active'));
    const target=document.getElementById('draft-centre-sub-'+name); if(target) target.classList.add('active');
    if(button) button.classList.add('active');
}

/* v48 — Player Relationship Graph. 100% self-contained SVG; no CDN dependency. */
const PLAYER_RELATIONSHIPS = __PLAYER_RELATIONSHIPS__;
const relationshipNodeById = new Map((PLAYER_RELATIONSHIPS.nodes || []).map(n => [n.id,n]));
const relationshipState = {mode:'current', owner:'all', focus:null, minWeeks:1, allLinks:false,
    zoom:1, viewX:0, viewY:0, positions:new Map(), latestEdges:[]};
const relationshipSVG_NS='http://www.w3.org/2000/svg';
function relationshipEscape(str){return String(str??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
function relationshipColour(owner){return owner==='Free Agent'?'#64748b':(MANAGER_COLORS[owner] || '#94a3b8');}
function initPlayerRelationships(){
    const panel=document.getElementById('analytics-sub-relationships');
    if(!panel)return;
    const picker=document.getElementById('relationship-owner');
    if(picker){
        const prev=picker.value;
        picker.querySelectorAll('option:not([value="all"])').forEach(o=>o.remove());
        MANAGER_ORDER.forEach(manager=>{
            const option=document.createElement('option');option.value=manager;option.textContent=manager;picker.appendChild(option);
        });
        relationshipState.owner=MANAGER_ORDER.includes('Kamararama FC')?'Kamararama FC':'all';
        if(prev&&prev!=='all'&&MANAGER_ORDER.includes(prev))relationshipState.owner=prev;
        picker.value=relationshipState.owner;
    }
    const choices=document.getElementById('relationship-players');
    if(choices){
        choices.replaceChildren();
        (PLAYER_RELATIONSHIPS.nodes||[]).slice().sort((a,b)=>a.name.localeCompare(b.name)).forEach(node=>{
            const o=document.createElement('option');o.value=relationshipPlayerLabel(node);choices.appendChild(o);
        });
    }
    // Rendering only after the tab becomes visible avoids a zero-width SVG.
}
function relationshipPlayerLabel(node){return node.name+' — '+node.owner+' [Draft #'+node.id+']';}
function setRelationshipMode(mode){
    if(!['current','history','trades','all'].includes(mode))return;
    relationshipState.mode=mode;
    document.querySelectorAll('[data-rel-mode]').forEach(b=>b.classList.toggle('active',b.dataset.relMode===mode));
    renderPlayerRelationshipGraph();
}
function setRelationshipOwner(owner){relationshipState.owner=owner;relationshipState.focus=null;
    const search=document.getElementById('relationship-search');if(search)search.value='';
    renderPlayerRelationshipGraph();}
function setRelationshipWeeks(raw){relationshipState.minWeeks=Math.max(1,Number(raw)||1);renderPlayerRelationshipGraph();}
function setRelationshipAllLinks(checked){relationshipState.allLinks=!!checked;renderPlayerRelationshipGraph();}
function focusRelationshipSearch(){
    const input=document.getElementById('relationship-search');if(!input)return;
    const value=input.value.trim().toLowerCase();if(!value){resetRelationshipFocus();return;}
    const nodes=PLAYER_RELATIONSHIPS.nodes||[];
    // Match the complete datalist value first: duplicate surnames remain safe.
    let found=nodes.find(n=>relationshipPlayerLabel(n).toLowerCase()===value);
    if(!found){const hits=nodes.filter(n=>n.name.toLowerCase()===value);if(hits.length===1)found=hits[0];}
    if(!found){const hits=nodes.filter(n=>n.name.toLowerCase().includes(value));if(hits.length===1)found=hits[0];}
    if(!found){const el=document.getElementById('relationship-empty');if(el){el.hidden=false;el.textContent='Choose a player from the suggestions. Multiple players may share the same surname.';}return;}
    focusRelationshipPlayer(found.id);
}
function focusRelationshipPlayer(pid){
    pid=Number(pid);if(!relationshipNodeById.has(pid))return;
    relationshipState.focus=pid;relationshipState.owner='all';
    const picker=document.getElementById('relationship-owner');if(picker)picker.value='all';
    const search=document.getElementById('relationship-search');if(search)search.value=relationshipPlayerLabel(relationshipNodeById.get(pid));
    renderPlayerRelationshipGraph();
}
function resetRelationshipFocus(){relationshipState.focus=null;
    const search=document.getElementById('relationship-search');if(search)search.value='';
    renderPlayerRelationshipGraph();}
function relationshipEdgeMatches(e,mode){
    if(mode==='current')return e.current;
    if(mode==='history')return e.shared_gws>=relationshipState.minWeeks;
    if(mode==='trades')return e.trade_count>0;
    return e.current||e.shared_gws>=relationshipState.minWeeks||e.trade_count>0;
}
function relationshipEdgeWeight(e){return (e.trade_count||0)*8+(e.current?7:0)+Math.min(e.shared_gws||0,12);}
function relationshipEdgeKind(e){
    if(relationshipState.mode==='trades'||(relationshipState.mode==='all'&&e.trade_count))return 'trade';
    if(relationshipState.mode==='history'||(relationshipState.mode==='all'&&!e.current))return 'history';
    return 'current';
}
function relationshipVisibleOwners(){return analyticsManagerState.visible;}
function relationshipAssemble(){
    const allowed=relationshipVisibleOwners();
    const ownerChoice=relationshipState.owner;
    const eligible=new Map((PLAYER_RELATIONSHIPS.nodes||[]).filter(n=>
        (n.owner==='Free Agent'?analyticsManagerState.includeFreeAgents:allowed.has(n.owner))&&
        (ownerChoice==='all'||n.owner===ownerChoice)).map(n=>[n.id,n]));
    if(relationshipState.focus!==null){
        // Search can select a player hidden by the global filter. Don't leak
        // that owner's data into a filtered view: show a clear empty message.
        const focus=eligible.get(relationshipState.focus);
        if(!focus)return {nodes:[],edges:[],message:'This player is hidden by the shared Analytics manager filter. Select their current owner above (or enable Free agents).'};
        const adjacent=(PLAYER_RELATIONSHIPS.edges||[]).filter(e=>relationshipEdgeMatches(e,relationshipState.mode)&&
            (e.a===focus.id||e.b===focus.id)&&eligible.has(e.a)&&eligible.has(e.b))
            .sort((a,b)=>relationshipEdgeWeight(b)-relationshipEdgeWeight(a));
        const maxNeighbours=relationshipState.allLinks?64:35;
        const selected=new Set([focus.id]);
        for(const edge of adjacent){if(selected.size>maxNeighbours)break;selected.add(edge.a);selected.add(edge.b);}
        const full=(PLAYER_RELATIONSHIPS.edges||[]).filter(e=>selected.has(e.a)&&selected.has(e.b)&&relationshipEdgeMatches(e,relationshipState.mode));
        const limit=relationshipState.allLinks?700:Math.min(110,Math.max(40,selected.size*3));
        const edges=full.sort((a,b)=>relationshipEdgeWeight(b)-relationshipEdgeWeight(a)).slice(0,limit);
        return {nodes:[...selected].map(id=>eligible.get(id)).filter(Boolean),edges,message:adjacent.length?'':'No connections of this type for this player within the current manager filter.'};
    }
    const byOwner=new Map();
    for(const n of eligible.values()){
        if(!byOwner.has(n.owner))byOwner.set(n.owner,[]);
        byOwner.get(n.owner).push(n);
    }
    const allOwners=ownerChoice==='all';
    const selected=new Map();
    for(const [owner,rows] of byOwner){
        rows.sort((a,b)=>b.points-a.points||a.name.localeCompare(b.name));
        const limit=allOwners?(owner==='Free Agent'?5:6):40;
        rows.slice(0,limit).forEach(n=>selected.set(n.id,n));
    }
    // In trade mode, substitute players with actual links so the overview
    // doesn't become empty just because the highest scorers weren't traded.
    if(relationshipState.mode==='trades'&&selected.size){
        selected.clear();
        const scores=new Map();
        for(const e of PLAYER_RELATIONSHIPS.edges||[]){
            if(!e.trade_count||!eligible.has(e.a)||!eligible.has(e.b))continue;
            scores.set(e.a,(scores.get(e.a)||0)+e.trade_count);
            scores.set(e.b,(scores.get(e.b)||0)+e.trade_count);
        }
        const ids=[...scores].sort((a,b)=>b[1]-a[1]).slice(0,65);
        ids.forEach(([id])=>selected.set(id,eligible.get(id)));
    }
    const candidate=(PLAYER_RELATIONSHIPS.edges||[]).filter(e=>selected.has(e.a)&&selected.has(e.b)&&relationshipEdgeMatches(e,relationshipState.mode))
      .sort((a,b)=>relationshipEdgeWeight(b)-relationshipEdgeWeight(a));
    // For current teammates a full clique drowns out the players. Strongest
    // links make a readable skeleton, with an explicit all-links toggle.
    const maxEdges=relationshipState.allLinks?800:Math.min(150,Math.max(30,selected.size*2));
    const edges=candidate.slice(0,maxEdges);
    return {nodes:[...selected.values()],edges,message:selected.size?'':'No players match the shared manager filters.'};
}
function relationshipLayout(nodes,focus){
    const pos=new Map();
    const sorted=nodes.slice().sort((a,b)=>a.owner.localeCompare(b.owner)||b.points-a.points||a.name.localeCompare(b.name));
    if(focus!==null&&sorted.some(n=>n.id===focus)){
        pos.set(focus,{x:480,y:292});
        const rest=sorted.filter(n=>n.id!==focus);
        rest.forEach((n,i)=>{
            const ownerAngle=(Math.abs([...n.owner].reduce((v,ch)=>v*31+ch.charCodeAt(0),0))%360)*Math.PI/180;
            const angle=2*Math.PI*(i+.37)/Math.max(rest.length,1)+(ownerAngle*.10);
            const ring=rest.length>17?(i<17?165:242):Math.min(215,110+rest.length*4);
            pos.set(n.id,{x:480+Math.cos(angle)*ring,y:292+Math.sin(angle)*ring*.89});
        });
        return pos;
    }
    const groups=new Map();
    sorted.forEach(n=>{if(!groups.has(n.owner))groups.set(n.owner,[]);groups.get(n.owner).push(n);});
    const owners=[...groups.keys()];
    if(owners.length===1){
        const group=groups.get(owners[0]);
        group.forEach((n,i)=>{const angle=2*Math.PI*i/group.length-Math.PI/2;
            const ring=group.length<=7?145:group.length<=17?205:230;
            pos.set(n.id,{x:480+Math.cos(angle)*ring,y:292+Math.sin(angle)*ring*.90});});
        return pos;
    }
    owners.forEach((owner,g)=>{
        const cols=owners.length<=4?2:owners.length<=9?3:4;
        const rows=Math.ceil(owners.length/cols);
        const cx=(g%cols+.5)*960/cols,cy=(Math.floor(g/cols)+.5)*590/rows;
        const players=groups.get(owner);
        const radius=Math.min(77,cols<=2?94:75);
        players.forEach((n,i)=>{
            const angle=2*Math.PI*i/players.length-Math.PI/2;
            pos.set(n.id,{x:cx+Math.cos(angle)*radius,y:cy+Math.sin(angle)*radius});
        });
    });
    return pos;
}
function relationshipSvgElement(tag,attrs){const el=document.createElementNS(relationshipSVG_NS,tag);
    Object.entries(attrs||{}).forEach(([k,v])=>el.setAttribute(k,String(v)));return el;}
function relationshipApplyView(){const svg=document.getElementById('relationship-svg');if(!svg)return;
    const w=960*relationshipState.zoom,h=590*relationshipState.zoom;
    svg.setAttribute('viewBox',[relationshipState.viewX+(960-w)/2,relationshipState.viewY+(590-h)/2,w,h].join(' '));}
function zoomRelationship(factor,reset){if(reset){relationshipState.zoom=1;relationshipState.viewX=0;relationshipState.viewY=0;}
    else relationshipState.zoom=Math.max(.5,Math.min(3.5,relationshipState.zoom*factor));relationshipApplyView();}
function renderRelationshipDetail(focus,visibleEdges){
    const target=document.getElementById('relationship-detail');if(!target)return;
    if(!focus){target.innerHTML='<h3>Explore the network</h3><p>Click any player to centre their squadmate and trade network. Use the mode buttons to switch the relationship you’re investigating.</p>';return;}
    const owner=focus.owner;
    const connected=visibleEdges.filter(e=>e.a===focus.id||e.b===focus.id).sort((a,b)=>relationshipEdgeWeight(b)-relationshipEdgeWeight(a));
    const links=connected.slice(0,14).map(e=>{
        const other=relationshipNodeById.get(e.a===focus.id?e.b:e.a);if(!other)return '';
        const descriptions=[];
        if(e.current)descriptions.push('Current squadmates');
        if(e.shared_gws)descriptions.push(e.shared_gws+' shared completed GW'+(e.shared_gws===1?'':'s'));
        if(e.trade_count)descriptions.push(e.trade_count+' processed trade'+(e.trade_count===1?'':'s'));
        return '<button type="button" class="relationship-neighbour" data-rel-focus="'+other.id+'"><span class="relationship-avatar" style="background:'+relationshipColour(other.owner)+'"></span><span><b>'+relationshipEscape(other.name)+'</b><small>'+relationshipEscape(descriptions.join(' · '))+'</small></span><span class="relationship-arrow">↗</span></button>';
    }).join('');
    const trades=(PLAYER_RELATIONSHIPS.trades[String(focus.id)]||[]).slice().sort((a,b)=>(Number(b.gw)||0)-(Number(a.gw)||0));
    const tradeList=trades.slice(0,6).map(t=>{
        const offered=(t.offered_ids||[]).map(id=>relationshipNodeById.get(id)?.name||'#'+id).join(', ');
        const received=(t.received_ids||[]).map(id=>relationshipNodeById.get(id)?.name||'#'+id).join(', ');
        return '<li><b>GW'+relationshipEscape(t.gw)+'</b> · '+relationshipEscape(t.offered_by||'Unknown')+' sent '+relationshipEscape(offered)+' ↔ '+relationshipEscape(t.received_by||'Unknown')+' sent '+relationshipEscape(received)+'</li>';
    }).join('');
    target.innerHTML='<div class="relationship-detail-owner"><span class="relationship-avatar" style="background:'+relationshipColour(owner)+'"></span>'+relationshipEscape(owner)+'</div>'+ 
        '<h3>'+relationshipEscape(focus.name)+'</h3><p>'+relationshipEscape(focus.club)+' · '+relationshipEscape(focus.position)+'</p>'+ 
        '<div class="relationship-detail-metrics"><div><strong>'+focus.points+'</strong><small>Season points</small></div><div><strong>'+(focus.draft_pick?'#'+focus.draft_pick:'—')+'</strong><small>Original pick</small></div><div><strong>'+connected.length+'</strong><small>Shown links</small></div></div>'+ 
        '<h4>Closest connections</h4>'+(links||'<p class="muted">No links of this type in the current filter.</p>')+
        (trades.length?'<h4>Processed trade history</h4><ul class="relationship-trade-list">'+tradeList+'</ul>':'');
    target.querySelectorAll('[data-rel-focus]').forEach(btn=>btn.addEventListener('click',()=>focusRelationshipPlayer(Number(btn.dataset.relFocus))));
}
function renderPlayerRelationshipGraph(){
    const page=document.getElementById('analytics-sub-relationships');if(!page||!page.classList.contains('active'))return;
    const svg=document.getElementById('relationship-svg'),empty=document.getElementById('relationship-empty');if(!svg)return;
    const assembled=relationshipAssemble();const nodes=assembled.nodes,links=assembled.edges;
    const selected=relationshipState.focus!==null?relationshipNodeById.get(relationshipState.focus):null;
    const positions=relationshipLayout(nodes,selected?.id??null);
    relationshipState.positions=positions;relationshipState.latestEdges=links;
    const label={current:'Current squadmates',history:'Shared squad history',trades:'Processed trade exchanges',all:'All relationships'}[relationshipState.mode];
    const caption=document.getElementById('relationship-caption');if(caption)caption.textContent=selected?selected.name+' · '+label:label+' · '+(relationshipState.owner==='all'?'Selected McDraft teams':relationshipState.owner);
    const stats=document.getElementById('relationship-stats');
    if(stats)stats.innerHTML='<div><strong>'+nodes.length+'</strong><span>Players shown</span></div><div><strong>'+links.length+'</strong><span>Links shown</span></div><div><strong>'+PLAYER_RELATIONSHIPS.summary.traded+'</strong><span>League-wide traded pairs</span></div><div><strong>'+PLAYER_RELATIONSHIPS.summary.historical+'</strong><span>Pairs sharing a completed GW</span></div>';
    const foot=document.getElementById('relationship-footnote');if(foot)foot.textContent=(relationshipState.allLinks?'All eligible links are shown up to the display safety cap. ':'Strongest links shown for clarity; enable Show all links to reveal more. ')+
        (relationshipState.owner==='all'&&!selected?'Overview limits each manager to six leading players. Select one owner or focus a player to see more. ':'')+
        'Historical links use completed-GW roster snapshots only. Trade links use processed trades only.';
    svg.replaceChildren();svg.appendChild(relationshipSvgElement('title',{})).textContent='McDraft player relationship network';
    if(empty){empty.hidden=!!nodes.length&&(!assembled.message||!!links.length);empty.textContent=assembled.message||'';}
    if(!nodes.length){renderRelationshipDetail(selected,[]);return;}
    const lineLayer=relationshipSvgElement('g',{'class':'relationship-link-layer'}),nodeLayer=relationshipSvgElement('g',{'class':'relationship-node-layer'});
    const refs=[];links.forEach(e=>{
        const a=positions.get(e.a),b=positions.get(e.b);if(!a||!b)return;
        const kind=relationshipEdgeKind(e);
        const line=relationshipSvgElement('line',{x1:a.x,y1:a.y,x2:b.x,y2:b.y,'class':'relationship-link relationship-link-'+kind,
             'stroke-width':Math.min(4,1.0+Math.log2(1+Math.max(e.trade_count,e.shared_gws,1))*.65)});
        const tip=relationshipSvgElement('title');tip.textContent=[e.current?'Current: '+e.current_team:'',e.shared_gws?e.shared_gws+' shared GW(s) with '+(e.shared_teams||[]).join(', '):'',e.trade_count?e.trade_count+' processed trade exchange(s)'+(e.trade_gws?.length?' in GW'+e.trade_gws.join(', GW'):''):''].filter(Boolean).join(' · ');
        line.appendChild(tip);lineLayer.appendChild(line);refs.push({e,line});
    });
    nodes.forEach(n=>{
        const p=positions.get(n.id);if(!p)return;
        const g=relationshipSvgElement('g',{'class':'relationship-node'+(selected?.id===n.id?' focused':''),transform:'translate('+p.x+','+p.y+')',tabindex:0,role:'button','aria-label':n.name+', '+n.owner+', click to focus'});
        const circle=relationshipSvgElement('circle',{r:selected?.id===n.id?19:12,fill:relationshipColour(n.owner)});
        g.appendChild(circle);
        const text=relationshipSvgElement('text',{x:0,y:selected?.id===n.id?33:25,'text-anchor':'middle'});
        text.textContent=n.name.length>19?n.name.slice(0,18)+'…':n.name;g.appendChild(text);
        const title=relationshipSvgElement('title');title.textContent=n.name+' · '+n.owner+' · '+n.club+' · '+n.points+' pts';g.appendChild(title);
        g.addEventListener('click',ev=>{ev.stopPropagation();if(!g.dataset.dragged)focusRelationshipPlayer(n.id);else delete g.dataset.dragged;});
        g.addEventListener('keydown',ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();focusRelationshipPlayer(n.id);}});
        let start=null;
        g.addEventListener('pointerdown',ev=>{if(ev.button!==0)return;start={x:ev.clientX,y:ev.clientY,ox:p.x,oy:p.y};g.setPointerCapture(ev.pointerId);});
        g.addEventListener('pointermove',ev=>{if(!start)return;
            const rect=svg.getBoundingClientRect();const dx=(ev.clientX-start.x)*960*relationshipState.zoom/Math.max(1,rect.width),dy=(ev.clientY-start.y)*590*relationshipState.zoom/Math.max(1,rect.height);
            if(Math.abs(ev.clientX-start.x)+Math.abs(ev.clientY-start.y)>5)g.dataset.dragged='1';
            p.x=start.ox+dx;p.y=start.oy+dy;g.setAttribute('transform','translate('+p.x+','+p.y+')');
            refs.forEach(({e,line})=>{if(e.a===n.id){line.setAttribute('x1',p.x);line.setAttribute('y1',p.y);}if(e.b===n.id){line.setAttribute('x2',p.x);line.setAttribute('y2',p.y);}});
        });
        g.addEventListener('pointerup',()=>{start=null;});g.addEventListener('pointercancel',()=>{start=null;});
        nodeLayer.appendChild(g);
    });
    svg.appendChild(lineLayer);svg.appendChild(nodeLayer);relationshipApplyView();
    renderRelationshipDetail(selected,links);
}

const TRANSFER_RIVER_PASSPORT = __TRANSFER_RIVER_PASSPORT__;
const passportState = { focusPlayer: null };

function passportEscape(value){
    return String(value ?? '')
      .replace(/&/g,'&amp;')
      .replace(/</g,'&lt;')
      .replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;')
      .replace(/'/g,'&#39;');
}
function riverNodeColor(name){
    if(name==='Draft Night') return '#94a3b8';
    if(name==='Free Agent') return '#64748b';
    return MANAGER_COLORS[name] || '#38bdf8';
}
function initTransferRiverPassport(){
    const list = document.getElementById('passport-player-list');
    if(list && !list.dataset.ready){
        list.innerHTML = (TRANSFER_RIVER_PASSPORT.players||[])
          .slice().sort((a,b)=>String(a.name).localeCompare(String(b.name)))
          .map(p=>'<option value="'+passportEscape(p.name)+'"></option>').join('');
        list.dataset.ready='1';
    }
    renderTransferRiverPassport();
}
function focusPassportSearch(){
    const input = document.getElementById('passport-player-search');
    const query = input ? input.value.trim().toLowerCase() : '';
    if(!query){ renderTransferRiverPassport(); return; }
    const match = (TRANSFER_RIVER_PASSPORT.players||[]).find(p=>String(p.name).toLowerCase()===query)
      || (TRANSFER_RIVER_PASSPORT.players||[]).find(p=>String(p.name).toLowerCase().includes(query));
    if(match){ passportState.focusPlayer = Number(match.id); if(input) input.value = match.name; }
    renderTransferRiverPassport();
}
function clearPassportPlayer(){
    passportState.focusPlayer = null;
    const input = document.getElementById('passport-player-search');
    if(input) input.value = '';
    renderTransferRiverPassport();
}
function renderTransferRiverPassport(){
    const page = document.getElementById('analytics-sub-river-passport');
    if(!page || !page.classList.contains('active')) return;
    const chart = document.getElementById('transfer-river-chart');
    const empty = document.getElementById('transfer-river-empty');
    const caption = document.getElementById('transfer-river-caption');
    const subcaption = document.getElementById('transfer-river-subcaption');
    const stats = document.getElementById('transfer-river-stats');
    if(!chart) return;

    const selectedManagers = MANAGER_ORDER.filter(m=>analyticsManagerState.visible.has(m));
    const includeFree = analyticsManagerState.includeFreeAgents;
    let labels = [];
    let linkRows = [];

    if(passportState.focusPlayer !== null){
        const player = TRANSFER_RIVER_PASSPORT.passports[String(passportState.focusPlayer)];
        const journey = (TRANSFER_RIVER_PASSPORT.journeys[String(passportState.focusPlayer)]||[]).slice();
        const seen = new Set();
        journey.forEach(step=>{ seen.add(step.source); seen.add(step.target); });
        labels = Array.from(seen);
        linkRows = journey.map(step=>({source:step.source,target:step.target,value:1,color:'#f59e0b',hover:step.label}));
        if(caption) caption.textContent = (player ? player.name : 'Player') + ' · full McDraft journey';
        if(subcaption) subcaption.textContent = 'Focused player view ignores manager filtering so the whole biography stays intact.';
    }else{
        const allowed = new Set(selectedManagers);
        if(includeFree) allowed.add('Free Agent');
        labels = ['Draft Night', ...selectedManagers];
        if(includeFree) labels.push('Free Agent');
        linkRows = (TRANSFER_RIVER_PASSPORT.river_edges||[]).filter(edge=>{
            if(edge.source==='Draft Night') return allowed.has(edge.target);
            return allowed.has(edge.source) && allowed.has(edge.target);
        }).map(edge=>({
            source:edge.source,
            target:edge.target,
            value:Math.max(1, Number(edge.moves)||0),
            color: edge.source==='Draft Night' ? 'rgba(148,163,184,.45)' : 'rgba(56,189,248,.35)',
            hover:(edge.player_names||[]).join(', ') + ((edge.player_names||[]).length>=8 ? '…' : '') + '<br>' + Object.entries(edge.kinds||{}).map(([k,v])=>k+': '+v).join(' · ')
        }));
        if(caption) caption.textContent = 'Transfer River · selected McDraft teams';
        if(subcaption) subcaption.textContent = 'Shared Analytics manager filter applied · Draft Night → managers → free-agent churn.';
    }

    const labelIndex = new Map();
    labels.forEach((name, idx)=>labelIndex.set(name, idx));
    const filteredLinks = linkRows.filter(row=>labelIndex.has(row.source) && labelIndex.has(row.target));
    if(stats){
        const nodeCount = passportState.focusPlayer !== null ? labels.length : new Set(filteredLinks.flatMap(l=>[l.source,l.target])).size;
        stats.innerHTML = '<div><strong>'+nodeCount+'</strong><span>'+(passportState.focusPlayer!==null?'Nodes in journey':'Nodes shown')+'</span></div>'+
            '<div><strong>'+filteredLinks.length+'</strong><span>'+(passportState.focusPlayer!==null?'Career steps':'River links')+'</span></div>'+
            '<div><strong>'+TRANSFER_RIVER_PASSPORT.summary.moves+'</strong><span>Season movements</span></div>'+
            '<div><strong>'+TRANSFER_RIVER_PASSPORT.summary.players+'</strong><span>Players tracked</span></div>';
    }
    if(empty){
        empty.hidden = filteredLinks.length > 0;
        empty.textContent = passportState.focusPlayer !== null ? 'No journey data found for that player yet.' : 'No movement links match the current manager filter.';
    }
    if(!filteredLinks.length){
        if(window.Plotly){ Plotly.purge(chart); }
        chart.innerHTML = '';
        renderPlayerPassportDetail();
        return;
    }
    if(typeof Plotly === 'undefined'){
        chart.innerHTML = '<div class="notice">Plotly failed to load, so the River chart cannot render right now.</div>';
        renderPlayerPassportDetail();
        return;
    }
    Plotly.react(chart, [{
        type: 'sankey',
        arrangement: 'snap',
        node: {
            label: labels,
            color: labels.map(riverNodeColor),
            pad: 18,
            thickness: 18,
            line: {color:'rgba(15,23,42,.95)', width:1}
        },
        link: {
            source: filteredLinks.map(row=>labelIndex.get(row.source)),
            target: filteredLinks.map(row=>labelIndex.get(row.target)),
            value: filteredLinks.map(row=>row.value),
            color: filteredLinks.map(row=>row.color),
            customdata: filteredLinks.map(row=>row.hover),
            hovertemplate: '%{source.label} → %{target.label}<br><b>%{value}</b> move(s)<br>%{customdata}<extra></extra>'
        }
    }], {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: {l:10,r:10,t:10,b:10},
        font: {color:'#e5eefb', size:12},
        height: passportState.focusPlayer !== null ? 440 : 520,
    }, {displayModeBar:false, responsive:true, scrollZoom:false});
    renderPlayerPassportDetail();
}
function renderPlayerPassportDetail(){
    const detail = document.getElementById('player-passport-detail');
    if(!detail) return;
    const passport = passportState.focusPlayer !== null ? TRANSFER_RIVER_PASSPORT.passports[String(passportState.focusPlayer)] : null;
    if(!passport){
        const top = (TRANSFER_RIVER_PASSPORT.top_movers||[]).map(row=>
          '<li><button type="button" onclick="passportState.focusPlayer='+row.id+';document.getElementById(\'passport-player-search\').value=\''+passportEscape(row.name)+'\';renderTransferRiverPassport()"><span><b>'+passportEscape(row.name)+'</b><small>'+passportEscape(row.owner)+' · '+passportEscape(row.points)+' points</small></span><span><strong>'+row.moves+'</strong><small>moves</small></span></button></li>'
        ).join('');
        detail.innerHTML = '<h3>Season biggest movers</h3><p>Open one of these passports or search for anyone in the league.</p><ol class="passport-mover-list">'+top+'</ol>';
        return;
    }
    const ownerRows = (passport.owner_breakdown||[]).map(row=>
        '<tr><td><span class="passport-owner-chip"><i style="background:'+riverNodeColor(row.owner)+'"></i>'+passportEscape(row.owner)+'</span></td><td><strong>'+row.points.toFixed(1)+'</strong></td><td>'+row.weeks+'</td></tr>'
    ).join('');
    const stints = (passport.stints||[]).map(stint=>
        '<div class="passport-stint"><span><span class="passport-owner-chip"><i style="background:'+riverNodeColor(stint.owner)+'"></i>'+passportEscape(stint.owner)+'</span></span><span>GW'+stint.start_gw+'–GW'+stint.end_gw+' · <strong>'+stint.points.toFixed(1)+'</strong> pts</span></div>'
    ).join('') || '<p class="muted">No finished-gameweek ownership stints captured yet.</p>';
    const tx = (passport.transactions||[]).map(item=>
        '<li><b>'+(item.gw ? ('GW'+item.gw) : 'Draft')+'</b> · '+passportEscape(item.kind)+'<br><span class="muted">'+passportEscape(item.from)+' → '+passportEscape(item.to)+'</span><br>'+passportEscape(item.summary)+'</li>'
    ).join('') || '<li>No movement history captured yet.</li>';
    detail.innerHTML = '<div class="passport-hero"><div><h3>'+passportEscape(passport.name)+'</h3><p>'+passportEscape(passport.club)+' · '+passportEscape(passport.position)+'</p></div><span class="passport-owner-chip"><i style="background:'+riverNodeColor(passport.current_owner)+'"></i>'+passportEscape(passport.current_owner)+'</span></div>'+
        '<div class="passport-metrics">'+
        '<div><strong>'+passport.total_points.toFixed(1)+'</strong><small>Season points</small></div>'+
        '<div><strong>'+(passport.original_pick ? ('#'+passport.original_pick) : '—')+'</strong><small>Original draft pick</small></div>'+
        '<div><strong>'+passportEscape(passport.original_manager)+'</strong><small>Original manager</small></div>'+
        '<div><strong>#'+passport.blended_rank+'</strong><small>McDraft blended rank</small></div>'+
        '</div>'+
        '<div class="passport-section"><h4>Ownership stints</h4><div class="passport-stints">'+stints+'</div></div>'+
        '<div class="passport-section"><h4>Points by owner</h4><table class="passport-table"><thead><tr><th>Owner</th><th>Points</th><th>Weeks</th></tr></thead><tbody>'+ownerRows+'</tbody></table></div>'+
        '<div class="passport-section"><h4>Transaction log</h4><ol class="passport-transactions">'+tx+'</ol></div>';
}

function showAnalyticsSubtab(name, button) {
    document.querySelectorAll('.analytics-subpage').forEach(function(page) { page.classList.remove('active'); });
    document.querySelectorAll('#page-analytics .analytics-subtab').forEach(function(tab) { tab.classList.remove('active'); });
    var target = document.getElementById('analytics-sub-' + name);
    if (target) target.classList.add('active');
    if (button) button.classList.add('active');
    // The shared Manager filter stays visible on every Analytics subtab.
    if(name==='player') applyPlayerAnalyticsFilter();
    if(name==='ratings'){applyPlayerAnalyticsFilter();ratingLabRender();}
    if(name==='relationships') requestAnimationFrame(renderPlayerRelationshipGraph);
    if(name==='river-passport') requestAnimationFrame(renderTransferRiverPassport);
}

/* ============================================================
   RATING LAB — persistent GW trends, current ratings and factor attribution
   ============================================================ */
const ratingLabState = {selected:[], initialised:false, position:'ALL'};
const ratingLabPalette = ['#edbd68','#6acbe0','#d296e8','#84d49d'];
const ratingLabFactors = ['3GW form','5GW form','Season output','Draft pedigree',
                          'PL club & form','Availability & minutes','Underlying stats'];
function ratingLabEsc(v){return String(v??'').replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}
function ratingTier(score){score=Number(score||0);return score>=90?'platinum':score>=80?'gold':score>=70?'silver':'bronze';}
function ratingTierLabel(score){const t=ratingTier(score);return t.charAt(0).toUpperCase()+t.slice(1);}
function ratingLabOwner(p){return (!p.fantasy_team || p.fantasy_team==='Free Agent' || p.fantasy_team==='Free agents')
    ? 'Free agents' : p.fantasy_team;}
function ratingLabAllowed(p){const owner=ratingLabOwner(p);
    return owner==='Free agents' ? analyticsManagerState.includeFreeAgents
         : analyticsManagerState.visible.has(owner);}
function ratingLabPool(){return playerSearchData.filter(p=>p.draft_active!==false && Number.isFinite(Number(p.player_rating)) && ratingLabAllowed(p));}
function ratingLabRecord(id){return playerSearchData.find(p=>Number(p.id)===Number(id));}
function ratingLabPoints(p){return (p.rating_history||[]).filter(r=>Number.isFinite(Number(r.rating)));}
function ratingLabAutoSelect(){
    ratingLabState.initialised=true;
    ratingLabState.selected=ratingLabPool().filter(p=>ratingLabPoints(p).length)
        .sort((a,b)=>Number(b.player_rating)-Number(a.player_rating)).slice(0,4).map(p=>Number(p.id));
    const search=document.getElementById('rating-lab-search');if(search)search.value='';
    ratingLabRender();
}
function ratingLabClear(){ratingLabState.initialised=true;ratingLabState.selected=[];ratingLabRender();}
function ratingLabAdd(pid){
    pid=Number(pid);const p=ratingLabRecord(pid);
    if(!p || !ratingLabAllowed(p) || ratingLabState.selected.includes(pid))return;
    ratingLabState.initialised=true;
    if(ratingLabState.selected.length===4) ratingLabState.selected.shift();
    ratingLabState.selected.push(pid);
    const search=document.getElementById('rating-lab-search');if(search)search.value='';
    ratingLabRender();
}
function ratingLabRemove(pid){ratingLabState.selected=ratingLabState.selected.filter(id=>id!==Number(pid));ratingLabRender();}
function ratingLabFind(){
    const input=document.getElementById('rating-lab-search');
    const root=document.getElementById('rating-lab-suggestions');if(!root)return;
    const term=(input?.value||'').trim().toLowerCase();
    if(!term){root.innerHTML='';return;}
    const rows=ratingLabPool().filter(p=>((p.name||'')+' '+(p.team||'')+' '+(p.position||'')).toLowerCase().includes(term))
        .sort((a,b)=>Number(b.player_rating)-Number(a.player_rating)).slice(0,12);
    root.innerHTML=rows.length ? rows.map(p=>'<button type="button" onclick="ratingLabAdd('+Number(p.id)+')">'
        +ratingLabEsc(p.name)+' <small>'+ratingLabEsc(p.position)+' · '+ratingLabEsc(ratingLabOwner(p))+'</small> '
        +'<strong class="rating-tier-number '+ratingTier(p.player_rating)+'">'+Number(p.player_rating)+'/100</strong></button>').join('')
        : '<span class="muted">No matching players in the current manager filter.</span>';
}
function ratingLabSVG(players,compact=false){
    const datasets=players.map(p=>({player:p,rows:ratingLabPoints(p)})).filter(d=>d.rows.length);
    if(!datasets.length)return '<div class="notice">No ratings available for this selection yet.</div>';
    const W=compact?700:1000,H=compact?190:342,L=compact?37:52,R=compact?15:27,T=compact?12:18,B=compact?26:49;
    const pw=W-L-R,ph=H-T-B;
    const historical=datasets.flatMap(d=>d.rows.filter(r=>r.source!=='latest').map(r=>Number(r.gw)));
    const minGw=historical.length?Math.min(...historical):1;
    const maxGw=Math.max(...historical,1);
    const hasNow=datasets.some(d=>d.rows.some(r=>r.source==='latest'));
    const end=maxGw+(hasNow?1:0);
    const X=r=>L+((r.source==='latest'?maxGw+1:Number(r.gw))-minGw)/Math.max(1,end-minGw)*pw;
    const Y=r=>T+(100-Math.max(30,Math.min(100,Number(r.rating))))/70*ph;
    let html='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Player ratings by gameweek">';
    for(const tick of [30,40,50,60,70,80,90,100]){
        const y=T+(100-tick)/70*ph;
        html+='<line class="rating-lab-grid" x1="'+L+'" x2="'+(W-R)+'" y1="'+y+'" y2="'+y+'"/>'
            +'<text class="rating-lab-axis" x="'+(L-9)+'" y="'+(y+4)+'" text-anchor="end">'+tick+'</text>';
    }
    const step=compact?Math.max(1,Math.ceil((end-minGw)/7)):Math.max(1,Math.ceil((end-minGw)/12));
    for(let g=minGw;g<=end;g++){
        if((g-minGw)%step!==0 && g!==end)continue;
        const x=L+(g-minGw)/Math.max(1,end-minGw)*pw;
        html+='<text class="rating-lab-axis" x="'+x+'" y="'+(H-B+17)+'" text-anchor="middle">'
            +(hasNow&&g===end?'Now':'GW'+g)+'</text>';
    }
    datasets.forEach((d,idx)=>{
        const colour=ratingLabPalette[idx%ratingLabPalette.length];
        const rows=d.rows;
        for(let j=1;j<rows.length;j++){
            const a=rows[j-1],b=rows[j];
            const estimate=a.source==='estimated'||b.source==='estimated';
            html+='<path d="M'+X(a).toFixed(1)+','+Y(a).toFixed(1)+' L'+X(b).toFixed(1)+','+Y(b).toFixed(1)+'"'
                +' stroke="'+colour+'" stroke-width="'+(compact?2:3)+'" fill="none"'
                +(estimate?' stroke-dasharray="7 5"':'')+'/>';
        }
        rows.forEach(r=>{
            const desc=(r.source==='estimated'?'Retrospective estimate':r.source==='latest'?'Latest build':'Observed GW snapshot');
            const tooltip=d.player.name+' · '+(r.source==='latest'?'Now':'GW'+r.gw)
                +' · '+r.rating+'/100 · '+desc+' · PL club form '+Number(r.club_form||0)+'/100';
            html+='<circle cx="'+X(r).toFixed(1)+'" cy="'+Y(r).toFixed(1)+'" r="'+(compact?3.1:4.3)+'"'
                +' fill="'+(r.source==='estimated'?'#101827':colour)+'" stroke="'+colour+'" stroke-width="2" tabindex="0">'
                +'<title>'+ratingLabEsc(tooltip)+'</title></circle>';
            // Invisible larger target makes the marker genuinely tappable on phones.
            html+='<circle cx="'+X(r).toFixed(1)+'" cy="'+Y(r).toFixed(1)+'" r="15"'
                +' fill="transparent" role="button" tabindex="0" data-chart-detail="'+ratingLabEsc(tooltip)+'"'
                +'><title>'+ratingLabEsc(tooltip)+'</title></circle>';
        });
    });
    html+='</svg>';
    return html;
}
function ratingLabRender(){
    const root=document.getElementById('analytics-sub-ratings');if(!root)return;
    if(!ratingLabState.initialised){ratingLabAutoSelect();return;}
    ratingLabState.selected=ratingLabState.selected.filter(id=>{const p=ratingLabRecord(id);return p&&ratingLabAllowed(p);});
    const picked=ratingLabState.selected.map(ratingLabRecord).filter(Boolean);
    const chips=document.getElementById('rating-lab-chips');
    if(chips)chips.innerHTML=picked.length?picked.map((p,i)=>'<button type="button" class="rating-lab-chip"'
        +' style="--chip:'+ratingLabPalette[i%ratingLabPalette.length]+'" onclick="ratingLabRemove('+Number(p.id)+')">'
        +ratingLabEsc(p.name)+' <b class="rating-tier-number '+ratingTier(p.player_rating)+'">'+Number(p.player_rating)+'</b> <span aria-label="Remove">×</span></button>').join('')
        :'<span class="muted">Search for players above, or choose Current top four.</span>';
    const canvas=document.getElementById('rating-lab-trend');
    if(canvas)canvas.innerHTML=ratingLabSVG(picked);
    ratingLabDrivers(false);
    ratingLabHistogram();
    ratingLabFind();
}
function ratingLabDrivers(keepWeek=false){
    const focus=document.getElementById('rating-lab-focus'),weeks=document.getElementById('rating-lab-week');
    const root=document.getElementById('rating-lab-drivers');if(!focus||!weeks||!root)return;
    const oldId=focus.value,oldIndex=weeks.value;
    const picked=ratingLabState.selected.map(ratingLabRecord).filter(Boolean);
    focus.innerHTML=picked.map(p=>'<option value="'+Number(p.id)+'">'+ratingLabEsc(p.name)+'</option>').join('');
    if(oldId&&picked.some(p=>String(p.id)===oldId))focus.value=oldId;
    const p=ratingLabRecord(focus.value);
    if(!p){weeks.innerHTML='';root.innerHTML='<div class="notice">Select at least one player to inspect their rating drivers.</div>';return;}
    const points=ratingLabPoints(p);
    weeks.innerHTML=points.map((r,i)=>'<option value="'+i+'">'
        +(r.source==='latest'?'Now':'GW'+r.gw)
        +(r.source==='estimated'?' · estimate':'')+'</option>').join('');
    weeks.value=(keepWeek && oldIndex!=='' && Number(oldIndex)<points.length)?oldIndex:String(Math.max(0,points.length-1));
    const at=Number(weeks.value),curr=points[at],prev=at>0?points[at-1]:null;
    if(!curr){root.innerHTML='<div class="notice">No snapshot has been captured yet.</div>';return;}
    const delta=prev?curr.rating-prev.rating:null;
    const trend=delta===null?'First snapshot':(delta>0?'+'+delta:delta)+' rating points';
    const summary='<div class="rating-lab-driver-summary"><div><strong class="rating-tier-number '+ratingTier(curr.rating)+'">'+curr.rating+'</strong><small>/100 · '+ratingTierLabel(curr.rating)+'</small>'
        +'<span class="'+(delta>0?'rating-up':delta<0?'rating-down':'rating-flat')+'">'+trend+'</span></div>'
        +'<div><b>'+Number(curr.club_form??50)+'/100</b><small>PL club last-5 form'
        +(prev?' · '+(Number(curr.club_form)-Number(prev.club_form)>=0?'+':'')
            +(Number(curr.club_form)-Number(prev.club_form))+' since previous':'' )+'</small></div></div>';
    const current=curr.components||[];const earlier=prev?.components||[];
    const rows=ratingLabFactors.map((name,i)=>{
        const value=Number(current[i]??50),before=prev?Number(earlier[i]??50):null;
        const change=before===null?null:value-before;
        return '<div class="rating-lab-factor"><div><span>'+ratingLabEsc(name)+'</span>'
            +'<strong>'+value+'/100'+(change===null?'':' <small class="'+(change>0?'rating-up':change<0?'rating-down':'rating-flat')+'">'
                +(change>0?'+':'')+change+'</small>')+'</strong></div>'
            +'<i><em style="width:'+Math.max(0,Math.min(100,value))+'%"></em>'
            +(before===null?'':'<b style="left:'+Math.max(0,Math.min(100,before))+'%" title="Previous: '+before+'"></b>')
            +'</i></div>';
    }).join('');
    const caution=(curr.source==='estimated'||prev?.source==='estimated')
        ?'<p class="rating-lab-caution">Dashed history uses reconstructed estimates. Historical medical status and unavailable per-GW advanced data are not recoverable.</p>':'';
    root.innerHTML=summary+rows+caution;
}
function ratingLabHistogram(){
    const root=document.getElementById('rating-lab-histogram'),filter=document.getElementById('rating-lab-position-filter');
    if(!root||!filter)return;
    const posLabels={ALL:'All players',GKP:'GK',DEF:'DEF',MID:'MID',FWD:'ATT'};
    filter.innerHTML=Object.entries(posLabels).map(([p,l])=>'<button type="button" class="'
        +(ratingLabState.position===p?'active':'')+'" onclick="ratingLabPosition('+"'"+p+"'"+')">'+l+'</button>').join('');
    const pool=ratingLabPool().filter(p=>ratingLabState.position==='ALL'||p.position===ratingLabState.position);
    const bins=[30,40,50,60,70,80,90];
    const counts=bins.map(min=>pool.filter(p=>Number(p.player_rating)>=min && Number(p.player_rating)<min+10).length);
    const maximum=Math.max(1,...counts);
    root.innerHTML=bins.map((min,i)=>'<div class="rating-lab-hist-row"><span>'+min+'–'+(min+9)+'</span>'
        +'<i><em class="rating-hist-'+ratingTier(min+5)+'" style="width:'+(counts[i]/maximum*100).toFixed(1)+'%"></em></i><strong>'+counts[i]+'</strong></div>').join('')
        +'<div class="rating-lab-hist-total">'+pool.length+' players in current filter</div>';
}
function ratingLabPosition(pos){ratingLabState.position=pos;ratingLabHistogram();}
function openRatingLabForPlayer(id){
    const p=ratingLabRecord(id);if(!p)return;
    const owner=ratingLabOwner(p);
    if(owner==='Free agents')analyticsManagerState.includeFreeAgents=true;
    else analyticsManagerState.visible.add(owner);
    renderAnalyticsManagerChips();applyAnalyticsManagerFilter();
    ratingLabState.initialised=true;ratingLabState.selected=[Number(id)];
    showPage('analytics');
    const btn=Array.from(document.querySelectorAll('#page-analytics .analytics-subtab'))
        .find(el=>(el.getAttribute('onclick')||'').includes("'ratings'"));
    showAnalyticsSubtab('ratings',btn||null);
}

/* ============================================================
   v53 — Season Simulator. All Monte Carlo runs are browser-local.
   Forecasts and fixtures are generated by the Python season model.
   ============================================================ */
const SEASON_SIMULATOR_DATA = __SEASON_SIMULATOR_DATA__;
const SIM_SCENARIOS = [
    {id:'baseline', label:'Current path', description:'Present squad projections, unchanged.', type:'baseline'},
    {id:'hot', label:'Hot streak', description:'+5 pts/GW for the focus manager.', type:'delta', delta:5},
    {id:'waiver', label:'Waiver upgrade', description:'+3 pts/GW after a hypothetical improvement.', type:'delta', delta:3},
    {id:'injury', label:'Injury setback', description:'−6 pts/GW for a major squad absence.', type:'delta', delta:-6},
    {id:'slump', label:'Form slump', description:'−4 pts/GW for the focus manager.', type:'delta', delta:-4},
    {id:'chaos', label:'League chaos', description:'55% greater weekly score volatility for everyone.', type:'chaos'},
    {id:'custom', label:'Your slider', description:'Use the points adjustment slider.', type:'custom'},
    {id:'roster', label:'Your custom moves', description:'Stack real-player trade, injury and waiver assumptions below.', type:'roster'}
];
const seasonSimState = {
    initialized:false, running:false, runId:0, selected:'baseline',
    outcomes:{}, focus:null, effectWeeks:5, sampleCount:3000, customDelta:3,
    progress:'', noFixtures:false, customActions:[],actionSeq:0,customDirty:false,visibleManagers:null,fixtureWeeks:[],lastConfigKey:null,savedVariants:[],variantSeq:0
};
function simEscape(v){
    return String(v ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}
function simColor(manager){return (SEASON_SIMULATOR_DATA.colors||{})[manager] || '#38bdf8';}
function simRgb(hex){
    const s=String(hex).replace('#','');
    return /^[0-9a-f]{6}$/i.test(s) ? [parseInt(s.slice(0,2),16),parseInt(s.slice(2,4),16),parseInt(s.slice(4,6),16)] : [56,189,248];
}
function simFmtDelta(v,digits=1){
    if(!Number.isFinite(v))return '—';
    return (v>0?'+':'')+v.toFixed(digits);
}
function simPct(v){return (Number(v)||0).toFixed(1)+'%';}
function simRank(v){return Math.round(v).toString();}
function simQuantile(sorted,q){
    if(!sorted.length)return 0;
    const at=Math.max(0,Math.min(1,q))*(sorted.length-1),lo=Math.floor(at),hi=Math.ceil(at);
    return sorted[lo]+(sorted[hi]-sorted[lo])*(at-lo);
}
function simSeed(seed){
    let a=seed>>>0;
    return function(){
        a=(a+0x6D2B79F5)>>>0;
        let t=a;
        t=Math.imul(t^(t>>>15),t|1);
        t^=t+Math.imul(t^(t>>>7),t|61);
        return ((t^(t>>>14))>>>0)/4294967296;
    };
}
function simNormalFactory(seed){
    const uniform=simSeed(seed);
    let spare=null;
    return function(){
        if(spare!==null){const next=spare;spare=null;return next;}
        let u=uniform();if(u<1e-12)u=1e-12;
        const v=uniform(),m=Math.sqrt(-2*Math.log(u)),theta=2*Math.PI*v;
        spare=m*Math.sin(theta);
        return m*Math.cos(theta);
    };
}
function simStatus(text,loading){
    const label=document.getElementById('sim-run-status');
    if(label)label.textContent=text;
    const button=document.querySelector('#page-season-simulator .sim-run-button');
    if(button){button.disabled=!!loading;button.textContent=loading?'Running…':'↻ Run scenarios';}
}
function simPaintSwitcher(){
    const wrap=document.getElementById('sim-scenario-switcher');if(!wrap)return;
    wrap.innerHTML=simAllScenarios().map(s=>
      '<button type="button" class="sim-scenario-chip'+(seasonSimState.selected===s.id?' active':'')+'" '
      +'aria-pressed="'+(seasonSimState.selected===s.id)+'" onclick="selectSeasonScenario(\''+s.id+'\')">'
      +'<strong>'+simEscape(s.label)+(seasonSimState.outcomes[s.id]?' ✓':'')+'</strong><small>'+simEscape(s.description)+'</small></button>'
    ).join('');
}
function selectSeasonScenario(id){
    if(!simAllScenarios().some(s=>s.id===id))return;
    if(!seasonSimState.outcomes[id]){simBuilderMessage('This scenario has not been simulated yet.',true);return;}
    seasonSimState.selected=id;
    simPaintSwitcher();
    simRenderResults();
}
function seasonSimCustomChanged(value){
    seasonSimState.customDelta=Number(value)||0;
    const label=document.getElementById('sim-custom-delta-value');
    if(label)label.textContent=simFmtDelta(seasonSimState.customDelta)+' pts/GW';
    const custom=SIM_SCENARIOS.find(s=>s.id==='custom');
    if(custom)custom.description=simFmtDelta(seasonSimState.customDelta)+' pts/GW for your manager.';
    simPaintSwitcher();
    if(seasonSimState.outcomes.custom){
        delete seasonSimState.outcomes.custom;
        const note=document.getElementById('sim-model-note');
        if(note)note.textContent='Custom adjustment changed; the custom scenario needs recalculation. Release the slider to rerun all scenarios.';
    }
}
function seasonSimConfigurationChanged(){
    if(!seasonSimState.initialized)return;
    runSeasonScenarios();
}
/* v54 — Interactive what-if workshop and all-manager projection graph. */
const SIM_POOL = new Map((SEASON_SIMULATOR_DATA.player_pool||[]).map(p=>[Number(p.id),p]));
const SIM_FORMATIONS = SEASON_SIMULATOR_DATA.formations || [
  {GKP:1,DEF:3,MID:4,FWD:3}, {GKP:1,DEF:3,MID:5,FWD:2},
  {GKP:1,DEF:4,MID:4,FWD:2}, {GKP:1,DEF:4,MID:5,FWD:1},
  {GKP:1,DEF:5,MID:3,FWD:2}, {GKP:1,DEF:5,MID:4,FWD:1}
];
function simPlayerLabel(pid){
    const p=SIM_POOL.get(Number(pid));
    return p ? p.name+' · '+p.position+' · '+p.club : 'Player #'+pid;
}
function simInitialRosters(){
    const rosters={};
    (SEASON_SIMULATOR_DATA.managers||[]).forEach(m=>rosters[m]=(SEASON_SIMULATOR_DATA.rosters?.[m]||[]).map(Number));
    return rosters;
}
function simActionOrder(actions){
    return actions.slice().sort((a,b)=>a.start-b.start||a.id-b.id);
}
function simApplyRosterAction(rosters,action){
    if(action.kind==='trade'){
        const a=rosters[action.aTeam],b=rosters[action.bTeam];
        if(!a||!b||action.aTeam===action.bTeam||!a.includes(action.aPid)||!b.includes(action.bPid))throw Error('Trade players must be owned by different selected managers at that gameweek.');
        if(SIM_POOL.get(action.aPid)?.position!==SIM_POOL.get(action.bPid)?.position)throw Error('Trade players must play the same position.');
        a.splice(a.indexOf(action.aPid),1,action.bPid);
        b.splice(b.indexOf(action.bPid),1,action.aPid);
    }else if(action.kind==='waiver'){
        const roster=rosters[action.team];
        if(!roster||!roster.includes(action.outPid))throw Error('The dropped player is no longer owned by that manager at the selected gameweek.');
        if(Object.values(rosters).some(ids=>ids.includes(action.inPid)))throw Error('The waiver target is already owned at the selected gameweek.');
        if(SIM_POOL.get(action.outPid)?.position!==SIM_POOL.get(action.inPid)?.position)throw Error('Waiver replacements must play the same position.');
        roster.splice(roster.indexOf(action.outPid),1,action.inPid);
    }
}
function simVirtualRostersAt(start){
    const rosters=simInitialRosters();
    simActionOrder(seasonSimState.customActions).forEach(a=>{
        if(a.start<=start && (a.kind==='trade'||a.kind==='waiver'))simApplyRosterAction(rosters,a);
    });
    return rosters;
}
function simBestProjectedXI(ids,gw){
    const group={GKP:[],DEF:[],MID:[],FWD:[]};
    ids.forEach(id=>{
        const p=SIM_POOL.get(Number(id));
        if(p && group[p.position])group[p.position].push(Number(p.by_gw?.[String(gw)]||0));
    });
    Object.keys(group).forEach(pos=>group[pos].sort((a,b)=>b-a));
    let best=-1;
    SIM_FORMATIONS.forEach(formation=>{
        let total=0;
        for(const pos of ['GKP','DEF','MID','FWD']){
            const num=Number(formation[pos]||0);
            if(group[pos].length<num)return;
            for(let i=0;i<num;i++)total+=group[pos][i];
        }
        best=Math.max(best,total);
    });
    if(best>=0)return best;
    // A hypothetical suspension/injury could otherwise leave no legal XI.
    // Count available players rather than spuriously treating the team as zero.
    return Object.values(group).flat().sort((a,b)=>b-a).slice(0,11).reduce((a,b)=>a+b,0);
}
function simComputeCustomDeltas(actions,weeks){
    const initial=simInitialRosters(),rosters=simInitialRosters();
    const deltas={};
    const ordered=simActionOrder(actions),byWeek=weeks.map(()=>[]);
    ordered.forEach(a=>{
        if(a.start>=weeks.length)throw Error('A move starts after the last remaining gameweek.');
        byWeek[a.start].push(a);
    });
    weeks.forEach((gw,wi)=>{
        for(const action of byWeek[wi]){
            if(action.kind==='trade'||action.kind==='waiver')simApplyRosterAction(rosters,action);
            else if(action.kind==='injury'){
                if(!Object.values(rosters).some(ids=>ids.includes(action.pid)))throw Error('The selected player is not on a squad when that injury begins.');
            }
        }
        const absent=new Set(ordered.filter(a=>a.kind==='injury'&&wi>=a.start&&wi<a.start+a.weeks).map(a=>a.pid));
        const map={};
        (SEASON_SIMULATOR_DATA.managers||[]).forEach(manager=>{
            const originalXI=simBestProjectedXI(initial[manager]||[],gw);
            const newXI=simBestProjectedXI((rosters[manager]||[]).filter(pid=>!absent.has(pid)),gw);
            let change=0.85*(newXI-originalXI);
            ordered.filter(a=>a.kind==='points'&&a.team===manager&&wi>=a.start&&wi<a.start+a.weeks)
                .forEach(a=>{change+=a.delta;});
            map[manager]=Math.max(-35,Math.min(35,change));
        });
        deltas[String(gw)]=map;
    });
    return deltas;
}
function simBuilderMessage(text,error){
    const el=document.getElementById('sim-builder-feedback');
    if(el){el.textContent=text||'';el.classList.toggle('error',!!error);}
}
function simSelectOptions(id,rows,keep){
    const el=document.getElementById(id);if(!el)return;
    const value=keep??el.value;
    el.innerHTML=rows.map(r=>'<option value="'+simEscape(r.value)+'">'+simEscape(r.text)+'</option>').join('');
    if(rows.some(r=>String(r.value)===String(value)))el.value=String(value);
}
function simManagerOptions(){return (SEASON_SIMULATOR_DATA.managers||[]).map(m=>({value:m,text:m}));}
function simRosterOptions(roster,pos){
    return (roster||[]).filter(pid=>!pos||SIM_POOL.get(Number(pid))?.position===pos)
      .sort((a,b)=>String(SIM_POOL.get(a)?.name||a).localeCompare(String(SIM_POOL.get(b)?.name||b)))
      .map(pid=>({value:pid,text:simPlayerLabel(pid)}));
}
function simBuilderTypeChanged(){
    const kind=document.getElementById('sim-action-type')?.value||'trade';
    ['trade','injury','waiver','points'].forEach(type=>{
        const el=document.getElementById('sim-builder-'+type);if(el)el.hidden=kind!==type;
    });
    simBuilderOptionsChanged();
}
function simBuilderOptionsChanged(){
    if(!document.getElementById('sim-action-type'))return;
    const start=Number(document.getElementById('sim-action-start')?.value||0);
    let rosters;
    try{rosters=simVirtualRostersAt(start);}
    catch(error){simBuilderMessage(error.message,true);return;}
    const opts=simManagerOptions();
    ['sim-trade-team-a','sim-trade-team-b','sim-injury-team','sim-waiver-team','sim-points-team']
      .forEach(id=>simSelectOptions(id,opts));
    const first=document.getElementById('sim-trade-team-a')?.value;
    const second=document.getElementById('sim-trade-team-b');
    if(second&&second.value===first){second.value=opts.find(r=>r.value!==first)?.value||first;}
    const apos=SIM_POOL.get(Number(document.getElementById('sim-trade-player-a')?.value))?.position;
    simSelectOptions('sim-trade-player-a',simRosterOptions(rosters[first]));
    const chosenPos=SIM_POOL.get(Number(document.getElementById('sim-trade-player-a')?.value))?.position||apos;
    simSelectOptions('sim-trade-player-b',simRosterOptions(rosters[second?.value],chosenPos));
    const injured=document.getElementById('sim-injury-team')?.value;
    simSelectOptions('sim-injury-player',simRosterOptions(rosters[injured]));
    const waive=document.getElementById('sim-waiver-team')?.value;
    simSelectOptions('sim-waiver-out',simRosterOptions(rosters[waive]));
    const drop=Number(document.getElementById('sim-waiver-out')?.value);
    const pos=SIM_POOL.get(drop)?.position;
    const owned=new Set(Object.values(rosters).flat());
    const free=(SEASON_SIMULATOR_DATA.player_pool||[]).filter(p=>p.position===pos&&!owned.has(Number(p.id)))
      .sort((a,b)=>(Number(b.by_gw?.[String((SEASON_SIMULATOR_DATA.fixtures||[])[0]?.gw)]||0)-Number(a.by_gw?.[String((SEASON_SIMULATOR_DATA.fixtures||[])[0]?.gw)]||0))||a.name.localeCompare(b.name))
      .map(p=>({value:p.id,text:simPlayerLabel(p.id)}));
    simSelectOptions('sim-waiver-in',free);
}
function simActionDescription(a){
    const timing='from GW'+(seasonSimState.fixtureWeeks?.[a.start]??'?');
    if(a.kind==='trade')return simPlayerLabel(a.aPid)+' ('+a.aTeam+') ↔ '+simPlayerLabel(a.bPid)+' ('+a.bTeam+') · '+timing;
    if(a.kind==='waiver')return a.team+': drop '+simPlayerLabel(a.outPid)+' → '+simPlayerLabel(a.inPid)+' · '+timing;
    if(a.kind==='injury')return simPlayerLabel(a.pid)+' unavailable for '+(a.weeks>=999?'all remaining':a.weeks)+' GWs · '+timing;
    return a.team+' '+simFmtDelta(a.delta)+' projected pts/GW for '+(a.weeks>=999?'all remaining':a.weeks)+' GWs · '+timing;
}
function simRenderCustomActions(){
    const wrap=document.getElementById('sim-build-list'),count=document.getElementById('sim-builder-count');
    if(count)count.textContent=seasonSimState.customActions.length+' / 6 moves';
    if(!wrap)return;
    wrap.innerHTML=seasonSimState.customActions.length ? seasonSimState.customActions.map((a,i)=>
        '<div class="sim-build-move"><span class="sim-build-index">'+(i+1)+'</span><div><strong>'+simEscape(a.kind==='trade'?'Trade':a.kind==='waiver'?'Waiver move':a.kind==='injury'?'Injury setback':'Points change')+'</strong><p>'+simEscape(simActionDescription(a))+'</p></div><button type="button" aria-label="Remove move" onclick="simRemoveCustomAction('+a.id+')">×</button></div>'
    ).join(''):'<div class="sim-build-placeholder">No moves queued yet. Choose a scenario above, then add it here.</div>';
    const effects=document.getElementById('sim-custom-effects');
    if(effects&&(!seasonSimState.outcomes.roster||seasonSimState.customDirty))effects.innerHTML='';
    simRenderSavedVariants();
    simPaintSwitcher();
}
function simInvalidateCustom(){
    seasonSimState.customDirty=true;
    delete seasonSimState.outcomes.roster;
    if(seasonSimState.selected==='roster')seasonSimState.selected='baseline';
    simRenderCustomActions();
    simRenderResults();
}
function simAddCustomAction(){
    if(seasonSimState.customActions.length>=6){simBuilderMessage('This scenario already contains six changes. Remove one to add another.',true);return;}
    const v=id=>document.getElementById(id)?.value;
    const start=Number(v('sim-action-start')||0),kind=v('sim-action-type');
    const id=++seasonSimState.actionSeq;
    let action;
    if(kind==='trade'){
        action={id,kind,start,aTeam:v('sim-trade-team-a'),bTeam:v('sim-trade-team-b'),aPid:Number(v('sim-trade-player-a')),bPid:Number(v('sim-trade-player-b'))};
        if(!action.aTeam||!action.bTeam||!action.aPid||!action.bPid){simBuilderMessage('Choose both managers and both players.',true);return;}
    }else if(kind==='waiver'){
        action={id,kind,start,team:v('sim-waiver-team'),outPid:Number(v('sim-waiver-out')),inPid:Number(v('sim-waiver-in'))};
        if(!action.team||!action.outPid||!action.inPid){simBuilderMessage('Choose a manager, dropped player and available replacement.',true);return;}
    }else if(kind==='injury'){
        action={id,kind,start,team:v('sim-injury-team'),pid:Number(v('sim-injury-player')),weeks:Number(v('sim-injury-weeks')||3)};
        if(!action.pid){simBuilderMessage('Choose the injured player.',true);return;}
    }else{
        action={id,kind:'points',start,team:v('sim-points-team'),delta:Number(v('sim-points-delta')),weeks:Number(v('sim-points-weeks')||5)};
        if(!action.team||!Number.isFinite(action.delta)||Math.abs(action.delta)>20){simBuilderMessage('Enter a valid points change between −20 and +20.',true);return;}
    }
    const all=[...seasonSimState.customActions,action];
    try{simComputeCustomDeltas(all,seasonSimState.fixtureWeeks||[]);}
    catch(error){simBuilderMessage('Could not add move: '+error.message,true);return;}
    seasonSimState.customActions=all;
    simInvalidateCustom();
    simBuilderMessage('Added: '+simActionDescription(action)+'. Press Simulate my moves to see the impact.',false);
    simBuilderOptionsChanged();
}
function simRemoveCustomAction(id){
    seasonSimState.customActions=seasonSimState.customActions.filter(a=>a.id!==Number(id));
    // Sequential moves can depend on a previous trade. Drop any now-invalid
    // follow-on actions rather than silently producing impossible rosters.
    let valid=[];
    seasonSimState.customActions.forEach(a=>{
        try{simComputeCustomDeltas([...valid,a],seasonSimState.fixtureWeeks||[]);valid.push(a);}
        catch(error){simBuilderMessage('Removed a dependent move that was no longer possible: '+error.message,true);}
    });
    seasonSimState.customActions=valid;
    simInvalidateCustom();
    simBuilderOptionsChanged();
}
function simClearCustomActions(){
    seasonSimState.customActions=[];
    simInvalidateCustom();
    simBuilderMessage('Your custom scenario has been cleared.',false);
    simBuilderOptionsChanged();
}
function simRenderTeamFilters(){
    const wrap=document.getElementById('sim-trajectory-filter');if(!wrap)return;
    const visible=seasonSimState.visibleManagers||new Set();
    let html='<div class="sim-team-presets">'+[['All','all'],['Top 5','top5'],['Focus','focus'],['None','none']].map(([name,id])=>
        '<button type="button" onclick="simSetTeamFilter(\''+id+'\')">'+name+'</button>'
    ).join('')+'</div><div class="sim-team-chips">';
    (SEASON_SIMULATOR_DATA.managers||[]).forEach(manager=>{
        const selected=visible.has(manager),color=simColor(manager);
        html+='<button type="button" class="sim-team-chip'+(selected?' active':'')+'" style="--sim-team-color:'+color+'" '+
            'aria-pressed="'+selected+'" data-team="'+simEscape(manager)+'"><i></i>'+simEscape(manager)+'</button>';
    });
    wrap.innerHTML=html+'</div>';
    wrap.querySelectorAll('.sim-team-chip').forEach(btn=>btn.addEventListener('click',()=>simToggleTeamFilter(btn.dataset.team)));
}
function simSetTeamFilter(preset){
    const managers=SEASON_SIMULATOR_DATA.managers||[];
    const focus=seasonSimState.focus||managers[0];
    seasonSimState.visibleManagers=new Set(preset==='all'?managers:preset==='top5'?managers.slice(0,5):preset==='focus'?[focus]:[]);
    simRenderTeamFilters();simRenderTrajectoryOnly();
}
function simToggleTeamFilter(manager){
    if(!seasonSimState.visibleManagers)seasonSimState.visibleManagers=new Set(SEASON_SIMULATOR_DATA.managers||[]);
    if(seasonSimState.visibleManagers.has(manager))seasonSimState.visibleManagers.delete(manager);
    else seasonSimState.visibleManagers.add(manager);
    simRenderTeamFilters();simRenderTrajectoryOnly();
}
function simRenderTrajectoryOnly(){
    const result=seasonSimState.outcomes[seasonSimState.selected]||seasonSimState.outcomes.baseline;
    const chart=document.getElementById('sim-trajectory-chart');if(!chart||!result)return;
    chart.innerHTML=simTrajectoryHTML(result,seasonSimState.outcomes.baseline,seasonSimState.focus);
}
function simRenderCustomEffects(result){
    const wrap=document.getElementById('sim-custom-effects');if(!wrap)return;
    if(!result||!result.effects){wrap.innerHTML='';return;}
    const weeks=seasonSimState.fixtureWeeks||[],summaries=[];
    (SEASON_SIMULATOR_DATA.managers||[]).forEach(m=>{
        const values=weeks.map(gw=>Number(result.effects[String(gw)]?.[m]||0)).filter(v=>Math.abs(v)>.001);
        if(values.length){
            const avg=values.reduce((a,b)=>a+b,0)/values.length;
            summaries.push({manager:m,avg,count:values.length});
        }
    });
    wrap.innerHTML=summaries.length?'<h4>Estimated weekly XI changes under these moves</h4><div class="sim-custom-impact-grid">'+summaries.map(r=>
        '<div><i style="background:'+simColor(r.manager)+'"></i><strong>'+simEscape(r.manager)+'</strong><span class="'+(r.avg>0?'positive':r.avg<0?'negative':'')+'">'+simFmtDelta(r.avg)+' pts/GW</span><small>across '+r.count+' affected GWs</small></div>'
    ).join('')+'</div>':'';
}
async function simRunCustomMoves(){
    if(!seasonSimState.customActions.length){simBuilderMessage('Add at least one trade, injury, waiver or points change first.',true);return;}
    const data=SEASON_SIMULATOR_DATA;
    if(!(data.fixtures||[]).length){simBuilderMessage('No remaining fixtures to simulate.',true);return;}
    const selector=document.getElementById('sim-manager');
    const focus=selector?.value||data.managers[0];
    const config={focus,effectWeeks:Number(document.getElementById('sim-horizon')?.value||5),
        sampleCount:Number(document.getElementById('sim-samples')?.value||3000),
        customDelta:Number(document.getElementById('sim-custom-delta')?.value||0),
        customActions:seasonSimState.customActions.slice()};
    let effects;
    try{effects=simComputeCustomDeltas(config.customActions,seasonSimState.fixtureWeeks||[]);}
    catch(error){simBuilderMessage('Fix this scenario before running: '+error.message,true);return;}
    const key=JSON.stringify([focus,config.effectWeeks,config.sampleCount,config.customDelta]);
    const runId=++seasonSimState.runId;
    seasonSimState.running=true;seasonSimState.focus=focus;seasonSimState.selected='roster';
    simStatus('Simulating custom roster changes…',true);simPaintSwitcher();
    if(seasonSimState.lastConfigKey!==key||!seasonSimState.outcomes.baseline){
        const baseline=await simRunOneScenario(SIM_SCENARIOS[0],config,runId);
        if(runId!==seasonSimState.runId)return;
        seasonSimState.outcomes={baseline};
    }
    const scenario=SIM_SCENARIOS.find(s=>s.id==='roster');
    const result=await simRunOneScenario(scenario,{...config,customEffects:effects},runId,(done,total)=>
        simStatus('Simulating custom moves · '+Math.round(done/total*100)+'%',true));
    if(runId!==seasonSimState.runId)return;
    seasonSimState.outcomes.roster=result;
    seasonSimState.lastConfigKey=key;
    seasonSimState.customDirty=false;seasonSimState.running=false;
    simRenderCustomEffects(result);
    simStatus(config.sampleCount.toLocaleString()+' custom seasons simulated',false);
    simPaintSwitcher();simRenderResults();
    simBuilderMessage('Custom scenario simulated. Select another scenario above to compare it against the baseline.',false);
}

function simAllScenarios(){return [...SIM_SCENARIOS,...(seasonSimState.savedVariants||[])];}
function simRenderSavedVariants(){
    const box=document.getElementById('sim-saved-variants');if(!box)return;
    const saved=seasonSimState.savedVariants||[];
    box.innerHTML=saved.length?'<span class="sim-saved-caption">Saved what-if scenarios</span>'+saved.map(s=>
        '<div class="sim-saved-item"><span><strong>'+simEscape(s.label)+'</strong><small>'+s.actions.length+' hypothetical changes · compare with baseline</small></span>'+
        '<button type="button" data-view-variant="'+s.id+'">View</button>'+
        '<button type="button" aria-label="Remove saved scenario" data-delete-variant="'+s.id+'">×</button></div>'
    ).join(''):'';
    box.querySelectorAll('[data-view-variant]').forEach(btn=>btn.addEventListener('click',()=>selectSeasonScenario(btn.dataset.viewVariant)));
    box.querySelectorAll('[data-delete-variant]').forEach(btn=>btn.addEventListener('click',()=>simRemoveSavedVariant(btn.dataset.deleteVariant)));
}
function simSaveCustomVariant(){
    if(seasonSimState.customDirty||!seasonSimState.outcomes.roster){
        simBuilderMessage('Simulate your current moves before saving a comparison version.',true);return;
    }
    if(seasonSimState.savedVariants.length>=4){simBuilderMessage('Four saved versions already exist. Remove one to save another.',true);return;}
    const labelInput=document.getElementById('sim-variant-name');
    const label=labelInput?.value.trim()||'Custom version '+(seasonSimState.savedVariants.length+1);
    if(seasonSimState.savedVariants.some(s=>s.label.toLowerCase()===label.toLowerCase())){
        simBuilderMessage('Use a different name for this version.',true);return;
    }
    const id='variant_'+(++seasonSimState.variantSeq);
    const actions=JSON.parse(JSON.stringify(seasonSimState.customActions));
    const variant={id,label,description:actions.length+' hypothetical move'+(actions.length===1?'':'s'),type:'roster',actions};
    seasonSimState.savedVariants.push(variant);
    seasonSimState.outcomes[id]={...seasonSimState.outcomes.roster,id,label,description:variant.description};
    seasonSimState.selected=id;
    if(labelInput)labelInput.value='';
    simRenderSavedVariants();simPaintSwitcher();simRenderResults();
    simBuilderMessage('Saved '+label+'. You can change the workshop and save another version to compare.',false);
}
function simRemoveSavedVariant(id){
    seasonSimState.savedVariants=seasonSimState.savedVariants.filter(s=>s.id!==id);
    delete seasonSimState.outcomes[id];
    if(seasonSimState.selected===id)seasonSimState.selected='baseline';
    simRenderSavedVariants();simPaintSwitcher();simRenderResults();
}

function initSeasonSimulator(){
    const page=document.getElementById('page-season-simulator');if(!page)return;
    if(!seasonSimState.initialized){
        seasonSimState.initialized=true;
        const selector=document.getElementById('sim-manager');
        const managers=SEASON_SIMULATOR_DATA.managers||[];
        if(selector){
            selector.innerHTML=managers.map(m=>'<option value="'+simEscape(m)+'">'+simEscape(m)+'</option>').join('');
            const preferred=managers.find(m=>String(m).toLowerCase()==='kamararama fc')||managers[0];
            if(preferred)selector.value=preferred;
        }
        seasonSimState.fixtureWeeks=[...new Set((SEASON_SIMULATOR_DATA.fixtures||[]).map(f=>Number(f.gw)))].sort((a,b)=>a-b);
        seasonSimState.visibleManagers=new Set(managers);
        seasonSimCustomChanged(3);
        simPaintSwitcher();
        simRenderTeamFilters();
        simBuilderTypeChanged();
        simRenderCustomActions();
    }
    if(!seasonSimState.running && !Object.keys(seasonSimState.outcomes).length)runSeasonScenarios();
    else simRenderResults();
}

async function simRunOneScenario(scenario, config, runId, onProgress){
    const data=SEASON_SIMULATOR_DATA;
    const managers=data.managers||[];
    const teamIndex=new Map(managers.map((m,i)=>[m,i]));
    const focusIndex=teamIndex.get(config.focus);
    const nTeams=managers.length,nRuns=config.sampleCount;
    const fixtures=(data.fixtures||[]).slice().sort((a,b)=>a.gw-b.gw);
    const weeks=[...new Set(fixtures.map(f=>f.gw))].sort((a,b)=>a-b);
    const weekIndex=new Map(weeks.map((w,i)=>[w,i]));
    const profile=managers.map(m=>data.profiles[m]||{});
    const matches=fixtures.map(f=>{
        const home=teamIndex.get(f.home),away=teamIndex.get(f.away),gw=Number(f.gw);
        const mu1=Number((profile[home].by_gw||{})[String(gw)] ?? profile[home].weekly_mean ?? 45);
        const mu2=Number((profile[away].by_gw||{})[String(gw)] ?? profile[away].weekly_mean ?? 45);
        return {gw,wi:weekIndex.get(gw),home,away,mu1,mu2,sd1:Number(profile[home].sd)||12,sd2:Number(profile[away].sd)||12,
                focusEffect:weekIndex.get(gw)<config.effectWeeks};
    });
    const histMean=(managers.reduce((t,m)=>t+Number((data.profiles[m]||{}).weekly_mean||45),0)/Math.max(1,nTeams));
    const sharedSD=Math.max(1,Math.min(5, histMean*0.055));
    const volatilityMultiplier=scenario.type==='chaos'?1.55:1;
    const delta=scenario.type==='custom'?config.customDelta:Number(scenario.delta||0);
    const scenarioEffects=scenario.type==='roster'?(scenario.actions?simComputeCustomDeltas(scenario.actions,weeks):(config.customEffects||simComputeCustomDeltas(config.customActions||[],weeks))):null;
    const rng=simNormalFactory(Number(data.seed||17288)+1024);
    const rankCounts=managers.map(()=>new Uint32Array(nTeams));
    const lpTotals=new Float64Array(nTeams);
    const pfTotals=new Float64Array(nTeams);
    const wTotals=new Float64Array(nTeams);
    const dTotals=new Float64Array(nTeams);
    const lTotals=new Float64Array(nTeams);
    const positions=managers.map(()=>[]);
    const lpSamples=managers.map(()=>[]);
    const timeline=weeks.map(()=>[]);
    const allTimelineTotals=weeks.map(()=>new Float64Array(nTeams));
    function captureWeek(wi,lp){
        if(wi<0)return;
        timeline[wi].push(lp[focusIndex]);
        for(let i=0;i<nTeams;i++)allTimelineTotals[wi][i]+=lp[i];
    }
    const lpInitial=profile.map(p=>Number(p.current_lp)||0);
    const pfInitial=profile.map(p=>Number(p.current_pf)||0);
    const chunks=125;
    for(let run=0;run<nRuns;run++){
        if(runId!==seasonSimState.runId)return null;
        const lp=Float64Array.from(lpInitial),pf=Float64Array.from(pfInitial);
        const wins=new Uint16Array(nTeams),draws=new Uint16Array(nTeams),losses=new Uint16Array(nTeams);
        let lastWeek=-1,weekShock=0;
        for(let ix=0;ix<matches.length;ix++){
            const f=matches[ix];
            if(f.wi!==lastWeek){
                if(lastWeek>=0)captureWeek(lastWeek,lp);
                lastWeek=f.wi;
                weekShock=rng()*sharedSD*volatilityMultiplier;
            }
            const adj=(f.focusEffect ? delta : 0);
            const effect=scenarioEffects?.[String(f.gw)];
            const muHome=f.mu1+((f.home===focusIndex)?adj:0)+Number(effect?.[managers[f.home]]||0);
            const muAway=f.mu2+((f.away===focusIndex)?adj:0)+Number(effect?.[managers[f.away]]||0);
            const s1=Math.max(0,Math.round(muHome+weekShock+rng()*f.sd1*volatilityMultiplier));
            const s2=Math.max(0,Math.round(muAway+weekShock+rng()*f.sd2*volatilityMultiplier));
            pf[f.home]+=s1;pf[f.away]+=s2;
            if(s1>s2){lp[f.home]+=3;wins[f.home]++;losses[f.away]++;}
            else if(s2>s1){lp[f.away]+=3;wins[f.away]++;losses[f.home]++;}
            else{lp[f.home]++;lp[f.away]++;draws[f.home]++;draws[f.away]++;}
        }
        if(lastWeek>=0)captureWeek(lastWeek,lp);
        const ranking=Array.from({length:nTeams},(_,i)=>i).sort((a,b)=>lp[b]-lp[a]||pf[b]-pf[a]||managers[a].localeCompare(managers[b]));
        ranking.forEach((ti,pos)=>{
            rankCounts[ti][pos]++;
            positions[ti].push(pos+1);
        });
        for(let ti=0;ti<nTeams;ti++){
            lpTotals[ti]+=lp[ti];pfTotals[ti]+=pf[ti];
            wTotals[ti]+=wins[ti];dTotals[ti]+=draws[ti];lTotals[ti]+=losses[ti];
            lpSamples[ti].push(lp[ti]);
        }
        if((run+1)%chunks===0){
            if(typeof onProgress==='function')onProgress(run+1,nRuns);
            await new Promise(resolve=>setTimeout(resolve,0));
        }
    }
    const teamRows=managers.map((manager,ti)=>{
        const sortedPositions=positions[ti].sort((a,b)=>a-b),sortedLP=lpSamples[ti].sort((a,b)=>a-b);
        const probabilities=Array.from(rankCounts[ti],x=>x/nRuns*100);
        return {manager,current_lp:lpInitial[ti],current_pf:pfInitial[ti],
            expected_lp:lpTotals[ti]/nRuns,expected_pf:pfTotals[ti]/nRuns,
            median_finish:simQuantile(sortedPositions,0.50),
            finish_p10:simQuantile(sortedPositions,0.10),finish_p90:simQuantile(sortedPositions,0.90),
            lp_p10:simQuantile(sortedLP,0.10),lp_p90:simQuantile(sortedLP,0.90),
            champion_pct:probabilities[0]||0,
            top3_pct:probabilities.slice(0,Math.min(3,nTeams)).reduce((a,b)=>a+b,0),
            wooden_pct:probabilities[nTeams-1]||0,
            expected_wins:wTotals[ti]/nRuns, expected_draws:dTotals[ti]/nRuns, expected_losses:lTotals[ti]/nRuns,
            positions_pct:probabilities};
    });
    const focusTimeline=[{gw:data.last_completed_gw,lo:lpInitial[focusIndex],mid:lpInitial[focusIndex],hi:lpInitial[focusIndex]}];
    weeks.forEach((gw,i)=>{
        const sorted=timeline[i].sort((a,b)=>a-b);
        focusTimeline.push({gw,lo:simQuantile(sorted,.10),mid:simQuantile(sorted,.50),hi:simQuantile(sorted,.90)});
    });
    const allTimelines={};
    managers.forEach((manager,ti)=>{
        allTimelines[manager]=[{gw:data.last_completed_gw,mid:lpInitial[ti]}];
        weeks.forEach((gw,wi)=>allTimelines[manager].push({gw,mid:allTimelineTotals[wi][ti]/nRuns}));
    });
    return {id:scenario.id,label:scenario.label,description:scenario.description,teams:teamRows,
        focus:config.focus,focusTimeline,allTimelines,focusIndex,runs:nRuns,
        effects:scenarioEffects,scenario_delta:delta, weeksAffected:config.effectWeeks};
}

async function runSeasonScenarios(){
    const data=SEASON_SIMULATOR_DATA;
    if(!data.managers||!data.managers.length)return;
    const selector=document.getElementById('sim-manager');
    const focus=(selector&&selector.value)||data.managers[0];
    const horizon=Number(document.getElementById('sim-horizon')?.value||5);
    const sampleCount=Number(document.getElementById('sim-samples')?.value||3000);
    const customDelta=Number(document.getElementById('sim-custom-delta')?.value||0);
    const config={focus,effectWeeks:horizon,sampleCount,customDelta,
        customActions:seasonSimState.customActions.slice()};
    const key=JSON.stringify([focus,horizon,sampleCount,customDelta]);
    const runId=++seasonSimState.runId;
    seasonSimState.running=true;seasonSimState.focus=focus;
    seasonSimState.effectWeeks=horizon;seasonSimState.sampleCount=sampleCount;seasonSimState.customDelta=customDelta;
    seasonSimState.outcomes={};
    seasonSimState.lastConfigKey=key;
    simPaintSwitcher();
    const note=document.getElementById('sim-model-note');
    if(note){
        const fixtureCount=(data.fixtures||[]).length;
        const confidence=data.confidence||'Unknown';
        note.textContent=fixtureCount+' remaining scheduled head-to-head fixtures across '+
          new Set((data.fixtures||[]).map(f=>f.gw)).size+' gameweeks. ' +
          'Scenarios modify expected scores, not historical results. Every scenario uses the same random draws. ' +
          (data.in_progress_gw ? ('GW'+data.in_progress_gw+' is live; its partial score is not locked in this model. ') : '')+
          confidence+' model confidence from completed-GW evidence. '+
          'Presets are illustrative; custom trades, injury absences and waiver swaps recalculate legal projected XIs from the latest captured rosters.';
    }
    if(!(data.fixtures||[]).length){
        seasonSimState.running=false;seasonSimState.noFixtures=true;
        simStatus('No remaining scheduled fixtures',false);
        simRenderResults();return;
    }
    seasonSimState.noFixtures=false;
    simStatus('Preparing '+sampleCount.toLocaleString()+' samples per scenario…',true);
    const runnable=simAllScenarios().filter(s=>s.id!=='roster'||config.customActions.length>0);
    try{
        if(config.customActions.length)config.customEffects=simComputeCustomDeltas(config.customActions,seasonSimState.fixtureWeeks);
    }catch(error){simBuilderMessage(error.message,true);seasonSimState.running=false;simStatus('Custom scenario invalid',false);return;}
    for(let ix=0;ix<runnable.length;ix++){
        if(runId!==seasonSimState.runId)return;
        const scenario=runnable[ix];
        simStatus('Running '+(ix+1)+'/'+runnable.length+': '+scenario.label+'…',true);
        const result=await simRunOneScenario(scenario,config,runId,(done,total)=>{
            simStatus('Scenario '+(ix+1)+'/'+runnable.length+': '+scenario.label+' · '+Math.round(done/total*100)+'%',true);
        });
        if(runId!==seasonSimState.runId)return;
        seasonSimState.outcomes[scenario.id]=result;
        if(scenario.id==='roster'){seasonSimState.customDirty=false;simRenderCustomEffects(result);}
        simPaintSwitcher();
        simRenderResults();
    }
    seasonSimState.running=false;
    simStatus((sampleCount*runnable.length).toLocaleString()+' seasons simulated · '+runnable.length+' scenarios ready',false);
    simRenderResults();
}
function simSvgPath(points){return points.map((p,i)=>(i?'L':'M')+p[0].toFixed(1)+','+p[1].toFixed(1)).join(' ');}
function simDistributionHTML(result,baseline,focus){
    const target=result?.teams.find(t=>t.manager===focus);
    const base=baseline?.teams.find(t=>t.manager===focus);
    if(!target)return '<div class="sim-empty">Run simulations to see the distribution.</div>';
    const n=target.positions_pct.length,w=680,h=265,pad={l:37,r:12,t:23,b:39};
    const plotW=w-pad.l-pad.r,plotH=h-pad.t-pad.b,barStep=plotW/n;
    const maxP=Math.max(12,...target.positions_pct,...(base?.positions_pct||[]));
    const top=Math.ceil(maxP/10)*10;
    const rgb=simRgb(simColor(focus)),color='rgb('+rgb.join(',')+')';
    const y=p=>pad.t+(1-p/top)*plotH;
    let grid='',labels='',bars='';
    for(let tick=0;tick<=4;tick++){
        const pct=tick*top/4,py=y(pct);
        grid+='<line x1="'+pad.l+'" y1="'+py+'" x2="'+(w-pad.r)+'" y2="'+py+'" class="sim-svg-grid"/>'+
              '<text class="sim-svg-label" x="'+(pad.l-8)+'" y="'+(py+4)+'" text-anchor="end">'+pct.toFixed(0)+'%</text>';
    }
    for(let i=0;i<n;i++){
        const cx=pad.l+(i+.5)*barStep;
        if(base&&result.id!=='baseline'){
            const bv=base.positions_pct[i]||0,bw=barStep*.68;
            bars+='<rect x="'+(cx-bw/2)+'" y="'+y(bv)+'" width="'+bw+'" height="'+Math.max(0,pad.t+plotH-y(bv))+'" rx="3" fill="#64748b" opacity=".42"><title>Baseline #'+(i+1)+': '+simPct(bv)+'</title></rect>';
        }
        const v=target.positions_pct[i],bw=barStep*((base && result.id !== 'baseline') ? .39 : .68);
        bars+='<rect x="'+(cx-bw/2)+'" y="'+y(v)+'" width="'+bw+'" height="'+Math.max(0,pad.t+plotH-y(v))+'" rx="3" fill="'+color+'" opacity=".85"><title>#'+(i+1)+': '+simPct(v)+'</title></rect>';
        labels+='<text class="sim-svg-label" x="'+cx+'" y="'+(h-16)+'" text-anchor="middle">#'+(i+1)+'</text>';
    }
    return '<svg role="img" aria-label="Simulated final rank probabilities" viewBox="0 0 '+w+' '+h+'">'+grid+bars+labels+'</svg>'+
      '<div class="sim-chart-legend"><span><i style="background:'+color+'"></i>'+simEscape(result.label)+'</span>'+
      (base&&result.id!=='baseline'?'<span><i style="background:#64748b"></i>Current path</span>':'')+'</div>';
}
function simTrajectoryHTML(result,baseline,focus){
    const all=result?.allTimelines||{},visible=seasonSimState.visibleManagers||new Set(SEASON_SIMULATOR_DATA.managers||[]);
    const managers=(SEASON_SIMULATOR_DATA.managers||[]).filter(m=>visible.has(m)&&all[m]?.length>1);
    if(!managers.length)return '<div class="sim-empty">No teams selected. Use All, Top 5, Focus, or the team chips above to display league-points trajectories.</div>';
    const baseRows=baseline?.allTimelines?.[focus]||[];
    const bandRows=(result.focusTimeline||[]);
    const hasBand=document.getElementById('sim-trajectory-band')?.checked!==false&&managers.includes(focus)&&bandRows.length>1;
    const allPoints=managers.flatMap(m=>all[m].map(r=>r.mid));
    if(hasBand)allPoints.push(...bandRows.flatMap(r=>[r.lo,r.hi]));
    if(baseline&&result.id!=='baseline'&&managers.includes(focus))allPoints.push(...baseRows.map(r=>r.mid));
    let min=Math.floor(Math.min(...allPoints)/5)*5,max=Math.ceil(Math.max(...allPoints)/5)*5;
    if(max-min<5){max+=5;min-=5;}
    const sample=all[managers[0]],w=940,h=362,pad={l:45,r:26,t:20,b:42};
    const x=i=>pad.l+i*(w-pad.l-pad.r)/Math.max(1,sample.length-1);
    const y=v=>pad.t+(max-v)/(max-min)*(h-pad.t-pad.b);
    let grid='',labels='',draw='';
    for(let t=0;t<=5;t++){
        const val=min+(max-min)*t/5,py=y(val);
        grid+='<line x1="'+pad.l+'" y1="'+py+'" x2="'+(w-pad.r)+'" y2="'+py+'" class="sim-svg-grid"/>'+
            '<text class="sim-svg-label" x="'+(pad.l-7)+'" y="'+(py+4)+'" text-anchor="end">'+val.toFixed(0)+'</text>';
    }
    const gwStep=Math.max(1,Math.ceil(sample.length/10));
    sample.forEach((r,i)=>{if(i%gwStep===0||i===sample.length-1){labels+='<text class="sim-svg-label" x="'+x(i)+'" y="'+(h-12)+'" text-anchor="middle">GW'+r.gw+'</text>';}});
    if(hasBand){
        const upper=bandRows.map((r,i)=>[x(i),y(r.hi)]);
        const lower=bandRows.map((r,i)=>[x(i),y(r.lo)]);
        const band=simSvgPath(upper)+' '+lower.reverse().map(p=>'L'+p[0].toFixed(1)+','+p[1].toFixed(1)).join(' ')+' Z';
        const rgb=simRgb(simColor(focus));
        draw+='<path d="'+band+'" fill="rgba('+rgb.join(',')+',.15)" stroke="none"/>';
    }
    if(baseline&&result.id!=='baseline'&&managers.includes(focus)&&baseRows.length===sample.length){
        draw+='<path d="'+simSvgPath(baseRows.map((r,i)=>[x(i),y(r.mid)]))+'" fill="none" stroke="'+simColor(focus)+'" stroke-dasharray="7 5" stroke-width="2" opacity=".55"><title>'+simEscape(focus)+' · baseline mean</title></path>';
    }
    managers.slice().sort((a,b)=>(a===focus?1:0)-(b===focus?1:0)).forEach(manager=>{
        const rows=all[manager],color=simColor(manager),focused=manager===focus;
        const path=simSvgPath(rows.map((r,i)=>[x(i),y(r.mid)]));
        draw+='<path class="sim-trajectory-line" d="'+path+'" fill="none" stroke="'+color+'" stroke-width="'+(focused?3.8:2.2)+'" '+
            'stroke-linecap="round" stroke-linejoin="round" opacity="'+(focused?1:.81)+'"><title>'+simEscape(manager)+' · '+simEscape(result.label)+' · final '+rows[rows.length-1].mid.toFixed(1)+' expected LP</title></path>';
        const end=rows[rows.length-1],endX=x(rows.length-1),endY=y(end.mid);
        draw+='<circle cx="'+endX+'" cy="'+endY+'" r="'+(focused?5:3.3)+'" fill="'+color+'" stroke="#0c1728" stroke-width="1.5"><title>'+simEscape(manager)+' · GW'+end.gw+': '+end.mid.toFixed(1)+' expected LP</title></circle>';
    });
    const legend=managers.map(m=>{
        const end=all[m][all[m].length-1].mid;
        return '<span><i style="background:'+simColor(m)+'"></i>'+simEscape(m)+' <b>'+end.toFixed(1)+'</b></span>';
    }).join('');
    return '<svg role="img" aria-label="Projected league-points trajectories for '+managers.length+' selected McDraft managers" viewBox="0 0 '+w+' '+h+'">'+grid+draw+labels+'</svg>'+
      '<div class="sim-trajectory-key">'+legend+'</div>'+
      (hasBand?'<p class="sim-helper-note">Shaded range: '+simEscape(focus)+' · 10th–90th percentile sampled league points.</p>':'');
}

function simRenderResults(){
    const page=document.getElementById('page-season-simulator');
    if(!page||!page.classList.contains('active'))return;
    const outcomes=seasonSimState.outcomes, result=outcomes[seasonSimState.selected]||outcomes.baseline;
    const baseline=outcomes.baseline;
    const focus=seasonSimState.focus||SEASON_SIMULATOR_DATA.managers?.[0];
    const metrics=document.getElementById('sim-selected-metrics');
    const dist=document.getElementById('sim-position-chart');
    const trajectory=document.getElementById('sim-trajectory-chart');
    const description=document.getElementById('sim-distribution-desc');
    const compare=document.getElementById('sim-compare-table');
    const league=document.getElementById('sim-league-table');
    const compareCount=document.getElementById('sim-compare-count');
    if(seasonSimState.noFixtures){
        const message='<div class="sim-empty">No remaining fixtures were returned by the Draft schedule. All completed results remain in the existing league table; there is nothing to simulate.</div>';
        [metrics,dist,trajectory,compare,league].forEach(el=>{if(el)el.innerHTML=message;});
        return;
    }
    if(!result){
        const message='<div class="sim-loading">Running the Monte Carlo model… Results appear as each scenario finishes.</div>';
        [metrics,dist,trajectory,compare,league].forEach(el=>{if(el)el.innerHTML=message;});
        return;
    }
    const row=result.teams.find(t=>t.manager===focus),baseRow=baseline?.teams.find(t=>t.manager===focus);
    const fmtPointDelta=baseRow ? simFmtDelta(row.expected_lp-baseRow.expected_lp,1)+' vs baseline':'Baseline scenario';
    if(metrics&&row){
        const cards=[
            ['Expected league points',row.expected_lp.toFixed(1),fmtPointDelta],
            ['Simulated 1st place',simPct(row.champion_pct),baseRow?simFmtDelta(row.champion_pct-baseRow.champion_pct)+' pp vs baseline':'All simulations'],
            ['Simulated top 3',simPct(row.top3_pct),baseRow?simFmtDelta(row.top3_pct-baseRow.top3_pct)+' pp vs baseline':'All simulations'],
            ['Median finish','#'+simRank(row.median_finish),'80% range #'+simRank(row.finish_p10)+'–#'+simRank(row.finish_p90)],
            ['Simulated last place',simPct(row.wooden_pct),'Modelled finishing-position frequency']
        ];
        metrics.innerHTML=cards.map(c=>'<div class="sim-metric"><span class="label">'+simEscape(c[0])+'</span><strong class="value">'+simEscape(c[1])+'</strong><span class="delta">'+simEscape(c[2])+'</span></div>').join('');
    }
    if(dist)dist.innerHTML=simDistributionHTML(result,baseline,focus);
    if(trajectory)trajectory.innerHTML=simTrajectoryHTML(result,baseline,focus);
    if(result.effects)simRenderCustomEffects(result);
    if(description)description.textContent=focus+' · '+result.label+' · based on '+result.runs.toLocaleString()+' sampled seasons.';
    if(compare){
        const rows=simAllScenarios().filter(s=>outcomes[s.id]).map(s=>{
            const r=outcomes[s.id].teams.find(t=>t.manager===focus),delta=baseRow?r.expected_lp-baseRow.expected_lp:0;
            return '<tr class="'+(seasonSimState.selected===s.id?'selected':'')+'"><td><button type="button" class="sim-scenario-chip'+(seasonSimState.selected===s.id?' active':'')+'" onclick="selectSeasonScenario(\''+s.id+'\')"><span class="sim-scenario-name">'+simEscape(s.label)+'</span><span class="sim-subtext">'+simEscape(s.description)+'</span></button></td>'+
              '<td>'+r.expected_lp.toFixed(1)+'</td><td>'+simFmtDelta(delta)+'</td><td>'+simPct(r.champion_pct)+'</td><td>'+simPct(r.top3_pct)+'</td><td>'+simPct(r.wooden_pct)+'</td><td>#'+simRank(r.finish_p10)+'–#'+simRank(r.finish_p90)+'</td></tr>';
        });
        compare.innerHTML='<table class="sim-table"><thead><tr><th>Scenario</th><th>Exp. LP</th><th>Δ LP</th><th>1st</th><th>Top 3</th><th>Last</th><th>80% finish range</th></tr></thead><tbody>'+rows.join('')+'</tbody></table>';
    }
    if(compareCount)compareCount.textContent=Object.keys(outcomes).length+' / '+(simAllScenarios().length-(!seasonSimState.customActions.length?1:0))+' scenarios completed';
    if(league){
        const rows=result.teams.slice().sort((a,b)=>b.expected_lp-a.expected_lp||b.expected_pf-a.expected_pf||a.manager.localeCompare(b.manager));
        let head='<tr><th>Manager</th><th>Current LP</th><th>Expected LP</th><th>Expected PF</th><th>80% finish range</th><th>1st</th><th>Top 3</th>';
        for(let i=1;i<=result.teams.length;i++)head+='<th>#'+i+'</th>';
        head+='</tr>';
        let body='';
        rows.forEach(t=>{
            const rgb=simRgb(simColor(t.manager));
            body+='<tr'+(t.manager===focus?' class="selected"':'')+'><td><span class="sim-manager-name"><i style="background:'+simColor(t.manager)+'"></i>'+simEscape(t.manager)+'</span></td>'+
              '<td>'+t.current_lp.toFixed(0)+'</td><td><b>'+t.expected_lp.toFixed(1)+'</b></td><td>'+t.expected_pf.toFixed(0)+'</td>'+
              '<td>#'+simRank(t.finish_p10)+'–#'+simRank(t.finish_p90)+'</td><td>'+simPct(t.champion_pct)+'</td><td>'+simPct(t.top3_pct)+'</td>';
            t.positions_pct.forEach((pct,i)=>{
                const alpha=Math.max(.07,Math.min(.62,.07+pct/100*.75));
                const bg='rgba('+rgb.join(',')+','+alpha.toFixed(3)+')';
                body+='<td class="sim-heat" style="background:'+bg+'"><span title="#'+(i+1)+': '+simPct(pct)+'">'+(pct>=.1?pct.toFixed(0)+'%':'·')+'</span></td>';
            });
            body+='</tr>';
        });
        league.innerHTML='<table class="sim-table"><thead>'+head+'</thead><tbody>'+body+'</tbody></table>';
    }
}


function showPage(
    pageName
) {

    pages.forEach(
        function(page) {

            page.classList.remove(
                "active"
            );

        }
    );


    navButtons.forEach(
        function(button) {

            button.classList.remove(
                "active"
            );

        }
    );


    const selectedPage =
        document.getElementById(
            "page-" + pageName
        );


    const selectedButton =
        document.querySelector(
            '[data-page="' +
            pageName +
            '"]'
        );


    if (selectedPage) {

        selectedPage.classList.add(
            "active"
        );

    }


    if (selectedButton) {

        selectedButton.classList.add(
            "active"
        );

    }


    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

    /* Hidden Plotly charts can initially calculate a zero width.
       Resize after making the page visible. */
    setTimeout(
        resizeCharts,
        50
    );

    if (pageName === "war-room") requestAnimationFrame(renderManagerWarRoom);
    if (pageName === "season-simulator") requestAnimationFrame(initSeasonSimulator);
    if (typeof mcdNavSync === "function") mcdNavSync(pageName);

}


/* ============================================================
   MOBILE TREND CHARTS
   (H2H League Points / League Position / Points Per Gameweek)

   These replace what used to be three dense Plotly line charts.
   Everything here is plain SVG + DOM, built to be legible and
   tappable on a phone: a manager chip picker instead of a tiny
   legend, thick lines, and a tap-a-gameweek readout panel instead
   of a hover-only tooltip.
   ============================================================ */

const TREND_DATA = {
    h2h: __CHART_H2H_DATA__,
    rank: __CHART_RANK_DATA__,
    scores: __CHART_SCORES_DATA__,
    cumulative: __CHART_CUMULATIVE_DATA__
};

const TREND_CONFIG = {
    h2h: { invert: true, fixedRange: null, deltaGood: "up" },
    rank: { invert: false, fixedRange: null, deltaGood: "down" },
    scores: { invert: true, fixedRange: null, deltaGood: "up" },
    cumulative: { invert: true, fixedRange: null, deltaGood: "up" }
};

const MANAGER_ORDER = __MANAGER_ORDER__;

const TREND_PALETTE = [
    "#38bdf8", "#f472b6", "#4ade80", "#facc15",
    "#a78bfa", "#fb923c", "#2dd4bf", "#f87171",
    "#818cf8", "#e879f9", "#84cc16", "#22d3ee",
    "#fbbf24", "#c084fc", "#34d399", "#fca5a5"
];

const MANAGER_COLORS = __MANAGER_COLORS__;
MANAGER_ORDER.forEach(function(manager, index) {
    if (!MANAGER_COLORS[manager]) MANAGER_COLORS[manager] = TREND_PALETTE[index % TREND_PALETTE.length];
});

const trendState = {};

function initTrendChart(key) {
    const defaultCount = Math.min(5, MANAGER_ORDER.length);
    trendState[key] = {
        visible: new Set(MANAGER_ORDER.slice(0, defaultCount)),
        selectedGw: null
    };
    renderTrendChips(key);
    renderTrendChart(key);
}

function setTrendPreset(key, preset) {
    const state = trendState[key];
    if (!state) return;

    if (preset === "top5") {
        state.visible = new Set(MANAGER_ORDER.slice(0, Math.min(5, MANAGER_ORDER.length)));
    } else if (preset === "all") {
        state.visible = new Set(MANAGER_ORDER);
    } else if (preset === "none") {
        state.visible = new Set();
    }

    renderTrendChips(key);
    renderTrendChart(key);
}

function toggleTrendManager(key, manager) {
    const state = trendState[key];
    if (!state) return;

    if (state.visible.has(manager)) {
        state.visible.delete(manager);
    } else {
        state.visible.add(manager);
    }

    renderTrendChips(key);
    renderTrendChart(key);
}

function renderTrendChips(key) {
    const container = document.getElementById("chips-" + key);
    if (!container) return;

    const state = trendState[key];
    container.innerHTML = "";

    const presets = [
        ["Top 5", "top5"],
        ["All", "all"],
        ["None", "none"]
    ];

    presets.forEach(function(pair) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "chart-chip-action";
        button.textContent = pair[0];
        button.addEventListener("click", function() {
            setTrendPreset(key, pair[1]);
        });
        container.appendChild(button);
    });

    MANAGER_ORDER.forEach(function(manager) {
        const active = state.visible.has(manager);
        const button = document.createElement("button");
        button.type = "button";
        button.className = "chart-chip" + (active ? " active" : "");
        button.style.setProperty("--chip-color", MANAGER_COLORS[manager]);
        button.textContent = manager;
        button.addEventListener("click", function() {
            toggleTrendManager(key, manager);
        });
        container.appendChild(button);
    });
}

function trendAllGameweeks(data) {
    const gwSet = new Set();
    Object.keys(data).forEach(function(manager) {
        data[manager].forEach(function(point) {
            gwSet.add(point[0]);
        });
    });
    return Array.from(gwSet).sort(function(a, b) { return a - b; });
}

function renderTrendChart(key) {
    const wrap = document.getElementById("chart-" + key);
    if (!wrap) return;

    const state = trendState[key];
    const config = TREND_CONFIG[key];
    const data = TREND_DATA[key];
    const gws = trendAllGameweeks(data);

    if (gws.length === 0) {
        wrap.innerHTML = '<div class="trend-chart-empty">No gameweeks completed yet.</div>';
        return;
    }

    const visibleManagers = MANAGER_ORDER.filter(function(manager) {
        return state.visible.has(manager) && data[manager] && data[manager].length;
    });

    if (state.selectedGw === null || gws.indexOf(state.selectedGw) === -1) {
        state.selectedGw = gws[gws.length - 1];
    }

    const width = 700;
    const height = 300;
    const padL = 34;
    const padR = 12;
    const padT = 12;
    const padB = 26;
    const plotW = width - padL - padR;
    const plotH = height - padT - padB;

    let yMin;
    let yMax;

    if (key === "rank") {
        yMin = 0.5;
        yMax = MANAGER_ORDER.length + 0.5;
    } else {
        let values = [];
        visibleManagers.forEach(function(manager) {
            data[manager].forEach(function(point) { values.push(point[1]); });
        });
        if (values.length === 0) values = [0, 1];
        yMin = Math.min.apply(null, values);
        yMax = Math.max.apply(null, values);
        if (yMin === yMax) { yMin -= 1; yMax += 1; }
        const yPad = (yMax - yMin) * 0.1;
        yMin -= yPad;
        yMax += yPad;
    }

    const xMin = gws[0];
    const xMax = gws[gws.length - 1];

    function xScale(gw) {
        if (xMax === xMin) return padL + plotW / 2;
        return padL + ((gw - xMin) / (xMax - xMin)) * plotW;
    }

    function yScale(value) {
        const t = (value - yMin) / (yMax - yMin);
        return config.invert ? padT + (1 - t) * plotH : padT + t * plotH;
    }

    // Gridlines: 4 horizontal reference lines.
    const gridCount = 4;
    let gridlines = "";
    for (let i = 0; i <= gridCount; i++) {
        const value = yMin + ((yMax - yMin) * i) / gridCount;
        const y = yScale(value).toFixed(1);
        const label = key === "rank" ? Math.round(value) : Math.round(value);
        gridlines += '<line class="trend-chart-gridline" x1="' + padL + '" x2="' + (width - padR) + '" y1="' + y + '" y2="' + y + '" />';
        gridlines += '<text class="trend-chart-axis-label" x="4" y="' + (Number(y) + 3.5) + '">' + label + '</text>';
    }

    // X-axis labels: sparse, always include first/last.
    const maxLabels = 6;
    const step = Math.max(1, Math.ceil(gws.length / maxLabels));
    let xLabels = "";
    gws.forEach(function(gw, index) {
        const isEdge = index === 0 || index === gws.length - 1;
        if (index % step === 0 || isEdge) {
            const x = xScale(gw).toFixed(1);
            xLabels += '<text class="trend-chart-axis-label" x="' + x + '" y="' + (height - 6) + '" text-anchor="middle">GW' + gw + '</text>';
        }
    });

    // Tap targets: one invisible band per gameweek covering the full
    // chart height, wide enough to comfortably hit with a thumb.
    let hitBands = "";
    const bandWidth = gws.length > 1 ? plotW / (gws.length - 1) : plotW;
    gws.forEach(function(gw) {
        const x = xScale(gw);
        const selected = gw === state.selectedGw;
        hitBands += '<rect class="trend-chart-hit-band' + (selected ? ' selected' : '') + '" data-gw="' + gw + '" x="' + (x - bandWidth / 2).toFixed(1) + '" y="' + padT + '" width="' + Math.max(bandWidth, 18).toFixed(1) + '" height="' + plotH + '" />';
        hitBands += '<rect class="trend-chart-hit" data-gw="' + gw + '" x="' + (x - bandWidth / 2).toFixed(1) + '" y="0" width="' + Math.max(bandWidth, 18).toFixed(1) + '" height="' + height + '" />';
    });

    // Lines + dots per visible manager.
    let lines = "";
    let endLabels = "";
    const showEndLabels = visibleManagers.length > 0 && visibleManagers.length <= 6;

    visibleManagers.forEach(function(manager) {
        const points = data[manager];
        const color = MANAGER_COLORS[manager];

        let d = "";
        points.forEach(function(point, index) {
            const x = xScale(point[0]).toFixed(1);
            const y = yScale(point[1]).toFixed(1);
            d += (index === 0 ? "M" : "L") + x + "," + y + " ";
        });

        lines += '<path class="trend-chart-line" d="' + d.trim() + '" stroke="' + color + '" />';

        points.forEach(function(point) {
            const isSelected = point[0] === state.selectedGw;
            const radius = isSelected ? 5.5 : 3;
            lines += '<circle class="trend-chart-dot" cx="' + xScale(point[0]).toFixed(1) + '" cy="' + yScale(point[1]).toFixed(1) + '" r="' + radius + '" fill="' + color + '" stroke="#111827" stroke-width="' + (isSelected ? 2 : 1) + '" />';
        });

        if (showEndLabels) {
            const last = points[points.length - 1];
            const lx = xScale(last[0]) + 6;
            const ly = yScale(last[1]) + 3.5;
            endLabels += '<text class="trend-chart-end-label" x="' + lx.toFixed(1) + '" y="' + ly.toFixed(1) + '" fill="' + color + '">' + manager.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") + '</text>';
        }
    });

    const svg = '<svg viewBox="0 0 ' + width + ' ' + height + '" preserveAspectRatio="xMidYMid meet">' +
        gridlines +
        hitBands +
        lines +
        endLabels +
        '</svg>';

    wrap.innerHTML = visibleManagers.length
        ? svg
        : '<div class="trend-chart-empty">No managers selected — tap a chip above to show a line.</div>' + svg;

    wrap.querySelectorAll(".trend-chart-hit").forEach(function(hit) {
        hit.addEventListener("click", function() {
            const gw = Number(hit.dataset.gw);
            state.selectedGw = gw;
            renderTrendChart(key);
            renderTrendReadout(key);
        });
    });

    renderTrendReadout(key);
}

function renderTrendReadout(key) {
    const container = document.getElementById("legend-" + key);
    if (!container) return;

    const state = trendState[key];
    const config = TREND_CONFIG[key];
    const data = TREND_DATA[key];
    const gw = state.selectedGw;

    const visibleManagers = MANAGER_ORDER.filter(function(manager) {
        return state.visible.has(manager) && data[manager] && data[manager].length;
    });

    if (gw === null || visibleManagers.length === 0) {
        container.innerHTML = '<div class="trend-readout"><div class="trend-readout-heading">No managers selected</div></div>';
        return;
    }

    const rows = [];

    visibleManagers.forEach(function(manager) {
        const points = data[manager];
        let current = null;
        let previous = null;

        for (let i = 0; i < points.length; i++) {
            if (points[i][0] === gw) {
                current = points[i][1];
                previous = i > 0 ? points[i - 1][1] : null;
                break;
            }
        }

        if (current === null) return;

        rows.push({ manager: manager, value: current, previous: previous });
    });

    rows.sort(function(a, b) {
        return key === "rank" ? a.value - b.value : b.value - a.value;
    });

    let html = '<div class="trend-readout">';
    html += '<div class="trend-readout-heading">Gameweek ' + gw + '</div>';

    rows.forEach(function(row) {
        const color = MANAGER_COLORS[row.manager];
        const safeName = row.manager.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

        let deltaHtml = '<span class="trend-readout-delta flat">—</span>';

        if (row.previous !== null && row.previous !== row.value) {
            const diff = row.value - row.previous;
            const improved = config.deltaGood === "up" ? diff > 0 : diff < 0;
            const arrow = (config.deltaGood === "up" ? diff > 0 : diff < 0) ? "▲" : "▼";
            const magnitude = Math.abs(diff);
            deltaHtml = '<span class="trend-readout-delta ' + (improved ? "up" : "down") + '">' + arrow + ' ' + magnitude + '</span>';
        }

        html += '<div class="trend-readout-row">' +
            '<span class="trend-readout-dot" style="background:' + color + '"></span>' +
            '<span class="trend-readout-name">' + safeName + '</span>' +
            deltaHtml +
            '<span class="trend-readout-value">' + row.value + '</span>' +
            '</div>';
    });

    html += '</div>';
    container.innerHTML = html;
}

function initAllTrendCharts() {
    ["h2h", "rank", "scores", "cumulative"].forEach(initTrendChart);

    window.addEventListener("resize", function() {
        // SVG scales via viewBox automatically; nothing to recompute.
    });
}


/* ============================================================
   MY TEAM — SQUAD BY GAMEWEEK + PERSONAL TREND CHARTS
   ============================================================ */

const MY_TEAM_HISTORY = __MY_TEAM_HISTORY_DATA__;
const MY_TEAM_POSITION_NEEDS = __MY_TEAM_POSITION_NEEDS__;
const FIVE_GW_PLANNER = __FIVE_GW_PLANNER__;
let plannerSelectedGW = null;
let plannerSelectedManager = null;

let myTeamSquadIndex = -1;
let myTeamSquadManager = null;

function currentMyTeamManager() {
    const select = document.getElementById("my-team-select");
    if (!select) return null;
    return MANAGER_ORDER[Number(select.value)] || null;
}


// Five-GW Squad Planner: precomputed using the same Python player projection
// and legal formation optimiser that feed season simulations.
function renderFiveGWPlanner(){
  const summary=document.getElementById('myteam-planner-summary');
  const chart=document.getElementById('myteam-planner-chart');
  const weekWrap=document.getElementById('myteam-planner-weeks');
  const upgrades=document.getElementById('myteam-planner-upgrades');
  if(!summary||!chart||!weekWrap||!upgrades)return;
  const manager=currentMyTeamManager(),plan=FIVE_GW_PLANNER[manager];
  if(!plan||!plan.weeks||!plan.weeks.length){
    summary.innerHTML='<div class="notice">No upcoming gameweeks or current roster data available yet.</div>';
    chart.innerHTML='';weekWrap.innerHTML='';upgrades.innerHTML='';return;
  }
  if(plannerSelectedManager!==manager||!plan.weeks.some(w=>w.gw===plannerSelectedGW)){
    plannerSelectedGW=plan.weeks[0].gw;plannerSelectedManager=manager;
  }
  const weeks=plan.weeks, max=Math.max(1,...weeks.map(w=>Number(w.xi)||0));
  summary.innerHTML='<div class="planner-stat-grid">'+
    '<div class="planner-stat"><small>Five-GW projected XI</small><strong>'+Number(plan.total).toFixed(1)+'</strong><span>points combined</span></div>'+
    '<div class="planner-stat"><small>Toughest squad week</small><strong>GW'+plan.worst_gw+'</strong><span>'+Number(weeks.find(w=>w.gw===plan.worst_gw)?.xi||0).toFixed(1)+' projected</span></div>'+
    '<div class="planner-stat"><small>Strongest squad week</small><strong>GW'+plan.best_gw+'</strong><span>'+Number(weeks.find(w=>w.gw===plan.best_gw)?.xi||0).toFixed(1)+' projected</span></div>'+'</div>'+
    (plan.warning?'<div class="notice">'+escapePlayerHTML(plan.warning)+'</div>':'');
  chart.innerHTML=weeks.map(w=>'<button type="button" class="planner-chart-week '+(w.gw===plannerSelectedGW?'active':'')+'" onclick="selectPlannerWeek('+w.gw+')" aria-pressed="'+(w.gw===plannerSelectedGW)+'" aria-label="Show GW'+w.gw+' projected squad"><span class="planner-chart-val">'+Number(w.xi).toFixed(1)+'</span><span class="planner-bar-area"><span class="planner-chart-bar" style="height:'+Math.max(5,Math.round(Number(w.xi||0)/max*126))+'px"></span></span><b>GW'+w.gw+'</b><small>'+escapePlayerHTML(w.opponent)+'</small></button>').join('');
  const week=weeks.find(w=>w.gw===plannerSelectedGW)||weeks[0];
  const fm=week.formation||'—';
  const posTotals=Object.entries(week.by_position||{}).map(([p,v])=>'<span>'+p+': '+Number(v).toFixed(1)+'</span>').join('');
  function plannerPlayerRow(p){
    const fixtures=(p.fixtures||[]).map(f=>'<span class="planner-fx diff-'+f.difficulty+'">'+escapePlayerHTML(f.opponent)+(f.home?' (H)':' (A)')+'</span>').join('')||'<span class="planner-fx planner-blank">Blank GW</span>';
    return '<div class="planner-player"><div><b>'+escapePlayerHTML(p.name)+'</b><small>'+escapePlayerHTML(p.position)+' · '+escapePlayerHTML(p.club)+'</small></div><div class="planner-player-fixtures">'+fixtures+'</div><strong>'+Number(p.projection).toFixed(1)+'</strong>'+(p.status!=='a'||p.availability<0.75?'<small class="planner-availability-warning" title="'+escapePlayerHTML(p.news||'Official FPL availability flag')+'">'+Math.round(Number(p.availability||0)*100)+'% available</small>':'')+'</div>';
  }
  weekWrap.innerHTML='<div class="planner-week-heading"><div><h3>GW'+week.gw+' · '+escapePlayerHTML(week.opponent)+'</h3><p class="card-description">Best '+fm+' · '+Number(week.xi).toFixed(1)+' XI points · '+Number(week.managed).toFixed(1)+' manager-adjusted estimate</p></div><div class="planner-week-flags">'+(week.blank_count?'<span class="badge">'+week.blank_count+' blanks</span>':'')+(week.double_count?'<span class="badge">'+week.double_count+' doubles</span>':'')+(week.flagged_count?'<span class="badge">'+week.flagged_count+' availability flags</span>':'')+'</div></div>'+
    '<div class="planner-pos-pills">'+posTotals+'</div>'+
    '<div class="planner-squad-columns"><div><h3>Projected XI</h3>'+(week.starters||[]).map(plannerPlayerRow).join('')+'</div><div><h3>Bench · '+Number(week.bench_cover).toFixed(1)+' projected pts</h3>'+(week.bench||[]).map(plannerPlayerRow).join('')+'</div></div>';
  upgrades.innerHTML=(plan.suggestions||[]).length?'<div class="trade-target-list">'+plan.suggestions.map(s=>'<div class="trade-target-row"><div><div class="trade-target-name">'+escapePlayerHTML(s.name)+' <span class="badge">'+s.position+'</span></div><div class="trade-target-meta">Potential swap for '+escapePlayerHTML(s.drop_name)+' · positional need '+s.need+'/100</div><div class="trade-target-reason">Projected improvement across five GWs with the best legal XI recalculated each week.</div>'+fixtureRunHTML(s.fixtures,true)+'</div><div class="trade-target-scores"><div class="trade-target-score"><span>Five-GW XI gain</span><b>+'+Number(s.gain).toFixed(1)+'</b></div></div><button type="button" class="results-button" onclick="openScoutFreeAgent('+s.id+')">View player →</button></div>').join('')+'</div>':'<div class="notice">No available same-position free agents project as a meaningful five-GW XI upgrade.</div>';
}
function selectPlannerWeek(gw){plannerSelectedGW=Number(gw);renderFiveGWPlanner();}

function renderMyTeamSquad() {
    const wrap = document.getElementById("myteam-squad-wrap");
    const gwDisplay = document.getElementById("myteam-squad-gw-display");
    const prevButton = document.getElementById("myteam-squad-prev");
    const nextButton = document.getElementById("myteam-squad-next");
    if (!wrap) return;

    const manager = currentMyTeamManager();
    const entries = (manager && MY_TEAM_HISTORY[manager]) || [];

    if (entries.length === 0) {
        wrap.innerHTML = '<div class="notice">No squad history captured yet.</div>';
        if (gwDisplay) gwDisplay.textContent = "—";
        if (prevButton) prevButton.disabled = true;
        if (nextButton) nextButton.disabled = true;
        return;
    }

    if (manager !== myTeamSquadManager || myTeamSquadIndex < 0 || myTeamSquadIndex >= entries.length) {
        myTeamSquadIndex = entries.length - 1;
        myTeamSquadManager = manager;
    }

    const entry = entries[myTeamSquadIndex];

    const starterRows = entry.starters.map(function(p) {
        let tag = "";
        if (p.is_captain) {
            tag = ' <span class="cap-badge">C</span>';
        } else if (p.is_vice_captain) {
            tag = ' <span class="cap-badge vc">VC</span>';
        }
        return '<div class="squad-row"><button type="button" class="squad-player-link" onclick="showSquadPlayerRadar(' + Number(p.id||0) + ')">' + escapePlayerHTML(p.name) + tag + ' ↗</button><b>' + p.points + '</b></div>';
    }).join("") || '<div class="muted">No starting XI captured.</div>';

    const benchRows = entry.bench.map(function(p) {
        return '<div class="squad-row bench-row"><button type="button" class="squad-player-link" onclick="showSquadPlayerRadar(' + Number(p.id||0) + ')">' + escapePlayerHTML(p.name) + ' ↗</button><b>' + p.points + '</b></div>';
    }).join("") || '<div class="muted">No bench captured.</div>';

    const statusText = entry.finished ? "" : " · In progress";
    const captainText = entry.captain ? (" · Captain: " + escapePlayerHTML(entry.captain)) : "";

    wrap.innerHTML =
        '<div class="squad-card">' +
        '<div class="squad-gw-heading">GW' + entry.gw + statusText + ' · <b>' + entry.points + ' pts</b>' + captainText + '</div>' +
        '<div class="squad-columns">' +
        '<div><div class="squad-heading">Starting XI</div>' + starterRows + '</div>' +
        '<div><div class="squad-heading">Bench</div>' + benchRows + '</div>' +
        '</div>' +
        '<div class="squad-player-radar-wrap" id="squad-player-radar-wrap"></div>' +
        '</div>';

    if (gwDisplay) gwDisplay.textContent = "GW" + entry.gw;
    if (prevButton) prevButton.disabled = myTeamSquadIndex === 0;
    if (nextButton) nextButton.disabled = myTeamSquadIndex === entries.length - 1;
}

function changeMyTeamSquadGw(direction) {
    const manager = currentMyTeamManager();
    const entries = (manager && MY_TEAM_HISTORY[manager]) || [];
    if (entries.length === 0) return;

    if (manager !== myTeamSquadManager || myTeamSquadIndex < 0) {
        myTeamSquadIndex = entries.length - 1;
        myTeamSquadManager = manager;
    }

    myTeamSquadIndex = Math.max(0, Math.min(entries.length - 1, myTeamSquadIndex + direction));
    renderMyTeamSquad();
}

function renderSingleLineChart(containerId, points, opts) {
    const wrap = document.getElementById(containerId);
    if (!wrap) return;

    if (!points || points.length === 0) {
        wrap.innerHTML = '<div class="trend-chart-empty">No data captured yet.</div>';
        return;
    }

    const width = 700;
    const height = 240;
    const padL = 34;
    const padR = 12;
    const padT = 12;
    const padB = 26;
    const plotW = width - padL - padR;
    const plotH = height - padT - padB;

    const gws = points.map(function(p) { return p[0]; });
    const xMin = Math.min.apply(null, gws);
    const xMax = Math.max.apply(null, gws);

    let yMin;
    let yMax;

    if (opts.rankMode) {
        yMin = 0.5;
        yMax = MANAGER_ORDER.length + 0.5;
    } else {
        const values = points.map(function(p) { return p[1]; });
        yMin = Math.min.apply(null, values);
        yMax = Math.max.apply(null, values);
        if (yMin === yMax) { yMin -= 1; yMax += 1; }
        const yPad = (yMax - yMin) * 0.15;
        yMin -= yPad;
        yMax += yPad;
    }

    function xScale(gw) {
        return xMax === xMin ? padL + plotW / 2 : padL + ((gw - xMin) / (xMax - xMin)) * plotW;
    }

    function yScale(value) {
        const t = (value - yMin) / (yMax - yMin);
        return opts.invert ? padT + (1 - t) * plotH : padT + t * plotH;
    }

    let gridlines = "";
    for (let i = 0; i <= 4; i++) {
        const value = yMin + ((yMax - yMin) * i) / 4;
        const y = yScale(value).toFixed(1);
        gridlines += '<line class="trend-chart-gridline" x1="' + padL + '" x2="' + (width - padR) + '" y1="' + y + '" y2="' + y + '" />';
        gridlines += '<text class="trend-chart-axis-label" x="4" y="' + (Number(y) + 3.5) + '">' + Math.round(value) + '</text>';
    }

    const step = Math.max(1, Math.ceil(gws.length / 6));
    let xLabels = "";
    gws.forEach(function(gw, index) {
        if (index % step === 0 || index === gws.length - 1) {
            xLabels += '<text class="trend-chart-axis-label" x="' + xScale(gw).toFixed(1) + '" y="' + (height - 6) + '" text-anchor="middle">GW' + gw + '</text>';
        }
    });

    let d = "";
    points.forEach(function(point, index) {
        const x = xScale(point[0]).toFixed(1);
        const y = yScale(point[1]).toFixed(1);
        d += (index === 0 ? "M" : "L") + x + "," + y + " ";
    });

    let dots = "";
    points.forEach(function(point) {
        dots += '<circle class="trend-chart-dot" cx="' + xScale(point[0]).toFixed(1) + '" cy="' + yScale(point[1]).toFixed(1) + '" r="3.5" fill="' + opts.color + '" stroke="#111827" stroke-width="1" />';
    });

    wrap.innerHTML = '<svg viewBox="0 0 ' + width + ' ' + height + '" preserveAspectRatio="xMidYMid meet">' +
        gridlines +
        xLabels +
        '<path class="trend-chart-line" d="' + d.trim() + '" stroke="' + opts.color + '" />' +
        dots +
        '</svg>';
}

function renderMyTeamStatsCharts() {
    const manager = currentMyTeamManager();
    if (!manager) return;

    const color = MANAGER_COLORS[manager] || "#38bdf8";

    renderSingleLineChart(
        "myteam-chart-scores",
        (TREND_DATA.scores && TREND_DATA.scores[manager]) || [],
        { invert: true, rankMode: false, color: color }
    );

    renderSingleLineChart(
        "myteam-chart-rank",
        (TREND_DATA.rank && TREND_DATA.rank[manager]) || [],
        { invert: false, rankMode: true, color: color }
    );
}


/* ============================================================
   TEAM OF THE WEEK
   ============================================================ */

const totwGameweeks =
    __TOTW_GAMEWEEKS__;


let totwIndex =
    totwGameweeks.length - 1;


function updateTOTW() {

    if (
        totwGameweeks.length === 0
    ) {

        return;

    }


    totwGameweeks.forEach(
        function(gw) {

            const slide =
                document.getElementById(
                    "totw-gw-" + gw
                );


            if (slide) {

                slide.style.display =
                    "none";

            }

        }
    );


    const selectedGW =
        totwGameweeks[
            totwIndex
        ];


    const selectedSlide =
        document.getElementById(
            "totw-gw-" + selectedGW
        );


    if (selectedSlide) {

        selectedSlide.style.display =
            "block";

    }


    const display =
        document.getElementById(
            "totw-gw-display"
        );


    if (display) {

        display.innerText =
            "GW" + selectedGW;

    }


    const prev =
        document.getElementById(
            "totw-prev"
        );


    const next =
        document.getElementById(
            "totw-next"
        );


    if (prev) {

        prev.disabled =
            totwIndex === 0;

    }


    if (next) {

        next.disabled =
            totwIndex ===
            totwGameweeks.length - 1;

    }

}


function changeTOTW(
    direction
) {

    const newIndex = resultsIndex + direction;

    if (
        newIndex < 0 ||
        newIndex >= resultsGameweeks.length
    ) {
        return;
    }

    resultsIndex = newIndex;
    updateResults();
}


/* ============================================================
   RESULTS
   ============================================================ */

const resultsGameweeks =
    __RESULT_GAMEWEEKS__;

const latestCompletedGameweek = totwGameweeks.length ? Math.max.apply(null, totwGameweeks) : null;
const dashboardDisplayGameweek = __DASHBOARD_DISPLAY_GW__;
const fixturePredictionGameweek = __FIXTURE_PREDICTION_GW__;
const dashboardGameState = "__DASHBOARD_GAME_STATE__";
const dashboardTargetGameweek = __DASHBOARD_TARGET_GW__;
let resultsIndex = resultsGameweeks.indexOf(dashboardDisplayGameweek);
if (resultsIndex < 0 && latestCompletedGameweek !== null) {
    resultsIndex = resultsGameweeks.indexOf(latestCompletedGameweek);
}
if (resultsIndex < 0) resultsIndex = Math.max(0, resultsGameweeks.length - 1);

function updateResults() {
    if (resultsGameweeks.length === 0) return;

    resultsGameweeks.forEach(function(gw) {
        const slide = document.getElementById("results-gw-" + gw);
        if (slide) slide.style.display = "none";
    });

    const selectedGW = resultsGameweeks[resultsIndex];
    const isCompleted = totwGameweeks.indexOf(selectedGW) !== -1;

    // Keep the real Premier League fixture panel locked to the same GW as the
    // McDraft results/preview/TOTW carousel. One gameweek selector drives all.
    const matchingPLIndex = PL_FIXTURE_GAMEWEEKS.indexOf(Number(selectedGW));
    if (matchingPLIndex !== -1) plFixtureIndex = matchingPLIndex;
    renderPLFixtureBrowser(selectedGW);

    const selectedSlide = document.getElementById("results-gw-" + selectedGW);
    if (selectedSlide) selectedSlide.style.display = "block";

    const display = document.getElementById("results-gw-display");
    if (display) display.innerText = "GW" + selectedGW;

    const summarySlides = document.querySelectorAll(".gw-summary-slide");
    summarySlides.forEach(function(slide) { slide.style.display = "none"; });
    const selectedSummary = document.getElementById("summary-gw-" + selectedGW);
    if (selectedSummary) selectedSummary.style.display = "block";

    const summaryCard = document.getElementById("gameweek-summary-card");
    if (summaryCard) summaryCard.style.display = isCompleted ? "block" : "none";

    const fixtureOddsCard = document.getElementById("fixture-odds-card");
    const upcomingFixtureOdds = document.getElementById("upcoming-fixture-odds");
    const liveFixtureOdds = document.getElementById("live-fixture-odds");
    const showLiveOdds = dashboardGameState === "live" && selectedGW === dashboardTargetGameweek;
    const showUpcomingOdds = selectedGW === fixturePredictionGameweek;
    if (fixtureOddsCard) fixtureOddsCard.style.display = (showLiveOdds || showUpcomingOdds) ? "block" : "none";
    if (liveFixtureOdds) liveFixtureOdds.style.display = showLiveOdds ? "block" : "none";
    if (upcomingFixtureOdds) upcomingFixtureOdds.style.display = showUpcomingOdds ? "block" : "none";

    const totwCard = document.getElementById("totw-card");
    if (totwCard) totwCard.style.display = isCompleted ? "block" : "none";

    if (isCompleted) {
        const matchingTOTWIndex = totwGameweeks.indexOf(selectedGW);
        if (matchingTOTWIndex !== -1) {
            totwIndex = matchingTOTWIndex;
            updateTOTW();
        }
    }

    const prev = document.getElementById("results-prev");
    const next = document.getElementById("results-next");
    if (prev) prev.disabled = resultsIndex === 0;
    if (next) next.disabled = resultsIndex === resultsGameweeks.length - 1;
}

function changeResults(direction) {
    const newIndex = resultsIndex + direction;
    if (newIndex < 0 || newIndex >= resultsGameweeks.length) return;
    resultsIndex = newIndex;
    updateResults();
}



/* Health analytics + responsive, dependency-free radar charts. */
const HEALTH_ANALYTICS = __HEALTH_ANALYTICS__;
const HEALTH_STATUSES = [
  { key:'i', label:'Injured', css:'injury' },
  { key:'s', label:'Suspended', css:'suspension' },
  { key:'d', label:'Doubtful', css:'doubt' },
  { key:'u', label:'Unavailable / ineligible', css:'unavailable' },
  { key:'a', label:'Available with news', css:'news' }
];
const HEALTH_VIEWS = {
  flags:   {title:'Flagged players', desc:'Current official FPL availability flags, stacked by status.', unit:'players'},
  risk:    {title:'Estimated next-GW points at risk', desc:'Modelled points difference between full availability and current FPL availability estimates. Not a forecast of confirmed absences.', unit:'pts'},
  new:     {title:'New and updated reports', desc:'New flags and changed FPL reports since the previous dashboard build. The first run creates a baseline.', unit:'reports'},
  removed: {title:'Removed from FPL player pool', desc:'Historical players no longer in the current FPL bootstrap. Grouped by LAST recorded PL club and LAST recorded fantasy owner; these are not confirmed transfers.', unit:'players'}
};
let healthSelectedView='flags';
let healthDetailSelection=null;
let healthRenderedGroups={pl:[],fantasy:[]};
function healthStatusBucket(s){return s==='n'?'u':(['i','s','d','u'].includes(s)?s:'a');}
function healthSetView(name){
  healthSelectedView=HEALTH_VIEWS[name]?name:'flags';
  healthDetailSelection=null;
  document.querySelectorAll('.health-metric-btn').forEach(btn=>{
    const active=btn.dataset.healthView===healthSelectedView;
    btn.classList.toggle('active',active);btn.setAttribute('aria-pressed',active?'true':'false');
  });
  const status=document.getElementById('health-status-filter');
  if(status)status.disabled=healthSelectedView==='removed';
  healthAnalyticsRender();
}
function healthFiltersChanged(){healthDetailSelection=null;healthAnalyticsRender();}
function healthFilteredRows(rows, opts){
  return (rows||[]).filter(p=>{
    const own=p.fantasy_team||'Former owner unknown';
    return (!opts.club||p.team===opts.club) && (!opts.owner||own===opts.owner)
      && (!opts.status||opts.removed||p.status===opts.status)
      && (!opts.query||[p.name,p.team,own,p.news||''].join(' ').toLowerCase().includes(opts.query));
  });
}
function healthSummarise(rows,dimension,view,allNames){
  const field=dimension==='pl'?'team':'fantasy_team';
  const groups=new Map((allNames||[]).map(name=>[name,{name,rows:[],count:0,risk:0,cats:{i:0,s:0,d:0,u:0,a:0},newRemoved:0}]));
  (rows||[]).forEach(p=>{
    const name=p[field]||(dimension==='pl'?'Former PL club unknown':'Former owner unknown');
    if(!groups.has(name))groups.set(name,{name,rows:[],count:0,risk:0,cats:{i:0,s:0,d:0,u:0,a:0},newRemoved:0});
    const g=groups.get(name);g.rows.push(p);g.count++;
    g.risk+=Math.max(0,Number(p.points_at_risk||0));
    g.cats[healthStatusBucket(p.status)]++;
    if(p.newly_removed)g.newRemoved++;
  });
  return Array.from(groups.values()).sort((a,b)=>{
    const av=view==='risk'?a.risk:a.count,bv=view==='risk'?b.risk:b.count;
    return bv-av||a.name.localeCompare(b.name);
  });
}
function healthMetricTotal(g,view){return view==='risk'?g.risk:g.count;}
function healthChartHTML(groups,dimension,view){
  const fantasy=dimension==='fantasy';
  const heading=fantasy?'McDraft fantasy teams':'Premier League clubs';
  const max=Math.max(1,...groups.map(g=>healthMetricTotal(g,view)));
  const total=groups.reduce((sum,g)=>sum+healthMetricTotal(g,view),0);
  const header='<div class="health-chart-heading"><div><h3>'+heading+'</h3><span>'+(fantasy?'Roster ownership':'Player\u2019s PL club')+'</span></div><strong>'+(view==='risk'?total.toFixed(1):total)+' '+(HEALTH_VIEWS[view].unit)+'</strong></div>';
  const bars=groups.map((g,index)=>{
    const metric=healthMetricTotal(g,view),pct=100*metric/max;
    let fill='';
    if(view==='flags'||view==='new'){
      const denom=Math.max(1,max);
      fill=HEALTH_STATUSES.map(st=>g.cats[st.key]?'<span class="health-stack-segment health-'+st.css+'" style="width:'+(100*g.cats[st.key]/denom).toFixed(2)+'%" title="'+escapePlayerHTML(st.label+': '+g.cats[st.key])+'"></span>':'').join('');
    }else if(view==='removed'){
      const newWidth=100*g.newRemoved/max;
      fill='<span class="health-stack-segment health-removed-old" style="width:'+(pct-newWidth).toFixed(2)+'%"></span><span class="health-stack-segment health-removed-new" style="width:'+newWidth.toFixed(2)+'%"></span>';
    }else fill='<span class="health-stack-segment health-risk-fill" style="width:'+pct.toFixed(2)+'%"></span>';
    const n=view==='risk'?metric.toFixed(1):String(metric);
    return '<button type="button" class="health-chart-row" onclick="healthSelectGroup(\''+dimension+'\','+index+')" title="View '+escapePlayerHTML(g.name)+' players" aria-label="View '+escapePlayerHTML(g.name)+': '+n+' '+HEALTH_VIEWS[view].unit+'"><span class="health-chart-name">'+escapePlayerHTML(g.name)+'</span><span class="health-stack-track">'+fill+'</span><strong>'+n+'</strong></button>';
  }).join('');
  const legend=(view==='flags'||view==='new')?'<div class="health-legend">'+HEALTH_STATUSES.map(s=>'<span><i class="health-'+s.css+'"></i>'+s.label+'</span>').join('')+'</div>' :view==='removed'?'<div class="health-legend"><span><i class="health-removed-old"></i>Previously removed</span><span><i class="health-removed-new"></i>Newly removed</span></div>':'';
  const note=fantasy?'<p class="health-chart-note">Free agents are excluded here unless enabled above or explicitly filtered; they are always included in the PL-club totals.</p>':'';
  return '<section class="health-chart-card">'+header+legend+'<div class="health-chart-scroll">'+(bars||'<div class="notice">No teams match these filters.</div>')+'</div>'+note+'</section>';
}
function healthSelectGroup(dimension,index){
  const g=(healthRenderedGroups[dimension]||[])[index];if(!g)return;
  healthDetailSelection={dimension,name:g.name};
  healthAnalyticsRender();
  document.getElementById('health-drilldown')?.scrollIntoView({behavior:'smooth',block:'nearest'});
}
function healthDetailHTML(){
  if(!healthDetailSelection)return '';
  const {dimension,name}=healthDetailSelection;
  const g=(healthRenderedGroups[dimension]||[]).find(group=>group.name===name);
  if(!g)return '';
  const departed=healthSelectedView==='removed';
  const records=g.rows.slice().sort((a,b)=>Number(b.points_at_risk||0)-Number(a.points_at_risk||0)||a.name.localeCompare(b.name));
  const items=records.map(p=>{
    const own=departed?'Last recorded McDraft owner: '+(p.fantasy_team||'Unknown'):(p.fantasy_team||'Free Agent');
    const extra=departed?'Last recorded in GW'+p.last_seen_gw+'; departure unconfirmed.':healthSelectedView==='risk'?'Est. '+Number(p.points_at_risk||0).toFixed(1)+' next-GW pts at risk':p.news||p.change_type||'Official FPL status';
    return '<div class="health-drill-row"><div><b>'+escapePlayerHTML(p.name)+'</b><small>'+escapePlayerHTML([p.position||'',p.team||'',own].filter(Boolean).join(' · '))+'</small><p>'+escapePlayerHTML(extra)+'</p></div><div>'+(departed?'<span class="health-removal-pill">Removed</span>':availabilityBadge(p))+'</div>'+(departed?'':'<button type="button" class="results-button" onclick="openScoutFreeAgent('+Number(p.id)+')">Player details →</button>')+'</div>';
  }).join('');
  return '<section class="health-drill-card" id="health-drilldown"><div class="health-drill-head"><div><h3>'+escapePlayerHTML(name)+'</h3><p>'+g.count+' '+HEALTH_VIEWS[healthSelectedView].unit+' · '+(dimension==='pl'?'Premier League club':'McDraft fantasy team')+'</p></div><button type="button" class="results-button" onclick="healthDetailSelection=null;healthAnalyticsRender()">Close details ×</button></div>'+(items||'<p class="notice">No matching players for this team and filters.</p>')+'</section>';
}
function healthAnalyticsRender(){
  const root=document.getElementById('analytics-health-root');if(!root)return;
  const opts={club:document.getElementById('health-club-filter')?.value||'',owner:document.getElementById('health-owner')?.value||'',status:document.getElementById('health-status-filter')?.value||'',query:(document.getElementById('health-query')?.value||'').trim().toLowerCase()};
  const view=healthSelectedView;
  const removed=view==='removed';opts.removed=removed;
  const flags=healthFilteredRows(HEALTH_ANALYTICS.flagged,opts),news=healthFilteredRows(HEALTH_ANALYTICS.new,opts);
  const oldRemoved=(HEALTH_ANALYTICS.removed||[]).map(p=>({...p,newly_removed:(HEALTH_ANALYTICS.new_removed||[]).some(n=>Number(n.id)===Number(p.id))}));
  const gone=healthFilteredRows(oldRemoved,opts);
  const rows=view==='new'?news:removed?gone:flags;
  const counts={inj:flags.filter(x=>x.status==='i').length,susp:flags.filter(x=>x.status==='s').length,doubt:flags.filter(x=>['d','u','n'].includes(x.status)).length,risk:flags.reduce((s,x)=>s+Number(x.points_at_risk||0),0),new:news.length,removed:gone.length};
  const kpis=[['Injured',counts.inj],['Suspended',counts.susp],['Doubtful / unavailable',counts.doubt],['Est. GW pts at risk',counts.risk.toFixed(1)],['New / updated',counts.new],['Historical removals',counts.removed]];
  const cards='<div class="health-kpis">'+kpis.map(([label,value])=>'<div class="health-kpi"><b>'+value+'</b><span>'+label+'</span></div>').join('')+'</div>';
  const clubNames=opts.club?[opts.club]:HEALTH_ANALYTICS.pl_clubs||[];
  // For removed identities, a historical club/manager can be absent from the current bootstrap.
  const ownerNames=opts.owner?[opts.owner]:(HEALTH_ANALYTICS.fantasy_teams||[]).slice();
  const includeFreeAgents=document.getElementById('health-free-agent-chart')?.checked||opts.owner==='Free Agent';
  if(includeFreeAgents&&!ownerNames.includes('Free Agent'))ownerNames.push('Free Agent');
  const pl=healthSummarise(rows,'pl',view,clubNames);
  const fantasyRows=includeFreeAgents?rows:rows.filter(p=>(p.fantasy_team||'Free Agent')!=='Free Agent');
  const fantasy=healthSummarise(fantasyRows,'fantasy',view,ownerNames);
  healthRenderedGroups={pl,fantasy};
  const sourceLabel=removed?'Last captured owner / club':'Current Draft ownership / PL club';
  const meta='<p class="health-data-note">'+rows.length+' matching records · '+sourceLabel+' · FPL data refreshed '+escapePlayerHTML(HEALTH_ANALYTICS.generated_at||'')+'.</p>';
  root.innerHTML=cards+'<div class="health-section-note"><h3>'+HEALTH_VIEWS[view].title+'</h3><p>'+HEALTH_VIEWS[view].desc+'</p></div><div class="health-chart-pair">'+healthChartHTML(pl,'pl',view)+healthChartHTML(fantasy,'fantasy',view)+'</div>'+meta+healthDetailHTML();
}
// Compare players to their own position so that GK and attackers share a fair 0–100 visual scale.
const RADAR_AXES=[['Output','points_per_game'],['Recent form','form'],['Goals','goals'],['Assists','assists'],['Defending','defensive'],['Bonus','bonus']];
function radarRaw(player,key){
 const minutes=Math.max(1,Number(player.minutes||0));
 if(key==='defensive')return 90*(Number(player.defensive_contributions||0)+Number(player.clean_sheets||0)*2+Number(player.saves||0)*0.15)/minutes;
 if(key==='goals'||key==='assists'||key==='bonus')return 90*Number(player[key]||0)/minutes;
 return Number(player[key]||0);
}
const RADAR_POOLS={};
function radarScores(player){
 const pos=player.position||'MID';
 if(!RADAR_POOLS[pos])RADAR_POOLS[pos]=playerSearchData.filter(p=>p.position===pos&&Number(p.minutes||0)>=90);
 return RADAR_AXES.map(([label,key])=>{
   const val=radarRaw(player,key);const sorted=RADAR_POOLS[pos].map(p=>radarRaw(p,key)).sort((a,b)=>a-b);
   if(!sorted.length)return 0;
   const rank=sorted.filter(v=>v<val).length+0.5*sorted.filter(v=>v===val).length;
   return Math.max(0,Math.min(100,Math.round(100*rank/sorted.length)));
 });
}
function radarSVG(scores,caption){
 const cx=170,cy=155,r=99,n=RADAR_AXES.length;
 const point=(i,factor)=>{const a=(i*2*Math.PI/n)-Math.PI/2;return [(cx+Math.cos(a)*r*factor).toFixed(1),(cy+Math.sin(a)*r*factor).toFixed(1)].join(',');};
 let svg='<svg class="performance-radar" viewBox="0 0 340 315" role="img" aria-label="'+escapePlayerHTML(caption||'Performance radar')+'">';
 [0.25,.5,.75,1].forEach(t=>svg+='<polygon points="'+RADAR_AXES.map((_,i)=>point(i,t)).join(' ')+'" class="radar-ring"/>');
 RADAR_AXES.forEach(([label],i)=>{const xy=point(i,1).split(',');let a=(i*2*Math.PI/n)-Math.PI/2;const lx=cx+Math.cos(a)*134,ly=cy+Math.sin(a)*119;svg+='<line x1="'+cx+'" y1="'+cy+'" x2="'+xy[0]+'" y2="'+xy[1]+'" class="radar-axis"/><text x="'+lx.toFixed(1)+'" y="'+(ly+4).toFixed(1)+'" text-anchor="middle" class="radar-label">'+escapePlayerHTML(label)+'</text>';});
 svg+='<polygon class="radar-area" points="'+scores.map((v,i)=>point(i,Math.max(0,Math.min(100,Number(v)||0))/100)).join(' ')+'"/>';
 scores.forEach((v,i)=>{const pt=point(i,Math.max(0,Math.min(100,Number(v)||0))/100).split(',');svg+='<circle class="radar-dot" cx="'+pt[0]+'" cy="'+pt[1]+'" r="3"><title>'+escapePlayerHTML(RADAR_AXES[i][0])+': '+Math.round(v)+'/100</title></circle>';});
 return svg+'</svg>';
}
function playerRadarHTML(player){
 if(!player)return '<div class="notice">Player data unavailable.</div>';
 if(Number(player.minutes||0)<90)return '<div class="notice">At least 90 PL minutes needed for reliable positional radar percentiles.</div>';
 const scores=radarScores(player);
 return '<div class="radar-layout">'+radarSVG(scores,player.name+' positional performance radar')+'<div class="radar-stats">'+RADAR_AXES.map(([name],i)=>'<span>'+name+'<b>'+scores[i]+'/100</b></span>').join('')+'</div></div><p class="card-description">Position-relative percentiles among active players with 90+ minutes. Goals, assists, defending and bonus are per 90; output and recent form use FPL PPG and form. These are descriptive comparisons, not skill ratings.</p>';
}
function showSquadPlayerRadar(playerId){
 const root=document.getElementById('squad-player-radar-wrap');if(!root)return;
 const player=playerSearchData.find(p=>Number(p.id)===Number(playerId));
 root.innerHTML='<h3>'+escapePlayerHTML(player?.name||'Player')+' · Performance profile</h3>'+playerRadarHTML(player);
 root.scrollIntoView({behavior:'smooth',block:'nearest'});
}
function renderMyTeamRadar(){
 const root=document.getElementById('myteam-radar');if(!root)return;
 const manager=currentMyTeamManager();const roster=playerSearchData.filter(p=>p.fantasy_team===manager);
 if(!roster.length){root.innerHTML='<div class="notice">No current roster found.</div>';return;}
 const eligible=roster.filter(p=>Number(p.minutes||0)>=90);
 if(!eligible.length){root.innerHTML='<div class="notice">No squad players have 90+ PL minutes yet.</div>';return;}
 const matrix=eligible.map(radarScores);const scores=RADAR_AXES.map((_,i)=>Math.round(matrix.reduce((n,row)=>n+row[i],0)/matrix.length));
 root.innerHTML='<div class="radar-layout">'+radarSVG(scores,manager+' squad performance radar')+'<div class="radar-stats">'+RADAR_AXES.map(([name],i)=>'<span>'+name+'<b>'+scores[i]+'/100</b></span>').join('')+'</div></div><p class="card-description">Mean position-relative percentile across '+eligible.length+' of '+roster.length+' current squad players with 90+ PL minutes. Switch managers above to compare profiles.</p>';
}

/* ============================================================
   PLAYER SEARCH
   ============================================================ */

const playerSearchData =
    __PLAYER_SEARCH_DATA__;
const PL_FIXTURE_BROWSER = __PL_FIXTURE_BROWSER__;
const CLUB_EXPLORER_DATA = __CLUB_EXPLORER_DATA__;

function clubExplorerRows(club){
    return (club.player_ids||[]).map(id=>playerSearchData.find(p=>Number(p.id)===Number(id))).filter(Boolean);
}
function clubPlayerCard(p){
    const team=p.fantasy_team||'Free Agent';
    return '<div class="trade-target-row"><div><div class="trade-target-name">'+escapePlayerHTML(p.name)+'</div><div class="trade-target-meta">'+escapePlayerHTML(p.position)+' · '+escapePlayerHTML(team)+'</div>'+fixtureRunHTML(p.next_fixtures,true)+'</div><div class="trade-target-scores"><div class="trade-target-score"><span>FPL pts</span><b>'+Number(p.total_points||0).toFixed(0)+'</b></div><div class="trade-target-score"><span>Projected season</span><b>'+Number(p.projected_season_points||0).toFixed(0)+'</b></div><div class="trade-target-score"><span>Value</span><b>'+Number(p.player_value||0).toFixed(0)+'</b></div></div></div>';
}
function clubFixturesHtml(fixtures,limit){
    const arr=limit ? (fixtures||[]).filter(f=>!f.finished).slice(0,limit) : (fixtures||[]);
    if(!arr.length)return '<div class="notice">No fixtures in this selection.</div>';
    return '<div class="future-fixtures-list">'+arr.map(f=>{
      const d=Number(f.difficulty||3), cls=Math.max(1,Math.min(5,Math.round(d)));
      return '<div class="future-fixture-row"><div class="future-fixture-team">GW'+f.gw+' · '+escapePlayerHTML(f.opponent)+' ('+(f.home?'H':'A')+')</div><div class="future-fixture-vs">'+(f.score||'vs')+'</div><div class="future-fixture-team right"><span class="fixture-chip fixture-diff-'+cls+'">'+d.toFixed(2)+'/5</span></div></div>';
    }).join('')+'</div>';
}
function renderClubExplorer(){
    const sel=document.getElementById('club-explorer-select');if(!sel)return;
    const club=CLUB_EXPLORER_DATA[sel.value];if(!club)return;
    const rows=clubExplorerRows(club).sort((a,b)=>Number(b.total_points||0)-Number(a.total_points||0));
    const free=rows.filter(p=>(p.fantasy_team||'Free Agent')==='Free Agent');
    const stat=document.getElementById('club-explorer-summary');
    if(stat)stat.innerHTML='<div class="club-stat-grid">'+[
      ['PL position','#'+club.position],['League points',club.pl_points],['Total FPL points',Number(club.fpl_points||0).toFixed(0)],
      ['Evolving club strength',club.fantasy_strength+'/100'],['Best-ten avg FPL rank','#'+Number(club.official_draft_rank||0).toFixed(0)],['Free agents',free.length]
    ].map(([k,v])=>'<div class="club-stat-card"><span>'+k+'</span><b>'+v+'</b></div>').join('')+'</div>';
    const overview=document.getElementById('club-overview-content');
    if(overview)overview.innerHTML='<p>The club has <b>'+rows.length+'</b> registered FPL players and <b>'+free.length+'</b> McDraft free agents. Total club FPL points include all players, whether selected in McDraft or not.</p><div class="trade-target-list">'+rows.slice(0,3).map(clubPlayerCard).join('')+'</div>';
    const fx=document.getElementById('club-overview-fixtures');if(fx)fx.innerHTML=clubFixturesHtml(club.fixtures,5);
    const gw=club.gw_points||[],max=Math.max(1,...gw.map(r=>Number(r.points||0)));
    const chart=document.getElementById('club-gw-chart');
    if(chart)chart.innerHTML='<div class="club-gw-bars">'+gw.map(r=>'<div class="club-gw-bar-wrap" title="GW'+r.gw+': '+r.points+' FPL points"><b>'+Number(r.points).toFixed(0)+'</b><div class="club-gw-bar" style="height:'+Math.max(4,Math.round(Number(r.points||0)/max*140))+'px"></div><span>'+r.gw+'</span></div>').join('')+'</div>';
    const table=document.getElementById('club-gw-table');if(table)table.innerHTML='<table><thead><tr><th>Club</th><th>GW</th><th>FPL points</th><th>Cumulative</th></tr></thead><tbody>'+gw.map((r,i)=>'<tr><td>'+escapePlayerHTML(club.short)+'</td><td>GW'+r.gw+'</td><td>'+Number(r.points).toFixed(0)+'</td><td>'+gw.slice(0,i+1).reduce((a,v)=>a+Number(v.points||0),0).toFixed(0)+'</td></tr>').join('')+'</tbody></table>';
    const top=document.getElementById('club-top-players');if(top)top.innerHTML='<div class="trade-target-list">'+rows.slice(0,25).map(clubPlayerCard).join('')+'</div>';
    const agents=document.getElementById('club-free-agents');if(agents)agents.innerHTML=free.length?'<div class="trade-target-list">'+free.map(clubPlayerCard).join('')+'</div>':'<div class="notice">No available free agents at this club.</div>';
    const all=document.getElementById('club-all-fixtures');if(all)all.innerHTML=clubFixturesHtml(club.fixtures,0);
}
function initialiseClubExplorer(){
  const sel=document.getElementById('club-explorer-select');if(!sel)return;
  const clubs=Object.values(CLUB_EXPLORER_DATA||{}).sort((a,b)=>a.name.localeCompare(b.name));
  sel.innerHTML=clubs.map(c=>'<option value="'+c.id+'">'+escapePlayerHTML(c.name)+'</option>').join('');
  if(clubs.length){sel.value=String(clubs[0].id);renderClubExplorer();}
}

// Scout: score every FPL player against the selected McDraft squad, not a shortlist.
function playerScoutSuitability(p,manager){
    const need=MY_TEAM_POSITION_NEEDS[manager]||{};
    const key=p.position==='GK'?'GKP':p.position;
    const positional=Number((need[key]||{}).need_score||50);
    const mine=(TRADE_SIMULATOR_DATA[manager]||[]).filter(r=>r.position===key);
    const baseline=mine.length ? mine.map(r=>Number(r.projection||0)).sort((a,b)=>a-b)[0] : 0;
    const projected=Number(p.next3_projected_points||0)/3;
    const quality=Math.max(0,Math.min(100,Number(p.player_value||0)));
    const run=Math.max(0,Math.min(100,50+(Number(p.fixture_run_score||1)-1)*150));
    const upgrade=Math.max(0,Math.min(100,50+(projected-baseline)*11));
    const owned=p.fantasy_team&&p.fantasy_team!=='Free Agent';
    const clubCount=mine.filter(r=>r.club===p.team).length;
    const concentration=clubCount>=3?9:clubCount===2?5:0;
    const self=p.fantasy_team===manager;
    // Squad need and comparative upside matter most; an unavailable own player is never suggested as an acquisition.
    const fit=Math.max(0,Math.min(100,0.31*positional+0.27*quality+0.24*upgrade+0.18*run-concentration-(self?30:0)));
    return {fit,need:positional,projected,baseline,owned,self};
}
function renderPlayerScout(){
    const wrap=document.getElementById('myteam-scout-results');if(!wrap)return;
    const manager=currentMyTeamManager();if(!manager)return;
    const q=(document.getElementById('scout-player-search')?.value||'').toLowerCase().trim();
    const pos=document.getElementById('scout-position')?.value||'';
    const ownership=document.getElementById('scout-ownership')?.value||'';
    const sort=document.getElementById('scout-sort')?.value||'fit';
    let rows=playerSearchData.filter(p=>(!q||p.name.toLowerCase().includes(q)||p.team.toLowerCase().includes(q))&&(!pos||p.position===pos));
    if(ownership==='free')rows=rows.filter(p=>(p.fantasy_team||'Free Agent')==='Free Agent');
    if(ownership==='owned')rows=rows.filter(p=>(p.fantasy_team||'Free Agent')!=='Free Agent');
    rows=rows.map(p=>({...p,scout:playerScoutSuitability(p,manager)}));
    rows.sort((a,b)=> sort==='points'?Number(b.total_points||0)-Number(a.total_points||0):sort==='value'?Number(b.player_value||0)-Number(a.player_value||0):sort==='projection'?Number(b.next3_projected_points||0)-Number(a.next3_projected_points||0):b.scout.fit-a.scout.fit);
    const count=document.getElementById('scout-count');if(count)count.textContent=rows.length+' matching players · top '+Math.min(60,rows.length)+' shown';
    wrap.innerHTML=rows.slice(0,60).map(p=>{
      const target=p.fantasy_team||'Free Agent';
      const own=p.scout.self;
      const action=own?'<span class="badge">Already in your squad</span>':target==='Free Agent'?'<button class="results-button" type="button" onclick="openScoutFreeAgent('+p.id+')">View free agent →</button>':'<button class="results-button" type="button" onclick="draftScoutTrade('+p.id+')">Draft trade offer →</button>';
      return '<div class="trade-target-row"><div><div class="trade-target-name">'+escapePlayerHTML(p.name)+'</div><div class="trade-target-meta">'+escapePlayerHTML(p.position)+' · '+escapePlayerHTML(p.team)+' · '+escapePlayerHTML(target)+'</div><div class="trade-target-reason">Need '+p.scout.need.toFixed(0)+'/100 · projected '+p.scout.projected.toFixed(1)+'/GW next 3 · replacement '+p.scout.baseline.toFixed(1)+'/GW</div>'+fixtureRunHTML(p.next_fixtures,true)+'</div><div class="trade-target-scores"><div class="trade-target-score"><span>Team fit</span><b>'+p.scout.fit.toFixed(0)+'</b></div><div class="trade-target-score"><span>Player value</span><b>'+Number(p.player_value||0).toFixed(0)+'</b></div><div class="trade-target-score"><span>Season proj.</span><b>'+Number(p.projected_season_points||0).toFixed(0)+'</b></div></div><div class="scout-action">'+action+'</div></div>';
    }).join('')||'<div class="notice">No players match the current filters.</div>';
}
function draftScoutTrade(playerId){
    const p=playerSearchData.find(r=>Number(r.id)===Number(playerId)),mine=currentMyTeamManager();
    if(!p||!mine||!p.fantasy_team||p.fantasy_team==='Free Agent'||p.fantasy_team===mine)return;
    showPage('transfers');
    const tradesBtn=document.querySelector('#page-transfers .transfer-subtab[onclick*="trades"]');
    if(tradesBtn)showTransferSubtab('trades',tradesBtn);
    const a=document.getElementById('trade-sim-manager-a'),b=document.getElementById('trade-sim-manager-b');
    if(!a||!b)return;
    a.value=mine;b.value=p.fantasy_team;
    renderTradeSimulator();
    const target=document.querySelector('.trade-sim-check[data-side="b"][data-id="'+Number(playerId)+'"]');
    if(target){target.checked=true;tradeSimSelectionChanged('b',p.position==='GK'?'GKP':p.position);}
    document.querySelector('.trade-simulator')?.scrollIntoView({behavior:'smooth',block:'start'});
}
function openScoutFreeAgent(playerId){
    const p=playerSearchData.find(r=>Number(r.id)===Number(playerId));if(!p)return;
    showPage('players');
    const btn=document.querySelector('#page-players .player-page-tab[onclick*="directory"]');
    if(btn)showPlayerSubtab('directory',btn);
    const search=document.getElementById('player-search');
    if(search){search.value=p.name;filterPlayers();}
    document.getElementById('player-search-results')?.scrollIntoView({behavior:'smooth',block:'start'});
}

const PL_FIXTURE_GAMEWEEKS = Object.keys(PL_FIXTURE_BROWSER || {}).map(Number).sort((a,b)=>a-b);
let plFixtureIndex = Math.max(0, PL_FIXTURE_GAMEWEEKS.indexOf(Number(dashboardDisplayGameweek || dashboardTargetGameweek || 1)));
if (plFixtureIndex < 0) plFixtureIndex = Math.max(0, PL_FIXTURE_GAMEWEEKS.length - 1);


function escapePlayerHTML(
    value
) {

    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );

}


function buildPlayerHistoryChart(historyRows) {

    const rows = (historyRows || []).filter(function(row) {
        return row && typeof row.gw !== "undefined";
    });

    if (rows.length === 0) {
        return '<div class="trend-chart-empty">No gameweek history captured yet.</div>';
    }

    const width = 700;
    const height = 200;
    const padL = 30;
    const padR = 10;
    const padT = 12;
    const padB = 26;
    const plotW = width - padL - padR;
    const plotH = height - padT - padB;

    const values = rows.map(function(row) { return row.points; });
    let yMax = Math.max.apply(null, values.concat([1]));
    let yMin = Math.min(0, Math.min.apply(null, values));
    if (yMax === yMin) yMax = yMin + 1;

    function yScale(value) {
        const t = (value - yMin) / (yMax - yMin);
        return padT + (1 - t) * plotH;
    }

    const zeroY = yScale(0);

    const gridCount = 3;
    let gridlines = "";
    for (let i = 0; i <= gridCount; i++) {
        const value = yMin + ((yMax - yMin) * i) / gridCount;
        const y = yScale(value).toFixed(1);
        gridlines += '<line class="trend-chart-gridline" x1="' + padL + '" x2="' + (width - padR) + '" y1="' + y + '" y2="' + y + '" />';
        gridlines += '<text class="trend-chart-axis-label" x="2" y="' + (Number(y) + 3.5) + '">' + Math.round(value) + '</text>';
    }

    const bandWidth = plotW / rows.length;
    const barWidth = Math.max(4, bandWidth * 0.55);

    let bars = "";
    let xLabels = "";
    const labelStep = Math.max(1, Math.ceil(rows.length / 8));

    rows.forEach(function(row, index) {
        const cx = padL + bandWidth * (index + 0.5);
        const barY = yScale(Math.max(row.points, 0));
        const barBottom = yScale(Math.min(row.points, 0));
        const barHeight = Math.max(1, barBottom - barY);

        bars += '<rect class="trend-chart-bar" x="' + (cx - barWidth / 2).toFixed(1) + '" y="' + barY.toFixed(1) + '" width="' + barWidth.toFixed(1) + '" height="' + barHeight.toFixed(1) + '">' +
            '<title>GW' + row.gw + ': ' + row.points + ' pts</title>' +
            '</rect>';

        if (index % labelStep === 0 || index === rows.length - 1) {
            xLabels += '<text class="trend-chart-axis-label" x="' + cx.toFixed(1) + '" y="' + (height - 6) + '" text-anchor="middle">GW' + row.gw + '</text>';
        }
    });

    return '<svg viewBox="0 0 ' + width + ' ' + height + '" preserveAspectRatio="xMidYMid meet">' +
        gridlines +
        '<line class="trend-chart-gridline" x1="' + padL + '" x2="' + (width - padR) + '" y1="' + zeroY.toFixed(1) + '" y2="' + zeroY.toFixed(1) + '" />' +
        bars +
        xLabels +
        '</svg>';
}


function fixtureRunHTML(fixtures, compact) {
    if (!Array.isArray(fixtures) || !fixtures.length) return '';
    const chips = fixtures.map(function(fx) {
        const diff = Math.max(1, Math.min(5, Number(fx.difficulty || 3)));
        const blank = !!fx.is_blank;
        const title = blank ? 'Blank gameweek' : ('Difficulty ' + diff + '/5' + (fx.is_double ? ' · Double GW' : ''));
        return '<span class="fixture-chip fixture-diff-' + diff + (blank ? ' fixture-blank' : '') + '" title="' + escapePlayerHTML(title) + '">' +
            '<span class="fixture-gw">GW' + Number(fx.gw || 0) + '</span>' +
            '<span>' + escapePlayerHTML(fx.label || '—') + '</span></span>';
    }).join('');
    return (compact ? '' : '<div class="fixture-run-heading">Next 3 Premier League fixtures</div>') + '<div class="fixture-run-strip">' + chips + '</div>';
}

function renderPlayerDirectoryCard(player) {
    const historyAvailable = Array.isArray(player.history) && player.history.length > 0;
    const owner = player.fantasy_team || "Free Agent";
    const ownerClass = owner === "Free Agent" ? "free-agent" : "";

    return '<div class="player-directory-card">' +
        '<div class="player-directory-main">' +
            '<div class="player-directory-name">' + escapePlayerHTML(player.name) + '</div>' +
            '<div class="player-rating-pill '+ratingTier(player.player_rating)+'" title="'+ratingTierLabel(player.player_rating)+' dynamic rating">' + Number(player.player_rating || 0).toFixed(0) + '<small>/100</small>' +
            (player.rating_change === null || player.rating_change === undefined ? '' :
             '<em class="' + (player.rating_change > 0 ? 'rating-up' : player.rating_change < 0 ? 'rating-down' : 'rating-flat') + '">' +
             (player.rating_change > 0 ? '+' : '') + Number(player.rating_change) + '</em>') + '</div>' +
            (player.availability && (player.availability.status!=='a'||player.availability.news) ? availabilityBadge(player):'') +
            '<div class="player-directory-meta">' +
                escapePlayerHTML(player.position) + ' · ' +
                escapePlayerHTML(player.team) + ' · ' +
                '<span class="' + ownerClass + '">' + escapePlayerHTML(owner) + '</span>' +
            '</div>' +
        '</div>' +
        '<div class="player-directory-stats">' +
            '<div><b>' + player.total_points + '</b><span>Pts</span></div>' +
            '<div><b>' + Number(player.form || 0).toFixed(1) + '</b><span>5GW</span></div>' +
            '<div><b>' + player.goals + '</b><span>G</span></div>' +
            '<div><b>' + player.assists + '</b><span>A</span></div>' +
        '</div>' +
        '<button class="player-details-button" onclick="togglePlayerDetails(' + player.id + ')">Details</button>' +
        '<div class="player-details" id="player-details-' + player.id + '" style="display:none;">' +
            '<div class="rating-lab-directory-link"><button type="button" onclick="openRatingLabForPlayer(' + player.id + ')">See rating history &amp; compare players →</button></div>' +
            '<div class="player-radar-panel"><h3>Player performance radar</h3>' + playerRadarHTML(player) + '</div>' +
            fixtureRunHTML(player.next_fixtures, false) +
            '<div class="player-stat-chips">' +
                '<span class="player-stat-chip"><b>' + player.total_points + '</b> Season points</span>' +
                '<span class="player-stat-chip"><b>' + Number(player.form || 0).toFixed(1) + '</b> 5 GW form</span>' +
                '<span class="player-stat-chip"><b>' + Number(player.points_per_game || 0).toFixed(1) + '</b> PPG</span>' +
                '<span class="player-stat-chip"><b>' + player.goals + '</b> Goals</span>' +
                '<span class="player-stat-chip"><b>' + player.assists + '</b> Assists</span>' +
                '<span class="player-stat-chip"><b>' + player.clean_sheets + '</b> Clean Sheets</span>' +
                '<span class="player-stat-chip"><b>' + player.minutes + '</b> Minutes</span>' +
                '<span class="player-stat-chip"><b>' + player.bonus + '</b> Bonus</span>' +
                '<span class="player-stat-chip"><b>' + Number(player.projected_season_points || 0).toFixed(0) + '</b> Projected season</span>' +
                '<span class="player-stat-chip"><b>' + Number(player.player_rating || 0).toFixed(0) + '</b> Dynamic rating /100</span>' +
                '<span class="player-stat-chip"><b>' + Number(player.club_form_score || 0).toFixed(0) + '</b> PL club last-5 form /100</span>' +
                '<span class="player-stat-chip"><b>' + Number(player.minutes_share || 0).toFixed(0) + '%</b> Game-time share</span>' +
                '<span class="player-stat-chip"><b>' + Number(player.matches_missed_estimate || 0) + '</b> PL starts missed</span>' +
                '<span class="player-stat-chip"><b>' + Number(player.player_value || 0).toFixed(0) + '</b> Separate trade value /100</span>' +
                '<div class="rating-breakdown"><b>Rating breakdown</b><p>3GW 23% · 5GW 10% · season 20% · draft 14% · PL club/form 13% · game-time/availability 11% · advanced stats 9%. Low-minute results shrink to the draft/club prior.</p>' +
                  Object.entries(player.rating_breakdown || {}).map(([label, value]) => '<div class="rating-factor"><span>' + escapePlayerHTML(label) + '</span><div class="rating-factor-track"><i style="width:' + Math.max(0,Math.min(100,Number(value))) + '%"></i></div><strong>' + Number(value).toFixed(0) + '</strong></div>').join('') + '</div>' +
                '<span class="player-stat-chip"><b>' + escapePlayerHTML(player.hot_cold_label || 'Neutral') + '</b> ' + Number(player.hot_cold_score || 0).toFixed(0) + ' heat</span>' +
                '<span class="player-stat-chip"><b>' + escapePlayerHTML(player.club_strength_label || 'Club') + '</b> ' + Number(player.club_strength || 0).toFixed(0) + '/100</span>' +
            '</div>' +
            (historyAvailable
                ? '<div class="player-history-chart-heading">Gameweek points & fixture difficulty</div>' +
                  '<div class="player-gw-chart-wrap trend-chart-svg-wrap">' +
                    buildPlayerHistoryChart(player.history) +
                  '</div>' +
                  '<div class="player-gw-table">' +
                    '<table><thead><tr><th>GW</th><th>Fixture</th><th>Difficulty</th><th>Manager(s)</th><th>Points</th></tr></thead><tbody>' +
                    player.history.map(function(row) {
                        const ownerNames = row.owners.length
                            ? row.owners.map(escapePlayerHTML).join(", ")
                            : "Not owned";
                        const fd = Number(row.fixture_difficulty || 3);
                        return '<tr><td>GW' + row.gw + '</td><td>' + escapePlayerHTML(row.fixture || '—') + '</td><td><span class="fixture-chip fixture-diff-' + Math.max(1,Math.min(5,Math.round(fd))) + '">' + fd.toFixed(1) + '/5</span></td><td>' + ownerNames + '</td><td><b>' + row.points + '</b></td></tr>';
                    }).join("") +
                    '</tbody></table></div>'
                : '<div class="notice">No draft ownership history has been captured for this player yet.</div>') +
        '</div>' +
    '</div>';
}



// v55 Waiver Intelligence. All changes are local browser exploration only.
const WI_DATA = __WAIVER_INTELLIGENCE_DATA__;
const wiState = {manager: null, ladder: [], assumedTaken: new Set()};
function wiSafe(value){return String(value??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}
function wiColour(m){return (typeof MANAGER_COLORS!=='undefined' && MANAGER_COLORS[m])||'#64748b';}
function wiHorizon(){return document.getElementById('wi-horizon')?.value||'3';}
function wiManager(){return document.getElementById('wi-manager')?.value||WI_DATA.league_order[0]||'';}
function wiAhead(){return WI_DATA.league_order.slice(0, WI_DATA.league_order.indexOf(wiManager()));}
function wiCandidate(id){return WI_DATA.candidates.find(p=>Number(p.id)===Number(id));}
function wiOwn(p){return (p.managers||{})[wiManager()]||{gains:{'1':0,'3':0,'5':0},drops:{},need:0};}
function wiAssessment(p){
  const before=wiAhead();
  const strong=[],possible=[];
  before.forEach(m=>{
    const info=p.managers[m];if(!info)return;
    if(info.interest==='Strong') strong.push({name:m,...info});
    else if(info.interest==='Possible') possible.push({name:m,...info});
  });
  const pressure=strong.length*2+possible.length*.8;
  const label=strong.length>=2||pressure>=3.6?'Crowded market':strong.length||possible.length>=2?'Possible competition':'Clearer route';
  const cls=label==='Crowded market'?'crowded':label==='Possible competition'?'possible':'clear';
  return {strong,possible,pressure,label,cls};
}
function wiScored(p){
  const own=wiOwn(p), gain=Math.max(0,Number(own.gains[wiHorizon()]||0));
  const risk=wiAssessment(p);
  const mode=document.getElementById('wi-strategy')?.value||'balanced';
  const score=mode==='value'?gain:mode==='realistic'?gain/(1+.40*risk.pressure):gain/(1+.18*risk.pressure);
  return {p,gain,own,risk,score};
}
function wiSortedCandidates(includeTaken=false){
  const pos=document.getElementById('wi-position')?.value||'';
  const search=(document.getElementById('wi-search')?.value||'').trim().toLowerCase();
  const hide=document.getElementById('wi-hide-risk')?.checked;
  const positives=document.getElementById('wi-positive-only')?.checked;
  return WI_DATA.candidates.map(wiScored).filter(r=>(!pos||r.p.position===pos) &&
     (!search||r.p.name.toLowerCase().includes(search)||r.p.club.toLowerCase().includes(search)) &&
     (includeTaken||!wiState.assumedTaken.has(r.p.id)) &&
     (!hide||r.risk.cls!=='crowded') && (!positives||r.gain>.05))
    .sort((a,b)=>b.score-a.score || b.gain-a.gain || a.p.name.localeCompare(b.p.name));
}
function initWaiverIntelligence(){
  const sel=document.getElementById('wi-manager');if(!sel)return;
  if(!sel.dataset.ready){
    sel.innerHTML=WI_DATA.league_order.map(m=>'<option value="'+wiSafe(m)+'">'+wiSafe(m)+'</option>').join('');
    const selected=(typeof currentMyTeamManager==='function'?currentMyTeamManager():null);
    if(WI_DATA.league_order.includes(selected))sel.value=selected;
    else if(WI_DATA.league_order.includes('Kamararama FC'))sel.value='Kamararama FC';
    sel.dataset.ready='1';
    wiState.manager=sel.value;
  }
  renderWaiverIntelligence();
}
function wiPriorityHTML(){
  const manager=wiManager();
  return WI_DATA.standings.map(row=>{
    const me=row.manager===manager;
    return '<div class="wi-queue-team '+(me?'mine':'')+'" style="--wi-team:'+wiColour(row.manager)+'"><strong>#'+row.priority+'</strong><span>'+wiSafe(row.manager)+'</span>'+(me?'<b>YOU</b>':'')+'</div>';
  }).join('');
}
function wiRenderTarget(r){
  const p=r.p,info=r.own,risk=r.risk;
  const drop=info.drops[wiHorizon()]||{};
  const flagged=p.availability!=='a';
  const competitors=[...risk.strong,...risk.possible];
  const competitorHtml=competitors.length?competitors.map(c=>
    '<div class="wi-contender" style="--wi-team:'+wiColour(c.name)+'"><span><i></i>'+wiSafe(c.name)+'</span><span>'+wiSafe(c.interest)+' · #'+c.pos_rank+' target for their '+wiSafe(p.position)+'s · +'+Number(c.gains[wiHorizon()]||0).toFixed(1)+' XI pts</span></div>'
  ).join(''):'<div class="muted">No earlier manager shows a clear same-position need for this player in our model. Their actual claims remain private.</div>';
  const taken=wiState.assumedTaken.has(p.id);
  const choice=wiState.ladder.some(i=>i.id===p.id);
  return '<article class="wi-target" style="--wi-team:'+wiColour(wiManager())+'">'+
    '<div class="wi-target-head"><div><strong>'+wiSafe(p.name)+'</strong><small>'+wiSafe(p.position)+' · '+wiSafe(p.club)+' · '+p.season_points+' pts this season</small></div><span class="wi-risk '+risk.cls+'">'+risk.label+'</span></div>'+
    '<div class="wi-target-metrics"><div><b class="wi-gain">+'+r.gain.toFixed(1)+'</b><small>Projected XI pts / '+wiHorizon()+' GW</small></div><div><b>'+p.next_projection.toFixed(1)+'</b><small>Next GW player projection</small></div><div><b>'+risk.strong.length+' / '+wiAhead().length+'</b><small>Earlier managers: strong interest</small></div></div>'+
    '<p class="wi-drop">Suggested claim: <b>'+wiSafe(p.name)+'</b> for <b>'+wiSafe(drop.name||'No legal drop')+'</b></p>'+
    '<p class="wi-fix">'+(p.fixtures.length?wiSafe(p.fixtures.join(' · ')):'Fixtures TBC')+(flagged?' · <span class="wi-flag">⚠ Availability flag: '+wiSafe(p.news||p.availability)+'</span>':'')+'</p>'+
    '<div class="wi-target-actions"><button class="relationship-reset" type="button" onclick="wiAddClaim('+p.id+')" '+(choice?'disabled':'')+'>'+(choice?'In claim ladder':'Add to claims')+'</button>'+
    '<button class="relationship-reset" type="button" onclick="wiToggleTaken('+p.id+')">'+(taken?'Restore':'Assume taken')+'</button>'+
    '<details><summary>Who might want him?</summary><div class="wi-contenders">'+competitorHtml+'</div></details></div></article>';
}
function renderWaiverIntelligence(){
  const host=document.getElementById('wi-target-list');if(!host)return;
  const manager=wiManager();
  if(wiState.manager!==manager){wiState.manager=manager;wiState.ladder=[];wiState.assumedTaken.clear();const status=document.getElementById('wi-ladder-notice');if(status)status.textContent='';}
  const priority=WI_DATA.league_order.indexOf(manager)+1;
  const ahead=wiAhead();
  document.getElementById('wi-priority').innerHTML=wiPriorityHTML();
  const assumedHost=document.getElementById('wi-assumed');
  if(assumedHost)assumedHost.innerHTML=wiState.assumedTaken.size?'<span>Assumed claimed:</span> '+Array.from(wiState.assumedTaken).map(id=>{const p=wiCandidate(id);return '<button type="button" onclick="wiToggleTaken('+id+')" aria-label="Restore target ' + wiSafe(p?.name||id) + '">'+wiSafe(p?.name||id)+' ×</button>';}).join('')+'<button type="button" onclick="wiRestoreAll()">Restore all</button>':'';
  const assessed=wiSortedCandidates();
  document.getElementById('wi-count').textContent=assessed.length+' targets shown';
  host.innerHTML=assessed.slice(0,60).map(wiRenderTarget).join('')||'<div class="notice">No current free agents meet these filters. Try another position, switch off upgrades-only or restore assumed-taken targets.</div>';
  const aheadHTML=ahead.length?ahead.map(m=>'<span style="--wi-team:'+wiColour(m)+'">'+wiSafe(m)+'</span>').join(''):'<b>Nobody — first in line</b>';
  const notice=document.getElementById('wi-notice');
  notice.innerHTML='<b>GW'+WI_DATA.target_gw+' provisional waiver order:</b> '+(WI_DATA.state==='live'?'Live scores are not a final league table. This queue can change at full time. ':WI_DATA.state==='upcoming'?'The upcoming GW may already have processed waivers; order shown is provisional for the following cycle. ':'Based on captured completed standings. ')+
    'Earlier claimants: '+aheadHTML+'. Rival interest is inferred from squad needs and projected improvement, never their private requests.';
  const crowded=WI_DATA.candidates.map(wiScored).filter(r=>r.gain>.1&&r.risk.cls==='crowded').length;
  const clearer=WI_DATA.candidates.map(wiScored).filter(r=>r.gain>.1&&r.risk.cls==='clear').length;
  document.getElementById('wi-stats').innerHTML=
    '<div><strong>#'+priority+' / '+WI_DATA.league_order.length+'</strong><span>Your current first-claim priority</span></div><div><strong>'+ahead.length+'</strong><span>Managers with earlier first claims</span></div><div><strong>'+crowded+'</strong><span>Upgrades with high modeled competition</span></div><div><strong>'+clearer+'</strong><span>Upgrades with clearer routes</span></div>';
  renderWiLadder();
}
function wiRestoreAll(){wiState.assumedTaken.clear();renderWaiverIntelligence();}
function wiToggleTaken(id){
  if(wiState.assumedTaken.has(id))wiState.assumedTaken.delete(id);else wiState.assumedTaken.add(id);
  renderWaiverIntelligence();
}
function wiAddClaim(id){
  id=Number(id);if(!wiCandidate(id)||wiState.ladder.some(x=>x.id===id))return;
  wiState.ladder.push({id});renderWaiverIntelligence();
}
function wiRemoveClaim(index){wiState.ladder.splice(index,1);renderWaiverIntelligence();}
function wiMoveClaim(index,direction){const target=index+direction;if(target<0||target>=wiState.ladder.length)return;
  const [item]=wiState.ladder.splice(index,1);wiState.ladder.splice(target,0,item);renderWaiverIntelligence();}
function clearWaiverLadder(){wiState.ladder=[];renderWaiverIntelligence();}
function autoWaiverLadder(){
  // First an ambitious high-upside claim, then two attainable alternatives,
  // preserving a legal like-for-like drop for each.
  const eligible=wiSortedCandidates().filter(r=>r.gain>.25&&!wiState.assumedTaken.has(r.p.id));
  if(!eligible.length){document.getElementById('wi-ladder-notice').textContent='No eligible upgrades for your current filters.';return;}
  const sortedValue=eligible.slice().sort((a,b)=>b.gain-a.gain);
  const result=[sortedValue[0]];
  const available=eligible.filter(r=>r.p.id!==result[0].p.id);
  // Prefer a credible alternative in the same position, then diversify.
  const backup=available.find(r=>r.p.position===result[0].p.position&&r.risk.cls!=='crowded');
  if(backup)result.push(backup);
  const used=new Set(result.map(r=>r.p.id));
  for(const r of available){
    if(result.length>=6)break;
    if(used.has(r.p.id))continue;
    const posCount=result.filter(x=>x.p.position===r.p.position).length;
    if(posCount>=2)continue;
    result.push(r);used.add(r.p.id);
  }
  wiState.ladder=result.map(r=>({id:r.p.id}));renderWaiverIntelligence();
  document.getElementById('wi-ladder-notice').textContent='Suggested order built. Review the outgoing player and claim priority in FPL Draft before submitting.';
}
function renderWiLadder(){
  const host=document.getElementById('wi-claim-ladder');if(!host)return;
  const selected=wiState.ladder.map(x=>wiCandidate(x.id)).filter(Boolean);
  if(!selected.length){host.innerHTML='<div class="wi-ladder-empty">No claims planned. Add players from the target board or generate a shortlist.</div>';return;}
  const usedDrops=new Map();
  host.innerHTML=selected.map((p,i)=>{
    const data=wiScored(p),drop=data.own.drops[wiHorizon()]||{};
    const duplicate=drop.id!==undefined&&usedDrops.has(drop.id);
    if(drop.id!==undefined&&!usedDrops.has(drop.id))usedDrops.set(drop.id,i+1);
    const warning=wiState.assumedTaken.has(p.id)?'<small class="wi-flag">You marked this target as taken.</small>':
       duplicate?'<small class="muted">Alternative to claim #'+usedDrops.get(drop.id)+' (same outgoing player)</small>':'';
    return '<div class="wi-ladder-row"><span class="wi-claim-num">'+(i+1)+'</span><div class="wi-claim-body"><b>'+wiSafe(p.name)+'</b><small>'+wiSafe(p.position)+' · +'+data.gain.toFixed(1)+' pts · '+data.risk.label+'</small><small>Drop '+wiSafe(drop.name||'—')+'</small>'+warning+'</div><div class="wi-claim-buttons">'+
       '<button type="button" onclick="wiMoveClaim('+i+',-1)" '+(i===0?'disabled':'')+' aria-label="Move claim up">↑</button>'+
       '<button type="button" onclick="wiMoveClaim('+i+',1)" '+(i===selected.length-1?'disabled':'')+' aria-label="Move claim down">↓</button>'+
       '<button type="button" onclick="wiRemoveClaim('+i+')" aria-label="Remove claim">×</button></div></div>';
  }).join('');
}
function wiLadderText(){
  return 'McDraft – proposed GW'+WI_DATA.target_gw+' waiver claims for '+wiManager()+' (first-claim priority #'+(WI_DATA.league_order.indexOf(wiManager())+1)+')\n'+
     wiState.ladder.map((item,i)=>{const p=wiCandidate(item.id),d=p?wiOwn(p).drops[wiHorizon()]:null;
        return (i+1)+'. CLAIM '+(p?p.name:'Unknown')+' / DROP '+(d?.name||'—');}).join('\n')+
     '\n\nDraft only: verify actual player availability and submit these claims in FPL Draft. Rival claims are private; no guaranteed success.';
}
async function copyWaiverLadder(){
  const notice=document.getElementById('wi-ladder-notice');
  if(!wiState.ladder.length){if(notice)notice.textContent='Add at least one claim first.';return;}
  const text=wiLadderText();
  try{if(navigator.clipboard?.writeText){await navigator.clipboard.writeText(text);if(notice)notice.textContent='Claim order copied.';return;}}
  catch(error){}
  const input=document.createElement('textarea');input.value=text;input.style.position='fixed';input.style.opacity='0';document.body.appendChild(input);input.select();
  const copied=document.execCommand('copy');input.remove();if(notice)notice.textContent=copied?'Claim order copied.':'Copy unavailable. Select and copy the following list manually: '+text;
}

function showTransferSubtab(name, button) {
 document.querySelectorAll('.transfer-subpanel').forEach(p=>p.classList.remove('active')); document.querySelectorAll('.transfer-subtab').forEach(t=>t.classList.remove('active')); const p=document.getElementById('transfer-subpanel-'+name); if(p)p.classList.add('active'); if(button)button.classList.add('active'); if(name==='intelligence') requestAnimationFrame(initWaiverIntelligence);
}
const TRADE_SIMULATOR_DATA = __TRADE_SIMULATOR_DATA__;
function renderTradeSimulator(){const a=document.getElementById('trade-sim-manager-a'),b=document.getElementById('trade-sim-manager-b'),ra=document.getElementById('trade-sim-roster-a'),rb=document.getElementById('trade-sim-roster-b');if(!a||!b||!ra||!rb)return;const ma=a.value,mb=b.value;document.getElementById('trade-sim-title-a').textContent=(ma||'Manager A')+' gives';document.getElementById('trade-sim-title-b').textContent=(mb||'Manager B')+' gives';if(!ma||!mb||ma===mb){ra.innerHTML=rb.innerHTML='<div class="notice">Choose two different managers.</div>';evaluateTradeSimulator();return;}ra.innerHTML=tradeSimRosterHtml(ma,'a');rb.innerHTML=tradeSimRosterHtml(mb,'b');evaluateTradeSimulator();}
function tradeSimRosterHtml(manager,side){return(TRADE_SIMULATOR_DATA[manager]||[]).map(p=>'<label class="trade-sim-player" data-side="'+side+'" data-position="'+p.position+'"><input type="checkbox" class="trade-sim-check" data-side="'+side+'" data-id="'+p.id+'" data-position="'+p.position+'" onchange="tradeSimSelectionChanged(\''+side+'\', \''+p.position+'\')"><span><b>'+escapePlayerHTML(p.name)+'</b><small><button type="button" class="trade-sim-position" onclick="tradeSimPositionClicked(event, \''+side+'\', \''+p.position+'\')">'+p.position+'</button> · '+escapePlayerHTML(p.club)+' · '+p.points+' pts · form '+Number(p.form).toFixed(1)+'</small></span><span class="trade-sim-player-value"><b>'+Number(p.value).toFixed(1)+'</b><span>value</span></span></label>').join('');}
function tradeSimSelectedCount(side){return document.querySelectorAll('.trade-sim-check[data-side="'+side+'"]:checked').length;}
function clearTradePositionHighlights(){document.querySelectorAll('.trade-sim-player.position-match').forEach(el=>el.classList.remove('position-match'));}
function tradeSelectedPositionCounts(side){
    const counts={GKP:0,DEF:0,MID:0,FWD:0};
    document.querySelectorAll('.trade-sim-check[data-side="'+side+'"]:checked').forEach(el=>{
        const pos=el.dataset.position;
        if(Object.prototype.hasOwnProperty.call(counts,pos)) counts[pos]++;
    });
    return counts;
}
function highlightTradeNeed(side, position){
    clearTradePositionHighlights();
    document.querySelectorAll('.trade-sim-player[data-side="'+side+'"][data-position="'+position+'"]').forEach(el=>el.classList.add('position-match'));
}
function refreshTradePositionHighlights(changedSide, changedPosition){
    clearTradePositionHighlights();
    const a=tradeSelectedPositionCounts('a'), b=tradeSelectedPositionCounts('b');
    const diff={GKP:a.GKP-b.GKP,DEF:a.DEF-b.DEF,MID:a.MID-b.MID,FWD:a.FWD-b.FWD};

    // First honour the position the user just changed. If one side now has an
    // unmatched player in that position, highlight exactly what the other side
    // needs to pair with it. This also makes deselection behave naturally.
    if(changedPosition && diff[changedPosition]!==0){
        highlightTradeNeed(diff[changedPosition]>0?'b':'a', changedPosition);
        return;
    }

    // If the position just changed is now balanced, move on to any other
    // outstanding positional mismatch. Once every selected position is paired,
    // highlighting disappears completely.
    const order=['GKP','DEF','MID','FWD'];
    for(const pos of order){
        if(diff[pos]!==0){
            highlightTradeNeed(diff[pos]>0?'b':'a', pos);
            return;
        }
    }
}
function tradeSimSelectionChanged(side, position){
    evaluateTradeSimulator();
    refreshTradePositionHighlights(side, position);
}
function tradeSimPositionClicked(event, side, position){
    if(event){event.preventDefault();event.stopPropagation();}
    // Position chips are a manual hint only. The next checkbox change will
    // immediately restore the true unmatched-position state.
    const opposingSide=side==='a'?'b':'a';
    highlightTradeNeed(opposingSide, position);
}
function selectedTradePlayers(side,manager){const ids=Array.from(document.querySelectorAll('.trade-sim-check[data-side="'+side+'"]:checked')).map(el=>Number(el.dataset.id));return(TRADE_SIMULATOR_DATA[manager]||[]).filter(p=>ids.includes(Number(p.id)));}
function tradePositionSignature(players){const c={GKP:0,DEF:0,MID:0,FWD:0};players.forEach(p=>{if(c[p.position]!==undefined)c[p.position]++});return c;} function samePositionSignature(a,b){return['GKP','DEF','MID','FWD'].every(pos=>a[pos]===b[pos]);}
function evaluateTradeSimulator(){
    const ae=document.getElementById('trade-sim-manager-a'),be=document.getElementById('trade-sim-manager-b'),result=document.getElementById('trade-sim-result'),score=document.getElementById('trade-sim-score');
    if(!ae||!be||!result||!score)return;
    const ma=ae.value,mb=be.value,pa=selectedTradePlayers('a',ma),pb=selectedTradePlayers('b',mb);
    score.innerHTML='<span>Fairness</span><b>—</b>';
    result.className='trade-sim-result notice';
    if(!ma||!mb||ma===mb||(!pa.length&&!pb.length)){
        result.innerHTML='Select managers and players to evaluate a deal.';
        return;
    }
    if(!samePositionSignature(tradePositionSignature(pa),tradePositionSignature(pb))){
        result.className='trade-sim-result notice invalid';
        result.innerHTML='<b>Position mismatch.</b> Each side must give the same positional combination. DEF + MID can swap for DEF + MID; DEF + MID cannot swap for MID + FWD.';
        return;
    }
    if(pa.length!==pb.length||pa.length===0){
        result.className='trade-sim-result notice invalid';
        result.innerHTML='<b>Incomplete deal.</b> Select the same number of players on each side.';
        return;
    }
    const sums=ps=>ps.reduce((o,p)=>{
        o.value+=Number(p.value||0);o.points+=Number(p.points||0);o.form+=Number(p.form||0);o.proj+=Number(p.projection||0);o.importance+=Number(p.importance||0);o.draft+=Number(p.draft_rank||151);return o;
    },{value:0,points:0,form:0,proj:0,importance:0,draft:0});
    const sa=sums(pa),sb=sums(pb),avg=(sa.value+sb.value)/2||1,gap=Math.abs(sa.value-sb.value),fair=Math.max(0,Math.min(100,100-gap/avg*100));
    const lean=sa.value>sb.value+2?mb+' receives more model value':(sb.value>sa.value+2?ma+' receives more model value':'Model sees this as essentially even');
    score.innerHTML='<span>Fairness</span><b>'+fair.toFixed(0)+'/100</b>';

    const avgA=sa.value/pa.length,avgB=sb.value/pb.length;
    const avgDraftA=sa.draft/pa.length,avgDraftB=sb.draft/pb.length;
    const pick=arr=>arr[Math.floor(Math.random()*arr.length)];
    const fmtManager=x=>escapePlayerHTML(x);
    const reasons=[];

    const fairnessPhrases={
      elite:[
        'This is about as close to a model-approved handshake as you are going to get.',
        'The numbers have stared at this deal for a while and basically shrugged: very even.',
        'Neither side is obviously nicking the silverware here — the packages are extremely close.',
        'Model value is almost dead level. This one passes the pub-test surprisingly comfortably.',
        'There is very little daylight between the two packages on blended value.',
        'This is the statistical equivalent of splitting the bill down the middle.',
        'On paper, this is a properly balanced exchange rather than daylight robbery.',
        'The calculator is struggling to pick a side, which is usually a decent sign for a trade.'
      ],
      good:[
        'The deal is broadly balanced, although one side has a modest edge.',
        'There is a lean here, but not enough to make the proposal ridiculous.',
        'This sits in the negotiable zone: close enough that team needs could easily outweigh the raw gap.',
        'The values are not identical, but this is still well within sensible trade territory.',
        'One package is a touch richer, though not by enough to kill the conversation.',
        'This looks more like a genuine football trade than a hostage negotiation.',
        'There is a detectable advantage to one side, but the deal remains defensible.',
        'Close-ish rather than perfectly even — exactly the sort of trade where preference matters.'
      ],
      middling:[
        'There is a noticeable value gap, so the weaker side would probably want a sweetener.',
        'The numbers are beginning to squint at this one. It is possible, but somebody is conceding value.',
        'This needs a reason beyond raw value — squad fit, fixture preference or an extra asset could get it there.',
        'The calculator sees enough imbalance that the short side should probably ask for more.',
        'Not outrageous, but definitely not one you accept without reading the small print.',
        'There is a meaningful gap between the packages; team needs would have to do some heavy lifting.',
        'This is drifting from even trade into persuasion-required territory.',
        'One manager is paying a premium here. Whether that is sensible depends on what problem the deal solves.'
      ],
      ugly:[
        'The model sees a substantial imbalance between the two packages.',
        'This currently looks less like a trade and more like somebody has left their phone unlocked.',
        'There is a fairly heroic value gap here. The weaker side should be asking awkward questions.',
        'The calculator has raised an eyebrow. Then the other eyebrow. This is heavily tilted.',
        'On the current numbers, one side is giving away considerably more than it receives.',
        'This is a long way from neutral value and probably needs another player or a rethink.',
        'The packages are operating in different postcodes on model value.',
        'Unless there is a very specific squad need involved, the short side is taking a kicking here.'
      ]
    };
    if(fair>=90) reasons.push(pick(fairnessPhrases.elite));
    else if(fair>=75) reasons.push(pick(fairnessPhrases.good));
    else if(fair>=55) reasons.push(pick(fairnessPhrases.middling));
    else reasons.push(pick(fairnessPhrases.ugly));

    if(Math.abs(sa.form-sb.form)>=1.5){
      const who=sa.form>sb.form?ma:mb;
      reasons.push(pick([
        who+' is surrendering the hotter recent-form package.',
        'Recent form leans toward the assets being sent by '+who+'.',
        who+' would be parting with more short-term momentum.',
        'On the last few gameweeks, '+who+' is giving up the livelier set of players.',
        who+' is paying more of the current-form premium.',
        'The hot-hand side of this deal belongs to the players leaving '+who+'.'
      ]));
    }
    if(Math.abs(sa.proj-sb.proj)>=1.0){
      const who=sa.proj>sb.proj?ma:mb;
      reasons.push(pick([
        who+' is giving up more projected weekly output.',
        'The forward-looking projection favours the package leaving '+who+'.',
        who+' is sacrificing the stronger near-term forecast.',
        'Projected points put more weight on the assets being moved by '+who+'.',
        'If the model is right about the next few weeks, '+who+' is sending away the better scoring package.',
        'The projection engine would rather own the group currently sitting with '+who+'.'
      ]));
    }
    if(Math.abs(sa.points-sb.points)>=8){
      const who=sa.points>sb.points?ma:mb;
      reasons.push(pick([
        who+' is surrendering more proven season production.',
        'The season-to-date points are stronger on the '+who+' side of the outgoing package.',
        who+' is giving away the larger body of banked evidence.',
        'Raw season scoring favours the players currently owned by '+who+'.',
        who+' is putting more established points on the table.',
        'If you value what has already happened, the outgoing '+who+' package has the edge.'
      ]));
    }
    if(Math.abs(sa.importance-sb.importance)>=8){
      const who=sa.importance>sb.importance?ma:mb;
      reasons.push(pick([
        who+' is giving up players who matter more to their current squad structure.',
        'Squad importance makes this more painful for '+who+' than the headline values alone suggest.',
        who+' is being asked to move more central pieces of their current XI.',
        'The assets leaving '+who+' carry more internal value to their present squad.',
        who+' would be breaking up a more important chunk of their team.',
        'Current-owner dependence says '+who+' feels this loss more sharply.'
      ]));
    }
    if(Math.abs(avgDraftA-avgDraftB)>=15){
      const who=avgDraftA<avgDraftB?ma:mb;
      reasons.push(pick([
        who+' is giving up the stronger blended draft pedigree.',
        'Draft-night expectations were materially higher for the package leaving '+who+'.',
        who+' is parting with the assets McDraft valued more highly before the season.',
        'Original draft capital favours the players being sent by '+who+'.',
        'On blended pre-season pedigree, '+who+' is contributing the more expensive package.',
        'The old draft board still gives the '+who+' side of the outgoing deal more cachet.'
      ]));
    }
    if(Math.abs(avgA-avgB)<2) reasons.push(pick([
      'Average asset quality is almost identical once the package sizes are normalised.',
      'On a per-player basis, there is barely anything between these groups.',
      'Strip away the names and the average model value per asset is remarkably similar.',
      'The individual-player value averages are basically neck and neck.',
      'Per head, these packages are extremely close in model value.',
      'The average player coming back is worth almost exactly what the average player going out is worth.'
    ]));

    const acceptA=[]; const acceptB=[];
    if(sb.form>sa.form+0.75) acceptA.push(pick(['gets the hotter recent form','buys more short-term momentum','lands the stronger recent performers','improves current form']));
    if(sb.proj>sa.proj+0.5) acceptA.push(pick(['raises projected weekly output','improves the near-term forecast','adds more projected points','wins on forward projection']));
    if(sb.points>sa.points+5) acceptA.push(pick(['brings in more proven season points','adds more banked production','gets the stronger season-to-date output','trades into the better established scoring record']));
    if(sb.importance<sa.importance-5) acceptA.push(pick(['can exchange highly important pieces for assets the other side relies on less','turns heavily-relied-upon assets into a less structurally costly package','may reduce dependence on a small core','gets comparable value without inheriting the same owner-dependence']));
    if(avgDraftB<avgDraftA-10) acceptA.push(pick(['upgrades original draft pedigree','buys back into stronger blended pre-season pedigree','receives the more highly drafted package','improves draft-capital quality']));

    if(sa.form>sb.form+0.75) acceptB.push(pick(['gets the hotter recent form','buys more short-term momentum','lands the stronger recent performers','improves current form']));
    if(sa.proj>sb.proj+0.5) acceptB.push(pick(['raises projected weekly output','improves the near-term forecast','adds more projected points','wins on forward projection']));
    if(sa.points>sb.points+5) acceptB.push(pick(['brings in more proven season points','adds more banked production','gets the stronger season-to-date output','trades into the better established scoring record']));
    if(sa.importance<sb.importance-5) acceptB.push(pick(['can exchange highly important pieces for assets the other side relies on less','turns heavily-relied-upon assets into a less structurally costly package','may reduce dependence on a small core','gets comparable value without inheriting the same owner-dependence']));
    if(avgDraftA<avgDraftB-10) acceptB.push(pick(['upgrades original draft pedigree','buys back into stronger blended pre-season pedigree','receives the more highly drafted package','improves draft-capital quality']));

    const noIncentive=()=>pick([
      'No obvious statistical incentive appears in the model — this side may need a preference, fixture or squad-balance reason.',
      'The numbers do not hand this manager a clear reason to say yes; negotiation would need to lean on fit rather than raw value.',
      'There is no screaming model-based incentive here. This would be a football-opinion trade rather than a spreadsheet trade.',
      'Nothing in the core metrics obviously improves for this side, so they would probably need a strategic reason to bite.',
      'The model cannot find an obvious carrot for this manager. You may need charm, threats, or a different player. Mostly charm.',
      'Statistically, this side has little reason to rush to the accept button.'
    ]);

    const intro=pick(['Trade Lab read','Deal diagnosis','Model verdict','Trade-room read','What the numbers reckon','Negotiation read','Deal temperature']);
    const acceptance='<div class="trade-sim-summary"><strong>'+intro+'</strong><p>'+reasons.map(escapePlayerHTML).join(' ')+'</p>'+ 
      '<div class="trade-sim-breakdown"><div><strong>Why '+fmtManager(ma)+' might accept</strong><br>'+(acceptA.length?escapePlayerHTML(acceptA.join(' · ')):escapePlayerHTML(noIncentive()))+'</div>'+ 
      '<div><strong>Why '+fmtManager(mb)+' might accept</strong><br>'+(acceptB.length?escapePlayerHTML(acceptB.join(' · ')):escapePlayerHTML(noIncentive()))+'</div></div></div>';

    result.className='trade-sim-result notice valid';
    result.innerHTML='<b>'+escapePlayerHTML(lean)+'.</b> The score blends form, total points, projection, blended draft pedigree (McDraft + official FPL Draft rank) and importance to the current owner.'+
      '<div class="trade-sim-breakdown"><div><strong>'+escapePlayerHTML(ma)+' gives</strong><br>Value '+sa.value.toFixed(1)+' · '+sa.points.toFixed(0)+' pts · form '+sa.form.toFixed(1)+' · projection '+sa.proj.toFixed(1)+' · owner importance '+sa.importance.toFixed(1)+'</div>'+
      '<div><strong>'+escapePlayerHTML(mb)+' gives</strong><br>Value '+sb.value.toFixed(1)+' · '+sb.points.toFixed(0)+' pts · form '+sb.form.toFixed(1)+' · projection '+sb.proj.toFixed(1)+' · owner importance '+sb.importance.toFixed(1)+'</div></div>'+acceptance;
}
function filterWaivers(){const s=document.getElementById('waiver-team-filter'),rows=document.querySelectorAll('.waiver-row'),empty=document.getElementById('waiver-search-empty'),q=s?s.value.trim().toLowerCase():'';let visible=0;rows.forEach(r=>{const show=!q||(r.dataset.team||'').includes(q);r.style.display=show?'':'none';if(show)visible++});if(empty)empty.style.display=(rows.length&&visible===0)?'block':'none';}

function filterTransfers() {
    const playerInput = document.getElementById("transfer-player-search");
    const teamSelect = document.getElementById("transfer-team-filter");
    const rows = document.querySelectorAll(".transfer-archive-row");
    const empty = document.getElementById("transfer-search-empty");

    const playerQuery = playerInput ? playerInput.value.trim().toLowerCase() : "";
    const teamQuery = teamSelect ? teamSelect.value.trim().toLowerCase() : "";
    let visible = 0;

    rows.forEach(function(row) {
        const player = (row.dataset.player || "").toLowerCase();
        const teams = (row.dataset.team || "").toLowerCase();
        const matchesPlayer = !playerQuery || player.includes(playerQuery);
        const matchesTeam = !teamQuery || teams.includes(teamQuery);
        const show = matchesPlayer && matchesTeam;
        row.style.display = show ? "" : "none";
        if (show) visible += 1;
    });

    if (empty) {
        empty.style.display = (rows.length && visible === 0) ? "block" : "none";
    }
}


function filterHistoricalTrades() {
    const teamSelect = document.getElementById("historical-trade-team-filter");
    const cards = document.querySelectorAll(".historical-trade-card");
    const empty = document.getElementById("historical-trade-search-empty");
    const teamQuery = teamSelect ? teamSelect.value.trim().toLowerCase() : "";
    let visible = 0;

    cards.forEach(function(card) {
        const teams = (card.dataset.team || "").toLowerCase();
        const show = !teamQuery || teams.includes(teamQuery);
        card.style.display = show ? "" : "none";
        if (show) visible += 1;
    });

    if (empty) {
        empty.style.display = (cards.length && visible === 0) ? "block" : "none";
    }
}


function filterPlayers() {
    const input = document.getElementById("player-search");
    const position = document.getElementById("player-position-filter");
    const club = document.getElementById("player-club-filter");
    const fantasy = document.getElementById("player-fantasy-filter");
    const sort = document.getElementById("player-sort");
    const results = document.getElementById("player-search-results");
    const count = document.getElementById("player-directory-count");

    if (!input || !results) return;

    const query = input.value.trim().toLowerCase();
    const positionValue = position ? position.value : "";
    const clubValue = club ? club.value : "";
    const fantasyValue = fantasy ? fantasy.value : "";
    const sortValue = sort ? sort.value : "rating";

    let matches = playerSearchData.filter(function(player) {
        return (!query || player.name.toLowerCase().includes(query)) &&
               (!positionValue || player.position === positionValue) &&
               (!clubValue || player.team === clubValue) &&
               (!fantasyValue || (player.fantasy_team || "Free Agent") === fantasyValue);
    });

    matches.sort(function(a, b) {
        if (sortValue === "name") return a.name.localeCompare(b.name);
        if (sortValue === "rating") return Number(b.player_rating || 0) - Number(a.player_rating || 0) || Number(b.total_points || 0) - Number(a.total_points || 0);
        if (sortValue === "form") {
            return (Number(b.form || 0) - Number(a.form || 0)) ||
                   (Number(b.total_points || 0) - Number(a.total_points || 0));
        }
        if (sortValue === "goals") {
            return (Number(b.goals || 0) - Number(a.goals || 0)) ||
                   (Number(b.total_points || 0) - Number(a.total_points || 0));
        }
        if (sortValue === "assists") {
            return (Number(b.assists || 0) - Number(a.assists || 0)) ||
                   (Number(b.total_points || 0) - Number(a.total_points || 0));
        }
        return (Number(b.total_points || 0) - Number(a.total_points || 0)) ||
               (Number(b.form || 0) - Number(a.form || 0));
    });

    if (count) {
        count.textContent = matches.length + " player" + (matches.length === 1 ? "" : "s");
    }

    if (matches.length === 0) {
        results.innerHTML = '<div class="notice">No players match those filters.</div>';
        return;
    }

    const visible = matches.slice(0, 100);
    results.innerHTML =
        visible.map(renderPlayerDirectoryCard).join("") +
        (matches.length > 100
            ? '<div class="notice">Showing the first 100 matches. Refine the filters to narrow the list.</div>'
            : '');
}


function togglePlayerDetails(playerId) {
    const details = document.getElementById("player-details-" + playerId);
    if (!details) return;

    const isOpen = details.style.display !== "none";
    details.style.display = isOpen ? "none" : "block";
}


const FREE_AGENT_RECOMMENDATIONS =
    __FREE_AGENT_RECOMMENDATIONS__;


const H2H_RECORDS =
    __H2H_RECORDS__;

const TRADE_TARGETS =
    __TRADE_TARGETS__;
const SELL_HIGH_CANDIDATES = __SELL_HIGH_CANDIDATES__;


function renderMyTeamFreeAgents() {
    const wrap = document.getElementById("myteam-free-agents");
    if (!wrap) return;

    const manager = currentMyTeamManager();
    const recommendations = FREE_AGENT_RECOMMENDATIONS[manager] || [];

    if (recommendations.length === 0) {
        wrap.innerHTML =
            '<div class="notice">No clear like-for-like free-agent upgrades found from the latest captured squad.</div>';
        return;
    }

    let html = '<div class="free-agent-list">';

    recommendations.forEach(function(player) {
        const seasonArrow =
            player.season_edge > 0
                ? '<span class="upgrade-positive">+' + player.season_edge + ' pts</span>'
                : '<span class="upgrade-neutral">Season level</span>';

        const formArrow =
            player.form_edge > 0
                ? '<span class="upgrade-positive">+' + player.form_edge.toFixed(1) + ' form</span>'
                : '<span class="upgrade-neutral">' + player.form_edge.toFixed(1) + ' form</span>';

        html +=
            '<div class="free-agent-row">' +
                '<div class="free-agent-main">' +
                    '<div class="free-agent-name">' + escapePlayerHTML(player.name) + '</div>' +
                    '<div class="free-agent-meta">' +
                        escapePlayerHTML(player.position) + ' · ' +
                        escapePlayerHTML(player.team) + ' · Free Agent' +
                    '</div>' +
                    fixtureRunHTML(player.next_fixtures, true) +
                '</div>' +
                '<div class="free-agent-comparison">' +
                    '<span class="free-agent-label">Over ' + escapePlayerHTML(player.replace_name) + '</span>' +
                    seasonArrow +
                    formArrow +
                '</div>' +
                '<div class="free-agent-stats">' +
                    '<b>' + player.total_points + '</b><span>Pts</span>' +
                    '<b>' + player.form.toFixed(1) + '</b><span>5GW</span>' +
                    '<b>' + Number(player.player_value || 0).toFixed(0) + '</b><span>Value</span>' +
                    '<b>' + Number(player.projected_season_points || 0).toFixed(0) + '</b><span>Season proj.</span>' +
                '</div>' +
            '</div>';
    });

    html += '</div>';
    wrap.innerHTML = html;
}




function renderMyTeamPositionNeeds(){
    const wrap=document.getElementById('myteam-position-needs');
    if(!wrap)return;
    const manager=currentMyTeamManager();
    const data=(manager&&MY_TEAM_POSITION_NEEDS[manager])||{};
    const positions=[['GKP','GK'],['DEF','DEF'],['MID','MID'],['FWD','FWD']];
    if(!Object.keys(data).length){wrap.innerHTML='<div class="notice">No positional-strength data available yet.</div>';return;}
    const colour=score=>score>=75?'#ef4444':score>=55?'#f97316':score>=35?'#eab308':score>=15?'#84cc16':'#22c55e';
    let html='<div class="myteam-position-need-grid">';
    positions.forEach(([key,label])=>{
        const r=data[key]||{need_score:50,strength_percentile:50,avg_projection:0,label:'Balanced'};
        const need=Number(r.need_score||0), pct=Number(r.strength_percentile||0), avg=Number(r.avg_projection||0), c=colour(need);
        html+='<div class="position-need-card" style="--need-colour:'+c+'">'+
          '<div class="position-need-top"><span class="position-need-pos">'+label+'</span><span class="position-need-score">'+need.toFixed(0)+'</span></div>'+
          '<div class="position-need-label">'+escapePlayerHTML(r.label||'Balanced')+'</div>'+
          '<div class="position-need-meta">Strength '+pct.toFixed(0)+'th percentile · avg projection '+avg.toFixed(1)+'</div>'+
          '<div class="position-need-track"><div class="position-need-fill" style="width:'+Math.max(3,need).toFixed(0)+'%"></div></div></div>';
    });
    wrap.innerHTML=html+'</div>';
}

function renderMyTeamTradeTargets() {
    const wrap = document.getElementById("myteam-trade-targets");
    if (!wrap) return;
    const manager = currentMyTeamManager();
    const targets = TRADE_TARGETS[manager] || [];
    if (!targets.length) {
        wrap.innerHTML = '<div class="notice">No sensible trade targets found from the latest rosters.</div>';
        return;
    }
    let html = '<div class="trade-target-list">';
    targets.forEach(function(t) {
        const clubNote = Number(t.same_club_owned || 0) >= 2
            ? ' · club concentration penalty: already ' + t.same_club_owned + ' from ' + escapePlayerHTML(t.team)
            : ' · diversification looks healthy';
        html += '<div class="trade-target-row">' +
            '<div><div class="trade-target-name">' + escapePlayerHTML(t.name) + '</div>' +
            '<div class="trade-target-meta">' + escapePlayerHTML(t.position) + ' · ' + escapePlayerHTML(t.team) + ' · owned by ' + escapePlayerHTML(t.owner) + '</div>' +
            '<div class="trade-target-reason">Projects ' + Number(t.upgrade || 0).toFixed(2) + ' pts/GW above ' + escapePlayerHTML(t.replace_name) + ' · ' + escapePlayerHTML(t.hot_cold_label || 'Neutral') + ' · positional need ' + Number(t.position_need || 0).toFixed(0) + '/100' + clubNote + '</div>' +
            fixtureRunHTML(t.next_fixtures, true) + '</div>' +
            '<div class="trade-target-scores"><div class="trade-target-score"><span>Target fit</span><b>' + Number(t.fit_score || 0).toFixed(0) + '</b></div>' +
            '<div class="trade-target-score"><span>Realism</span><b>' + Number(t.realism_score || 0).toFixed(0) + '</b></div>' +
            '<div class="trade-target-score"><span>Projection</span><b>' + Number(t.projection || 0).toFixed(1) + '</b></div>' +
            '<div class="trade-target-score"><span>Value</span><b>' + Number(t.player_value || 0).toFixed(0) + '</b></div>' +
            '<div class="trade-target-score"><span>Season</span><b>' + Number(t.projected_season_points || 0).toFixed(0) + '</b></div></div>' +
            '<div class="trade-target-offer"><span>Comparable outgoing asset</span><b>' + escapePlayerHTML(t.offer_name) + '</b><span>' + Number(t.offer_projection || 0).toFixed(1) + ' projected</span></div>' +
            '</div>';
    });
    html += '</div>';
    wrap.innerHTML = html;
}

function renderMyTeamSellHigh(){
    const wrap=document.getElementById('myteam-sell-high'); if(!wrap)return;
    const rows=SELL_HIGH_CANDIDATES[currentMyTeamManager()]||[];
    if(!rows.length){wrap.innerHTML='<div class="notice">No obvious sell-high candidates right now — which is usually a nice problem to have.</div>';return;}
    wrap.innerHTML='<div class="trade-target-list">'+rows.map(function(p){
        const future=p.fixture_run_score<0.97?'tougher fixtures ahead':(p.fixture_run_score>1.04?'still has a friendly run':'mixed fixtures ahead');
        return '<div class="trade-target-row"><div><div class="trade-target-name">'+escapePlayerHTML(p.name)+'</div><div class="trade-target-meta">'+escapePlayerHTML(p.position)+' · '+escapePlayerHTML(p.team)+' · '+escapePlayerHTML(p.heat_label)+'</div><div class="trade-target-reason">Heat '+Number(p.heat||0).toFixed(0)+' · '+future+' · positional need '+Number(p.position_need||0).toFixed(0)+'/100</div>'+fixtureRunHTML(p.next_fixtures,true)+'</div><div class="trade-target-scores"><div class="trade-target-score"><span>Stock</span><b>'+Number(p.stock_score||0).toFixed(0)+'</b></div><div class="trade-target-score"><span>Value</span><b>'+Number(p.player_value||0).toFixed(0)+'</b></div><div class="trade-target-score"><span>Season proj.</span><b>'+Number(p.projected_season_points||0).toFixed(0)+'</b></div></div></div>';
    }).join('')+'</div>';
}

function renderPLFixtureBrowser(requestedGw){
    const wrap=document.getElementById('pl-fixture-browser'); if(!wrap||!PL_FIXTURE_GAMEWEEKS.length)return;
    if (requestedGw !== undefined && requestedGw !== null) {
        const idx = PL_FIXTURE_GAMEWEEKS.indexOf(Number(requestedGw));
        if (idx !== -1) plFixtureIndex = idx;
    }
    plFixtureIndex=Math.max(0,Math.min(plFixtureIndex,PL_FIXTURE_GAMEWEEKS.length-1));
    const gw=PL_FIXTURE_GAMEWEEKS[plFixtureIndex], rows=PL_FIXTURE_BROWSER[String(gw)]||[];
    const display=document.getElementById('pl-fixture-gw-display');
    if(display) display.textContent='GW'+gw+' · synced';
    wrap.innerHTML='<div class="future-fixtures-list">'+rows.map(function(f){
      const hp=Number(f.home_fpl_points||0),ap=Number(f.away_fpl_points||0);
      return '<div class="future-fixture-row"><div class="future-fixture-team">'+escapePlayerHTML(f.home)+' <small>'+hp.toFixed(0)+' FPL pts</small></div><div class="future-fixture-vs">'+escapePlayerHTML(f.score||'vs')+'</div><div class="future-fixture-team right">'+escapePlayerHTML(f.away)+' <small>'+ap.toFixed(0)+' FPL pts</small></div></div>';
    }).join('')+'</div>';
}

function renderMyTeamH2H() {
    const wrap = document.getElementById("myteam-h2h-record");
    if (!wrap) return;

    const manager = currentMyTeamManager();
    if (!manager) {
        wrap.innerHTML = '<div class="notice">Select a team to view its head-to-head record.</div>';
        return;
    }

    const records = H2H_RECORDS[manager] || {};
    const opponents = MANAGER_ORDER.filter(function(opponent) {
        return opponent !== manager && records[opponent];
    });

    if (opponents.length === 0) {
        wrap.innerHTML = '<div class="notice">No head-to-head matches captured yet.</div>';
        return;
    }

    opponents.sort(function(a, b) {
        const ra = records[a];
        const rb = records[b];
        const aWinRate = ra.played ? ra.wins / ra.played : 0;
        const bWinRate = rb.played ? rb.wins / rb.played : 0;
        return (bWinRate - aWinRate) || (rb.wins - ra.wins) || a.localeCompare(b);
    });

    let html = '<div class="h2h-record-list">';

    opponents.forEach(function(opponent) {
        const record = records[opponent];
        const resultClass =
            record.wins > record.losses
                ? "h2h-positive"
                : record.losses > record.wins
                    ? "h2h-negative"
                    : "h2h-neutral";

        html +=
            '<div class="h2h-record-row">' +
                '<div class="h2h-opponent">' + escapePlayerHTML(opponent) + '</div>' +
                '<div class="h2h-record-summary ' + resultClass + '">' +
                    record.wins + 'W ' + record.draws + 'D ' + record.losses + 'L' +
                '</div>' +
                '<div class="h2h-record-score">' + record["for"] + '–' + record["against"] + '</div>' +
                '<div class="h2h-record-played">' +
                    record.played + ' game' + (record.played === 1 ? '' : 's') +
                '</div>' +
            '</div>';
    });

    html += '</div>';
    wrap.innerHTML = html;
}


/* ============================================================
   INITIALISE
   ============================================================ */

/* ============================================================
   SAFE DASHBOARD STARTUP
   ------------------------------------------------------------
   Initialise each feature independently. One broken optional
   component must never take down navigation or the rest of the UI.
   ============================================================ */

function safeInit(label, fn) {
    try {
        fn();
    } catch (error) {
        console.error("FPL Dashboard " + label + " failed:", error);
    }
}


function closeFixtureDetail() {
    const overlay = document.getElementById("fixture-detail-overlay");
    if (!overlay) return;
    overlay.hidden = true;
    overlay.setAttribute("aria-hidden", "true");
    overlay.querySelectorAll(".fixture-detail-panel").forEach(panel => panel.hidden = true);
    document.body.style.overflow = "";
}
function openFixtureDetail(detailId) {
    const overlay = document.getElementById("fixture-detail-overlay");
    const panel = document.getElementById(detailId);
    if (!overlay || !panel) return;
    overlay.querySelectorAll(".fixture-detail-panel").forEach(item => item.hidden = true);
    panel.hidden = false;
    overlay.hidden = false;
    overlay.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    const closeButton = document.getElementById("fixture-detail-close");
    if (closeButton) closeButton.focus();
}
function initialiseFixtureDrilldown() {
    document.querySelectorAll(".fixture-clickable[data-fixture-detail]").forEach(function(card) {
        card.addEventListener("click", () => openFixtureDetail(card.dataset.fixtureDetail));
        card.addEventListener("keydown", function(event) {
            if (event.key === "Enter" || event.key === " ") { event.preventDefault(); openFixtureDetail(card.dataset.fixtureDetail); }
        });
    });
    const closeButton = document.getElementById("fixture-detail-close");
    if (closeButton) closeButton.addEventListener("click", closeFixtureDetail);
    const overlay = document.getElementById("fixture-detail-overlay");
    if (overlay) overlay.addEventListener("click", event => { if (event.target === overlay) closeFixtureDetail(); });
    document.addEventListener("keydown", event => { if (event.key === "Escape") closeFixtureDetail(); });
}


const DASHBOARD_THEME_KEY = 'mcdraft-theme';

function dashboardThemePalette(theme){
    if(theme==='light'){
        return {paper:'#ffffff', plot:'#ffffff', text:'#334155', grid:'#e2e8f0', zero:'#cbd5e1'};
    }
    return {paper:'#111827', plot:'#111827', text:'#cbd5e1', grid:'#334155', zero:'#475569'};
}

function rethemePlotlyCharts(theme){
    if(typeof Plotly==='undefined') return;
    const p=dashboardThemePalette(theme);
    document.querySelectorAll('.js-plotly-plot').forEach(function(chart){
        try{
            Plotly.relayout(chart,{
                paper_bgcolor:p.paper,
                plot_bgcolor:p.plot,
                'font.color':p.text,
                'xaxis.color':p.text,
                'yaxis.color':p.text,
                'xaxis.gridcolor':p.grid,
                'yaxis.gridcolor':p.grid,
                'xaxis.zerolinecolor':p.zero,
                'yaxis.zerolinecolor':p.zero,
                'legend.font.color':p.text,
                'title.font.color':p.text
            });
        }catch(e){}
    });
}

function setDashboardTheme(theme, persist=true){
    const chosen=theme==='light'?'light':'dark';
    document.body.dataset.theme=chosen;
    document.documentElement.dataset.theme=chosen;
    const btn=document.getElementById('theme-toggle');
    if(btn){
        const light=chosen==='light';
        btn.setAttribute('aria-pressed', light?'true':'false');
        btn.title=light?'Switch to dark mode':'Switch to light mode';
        const icon=btn.querySelector('.theme-toggle-icon');
        const label=btn.querySelector('.theme-toggle-label');
        if(icon) icon.textContent=light?'☾':'☀';
        if(label) label.textContent=light?'Dark':'Light';
    }
    if(persist){
        try{localStorage.setItem(DASHBOARD_THEME_KEY,chosen);}catch(e){}
    }
    requestAnimationFrame(function(){
        rethemePlotlyCharts(chosen);
        if(typeof resizeCharts==='function') setTimeout(function(){try{resizeCharts();}catch(e){}},40);
    });
}

function initialiseDashboardTheme(){
    let saved=null;
    try{saved=localStorage.getItem(DASHBOARD_THEME_KEY);}catch(e){}
    setDashboardTheme(saved==='light'?'light':'dark',false);
}

function toggleDashboardTheme(){
    setDashboardTheme(document.body.dataset.theme==='light'?'dark':'light',true);
}

function initialiseDashboard() {
    safeInit("colour theme", initialiseDashboardTheme);

    safeInit("page navigation", function() {
        // The Live Centre section is only rendered when the GW is live.
        // Use it as the initial landing page, otherwise keep Overview.
        // This runs once on page load; visitors can still browse any page.
        const landingPage = document.getElementById("page-live-centre")
            ? "live-centre"
            : "overview";
        showPage(landingPage);
    });

    safeInit("Club Explorer", initialiseClubExplorer);
    safeInit("My Team", function() {
        initialiseMyTeam();
    });

    safeInit("Future fixtures", function() {
        updateFutureFixtures();
    });

    safeInit("Team of the Week", function() {
        updateTOTW();
    });

    safeInit("Results", function() {
        updateResults();
    });

    safeInit("Fixture drilldown", initialiseFixtureDrilldown);

    safeInit("My Team charts", function() {
        renderMyTeamStatsCharts();
    });

    safeInit("trend charts", function() {
        initAllTrendCharts();
    });

    safeInit("Analytics manager filters", function() {
        initAnalyticsManagerFilter();
        initPlayerRelationships();
        initWaiverIntelligence();
        initTransferRiverPassport();
        initManagerWarRoom();
if ((SEASON_TIMELINE_DATA||[]).length) renderSeasonTimeline(SEASON_TIMELINE_DATA.length-1);
    });

    safeInit("My Team recommendations", function() {
        renderMyTeamFreeAgents();
        renderMyTeamTradeTargets();
        renderMyTeamSellHigh();
    });

    safeInit("Premier League fixtures", function() {
        const selectedGW = resultsGameweeks.length ? resultsGameweeks[resultsIndex] : dashboardDisplayGameweek;
        renderPLFixtureBrowser(selectedGW);
    });

    safeInit("My Team H2H", function() {
        renderMyTeamH2H();
    });

    setTimeout(function() {
        safeInit("chart resize", resizeCharts);
    }, 150);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialiseDashboard);
} else {
    initialiseDashboard();
}

window.addEventListener("resize", function() {
    safeInit("chart resize", resizeCharts);
});
"""


vulnerability_css = r"""
/* My Team · Squad Vulnerability Radar, including light theme and touch controls. */
.vuln-head{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:12px}
.vuln-overall{display:flex;flex-direction:column;gap:5px;padding:13px 19px;border:1px solid var(--border);border-radius:14px;background:var(--bg-secondary)}
.vuln-overall>span:first-child,.vuln-eyebrow{font-size:11px;color:var(--muted);font-weight:800;letter-spacing:.08em;text-transform:uppercase}
.vuln-overall>strong{font-size:37px;color:var(--text);font-weight:850;line-height:1.2;font-variant-numeric:tabular-nums}
.vuln-overall>strong small{font-size:15px;color:var(--muted);font-weight:600}
.vuln-meta{text-align:right;font-size:12px;line-height:1.8;color:var(--muted)}
.vuln-layout{display:grid;grid-template-columns:minmax(270px,1fr) minmax(275px,1fr);gap:20px;align-items:center}
.vuln-visual{min-width:0;display:flex;flex-direction:column;align-items:center;gap:6px}
.vuln-radar{width:min(100%,470px);height:auto;overflow:visible;color:var(--text)}
.vuln-grid{fill:none;stroke:var(--border);stroke-width:1}.vuln-axis-line{stroke:var(--border);stroke-width:1}
.vuln-league-area{fill:#5193b5;fill-opacity:.075;stroke:#5193b5;stroke-width:2;stroke-dasharray:5 4}
.vuln-squad-area{fill:#ee8e4d;fill-opacity:.27;stroke:#e78d4e;stroke-width:2.8;stroke-linejoin:round}
.vuln-label{fill:var(--text);font-size:10.6px;font-weight:750;pointer-events:none}
.vuln-radar-point{outline:none;cursor:pointer}.vuln-touch-target{fill:transparent;stroke:none;cursor:pointer}
.vuln-dot{fill:#f6ac62;stroke:var(--bg-secondary);stroke-width:2.5;pointer-events:none}
.vuln-radar-point.selected .vuln-dot,.vuln-radar-point:focus-visible .vuln-dot{fill:#fbdf85;stroke:#e07833;stroke-width:3}
.vuln-radar-point:focus-visible .vuln-touch-target{stroke:var(--accent);stroke-width:2;stroke-dasharray:3 3}
.vuln-legend{display:flex;justify-content:center;gap:16px;flex-wrap:wrap;color:var(--muted);font-size:11px;font-weight:700}
.vuln-legend span{display:inline-flex;align-items:center;gap:6px}.vuln-legend i{width:15px;height:3px;border-radius:2px;background:#e78d4e;display:inline-block}.vuln-legend i.vuln-league-swatch{background:#5193b5}
.vuln-compare{background:var(--bg-secondary);color:var(--text);border:1px solid var(--border);border-radius:9px;padding:9px 14px;cursor:pointer;min-height:40px;font:inherit;font-size:12px;font-weight:700}
.vuln-compare:hover,.vuln-axis-button:hover{border-color:var(--accent)}
.vuln-axes{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
.vuln-axis-button{min-width:0;min-height:86px;text-align:left;cursor:pointer;border:1px solid var(--border);border-radius:11px;padding:11px 12px;background:var(--bg-secondary);color:var(--text);display:flex;flex-direction:column;gap:6px;font:inherit}
.vuln-axis-button[aria-pressed="true"]{border:2px solid var(--accent);padding:10px 11px;box-shadow:0 0 0 2px rgba(54,165,190,.12)}
.vuln-axis-button>span{display:flex;gap:6px;align-items:center;font-size:12px;font-weight:750}
.vuln-axis-dot{width:9px;height:9px;flex:none;border-radius:50%;display:inline-block}
.vuln-axis-dot.vuln-low{background:#29a57b}.vuln-axis-dot.vuln-moderate{background:#d2a34a}.vuln-axis-dot.vuln-high{background:#e17e42}.vuln-axis-dot.vuln-critical{background:#dd5364}
.vuln-axis-button>strong{font-size:21px;font-weight:850;font-variant-numeric:tabular-nums}
.vuln-axis-button>small{color:var(--muted);font-size:11px}
.vuln-detail{border:1px solid var(--border);border-radius:12px;padding:15px 18px;background:var(--bg-secondary);margin-top:16px;color:var(--text)}
.vuln-detail-head{display:flex;align-items:center;justify-content:space-between;gap:9px;flex-wrap:wrap}
.vuln-detail h3{font-size:18px;margin:5px 0 10px;color:var(--text)}.vuln-detail p{font-size:13px;line-height:1.6;color:var(--text);margin:8px 0 12px}
.vuln-risk-badge{width:fit-content;font-weight:800;font-size:11px;border-radius:12px;padding:5px 9px;border:1px solid}
.vuln-risk-badge.vuln-low{color:#16835a;border-color:#16835a}.vuln-risk-badge.vuln-moderate{color:#bc912b;border-color:#bc912b}.vuln-risk-badge.vuln-high{color:#dd7c34;border-color:#dd7c34}.vuln-risk-badge.vuln-critical{color:#db5364;border-color:#db5364}
.vuln-driver-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:8px}
.vuln-driver-list>div{font-size:12px;line-height:1.45;border-left:3px solid #e78d4e;background:rgba(128,128,128,.055);padding:9px 11px;border-radius:6px}
.vuln-footnote{font-size:11px;line-height:1.55;color:var(--muted);margin:12px 0 0}
body[data-theme="light"] .vuln-radar-point .vuln-dot{stroke:#fff}
@media(max-width:850px){.vuln-layout{grid-template-columns:1fr}.vuln-axes{grid-template-columns:repeat(3,minmax(0,1fr))}.vuln-radar{max-width:410px}}
@media(max-width:560px){.vuln-axes{grid-template-columns:repeat(2,minmax(0,1fr))}.vuln-head{align-items:flex-start}.vuln-meta{text-align:left}.vuln-visual{margin:0 -9px}.vuln-axis-button{min-height:89px}.vuln-overall>strong{font-size:31px}}

"""

radar_health_css = r"""

/* v41: summary-first analytics, detailed explorer under Players. */
.analytics-impact-intro{margin-bottom:22px}
.analytics-impact-group-title{margin:25px 0 12px;font-size:1.18rem;letter-spacing:-.01em}
#player-sub-availability .health-chart-pair{max-width:100%}
@media(max-width:560px){.analytics-impact-intro .stats-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
/* v40: both dimensions visible at once; all team bars drill to players. */
.health-metric-switch{display:flex;gap:7px;flex-wrap:wrap;margin:17px 0 13px}
.health-metric-btn{font:inherit;font-size:.82rem;font-weight:800;color:var(--muted);border:1px solid var(--border);background:var(--bg-secondary);border-radius:9px;padding:10px 12px;cursor:pointer}
.health-metric-btn.active{background:var(--accent-dark);border-color:var(--accent);color:var(--text)}
.health-filters{margin:10px 0}.health-free-agent-toggle{display:flex;align-items:center;gap:8px;font-size:.79rem;color:var(--muted);margin:10px 0 3px;cursor:pointer}
.health-free-agent-toggle input{accent-color:var(--accent)}
.health-data-note,.health-chart-note{font-size:.73rem;color:var(--muted);margin:10px 0 0;line-height:1.4}
.health-section-note{margin:19px 0 12px}.health-section-note h3{font-size:1.05rem;margin:0 0 5px}.health-section-note p{font-size:.83rem;color:var(--muted);line-height:1.4;margin:0}
.health-chart-pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px;align-items:start}
.health-chart-card{min-width:0;background:var(--bg-secondary);border:1px solid var(--border);border-radius:12px;padding:15px}
.health-chart-heading{display:flex;align-items:start;justify-content:space-between;gap:8px;margin-bottom:10px}.health-chart-heading h3{margin:0 0 4px;font-size:.96rem}.health-chart-heading span{display:block;color:var(--muted);font-size:.7rem}.health-chart-heading strong{color:var(--accent);white-space:nowrap;font-size:.82rem}
.health-legend{display:flex;flex-wrap:wrap;gap:7px 11px;margin-bottom:11px}.health-legend span{color:var(--muted);font-size:.65rem;display:flex;align-items:center;gap:4px}.health-legend i{width:8px;height:8px;border-radius:2px;display:inline-block;flex-shrink:0}
.health-chart-scroll{max-height:755px;overflow-y:auto;scrollbar-width:thin;padding-right:3px}.health-chart-row{display:grid;grid-template-columns:minmax(83px,141px) minmax(0,1fr) 41px;gap:8px;align-items:center;width:100%;font:inherit;padding:7px 4px;background:transparent;border:0;border-bottom:1px solid var(--border);text-align:left;color:var(--text);cursor:pointer;border-radius:4px}.health-chart-row:hover,.health-chart-row:focus-visible{background:rgba(128,128,128,.12);outline-offset:-2px}.health-chart-row strong{text-align:right;font-size:.77rem;font-variant-numeric:tabular-nums}.health-chart-name{font-size:.72rem;font-weight:750;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.health-stack-track{display:flex;align-items:stretch;gap:0;height:12px;background:rgba(128,128,128,.15);border-radius:3px;overflow:hidden;min-width:0}.health-stack-segment{display:block;min-width:0;height:100%}.health-injury{background:#ef6f86}.health-suspension{background:#f1ad47}.health-doubt{background:#e8d36a}.health-unavailable{background:#8d8acb}.health-news{background:#4ba9b3}.health-risk-fill{background:linear-gradient(90deg,#efb94d,#ec6b80)}.health-removed-old{background:#8294a9}.health-removed-new{background:#54ccae}
.health-drill-card{margin-top:20px;border:1px solid var(--accent);border-radius:13px;padding:15px;background:var(--bg-secondary)}.health-drill-head{display:flex;justify-content:space-between;gap:10px;align-items:center}.health-drill-head h3{margin:0;font-size:1rem}.health-drill-head p{font-size:.74rem;color:var(--muted);margin:4px 0}.health-drill-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:1px solid var(--border);flex-wrap:wrap}.health-drill-row:last-child{border-bottom:0}.health-drill-row>div:first-child{flex:1 1 190px;min-width:0}.health-drill-row b{font-size:.84rem}.health-drill-row small{display:block;font-size:.7rem;color:var(--muted);margin-top:4px}.health-drill-row p{margin:5px 0 0;font-size:.74rem;line-height:1.4}.health-removal-pill{font-size:.7rem;border:1px solid var(--border);border-radius:8px;padding:5px 7px}
@media(max-width:950px){.health-chart-pair{grid-template-columns:1fr}.health-chart-scroll{max-height:610px}.health-chart-row{grid-template-columns:minmax(95px,165px) minmax(0,1fr) 47px}}@media(max-width:480px){.health-chart-card{padding:11px}.health-chart-row{grid-template-columns:minmax(81px,116px) minmax(0,1fr) 39px;gap:6px}.health-chart-name{font-size:.7rem}}
.health-kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin:20px 0}.health-kpi{display:flex;flex-direction:column;gap:5px;border:1px solid var(--border,#405069);border-radius:13px;padding:16px;background:rgba(128,128,128,.06)}.health-kpi b{font-size:1.7rem}.health-kpi span{font-size:.78rem;opacity:.75}.health-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:12px}.health-event{border:1px solid var(--border,#405069);border-radius:13px;padding:15px;min-width:0}.health-event strong,.health-event small{display:block}.health-event small{opacity:.75;margin-top:4px}.health-event p{line-height:1.5}.radar-layout{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:12px}.performance-radar{width:min(100%,360px);height:auto;overflow:visible}.radar-ring{fill:none;stroke:currentColor;stroke-opacity:.14;stroke-width:1}.radar-axis{stroke:currentColor;stroke-opacity:.17;stroke-width:1}.radar-label{fill:currentColor;font-size:11px;font-weight:600}.radar-area{fill:#39b8c8;fill-opacity:.29;stroke:#39b8c8;stroke-width:2}.radar-dot{fill:#39b8c8;stroke:var(--card-bg,#132236);stroke-width:1}.radar-stats{display:grid;grid-template-columns:repeat(2,minmax(108px,1fr));gap:9px;max-width:310px;flex:1}.radar-stats span{padding:9px;border:1px solid rgba(128,128,128,.2);border-radius:9px;font-size:.8rem}.radar-stats b{display:block;font-size:1.15rem;margin-top:3px}.squad-player-link{border:0;background:transparent;color:inherit;cursor:pointer;text-align:left;font:inherit;text-decoration:underline;text-decoration-style:dotted;text-underline-offset:3px}.squad-player-radar-wrap{margin:15px 0}.player-radar-panel{margin:14px 0;border-top:1px solid rgba(128,128,128,.2);padding-top:13px}.player-radar-panel h3{margin-bottom:8px}@media(max-width:600px){.radar-layout{flex-direction:column}.radar-stats{max-width:100%;width:100%}}
"""

# ============================================================
# HTML TEMPLATE
# ============================================================

