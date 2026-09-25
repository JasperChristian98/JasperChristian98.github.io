def _fixture_team_snapshot(gw, manager):
    snapshot = history.get("gameweeks", {}).get(str(gw), {})
    for team_data in snapshot.get("teams", {}).values():
        if team_data.get("manager") == manager:
            return team_data
    return None


def _fixture_player_status(player, gw, is_live=False):
    if not is_live or int(gw) != int(dashboard_target_gw):
        return "FT" if int(gw) in finished_gws else ""
    pid = player.get("element_id")
    if pid is None:
        return ""
    meta = elements.get(int(pid), {})
    _, state = _club_fixture_remaining_fraction(meta.get("team"))
    return {"finished": "FT", "live": "LIVE", "upcoming": "TO PLAY"}.get(state, "")


def _fixture_xi_pitch(gw, manager, is_live=False):
    team_data = _fixture_team_snapshot(gw, manager)
    if not team_data:
        return '<div class="notice">Selected XI was not captured for this team.</div>'

    starters = list(team_data.get("starters", []) or [])
    by_pos = {"GKP": [], "DEF": [], "MID": [], "FWD": []}
    for player in starters:
        pos = player.get("position", "")
        if pos in by_pos:
            by_pos[pos].append(player)

    formation = f"{len(by_pos['DEF'])}-{len(by_pos['MID'])}-{len(by_pos['FWD'])}"

    def chip(player):
        name = escape_html(player.get("web_name", "Unknown"))
        try:
            pts = int(player.get("points", 0) or 0)
        except (TypeError, ValueError):
            pts = 0
        status = _fixture_player_status(player, gw, is_live)
        state_class = status.lower().replace(" ", "-")
        status_html = (
            f'<span class="fixture-player-state fixture-player-state-{state_class}">{status}</span>'
            if status else ""
        )
        return (
            '<div class="chip fixture-xi-chip">'
            f'<div class="chip-name">{name}</div>'
            f'<div class="chip-sub">{pts} pts {status_html}</div>'
            '</div>'
        )

    total = sum(int(p.get("points", 0) or 0) for p in starters)
    return (
        '<div class="fixture-xi-heading">'
        f'<strong>{escape_html(manager)}</strong>'
        f'<span>{formation} · {total} XI pts</span>'
        '</div>'
        '<div class="pitch fixture-xi-pitch">'
        f'<div class="row">{"".join(chip(p) for p in by_pos["FWD"])}</div>'
        f'<div class="row">{"".join(chip(p) for p in by_pos["MID"])}</div>'
        f'<div class="row">{"".join(chip(p) for p in by_pos["DEF"])}</div>'
        f'<div class="row">{"".join(chip(p) for p in by_pos["GKP"])}</div>'
        '</div>'
    )


def _fixture_detail_panel(detail_id, gw, team1, score1, team2, score2, is_live=False):
    state = "LIVE" if is_live else "FINAL"
    return (
        f'<section class="fixture-detail-panel" id="{detail_id}" hidden>'
        '<div class="fixture-detail-scoreline">'
        f'<div><strong>{escape_html(team1)}</strong><span>{score1}</span></div>'
        f'<div class="fixture-detail-state">GW{gw} · {state}</div>'
        f'<div><span>{score2}</span><strong>{escape_html(team2)}</strong></div>'
        '</div>'
        '<div class="fixture-xi-grid">'
        f'<div>{_fixture_xi_pitch(gw, team1, is_live=is_live)}</div>'
        f'<div>{_fixture_xi_pitch(gw, team2, is_live=is_live)}</div>'
        '</div>'
        '</section>'
    )


fixture_detail_sections = ""
results_sections = ""
latest_completed_for_browser = max(result_gameweeks) if result_gameweeks else None
browser_default_gw = (
    dashboard_target_gw
    if dashboard_game_state in ("upcoming", "live") and dashboard_target_gw in gameweek_browser_gameweeks
    else latest_completed_for_browser
)

for gw in gameweek_browser_gameweeks:
    display_mode = "block" if gw == browser_default_gw else "none"
    fixtures_html = ""

    # During a live gameweek, render the current raw Draft H2H scores rather
    # than the frozen completed-results archive or scoreless future fixtures.
    if dashboard_game_state == "live" and int(gw) == int(dashboard_target_gw):
        live_matches = [
            match for match in (league_matches_all or [])
            if int(match.get("event", 0) or 0) == int(gw)
        ]

        for match in live_matches:
            e1 = match.get("league_entry_1")
            e2 = match.get("league_entry_2")
            team1 = league_entry_id_to_name.get(e1, league_entry_id_to_name.get(str(e1), "Unknown"))
            team2 = league_entry_id_to_name.get(e2, league_entry_id_to_name.get(str(e2), "Unknown"))
            try:
                score1 = int(match.get("league_entry_1_points", 0) or 0)
            except (TypeError, ValueError):
                score1 = 0
            try:
                score2 = int(match.get("league_entry_2_points", 0) or 0)
            except (TypeError, ValueError):
                score2 = 0

            derby = _derby_name(team1, team2)
            derby_html = f'<div class="fixture-derby unified-derby">{escape_html(derby)}</div>' if derby else ''
            detail_id = f"fixture-detail-gw{gw}-live-{e1}-{e2}"
            fixture_detail_sections += _fixture_detail_panel(detail_id, gw, team1, score1, team2, score2, is_live=True)
            fixtures_html += f"""
                <div class="fixture fixture-clickable" data-fixture-detail="{detail_id}" role="button" tabindex="0" aria-label="Open {escape_html(team1)} versus {escape_html(team2)} lineups">
                    {derby_html}
                    <div class="fixture-team">
                        <span class="fixture-manager">{escape_html(team1)}</span>
                        <span class="fixture-score">{score1}</span>
                    </div>
                    <div class="fixture-vs">LIVE<br><small>View XI</small></div>
                    <div class="fixture-team">
                        <span class="fixture-score">{score2}</span>
                        <span class="fixture-manager">{escape_html(team2)}</span>
                    </div>
                </div>
            """

        title = f"Gameweek {gw} · Live"
        state_class = "live-gw"

    elif gw in results_by_gw:
        for fixture in results_by_gw[gw]:
            team1_class = ""
            team2_class = ""
            if fixture["result"] == "win1":
                team1_class, team2_class = "winner", "loser"
            elif fixture["result"] == "win2":
                team1_class, team2_class = "loser", "winner"
            else:
                team1_class = team2_class = "draw"

            derby = _derby_name(fixture["team1"], fixture["team2"])
            derby_html = f'<div class="fixture-derby unified-derby">{escape_html(derby)}</div>' if derby else ''
            detail_id = f"fixture-detail-gw{gw}-{escape_html(fixture['team1']).replace(' ', '-')}-{escape_html(fixture['team2']).replace(' ', '-')}"
            fixture_detail_sections += _fixture_detail_panel(
                detail_id, gw, fixture["team1"], fixture["score1"], fixture["team2"], fixture["score2"], is_live=False
            )
            fixtures_html += f"""
                <div class="fixture fixture-clickable" data-fixture-detail="{detail_id}" role="button" tabindex="0" aria-label="Open {escape_html(fixture['team1'])} versus {escape_html(fixture['team2'])} lineups">
                    {derby_html}
                    <div class="fixture-team {team1_class}">
                        <span class="fixture-manager">{escape_html(fixture["team1"])}</span>
                        <span class="fixture-score">{fixture["score1"]}</span>
                    </div>
                    <div class="fixture-vs">VS<br><small>View XI</small></div>
                    <div class="fixture-team {team2_class}">
                        <span class="fixture-score">{fixture["score2"]}</span>
                        <span class="fixture-manager">{escape_html(fixture["team2"])}</span>
                    </div>
                </div>
            """
        title = f"Gameweek {gw} · Results"
        state_class = "completed-gw"
    else:
        for fixture in full_fixture_schedule.get(gw, []):
            derby = _derby_name(fixture["team1"], fixture["team2"])
            derby_html = f'<div class="fixture-derby unified-derby">{escape_html(derby)}</div>' if derby else ''
            fixtures_html += f"""
                <div class="fixture future-fixture-unified">
                    {derby_html}
                    <div class="fixture-team">
                        <span class="fixture-manager">{escape_html(fixture["team1"])}</span>
                    </div>
                    <div class="fixture-vs">VS</div>
                    <div class="fixture-team">
                        <span class="fixture-manager">{escape_html(fixture["team2"])}</span>
                    </div>
                </div>
            """
        if dashboard_game_state == "live" and int(gw) == int(dashboard_target_gw):
            title = f"Gameweek {gw} · Live"
            state_class = "live-gw"
        elif int(gw) == int(dashboard_target_gw):
            title = f"Gameweek {gw} · Upcoming Fixtures"
            state_class = "future-gw"
        else:
            title = f"Gameweek {gw} · Future Fixtures"
            state_class = "future-gw"

    if not fixtures_html:
        fixtures_html = '<div class="notice">No fixtures available for this gameweek.</div>'

    results_sections += f"""
        <div class="results-slide {state_class}" id="results-gw-{gw}" style="display:{display_mode};">
            <div class="results-title">{title}</div>
            <div class="fixtures-list">{fixtures_html}</div>
        </div>
    """


# ============================================================
# TOTW HTML
# ============================================================

totw_sections = ""


for index, gw in enumerate(
    finished_gws
):

    display_mode = (
        "block"
        if index == len(
            finished_gws
        ) - 1
        else "none"
    )

    totw_sections += f"""
        <div
            class="totw-slide"
            id="totw-gw-{gw}"
            style="display:{display_mode};"
        >

            <div class="totw-title">
                Gameweek {gw} · Best XI
            </div>

            {totw_by_gw.get(gw, "")}

        </div>
    """


# ============================================================
# FUN STATS
# ============================================================

most_transferred_name = (
    most_transferred_players[0]["name"]
    if most_transferred_players
    else "N/A"
)


most_transferred_count = (
    most_transferred_players[0]["transfers"]
    if most_transferred_players
    else 0
)


most_used_name = (
    most_owned_managers[0]["name"]
    if most_owned_managers
    else "N/A"
)


most_used_count = (
    most_owned_managers[0]["owners"]
    if most_owned_managers
    else 0
)


best_form_name = (
    top_players_by_5[0]["name"]
    if top_players_by_5
    else "N/A"
)


best_form_score = (
    top_players_by_5[0]["avg_5"]
    if top_players_by_5
    else None
)


best_form_display = (
    f"{best_form_score:.1f}"
    if best_form_score is not None
    else "N/A"
)


dream_team_manager = (
    max(
        total_dreamteam,
        key=total_dreamteam.get
    )
    if total_dreamteam
    else "N/A"
)


dream_team_count = (
    max(
        total_dreamteam.values()
    )
    if total_dreamteam
    else 0
)


highest_avg_manager = (
    max(
        avg_points,
        key=avg_points.get
    )
    if avg_points
    else "N/A"
)


highest_avg_score = (
    max(
        avg_points.values()
    )
    if avg_points
    else 0
)


fun_stats_html = f"""
    <div class="stats-grid">

        <div class="stat-card">

            <div class="stat-label">
                Most Consistent Manager
            </div>

            <div class="stat-value">
                {escape_html(most_consistent or "N/A")}
            </div>

            <div class="stat-description">
                Lowest weekly score variance
            </div>

        </div>


        <div class="stat-card">

            <div class="stat-label">
                Biggest Bench Hoarder
            </div>

            <div class="stat-value">
                {escape_html(top_bench_waster or "N/A")}
            </div>

            <div class="stat-description">
                {total_bench_wasted.get(
                    top_bench_waster,
                    0
                ):.0f} pts left on the bench
            </div>

        </div>


        <div class="stat-card">

            <div class="stat-label">
                Most Dream Team Appearances
            </div>

            <div class="stat-value">
                {escape_html(dream_team_manager)}
            </div>

            <div class="stat-description">
                {dream_team_count} appearances
            </div>

        </div>


        <div class="stat-card">

            <div class="stat-label">
                Highest Average Score
            </div>

            <div class="stat-value">
                {escape_html(highest_avg_manager)}
            </div>

            <div class="stat-description">
                {highest_avg_score:.1f} pts per GW
            </div>

        </div>


        <div class="stat-card">

            <div class="stat-label">
                Most Transferred Player
            </div>

            <div class="stat-value">
                {escape_html(most_transferred_name)}
            </div>

            <div class="stat-description">
                {most_transferred_count}
                ownership changes
            </div>

        </div>


        <div class="stat-card">

            <div class="stat-label">
                Biggest Team Hopper
            </div>

            <div class="stat-value">
                {escape_html(most_used_name)}
            </div>

            <div class="stat-description">
                Used by {most_used_count}
                different managers
            </div>

        </div>


        <div class="stat-card">

            <div class="stat-label">
                Current Best 5GW Form
            </div>

            <div class="stat-value">
                {escape_html(best_form_name)}
            </div>

            <div class="stat-description">
                {best_form_display} pts per GW
            </div>

        </div>

    </div>
"""


# ============================================================
# TOP PLAYER CARDS
# ============================================================

top_player_cards = ""


for index, player in enumerate(
    top_players_by_season[:10],
    start=1
):

    top_player_cards += f"""
        <div class="top-player-card">

            <div class="top-player-rank">
                #{index}
            </div>

            <div class="top-player-name">
                {escape_html(player["name"])}
            </div>

            <div class="top-player-stat">
                {player["season_points"]} season points
            </div>

            <div class="top-player-stat">
                Used by {player["owners"]} managers
            </div>

        </div>
    """



# ============================================================
# FIXTURES + ANALYTICS LAB + REALISTIC TRADE TARGETS
# ============================================================

RIVALRY_FIXTURES = {
    frozenset(("Kamararama FC", "Buendophilia")): "The Christian Classico",
    frozenset(("NoRSNoRB No Chance", "Backstreet Moyes")): "The Brammer Derby",
    frozenset(("Ollie Gonna Squashya", "No Weimann No Cry")): "The Cheltenham Derby",
    frozenset(("danny’s doggy dudes", "PAUer Rangers")): "The Sadly Broke Scuffle",
    frozenset(("danny's doggy dudes", "PAUer Rangers")): "The Sadly Broke Scuffle",
    frozenset(("Jaap? Best Stam", "Backstreet Moyes")): "The Bald Derby",
    frozenset(("Jacquet Potato", "No Weimann No Cry")): "The Shit Beard Rivalry",
}


def _rivalry_label(team1, team2):
    # Prefer the dashboard's existing rivalry resolver if it knows this pair.
    try:
        existing = _derby_name(team1, team2)
        if existing:
            return existing
    except Exception:
        pass
    return RIVALRY_FIXTURES.get(frozenset((team1, team2)))


def _manager_last_n_avg(manager, n=3):
    vals = [float(v or 0) for _, v in sorted(raw_score_by_gw.get(manager, []))[-n:]]
    return statistics.mean(vals) if vals else 0.0


def _manager_season_avg(manager):
    vals = [float(v or 0) for _, v in sorted(raw_score_by_gw.get(manager, []))]
    return statistics.mean(vals) if vals else 0.0


def _norm_dict(values, invert=False):
    if not values:
        return {}
    lo, hi = min(values.values()), max(values.values())
    if hi == lo:
        return {k: 50.0 for k in values}
    out = {k: ((v-lo)/(hi-lo))*100.0 for k,v in values.items()}
    if invert:
        out = {k: 100.0-v for k,v in out.items()}
    return out


# Fixture difficulty is intentionally opponent-centric. Higher = harder.
_fd_form = {m: _manager_last_n_avg(m, 3) for m in managers}
_fd_pf = {m: _manager_season_avg(m) for m in managers}
_fd_squad = {m: float(current_squad_strength.get(m, {}).get("managed_xi", 0) or 0) for m in managers}
_fd_power = {m: float(power_score.get(m, 0) or 0) for m in managers}
_fd_form_n = _norm_dict(_fd_form)
_fd_pf_n = _norm_dict(_fd_pf)
_fd_squad_n = _norm_dict(_fd_squad)
_fd_power_n = _norm_dict(_fd_power)
fixture_strength_score = {
    m: (0.35*_fd_squad_n.get(m,0) + 0.25*_fd_form_n.get(m,0) +
        0.20*_fd_pf_n.get(m,0) + 0.20*_fd_power_n.get(m,0))
    for m in managers
}


# Cache GW-specific squad projections because Fixtures renders the same weeks repeatedly.
_fixture_squad_strength_cache = {int(dashboard_target_gw): current_squad_strength} if dashboard_target_gw else {}

def _fixture_squad_strength_for_gw(gw):
    try:
        gw = int(gw)
    except (TypeError, ValueError):
        gw = int(dashboard_target_gw or 1)
    if gw not in _fixture_squad_strength_cache:
        _fixture_squad_strength_cache[gw] = _build_current_squad_strength(gw)
    return _fixture_squad_strength_cache[gw]

def _manager_pl_fixture_multiplier(manager, gw):
    """Projected XI fixture environment for a manager in a specific FPL GW.

    >1 means the likely XI has a kinder-than-neutral real Premier League slate;
    <1 means a tougher slate. The average is projection-weighted so the fixture
    faced by a core starter matters more than the fixture faced by a fringe asset.
    """
    squad = _fixture_squad_strength_for_gw(gw).get(manager, {})
    players = list(squad.get('players', []) or [])
    best = _best_projected_xi(players) if players else None
    xi = list(best.get('players', []) or []) if best else []
    if not xi:
        return 1.0
    weighted = 0.0
    total_w = 0.0
    for player in xi:
        mult = float(player.get('fixture_multiplier', 1.0) or 1.0)
        # Blank GW assets should materially hurt a matchup, but avoid zero weight.
        if mult <= 0:
            mult = 0.55
        weight = max(0.75, float(player.get('projection', 0) or 0))
        weighted += mult * weight
        total_w += weight
    return weighted / total_w if total_w else 1.0

def fixture_difficulty(manager, opponent, gw=None):
    """1 easy .. 5 brutal, blending McDraft opponent quality and both XIs' PL slates."""
    raw = float(fixture_strength_score.get(opponent, 50.0))
    base = 1.0 + (raw / 100.0) * 4.0
    if gw is None:
        gw = dashboard_target_gw
    own_pl = _manager_pl_fixture_multiplier(manager, gw)
    opp_pl = _manager_pl_fixture_multiplier(opponent, gw)

    # A kind real-PL slate for your XI makes the McDraft fixture easier; a kind
    # slate for the opponent makes it harder. This is deliberately material but
    # does not overwhelm the opponent's underlying McDraft strength.
    pl_adjustment = 2.25 * (opp_pl - own_pl)
    difficulty = base + pl_adjustment
    return round(min(5.0, max(1.0, difficulty)) * 4) / 4


def _difficulty_class(value):
    if value >= 4.15: return "fixture-diff-brutal"
    if value >= 3.35: return "fixture-diff-hard"
    if value >= 2.65: return "fixture-diff-medium"
    if value >= 1.85: return "fixture-diff-kind"
    return "fixture-diff-soft"


def _next_fixture_rows(manager, count=5):
    out = []
    for gw in sorted(full_fixture_schedule):
        if int(gw) <= int(dashboard_last_finished_gw or 0):
            continue
        for f in full_fixture_schedule.get(gw, []):
            t1, t2 = f.get("team1"), f.get("team2")
            if manager not in (t1, t2):
                continue
            opp = t2 if manager == t1 else t1
            out.append({
                "gw": int(gw), "opponent": opp,
                "difficulty": fixture_difficulty(manager, opp, gw),
                "pl_fixture_multiplier": _manager_pl_fixture_multiplier(manager, gw),
                "opponent_pl_fixture_multiplier": _manager_pl_fixture_multiplier(opp, gw),
                "rivalry": _rivalry_label(manager, opp),
            })
            if len(out) >= count:
                return out
    return out


def fixtures_page_html():
    # Upcoming fixture cards for the next five schedule weeks.
    future_gws = [gw for gw in sorted(full_fixture_schedule) if int(gw) > int(dashboard_last_finished_gw or 0)][:5]
    fixture_sections = ""
    for gw in future_gws:
        cards = ""
        for f in full_fixture_schedule.get(gw, []):
            t1, t2 = f.get("team1", "Unknown"), f.get("team2", "Unknown")
            d1 = fixture_difficulty(t1, t2, gw)
            d2 = fixture_difficulty(t2, t1, gw)
            pl1 = _manager_pl_fixture_multiplier(t1, gw)
            pl2 = _manager_pl_fixture_multiplier(t2, gw)
            rivalry = _rivalry_label(t1, t2)
            rivalry_html = f'<div class="fixture-rivalry-banner">🔥 {escape_html(rivalry)}</div>' if rivalry else ""
            cards += f'''<div class="fixture-planner-card">
                {rivalry_html}
                <div class="fixture-planner-gw">GW{gw}</div>
                <div class="fixture-planner-match"><strong>{escape_html(t1)}</strong><span>vs</span><strong>{escape_html(t2)}</strong></div>
                <div class="fixture-difficulty-row">
                    <span class="fixture-difficulty-pill {_difficulty_class(d1)}">{escape_html(t1)} · {d1:.2f}/5 <small>PL slate {pl1:.2f}×</small></span>
                    <span class="fixture-difficulty-pill {_difficulty_class(d2)}">{escape_html(t2)} · {d2:.2f}/5 <small>PL slate {pl2:.2f}×</small></span>
                </div>
            </div>'''
        fixture_sections += f'<div class="fixture-week-block"><h3>Gameweek {gw}</h3><div class="fixture-planner-grid">{cards}</div></div>'

    # Upcoming run matrix.
    header_gws = sorted({row["gw"] for m in managers for row in _next_fixture_rows(m, 5)})[:5]
    head = "".join(f"<th>GW{gw}</th>" for gw in header_gws)
    rows = ""
    run_scores = []
    for manager in current_standings:
        by_gw = {r["gw"]: r for r in _next_fixture_rows(manager, 5)}
        vals = [r["difficulty"] for r in by_gw.values()]
        run_avg = statistics.mean(vals) if vals else 0.0
        run_scores.append((run_avg, manager))
        cells = ""
        for gw in header_gws:
            r = by_gw.get(gw)
            if not r:
                cells += '<td class="fixture-cell-empty">—</td>'
                continue
            badge = "🔥" if r.get("rivalry") else ""
            cells += f'<td><div class="fixture-run-cell {_difficulty_class(r["difficulty"])}"><b>{escape_html(r["opponent"])}</b><span>{badge} {r["difficulty"]:.2f}</span></div></td>'
        rows += f'<tr><td class="manager-name">{escape_html(manager)}</td>{cells}<td><b>{run_avg:.2f}</b></td></tr>'
    run_scores.sort(reverse=True)
    hardest = run_scores[0] if run_scores else (0, "—")
    easiest = run_scores[-1] if run_scores else (0, "—")
    summary = f'''<div class="analytics-insight-grid">
        <div class="analytics-insight"><span>Hardest upcoming run</span><strong>{escape_html(hardest[1])}</strong><small>{hardest[0]:.2f}/5 average difficulty</small></div>
        <div class="analytics-insight"><span>Kindest upcoming run</span><strong>{escape_html(easiest[1])}</strong><small>{easiest[0]:.2f}/5 average difficulty</small></div>
    </div>'''
    return f'''{summary}
        <div class="card"><h2>Upcoming run · next five</h2><p class="card-description">The only fixture planner view: five upcoming McDraft gameweeks, with GW-specific difficulty already adjusted for the real Premier League schedules faced by both projected XIs. Lower is kinder. Higher is filthier.</p><div class="table-wrap fixture-run-table"><table><thead><tr><th>McDraft</th>{head}<th>Run</th></tr></thead><tbody>{rows}</tbody></table></div></div>'''


# ---------------------------- Trade targets ----------------------------
def _current_rosters_from_status():
    rosters = {m: [] for m in managers}
    for pid, owner in current_owner_by_player.items():
        name = _dashboard_owner_name(owner)
        if name in rosters:
            rosters[name].append(int(pid))
    if not any(rosters.values()):
        for m, roster in current_rosters_by_manager.items():
            rosters[m] = [int(pid) for pid in roster]
    return rosters


_trade_rosters = _current_rosters_from_status()
# Owner colours in Player Analytics use the latest Draft ownership and remain
# draft-ID keyed, even where the identity CSV points to another classic FPL ID.
_analytics_owner_by_id = {
    int(pid): manager
    for manager, pids in _trade_rosters.items()
    for pid in pids
}
for _pid, _owner in current_owner_by_player.items():
    _owner_name = _dashboard_owner_name(_owner)
    if _owner_name in managers:
        _analytics_owner_by_id[int(_pid)] = _owner_name
    else:
        _analytics_owner_by_id.pop(int(_pid), None)
_all_current_player_ids = [pid for ids in _trade_rosters.values() for pid in ids]
_trade_proj_vals = []
for pid in _all_current_player_ids:
    # Reuse the projection already calculated inside current_squad_strength when possible.
    for m in managers:
        row = next((p for p in current_squad_strength.get(m, {}).get("players", []) if p.get("id") == pid), None)
        if row:
            _trade_proj_vals.append(float(row.get("projection", 0) or 0)); break
_trade_proj_median = statistics.median(_trade_proj_vals) if _trade_proj_vals else 3.0


def _trade_player_projection(pid):
    for m in managers:
        for p in current_squad_strength.get(m, {}).get("players", []):
            if int(p.get("id", -1)) == int(pid):
                return float(p.get("projection", 0) or 0)
    meta = elements.get(pid, {})
    return float(meta.get("points_per_game", 0) or 0)


# ---------------------------- My Team positional needs ----------------------------
# Strength is calculated against the other McDraft squads at the same position,
# using current projected output. Need is simply the inverse percentile: a weak
# position across the league becomes an urgent target; a stacked position becomes
# a low priority. This is also fed back into trade-target ranking.
_POSITION_ORDER = ["GKP", "DEF", "MID", "FWD"]
_position_avg_projection = {m: {} for m in current_standings}
for _m in current_standings:
    _by_pos = defaultdict(list)
    for _pid in _trade_rosters.get(_m, []):
        _metric = _player_current_metrics(_pid)
        _pos = _metric.get("position")
        if _pos in _POSITION_ORDER:
            _by_pos[_pos].append(_trade_player_projection(_pid))
    for _pos in _POSITION_ORDER:
        _vals = _by_pos.get(_pos, [])
        _position_avg_projection[_m][_pos] = statistics.mean(_vals) if _vals else 0.0

positional_need_map = {m: {} for m in current_standings}
for _pos in _POSITION_ORDER:
    _ranked = sorted(
        [(m, float(_position_avg_projection.get(m, {}).get(_pos, 0.0) or 0.0)) for m in current_standings],
        key=lambda x: x[1]
    )
    _n = max(1, len(_ranked))
    for _idx, (_m, _avg) in enumerate(_ranked):
        # Weakest manager ~= 0th percentile; strongest ~= 100th percentile.
        _pct = 50.0 if _n == 1 else (_idx / (_n - 1)) * 100.0
        _need = 100.0 - _pct
        if _need >= 75:
            _label = "Urgent need"
        elif _need >= 55:
            _label = "High need"
        elif _need >= 35:
            _label = "Balanced"
        elif _need >= 15:
            _label = "Strong"
        else:
            _label = "Overloaded"
        positional_need_map[_m][_pos] = {
            "avg_projection": round(_avg, 2),
            "strength_percentile": round(_pct, 1),
            "need_score": round(_need, 1),
            "label": _label,
        }

positional_need_json = json.dumps(positional_need_map, ensure_ascii=False)

# ============================================================
# MY TEAM · SQUAD VULNERABILITY RADAR
# ============================================================
# Snapshot of the CURRENT Draft roster, not a claim about a manager's old squad.
# All axes represent exposure (0 = less exposed, 100 = more exposed).  The
# existing next-GW forecast and FPL availability flags are reused; no new API
# calls are required. Rebuilt whenever the existing dashboard job runs.

def _vulnerability_clamp(value):
    return round(max(0.0, min(100.0, float(value))), 1)


def build_squad_vulnerability_data(rosters=None):
    import collections
    roster_map = _trade_rosters if rosters is None else rosters
    pos_labels = {'GKP': 'goalkeeper', 'DEF': 'defence', 'MID': 'midfield', 'FWD': 'attack'}
    scores_weight = {'star': 0.18, 'medical': 0.23, 'depth': 0.21,
                     'clubs': 0.10, 'fixtures': 0.14, 'fragility': 0.14}
    target = int(dashboard_target_gw or (max(finished_gws, default=0) + 1))
    result = {}

    def axis(key, title, score, summary, drivers, available=True):
        return {'key': key, 'label': title,
                'score': _vulnerability_clamp(score) if available else None,
                'summary': summary, 'drivers': drivers[:4], 'available': available}

    for manager in managers:
        ids = [int(pid) for pid in roster_map.get(manager, []) if int(pid) in elements]
        if not ids:
            result[manager] = {'as_of_gw': target, 'overall': None, 'axes': [],
                               'warning': 'Current Draft roster unavailable. No risk estimate shown.'}
            continue
        players = []
        for pid in ids:
            meta = elements[pid]
            pos = positions_lookup.get(meta.get('element_type'), '')
            if pos not in pos_labels:
                continue
            healthy = max(0.0, float(_player_weekly_projection(
                pid, _global_position_baselines, _global_league_player_mean,
                target_gw=target, apply_availability=False) or 0))
            avail = max(0.0, min(1.0, float(_availability_factor(pid, target) or 0)))
            players.append({'id': pid, 'name': meta.get('web_name') or f'Player {pid}',
                            'position': pos, 'projection': healthy,
                            'availability': avail, 'club': meta.get('team'),
                            'status': str((_fpl_availability.get(pid) or {}).get('status') or 'a')})
        best = _best_projected_xi(players)
        if not best or best.get('total', 0) <= 0:
            result[manager] = {'as_of_gw': target, 'overall': None, 'axes': [],
                               'warning': 'Insufficient player projections or no legal XI available.'}
            continue
        xi = best['players']
        xi_total = float(best['total'])
        xi_ids = {p['id'] for p in xi}
        top3 = sorted(xi, key=lambda p: p['projection'], reverse=True)[:3]
        star_share = sum(p['projection'] for p in top3) / xi_total
        # A fairly evenly scoring XI still has roughly one third of its points
        # supplied by its top three. Avoid marking that baseline as high risk.
        star_score = _vulnerability_clamp(100 * (star_share - 0.34) / 0.32)
        star = axis('star', 'Star reliance', star_score,
                    f'The three highest-projected starters supply {star_share:.0%} of this XI’s estimated points.',
                    [f"{p['name']}: {p['projection']:.1f} healthy projected pts" for p in top3])

        flags = sorted((p for p in players if p['status'] not in ('a', '') or p['availability'] < 0.999),
                       key=lambda p: p['projection'] * (1 - p['availability']), reverse=True)
        at_risk = sum(p['projection'] * (1 - p['availability']) for p in xi)
        medical_score = _vulnerability_clamp(100 * at_risk / max(0.25 * xi_total, 1))
        medical = axis('medical', 'Medical room', medical_score,
                       f'{at_risk:.1f} estimated starting-XI points are exposed to official FPL availability flags for GW{target}.',
                       [f"{p['name']} ({p['status'].upper()}): {p['availability']:.0%} estimated availability; "
                        f"{p['projection'] * (1-p['availability']):.1f} points exposed"
                        for p in flags[:3]] or ['No flagged or doubtful players in the current squad.'])

        # Test a loss at EACH position. The existing legal-formation optimiser
        # can switch 4-4-2 to 3-5-2 etc, instead of assuming same-position subs.
        position_losses = {}
        for pos in pos_labels:
            starters = [p for p in xi if p['position'] == pos]
            if not starters:
                continue
            key_player = max(starters, key=lambda p: p['projection'])
            reduced = _best_projected_xi([p for p in players if p['id'] != key_player['id']])
            if reduced:
                loss = max(0.0, (xi_total - float(reduced['total'])) / xi_total)
                score = _vulnerability_clamp(100 * loss / 0.13)
            else:
                loss = 1.0
                score = 100.0
            position_losses[pos] = (score, loss, key_player['name'], bool(reduced))
        depth_score = (sum(v[0] for v in position_losses.values()) / len(position_losses)
                       if position_losses else 0.0)
        thin = sorted(position_losses.items(), key=lambda item: item[1][0], reverse=True)
        depth = axis('depth', 'Positional cover', depth_score,
                     'Modelled damage from losing the strongest starter in each position, allowing formation changes but no transfers.',
                     [f"{pos_labels[pos].capitalize()}: {value[1]:.0%} projected XI loss after "
                      f"{value[2]} is removed" if value[3]
                      else f"{pos_labels[pos].capitalize()}: cannot field a legal XI without {value[2]}"
                      for pos, value in thin])

        clubs = collections.Counter(p['club'] for p in xi if p['club'] is not None)
        biggest_club, biggest_count = clubs.most_common(1)[0] if clubs else (None, 0)
        share = biggest_count / max(1, len(xi))
        hhi = sum((n / len(xi))**2 for n in clubs.values()) if clubs else 0.0
        clubs_score = _vulnerability_clamp(100 * (0.70 * max(0, share - 0.15) / 0.35
                                                   + 0.30 * max(0, hhi - 0.11) / 0.24))
        club_name = teams_lookup.get(biggest_club, 'Unknown club')
        groups = [f'{teams_lookup.get(tid, "Unknown")}: {count} projected starters'
                  for tid, count in clubs.most_common(3) if count > 1]
        club = axis('clubs', 'Club concentration', clubs_score,
                    f'{biggest_count} of the projected 11 play for {club_name}. Correlated blanks and bad fixtures can hit several at once.',
                    groups or ['Projected starters are spread across different Premier League clubs.'])

        # A difficult/blank PL run matters mainly for players expected to START.
        # Include ALL five scheduled upcoming GWs, weighting by healthy expected
        # contribution so a marginal bench player cannot dominate the radar.
        weighted_difficulty = 0.0
        fixture_weights = 0.0
        blank_hits = 0
        schedule_drivers = []
        for p in xi:
            run = _player_next_fixture_run(p['id'], count=5, start_gw=target)
            if not run:
                continue
            difficulty = sum(float(g.get('difficulty', 3) or 3) for g in run) / len(run)
            weight = max(0.05, p['projection'])
            weighted_difficulty += difficulty * weight
            fixture_weights += weight
            blanks = sum(bool(g.get('is_blank')) for g in run)
            blank_hits += blanks
            schedule_drivers.append((difficulty, p['name'], blanks))
        if fixture_weights:
            avg_diff = weighted_difficulty / fixture_weights
            fixtures_score = _vulnerability_clamp(100 * (avg_diff - 2.0) / 2.65)
            hard = sorted(schedule_drivers, reverse=True)[:3]
            fixtures = axis('fixtures', 'Fixture exposure', fixtures_score,
                            f'Projection-weighted PL fixture difficulty: {avg_diff:.1f}/5 across the next five scheduled GWs' +
                            (f'; {blank_hits} starter blank-GW occurrences.' if blank_hits else '.'),
                            [f'{name}: {difficulty:.1f}/5' + (f' · {blank} blanks' if blank else '')
                             for difficulty, name, blank in hard])
        else:
            fixtures = axis('fixtures', 'Fixture exposure', 50,
                            'No future Premier League fixture data is available.',
                            ['This axis is omitted from the overall score until fixtures are available.'], False)

        # Losing the two top assets is a separate compound shock from the
        # individual-position tests above (depth). No hypothetical free agents.
        top2 = sorted(xi, key=lambda p: p['projection'], reverse=True)[:2]
        without_two = _best_projected_xi([p for p in players if p['id'] not in {p['id'] for p in top2}])
        two_loss = max(0.0, (xi_total - float(without_two['total'])) / xi_total) if without_two else 1.0
        fragility_score = _vulnerability_clamp(100 * two_loss / 0.25)
        fragility = axis('fragility', 'Two-star shock', fragility_score,
                         f'If both top-projected starters were unavailable, the best legal XI would lose {two_loss:.0%} of expected output' +
                         ('.' if without_two else ' and could not be formed.'),
                         [f"{p['name']}: {p['projection']:.1f} projected pts" for p in top2])

        axes = [star, medical, depth, club, fixtures, fragility]
        active_weights = sum(scores_weight[x['key']] for x in axes if x['available'])
        overall = sum(x['score'] * scores_weight[x['key']] for x in axes if x['available']) / active_weights
        result[manager] = {'as_of_gw': target, 'overall': _vulnerability_clamp(overall),
                           'xi_projection_healthy': round(xi_total, 1),
                           'axes': axes, 'warning': None}
    return result


squad_vulnerability_json = json.dumps(build_squad_vulnerability_data(), ensure_ascii=False)


# ============================================================
# FIVE-GW SQUAD PLANNER — actual fixture-specific player forecasts
# ============================================================
def _build_five_gw_planner():
    # The McDraft schedule and the PL schedule use the same FPL event numbers.
    # Exclude completed weeks, but include the active GW when appropriate.
    first_gw = int(dashboard_target_gw or (max(finished_gws, default=0) + 1))
    future_gws = sorted({int(gw) for gw in full_fixture_schedule if int(gw) >= first_gw})[:5]
    if not future_gws:
        future_gws = sorted({int(f.get('event')) for f in _all_pl_fixtures
                             if f.get('event') is not None and int(f['event']) >= first_gw})[:5]
    if not future_gws:
        return {m:{'weeks':[],'suggestions':[],'total':0,'warning':'No future fixtures available.'} for m in managers}

    roster_map = _current_roster_by_manager()
    roster_map_fallback = globals().get('current_rosters_by_manager', {})
    all_owned = {int(pid) for pids in roster_map.values() for pid in pids}
    free_by_position = defaultdict(list)
    for pid, meta in elements.items():
        if int(pid) not in all_owned:
            pos = positions_lookup.get(meta.get('element_type'), '')
            if pos in ('GKP','DEF','MID','FWD'):
                free_by_position[pos].append(int(pid))

    def project(pid, gw):
        return round(float(_player_weekly_projection(pid, _global_position_baselines,
                      _global_league_player_mean, target_gw=gw) or 0), 3)

    def player_row(pid, gw):
        meta = elements.get(pid, {})
        components = _player_fixture_components(pid, gw)
        return {'id':int(pid), 'name':meta.get('web_name', f'Player {pid}'),
                'position':positions_lookup.get(meta.get('element_type'), ''),
                'club':_pl_team_meta_by_id.get(int(meta.get('team') or 0), {}).get('short_name','—'),
                'projection':project(pid,gw),
                'availability':round(_availability_factor(pid,gw),2),
                'status':_fpl_availability.get(pid,{}).get('status','a'),
                'news':_fpl_availability.get(pid,{}).get('news',''),
                'fixtures':[{'opponent':f.get('opponent','—'), 'home':bool(f.get('is_home')),
                             'difficulty':_fixture_difficulty_from_multiplier(f.get('multiplier',1))}
                            for f in components]}

    result = {}
    for manager in managers:
        roster = [int(pid) for pid in (roster_map.get(manager) or roster_map_fallback.get(manager, []))]
        weeks = []
        for gw in future_gws:
            pool = [player_row(pid, gw) for pid in roster]
            best = _best_projected_xi(pool)
            starters = sorted((best or {}).get('players', []),
                              key=lambda x:({'GKP':0,'DEF':1,'MID':2,'FWD':3}.get(x['position'],4),-x['projection']))
            starter_ids = {p['id'] for p in starters}
            bench = sorted([p for p in pool if p['id'] not in starter_ids],
                           key=lambda p:p['projection'], reverse=True)
            xi = round(sum(p['projection'] for p in starters), 2)
            # Match the season simulator's selection-efficiency convention;
            # present XI totals separately to keep the two distinguishable.
            selection = float(current_squad_strength.get(manager,{}).get('selection_efficiency',90) or 90)
            managed = round(xi * min(1.0,max(.75,selection/100.0)) + .05 * sum(p['projection'] for p in bench[:4]), 2)
            opponents = [f.get('team2') if f.get('team1') == manager else f.get('team1')
                         for f in full_fixture_schedule.get(gw,[])
                         if manager in (f.get('team1'),f.get('team2'))]
            by_pos = defaultdict(float)
            for p in starters: by_pos[p['position']] += p['projection']
            weeks.append({'gw':gw,'opponent':' / '.join(str(x) for x in opponents if x) or 'TBC',
                          'xi':xi,'managed':managed,
                          'formation': f"{best['formation']['DEF']}-{best['formation']['MID']}-{best['formation']['FWD']}" if best else '—',
                          'starters':starters,'bench':bench,'by_position':dict(by_pos),
                          'blank_count':sum(1 for p in pool if not p['fixtures']),
                          'double_count':sum(1 for p in pool if len(p['fixtures'])>1),
                          'bench_cover':round(sum(p['projection'] for p in bench[:4]),2),
                          'flagged_count':sum(1 for p in pool if p.get('status')!='a' or p.get('availability',1)<0.75)})

        # Weaknesses are derived from the planned five actual XIs, not from a
        # duplicate generic season-points metric. Only offer currently free players.
        needed = sorted(('GKP','DEF','MID','FWD'),
                        key=lambda pos:float(positional_need_map.get(manager,{}).get(pos,{}).get('need_score',50)),
                        reverse=True)
        suggestions = []
        base_total = sum(w['xi'] for w in weeks)
        # Limit candidates per position before re-solving full five-week XIs.
        for pos in needed:
            candidates = sorted(free_by_position.get(pos,[]),
                                key=lambda pid:sum(project(pid,gw) for gw in future_gws),
                                reverse=True)[:7]
            for pid in candidates:
                best_gain = 0.0; best_out = None
                same_pos = [own for own in roster if positions_lookup.get(elements.get(own,{}).get('element_type')) == pos]
                for outgoing in same_pos:
                    total = 0.0
                    new_ids = [r for r in roster if r != outgoing] + [pid]
                    for gw in future_gws:
                        xi_best = _best_projected_xi([player_row(r,gw) for r in new_ids])
                        total += float((xi_best or {}).get('total',0) or 0)
                    gain = total-base_total
                    if gain > best_gain:
                        best_gain, best_out = gain, outgoing
                if best_out is not None and best_gain > .1:
                    suggestions.append({'id':pid,'name':elements.get(pid,{}).get('web_name',f'Player {pid}'),
                                        'position':pos,'gain':round(best_gain,2),
                                        'drop_id':best_out,
                                        'drop_name':elements.get(best_out,{}).get('web_name',str(best_out)),
                                        'need':round(float(positional_need_map.get(manager,{}).get(pos,{}).get('need_score',50)),0),
                                        'fixtures':_player_next_fixture_run(pid,5,start_gw=future_gws[0])})
        suggestions.sort(key=lambda row:(-row['gain'],-row['need']))
        worst = min(weeks,key=lambda w:w['xi']) if weeks else None
        best_week = max(weeks,key=lambda w:w['xi']) if weeks else None
        result[manager] = {'weeks':weeks,'total':round(base_total,1),
                           'worst_gw':worst['gw'] if worst else None,
                           'best_gw':best_week['gw'] if best_week else None,
                           'suggestions':suggestions[:6],
                           'warning':None if roster else 'No current roster is available for this manager.'}
    return result

five_gw_planner_data = _build_five_gw_planner()
five_gw_planner_json = json.dumps(five_gw_planner_data, ensure_ascii=False)

# ---------------------------- Waiver Intelligence (v55) ----------------------------
# Read-only model: uses captured standings and public current rosters, not
# private competing claims. No event ledger or historical mutation.
def _waiver_intelligence_payload():
    league_order = list(reversed(current_standings))
    future_start = max(max(finished_gws, default=0) + 1,
                       int(dashboard_target_gw or 1) + (1 if dashboard_game_state in ('live', 'upcoming') else 0))
    next_gws = sorted({int(gw) for gw in full_fixture_schedule if int(gw) >= future_start})[:5]
    if not next_gws:
        next_gws = sorted({int(f.get('event')) for f in _all_pl_fixtures
                           if f.get('event') is not None and int(f['event']) >= future_start})[:5]
    if not next_gws:
        next_gws = [future_start + i for i in range(5)]

    rosters = {m: [int(pid) for pid in _trade_rosters.get(m, [])] for m in managers}
    all_owned = {pid for ids in rosters.values() for pid in ids}
    # The current Draft element-status pool can be broader than stored rosters.
    all_owned.update(int(pid) for pid, owner in _analytics_owner_by_id.items() if owner in managers)
    by_position = defaultdict(list)
    for pid, meta in elements.items():
        try:
            pid = int(pid)
        except (TypeError, ValueError):
            continue
        if pid in all_owned or not meta.get('draft_active', True):
            continue
        pos = positions_lookup.get(meta.get('element_type'), '')
        if pos in ('GKP', 'DEF', 'MID', 'FWD'):
            by_position[pos].append(pid)

    proj_cache = {}
    def proj(pid, gw):
        key = (int(pid), int(gw))
        if key not in proj_cache:
            proj_cache[key] = round(float(_player_weekly_projection(
                int(pid), _global_position_baselines, _global_league_player_mean,
                target_gw=int(gw)) or 0), 3)
        return proj_cache[key]

    # A generous selection of realistic targets at every position. This is
    # independent of any manager's own roster, so competition can be estimated.
    candidate_ids = []
    for pos, ids in by_position.items():
        scored = sorted(ids, key=lambda pid: (
            -sum(proj(pid, gw) for gw in next_gws[:3]),
            -float(elements[pid].get('total_points', 0) or 0), pid
        ))
        candidate_ids.extend(scored[:22])
    candidate_ids = list(dict.fromkeys(candidate_ids))

    base_week = {}
    for manager, ids in rosters.items():
        base_week[manager] = {}
        for gw in next_gws:
            players = [{'id': pid, 'position': positions_lookup.get(elements.get(pid, {}).get('element_type'), ''),
                        'projection': proj(pid, gw)} for pid in ids]
            result = _best_projected_xi(players)
            base_week[manager][gw] = float(result['total']) if result else 0.0

    # Candidate x manager x horizon, assessed by re-solving a legal best XI.
    interests = {m: {} for m in league_order}
    targets = []
    for pid in candidate_ids:
        meta = elements[pid]
        pos = positions_lookup.get(meta.get('element_type'), '')
        candidate = {
            'id': pid, 'name': meta.get('web_name', f'Player {pid}'), 'position': pos,
            'club': teams_lookup.get(meta.get('team'), '—'),
            'season_points': float(meta.get('total_points', 0) or 0),
            'next_projection': round(proj(pid, next_gws[0]), 2),
            'next_three': round(sum(proj(pid, gw) for gw in next_gws[:3]), 2),
            'availability': _fpl_availability.get(pid, {}).get('status', 'a'),
            'news': _fpl_availability.get(pid, {}).get('news', ''),
            'fixtures': [row.get('label', '—') for row in _player_next_fixture_run(pid, 3, start_gw=next_gws[0])],
        }
        per_manager = {}
        for manager in league_order:
            ids = rosters.get(manager, [])
            outgoing = [out for out in ids if positions_lookup.get(elements.get(out, {}).get('element_type'), '') == pos]
            if not outgoing:
                per_manager[manager] = {'gains': {'1': 0., '3': 0., '5': 0.}, 'drops': {}, 'need': 0., 'best_drop': None}
                continue
            best = {1: (-float('inf'), None), 3: (-float('inf'), None), 5: (-float('inf'), None)}
            for out in outgoing:
                new_roster = [p for p in ids if p != out] + [pid]
                running = 0.0
                for index, gw in enumerate(next_gws, start=1):
                    player_rows = [{'id': p, 'position': positions_lookup.get(elements.get(p, {}).get('element_type'), ''),
                                    'projection': proj(p, gw)} for p in new_roster]
                    result = _best_projected_xi(player_rows)
                    running += float(result['total']) - base_week[manager].get(gw, 0) if result else 0.0
                    if index in (1, 3, 5) and running > best[index][0]:
                        best[index] = (running, out)
                # For early season or partial schedule, repeat the last horizon.
                if len(next_gws) < 5 and running > best[5][0]: best[5] = (running, out)
                if len(next_gws) < 3 and running > best[3][0]: best[3] = (running, out)
            pos_need = float(positional_need_map.get(manager, {}).get(pos, {}).get('need_score', 50) or 50)
            row = {'gains': {str(h): round(max(0., gain if gain != -float('inf') else 0.), 2) for h, (gain, _) in best.items()},
                   'drops': {str(h): {'id': out, 'name': elements.get(out, {}).get('web_name', f'Player {out}')}
                             for h, (_, out) in best.items() if out is not None},
                   'need': round(pos_need), 'best_drop': best[3][1]}
            per_manager[manager] = row
            interests[manager][pid] = row
        candidate['managers'] = per_manager
        targets.append(candidate)

    # Model each rival's interest by relative projected value *within the same
    # positional free-agent pool*; a manager with better options at the same
    # position is less likely to contest this particular name.
    ranked_rival_targets = {m: defaultdict(list) for m in league_order}
    for manager in league_order:
        for candidate in targets:
            row = candidate['managers'][manager]
            ranked_rival_targets[manager][candidate['position']].append((
                candidate['id'], float(row['gains'].get('3', 0)), float(row['need'])))
        for pos in ranked_rival_targets[manager]:
            ranked_rival_targets[manager][pos].sort(key=lambda t: (-t[1], -t[2], t[0]))
    for candidate in targets:
        pos = candidate['position']
        for manager in league_order:
            row = candidate['managers'][manager]
            rank = next((i for i, item in enumerate(ranked_rival_targets[manager][pos], start=1)
                         if item[0] == candidate['id']), 99)
            row['pos_rank'] = rank
            gain = float(row['gains'].get('3', 0))
            need = float(row['need'])
            row['interest'] = ('Strong' if gain >= 2.0 and rank <= 4 and need >= 35
                               else 'Possible' if gain >= 0.7 and rank <= 10 and need >= 20
                               else 'Limited')

    # Interest assessment deliberately has no fabricated claim success %.
    return {
        'league_order': league_order,
        'standings': [{'manager': m, 'league_rank': current_standings.index(m) + 1,
                       'priority': league_order.index(m) + 1,
                       'lp': int(league_points.get(m, 0)),
                       'pf': round(float(points_for.get(m, 0)), 1)} for m in league_order],
        'target_gw': next_gws[0], 'horizon_gws': next_gws,
        'state': dashboard_game_state,
        'candidates': targets,
        'model_note': 'Estimates based on current roster needs and projected XI gains; rivals’ private claims are not accessible.',
    }


waiver_intelligence_json = json.dumps(_waiver_intelligence_payload(), ensure_ascii=False, separators=(',', ':'))


def waiver_intelligence_html():
    return '''<div class="wi-shell">
      <div class="card wi-intro">
        <span class="relationship-eyebrow">READ THE ROOM BEFORE CLAIMING</span>
        <h2>Waiver Intelligence</h2>
        <p class="card-description">Bottom of the completed McDraft table gets first priority. When a manager wins a claim, they move to the back for that gameweek. We assess your likely competition using earlier managers’ squad weaknesses and projected XI improvements. <b>We cannot see their private waiver requests or promise that any player will survive.</b></p>
        <div class="wi-controls">
          <label>My McDraft team<select id="wi-manager" onchange="renderWaiverIntelligence()"></select></label>
          <label>Value horizon<select id="wi-horizon" onchange="renderWaiverIntelligence()"><option value="1">Next GW</option><option value="3" selected>Next 3 GWs</option><option value="5">Next 5 GWs</option></select></label>
          <label>Pick strategy<select id="wi-strategy" onchange="renderWaiverIntelligence()"><option value="balanced">Balance value &amp; competition</option><option value="value">Highest projected XI gain</option><option value="realistic">Less-contested targets first</option></select></label>
          <label>Position<select id="wi-position" onchange="renderWaiverIntelligence()"><option value="">All positions</option><option value="GKP">Goalkeepers</option><option value="DEF">Defenders</option><option value="MID">Midfielders</option><option value="FWD">Forwards</option></select></label>
        </div>
        <div class="wi-stats" id="wi-stats"></div>
        <div id="wi-priority" class="wi-priority" aria-label="Estimated waiver queue"></div>
        <div id="wi-notice" class="wi-notice"></div>
      </div>
      <div class="wi-grid">
        <div class="card wi-market">
          <div class="wi-heading"><div><h2>Target board</h2><p class="card-description">Projected improvement to your legal best XI, not just player form. Claim pressure shows estimated competition among teams currently ahead of you.</p></div><span class="muted" id="wi-count"></span></div>
          <div class="wi-chip-row"><input id="wi-search" class="wi-search" type="search" placeholder="Search free agents…" oninput="renderWaiverIntelligence()" aria-label="Search free agents"><label class="wi-toggle"><input id="wi-hide-risk" type="checkbox" onchange="renderWaiverIntelligence()"> Hide heavily contested</label><label class="wi-toggle"><input id="wi-positive-only" type="checkbox" checked onchange="renderWaiverIntelligence()"> Projected XI upgrades only</label></div>
          <div id="wi-assumed" class="wi-assumed"></div>
          <div class="wi-target-scroll" id="wi-target-list"></div>
        </div>
        <div class="card wi-ladder-card">
          <h2>My claim ladder</h2><p class="card-description">Build an ordered shortlist, choose backups, and copy it into your FPL Draft waiver requests. Nothing is submitted automatically.</p>
          <div id="wi-claim-ladder" class="wi-ladder"></div>
          <div class="wi-ladder-actions"><button type="button" class="relationship-reset" onclick="autoWaiverLadder()">Build sensible shortlist</button><button type="button" class="relationship-reset" onclick="copyWaiverLadder()">Copy claim order</button><button type="button" class="relationship-reset" onclick="clearWaiverLadder()">Clear</button></div>
          <div class="wi-notice" id="wi-ladder-notice" aria-live="polite"></div>
          <div class="wi-how"><h3>How to use it</h3><p>Your highest-priority requests go first. A speculative top pick can still be worth submitting, because an unsuccessful claim does not move you back. After a successful claim you move to the back for that GW, so line up realistic fallbacks as well. Claims for different players with the same outgoing player act as alternatives: once one succeeds, others involving that outgoing player become invalid.</p><p>After waivers process, free agency opens; check actual availability in FPL Draft before submitting any move.</p></div>
        </div>
      </div>
    </div>'''

# ---------------------------- Manager War Room ----------------------------
def _build_manager_war_room(planner_data):
    roster_map = _current_roster_by_manager()
    roster_map_fallback = globals().get('current_rosters_by_manager', {})
    all_owned = {int(pid) for pids in roster_map.values() for pid in pids}
    free_by_position = defaultdict(list)
    for pid, meta in elements.items():
        if int(pid) in all_owned:
            continue
        pos = positions_lookup.get(meta.get('element_type'), '')
        if pos in ('GKP','DEF','MID','FWD'):
            free_by_position[pos].append(int(pid))

    def project(pid, gw):
        return round(float(_player_weekly_projection(
            pid, _global_position_baselines, _global_league_player_mean, target_gw=gw
        ) or 0), 3)

    def row(pid, gw):
        meta = elements.get(pid, {}) or {}
        return {
            'id': int(pid),
            'name': meta.get('web_name', f'Player {pid}'),
            'position': positions_lookup.get(meta.get('element_type'), '—'),
            'club': _pl_team_meta_by_id.get(int(meta.get('team') or 0), {}).get('short_name', '—'),
            'projection': project(pid, gw),
            'availability': round(_availability_factor(pid, gw), 2),
            'status': _fpl_availability.get(pid, {}).get('status', 'a'),
            'news': _fpl_availability.get(pid, {}).get('news', ''),
        }

    payload = {}
    for manager in managers:
        plan = planner_data.get(manager, {}) or {}
        weeks = plan.get('weeks', []) or []
        if not weeks:
            payload[manager] = {'warning': 'No upcoming fixture is available yet.'}
            continue
        week = weeks[0]
        gw = int(week.get('gw') or 0)
        opponent = str(week.get('opponent') or 'TBC').split(' / ')[0]
        opp_plan = planner_data.get(opponent, {}) or {}
        opp_week = next((w for w in (opp_plan.get('weeks', []) or []) if int(w.get('gw', -1)) == gw), None)

        own_xi = week.get('starters', []) or []
        opp_xi = (opp_week or {}).get('starters', []) or []
        own_bench = week.get('bench', []) or []
        opp_bench = (opp_week or {}).get('bench', []) or []

        def enrich_importance(starters, bench):
            pool = list(starters) + list(bench)
            if not pool:
                return [], []
            max_projection = max([float(p.get('projection', 0) or 0) for p in pool] or [1.0]) or 1.0
            enriched = []
            for player in pool:
                p = dict(player)
                projection = float(p.get('projection', 0) or 0)
                pos = p.get('position')
                alternatives = [float(a.get('projection', 0) or 0) for a in pool if a.get('id') != p.get('id') and a.get('position') == pos]
                best_alt = max(alternatives) if alternatives else 0.0
                replacement_gap = max(0.0, projection - best_alt)
                projection_component = 65.0 * min(1.0, projection / max_projection)
                gap_component = 35.0 * min(1.0, replacement_gap / max(1.0, projection))
                p['importance'] = round(min(100.0, projection_component + gap_component), 1)
                p['replacement_gap'] = round(replacement_gap, 2)
                p['importance_label'] = ('Critical' if p['importance'] >= 80 else 'High' if p['importance'] >= 65 else 'Medium' if p['importance'] >= 45 else 'Low')
                enriched.append(p)
            starters_ids = {p.get('id') for p in starters}
            return ([p for p in enriched if p.get('id') in starters_ids], [p for p in enriched if p.get('id') not in starters_ids])

        own_xi, own_bench = enrich_importance(own_xi, own_bench)
        opp_xi, opp_bench = enrich_importance(opp_xi, opp_bench)
        own_by_pos = {p: round(float((week.get('by_position', {}) or {}).get(p, 0) or 0), 2) for p in ('GKP','DEF','MID','FWD')}
        opp_by_pos = {p: round(float(((opp_week or {}).get('by_position', {}) or {}).get(p, 0) or 0), 2) for p in ('GKP','DEF','MID','FWD')}
        positional = []
        for pos in ('GKP','DEF','MID','FWD'):
            diff = round(own_by_pos[pos] - opp_by_pos[pos], 2)
            positional.append({'position': pos, 'you': own_by_pos[pos], 'opponent': opp_by_pos[pos], 'edge': diff})

        roster = [int(pid) for pid in (roster_map.get(manager) or roster_map_fallback.get(manager, []))]
        base_pool = [row(pid, gw) for pid in roster]
        base_best = _best_projected_xi(base_pool)
        base_total = float((base_best or {}).get('total', 0) or 0)
        upgrades = []
        for pos in ('GKP','DEF','MID','FWD'):
            own_pos = [pid for pid in roster if positions_lookup.get(elements.get(pid, {}).get('element_type')) == pos]
            candidates = sorted(free_by_position.get(pos, []), key=lambda pid: project(pid, gw), reverse=True)[:10]
            for incoming in candidates:
                best_gain, best_out = 0.0, None
                for outgoing in own_pos:
                    candidate_ids = [pid for pid in roster if pid != outgoing] + [incoming]
                    candidate_best = _best_projected_xi([row(pid, gw) for pid in candidate_ids])
                    total = float((candidate_best or {}).get('total', 0) or 0)
                    gain = total - base_total
                    if gain > best_gain:
                        best_gain, best_out = gain, outgoing
                if best_out is not None and best_gain > 0.10:
                    upgrades.append({
                        'in_id': incoming,
                        'in_name': elements.get(incoming, {}).get('web_name', f'Player {incoming}'),
                        'out_id': best_out,
                        'out_name': elements.get(best_out, {}).get('web_name', f'Player {best_out}'),
                        'position': pos,
                        'gain': round(best_gain, 2),
                        'incoming_projection': project(incoming, gw),
                        'outgoing_projection': project(best_out, gw),
                    })
        upgrades.sort(key=lambda r: (-r['gain'], -r['incoming_projection'], r['in_name']))

        own_flags = [p for p in (week.get('starters', []) + week.get('bench', [])) if p.get('status') != 'a' or float(p.get('availability', 1) or 0) < .75]
        opp_flags = [p for p in (((opp_week or {}).get('starters', []) or []) + ((opp_week or {}).get('bench', []) or [])) if p.get('status') != 'a' or float(p.get('availability', 1) or 0) < .75]

        odds = None
        if opponent in managers and int(fixture_prediction_gw or 0) == gw:
            odds_raw = _fixture_odds_for_match(manager, opponent)
            if odds_raw:
                odds = {
                    'you_win': round(float(odds_raw.get('team1_win', 0)), 1),
                    'draw': round(float(odds_raw.get('draw', 0)), 1),
                    'opponent_win': round(float(odds_raw.get('team2_win', 0)), 1),
                    'you_mean': round(float(odds_raw.get('team1_mean', 0)), 1),
                    'opponent_mean': round(float(odds_raw.get('team2_mean', 0)), 1),
                    'you_low': round(float(odds_raw.get('team1_low', 0)), 1),
                    'you_high': round(float(odds_raw.get('team1_high', 0)), 1),
                    'opponent_low': round(float(odds_raw.get('team2_low', 0)), 1),
                    'opponent_high': round(float(odds_raw.get('team2_high', 0)), 1),
                    'confidence': (odds_raw.get('confidence') or {}).get('label', '—'),
                }

        largest_edge = max(positional, key=lambda r: abs(r['edge'])) if positional else None
        keys = []
        if largest_edge:
            if largest_edge['edge'] > 0:
                keys.append(f"Your biggest positional edge is {largest_edge['position']} (+{largest_edge['edge']:.1f} projected points).")
            elif largest_edge['edge'] < 0:
                keys.append(f"The largest matchup concern is {largest_edge['position']} ({largest_edge['edge']:.1f} projected points versus the opponent).")
        if own_flags:
            keys.append(f"You have {len(own_flags)} flagged squad asset{'s' if len(own_flags)!=1 else ''} to monitor before GW{gw}.")
        if opp_flags:
            keys.append(f"{opponent} have {len(opp_flags)} flagged squad asset{'s' if len(opp_flags)!=1 else ''}; their projected XI could move before kickoff.")
        if upgrades:
            keys.append(f"The strongest available one-move waiver improvement currently adds about {upgrades[0]['gain']:.1f} projected XI points for GW{gw}.")
        if not keys:
            keys.append('No single risk or positional mismatch dominates this matchup on the current projections.')

        payload[manager] = {
            'gw': gw,
            'opponent': opponent,
            'you': {
                'xi': round(float(week.get('xi', 0) or 0), 2),
                'managed': round(float(week.get('managed', 0) or 0), 2),
                'formation': week.get('formation', '—'),
                'bench_cover': round(float(week.get('bench_cover', 0) or 0), 2),
                'starters': own_xi,
                'bench': own_bench,
                'flags': own_flags,
            },
            'opponent_team': {
                'xi': round(float((opp_week or {}).get('xi', 0) or 0), 2),
                'managed': round(float((opp_week or {}).get('managed', 0) or 0), 2),
                'formation': (opp_week or {}).get('formation', '—'),
                'bench_cover': round(float((opp_week or {}).get('bench_cover', 0) or 0), 2),
                'starters': opp_xi,
                'bench': opp_bench,
                'flags': opp_flags,
            },
            'positional': positional,
            'upgrades': upgrades[:8],
            'odds': odds,
            'keys': keys[:4],
        }
    return payload


def manager_war_room_html():
    return '''<div class="war-room-shell">
      <div class="card war-room-hero">
        <div><span class="relationship-eyebrow">NEXT MATCHUP · DECISION SUPPORT</span><h2>Manager War Room</h2><p class="card-description">Prepare for the next McDraft fixture with two projected formations on the pitch, benches, positional matchup edges, availability risk and next-GW-specific free-agent improvements. Click any player for opponent, injury risk, projected points and team importance.</p></div>
        <label class="war-room-manager-select">Manager<select id="war-room-manager" onchange="renderManagerWarRoom()"></select></label>
      </div>
      <div id="war-room-content"></div>
    </div>'''


manager_war_room_json = json.dumps(_build_manager_war_room(five_gw_planner_data), ensure_ascii=False)


def build_trade_targets(manager, limit=12):
    own_ids = _trade_rosters.get(manager, [])
    if not own_ids:
        return []
    own_metrics = [_player_current_metrics(pid) for pid in own_ids]
    own_proj = {pid: _trade_player_projection(pid) for pid in own_ids}
    club_counts = defaultdict(int)
    for p in own_metrics:
        club_counts[p["team"]] += 1

    own_by_pos = defaultdict(list)
    for p in own_metrics:
        own_by_pos[p["position"]].append(p)
    for pos in own_by_pos:
        own_by_pos[pos].sort(key=lambda p: own_proj.get(p["id"], 0))

    targets = []
    for seller in managers:
        if seller == manager:
            continue
        seller_ids = _trade_rosters.get(seller, [])
        seller_pos_counts = defaultdict(int)
        for sid in seller_ids:
            seller_pos_counts[_player_current_metrics(sid)["position"]] += 1

        for pid in seller_ids:
            cand = _player_current_metrics(pid)
            pos = cand["position"]
            if pos not in own_by_pos or not own_by_pos[pos]:
                continue
            target_proj = _trade_player_projection(pid)
            weakest = own_by_pos[pos][0]
            replace_proj = own_proj.get(weakest["id"], 0.0)
            upgrade = target_proj - replace_proj
            if upgrade <= -0.35:
                continue

            # Need: league-relative positional weakness. A manager stacked at MID
            # should not be pushed toward another midfielder while an anaemic FWD
            # line is ignored. This score also powers the My Team need map.
            need = float(positional_need_map.get(manager, {}).get(pos, {}).get("need_score", 50.0))

            # Attainability: only propose like-for-like positional swaps.
            # A midfielder target should suggest a midfielder going the other way, etc.
            offer_pool = list(own_by_pos.get(pos, []))
            best_offer = min(offer_pool, key=lambda p: abs(own_proj.get(p["id"],0)-target_proj), default=weakest)
            value_gap = abs(own_proj.get(best_offer["id"], 0) - target_proj)
            attainability = max(0.0, 100.0 - value_gap * 30.0)

            # Seller depth: standard Draft roster sizes mean DEF/MID depth matters most.
            expected_min = {"GKP":2, "DEF":5, "MID":5, "FWD":3}.get(pos, 3)
            surplus = max(0, seller_pos_counts.get(pos,0) - expected_min)
            seller_flex = min(100.0, 45.0 + surplus*25.0)

            # Club concentration risk. Third asset from one PL club gets a modest penalty; fourth+ a large one.
            existing_same_club = club_counts.get(cand["team"], 0)
            diversification = max(5.0, 100.0 - max(0, existing_same_club-1)*28.0)

            form_score = max(0.0, min(100.0, 20.0 + cand["form"]*12.0))
            upgrade_score = max(0.0, min(100.0, 50.0 + upgrade*24.0))
            fixture_run = _player_next_fixture_run(pid, 3)
            fixture_score_raw = _fixture_run_score(pid, 3)
            fixture_fit = max(0.0, min(100.0, 50.0 + ((fixture_score_raw - 1.0) * 100.0)))
            fit = 0.26*upgrade_score + 0.29*need + 0.16*attainability + 0.08*seller_flex + 0.08*diversification + 0.07*form_score + 0.06*fixture_fit
            realism = 0.55*attainability + 0.25*seller_flex + 0.20*diversification

            targets.append({
                **cand, "owner": seller, "projection": target_proj,
                "replace_name": weakest["name"], "replace_projection": replace_proj,
                "upgrade": upgrade, "fit_score": round(fit,1), "realism_score": round(realism,1),
                "offer_name": best_offer["name"], "offer_projection": own_proj.get(best_offer["id"],0),
                "same_club_owned": existing_same_club,
                "position_need": round(need, 1),
                "next_fixtures": fixture_run,
                "fixture_run_score": round(fixture_score_raw, 3),
                "player_value": _player_model_by_id.get(int(pid),{}).get("player_value",50),
                "projected_season_points": _player_model_by_id.get(int(pid),{}).get("projected_season_points",0),
                "hot_cold_score": _player_model_by_id.get(int(pid),{}).get("hot_cold_score",0),
                "hot_cold_label": _player_model_by_id.get(int(pid),{}).get("hot_cold_label","Neutral"),
            })
    targets.sort(key=lambda x:(-x["fit_score"], -x["realism_score"], -x["projection"], x["name"]))
    # Avoid one selling team monopolising the recommendations.
    selected, per_seller = [], defaultdict(int)
    for t in targets:
        if per_seller[t["owner"]] >= 3:
            continue
        selected.append(t); per_seller[t["owner"]] += 1
        if len(selected) >= limit: break
    return selected


trade_targets = {m: build_trade_targets(m) for m in current_standings}
trade_targets_json = json.dumps(trade_targets, ensure_ascii=False)

_player_search_by_id={int(r.get('id',0) or 0):r for r in player_search_data}
def build_sell_high_candidates(manager, limit=6):
    rows=[]
    for pid in _trade_rosters.get(manager,[]):
        p=_player_search_by_id.get(int(pid),{})
        if not p: continue
        pos=_player_current_metrics(pid).get('position')
        heat=float(p.get('hot_cold_score',0) or 0)
        fixture=float(_fixture_run_score(pid,3) or 1.0)
        need=float(positional_need_map.get(manager,{}).get(pos,{}).get('need_score',50) or 50)
        # High stock = hot recent output, tougher road ahead, and not a desperate positional need.
        score=(0.48*max(0,heat)) + (36.0*max(0,1.03-fixture)) + (0.18*max(0,55-need)) + (0.10*float(p.get('player_value',50) or 50))
        if score < 10: continue
        rows.append({
            'id':pid,'name':p.get('name','Unknown'),'position':pos,'team':p.get('team','—'),
            'stock_score':round(score,1),'heat':round(heat,1),'heat_label':p.get('hot_cold_label','Neutral'),
            'player_value':p.get('player_value',50),'projected_season_points':p.get('projected_season_points',0),
            'next_fixtures':p.get('next_fixtures',[]),'fixture_run_score':round(fixture,3),
            'position_need':round(need,1),
        })
    rows.sort(key=lambda r:(-r['stock_score'],-r['player_value']))
    return rows[:limit]

sell_high_candidates={m:build_sell_high_candidates(m) for m in current_standings}
sell_high_candidates_json=json.dumps(sell_high_candidates,ensure_ascii=False)


# ---------------------------- Availability impact ----------------------------
def _availability_impact_charts():
    """Build current-team availability impact from official FPL flags.

    Next-GW 'points at risk' is full-availability model projection minus the
    availability-adjusted projection. It is NOT realized historical points lost;
    GW histories do not record a reliable reason for every player's absence.
    """
    from collections import defaultdict

    clubs = sorted(set(teams_lookup.values()))
    owner_by_id = {
        int(pid): manager
        for manager, ids in _trade_rosters.items()
        for pid in ids
    }
    original_board = history.get('original_draft_rank', {}) or {}

    # Avoid attributing a newly re-used FPL element ID to a departed original
    # draftee. If we pinned a GW1 identity, it must still match the current one.
    original_identities = {}
    gw1 = history.get('gameweeks', {}).get('1', {})
    for squad in (gw1.get('teams', {}) or {}).values():
        for pick in (squad.get('starters', []) or []) + (squad.get('bench', []) or []):
            if pick.get('element_id') is not None and pick.get('web_name'):
                original_identities[int(pick['element_id'])] = str(pick['web_name']).casefold().strip()

    def original_draft_entry(pid):
        entry = original_board.get(str(pid), {}) or {}
        if not entry:
            return None
        try:
            rank = int(entry.get('overall_pick', 9999))
        except (TypeError, ValueError):
            return None
        if not 1 <= rank <= DRAFTED_PLAYER_COUNT:
            return None
        if pid in original_identities:
            now_name = str(elements.get(pid, {}).get('web_name') or '').casefold().strip()
            if now_name != original_identities[pid]:
                return None
        return entry

    team_risk = {m: 0.0 for m in managers}
    injury_risk = {m: 0.0 for m in managers}
    suspension_risk = {m: 0.0 for m in managers}
    team_absent = {m: 0 for m in managers}
    team_injured = {m: 0 for m in managers}
    team_suspended = {m: 0 for m in managers}
    team_doubtful = {m: 0 for m in managers}
    team_drafted_out = {m: 0 for m in managers}
    original_manager_losses = {m: 0 for m in managers}
    club_risk = {c: 0.0 for c in clubs}
    club_absent = {c: 0 for c in clubs}
    club_drafted_out = {c: 0 for c in clubs}
    club_owned_flagged = {c: 0 for c in clubs}
    club_doubt = {c: 0 for c in clubs}
    club_new = {c: 0 for c in clubs}
    absent_statuses = {'i', 's', 'u', 'n'}
    affected_owned = set()
    original_out_owned = set()

    for row in injury_list_rows:
        pid = int(row.get('id') or 0)
        meta = elements.get(pid, {})
        club = teams_lookup.get(meta.get('team')) or row.get('team') or 'Unknown'
        manager = owner_by_id.get(pid)
        status = str(row.get('status') or 'a')
        risk = max(0.0, float(row.get('points_at_risk') or 0))
        draft = original_draft_entry(pid)
        club_risk[club] = club_risk.get(club, 0) + risk
        if status in absent_statuses:
            club_absent[club] = club_absent.get(club, 0) + 1
            if draft:
                club_drafted_out[club] = club_drafted_out.get(club, 0) + 1
                original_manager = draft.get('manager')
                if original_manager in original_manager_losses:
                    original_manager_losses[original_manager] += 1
        if status == 'd':
            club_doubt[club] = club_doubt.get(club, 0) + 1
        if manager not in team_risk:
            continue  # PL chart includes free agents; fantasy chart excludes them.
        team_risk[manager] += risk
        if status == 'i':
            injury_risk[manager] += risk
            team_injured[manager] += 1
        elif status == 's':
            suspension_risk[manager] += risk
            team_suspended[manager] += 1
        elif status == 'd':
            team_doubtful[manager] += 1
        if status in absent_statuses:
            affected_owned.add(pid)
            team_absent[manager] += 1
            if draft:
                team_drafted_out[manager] += 1
                original_out_owned.add(pid)
        if status != 'a' or risk > 0:
            club_owned_flagged[club] = club_owned_flagged.get(club, 0) + 1

    for row in new_health_events:
        club = row.get('team') or 'Unknown'
        club_new[club] = club_new.get(club, 0) + 1

    # Percent-of-roster comparison prevents a 3-player injury problem looking
    # the same for a team missing 3 starters vs a team missing fringe options.
    healthy_by_team = {m: 0.0 for m in managers}
    for manager, ids in _trade_rosters.items():
        if manager not in healthy_by_team:
            continue
        healthy_by_team[manager] = sum(
            _player_weekly_projection(int(pid), _global_position_baselines,
                                      _global_league_player_mean,
                                      target_gw=dashboard_target_gw,
                                      apply_availability=False)
            for pid in ids if int(pid) in elements
        )
    risk_share = {
        m: round(100 * team_risk[m] / healthy_by_team[m], 1)
        if healthy_by_team[m] > 0 else 0.0
        for m in managers
    }

    # Illustrative five-week trend, regenerates each build. Future health
    # probabilities regress toward 100%; this is NOT a confirmed return date.
    future_gws = [int(e['id']) for e in bootstrap.get('events', [])
                  if e.get('id') is not None
                  and dashboard_target_gw <= int(e['id']) < dashboard_target_gw + 5]
    flagged_by_id = {int(row['id']): row for row in injury_list_rows}
    projected_risk_by_gw = {}
    for manager, ids in _trade_rosters.items():
        if manager not in managers:
            continue
        projected_risk_by_gw[manager] = []
        for gw in future_gws:
            projected_loss = 0.0
            for pid in ids:
                pid = int(pid)
                if pid not in flagged_by_id or pid not in elements:
                    continue
                healthy = _player_weekly_projection(
                    pid, _global_position_baselines, _global_league_player_mean,
                    target_gw=gw, apply_availability=False)
                projected_loss += healthy * (1.0 - _availability_factor(pid, gw))
            projected_risk_by_gw[manager].append((gw, round(projected_loss, 2)))

    kpis = [
        ('Next GW points at risk', f'{sum(team_risk.values()):.1f}',
         'Across currently owned McDraft squads'),
        ('Currently unavailable', str(len(affected_owned)),
         'Injured, suspended, unavailable or ineligible'),
        ('Drafted assets unavailable', str(len(original_out_owned)),
         'Originally drafted players on current rosters'),
        ('Fantasy squads affected', str(sum(bool(team_absent[m] or team_doubtful[m]) for m in managers)),
         'At least one unavailable or doubtful player'),
    ]
    summary = ''.join(
        f'<div class="stat-card"><div class="stat-label">{escape_html(label)}</div>'
        f'<div class="stat-value">{escape_html(value)}</div>'
        f'<div class="stat-description">{escape_html(note)}</div></div>'
        for label, value, note in kpis
    )
    availability_status_mix = {
        'Injured': sum(team_injured.values()),
        'Suspended': sum(team_suspended.values()),
        'Doubtful': sum(team_doubtful.values()),
        'Other unavailable': max(0, sum(team_absent.values()) - sum(team_injured.values()) - sum(team_suspended.values())),
    }
    total_charts = [
        _pie_chart_html('Share of next-GW points at risk', team_risk,
            'League-wide availability drag split across current McDraft squads.', manager_colours=True),
        _pie_chart_html('Share of unavailable owned players', team_absent,
            'Current unavailable assets split across the ten McDraft squads.', manager_colours=True),
        _pie_chart_html('Unavailable original draft picks by original manager', original_manager_losses,
            'Who originally drafted the unavailable assets, whether or not they still own them.', manager_colours=True),
        _pie_chart_html('Current availability issue mix', availability_status_mix,
            'League-wide current flags across owned players.',
            category_colours={'Injured':'#f87171','Suspended':'#fb923c','Doubtful':'#facc15','Other unavailable':'#a78bfa'}),
    ]

    fantasy_charts = [
        _bar_chart_html('Estimated next-GW points at risk by fantasy team', team_risk,
            'Healthy-squad projected points minus availability-adjusted projections. Current McDraft owners only.',
            x_label='McDraft manager', y_label='Projected points at risk'),
        _bar_chart_html('Injury-specific points at risk', injury_risk,
            'Current injured players only. An estimate, not actual points previously lost.',
            x_label='McDraft manager', y_label='Projected next-GW points'),
        _bar_chart_html('Unavailable players per fantasy squad', team_absent,
            'FPL statuses: injured, suspended, unavailable and ineligible; doubtful players shown separately.',
            x_label='McDraft manager', y_label='Players'),
        _bar_chart_html('Original draft picks currently unavailable', team_drafted_out,
            'Originally drafted assets now unavailable on each CURRENT squad, regardless of who drafted them.',
            x_label='Current manager', y_label='Drafted players'),
        _bar_chart_html('Draft-night picks now unavailable by original drafter', original_manager_losses,
            'Attributed to whoever drafted each player, even if that player has since been traded or released.',
            x_label='Original drafting manager', y_label='Players'),
        _bar_chart_html('Percentage of squad projection at risk', risk_share,
            'Estimated unavailable output relative to the whole current squad if everyone were fully available.',
            value_suffix='%', x_label='McDraft manager', y_label='Projected points at risk'),
        _bar_chart_html('Injured players per fantasy squad', team_injured,
            x_label='McDraft manager', y_label='Players'),
        _bar_chart_html('Suspended players per fantasy squad', team_suspended,
            x_label='McDraft manager', y_label='Players'),
        _bar_chart_html('Doubtful players per fantasy squad', team_doubtful,
            x_label='McDraft manager', y_label='Players'),
    ]
    if future_gws:
        fantasy_charts.append(_line_chart_html('Projected availability drag: next five GWs',
            projected_risk_by_gw,
            'Illustrative forecast at current ownership. Future availability regresses toward healthy; no medical return date is assumed.',
            x_label='Upcoming gameweek', y_label='Projected points at risk'))
    club_charts = [
        _category_bar_chart_html('Estimated next-GW points at risk by Premier League club',
            list(club_risk.items()), 'Includes free agents and McDraft-owned players.',
            x_label='Premier League club', y_label='Projected next-GW points', limit=20),
        _category_bar_chart_html('Unavailable players by Premier League club',
            list(club_absent.items()), 'Injured, suspended, unavailable and ineligible.',
            x_label='Premier League club', y_label='Players', limit=20),
        _category_bar_chart_html('Originally drafted players currently unavailable by club',
            list(club_drafted_out.items()), 'Current club and availability of original McDraft selections, including released assets.',
            x_label='Premier League club', y_label='Drafted players', limit=20),
        _category_bar_chart_html('Flagged McDraft-owned assets by Premier League club',
            list(club_owned_flagged.items()), 'Players on CURRENT McDraft squads with a flag or reduced next-GW availability.',
            x_label='Premier League club', y_label='Owned players', limit=20),
        _category_bar_chart_html('Doubtful players by Premier League club',
            list(club_doubt.items()), x_label='Premier League club', y_label='Players', limit=20),
        _category_bar_chart_html('New or changed reports by Premier League club',
            list(club_new.items()), 'Since the last successful dashboard build. First run establishes a baseline.',
            x_label='Premier League club', y_label='Reports', limit=20),
    ]
    return (
        '<div class="card analytics-impact-intro"><h2>Availability impact · McDraft & PL clubs</h2>'
        '<p class="card-description">How current injuries, suspensions and doubtful players affect '
        'fantasy rosters and Premier League clubs. Points at risk are estimated for the NEXT gameweek '
        'from full-availability versus availability-adjusted projections; they are not confirmed historical '
        'points lost. Original draft metrics only include identities still matching their pinned history.</p>'
        f'<div class="stats-grid">{summary}</div>'
        f'<p class="health-data-note">Latest official FPL flags · GW{dashboard_target_gw} · '
        f'{escape_html(health_analytics_data["generated_at"])}</p></div>'
        '<h2 class="analytics-impact-group-title">League-wide totals</h2>'
        f'<div class="analytics-chart-grid">{"".join(total_charts)}</div>'
        '<h2 class="analytics-impact-group-title">McDraft fantasy-team impact</h2>'
        f'<div class="analytics-chart-grid">{"".join(fantasy_charts)}</div>'
        '<h2 class="analytics-impact-group-title">Premier League club impact</h2>'
        f'<div class="analytics-chart-grid">{"".join(club_charts)}</div>'
        '<p class="health-data-note">For individual players, changes in injury reports and '
        'departures, use Players → Availability &amp; Departures.</p>'
    )


# ---------------------------- Player Relationship Graph ----------------------------
# All network identities remain Draft-ID keyed; the corrected CSV-backed
# `elements` lookup supplies the display identity/statistics independently.
def _player_relationship_payload():
    from itertools import combinations

    roster_ids = {manager: set(map(int, pids)) for manager, pids in _trade_rosters.items()}
    owner_now = {int(pid): owner for pid, owner in _analytics_owner_by_id.items()}
    current_links = {}
    for manager, pids in roster_ids.items():
        for a, b in combinations(sorted(pids), 2):
            current_links[(a, b)] = {"team": manager}

    # GW snapshots are the evidence of actual shared time on a manager's squad.
    # Do not fabricate a relationship from sequential ownership alone.
    historical = {}
    observed_players = set(owner_now)
    for gw_str, snapshot in (history.get("gameweeks") or {}).items():
        if not snapshot.get("finished"):
            continue
        try:
            gw = int(gw_str)
        except (TypeError, ValueError):
            continue
        for squad in (snapshot.get("teams") or {}).values():
            manager = squad.get("manager")
            if not manager:
                continue
            pids = set()
            for pick in (squad.get("starters") or []) + (squad.get("bench") or []):
                try:
                    pids.add(int(pick["element_id"]))
                except (TypeError, ValueError, KeyError):
                    continue
            observed_players.update(pids)
            for a, b in combinations(sorted(pids), 2):
                row = historical.setdefault((a, b), {"gws": set(), "teams": set()})
                row["gws"].add(gw)
                row["teams"].add(manager)

    trade_links = {}
    trade_by_player = defaultdict(list)
    for trade in normalised_trades:
        if str(trade.get("status", "")).casefold() != "processed":
            continue
        offered = set()
        received = set()
        for item in trade.get("player_ids1", []):
            try:
                offered.add(int(item))
            except (TypeError, ValueError):
                continue
        for item in trade.get("player_ids2", []):
            try:
                received.add(int(item))
            except (TypeError, ValueError):
                continue
        if not offered or not received:
            continue
        observed_players.update(offered | received)
        trade_meta = {
            "gw": trade.get("gw"),
            "date": trade.get("date"),
            "offered_by": trade.get("manager1"),
            "received_by": trade.get("manager2"),
            "offered_ids": sorted(offered),
            "received_ids": sorted(received),
        }
        for pid in offered | received:
            trade_by_player[pid].append(trade_meta)
        for a in offered:
            for b in received:
                if a == b:
                    continue  # malformed self-trades cannot link a player to itself
                key = tuple(sorted((a, b)))
                row = trade_links.setdefault(key, {"count": 0, "gws": set(), "teams": set()})
                row["count"] += 1
                if str(trade.get("gw") or "").isdigit():
                    row["gws"].add(int(trade["gw"]))
                row["teams"].update([trade.get("manager1"), trade.get("manager2")])

    # Historical/current squads and executed trades can reference former Draft
    # players absent from today's bootstrap. Prefer snapshot-pinned names then.
    past_names = {}
    for gw_str in sorted((history.get("gameweeks") or {}), key=lambda k: int(k) if str(k).isdigit() else 0):
        for squad in ((history["gameweeks"].get(gw_str) or {}).get("teams") or {}).values():
            for pick in (squad.get("starters") or []) + (squad.get("bench") or []):
                try:
                    pid = int(pick.get("element_id"))
                except (TypeError, ValueError):
                    continue
                if pick.get("web_name"):
                    past_names[pid] = pick["web_name"]

    # Historical ownership can include departed or waived players with no
    # completed-snapshot data yet (legacy history imports).
    observed_players.update(int(pid) for pid in player_ownership)
    total_points = {
        int(row["id"]): int(row.get("season_points", 0) or 0)
        for row in player_form_stats if row.get("id") is not None
    }
    draft = history.get("original_draft_rank", {}) or {}
    nodes = []
    for pid in sorted(observed_players):
        meta = elements.get(pid) or {}
        position = positions_lookup.get(meta.get("element_type"), "—")
        club = teams_lookup.get(meta.get("team"), "—")
        draft_row = draft.get(str(pid), {}) or {}
        pick = draft_row.get("overall_pick")
        nodes.append({
            "id": pid,
            "name": meta.get("web_name") or past_names.get(pid) or player_ownership.get(pid, {}).get("name") or f"Draft player #{pid}",
            "owner": owner_now.get(pid) or "Free Agent",
            "club": club,
            "position": position,
            "points": total_points.get(pid, int(meta.get("total_points", 0) or 0)),
            "draft_pick": pick if isinstance(pick, int) and 1 <= pick <= DRAFTED_PLAYER_COUNT else None,
            "fpl_id": meta.get("fpl_player_id", fpl_id_for_draft(pid)),
        })
    edges = []
    keys = set(current_links) | set(historical) | set(trade_links)
    for a, b in sorted(keys):
        shared = historical.get((a, b), {})
        swap = trade_links.get((a, b), {})
        edges.append({
            "a": a, "b": b,
            "current": (a, b) in current_links,
            "current_team": (current_links.get((a, b)) or {}).get("team"),
            "shared_gws": len(shared.get("gws", [])),
            "shared_teams": sorted(shared.get("teams", [])),
            "trade_count": swap.get("count", 0),
            "trade_gws": sorted(swap.get("gws", [])),
        })
    return {
        "nodes": nodes, "edges": edges,
        "trades": {str(pid): rows for pid, rows in trade_by_player.items()},
        "summary": {
            "players": len(nodes),
            "current": len(current_links),
            "historical": len(historical),
            "traded": len(trade_links),
        },
    }


player_relationships_json = json.dumps(_player_relationship_payload(), ensure_ascii=False, separators=(",", ":"))


def player_relationship_html():
    return '''<div class="card relationship-intro">
      <div><span class="relationship-eyebrow">PLAYER CONNECTIONS · LIVE ROSTERS + ARCHIVE</span>
      <h2>Player Relationship Graph</h2>
      <p class="card-description">See who shares a squad today, who played together in completed gameweeks, and who was exchanged in a <b>processed trade</b>. Nodes use current McDraft owner colours; grey means free agent. Click a player to uncover their entire network.</p></div>
      <div class="relationship-mode-controls" role="group" aria-label="Relationship type">
        <button class="relationship-mode active" type="button" data-rel-mode="current" onclick="setRelationshipMode('current')">Current squadmates</button>
        <button class="relationship-mode" type="button" data-rel-mode="history" onclick="setRelationshipMode('history')">Shared history</button>
        <button class="relationship-mode" type="button" data-rel-mode="trades" onclick="setRelationshipMode('trades')">Trade connections</button>
        <button class="relationship-mode" type="button" data-rel-mode="all" onclick="setRelationshipMode('all')">All relationships</button>
      </div>
      <div class="relationship-controls">
        <label>Show owner<select id="relationship-owner" onchange="setRelationshipOwner(this.value)"><option value="all">All selected managers</option></select></label>
        <label>Find a player<input id="relationship-search" type="search" list="relationship-players" placeholder="Search any player…" onkeydown="if(event.key==='Enter')focusRelationshipSearch()" onchange="focusRelationshipSearch()"><datalist id="relationship-players"></datalist></label>
        <label>Minimum shared GWs<select id="relationship-weeks" onchange="setRelationshipWeeks(this.value)"><option value="1">1+ GW</option><option value="2">2+ GWs</option><option value="3">3+ GWs</option><option value="5">5+ GWs</option><option value="10">10+ GWs</option></select></label>
        <label class="relationship-check"><input id="relationship-full-links" type="checkbox" onchange="setRelationshipAllLinks(this.checked)"> Show all links</label>
        <button class="relationship-reset" type="button" onclick="resetRelationshipFocus()">Clear focus</button>
      </div>
      <div id="relationship-stats" class="relationship-stats" aria-live="polite"></div>
      <div class="relationship-main">
        <div class="relationship-graph-panel">
          <div class="relationship-graph-toolbar"><span id="relationship-caption">Select a player or explore the squads</span><div><button type="button" onclick="zoomRelationship(0.8)" aria-label="Zoom in">＋</button><button type="button" onclick="zoomRelationship(1.25)" aria-label="Zoom out">－</button><button type="button" onclick="zoomRelationship(1, true)">Reset view</button></div></div>
          <svg id="relationship-svg" role="img" aria-label="Interactive McDraft player relationship network" viewBox="0 0 960 590" preserveAspectRatio="xMidYMid meet"><title>Player relationships, click a node to explore</title></svg>
          <div id="relationship-empty" class="notice" hidden></div>
          <div class="relationship-legend"><span><i style="background:#60a5fa"></i> Current teammates</span><span><i style="background:#34d399"></i> Shared completed GWs</span><span><i style="background:#fb923c"></i> Exchanged in processed trade</span><span><i style="background:#64748b"></i> Free agents</span></div>
        </div>
        <aside class="relationship-detail" id="relationship-detail"><h3>Explore the network</h3><p>Select a player to see their current owner, former squadmates, shared gameweeks and trade connections.</p></aside>
      </div>
      <p class="relationship-footnote" id="relationship-footnote">Default view shows the strongest connections to avoid a wall of lines. Use “Show all links” to see the full network. The shared Analytics manager filter applies here too.</p>
    </div>'''

# ---------------------------- Transfer River + Player Passport ----------------------------
def _transfer_river_passport_payload():
    observed = set()
    for pid in (player_ownership or {}).keys():
        try:
            observed.add(int(pid))
        except (TypeError, ValueError):
            pass
    for pid in elements.keys():
        try:
            observed.add(int(pid))
        except (TypeError, ValueError):
            pass
    for pid_text in (history.get('original_draft_rank', {}) or {}).keys():
        try:
            observed.add(int(pid_text))
        except (TypeError, ValueError):
            pass
    for row in transfer_movements:
        try:
            observed.add(int(row.get('player_id')))
        except (TypeError, ValueError):
            pass
    for snapshot in (history.get('gameweeks', {}) or {}).values():
        for squad in ((snapshot or {}).get('teams', {}) or {}).values():
            for pick in (squad.get('starters') or []) + (squad.get('bench') or []):
                try:
                    observed.add(int(pick.get('element_id')))
                except (TypeError, ValueError):
                    continue

    owner_by_gw = defaultdict(dict)
    name_by_snapshot = {}
    for gw in finished_gws:
        snap = (history.get('gameweeks', {}) or {}).get(str(gw), {}) or {}
        for squad in (snap.get('teams') or {}).values():
            manager = squad.get('manager') or 'Unknown'
            for pick in (squad.get('starters') or []) + (squad.get('bench') or []):
                try:
                    pid = int(pick.get('element_id'))
                except (TypeError, ValueError):
                    continue
                owner_by_gw[pid][gw] = manager
                if pick.get('web_name'):
                    name_by_snapshot[pid] = pick.get('web_name')

    current_owner = {int(pid): owner for pid, owner in (_dashboard_current_owner or {}).items()}
    points_lookup = {int(row.get('id')): float(row.get('season_points', 0) or 0) for row in player_form_stats if row.get('id') is not None}
    original = history.get('original_draft_rank', {}) or {}

    river_edges = defaultdict(lambda: {'moves': 0, 'players': set(), 'gws': set(), 'kinds': defaultdict(int), 'points': 0.0})
    journeys = defaultdict(list)
    for pid_text, info in original.items():
        try:
            pid = int(pid_text)
            pick = int(info.get('overall_pick', UNDRAFTED_PLAYER_RANK) or UNDRAFTED_PLAYER_RANK)
        except (TypeError, ValueError):
            continue
        manager = info.get('manager')
        if not manager or pick > DRAFTED_PLAYER_COUNT:
            continue
        edge = river_edges[('Draft Night', manager)]
        edge['moves'] += 1
        edge['players'].add(pid)
        edge['gws'].add(0)
        edge['kinds']['Drafted'] += 1
        edge['points'] += float(points_lookup.get(pid, elements.get(pid, {}).get('total_points', 0) or 0))
        journeys[pid].append({'gw': 0, 'source': 'Draft Night', 'target': manager, 'kind': 'Drafted', 'label': f'Original draft pick #{pick}'})

    trade_move_index = defaultdict(list)
    for trade in normalised_trades:
        if str(trade.get('status', '')).lower() != 'processed':
            continue
        try:
            gw = int(trade.get('gw', 0) or 0)
        except (TypeError, ValueError):
            gw = 0
        m1 = trade.get('manager1') or 'Unknown'
        m2 = trade.get('manager2') or 'Unknown'
        for pid in trade.get('player_ids1', []) or []:
            try:
                pid = int(pid)
            except (TypeError, ValueError):
                continue
            pname = elements.get(pid, {}).get('web_name') or name_by_snapshot.get(pid) or f'Player {pid}'
            trade_move_index[pid].append({'gw': gw, 'kind': 'Trade', 'from_team': m1, 'to_team': m2, 'summary': f'{m1} traded {pname} to {m2}'})
        for pid in trade.get('player_ids2', []) or []:
            try:
                pid = int(pid)
            except (TypeError, ValueError):
                continue
            pname = elements.get(pid, {}).get('web_name') or name_by_snapshot.get(pid) or f'Player {pid}'
            trade_move_index[pid].append({'gw': gw, 'kind': 'Trade', 'from_team': m2, 'to_team': m1, 'summary': f'{m2} traded {pname} to {m1}'})

    for row in _all_activity_movements_for_market_pages():
        try:
            pid = int(row.get('player_id'))
        except (TypeError, ValueError):
            continue
        gw = int(row.get('gw', 0) or 0)
        from_team = row.get('from_team') or 'Free Agent'
        to_team = row.get('to_team') or 'Free Agent'
        if from_team == to_team:
            continue
        kind = row.get('move') or row.get('action') or 'Move'
        edge = river_edges[(from_team, to_team)]
        edge['moves'] += 1
        edge['players'].add(pid)
        edge['gws'].add(gw)
        edge['kinds'][kind] += 1
        edge['points'] += float(points_lookup.get(pid, elements.get(pid, {}).get('total_points', 0) or 0))
        journeys[pid].append({'gw': gw, 'source': from_team, 'target': to_team, 'kind': kind, 'label': f'GW{gw} · {kind}'})

    players = []
    passports = {}
    movers = []
    for pid in sorted(observed):
        meta = elements.get(pid, {}) or {}
        draft_row = original.get(str(pid), {}) or {}
        name = meta.get('web_name') or name_by_snapshot.get(pid) or player_ownership.get(pid, {}).get('name') or f'Player #{pid}'
        club = teams_lookup.get(meta.get('team'), '—')
        position = positions_lookup.get(meta.get('element_type'), '—')
        total_points = float(points_lookup.get(pid, meta.get('total_points', 0) or 0))
        current = current_owner.get(pid, 'Free Agent')
        player_gw_owner = {gw: owner_by_gw.get(pid, {}).get(gw, 'Free Agent') for gw in finished_gws}
        stints = []
        if finished_gws:
            active_owner = player_gw_owner.get(finished_gws[0], 'Free Agent')
            start_gw = finished_gws[0]
            for gw in finished_gws[1:]:
                owner = player_gw_owner.get(gw, 'Free Agent')
                if owner != active_owner:
                    pts = sum(float(player_form.get(pid, {}).get(g, 0) or 0) for g in finished_gws if start_gw <= g < gw)
                    stints.append({'owner': active_owner, 'start_gw': start_gw, 'end_gw': gw - 1, 'points': round(pts, 1)})
                    active_owner = owner
                    start_gw = gw
            pts = sum(float(player_form.get(pid, {}).get(g, 0) or 0) for g in finished_gws if g >= start_gw)
            stints.append({'owner': active_owner, 'start_gw': start_gw, 'end_gw': finished_gws[-1], 'points': round(pts, 1)})

        owner_points = defaultdict(float)
        owner_weeks = defaultdict(int)
        for gw in finished_gws:
            owner = player_gw_owner.get(gw, 'Free Agent')
            owner_points[owner] += float(player_form.get(pid, {}).get(gw, 0) or 0)
            owner_weeks[owner] += 1
        owner_breakdown = [
            {'owner': owner, 'points': round(points, 1), 'weeks': owner_weeks.get(owner, 0)}
            for owner, points in owner_points.items()
        ]
        owner_breakdown.sort(key=lambda row: (-row['points'], row['owner']))

        movement_rows = []
        for step in journeys.get(pid, []):
            movement_rows.append({'gw': step['gw'], 'kind': step['kind'], 'from': step['source'], 'to': step['target'], 'summary': step['label']})
        for trade_row in trade_move_index.get(pid, []):
            movement_rows.append({'gw': trade_row['gw'], 'kind': 'Trade', 'from': trade_row['from_team'], 'to': trade_row['to_team'], 'summary': trade_row['summary']})
        seen = set()
        dedup = []
        for item in sorted(movement_rows, key=lambda r: (r['gw'], r['kind'], r['from'], r['to'], r['summary'])):
            key = (item['gw'], item['kind'], item['from'], item['to'], item['summary'])
            if key in seen:
                continue
            seen.add(key)
            dedup.append(item)
        movement_rows = sorted(dedup, key=lambda r: (r['gw'], r['kind'] != 'Drafted', r['from'], r['to']))

        passport = {
            'id': pid,
            'name': name,
            'club': club,
            'position': position,
            'current_owner': current,
            'total_points': round(total_points, 1),
            'original_manager': draft_row.get('manager') or 'Undrafted / unknown',
            'original_pick': int(draft_row.get('overall_pick')) if str(draft_row.get('overall_pick', '')).isdigit() else None,
            'official_rank': _official_draft_rank(pid),
            'blended_rank': _blended_draft_rank(pid),
            'transactions': movement_rows,
            'stints': stints,
            'owner_breakdown': owner_breakdown,
            'fpl_id': meta.get('fpl_player_id', fpl_id_for_draft(pid)),
        }
        passports[str(pid)] = passport
        players.append({'id': pid, 'name': name, 'owner': current, 'club': club, 'position': position, 'points': round(total_points, 1)})
        movers.append({'id': pid, 'name': name, 'moves': len([m for m in movement_rows if m['gw'] > 0]), 'owner': current, 'points': round(total_points, 1)})

    movers.sort(key=lambda row: (-row['moves'], -row['points'], row['name']))
    edges = []
    for (source, target), info in river_edges.items():
        edges.append({
            'source': source,
            'target': target,
            'moves': info['moves'],
            'players': sorted(info['players']),
            'player_names': [passports.get(str(pid), {}).get('name', f'Player {pid}') for pid in sorted(info['players'])[:8]],
            'gws': sorted(g for g in info['gws'] if g),
            'kinds': dict(info['kinds']),
            'points': round(info['points'], 1),
        })

    journey_payload = {}
    for pid, rows in journeys.items():
        ordered = sorted(rows, key=lambda r: (r['gw'], r['kind'] != 'Drafted', r['source'], r['target']))
        journey_payload[str(pid)] = ordered

    return {
        'players': players,
        'passports': passports,
        'river_edges': edges,
        'journeys': journey_payload,
        'top_movers': movers[:18],
        'summary': {
            'players': len(players),
            'edges': len(edges),
            'moves': int(sum(edge['moves'] for edge in edges if edge['source'] != 'Draft Night')),
        },
    }


transfer_river_passport_json = json.dumps(_transfer_river_passport_payload(), ensure_ascii=False, separators=(',', ':'))


def transfer_river_passport_html():
    return '''<div class="card river-passport-card">
      <div class="river-passport-head"><div><span class="relationship-eyebrow">MARKET FLOWS · OWNERSHIP BIOGRAPHIES</span>
      <h2>The Transfer River + Player Passport</h2>
      <p class="card-description">Follow the season’s player movement between McDraft teams, then drill into any individual player’s full biography: original draft slot, current owner, scoring by owner, roster stints and key transactions. The shared Analytics manager filter controls the league-wide River view; searching for a player opens their full Passport.</p></div>
      <div class="river-passport-tools">
        <label>Find a player<input id="passport-player-search" type="search" list="passport-player-list" placeholder="Search any player…" onchange="focusPassportSearch()" onkeydown="if(event.key==='Enter')focusPassportSearch()"><datalist id="passport-player-list"></datalist></label>
        <div class="river-passport-buttons"><button type="button" class="relationship-reset" onclick="focusPassportSearch()">Open passport</button><button type="button" class="relationship-reset" onclick="clearPassportPlayer()">Clear player</button></div>
      </div></div>
      <div id="transfer-river-stats" class="relationship-stats" aria-live="polite"></div>
      <div class="river-passport-layout">
        <div class="river-panel">
          <div class="relationship-graph-toolbar"><span id="transfer-river-caption">Transfer River · selected McDraft teams</span><div class="muted" id="transfer-river-subcaption">League-wide movement view</div></div>
          <div id="transfer-river-chart" class="transfer-river-chart"></div>
          <div id="transfer-river-empty" class="notice" hidden></div>
          <div class="relationship-legend river-legend"><span><i style="background:#64748b"></i> Free agent pool</span><span><i style="background:#94a3b8"></i> Draft night</span><span><i style="background:#38bdf8"></i> League movement</span><span><i style="background:#f59e0b"></i> Focused player journey</span></div>
        </div>
        <aside id="player-passport-detail" class="passport-detail"><h3>Open a passport</h3><p>Search any player above to view their McDraft biography. Without a selected player, the passport panel shows the season’s biggest movers.</p></aside>
      </div>
    </div>'''

# ---------------------------- Analytics Lab ----------------------------
def _bar_chart_html(title, values, description="", value_suffix="", reverse=False, x_label="Manager", y_label="Value"):
    items = [(m, float(values.get(m,0) or 0)) for m in current_standings]
    items.sort(key=lambda x:x[1], reverse=not reverse)
    maximum = max([abs(v) for _,v in items] + [1.0])
    league_avg = statistics.mean([v for _, v in items]) if items else 0.0
    avg_pct = max(0.0, min(100.0, abs(league_avg) / maximum * 100.0))
    bars = ""
    for m,v in items:
        width = max(2.0, abs(v)/maximum*100.0)
        delta = v - league_avg
        colour = manager_color(m)
        bars += f'''<div class="analytics-bar-row" role="button" tabindex="0" data-chart-detail="{escape_html(f'{m} · {y_label}: {v:.1f}{value_suffix}')}" data-analytics-manager="{escape_html(m)}"><div class="analytics-bar-label"><span class="analytics-manager-swatch" style="background:{colour}"></span>{escape_html(m)}</div><div class="analytics-bar-track"><div class="analytics-bar-fill" style="width:{width:.1f}%;background:{colour}"></div><div class="analytics-average-marker" style="left:{avg_pct:.1f}%" title="League average: {league_avg:.1f}{value_suffix}"></div></div><div class="analytics-bar-value">{v:.1f}{value_suffix}<span class="analytics-average-delta"> ({delta:+.1f} vs avg)</span></div></div>'''
    return f'''<div class="card analytics-chart-card analytics-average-capable" data-league-average="{league_avg:.3f}"><h2>{escape_html(title)}</h2>{f'<p class="card-description">{escape_html(description)}</p>' if description else ''}<div class="analytics-axis-title analytics-axis-y">{escape_html(y_label)}</div><div class="analytics-bar-chart">{bars}</div><div class="analytics-average-key">League average: {league_avg:.1f}{value_suffix}</div><div class="analytics-axis-title analytics-axis-x">{escape_html(x_label)}</div></div>'''


def _category_bar_chart_html(title, rows, description="", value_suffix="", x_label="Player", y_label="Value", limit=20, reverse=False):
    clean=[]
    for row in rows:
        try:
            label,raw_value=row[:2]
            value=float(raw_value or 0)
        except (TypeError,ValueError,IndexError):
            continue
        pid=row[2] if len(row)>2 else None
        clean.append((str(label),value,pid))
    is_player_chart=any(pid is not None for _,_,pid in clean)
    clean.sort(key=lambda r:r[1], reverse=not reverse)
    if not is_player_chart:
        clean=clean[:limit]
    maximum=max([abs(v) for _,v,_ in clean[:limit]]+[1.0])
    bars=""
    for idx,(label,value,pid) in enumerate(clean):
        width=max(2.0,abs(value)/maximum*100.0)
        attr=""; colour_style=""
        if is_player_chart and pid is not None:
            try: owner=_analytics_owner_by_id.get(int(pid),'Free agents')
            except (TypeError,ValueError): owner='Free agents'
            colour=manager_color(owner) if owner in managers else '#64748b'
            attr=(f' data-player-id="{escape_html(str(pid))}" data-player-owner="{escape_html(owner)}"'
                  f' data-player-value="{value}" class="analytics-bar-row analytics-player-bar"')
            colour_style=f'background:{colour};'
            if idx >= limit: attr+=' hidden'
        else:
            attr=' class="analytics-bar-row"'
        attr += f' role="button" tabindex="0" data-chart-detail="{escape_html(f"{label} · {y_label}: {value:.1f}{value_suffix}")}"'
        swatch = f'<span class="analytics-manager-swatch" style="{colour_style}"></span>' if colour_style else ''
        bars += (f'<div{attr}><div class="analytics-bar-label" title="{escape_html(label)}">'
                 f'{swatch}{escape_html(label)}</div>'
                 f'<div class="analytics-bar-track"><div class="analytics-bar-fill" style="width:{width:.1f}%;{colour_style}"></div></div>'
                 f'<div class="analytics-bar-value">{value:.1f}{value_suffix}</div></div>')
    empty=f'<div class="notice analytics-player-chart-empty" hidden>No players in this chart for the selected team.</div>' if is_player_chart else ''
    body=bars or '<div class="notice">Not enough data yet.</div>'
    is_player_attr=f' data-player-limit="{limit}"' if is_player_chart else ''
    chart_class=' analytics-player-bar-card' if is_player_chart else ''
    paragraph=f'<p class="card-description">{escape_html(description)}</p>' if description else ''
    return (f'<div class="card analytics-chart-card{chart_class}"{is_player_attr}>'
            f'<h2>{escape_html(title)}</h2>{paragraph}'
            f'<div class="analytics-axis-title analytics-axis-y">{escape_html(y_label)}</div>'
            f'<div class="analytics-bar-chart">{body}{empty}</div>'
            f'<div class="analytics-axis-title analytics-axis-x">{escape_html(x_label)}</div></div>')


def _dual_category_bar_chart_html(title, rows, first_label="Drafted-player points", second_label="All-player points", description="", x_label="Premier League club", y_label="Fantasy points", limit=20):
    clean=[]
    for label, first, second in rows:
        try:
            a=float(first or 0); b=float(second or 0)
        except (TypeError, ValueError):
            continue
        clean.append((str(label), a, b))
    clean.sort(key=lambda x:x[2], reverse=True)
    clean=clean[:limit]
    maximum=max([max(abs(a),abs(b)) for _,a,b in clean]+[1.0])
    body=""
    for label,a,b in clean:
        wa=max(1.5,abs(a)/maximum*100.0); wb=max(1.5,abs(b)/maximum*100.0)
        body += f'''<div class="analytics-dual-row"><div class="analytics-bar-label" title="{escape_html(label)}">{escape_html(label)}</div><div class="analytics-dual-bars"><div class="analytics-dual-series"><span>{escape_html(first_label)}</span><div class="analytics-bar-track"><div class="analytics-bar-fill analytics-bar-fill-secondary" style="width:{wa:.1f}%"></div></div><strong>{a:.0f}</strong></div><div class="analytics-dual-series"><span>{escape_html(second_label)}</span><div class="analytics-bar-track"><div class="analytics-bar-fill" style="width:{wb:.1f}%"></div></div><strong>{b:.0f}</strong></div></div></div>'''
    body = body or '<div class="notice">Not enough data yet.</div>'
    desc = f'<p class="card-description">{escape_html(description)}</p>' if description else ''
    return f'''<div class="card analytics-chart-card"><h2>{escape_html(title)}</h2>{desc}<div class="analytics-axis-title analytics-axis-y">{escape_html(y_label)}</div><div class="analytics-dual-chart">{body}</div><div class="analytics-axis-title analytics-axis-x">{escape_html(x_label)}</div></div>'''

def _pie_chart_html(title, values, description="", value_suffix="", manager_colours=False, category_colours=None):
    """Responsive donut chart for a single part-to-whole snapshot."""
    clean=[]
    for label, raw in values.items():
        try:
            value=max(0.0, float(raw or 0))
        except (TypeError, ValueError):
            continue
        if value > 0:
            clean.append((str(label), value))
    total=sum(value for _, value in clean)
    if total <= 0:
        return f'<div class="card analytics-chart-card"><h2>{escape_html(title)}</h2><div class="notice">Not enough data yet.</div></div>'
    fallback=["#38bdf8","#f472b6","#4ade80","#facc15","#a78bfa","#fb923c","#2dd4bf","#f87171"]
    segments=[]; legend=[]; cursor=0.0
    for idx,(label,value) in enumerate(clean):
        pct=(value/total)*100.0
        colour=(manager_color(label) if manager_colours else ((category_colours or {}).get(label) or fallback[idx % len(fallback)]))
        segments.append(f'{colour} {cursor:.3f}% {cursor+pct:.3f}%')
        legend.append(f'<button type="button" class="analytics-pie-legend-row" data-pie-start="{cursor:.4f}" data-pie-end="{cursor+pct:.4f}" data-chart-detail="{escape_html(f"{label}: {value:.1f}{value_suffix} ({pct:.1f}% of total)")}"><span class="analytics-manager-swatch" style="background:{colour}"></span><span class="analytics-pie-name">{escape_html(label)}</span><strong>{value:.1f}{value_suffix}</strong><small>{pct:.1f}%</small></button>')
        cursor += pct
    desc=f'<p class="card-description">{escape_html(description)}</p>' if description else ''
    total_text=f'{total:.1f}{value_suffix}'
    return (f'<div class="card analytics-chart-card analytics-pie-card"><h2>{escape_html(title)}</h2>{desc}'
            f'<div class="analytics-pie-layout"><div class="analytics-pie" style="background:conic-gradient({", ".join(segments)})"><div class="analytics-pie-hole"><strong>{escape_html(total_text)}</strong><span>Total</span></div></div>'
            f'<div class="analytics-pie-legend">{"".join(legend)}</div></div></div>')

def _line_chart_html(title, series_map, description="", x_label="Gameweek", y_label="Points", invert_y=False):
    all_pts=[(gw,float(v or 0)) for pts in series_map.values() for gw,v in pts]
    if not all_pts:
        return f'<div class="card analytics-chart-card"><h2>{escape_html(title)}</h2><div class="notice">Not enough data yet.</div></div>'
    min_gw,max_gw=min(g for g,_ in all_pts),max(g for g,_ in all_pts)
    min_v,max_v=min(v for _,v in all_pts),max(v for _,v in all_pts)
    if max_v==min_v: max_v=min_v+1
    W,H,PL,PR,PT,PB=760,275,58,20,18,48
    pw,ph=W-PL-PR,H-PT-PB
    def xy(g,v):
        x=PL + (0 if max_gw==min_gw else (g-min_gw)/(max_gw-min_gw)*pw)
        if invert_y:
            y=PT + (v-min_v)/(max_v-min_v)*ph
        else:
            y=PT + (max_v-v)/(max_v-min_v)*ph
        return x,y
    grid=""; labels=""
    for i in range(5):
        val=(min_v+(max_v-min_v)*i/4) if invert_y else (max_v-(max_v-min_v)*i/4); y=PT+ph*i/4
        grid += f'<line class="trend-chart-gridline" x1="{PL}" x2="{W-PR}" y1="{y:.1f}" y2="{y:.1f}" />'
        labels += f'<text class="trend-chart-axis-label" x="4" y="{y+4:.1f}">{val:.0f}</text>'
    for g in sorted(set(g for g,_ in all_pts)):
        x,_=xy(g,min_v)
        labels += f'<text class="trend-chart-axis-label" x="{x:.1f}" y="{H-24}" text-anchor="middle">GW{g}</text>'
    paths=""
    by_gw = defaultdict(list)
    for _m, _pts in series_map.items():
        for _gw, _v in _pts:
            try:
                by_gw[int(_gw)].append(float(_v or 0))
            except Exception:
                pass
    avg_pts = [(g, statistics.mean(vals)) for g, vals in sorted(by_gw.items()) if vals]
    if avg_pts:
        avg_coords=[xy(g,v) for g,v in avg_pts]
        avg_d=" ".join(("M" if i==0 else "L")+f" {x:.1f} {y:.1f}" for i,(x,y) in enumerate(avg_coords))
        paths += f'<path class="trend-chart-line analytics-average-series" d="{avg_d}" />'
    for idx,(m,pts) in enumerate(series_map.items()):
        pts=sorted(pts)
        if not pts: continue
        coords=[xy(g,float(v or 0)) for g,v in pts]
        d=" ".join(("M" if i==0 else "L")+f" {x:.1f} {y:.1f}" for i,(x,y) in enumerate(coords))
        try: color=manager_color(m)
        except Exception: color=f"hsl({(idx*47)%360} 70% 62%)"
        paths += f'<path class="trend-chart-line analytics-manager-mark" data-analytics-manager="{escape_html(m)}" d="{d}" stroke="{color}" />'
        for (gw,val),(cx,cy) in zip(pts,coords):
            detail=escape_html(f'{m} · GW{gw} · {y_label}: {float(val):.1f}')
            paths += (f'<circle class="analytics-manager-mark" data-analytics-manager="{escape_html(m)}" '
                      f'cx="{cx:.1f}" cy="{cy:.1f}" r="8" fill="{color}" fill-opacity="0.65" '
                      f'role="button" tabindex="0" data-chart-detail="{detail}"><title>{detail}</title></circle>')
    axis_titles=(f'<text class="analytics-svg-axis-title" x="{PL+pw/2:.1f}" y="{H-3}" text-anchor="middle">{escape_html(x_label)}</text>'
                 f'<text class="analytics-svg-axis-title" transform="translate(14 {PT+ph/2:.1f}) rotate(-90)" text-anchor="middle">{escape_html(y_label)}</text>')
    return f'''<div class="card analytics-chart-card trend-chart-card"><h2>{escape_html(title)}</h2>{f'<p class="card-description">{escape_html(description)}</p>' if description else ''}<div class="trend-chart-svg-wrap"><svg viewBox="0 0 {W} {H}">{grid}{labels}{paths}{axis_titles}</svg></div></div>'''


def _scatter_chart_html(title, xvals, yvals, description="", x_label="X", y_label="Y", invert_y=False):
    labels=list(dict.fromkeys(list(xvals.keys()) + list(yvals.keys())))
    pts=[(m,float(xvals.get(m,0) or 0),float(yvals.get(m,0) or 0)) for m in labels]
    if not pts: return ""
    xs=[x for _,x,_ in pts]; ys=[y for *_,y in pts]
    xmin,xmax=min(xs),max(xs); ymin,ymax=min(ys),max(ys)
    if xmax==xmin:xmax=xmin+1
    if ymax==ymin:ymax=ymin+1
    W,H,PL,PR,PT,PB=760,290,66,24,18,54; pw=W-PL-PR; ph=H-PT-PB
    grid=""; labels=""
    for i in range(5):
        xv=xmin+(xmax-xmin)*i/4; x=PL+pw*i/4
        yv=(ymin+(ymax-ymin)*i/4) if invert_y else (ymax-(ymax-ymin)*i/4); y=PT+ph*i/4
        grid += f'<line class="trend-chart-gridline" x1="{x:.1f}" x2="{x:.1f}" y1="{PT}" y2="{H-PB}"/><line class="trend-chart-gridline" x1="{PL}" x2="{W-PR}" y1="{y:.1f}" y2="{y:.1f}"/>'
        labels += f'<text class="trend-chart-axis-label" x="{x:.1f}" y="{H-30}" text-anchor="middle">{xv:.1f}</text><text class="trend-chart-axis-label" x="5" y="{y+4:.1f}">{yv:.1f}</text>'
    dots=""
    for idx,(m,x,y) in enumerate(pts):
        cx=PL+(x-xmin)/(xmax-xmin)*pw
        cy=PT+((y-ymin)/(ymax-ymin)*ph if invert_y else (ymax-y)/(ymax-ymin)*ph)
        try: color=manager_color(m)
        except Exception: color=f"hsl({(idx*47)%360} 70% 62%)"
        if m in managers:
            group_attrs = f'class="analytics-manager-mark" role="button" tabindex="0" data-chart-detail="{escape_html(f"{m} · {x_label}: {x:.1f} · {y_label}: {y:.1f}")}" data-analytics-manager="{escape_html(m)}"'
        else:
            group_attrs = f'class="analytics-entity-mark" role="button" tabindex="0" data-chart-detail="{escape_html(f"{m} · {x_label}: {x:.1f} · {y_label}: {y:.1f}")}"'
        dots += f'<g {group_attrs}><circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="{color}"><title>{escape_html(m)}: {x:.1f}, {y:.1f}</title></circle><text class="trend-chart-axis-label" x="{cx+9:.1f}" y="{cy+4:.1f}">{escape_html(m[:18])}</text></g>'
    axis_titles=(f'<text class="analytics-svg-axis-title" x="{PL+pw/2:.1f}" y="{H-3}" text-anchor="middle">{escape_html(x_label)}</text>'
                 f'<text class="analytics-svg-axis-title" transform="translate(14 {PT+ph/2:.1f}) rotate(-90)" text-anchor="middle">{escape_html(y_label)}</text>')
    return f'''<div class="card analytics-chart-card"><h2>{escape_html(title)}</h2>{f'<p class="card-description">{escape_html(description)}</p>' if description else ''}<div class="trend-chart-svg-wrap"><svg viewBox="0 0 {W} {H}">{grid}{labels}{dots}{axis_titles}</svg></div></div>'''



def _player_scatter_chart_html(title, rows, description="", x_label="X", y_label="Y",
                               reverse_x=False, invert_y=False, fixed_x_max=None, fixed_x_min=None):
    """Interactive owner-coloured player scatter. rows = (draft_id, name, x, y).

    All ownership comes from the current Draft element-status snapshot. Player
    identity and scores remain draft-ID keyed (respecting the CSV ID mapping).
    """
    clean=[]
    for pid, name, raw_x, raw_y in rows:
        try:
            x=float(raw_x); y=float(raw_y); pid=int(pid)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(x) or not math.isfinite(y):
            continue
        clean.append((pid,str(name),x,y))
    if not clean:
        return f'<div class="card analytics-chart-card analytics-player-scatter"><h2>{escape_html(title)}</h2><div class="notice">Not enough player data yet.</div></div>'
    xs=[r[2] for r in clean]; ys=[r[3] for r in clean]
    xmin=float(fixed_x_min) if fixed_x_min is not None else min(xs)
    xmax=float(fixed_x_max) if fixed_x_max is not None else max(xs)
    ymin,ymax=min(ys),max(ys)
    if xmin==xmax: xmax=xmin+1
    if ymin==ymax: ymax=ymin+1
    W,H,PL,PR,PT,PB=760,310,68,22,20,55
    pw,ph=W-PL-PR,H-PT-PB
    def scale_x(x):
        fraction=(x-xmin)/(xmax-xmin)
        return PL + ((1.0-fraction) if reverse_x else fraction)*pw
    def scale_y(y):
        fraction=(y-ymin)/(ymax-ymin)
        return PT + (fraction if invert_y else 1.0-fraction)*ph
    grid=""; labels=""
    for i in range(5):
        x=PL+pw*i/4
        x_val=(xmax-(xmax-xmin)*i/4) if reverse_x else (xmin+(xmax-xmin)*i/4)
        y=PT+ph*i/4
        y_val=(ymin+(ymax-ymin)*i/4) if invert_y else (ymax-(ymax-ymin)*i/4)
        grid += (f'<line class="trend-chart-gridline" x1="{x:.1f}" x2="{x:.1f}" y1="{PT}" y2="{H-PB}"/>'
                 f'<line class="trend-chart-gridline" x1="{PL}" x2="{W-PR}" y1="{y:.1f}" y2="{y:.1f}"/>')
        labels += (f'<text class="trend-chart-axis-label" x="{x:.1f}" y="{H-31}" text-anchor="middle">{x_val:.0f}</text>'
                   f'<text class="trend-chart-axis-label" x="5" y="{y+4:.1f}">{y_val:.0f}</text>')
    dots=""
    # Deterministic placement and ID-keyed identity keep same-name players separate.
    for pid,name,x,y in clean:
        owner=_analytics_owner_by_id.get(pid,'Free agents')
        colour=manager_color(owner) if owner in managers else '#64748b'
        cx,cy=scale_x(x),scale_y(y)
        title_text=escape_html(f'{name} · {owner} · {x_label}: {x:.1f} · {y_label}: {y:.1f}')
        dots += (f'<g class="analytics-player-dot" data-chart-detail="{title_text}" data-player-id="{pid}" data-player-owner="{escape_html(owner)}" tabindex="0" role="img" aria-label="{title_text}">'
                 f'<circle class="analytics-player-circle" cx="{cx:.1f}" cy="{cy:.1f}" r="5.3" fill="{colour}" stroke="#0b1220" stroke-width="1"><title>{title_text}</title></circle>'
                 f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="16" fill="transparent" role="button" '
                 f'tabindex="0" data-chart-detail="{title_text}"><title>{title_text}</title></circle>'
                 f'<text class="trend-chart-axis-label analytics-player-dot-label" x="{cx+8:.1f}" y="{cy+3:.1f}">{escape_html(name[:19])}</text></g>')
    axis_titles=(f'<text class="analytics-svg-axis-title" x="{PL+pw/2:.1f}" y="{H-3}" text-anchor="middle">{escape_html(x_label)}</text>'
                 f'<text class="analytics-svg-axis-title" transform="translate(14 {PT+ph/2:.1f}) rotate(-90)" text-anchor="middle">{escape_html(y_label)}</text>')
    note='<p class="card-description">Coloured by current fantasy owner. Grey = free agent. Hover a dot for the player and owner; filter above to isolate a squad.</p>'
    if reverse_x:
        note='<p class="card-description">Draft ranking runs from the largest rank number on the left to #1 on the right. Dots use current fantasy-team colours; hover for details.</p>'
    paragraph = f'<p class="card-description">{escape_html(description)}</p>' if description else note
    return (f'<div class="card analytics-chart-card analytics-player-scatter"><h2>{escape_html(title)}</h2>'
            f'{paragraph}'
            f'<div class="trend-chart-svg-wrap"><svg viewBox="0 0 {W} {H}" role="group" aria-label="{escape_html(title)}">'
            f'{grid}{labels}{dots}{axis_titles}</svg></div><div class="analytics-player-chart-empty" hidden>No players in this chart for the selected team.</div></div>')



def _player_position_totals_chart_html(rows):
    """Current-owner-filterable breakdown; source rows are Draft-ID keyed."""
    pos_names={'GKP':'Goalkeepers','DEF':'Defenders','MID':'Midfielders','FWD':'Forwards'}
    positions=('GKP','DEF','MID','FWD')
    totals={pos:0.0 for pos in positions}
    metadata=[]
    for p in rows:
        pos=str(p.get('position',''))
        if pos not in totals: continue
        try: pid=int(p['id']); pts=float(p.get('season_points',0) or 0)
        except (KeyError,TypeError,ValueError): continue
        owner=_analytics_owner_by_id.get(pid,'Free agents')
        totals[pos]+=pts
        metadata.append((pos,owner,pts,pid))
    largest=max([abs(v) for v in totals.values()]+[1.0])
    bars=''.join(
        (f'<div class="analytics-bar-row" data-player-position="{pos}"><div class="analytics-bar-label">{pos_names[pos]}</div>'
         f'<div class="analytics-bar-track"><div class="analytics-bar-fill" style="width:{max(2,totals[pos]/largest*100):.1f}%"></div></div>'
         f'<div class="analytics-bar-value">{totals[pos]:.0f}</div></div>') for pos in positions
    )
    records=''.join(
        f'<span hidden class="analytics-position-player" data-player-position="{pos}" data-player-owner="{escape_html(owner)}" data-player-points="{pts}" data-player-id="{pid}"></span>'
        for pos,owner,pts,pid in metadata
    )
    return (f'<div class="card analytics-chart-card analytics-player-position-card"><h2>Points by position</h2>'
            '<p class="card-description">Season points contributed by players owned by the selected managers, plus free agents when included. League totals appear with All selected.</p>'
            f'<div class="analytics-bar-chart">{bars}</div>{records}'
            '<div class="analytics-player-chart-empty" hidden>No eligible players for this team.</div></div>')


# v47: Matrix-specific names in logical order: low X/high Y, high X/high Y,
# low X/low Y, high X/low Y. Screen positions account for reversed axes.
MATRIX_QUADRANT_LABELS = {'Form vs quality': ('Punching above weight',
                     'Quality in form',
                     'Underpowered and cold',
                     'Quality not clicking'),
 'Squad quality vs season output': ('Outscoring expectations',
                                    'Quality delivering',
                                    'Modest on both fronts',
                                    'Talent not translating'),
 'Recent form vs season pace': ('Recent resurgence',
                                'Sustained scorers',
                                'Still searching',
                                'Cooling off'),
 '5GW baseline vs 3GW form': ('Recent resurgence',
                              'Strong across both',
                              'Cold across both',
                              'Recent dip'),
 'Quality vs momentum': ('Underdogs on the rise',
                         'Quality gathering pace',
                         'Weak and losing steam',
                         'Quality losing momentum'),
 'Consistency vs recent form': ('Reliable scorers',
                                'Volatile but firing',
                                'Steady but quiet',
                                'Erratic and cold'),
 'Recent form vs win rate': ('Wins despite cold form',
                             'Form and results',
                             'Neither clicking',
                             'Form without the wins'),
 'Draft pedigree vs current quality': ('Pedigree delivers',
                                       'Underdogs delivering',
                                       'High picks underperform',
                                       'Long-shot squad'),
 'Draft pedigree vs recent form': ('Top picks firing',
                                   'Underdogs firing',
                                   'Pedigree in a slump',
                                   'Little pedigree or form'),
 'Elite talent vs squad depth': ('Depth without stars',
                                 'Stars and support',
                                 'Thin across the board',
                                 'Top-heavy talent'),
 'Depth vs projected XI': ('Strong XI, thin bench',
                           'Deep and dangerous',
                           'Thin squad, weak XI',
                           'Depth beyond the XI'),
 'Depth vs star reliance': ('Three players carry',
                            'Deep but star-led',
                            'Shallow but balanced',
                            'Depth across the squad'),
 'Star reliance vs consistency': ('Shared load, erratic',
                                  'Star-driven swings',
                                  'Balanced and steady',
                                  'Stars deliver steadily'),
 'Club diversity vs fragility': ('Stacked and fragile',
                                 'Spread but fragile',
                                 'Stacked yet robust',
                                 'Spread and resilient'),
 'Club concentration vs volatility': ('Diverse but erratic',
                                      'Club stack, big swings',
                                      'Spread and stable',
                                      'Club stack, stable'),
 'Original draft retention vs quality': ('Successful rebuild',
                                         'Original core firing',
                                         'Rebuild needs work',
                                         'Loyal but underpowered'),
 'Defensive spine': ('Defenders lead',
                     'Complete defensive unit',
                     'Defensive weak spot',
                     'Keepers carry defence'),
 'Attacking balance': ('Strikers lead',
                       'Full attacking force',
                       'Attack needs help',
                       'Midfield carries attack'),
 'Elite percentile vs star reliance': ('Reliance without elite',
                                       'Elite stars carry load',
                                       'Few stars, shared load',
                                       'Elite talent shared'),
 'Transfer activity vs ROI': ('Selective, strong return',
                              'Busy and productive',
                              'Quiet, modest return',
                              'Busy, modest return'),
 'Market ROI vs recent momentum': ('Momentum beyond moves',
                                   'Strong ROI and momentum',
                                   'Both metrics subdued',
                                   'ROI without momentum'),
 'Transfer activity vs scoring': ('Set-and-forget scorers',
                                  'Active and scoring',
                                  'Quiet and low scoring',
                                  'Busy, little scoring'),
 'Draft loyalty vs trading': ('Full squad overhaul',
                              'Loyal core, active market',
                              'Rebuilt then settled',
                              'Draft-day loyalists'),
 'Selection efficiency vs scoring': ('Scoring despite choices',
                                     'Sharp and productive',
                                     'Poor choices, low output',
                                     'Good choices, low output'),
 'Bench wastage vs selection': ('Efficient and tidy',
                                'Good calls, strong bench',
                                'Low waste, poor picks',
                                'Bench points squandered'),
 'Bench wastage vs win rate': ('Lean bench, many wins',
                               'Winning despite waste',
                               'Low waste, few wins',
                               'Bench waste, few wins'),
 'Dream-team picks vs win rate': ('Winning without stars',
                                  'Standouts and wins',
                                  'Few standouts or wins',
                                  'Standouts, little reward'),
 'Market ROI vs win rate': ('Winning without ROI',
                            'Trade returns and wins',
                            'Neither metric strong',
                            'Good ROI, few wins'),
 'Squad quality vs H2H return': ('Results exceed pedigree',
                                 'Quality rewarded',
                                 'Weak squad, low return',
                                 'Quality without results'),
 'Expected vs actual league points': ('Surprise points haul',
                                      'High expected and actual',
                                      'Modest on both counts',
                                      'Expected more points'),
 'Season scoring vs league return': ('Low scoring, strong H2H',
                                     'Goals and table points',
                                     'Low scoring, low return',
                                     'Scorers unrewarded'),
 'Scoring vs fixture luck': ('Favourable draw, few pts',
                             'Scoring and good fortune',
                             'Low output, tough luck',
                             'Scoring but unlucky'),
 'Points conceded vs H2H return': ('Kind draw, strong return',
                                   'Thriving in hard fixtures',
                                   'Kind draw, few wins',
                                   'Tough draw, few wins'),
 'Volatility vs luck': ('Steady, favourable swing',
                        'Wild scores, good fortune',
                        'Steady, tough luck',
                        'Erratic and unlucky'),
 'Opponent strength vs win rate': ('Kind draw, many wins',
                                   'Winning tough fixtures',
                                   'Kind draw, few wins',
                                   'Tough draw, few wins'),
 'Current injury risk vs squad quality': ('Strong with low risk',
                                          'Powerhouse under threat',
                                          'Healthy but underpowered',
                                          'Weak and injury-exposed'),
 'Unavailable players vs projected loss': ('Few out, big impact',
                                           'Absences taking a toll',
                                           'Few out, little impact',
                                           'Many out, depth holding'),
 'Injury count vs recent form': ('Healthy and in form',
                                 'Form despite injuries',
                                 'Few injuries, cold form',
                                 'Injury-hit and cold'),
 'Squad fragility vs injury exposure': ('Robust but exposed',
                                        'Brittle and exposed',
                                        'Robust and low risk',
                                        'Brittle but available'),
 'Upcoming fixtures vs recent form': ('In form, kind run',
                                      'In form, tough run',
                                      'Cold but kind fixtures',
                                      'Cold with a hard run'),
 'Upcoming fixtures vs win rate': ('Winning, kind run',
                                   'Winners face tough run',
                                   'Few wins, kind run',
                                   'Few wins, tough run'),
 'Quality vs resilience': ('Resilient but modest',
                           'Strong and resilient',
                           'Weak and brittle',
                           'Strong but brittle'),
 'Club concentration vs injuries': ('Spread and injury-hit',
                                    'Club stack, injury-hit',
                                    'Spread and available',
                                    'Club stack, healthy')}

# ---------------------------- Matrix Lab ----------------------------
def _matrix_chart_html(title, x_values, y_values, *, group, x_label, y_label,
                       description='', quadrants=None, reverse_x=False,
                       reverse_y=False, require_gws=False):
    """Manager-coloured, shared-filter-compatible quadrant scatter.

    Crosshair is fixed to whole-league medians, even when the user filters to
    one manager; this makes comparisons meaningful across filter changes.
    Unknown/missing values are skipped rather than silently plotting at zero.
    """
    if require_gws and not finished_gws:
        return (f'<div class="card analytics-chart-card matrix-card" data-matrix-group="{escape_html(group)}">'
                f'<h2>{escape_html(title)}</h2><div class="notice">Waiting for completed gameweeks.</div></div>')
    clean=[]
    for m in current_standings:
        try:
            rawx=x_values.get(m); rawy=y_values.get(m)
            if rawx is None or rawy is None: continue
            x=float(rawx); y=float(rawy)
        except (TypeError, ValueError):
            continue
        if math.isfinite(x) and math.isfinite(y): clean.append((m,x,y))
    if len(clean)<2:
        return (f'<div class="card analytics-chart-card matrix-card" data-matrix-group="{escape_html(group)}">'
                f'<h2>{escape_html(title)}</h2><div class="notice">Not enough comparable teams yet.</div></div>')
    xs=[r[1] for r in clean]; ys=[r[2] for r in clean]
    med_x=statistics.median(xs); med_y=statistics.median(ys)
    minx,maxx=min(xs),max(xs); miny,maxy=min(ys),max(ys)
    dx=max(maxx-minx, 1.0 if maxx==minx else 0.01)
    dy=max(maxy-miny, 1.0 if maxy==miny else 0.01)
    xmin,xmax=minx-0.10*dx,maxx+0.10*dx
    ymin,ymax=miny-0.13*dy,maxy+0.13*dy
    W,H,PL,PR,PT,PB=760,370,65,22,28,59
    pw,ph=W-PL-PR,H-PT-PB
    def mapx(v):
        z=(v-xmin)/(xmax-xmin)
        return PL+pw*(1-z if reverse_x else z)
    def mapy(v):
        z=(v-ymin)/(ymax-ymin)
        return PT+ph*(z if reverse_y else 1-z)
    mx,my=mapx(med_x),mapy(med_y)
    grid='';ticks=''
    def fmt(v):
        return f'{v:.0f}' if abs(v)>=20 else f'{v:.1f}'
    for i in range(5):
        px=PL+pw*i/4; py=PT+ph*i/4
        valx=(xmax-(xmax-xmin)*i/4) if reverse_x else (xmin+(xmax-xmin)*i/4)
        valy=(ymin+(ymax-ymin)*i/4) if reverse_y else (ymax-(ymax-ymin)*i/4)
        grid += (f'<line class="matrix-gridline" x1="{px:.1f}" x2="{px:.1f}" y1="{PT}" y2="{PT+ph}"/>'
                 f'<line class="matrix-gridline" x1="{PL}" x2="{PL+pw}" y1="{py:.1f}" y2="{py:.1f}"/>')
        ticks += (f'<text class="matrix-tick" x="{px:.1f}" y="{H-36}" text-anchor="middle">{fmt(valx)}</text>'
                  f'<text class="matrix-tick" x="{PL-8}" y="{py+3:.1f}" text-anchor="end">{fmt(valy)}</text>')
    # Logical quadrants become visible names AND a compact legend. For very
    # narrow quadrants the legend keeps the descriptor accessible even when
    # there isn't enough room for readable text inside the plot.
    quadrants=quadrants or MATRIX_QUADRANT_LABELS.get(title)
    if quadrants is None:
        quadrants=(f'Lower {x_label}, higher {y_label}',
                   f'Higher {x_label} and {y_label}',
                   f'Lower {x_label} and {y_label}',
                   f'Higher {x_label}, lower {y_label}')
    assert len(quadrants)==4, (title, quadrants)
    qlabels=''; qlegend=''
    for low_x,high_y,label in [(True,True,quadrants[0]),(False,True,quadrants[1]),
                               (True,False,quadrants[2]),(False,False,quadrants[3])]:
        axis_left=(low_x != reverse_x)
        axis_top=(high_y != reverse_y)
        position=('left' if axis_left else 'right', 'top' if axis_top else 'bottom')
        arrows={('left','top'):'↖',('right','top'):'↗',
                ('left','bottom'):'↙',('right','bottom'):'↘'}
        arrow=arrows[position]
        x0,x1=(PL,mx) if axis_left else (mx,PL+pw)
        y0,y1=(PT,my) if axis_top else (my,PT+ph)
        explanation=(f'{x_label}: {"below" if low_x else "above"} league median; '
                     f'{y_label}: {"above" if high_y else "below"} league median.')
        qlegend += (f'<span class="matrix-quad-key" title="{escape_html(explanation)}">'
                    f'<b aria-hidden="true">{arrow}</b> {escape_html(label)}</span>')
        if x1-x0<115 or y1-y0<35: continue
        tx=(x0+x1)/2
        max_chars=max(13,int((x1-x0-16)/5.8))
        words=label.split()
        pieces=[]
        if len(label)>max_chars and len(words)>1:
            # Two balanced lines: avoid a long one-line label overflowing a
            # median boundary at narrower viewport dimensions.
            best=min(range(1,len(words)),
                     key=lambda i:abs(len(' '.join(words[:i]))-len(' '.join(words[i:]))))
            pieces=[' '.join(words[:best]),' '.join(words[best:])]
        else:
            pieces=[label]
        ty=y0+min(24,(y1-y0)*0.38)
        if len(pieces)>1 and y1-y0<49: continue
        if len(pieces)==1:
            text_lines=escape_html(label)
        else:
            text_lines=''.join(f'<tspan x="{tx:.1f}" dy="{0 if i==0 else 12}">{escape_html(piece)}</tspan>'
                               for i,piece in enumerate(pieces))
        qlabels += (f'<text class="matrix-quadrant-label" x="{tx:.1f}" y="{ty:.1f}" '
                    f'text-anchor="middle" aria-label="{escape_html(label)}">{text_lines}</text>')
    dots=''
    for m,x,y in clean:
        px,py=mapx(x),mapy(y)
        hover=escape_html(f'{m} | {x_label}: {x:.2f} | {y_label}: {y:.2f}')
        dots += (f'<g class="analytics-manager-mark matrix-manager-point" data-analytics-manager="{escape_html(m)}" '
                 f'tabindex="0" role="button" data-chart-detail="{hover}" aria-label="{hover}">'
                 f'<circle class="matrix-dot" cx="{px:.1f}" cy="{py:.1f}" r="7" fill="{manager_color(m)}" '
                 f'stroke="#0f172a" stroke-width="1.8"><title>{hover}</title></circle>'
                 f'<text class="matrix-dot-label" x="{px+10:.1f}" y="{py+4:.1f}">{escape_html(m[:22])}</text></g>')
    axes=(f'<text class="matrix-axis-label" x="{PL+pw/2:.1f}" y="{H-8}" text-anchor="middle">{escape_html(x_label)}</text>'
          f'<text class="matrix-axis-label" transform="translate(15 {PT+ph/2:.1f}) rotate(-90)" text-anchor="middle">{escape_html(y_label)}</text>')
    desc=(f'<p class="card-description">{escape_html(description)}</p>' if description else '')
    return (f'<div class="card analytics-chart-card matrix-card" data-matrix-group="{escape_html(group)}">'
            f'<div class="matrix-card-top"><div><span class="matrix-category">{escape_html(group)}</span><h2>{escape_html(title)}</h2></div>'
            f'<span class="matrix-visible-count">{len(clean)} / {len(clean)} teams</span></div>{desc}'
            f'<div class="matrix-plot-wrap"><svg class="matrix-svg" viewBox="0 0 {W} {H}" role="group" aria-label="{escape_html(title)}">'
            f'{grid}<line class="matrix-median" x1="{mx:.1f}" x2="{mx:.1f}" y1="{PT}" y2="{PT+ph}"/>'
            f'<line class="matrix-median" x1="{PL}" x2="{PL+pw}" y1="{my:.1f}" y2="{my:.1f}"/>'
            f'{qlabels}{ticks}{dots}{axes}</svg></div>'
            f'<div class="matrix-quadrant-key" aria-label="Quadrant descriptions">{qlegend}</div>'
            f'<div class="matrix-meta"><span>League medians: {escape_html(x_label)} {fmt(med_x)} · '
            f'{escape_html(y_label)} {fmt(med_y)}</span><span>Hover or focus a coloured dot</span></div>'
            '<div class="matrix-empty" hidden>Select a fantasy manager to show teams here.</div></div>')


def _analytics_observations():
    if not managers: return []
    observations=[]
    luckiest=max(managers,key=lambda m:luck_index.get(m,0)); unluckiest=min(managers,key=lambda m:luck_index.get(m,0))
    observations.append(("Luck watch", f"{luckiest} have the biggest positive luck swing at {luck_index.get(luckiest,0):+.1f} league points versus expected. {unluckiest} sit at {luck_index.get(unluckiest,0):+.1f}."))
    top_pf=max(managers,key=lambda m:points_for.get(m,0)); observations.append(("Underlying scoring", f"{top_pf} lead McDraft for points scored with {points_for.get(top_pf,0):.0f}, irrespective of what the head-to-head results did with them."))
    run_avgs={m:(statistics.mean([r['difficulty'] for r in _next_fixture_rows(m,5)]) if _next_fixture_rows(m,5) else 0) for m in managers}
    hard=max(run_avgs,key=run_avgs.get); easy=min(run_avgs,key=run_avgs.get)
    observations.append(("Fixture runway", f"{hard} have the hardest next-five run ({run_avgs[hard]:.2f}/5); {easy} have the kindest ({run_avgs[easy]:.2f}/5)."))
    bench_avg={m:(statistics.mean([v for _,v in bench_scores.get(m,[])]) if bench_scores.get(m) else 0) for m in managers}
    waste=max(bench_avg,key=bench_avg.get); observations.append(("Bench watch", f"{waste} are leaving the most points on the bench on average ({bench_avg[waste]:.1f} per captured GW)."))
    roi_map={r['manager']:r['net_roi'] for r in transfer_roi}
    if roi_map:
        best=max(roi_map,key=roi_map.get); worst=min(roi_map,key=roi_map.get)
        observations.append(("Market efficiency", f"{best} currently lead transfer ROI at {roi_map[best]:+.0f}; {worst} are at {roi_map[worst]:+.0f}."))
    conc={}
    for m,ids in _trade_rosters.items():
        counts=defaultdict(int)
        for pid in ids: counts[_player_current_metrics(pid)['team']]+=1
        conc[m]=max(counts.values()) if counts else 0
    concentrated=max(conc,key=conc.get)
    observations.append(("Squad construction", f"{concentrated} have the highest single-club concentration with {conc[concentrated]} players from one Premier League side. Diversification may be worth considering when values are otherwise similar."))
    busiest=max(manager_transaction_counts,key=manager_transaction_counts.get) if manager_transaction_counts else None
    if busiest:
        observations.append(("Market activity", f"{busiest} have made the most completed roster moves ({manager_transaction_counts[busiest]}), counting a waiver drop-and-pickup as one move and only incoming legs of negotiated trades."))
    return observations[:8]


# ============================================================
# SQUAD TIME MACHINE — HISTORIC FIFA-STYLE SQUAD RATINGS
# ============================================================
def _historic_pedigree_line_score(players, position, starters, gw, fallback=45):
    """Historic positional unit using the player rating recorded/estimated for that GW."""
    scores = []
    for player in players:
        if player.get('position') != position:
            continue
        try:
            pid = int(player.get('id'))
        except (TypeError, ValueError):
            continue
        snap = (_rating_archive.get(str(pid), {}) or {}).get(str(gw), {}) or {}
        rating = snap.get('rating')
        if rating is None:
            continue
        scores.append(float(rating))
    scores.sort(reverse=True)
    top = scores[:starters]
    first = (sum(top) + fallback * max(0, starters - len(top))) / float(starters)
    depth = statistics.mean(scores[starters:]) if len(scores) > starters else first
    return round(0.85 * first + 0.15 * depth, 1)


def _squad_time_machine_series():
    """Rebuild every manager's DEF/MID/ATT/OVR from their actual roster in each completed GW."""
    out = {m: [] for m in managers}
    for gw in sorted(set(int(g) for g in finished_gws)):
        snapshot = (history.get('gameweeks', {}).get(str(gw), {}) or {}).get('teams', {}) or {}
        for squad in snapshot.values():
            manager = squad.get('manager')
            if manager not in out:
                continue
            players = []
            for pick in (squad.get('starters', []) or []) + (squad.get('bench', []) or []):
                try:
                    pid = int(pick.get('element_id'))
                except (TypeError, ValueError):
                    continue
                position = pick.get('position') or positions_lookup.get(elements.get(pid, {}).get('element_type'), '')
                players.append({'id': pid, 'position': position})
            if not players:
                continue
            gk = _historic_pedigree_line_score(players, 'GKP', 1, gw)
            defenders = _historic_pedigree_line_score(players, 'DEF', 4, gw)
            mid = _historic_pedigree_line_score(players, 'MID', 4, gw)
            att = _historic_pedigree_line_score(players, 'FWD', 2, gw)
            defense = round(0.80 * defenders + 0.20 * gk, 1)
            ovr = round(0.34 * defense + 0.38 * mid + 0.28 * att, 1)
            out[manager].append({'gw': gw, 'ovr': ovr, 'def': defense, 'mid': mid, 'att': att})
    return out


def _squad_time_machine_line_svg(series, metric, title, description):
    rows = [(m, pts) for m, pts in series.items() if pts]
    if not rows:
        return f'<div class="card analytics-chart-card"><h2>{escape_html(title)}</h2><div class="notice">Not enough rating history yet.</div></div>'
    gws = sorted({int(p['gw']) for _, pts in rows for p in pts})
    if not gws:
        return ''
    W,H,PL,PR,PT,PB=920,360,50,22,24,48
    pw,ph=W-PL-PR,H-PT-PB
    min_gw,max_gw=min(gws),max(gws)
    vals=[float(p[metric]) for _,pts in rows for p in pts]
    lo=max(30, min(vals)-4); hi=min(100, max(vals)+4)
    if hi-lo < 20:
        mid=(hi+lo)/2; lo=max(30,mid-10); hi=min(100,mid+10)
    def x(g): return PL + (float(g)-min_gw)/max(1,max_gw-min_gw)*pw
    def y(v): return PT + (hi-float(v))/max(1e-9,hi-lo)*ph
    grid=''
    for i in range(5):
        v=lo+(hi-lo)*i/4
        yy=y(v)
        grid += f'<line class="matrix-grid" x1="{PL}" x2="{W-PR}" y1="{yy:.1f}" y2="{yy:.1f}"/><text class="matrix-tick" x="{PL-8}" y="{yy+4:.1f}" text-anchor="end">{v:.0f}</text>'
    for gw in gws:
        xx=x(gw)
        grid += f'<text class="matrix-tick" x="{xx:.1f}" y="{H-18}" text-anchor="middle">GW{gw}</text>'
    marks=''; legend=''
    for manager, pts in rows:
        clean=sorted(pts,key=lambda r:r['gw'])
        colour=manager_color(manager)
        path=' '.join(('M' if i==0 else 'L')+f'{x(p["gw"]):.1f},{y(p[metric]):.1f}' for i,p in enumerate(clean))
        marks += f'<g class="analytics-manager-mark time-machine-manager" data-analytics-manager="{escape_html(manager)}"><path d="{path}" fill="none" stroke="{colour}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>'
        for p in clean:
            tooltip=f'{manager} · GW{p["gw"]} · {metric.upper()} {p[metric]:.1f}'
            marks += (f'<circle cx="{x(p["gw"]):.1f}" cy="{y(p[metric]):.1f}" r="3.8" '
                      f'fill="{colour}" stroke="#0f172a" stroke-width="1.2"><title>{escape_html(tooltip)}</title></circle>'
                      f'<circle cx="{x(p["gw"]):.1f}" cy="{y(p[metric]):.1f}" r="13" fill="transparent" '
                      f'role="button" tabindex="0" data-chart-detail="{escape_html(tooltip)}"><title>{escape_html(tooltip)}</title></circle>')
        marks += '</g>'
        legend += f'<span class="time-machine-key analytics-manager-mark" data-analytics-manager="{escape_html(manager)}"><i style="background:{colour}"></i>{escape_html(manager)}</span>'
    return (f'<div class="card analytics-chart-card time-machine-card"><h2>{escape_html(title)}</h2>'
            f'<p class="card-description">{escape_html(description)}</p><div class="time-machine-svg-wrap"><svg class="time-machine-svg" viewBox="0 0 {W} {H}" role="img" aria-label="{escape_html(title)}">{grid}{marks}</svg></div>'
            f'<div class="time-machine-legend">{legend}</div></div>')


def squad_time_machine_html():
    series = _squad_time_machine_series()
    changes=[]
    for manager, pts in series.items():
        if len(pts) < 2:
            continue
        pts=sorted(pts,key=lambda r:r['gw'])
        changes.append((manager, round(pts[-1]['ovr']-pts[0]['ovr'],1)))
    changes.sort(key=lambda r:-r[1])
    change_chart = _category_bar_chart_html(
        'Squad rating change since first captured GW', changes,
        'Current historic squad OVR minus the first available OVR for that manager. Positive means the squad has improved on the dynamic rating model.',
        value_suffix=' pts', y_label='OVR change') if changes else ''
    cards = [
        _squad_time_machine_line_svg(series,'ovr','League Rating Race','Every manager’s FIFA-style squad OVR through completed gameweeks, using the players they actually owned and those players’ rating at that point in time.'),
        _squad_time_machine_line_svg(series,'def','Defence rating race','Historic DEF strength, including the goalkeeper contribution used by Squad Pedigree.'),
        _squad_time_machine_line_svg(series,'mid','Midfield rating race','Historic MID strength from the best starting midfield assets plus squad depth.'),
        _squad_time_machine_line_svg(series,'att','Attack rating race','Historic ATT strength from the forward unit and its depth.'),
        change_chart,
    ]
    return ('<div class="card time-machine-intro"><div><h2>Squad Time Machine</h2>'
            '<p class="card-description">Track how each McDraft squad has strengthened or weakened as transfers, waivers, player form, output and Premier League club form changed. Reconstructed early player ratings remain estimates; observed snapshots stay frozen once captured.</p></div></div>'
            '<div class="analytics-chart-grid time-machine-grid">'+''.join(c for c in cards if c)+'</div>')


# ============================================================
# RATING LAB — CURRENT PLAYER / SQUAD RATING ANALYTICS
# ============================================================
def rating_lab_html():
    rated = [p for p in player_search_data
             if p.get('player_rating') is not None
             and elements.get(int(p['id']), {}).get('draft_active', True)]
    useful = [p for p in rated if _rating_num(p.get('minutes')) >= 90
              or _rating_num(p.get('total_points')) > 0]
    top = sorted(rated, key=lambda p: (-p['player_rating'], p['name']))
    top_rows = [(p['name'], p['player_rating'], p['id']) for p in top]
    free = [p for p in top if p.get('fantasy_team') in ('Free Agent', 'Free agents', None, '')]
    movers = [p for p in rated if p.get('rating_gw_delta') is not None]
    risers = sorted((p for p in movers if p['rating_gw_delta'] > 0),
                    key=lambda p: (-p['rating_gw_delta'], -p['player_rating']))
    fallers = sorted((p for p in movers if p['rating_gw_delta'] < 0),
                     key=lambda p: (p['rating_gw_delta'], p['player_rating']))
    current_club_scores = [(p['id'], p['name'], p.get('club_form_score', 50), p['player_rating'])
                           for p in useful]
    squad_rows = []
    for manager in managers:
        roster = current_squad_strength.get(manager, {}).get('players', [])
        if not roster:
            continue
        gk, _ = _pedigree_line_score(roster, 'GKP', 1)
        d, _ = _pedigree_line_score(roster, 'DEF', 4)
        m, _ = _pedigree_line_score(roster, 'MID', 4)
        a, _ = _pedigree_line_score(roster, 'FWD', 2)
        defensive = round(.8 * d + .2 * gk, 1)
        overall = round(.34 * defensive + .38 * m + .28 * a, 1)
        squad_rows.append((manager, overall, defensive, m, a))
    squad_rows.sort(key=lambda t: -t[1])
    squad_cards = ''.join(
        f'<div class="rating-lab-team {_rating_tier(ovr)}" data-analytics-manager="{escape_html(name)}">'
        f'<div><strong>{escape_html(name)}</strong><span class="rating-tier-number {_rating_tier(ovr)}">OVR {ovr:.0f}</span></div>'
        f'<div class="rating-lab-team-units">'
        + ''.join(f'<div title="{pos}: {score:.1f} / 100"><small>{pos}</small>'
                  f'<i><em style="width:{score:.1f}%"></em></i><b>{score:.0f}</b></div>'
                  for pos, score in (('DEF', defense), ('MID', mid), ('ATT', att)))
        + '</div></div>'
        for name, ovr, defense, mid, att in squad_rows
    )
    intro = ('Ratings refresh when the dashboard rebuilds. Compare player ' 
             'rating trajectories, see which factors moved and spot rating ' 
             'gaps by position. Bronze is <70, Silver 70–79, Gold 80–89 and Platinum 90+. The shared manager chips also filter this lab.')
    _tier_distribution = {tier: sum(1 for p in rated if _rating_tier(p['player_rating']) == tier.lower())
                          for tier in ('Platinum', 'Gold', 'Silver', 'Bronze')}
    _position_distribution = {pos: sum(1 for p in rated if p.get('position') == pos)
                              for pos in ('GKP', 'DEF', 'MID', 'FWD')}
    _elite_owners = {'Currently owned': sum(1 for p in top[:40] if p.get('fantasy_team')
                       not in ('Free Agent', 'Free agents', None, '')),
                     'Free agents': sum(1 for p in top[:40] if p.get('fantasy_team')
                       in ('Free Agent', 'Free agents', None, ''))}
    charts = [
        _pie_chart_html('Player rating tiers', _tier_distribution,
            'Platinum 90+, Gold 80–89, Silver 70–79, Bronze below 70. All active Draft players.',
            category_colours={'Platinum':'#b2e1e9','Gold':'#e1b650','Silver':'#9aadb9','Bronze':'#bd7c4d'}),
        _pie_chart_html('Rated player pool by position', _position_distribution,
            'Share of the active rated player pool across the four fantasy positions.'),
        _pie_chart_html('Top 40 rated assets · ownership', _elite_owners,
            'How many of the 40 highest-rated active players are owned versus available?'),
        _category_bar_chart_html('Top-rated players /100', top_rows,
            'Current seven-factor rating (not the trade-value score). Filter by manager above.',
            y_label='Current rating /100', limit=20),
        _category_bar_chart_html('Highest-rated free agents',
            [(p['name'], p['player_rating'], p['id']) for p in free],
            'Unowned players: ratings are based on football output and availability, not ownership.',
            y_label='Rating /100', limit=15),
        _category_bar_chart_html('Biggest rating rises',
            [(p['name'], p['rating_gw_delta'], p['id']) for p in risers],
            'Change since the previous finished GW. Earlier unrecorded GWs are estimates.',
            value_suffix=' pts', y_label='Rating change', limit=15),
        _category_bar_chart_html('Biggest rating falls',
            [(p['name'], abs(p['rating_gw_delta']), p['id']) for p in fallers],
            'Absolute size of the rating decline since the previous finished GW.',
            value_suffix=' pts', y_label='Rating drop', limit=15),
        _player_scatter_chart_html('Rating vs season production',
            [(p['id'], p['name'], p.get('total_points', 0), p['player_rating']) for p in useful],
            'Who looks better or worse once form, draft pedigree, club quality and availability count?',
            x_label='FPL points this season', y_label='Dynamic rating /100'),
        _player_scatter_chart_html('PL club form vs player rating', current_club_scores,
            'Club form alone is only one input; this distinguishes individual stars from their clubs.',
            x_label='Club last-five form /100', y_label='Player rating /100',
            fixed_x_min=0, fixed_x_max=100),
        _player_scatter_chart_html('Draft pedigree vs current rating',
            [(p['id'], p['name'], p.get('blended_draft_rank', 151), p['player_rating']) for p in useful],
            'How much has on-pitch evidence changed each player’s preseason expectations?',
            x_label='Blended original draft rank', y_label='Player rating /100',
            reverse_x=True, fixed_x_min=1, fixed_x_max=151),
        _bar_chart_html('FIFA squad OVR /100', {n: ovr for n, ovr, *_ in squad_rows},
            'Exactly the same current-roster formula used in Squad Pedigree.',
            y_label='Squad OVR /100'),
    ]
    return f'''<div class="card rating-lab-intro"><div><h2>Player Rating Lab</h2>
        <p class="card-description">{escape_html(intro)}</p></div>
        <span class="rating-lab-stamp">Last updated {escape_html(format_london_timestamp(history.get('last_updated','')))}</span></div>
    {squad_time_machine_html()}
    <div class="card rating-lab-trend-card"><h2>Rating evolution · choose up to four players</h2>
        <p class="card-description">End-of-gameweek ratings are fixed when first observed. Earlier missing weeks are reconstructed from historical points, minutes and Premier League results and shown with dashed lines. Historic injuries, unavailable underlying statistics and some old club moves may not be fully recoverable.</p>
        <div class="rating-lab-searchbar"><label for="rating-lab-search">Find player</label>
          <input id="rating-lab-search" type="search" placeholder="Search the player pool…" oninput="ratingLabFind()" autocomplete="off" />
          <button type="button" onclick="ratingLabAutoSelect()">Current top four</button>
          <button type="button" onclick="ratingLabClear()">Clear</button></div>
        <div id="rating-lab-suggestions" class="rating-lab-suggestions" aria-live="polite"></div>
        <div id="rating-lab-chips" class="rating-lab-selected" aria-live="polite"></div>
        <div id="rating-lab-trend" class="rating-lab-trend" role="img" aria-label="Dynamic player rating chart"></div>
        <div class="rating-lab-legend"><span><i></i> Observed end-of-GW rating</span>
            <span><i class="estimated"></i> Retrospective estimate</span></div></div>
    <div class="analytics-chart-grid rating-lab-detailed">
      <div class="card rating-lab-driver-card"><h2>Why did the rating move?</h2>
        <div class="rating-lab-driver-controls"><label for="rating-lab-focus">Player</label>
        <select id="rating-lab-focus" onchange="ratingLabDrivers()"></select>
        <label for="rating-lab-week">Snapshot</label>
        <select id="rating-lab-week" onchange="ratingLabDrivers(true)"></select></div>
        <div id="rating-lab-drivers"></div></div>
      <div class="card rating-lab-hist-card"><h2>Where do the ratings sit?</h2>
        <p class="card-description">Live distribution of currently selected players, grouped by position. Use the manager filter above.</p>
        <div id="rating-lab-position-filter" class="rating-lab-position-chips"></div>
        <div id="rating-lab-histogram"></div></div>
    </div>
    <div class="card rating-lab-squad-card"><h2>Squad OVR · DEF / MID / ATT</h2>
        <p class="card-description">FIFA-style unit breakdown from the same individual player ratings shown above. Only managers selected in the shared filter remain visible.</p>
        <div class="rating-lab-team-grid">{squad_cards}</div></div>
    <div class="analytics-chart-grid rating-lab-main-charts">{''.join(charts)}</div>'''

def analytics_page_html():
    avg_score={m:_manager_season_avg(m) for m in managers}
    last3={m:_manager_last_n_avg(m,3) for m in managers}
    volatility={m:(statistics.pstdev([v for _,v in raw_score_by_gw.get(m,[])]) if len(raw_score_by_gw.get(m,[]))>1 else 0) for m in managers}
    bench_avg={m:(statistics.mean([v for _,v in bench_scores.get(m,[])]) if bench_scores.get(m) else 0) for m in managers}
    dream_avg={m:(statistics.mean([v for _,v in dreamteam_counts.get(m,[])]) if dreamteam_counts.get(m) else 0) for m in managers}
    win_pct={m:(matches_won.get(m,0)/matches_played.get(m,1)*100 if matches_played.get(m,0) else 0) for m in managers}
    selection={m:float(manager_selection.get(m,{}).get('efficiency',0) or 0) for m in managers}
    squad_strength={m:float(current_squad_strength.get(m,{}).get('managed_xi',0) or 0) for m in managers}
    optimal_strength={m:float(current_squad_strength.get(m,{}).get('optimal_xi',0) or 0) for m in managers}
    depth={m:float(current_squad_strength.get(m,{}).get('depth_bonus',0) or 0) for m in managers}
    draft_total={m:float(current_squad_strength.get(m,{}).get('squad_draft_rank_total',0) or 0) for m in managers}
    roi_map={r['manager']:float(r['net_roi']) for r in transfer_roi}
    moves={m:float(manager_transaction_counts.get(m,0)) for m in managers}
    opp={m:opponent_avg_score.get(m,0) for m in managers}
    exp_lp={m:expected_league_points.get(m,0) for m in managers}
    actual_lp={m:actual_finished_league_points.get(m,0) for m in managers}
    schedule={m:(statistics.mean([r['difficulty'] for r in _next_fixture_rows(m,5)]) if _next_fixture_rows(m,5) else 0) for m in managers}
    club_conc={}; club_div={}; retained={}
    for m,ids in _trade_rosters.items():
        cc=defaultdict(int); retained_count=0
        for pid in ids:
            cc[_player_current_metrics(pid)['team']]+=1
            draft=history.get('original_draft_rank',{}).get(str(pid),{})
            if draft.get('manager')==m: retained_count+=1
        club_conc[m]=max(cc.values()) if cc else 0
        club_div[m]=len(cc)
        retained[m]=retained_count

    # --------------------------------------------------------
    # POSITIONAL SQUAD ANALYTICS
    # --------------------------------------------------------
    # Two complementary views:
    # 1) depth = average current-squad output/form at each position;
    # 2) ceiling = the best player a manager owns at each position, ranked
    #    against every currently-owned player in McDraft at that position.
    _positions=('GKP','DEF','MID','FWD')
    positional_avg_points={pos:{} for pos in _positions}
    positional_avg_form5={pos:{} for pos in _positions}
    positional_best_percentile={pos:{} for pos in _positions}
    positional_best_rank={pos:{} for pos in _positions}
    positional_best_player={m:{} for m in managers}

    _owned_pos_pool={pos:[] for pos in _positions}
    for _manager,_ids in _trade_rosters.items():
        for _pid in _ids:
            _meta=elements.get(_pid,{})
            _pos=positions_lookup.get(_meta.get('element_type'),'')
            if _pos not in _owned_pos_pool:
                continue
            _pts=float(_meta.get('total_points',0) or 0)
            _name=_meta.get('web_name',f'Player {_pid}')
            _owned_pos_pool[_pos].append((_pid,_name,_pts,_manager))

    _owned_pos_rank={}
    for _pos,_rows in _owned_pos_pool.items():
        _rows=sorted(_rows,key=lambda x:(-x[2],x[1]))
        _n=len(_rows)
        for _rank,(_pid,_name,_pts,_owner) in enumerate(_rows,start=1):
            _pct=(100.0 if _n<=1 else 100.0*(_n-_rank)/(_n-1))
            _owned_pos_rank[(_pos,_pid)]={'rank':_rank,'percentile':_pct,'pool':_n}

    for _manager in managers:
        _ids=_trade_rosters.get(_manager,[])
        for _pos in _positions:
            _rows=[]
            for _pid in _ids:
                _meta=elements.get(_pid,{})
                if positions_lookup.get(_meta.get('element_type'),'') != _pos:
                    continue
                _points=float(_meta.get('total_points',0) or 0)
                _recent=[]
                for _gw in finished_gws[-5:]:
                    _recent.append(float((player_form.get(_pid,{}) or {}).get(_gw,0) or 0))
                _form5=statistics.mean(_recent) if _recent else (_points/max(len(finished_gws),1))
                _rows.append({'id':_pid,'name':_meta.get('web_name',f'Player {_pid}'),'points':_points,'form5':_form5})
            positional_avg_points[_pos][_manager]=(statistics.mean(r['points'] for r in _rows) if _rows else 0.0)
            positional_avg_form5[_pos][_manager]=(statistics.mean(r['form5'] for r in _rows) if _rows else 0.0)
            if _rows:
                _best=max(_rows,key=lambda r:(r['points'],r['form5'],r['name']))
                _rk=_owned_pos_rank.get((_pos,_best['id']),{'rank':0,'percentile':0.0,'pool':0})
                positional_best_player[_manager][_pos]={**_best,**_rk}
                positional_best_rank[_pos][_manager]=float(_rk['rank'])
                positional_best_percentile[_pos][_manager]=float(_rk['percentile'])
            else:
                positional_best_player[_manager][_pos]={'name':'—','points':0,'form5':0,'rank':0,'percentile':0,'pool':0}
                positional_best_rank[_pos][_manager]=0.0
                positional_best_percentile[_pos][_manager]=0.0

    positional_elite_score={
        m:statistics.mean([positional_best_percentile[p].get(m,0.0) for p in _positions])
        for m in managers
    }
    positional_depth_score={
        m:statistics.mean([positional_avg_points[p].get(m,0.0) for p in _positions])
        for m in managers
    }

    def _positional_table_html():
        labels={'GKP':'GK','DEF':'DEF','MID':'MID','FWD':'FWD'}
        rows=''
        for _m in current_standings:
            cells=''
            for _pos in _positions:
                _r=positional_best_player.get(_m,{}).get(_pos,{})
                _rank=int(_r.get('rank',0) or 0)
                _pool=int(_r.get('pool',0) or 0)
                _pct=float(_r.get('percentile',0) or 0)
                _rank_text=(f'{_ordinal_text(_rank)} / {_pool}' if _rank and _pool else '—')
                cells += f'''<td><strong>{escape_html(_r.get('name','—'))}</strong><br><span class="muted">{int(_r.get('points',0) or 0)} pts · {_rank_text}<br>{_pct:.0f}th percentile</span></td>'''
            rows += f'''<tr data-analytics-manager="{escape_html(_m)}"><td><strong>{escape_html(_m)}</strong></td>{cells}</tr>'''
        return f'''<div class="card analytics-chart-card positional-rank-table"><h2>Best player by position: rank & percentile</h2><p class="card-description">Each manager's highest-scoring current player at every position, ranked against all currently-owned McDraft players at that position.</p><div class="table-wrap"><table><thead><tr><th>Manager</th>{''.join(f'<th>{labels[p]}</th>' for p in _positions)}</tr></thead><tbody>{rows}</tbody></table></div></div>'''

    # Starting-XI concentration / reliance. For each finished GW, rank the XI by
    # effective fantasy points (including captain doubling) and measure how much
    # of the team's actual score came from its top 3 and top 6 contributors.
    top3_reliance_by_gw={m:[] for m in managers}
    top6_reliance_by_gw={m:[] for m in managers}
    top3_reliance_overall={m:0.0 for m in managers}
    top6_reliance_overall={m:0.0 for m in managers}
    _rel_totals={m:{'xi':0.0,'top3':0.0,'top6':0.0} for m in managers}
    for _gw in finished_gws:
        _teams=history.get('gameweeks',{}).get(str(_gw),{}).get('teams',{})
        for _td in _teams.values():
            _m=_td.get('manager')
            if _m not in _rel_totals:
                continue
            _effective=[]
            for _pl in (_td.get('starters',[]) or []):
                _pts=float(_pl.get('points',0) or 0) * (2.0 if _pl.get('is_captain') else 1.0)
                _effective.append(_pts)
            _effective.sort(reverse=True)
            _xi=sum(_effective)
            _t3=sum(_effective[:3])
            _t6=sum(_effective[:6])
            _r3=(100.0*_t3/_xi) if _xi>0 else 0.0
            _r6=(100.0*_t6/_xi) if _xi>0 else 0.0
            top3_reliance_by_gw[_m].append((_gw,_r3))
            top6_reliance_by_gw[_m].append((_gw,_r6))
            _rel_totals[_m]['xi'] += _xi
            _rel_totals[_m]['top3'] += _t3
            _rel_totals[_m]['top6'] += _t6
    for _m,_vals in _rel_totals.items():
        if _vals['xi']>0:
            top3_reliance_overall[_m]=100.0*_vals['top3']/_vals['xi']
            top6_reliance_overall[_m]=100.0*_vals['top6']/_vals['xi']


    # --------------------------------------------------------
    # DRAFT CAPITAL BY POSITION
    # --------------------------------------------------------
    _draft_positions_by_player={}
    _first_captured_gw=min([int(g) for g in history.get('gameweeks',{}).keys()] or [1])
    for _td in history.get('gameweeks',{}).get(str(_first_captured_gw),{}).get('teams',{}).values():
        for _pl in (_td.get('starters',[]) or []) + (_td.get('bench',[]) or []):
            _pid=_pl.get('element_id')
            if _pid is not None:
                _draft_positions_by_player[int(_pid)] = _pl.get('position') or positions_lookup.get(elements.get(int(_pid),{}).get('element_type'),'')
    draft_capital_position={pos:{m:0.0 for m in managers} for pos in _positions}
    draft_capital_position_share={pos:{m:0.0 for m in managers} for pos in _positions}
    draft_capital_total={m:0.0 for m in managers}
    for _pid_text,_info in (history.get('original_draft_rank',{}) or {}).items():
        try:
            _pid=int(_pid_text); _pick=int(_info.get('overall_pick',UNDRAFTED_PLAYER_RANK) or UNDRAFTED_PLAYER_RANK)
        except (TypeError,ValueError):
            continue
        if _pick>DRAFTED_PLAYER_COUNT: continue
        _manager=_info.get('manager')
        if _manager not in draft_capital_total: continue
        _pos=_draft_positions_by_player.get(_pid) or positions_lookup.get(elements.get(_pid,{}).get('element_type'),'')
        if _pos not in draft_capital_position: continue
        _capital=float(DRAFTED_PLAYER_COUNT+1-_pick)
        draft_capital_position[_pos][_manager]+=_capital
        draft_capital_total[_manager]+=_capital
    for _pos in _positions:
        for _manager in managers:
            _tot=draft_capital_total.get(_manager,0.0)
            draft_capital_position_share[_pos][_manager]=(100.0*draft_capital_position[_pos].get(_manager,0.0)/_tot) if _tot else 0.0

    # CURRENT SQUAD FRAGILITY
    # Model the loss after replacing unavailable stars with the best realistic
    # same-position free-agent cover. The previous implementation could return
    # no legal formation after removing several players from one position and
    # incorrectly translate that into a 100% loss of team strength.
    _frag_pos_values=defaultdict(list); _frag_all_values=[]
    for _pid,_meta in elements.items():
        _pos=positions_lookup.get(_meta.get('element_type'),'')
        _val=float(_meta.get('total_points',0) or 0)/max(len(finished_gws),1)
        if _pos: _frag_pos_values[_pos].append(_val)
        _frag_all_values.append(_val)
    _frag_league_mean=statistics.mean(_frag_all_values) if _frag_all_values else 2.5
    _frag_pos_baselines={p:(statistics.mean(v) if v else _frag_league_mean) for p,v in _frag_pos_values.items()}
    _league_owned_ids={int(pid) for pid,owner in current_owner_by_player.items() if owner not in (None,'',0,'0')}
    if not current_owner_by_player:
        for _ids in _trade_rosters.values():
            _league_owned_ids.update(int(pid) for pid in _ids)
    _replacement_pool=defaultdict(list)
    for _pid,_meta in elements.items():
        if int(_pid) in _league_owned_ids:
            continue
        if _meta.get('status') not in (None,'','a'):
            continue
        _pos=positions_lookup.get(_meta.get('element_type'),'')
        if _pos not in _positions:
            continue
        _projection=_player_weekly_projection(int(_pid),_frag_pos_baselines,_frag_league_mean)
        _replacement_pool[_pos].append({
            'id':f'fa-{_pid}', 'name':_meta.get('web_name',f'Player {_pid}'),
            'position':_pos, 'projection':_projection, 'replacement':True,
        })
    for _pos in _replacement_pool:
        _replacement_pool[_pos].sort(key=lambda r:float(r.get('projection',0) or 0),reverse=True)

    squad_fragility_1={}; squad_fragility_2={}; squad_fragility_3={}; squad_fragility_score={}
    for _manager in managers:
        _players=list(current_squad_strength.get(_manager,{}).get('players',[]) or [])
        _base=_best_projected_xi(_players); _base_total=float((_base or {}).get('total',0) or 0)
        _ordered=sorted(_players,key=lambda r:float(r.get('projection',0) or 0),reverse=True)
        _losses=[]
        for _n in (1,2,3):
            _removed=_ordered[:_n]
            _remove={p.get('id') for p in _removed}
            _scenario=[p for p in _players if p.get('id') not in _remove]
            _used_by_pos=defaultdict(int)
            for _p in _removed:
                _pos=_p.get('position')
                _idx=_used_by_pos[_pos]
                _used_by_pos[_pos]+=1
                _pool=_replacement_pool.get(_pos,[])
                if _idx < len(_pool):
                    _scenario.append(dict(_pool[_idx]))
                else:
                    _scenario.append({
                        'id':f'repl-{_pos}-{_idx}', 'name':'Replacement level',
                        'position':_pos, 'projection':float(_frag_pos_baselines.get(_pos,_frag_league_mean)),
                        'replacement':True,
                    })
            _after=_best_projected_xi(_scenario)
            _after_total=float((_after or {}).get('total',0) or 0)
            _losses.append((100.0*max(0.0,_base_total-_after_total)/_base_total) if _base_total else 0.0)
        squad_fragility_1[_manager],squad_fragility_2[_manager],squad_fragility_3[_manager]=_losses
        squad_fragility_score[_manager]=statistics.mean(_losses) if _losses else 0.0

    # --------------------------------------------------------
    # POSITIONAL SCARCITY
    # --------------------------------------------------------
    _slot_demand={'GKP':20,'DEF':50,'MID':50,'FWD':30}
    positional_scarcity={}
    positional_best_fa={}
    positional_elite_avg={}
    positional_cutoff={}
    _owned_ids={int(pid) for pid,owner in current_owner_by_player.items() if owner not in (None,'',0,'0')}
    if not _owned_ids:
        for _ids in _trade_rosters.values():
            _owned_ids.update(int(x) for x in _ids)
    _scarcity_rows=[]
    for _pos in _positions:
        _pool=[]; _fas=[]
        for _pid,_meta in elements.items():
            if positions_lookup.get(_meta.get('element_type'),'') != _pos: continue
            _score=float(_meta.get('total_points',0) or 0)/max(len(finished_gws),1)
            _pool.append((_score,_pid,_meta.get('web_name',f'Player {_pid}')))
            if int(_pid) not in _owned_ids and _meta.get('status') in (None,'','a'):
                _fas.append((_score,_pid,_meta.get('web_name',f'Player {_pid}')))
        _pool.sort(reverse=True); _fas.sort(reverse=True)
        _elite_vals=[x[0] for x in _pool[:5]]
        _elite=statistics.mean(_elite_vals) if _elite_vals else 0.0
        _fa=_fas[0][0] if _fas else 0.0; _fa_name=_fas[0][2] if _fas else 'None'
        _cut_rank=min(max(1,_slot_demand.get(_pos,20)),len(_pool)); _cut=_pool[_cut_rank-1][0] if _pool else 0.0
        _scarcity=max(0.0,min(100.0,100.0*max(0.0,_elite-_fa)/max(_elite,0.01)))
        positional_scarcity[_pos]=_scarcity; positional_best_fa[_pos]=_fa; positional_elite_avg[_pos]=_elite; positional_cutoff[_pos]=_cut
        _scarcity_rows.append((_pos,_elite,_fa,_cut,_scarcity,_fa_name))

    def _positional_scarcity_table_html():
        labels={'GKP':'GK','DEF':'DEF','MID':'MID','FWD':'FWD'}; rows=''
        for _pos,_elite,_fa,_cut,_scarcity,_fa_name in sorted(_scarcity_rows,key=lambda r:r[4],reverse=True):
            rows += f'<tr><td><strong>{labels.get(_pos,_pos)}</strong></td><td>{_scarcity:.0f}/100</td><td>{_elite:.2f}</td><td>{_cut:.2f}</td><td>{escape_html(_fa_name)} · {_fa:.2f}</td></tr>'
        return f'<div class="card analytics-chart-card"><h2>Positional scarcity dashboard</h2><p class="card-description">Higher scarcity means elite players sit much further above the best realistic free-agent replacement. Scores use points per completed GW so positions remain comparable.</p><div class="table-wrap"><table><thead><tr><th>Position</th><th>Scarcity</th><th>Top-5 avg</th><th>Roster cutoff</th><th>Best free agent</th></tr></thead><tbody>{rows}</tbody></table></div></div>'

    # --------------------------------------------------------
    # SQUAD ARCHETYPES
    # --------------------------------------------------------
    _avg_reliance=statistics.mean(top3_reliance_overall.values()) if top3_reliance_overall else 0
    _avg_frag=statistics.mean(squad_fragility_score.values()) if squad_fragility_score else 0
    _avg_depth=statistics.mean(positional_depth_score.values()) if positional_depth_score else 0
    _avg_moves=statistics.mean(moves.values()) if moves else 0
    _avg_retained=statistics.mean(retained.values()) if retained else 0
    squad_archetypes={}
    for _m in managers:
        if top3_reliance_overall.get(_m,0) >= _avg_reliance+4 and squad_fragility_score.get(_m,0) >= _avg_frag:
            _name='Star Heavy'; _desc='Big weekly output is concentrated in a small elite core; wonderful when healthy, twitchy when stars disappear.'
        elif positional_depth_score.get(_m,0) >= _avg_depth and top3_reliance_overall.get(_m,0) <= _avg_reliance-3:
            _name='Deep & Balanced'; _desc='Production is spread across the squad with fewer obvious single points of failure.'
        elif moves.get(_m,0) >= max(3,_avg_moves*1.35) and retained.get(_m,0) <= _avg_retained:
            _name='Waiver Built'; _desc='The current squad owes plenty to in-season reconstruction rather than stubborn loyalty to draft night.'
        elif retained.get(_m,0) >= _avg_retained+2:
            _name='Draft Loyalist'; _desc='Still heavily powered by the original draft; continuity is doing the heavy lifting.'
        elif club_conc.get(_m,0) >= 4:
            _name='Club Stacker'; _desc='Leans heavily into a small number of Premier League clubs, creating correlated upside and risk.'
        elif positional_elite_score.get(_m,0) >= 70 and squad_fragility_score.get(_m,0) <= _avg_frag:
            _name='Complete Package'; _desc='High-end talent without extreme fragility: annoyingly sensible squad construction.'
        else:
            _name='Balanced Core'; _desc='No single construction trait dominates; the squad sits between stars, depth and churn.'
        squad_archetypes[_m]={'name':_name,'description':_desc}

    def _squad_archetypes_html():
        rows=''
        for _m in current_standings:
            _a=squad_archetypes.get(_m,{'name':'Balanced Core','description':''})
            rows += f'<div class="archetype-card" data-analytics-manager="{escape_html(_m)}"><span>{escape_html(_a["name"])}</span><strong>{escape_html(_m)}</strong><p>{escape_html(_a["description"])}</p></div>'
        return f'<div class="card analytics-chart-card"><h2>Squad archetypes</h2><p class="card-description">A descriptive squad-construction label derived from depth, reliance, fragility, draft retention, transfer activity and club concentration.</p><div class="archetype-grid">{rows}</div></div>'

    # NEMESIS / FAVOURITE OPPONENT
    nemesis_by_manager={}; favourite_by_manager={}
    for _manager in managers:
        _records=h2h_records.get(_manager,{}) or {}
        _valid=[(opp,rec) for opp,rec in _records.items() if (rec.get('wins',0)+rec.get('draws',0)+rec.get('losses',0))>0]
        def _ppg(item):
            _opp,_rec=item; _played=_rec.get('wins',0)+_rec.get('draws',0)+_rec.get('losses',0)
            return ((3*_rec.get('wins',0))+_rec.get('draws',0))/_played if _played else 0.0
        if _valid:
            _fav=max(_valid,key=lambda item:(_ppg(item),item[1].get('wins',0),-item[1].get('losses',0)))
            _nem=min(_valid,key=lambda item:(_ppg(item),-item[1].get('losses',0),item[1].get('wins',0)))
            favourite_by_manager[_manager]=(_fav[0],_ppg(_fav)); nemesis_by_manager[_manager]=(_nem[0],_ppg(_nem))
        else:
            favourite_by_manager[_manager]=('—',0.0); nemesis_by_manager[_manager]=('—',0.0)

    def _nemesis_favourite_table_html():
        _rows=''
        for _manager in current_standings:
            _fav,_fav_ppg=favourite_by_manager.get(_manager,('—',0.0)); _nem,_nem_ppg=nemesis_by_manager.get(_manager,('—',0.0))
            _rows += f'<tr><td><strong>{escape_html(_manager)}</strong></td><td>{escape_html(_fav)}<br><span class="muted">{_fav_ppg:.2f} pts/game</span></td><td>{escape_html(_nem)}<br><span class="muted">{_nem_ppg:.2f} pts/game</span></td></tr>'
        return f'<div class="card analytics-chart-card"><h2>Favourite opponent & nemesis</h2><p class="card-description">Best and worst head-to-head opponent by league points per meeting.</p><div class="table-wrap"><table><thead><tr><th>Manager</th><th>Favourite opponent</th><th>Nemesis</th></tr></thead><tbody>{_rows}</tbody></table></div></div>'

    # HISTORIC FIXTURE DIFFICULTY + FIXTURE SWING
    _scores_by_manager_gw={m:{int(g):float(v or 0) for g,v in raw_score_by_gw.get(m,[])} for m in managers}
    def _pre_gw_strength(_manager,_gw):
        _prior=sorted((g,v) for g,v in _scores_by_manager_gw.get(_manager,{}).items() if g<_gw)
        if not _prior:
            return 0.0
        return (0.60*statistics.mean(v for _,v in _prior[-3:]))+(0.40*statistics.mean(v for _,v in _prior))

    historic_fixture_difficulty={m:[] for m in managers}
    fixture_swing_rows=[]
    historic_prediction_rows=[]
    for _match in enriched_matches:
        _gw=int(_match.get('event',0) or 0)
        _m1=_match.get('entry_1_name'); _m2=_match.get('entry_2_name')
        if _m1 not in managers or _m2 not in managers:
            continue
        _s1=_pre_gw_strength(_m1,_gw); _s2=_pre_gw_strength(_m2,_gw)
        _vals=[_pre_gw_strength(m,_gw) for m in managers]
        def _difficulty(_strength):
            if not _vals or max(_vals)==min(_vals):
                return 3.0
            return 1.0+4.0*((_strength-min(_vals))/(max(_vals)-min(_vals)))
        historic_fixture_difficulty[_m1].append((_gw,_difficulty(_s2)))
        historic_fixture_difficulty[_m2].append((_gw,_difficulty(_s1)))

        _p1=float(_match.get('entry_1_points',0) or 0); _p2=float(_match.get('entry_2_points',0) or 0)
        _actual=_p1-_p2; _expected=_s1-_s2
        _has_prior=(any(g<_gw for g in _scores_by_manager_gw.get(_m1,{})) and any(g<_gw for g in _scores_by_manager_gw.get(_m2,{})))
        if not _has_prior:
            continue
        _predicted=(_m1 if _expected>0.25 else (_m2 if _expected<-0.25 else 'Too close to call'))
        _actual_winner=(_m1 if _actual>0 else (_m2 if _actual<0 else 'Draw'))
        _correct=(_predicted==_actual_winner) if _predicted!='Too close to call' else None
        _swing=abs(_actual-_expected)
        fixture_swing_rows.append((f'GW{_gw}: {_m1} v {_m2}',_swing))
        historic_prediction_rows.append({
            'gw':_gw,'m1':_m1,'m2':_m2,'expected':_expected,
            'p1':_p1,'p2':_p2,'actual':_actual,'predicted':_predicted,
            'winner':_actual_winner,'correct':_correct,'swing':_swing,
        })
    historic_difficulty_avg={m:(statistics.mean(v for _,v in rows) if rows else 0.0) for m,rows in historic_fixture_difficulty.items()}

    def _historic_prediction_table_html():
        if not historic_prediction_rows:
            return '<div class="card analytics-chart-card"><h2>Historic predictions vs outcomes</h2><div class="notice">Not enough pre-gameweek history yet.</div></div>'
        _rows=''
        for _r in sorted(historic_prediction_rows,key=lambda r:(-r['gw'],-r['swing'])):
            if _r['expected']>0.25:
                _exp=f"{escape_html(_r['m1'])} by {_r['expected']:.1f}"
            elif _r['expected']<-0.25:
                _exp=f"{escape_html(_r['m2'])} by {abs(_r['expected']):.1f}"
            else:
                _exp='Too close to call'
            _actual_text=f"{escape_html(_r['m1'])} {_r['p1']:.0f}–{_r['p2']:.0f} {escape_html(_r['m2'])}"
            _badge=('✓' if _r['correct'] is True else ('✕' if _r['correct'] is False else '—'))
            _rows += (
                f"<tr><td>GW{_r['gw']}</td><td><strong>{escape_html(_r['m1'])}</strong> v <strong>{escape_html(_r['m2'])}</strong></td>"
                f"<td>{_exp}</td><td>{_actual_text}</td><td>{_r['swing']:.1f}</td><td>{_badge}</td></tr>"
            )
        return (
            '<div class="card analytics-chart-card fixture-outcome-table"><h2>Historic predictions vs outcomes</h2>'
            '<p class="card-description">Pre-GW expectation uses only scoring information available before that gameweek. GW1 is excluded because there was no league history yet.</p>'
            '<div class="table-wrap"><table><thead><tr><th>GW</th><th>Fixture</th><th>Pre-GW expectation</th><th>Actual result</th><th>Swing</th><th>Call</th></tr></thead>'
            f'<tbody>{_rows}</tbody></table></div></div>'
        )

    player_rows=[]
    original_rank_map = history.get('original_draft_rank', {})
    for p in player_form_stats:
        pid=p.get('id'); meta=elements.get(pid,{})
        draft_info = original_rank_map.get(str(pid), {})
        draft_rank = int(draft_info.get('overall_pick', UNDRAFTED_PLAYER_RANK) or UNDRAFTED_PLAYER_RANK)
        official_draft_rank = _official_draft_rank(pid)
        blended_draft_rank = float(_blended_draft_rank(pid))
        minutes = int(meta.get('minutes', 0) or 0)
        goals = int(meta.get('goals_scored', 0) or 0)
        assists = int(meta.get('assists', 0) or 0)
        clean_sheets = int(meta.get('clean_sheets', 0) or 0)
        bonus = int(meta.get('bonus', 0) or 0)
        saves = int(meta.get('saves', 0) or 0)
        defensive_contributions = int(meta.get('defensive_contribution', 0) or 0)
        expected_goals = float(meta.get('expected_goals', 0) or 0)
        expected_assists = float(meta.get('expected_assists', 0) or 0)
        expected_goal_involvements = float(meta.get('expected_goal_involvements', 0) or 0)
        season_points = float(p.get('season_points', 0) or 0)
        player_rows.append({
            **p,
            'club':teams_lookup.get(meta.get('team'),'—'),
            'position':positions_lookup.get(meta.get('element_type'),'—'),
            'projection':_trade_player_projection(pid),
            'draft_rank': draft_rank,
            'official_draft_rank': official_draft_rank,
            'blended_draft_rank': blended_draft_rank,
            'drafted': draft_rank <= DRAFTED_PLAYER_COUNT,
            'minutes': minutes,
            'goals': goals,
            'assists': assists,
            'goal_involvements': goals + assists,
            'clean_sheets': clean_sheets,
            'bonus': bonus,
            'saves': saves,
            'defensive_contributions': defensive_contributions,
            'expected_goals': expected_goals,
            'expected_assists': expected_assists,
            'expected_goal_involvements': expected_goal_involvements,
            'points_per_90': (season_points * 90.0 / minutes) if minutes > 0 else 0,
            'goals_per_90': (goals * 90.0 / minutes) if minutes > 0 else 0,
            'assists_per_90': (assists * 90.0 / minutes) if minutes > 0 else 0,
        })

    # Performance rank is based on actual fantasy output to date. Ties are
    # resolved deterministically by name so the draft-value charts remain stable.
    ranked_by_points = sorted(player_rows, key=lambda row: (-float(row.get('season_points', 0) or 0), row.get('name','')))
    for perf_rank, row in enumerate(ranked_by_points, start=1):
        row['performance_rank'] = perf_rank
        # Main draft-value metric uses the blended pedigree rank. Keep the raw
        # McDraft and official FPL deltas alongside it for diagnostics.
        row['draft_rank_delta'] = float(row.get('blended_draft_rank', UNDRAFTED_PLAYER_RANK)) - float(perf_rank)
        row['mcdraft_rank_delta'] = float(row.get('draft_rank', UNDRAFTED_PLAYER_RANK)) - float(perf_rank)
        _official = row.get('official_draft_rank')
        row['official_rank_delta'] = (float(_official) - float(perf_rank)) if _official is not None else None
        # Ratio is useful for spotting extreme late-round/undrafted breakouts.
        row['draft_value_ratio'] = float(row.get('blended_draft_rank', UNDRAFTED_PLAYER_RANK)) / max(float(perf_rank), 1.0)

    season_pts=[(p['name'],p.get('season_points',0),p['id']) for p in player_rows]
    form5=[(p['name'],p.get('avg_5') or 0,p['id']) for p in player_rows if p.get('avg_5') is not None]
    form10=[(p['name'],p.get('avg_10') or 0,p['id']) for p in player_rows if p.get('avg_10') is not None]
    trend=[(p['name'],p.get('trend') or 0,p['id']) for p in player_rows if p.get('trend') is not None]
    transfer_freq=[(p['name'],p.get('transfers',0),p['id']) for p in player_rows]
    owner_count=[(p['name'],p.get('owners',0),p['id']) for p in player_rows]
    appearances=[(p['name'],p.get('appearances',0),p['id']) for p in player_rows]
    projections=[(p['name'],p.get('projection',0),p['id']) for p in player_rows]
    _all_player_model_rows=[r for r in player_search_data if int(r.get('minutes',0) or 0)>0 or float(r.get('total_points',0) or 0)>0]
    hot_players=[(r.get('name','Unknown'),float(r.get('hot_cold_score',0) or 0),r['id']) for r in _all_player_model_rows]
    season_projection_players=[(r.get('name','Unknown'),float(r.get('projected_season_points',0) or 0),r['id']) for r in _all_player_model_rows]
    value_players=[(r.get('name','Unknown'),float(r.get('player_value',0) or 0),r['id']) for r in _all_player_model_rows]
    club_strength_x={r.get('name','Unknown'):float(r.get('club_strength',0) or 0) for r in _all_player_model_rows}
    season_projection_y={r.get('name','Unknown'):float(r.get('projected_season_points',0) or 0) for r in _all_player_model_rows}
    fixture_run_x={r.get('name','Unknown'):float(r.get('fixture_run_score',1) or 1) for r in _all_player_model_rows}
    value_y={r.get('name','Unknown'):float(r.get('player_value',0) or 0) for r in _all_player_model_rows}
    fa_points=[]
    for p in player_rows:
        if current_owner_by_player.get(int(p['id'])) in (None,"",0,"0"):
            fa_points.append((p['name'],p.get('season_points',0),p['id']))
    pos_points=defaultdict(float); club_points=defaultdict(float)
    club_drafted_points=defaultdict(float); club_undrafted_points=defaultdict(float)
    club_drafted_count=defaultdict(int); club_player_count=defaultdict(int)
    club_goals=defaultdict(int); club_assists=defaultdict(int); club_clean_sheets=defaultdict(int)
    club_bonus=defaultdict(int); club_minutes=defaultdict(int)
    for p in player_rows:
        pts=float(p.get('season_points',0) or 0)
        club=p['club']
        pos_points[p['position']] += pts
        club_points[club] += pts
        club_player_count[club] += 1
        club_goals[club] += int(p.get('goals',0) or 0)
        club_assists[club] += int(p.get('assists',0) or 0)
        club_clean_sheets[club] += int(p.get('clean_sheets',0) or 0)
        club_bonus[club] += int(p.get('bonus',0) or 0)
        club_minutes[club] += int(p.get('minutes',0) or 0)
        if p.get('drafted'):
            club_drafted_points[club] += pts
            club_drafted_count[club] += 1
        else:
            club_undrafted_points[club] += pts
    # Real-club totals use the complete current FPL player pool, not only players
    # who have appeared in McDraft ownership history. 'Banked' means points that
    # actually made a McDraft starting XI in a finished gameweek.
    club_all_fpl_points=defaultdict(float)
    for _pid, _meta in elements.items():
        _club=teams_lookup.get(_meta.get('team'),'—')
        club_all_fpl_points[_club] += float(_meta.get('total_points',0) or 0)

    club_bank_points=defaultdict(float)
    for _gw in finished_gws:
        _gw_data=history.get('gameweeks',{}).get(str(_gw),{})
        for _team_data in _gw_data.get('teams',{}).values():
            for _starter in _team_data.get('starters',[]) or []:
                _club=_starter.get('team') or '—'
                club_bank_points[_club] += float(_starter.get('points',0) or 0)

    club_all_names=sorted(set(club_all_fpl_points) | set(club_bank_points))
    club_bank_vs_all=[(club,club_bank_points.get(club,0),club_all_fpl_points.get(club,0)) for club in club_all_names]
    club_bank_share={club:(100.0*club_bank_points.get(club,0)/club_all_fpl_points.get(club,1) if club_all_fpl_points.get(club,0) else 0) for club in club_all_names}

    club_drafted_share={club:(100.0*club_drafted_points.get(club,0)/club_points.get(club,1) if club_points.get(club,0) else 0) for club in club_all_names}
    club_points_per_drafted={club:(club_drafted_points.get(club,0)/club_drafted_count.get(club,1) if club_drafted_count.get(club,0) else 0) for club in club_all_names}
    club_points_per_player={club:(club_points.get(club,0)/club_player_count.get(club,1) if club_player_count.get(club,0) else 0) for club in club_all_names}

    # Draft-value and real-football production datasets.
    draft_overperformers=[(p['name'],p['draft_rank_delta'],p['id']) for p in player_rows if p.get('drafted')]
    draft_underperformers=[(p['name'],p['draft_rank_delta'],p['id']) for p in player_rows if p.get('drafted')]
    undrafted_gems=[(p['name'],p.get('season_points',0),p['id']) for p in player_rows if not p.get('drafted')]
    goals=[(p['name'],p.get('goals',0),p['id']) for p in player_rows if p.get('goals',0)>0]
    assists_data=[(p['name'],p.get('assists',0),p['id']) for p in player_rows if p.get('assists',0)>0]
    goal_involvements=[(p['name'],p.get('goal_involvements',0),p['id']) for p in player_rows if p.get('goal_involvements',0)>0]
    clean_sheets=[(p['name'],p.get('clean_sheets',0),p['id']) for p in player_rows if p.get('clean_sheets',0)>0]
    bonus_points=[(p['name'],p.get('bonus',0),p['id']) for p in player_rows if p.get('bonus',0)>0]
    saves_data=[(p['name'],p.get('saves',0),p['id']) for p in player_rows if p.get('saves',0)>0]
    defensive_contrib=[(p['name'],p.get('defensive_contributions',0),p['id']) for p in player_rows if p.get('defensive_contributions',0)>0]
    points_per90=[(p['name'],p.get('points_per_90',0),p['id']) for p in player_rows if p.get('minutes',0)>=180]
    goals_per90=[(p['name'],p.get('goals_per_90',0),p['id']) for p in player_rows if p.get('minutes',0)>=180 and p.get('goals',0)>0]
    assists_per90=[(p['name'],p.get('assists_per_90',0),p['id']) for p in player_rows if p.get('minutes',0)>=180 and p.get('assists',0)>0]
    draft_x={p['name']:p['blended_draft_rank'] for p in player_rows if p.get('drafted')}
    mcdraft_x={p['name']:p['draft_rank'] for p in player_rows if p.get('drafted')}
    official_draft_x={p['name']:p['official_draft_rank'] for p in player_rows if p.get('official_draft_rank') is not None}
    perf_y={p['name']:p['performance_rank'] for p in player_rows if p.get('drafted')}
    perf_y_official={p['name']:p['performance_rank'] for p in player_rows if p.get('official_draft_rank') is not None}
    points_y={p['name']:float(p.get('season_points',0) or 0) for p in player_rows if p.get('drafted')}
    gi_y={p['name']:float(p.get('goal_involvements',0) or 0) for p in player_rows if p.get('drafted')}
    minutes_y={p['name']:float(p.get('minutes',0) or 0) for p in player_rows if p.get('drafted')}
    xgi_x={p['name']:float(p.get('expected_goal_involvements',0) or 0) for p in player_rows if p.get('minutes',0)>=180}
    actual_gi_y={p['name']:float(p.get('goal_involvements',0) or 0) for p in player_rows if p.get('minutes',0)>=180}

    extra_obs=[]
    if club_all_names:
        _best_capture=max(club_all_names,key=lambda c:club_bank_share.get(c,0))
        _most_banked=max(club_all_names,key=lambda c:club_bank_points.get(c,0))
        extra_obs.append(('Club capture', f"{_best_capture} have the highest McDraft capture rate: {club_bank_share.get(_best_capture,0):.1f}% of their available FPL points have actually been banked in starting XIs."))
        extra_obs.append(('Most banked club', f"Players from {_most_banked} have supplied the most points to McDraft starting XIs ({club_bank_points.get(_most_banked,0):.0f})."))
    drafted_rows=[p for p in player_rows if p.get('drafted')]
    if drafted_rows:
        steal=max(drafted_rows,key=lambda p:p.get('draft_rank_delta',-999))
        bust=min(drafted_rows,key=lambda p:p.get('draft_rank_delta',999))
        extra_obs.append(('Draft steal', f"{steal['name']} has a blended pedigree rank of #{steal['blended_draft_rank']:.0f} (McDraft #{int(steal['draft_rank'])}" + (f", FPL #{int(steal['official_draft_rank'])}" if steal.get('official_draft_rank') is not None else '') + f") but currently ranks #{int(steal['performance_rank'])} for fantasy output — {int(steal['draft_rank_delta'])} places above blended expectation."))
        extra_obs.append(('Draft underperformer', f"{bust['name']} has a blended pedigree rank of #{bust['blended_draft_rank']:.0f} (McDraft #{int(bust['draft_rank'])}" + (f", FPL #{int(bust['official_draft_rank'])}" if bust.get('official_draft_rank') is not None else '') + f") but currently ranks #{int(bust['performance_rank'])} — {abs(int(bust['draft_rank_delta']))} places below blended expectation."))
    undrafted_rows=[p for p in player_rows if not p.get('drafted')]
    if undrafted_rows:
        gem=max(undrafted_rows,key=lambda p:float(p.get('season_points',0) or 0))
        extra_obs.append(('Undrafted gem', f"{gem['name']} went undrafted and has already produced {int(gem.get('season_points',0) or 0)} fantasy points."))
    if player_rows:
        gi_leader=max(player_rows,key=lambda p:p.get('goal_involvements',0))
        bonus_leader=max(player_rows,key=lambda p:p.get('bonus',0))
        extra_obs.append(('Goal involvement leader', f"{gi_leader['name']} leads this player pool with {int(gi_leader.get('goal_involvements',0))} combined goals and assists."))
        extra_obs.append(('Bonus magnet', f"{bonus_leader['name']} has collected the most bonus points ({int(bonus_leader.get('bonus',0))})."))

    if club_all_names:
        club_total_leader=max(club_all_names,key=lambda c:club_points.get(c,0))
        club_undrafted_leader=max(club_all_names,key=lambda c:club_undrafted_points.get(c,0))
        club_drafted_share_leader=max(club_all_names,key=lambda c:club_drafted_share.get(c,0))
        extra_obs.append(('Club production', f"{club_total_leader} players have produced the most fantasy points overall ({int(club_points.get(club_total_leader,0))})."))
        extra_obs.append(('Ignored club value', f"{club_undrafted_leader} have supplied the most points from players who went undrafted ({int(club_undrafted_points.get(club_undrafted_leader,0))})."))
        extra_obs.append(('Draft dependence', f"{club_drafted_share_leader} have the highest share of club fantasy output coming from originally drafted players ({club_drafted_share.get(club_drafted_share_leader,0):.0f}%)."))
    if top3_reliance_overall:
        _most_top3=max(top3_reliance_overall,key=top3_reliance_overall.get)
        _least_top3=min(top3_reliance_overall,key=top3_reliance_overall.get)
        extra_obs.append(('Star dependence', f"{_most_top3} are the most reliant on their weekly top three starters: {top3_reliance_overall[_most_top3]:.1f}% of starting-XI points come from the top trio."))
        extra_obs.append(('Scoring spread', f"{_least_top3} have the most distributed scoring: only {top3_reliance_overall[_least_top3]:.1f}% of XI output comes from their weekly top three."))
    if positional_elite_score:
        _elite=max(positional_elite_score,key=positional_elite_score.get)
        _depth=max(positional_depth_score,key=positional_depth_score.get)
        _weak=min(positional_elite_score,key=positional_elite_score.get)
        extra_obs.append(('Positional elite', f"{_elite} have the strongest top-end positional profile: their best player at GK, DEF, MID and FWD averages the {positional_elite_score[_elite]:.0f}th percentile across McDraft."))
        extra_obs.append(('Positional depth', f"{_depth} lead the league for average current-squad production across the four positions ({positional_depth_score[_depth]:.1f} points per player on the positional-average measure)."))
        extra_obs.append(('Positional weak spot', f"{_weak} currently have the lowest average best-player positional percentile ({positional_elite_score[_weak]:.0f}th), suggesting fewer elite anchors across the four positions."))
    # Matrix Lab shares *all* manager metrics with existing Analytics, and uses
    # the same manager chips rather than inventing a separate filter.
    matrix_recent5={m:_manager_last_n_avg(m,5) for m in managers}
    matrix_momentum={m:last3.get(m,0)-avg_score.get(m,0) for m in managers}
    matrix_ppg={m:(float(league_points.get(m,0) or 0)/max(1,int(matches_played.get(m,0) or 0)))
                for m in managers}
    matrix_conceded={m:(float(points_against.get(m,0) or 0)/max(1,int(matches_played.get(m,0) or 0)))
                     for m in managers}
    matrix_injury_risk={m:0.0 for m in managers}
    matrix_injuries={m:0 for m in managers}
    matrix_absent={m:0 for m in managers}
    for _row in injury_list_rows:
        try: _pid=int(_row.get('id'))
        except (TypeError, ValueError): continue
        _owner=_analytics_owner_by_id.get(_pid)
        if _owner not in matrix_injury_risk: continue
        _status=str(_row.get('status') or 'a')
        matrix_injury_risk[_owner] += max(0.0,float(_row.get('points_at_risk') or 0))
        matrix_injuries[_owner] += int(_status=='i')
        matrix_absent[_owner] += int(_status in ('i','s','u','n'))
    _risk_inverse={m:max(0.0,100.0-squad_fragility_score.get(m,0)) for m in managers}
    _ppg_note='League points per completed McDraft fixture, not total points (avoids games-played bias).'
    _matrix_cards=[]
    def matrix(group,title,x,y,xlab,ylab,description='',quadrants=None,**kwargs):
        # Every existing matrix has its own four descriptive quadrant names;
        # fail visibly if a new matrix is added without descriptors.
        labels=MATRIX_QUADRANT_LABELS[title]
        _matrix_cards.append(_matrix_chart_html(title,x,y,group=group,x_label=xlab,y_label=ylab,
                                                description=description,quadrants=labels,**kwargs))
    q=('Underpowered / firing','Strong and firing','Underpowered / struggling','Strong on paper / cold')
    matrix('Form & Quality','Form vs quality',squad_strength,last3,'Projected managed XI','Last 3 GW avg',
           'The headline matrix: current fixture-aware XI projection against recent completed-gameweek scoring. Medians use every manager.',q,require_gws=True)
    matrix('Form & Quality','Squad quality vs season output',squad_strength,avg_score,'Projected managed XI','Season points / GW',
           'Who has converted their current squad projection into fantasy points?',require_gws=True)
    matrix('Form & Quality','Recent form vs season pace',avg_score,last3,'Season points / GW','Last 3 GW avg',
           'Upper-left = recent improvement from a modest season baseline.',
           ('Recent surge','Sustained scorers','Cold season / still cold','High season pace / cooling'),require_gws=True)
    matrix('Form & Quality','5GW baseline vs 3GW form',matrix_recent5,last3,'Last 5 GW avg','Last 3 GW avg',
           'The two windows overlap. Use as a visual form comparison, not independent signals.',require_gws=True)
    matrix('Form & Quality','Quality vs momentum',squad_strength,matrix_momentum,'Projected managed XI','3GW minus season avg',
           'Positive Y means recent scoring is above the manager’s season average.',require_gws=True)
    matrix('Form & Quality','Consistency vs recent form',volatility,last3,'Scoring volatility','Last 3 GW avg',
           'Low X means lower gameweek-to-gameweek scoring variability.',require_gws=True)
    matrix('Form & Quality','Recent form vs win rate',last3,win_pct,'Last 3 GW avg','H2H win rate (%)',
           'Compares latest scoring form with cumulative head-to-head results.',require_gws=True)
    matrix('Form & Quality','Draft pedigree vs current quality',draft_total,squad_strength,'Current squad draft-rank total','Projected managed XI',
           'Lower draft-rank totals mean earlier combined McDraft/FPL picks; the X-axis runs from high rank to low rank.',
           reverse_x=True)
    matrix('Form & Quality','Draft pedigree vs recent form',draft_total,last3,'Current squad draft-rank total','Last 3 GW avg',
           'Original pick pedigree of the current squad versus recent form; high rank on the left, strong pedigree on the right.',
           reverse_x=True,require_gws=True)

    matrix('Squad Construction','Elite talent vs squad depth',positional_elite_score,positional_depth_score,
           'Best-player percentile (%)','Cross-position depth',
           'Top-end talent at each position versus how much the whole squad contributes.')
    matrix('Squad Construction','Depth vs projected XI',positional_depth_score,squad_strength,'Average positional points','Projected managed XI')
    matrix('Squad Construction','Depth vs star reliance',positional_depth_score,top3_reliance_overall,
           'Average positional points','Top-3 scoring share (%)',
           'Measures whether deep squads also depend heavily on weekly star performances.',require_gws=True)
    matrix('Squad Construction','Star reliance vs consistency',top3_reliance_overall,volatility,
           'Top-3 scoring share (%)','Score volatility',
           'Does relying on a handful of players correspond to more volatile weekly totals?',require_gws=True)
    matrix('Squad Construction','Club diversity vs fragility',club_div,squad_fragility_score,
           'Premier League clubs represented','Modelled XI fragility (%)',
           'Fragility is loss of projected XI output when one, two or three stars are replaced.')
    matrix('Squad Construction','Club concentration vs volatility',club_conc,volatility,
           'Largest same-club group','Score volatility',require_gws=True)
    matrix('Squad Construction','Original draft retention vs quality',retained,squad_strength,
           'Original picks still owned','Projected managed XI')
    matrix('Squad Construction','Defensive spine',positional_avg_points['GKP'],positional_avg_points['DEF'],
           'Average GK points','Average DEF points','Current roster, not just the players selected in recent XIs.')
    matrix('Squad Construction','Attacking balance',positional_avg_points['MID'],positional_avg_points['FWD'],
           'Average MID points','Average FWD points')
    matrix('Squad Construction','Elite percentile vs star reliance',positional_elite_score,top3_reliance_overall,
           'Best-player percentile (%)','Top-3 scoring share (%)',require_gws=True)

    matrix('Transfers & Decisions','Transfer activity vs ROI',moves,roi_map,'Completed roster moves','Net transfer ROI',
           'Net ROI uses the dashboard’s existing gained-minus-given-away metric, not a causal measure.')
    matrix('Transfers & Decisions','Market ROI vs recent momentum',roi_map,matrix_momentum,'Net transfer ROI','3GW minus season avg',
           'Whether strong past acquisitions coincide with recently improving team scores.',require_gws=True)
    matrix('Transfers & Decisions','Transfer activity vs scoring',moves,avg_score,'Completed roster moves','Season points / GW',require_gws=True)
    matrix('Transfers & Decisions','Draft loyalty vs trading',retained,moves,'Original picks still owned','Completed roster moves')
    matrix('Transfers & Decisions','Selection efficiency vs scoring',selection,avg_score,
           'Selection efficiency (%)','Season points / GW',require_gws=True)
    matrix('Transfers & Decisions','Bench wastage vs selection',bench_avg,selection,
           'Bench points / GW','Selection efficiency (%)',require_gws=True)
    matrix('Transfers & Decisions','Bench wastage vs win rate',bench_avg,win_pct,
           'Bench points / GW','H2H win rate (%)',require_gws=True)
    matrix('Transfers & Decisions','Dream-team picks vs win rate',dream_avg,win_pct,
           'Dream-team starters / GW','H2H win rate (%)',require_gws=True)
    matrix('Transfers & Decisions','Market ROI vs win rate',roi_map,win_pct,
           'Net transfer ROI','H2H win rate (%)',require_gws=True)

    matrix('Results & Luck','Squad quality vs H2H return',squad_strength,matrix_ppg,
           'Projected managed XI','League points / match',_ppg_note,require_gws=True)
    matrix('Results & Luck','Expected vs actual league points',exp_lp,actual_lp,
           'Expected league points','Actual league points',require_gws=True)
    matrix('Results & Luck','Season scoring vs league return',avg_score,matrix_ppg,
           'Season points / GW','League points / match',_ppg_note,require_gws=True)
    matrix('Results & Luck','Scoring vs fixture luck',points_for,luck_index,
           'Season fantasy points','League-point luck index',
           'The existing Luck Index is actual minus expected head-to-head league points.',require_gws=True)
    matrix('Results & Luck','Points conceded vs H2H return',matrix_conceded,matrix_ppg,
           'Opponent points / match','League points / match',_ppg_note,require_gws=True)
    matrix('Results & Luck','Volatility vs luck',volatility,luck_index,
           'Scoring volatility','League-point luck index',require_gws=True)
    matrix('Results & Luck','Opponent strength vs win rate',opp,win_pct,
           'Opponent avg fantasy score','H2H win rate (%)',require_gws=True)

    matrix('Availability & Fixtures','Current injury risk vs squad quality',matrix_injury_risk,squad_strength,
           'Next-GW projected points at risk','Projected managed XI',
           'Availability risk is modelled for next GW, not verified historical injury points.')
    matrix('Availability & Fixtures','Unavailable players vs projected loss',matrix_absent,matrix_injury_risk,
           'Unavailable owned players','Next-GW points at risk',
           'A status flag and a modelled risk are different measures; a bench player may add little points risk.')
    matrix('Availability & Fixtures','Injury count vs recent form',matrix_injuries,last3,
           'Currently injured players','Last 3 GW avg',
           'Current injuries need not have affected all three historical weeks.',require_gws=True)
    matrix('Availability & Fixtures','Squad fragility vs injury exposure',squad_fragility_score,matrix_injury_risk,
           'Modelled XI fragility (%)','Next-GW points at risk')
    matrix('Availability & Fixtures','Upcoming fixtures vs recent form',schedule,last3,
           'Next 5 GW difficulty /5','Last 3 GW avg',
           'Left means a kinder forthcoming run; high Y means better recent results.',require_gws=True)
    matrix('Availability & Fixtures','Upcoming fixtures vs win rate',schedule,win_pct,
           'Next 5 GW difficulty /5','H2H win rate (%)',require_gws=True)
    matrix('Availability & Fixtures','Quality vs resilience',squad_strength,_risk_inverse,
           'Projected managed XI','Modelled resilience /100',
           'Resilience = 100 minus the existing Squad Fragility Index; a scenario metric, not medical certainty.')
    matrix('Availability & Fixtures','Club concentration vs injuries',club_conc,matrix_injuries,
           'Largest same-club group','Currently injured players')
    matrix_groups=('Form & Quality','Squad Construction','Transfers & Decisions',
                   'Results & Luck','Availability & Fixtures')
    matrix_group_counts={g:sum(1 for c in _matrix_cards if f'data-matrix-group="{escape_html(g)}"' in c) for g in matrix_groups}
    matrix_controls=''.join(
        f'<button type="button" class="matrix-group-chip{" active" if i==0 else ""}" '
        f'data-matrix-group-button="{escape_html(group)}" onclick="setMatrixGroup({escape_html(json.dumps(group))})">'
        f'{escape_html(group)} <span>{matrix_group_counts[group]}</span></button>'
        for i,group in enumerate(matrix_groups)
    )
    matrix_controls += (f'<button type="button" class="matrix-group-chip" data-matrix-group-button="All" '
                        f'onclick="setMatrixGroup(\'All\')">All <span>{len(_matrix_cards)}</span></button>')
    matrix_html=(f'<div class="card matrix-intro"><div><h2>Matrix Lab · {len(_matrix_cards)} comparisons</h2>'
                 '<p class="card-description">Every dot is a McDraft team and always keeps its team colour. '
                 'Dashed lines show whole-league medians. The named quadrants compare teams to those medians and remain fixed when you change the shared manager filter. '
                 'These are descriptive comparisons, not causal findings.</p></div>'
                 '<span id="matrix-manager-summary" class="muted" aria-live="polite"></span></div>'
                 f'<div class="matrix-group-controls" role="group" aria-label="Matrix categories">{matrix_controls}</div>'
                 f'<div class="analytics-chart-grid matrix-grid">{"".join(_matrix_cards)}</div>')


    insight_rows = _analytics_observations() + extra_obs
    insights=''.join(f'<div class="analytics-insight"><span>{escape_html(k)}</span><strong>{escape_html(v)}</strong></div>' for k,v in insight_rows[:13])
    _player_points_position_mix = {pos: sum(max(0.0, float(p.get('total_points',0) or 0))
                                    for p in player_search_data if p.get('position') == pos)
                                    for pos in ('GKP','DEF','MID','FWD')}
    player_charts=[
        _pie_chart_html('Season FPL points by position', _player_points_position_mix,
            'The share of all active player-pool season points generated by each position.'),
        _category_bar_chart_html('Dynamic player rating /100', [(p['name'], p['player_rating'], p['id']) for p in player_search_data if p.get('player_rating') is not None], 'Current seven-factor rating, refreshed on each dashboard build.', y_label='Rating /100', limit=20),
        _category_bar_chart_html('Largest player rating moves', [(p['name'], abs(p['rating_gw_delta']), p['id']) for p in player_search_data if p.get('rating_gw_delta') is not None], 'Absolute moves since the previous completed gameweek; see Rating Lab for the direction and reasons.', y_label='Rating change', limit=20),
        _positional_scarcity_table_html(),
        _category_bar_chart_html('Positional scarcity index',[( {'GKP':'GK','DEF':'DEF','MID':'MID','FWD':'FWD'}.get(p,p),v) for p,v in positional_scarcity.items()],'Higher means the elite tier sits further above the best available free-agent replacement.',x_label='Position',y_label='Scarcity index',limit=10),
        _category_bar_chart_html('Best free-agent production by position',[( {'GKP':'GK','DEF':'DEF','MID':'MID','FWD':'FWD'}.get(p,p),v) for p,v in positional_best_fa.items()],'Best unowned player at each position, measured in points per completed GW.',x_label='Position',y_label='Points per GW',limit=10),
        _category_bar_chart_html('Top-five production by position',[( {'GKP':'GK','DEF':'DEF','MID':'MID','FWD':'FWD'}.get(p,p),v) for p,v in positional_elite_avg.items()],'Average points per completed GW among the top five players at each position.',x_label='Position',y_label='Points per GW',limit=10),
        _category_bar_chart_html('Top season scorers',season_pts,x_label='Player',y_label='Fantasy points'),
        _category_bar_chart_html('Best 5GW form',form5,x_label='Player',y_label='Points per GW'),
        _category_bar_chart_html('Best 10GW form',form10,x_label='Player',y_label='Points per GW'),
        _category_bar_chart_html('Fastest-rising form',trend,x_label='Player',y_label='5GW minus 10GW form'),
        _category_bar_chart_html('Projected player strength',projections,x_label='Player',y_label='Projection'),
        _category_bar_chart_html('Fixture-adjusted hot players',hot_players,'Recent scoring after neutralising fixture difficulty. Positive = running above season baseline; negative = cold.',x_label='Player',y_label='Hot/cold index',limit=20),
        _category_bar_chart_html('Projected season points',season_projection_players,'Actual points plus fixture-aware projection for every remaining Premier League gameweek.',x_label='Player',y_label='Projected season points',limit=20),
        _category_bar_chart_html('Player value model',value_players,'Composite value blending season projection, next-three fixtures, blended draft pedigree and Premier League club strength.',x_label='Player',y_label='Value /100',limit=20),
        _player_scatter_chart_html('Premier League club strength vs projected season points',[(r['id'],r.get('name','Unknown'),r.get('club_strength',0),r.get('projected_season_points',0)) for r in _all_player_model_rows],x_label='Club strength /100',y_label='Projected season points'),
        _player_scatter_chart_html('Next-three fixture outlook vs player value',[(r['id'],r.get('name','Unknown'),r.get('fixture_run_score',1),r.get('player_value',0)) for r in _all_player_model_rows],x_label='Next-three fixture multiplier',y_label='Player value /100'),
        _category_bar_chart_html('Most transferred players',transfer_freq,x_label='Player',y_label='Ownership hand-offs'),
        _category_bar_chart_html('Most widely owned players',owner_count,x_label='Player',y_label='Different managers'),
        _category_bar_chart_html('Most appearances',appearances,x_label='Player',y_label='Captured GWs'),
        _category_bar_chart_html('Best available free agents',fa_points,'Unowned players ranked by season scoring.',x_label='Player',y_label='Fantasy points'),
        _player_position_totals_chart_html(player_rows),
        _category_bar_chart_html('Biggest draft steals',draft_overperformers,'Positive values mean the player is outperforming a 60% McDraft / 40% official FPL Draft pedigree rank.',x_label='Player',y_label='Places above blended rank',limit=20),
        _category_bar_chart_html('Biggest draft busts',draft_underperformers,'Most negative deltas against the blended McDraft + official FPL Draft pedigree rank.',reverse=True,x_label='Player',y_label='Blended rank delta',limit=20),
        _category_bar_chart_html('Undrafted gems',undrafted_gems,'Players outside the original 150-player draft ranked by fantasy points.',x_label='Player',y_label='Fantasy points',limit=20),
        _player_scatter_chart_html('Blended draft pedigree vs current performance rank',[(p['id'],p['name'],p['blended_draft_rank'],p['performance_rank']) for p in player_rows if p.get('drafted')],x_label='60% McDraft + 40% FPL Draft rank',y_label='Current points rank',reverse_x=True,fixed_x_max=151,fixed_x_min=1),
        _player_scatter_chart_html('McDraft pick vs current performance rank',[(p['id'],p['name'],p['draft_rank'],p['performance_rank']) for p in player_rows if p.get('drafted')],x_label='Actual McDraft pick',y_label='Current points rank',reverse_x=True,fixed_x_max=DRAFTED_PLAYER_COUNT,fixed_x_min=1),
        _player_scatter_chart_html('Official FPL Draft rank vs current performance rank',[(p['id'],p['name'],p['official_draft_rank'],p['performance_rank']) for p in player_rows if p.get('official_draft_rank') is not None and 1 <= p['official_draft_rank'] < UNDRAFTED_PLAYER_RANK],x_label='Official FPL Draft rank',y_label='Current points rank',reverse_x=True,fixed_x_max=DRAFTED_PLAYER_COUNT,fixed_x_min=1),
        _player_scatter_chart_html('Blended draft pedigree vs fantasy points',[(p['id'],p['name'],p['blended_draft_rank'],p.get('season_points',0)) for p in player_rows if p.get('drafted')],x_label='Blended draft rank',y_label='Fantasy points',reverse_x=True,fixed_x_max=151,fixed_x_min=1),
        _player_scatter_chart_html('Draft pick vs goal involvements',[(p['id'],p['name'],p['blended_draft_rank'],p.get('goal_involvements',0)) for p in player_rows if p.get('drafted')],x_label='Blended draft rank',y_label='Goals + assists',reverse_x=True,fixed_x_max=151,fixed_x_min=1),
        _player_scatter_chart_html('Draft pick vs minutes played',[(p['id'],p['name'],p['blended_draft_rank'],p.get('minutes',0)) for p in player_rows if p.get('drafted')],x_label='Blended draft rank',y_label='Minutes',reverse_x=True,fixed_x_max=151,fixed_x_min=1),
        _category_bar_chart_html('Goals',goals,x_label='Player',y_label='Goals',limit=20),
        _category_bar_chart_html('Assists',assists_data,x_label='Player',y_label='Assists',limit=20),
        _category_bar_chart_html('Goal involvements',goal_involvements,x_label='Player',y_label='Goals + assists',limit=20),
        _category_bar_chart_html('Clean sheets',clean_sheets,'Most relevant to goalkeepers and defenders, but shown directly from FPL player statistics.',x_label='Player',y_label='Clean sheets',limit=20),
        _category_bar_chart_html('Bonus points',bonus_points,x_label='Player',y_label='Bonus points',limit=20),
        _category_bar_chart_html('Goalkeeper saves',saves_data,x_label='Player',y_label='Saves',limit=20),
        _category_bar_chart_html('Defensive contributions',defensive_contrib,x_label='Player',y_label='Defensive contributions',limit=20),
        _category_bar_chart_html('Fantasy points per 90',points_per90,'Minimum 180 minutes to suppress tiny-sample nonsense.',x_label='Player',y_label='Points per 90',limit=20),
        _category_bar_chart_html('Goals per 90',goals_per90,'Minimum 180 minutes.',x_label='Player',y_label='Goals per 90',limit=20),
        _category_bar_chart_html('Assists per 90',assists_per90,'Minimum 180 minutes.',x_label='Player',y_label='Assists per 90',limit=20),
        _player_scatter_chart_html('Expected vs actual goal involvements',[(p['id'],p['name'],p.get('expected_goal_involvements',0),p.get('goal_involvements',0)) for p in player_rows if p.get('minutes',0)>=180],x_label='Expected goal involvements',y_label='Actual goals + assists'),
    ]
    club_charts=[
        _dual_category_bar_chart_html('Premier League club points: McDraft banked vs total FPL output',club_bank_vs_all,'McDraft banked points','Total FPL points','Compares points actually banked in McDraft starting XIs with the total FPL points produced by every player at that Premier League club.',x_label='Premier League club',y_label='Fantasy points',limit=20),
        _category_bar_chart_html('Total FPL points by Premier League club',list(club_all_fpl_points.items()),'Every player at the club, whether drafted in McDraft or not.',x_label='Premier League club',y_label='Fantasy points',limit=20),
        _category_bar_chart_html('McDraft banked points by Premier League club',list(club_bank_points.items()),'Only points that actually appeared in a McDraft starting XI in completed gameweeks.',x_label='Premier League club',y_label='Banked fantasy points',limit=20),
        _category_bar_chart_html('McDraft capture rate by Premier League club',list(club_bank_share.items()),'Share of each real club’s available FPL output that was actually banked in McDraft starting XIs.',value_suffix='%',x_label='Premier League club',y_label='Banked share of total output',limit=20),
        _category_bar_chart_html('Points from originally drafted players',list(club_drafted_points.items()),x_label='Premier League club',y_label='Drafted-player points',limit=20),
        _category_bar_chart_html('Undrafted player points by club',list(club_undrafted_points.items()),'Where McDraft left value on the table on draft night.',x_label='Premier League club',y_label='Undrafted-player points',limit=20),
        _category_bar_chart_html('Drafted share of club output',list(club_drafted_share.items()),'Percentage of each club fantasy output supplied by originally drafted players.',value_suffix='%',x_label='Premier League club',y_label='Drafted share',limit=20),
        _category_bar_chart_html('Drafted players by Premier League club',list(club_drafted_count.items()),x_label='Premier League club',y_label='Players drafted',limit=20),
        _category_bar_chart_html('Average points per drafted player',list(club_points_per_drafted.items()),x_label='Premier League club',y_label='Points per drafted player',limit=20),
        _category_bar_chart_html('Average points per player',list(club_points_per_player.items()),x_label='Premier League club',y_label='Points per player',limit=20),
        _category_bar_chart_html('Goals by Premier League club',list(club_goals.items()),x_label='Premier League club',y_label='Goals',limit=20),
        _category_bar_chart_html('Assists by Premier League club',list(club_assists.items()),x_label='Premier League club',y_label='Assists',limit=20),
        _category_bar_chart_html('Clean sheets by Premier League club',list(club_clean_sheets.items()),x_label='Premier League club',y_label='Clean sheets',limit=20),
        _category_bar_chart_html('Bonus points by Premier League club',list(club_bonus.items()),x_label='Premier League club',y_label='Bonus points',limit=20),
        _category_bar_chart_html('Minutes played by Premier League club',list(club_minutes.items()),x_label='Premier League club',y_label='Minutes',limit=20),
        _scatter_chart_html('Club draft investment vs club output',club_drafted_count,club_points,x_label='Players drafted from club',y_label='Total fantasy points'),
        _scatter_chart_html('Drafted club output vs overall club output',club_drafted_points,club_points,x_label='Drafted-player points',y_label='All-player points'),
        _scatter_chart_html('Undrafted club output vs drafted club output',club_undrafted_points,club_drafted_points,x_label='Undrafted-player points',y_label='Drafted-player points'),
    ]
    squad_strength_charts=[
        _positional_table_html(),
        _bar_chart_html('Goalkeeper depth: average points',positional_avg_points['GKP'],'Average season FPL points of the goalkeepers currently owned by each manager.',x_label='Manager',y_label='Average GK points'),
        _bar_chart_html('Defensive depth: average points',positional_avg_points['DEF'],'Average season FPL points of current defenders.',x_label='Manager',y_label='Average DEF points'),
        _bar_chart_html('Midfield depth: average points',positional_avg_points['MID'],'Average season FPL points of current midfielders.',x_label='Manager',y_label='Average MID points'),
        _bar_chart_html('Forward depth: average points',positional_avg_points['FWD'],'Average season FPL points of current forwards.',x_label='Manager',y_label='Average FWD points'),
        _bar_chart_html('Goalkeeper form: squad average',positional_avg_form5['GKP'],'Average points per game across the last five completed GWs for currently-owned goalkeepers.',x_label='Manager',y_label='5GW points per game'),
        _bar_chart_html('Defensive form: squad average',positional_avg_form5['DEF'],'Average points per game across the last five completed GWs for currently-owned defenders.',x_label='Manager',y_label='5GW points per game'),
        _bar_chart_html('Midfield form: squad average',positional_avg_form5['MID'],'Average points per game across the last five completed GWs for currently-owned midfielders.',x_label='Manager',y_label='5GW points per game'),
        _bar_chart_html('Forward form: squad average',positional_avg_form5['FWD'],'Average points per game across the last five completed GWs for currently-owned forwards.',x_label='Manager',y_label='5GW points per game'),
        _bar_chart_html('Best goalkeeper percentile',positional_best_percentile['GKP'],'100 = owns the highest-scoring currently-owned goalkeeper in McDraft.',value_suffix='%',x_label='Manager',y_label='Positional percentile'),
        _bar_chart_html('Best defender percentile',positional_best_percentile['DEF'],'Percentile rank of each manager’s best current defender among all owned defenders.',value_suffix='%',x_label='Manager',y_label='Positional percentile'),
        _bar_chart_html('Best midfielder percentile',positional_best_percentile['MID'],'Percentile rank of each manager’s best current midfielder among all owned midfielders.',value_suffix='%',x_label='Manager',y_label='Positional percentile'),
        _bar_chart_html('Best forward percentile',positional_best_percentile['FWD'],'Percentile rank of each manager’s best current forward among all owned forwards.',value_suffix='%',x_label='Manager',y_label='Positional percentile'),
        _bar_chart_html('Positional elite score',positional_elite_score,'Average percentile of each manager’s best GK, DEF, MID and FWD.',value_suffix='%',x_label='Manager',y_label='Average best-player percentile'),
        _bar_chart_html('Cross-position depth score',positional_depth_score,'Mean of each manager’s average current-squad points at GK, DEF, MID and FWD.',x_label='Manager',y_label='Average positional points'),
        _bar_chart_html('Managed XI strength',squad_strength,x_label='Manager',y_label='Projected XI strength'),
        _bar_chart_html('Optimal XI strength',optimal_strength,x_label='Manager',y_label='Optimal projected XI'),
        _bar_chart_html('Bench depth contribution',depth,x_label='Manager',y_label='Depth bonus'),
    ]
    _current_roster_pos = {pos: sum(1 for ids in _trade_rosters.values() for pid in ids
                              if positions_lookup.get(elements.get(pid,{}).get('element_type'),'') == pos)
                           for pos in ('GKP','DEF','MID','FWD')}
    _club_roster_counts = defaultdict(int)
    for _ids in _trade_rosters.values():
        for _pid in _ids:
            _club_roster_counts[teams_lookup.get(elements.get(_pid,{}).get('team'),'Unknown')] += 1
    _top_clubs = sorted(_club_roster_counts.items(), key=lambda x:-x[1])[:5]
    _top_club_mix = dict(_top_clubs)
    _top_club_mix['Other clubs'] = sum(_club_roster_counts.values()) - sum(n for _,n in _top_clubs)
    squad_construction_charts=[
        _pie_chart_html('Current squad slots by position', _current_roster_pos,
            'All currently owned McDraft players, grouped by fantasy position.'),
        _pie_chart_html('Premier League club concentration', _top_club_mix,
            'Five most represented real PL clubs in all ten current squads, plus everyone else.'),
        _squad_archetypes_html(),
        _bar_chart_html('GK draft capital share',draft_capital_position_share['GKP'],'Share of original draft capital invested at goalkeeper. Earlier picks carry more capital.',value_suffix='%',x_label='Manager',y_label='Draft capital share'),
        _bar_chart_html('DEF draft capital share',draft_capital_position_share['DEF'],'Share of original draft capital invested in defenders.',value_suffix='%',x_label='Manager',y_label='Draft capital share'),
        _bar_chart_html('MID draft capital share',draft_capital_position_share['MID'],'Share of original draft capital invested in midfielders.',value_suffix='%',x_label='Manager',y_label='Draft capital share'),
        _bar_chart_html('FWD draft capital share',draft_capital_position_share['FWD'],'Share of original draft capital invested in forwards.',value_suffix='%',x_label='Manager',y_label='Draft capital share'),
        _bar_chart_html('Squad fragility: lose best player',squad_fragility_1,'Projected XI loss after replacing the unavailable star with realistic same-position free-agent cover.',value_suffix='%',x_label='Manager',y_label='XI strength lost'),
        _bar_chart_html('Squad fragility: lose top two',squad_fragility_2,'Projected XI loss after replacing the top two unavailable assets with same-position free-agent cover.',value_suffix='%',x_label='Manager',y_label='XI strength lost'),
        _bar_chart_html('Squad fragility: lose top three',squad_fragility_3,'Projected XI loss after replacing the top three unavailable assets with realistic same-position free-agent cover.',value_suffix='%',x_label='Manager',y_label='XI strength lost'),
        _bar_chart_html('Squad Fragility Index',squad_fragility_score,'Average projected damage across the one-, two- and three-star loss scenarios.',value_suffix='%',x_label='Manager',y_label='Fragility'),
        _bar_chart_html('Premier League clubs represented',club_div,x_label='Manager',y_label='Different clubs'),
        _bar_chart_html('Largest single-club concentration',club_conc,x_label='Manager',y_label='Players from same club'),
        _bar_chart_html('Top 3 starter reliance',top3_reliance_overall,'Share of finished-GW XI points supplied by each week’s top three scorers.',value_suffix='%',x_label='Manager',y_label='Share of XI points'),
        _bar_chart_html('Top 6 starter reliance',top6_reliance_overall,'Share of finished-GW XI points supplied by each week’s top six scorers.',value_suffix='%',x_label='Manager',y_label='Share of XI points'),
        _line_chart_html('Top 3 reliance by gameweek',top3_reliance_by_gw,'Weekly concentration in the three biggest contributors.',x_label='Gameweek',y_label='Top 3 share (%)'),
        _line_chart_html('Top 6 reliance by gameweek',top6_reliance_by_gw,'Weekly concentration in the six biggest contributors.',x_label='Gameweek',y_label='Top 6 share (%)'),
        _bar_chart_html('Original draft players retained',retained,x_label='Manager',y_label='Players retained'),
        _bar_chart_html('Current squad blended draft-rank total',draft_total,'Lower is stronger blended pre-season pedigree. 60% McDraft pick order + 40% official FPL Draft rank.',reverse=True,x_label='Manager',y_label='Draft rank total'),
        _scatter_chart_html('Star reliance vs scoring',top3_reliance_overall,points_for,x_label='Top 3 reliance (%)',y_label='Points scored'),
        _scatter_chart_html('Star reliance vs league position',top3_reliance_overall,{m:manager_current_rank.get(m,0) for m in managers},x_label='Top 3 reliance (%)',y_label='League position',invert_y=True),
        _scatter_chart_html('Club concentration vs scoring',club_conc,points_for,x_label='Largest same-club group',y_label='Points scored'),
        _scatter_chart_html('Squad strength vs league position',squad_strength,{m:manager_current_rank.get(m,0) for m in managers},x_label='Squad strength',y_label='League position',invert_y=True),
    ]
    decision_charts=[
        _pie_chart_html('Share of completed roster moves', moves,
            'Each manager’s share of all completed roster moves captured by the dashboard.', manager_colours=True),
        _bar_chart_html('Selection efficiency',selection,value_suffix='%',x_label='Manager',y_label='Efficiency'),
        _bar_chart_html('Bench points wasted per GW',bench_avg,x_label='Manager',y_label='Bench points'),
        _bar_chart_html('Dream-team starters per GW',dream_avg,x_label='Manager',y_label='Dream-team starters'),
        _bar_chart_html('Completed roster moves',moves,'Waiver drop+pickup = one move. Trade counts incoming players only.',x_label='Manager',y_label='Moves'),
        _bar_chart_html('Transfer ROI',roi_map,x_label='Manager',y_label='Net points'),
        _scatter_chart_html('Transfer activity vs scoring',moves,points_for,x_label='Completed roster moves',y_label='Points scored'),
        _scatter_chart_html('Transfer ROI vs league points',roi_map,league_points,x_label='Transfer ROI',y_label='League points'),
        _scatter_chart_html('Selection efficiency vs scoring',selection,points_for,x_label='Selection efficiency (%)',y_label='Points scored'),
    ]
    fixture_analytics_charts=[
        _historic_prediction_table_html(),
        _nemesis_favourite_table_html(),
        _category_bar_chart_html('Biggest fixture swings',fixture_swing_rows,'Largest absolute gap between the pre-GW expected scoring margin and the actual H2H margin.',x_label='Fixture',y_label='Margin swing',limit=25),
    ]
    season_charts=[
        _pie_chart_html('Share of total fantasy points', points_for,
            'Each manager’s share of all fantasy points scored in completed head-to-head fixtures.', manager_colours=True),
        _bar_chart_html('Points scored',points_for,x_label='Manager',y_label='Points'),
        _bar_chart_html('Points conceded',points_against,x_label='Manager',y_label='Points'),
        _bar_chart_html('Average weekly score',avg_score,x_label='Manager',y_label='Points per GW'),
        _bar_chart_html('Last 3 GW scoring',last3,x_label='Manager',y_label='Points per GW'),
        _bar_chart_html('League points',league_points,x_label='Manager',y_label='League points'),
        _bar_chart_html('Win rate',win_pct,value_suffix='%',x_label='Manager',y_label='Win rate'),
        _bar_chart_html('Scoring volatility',volatility,'Lower means more consistent.',x_label='Manager',y_label='Standard deviation'),
        _line_chart_html('Points per gameweek',raw_score_by_gw,x_label='Gameweek',y_label='Fantasy points'),
        _line_chart_html('League position over time',rank_history,x_label='Gameweek',y_label='League position',invert_y=True),
        _line_chart_html('Cumulative fantasy points',cumulative_score_history,x_label='Gameweek',y_label='Cumulative points'),
        _bar_chart_html('Luck Index',luck_index,'Actual H2H league points minus expected H2H return.',x_label='Manager',y_label='League-point difference'),
        _bar_chart_html('Expected league points',exp_lp,x_label='Manager',y_label='Expected league points'),
        _bar_chart_html('Actual finished league points',actual_lp,x_label='Manager',y_label='League points'),
        _scatter_chart_html('Scoring vs league points',points_for,league_points,x_label='Points scored',y_label='League points'),
        _scatter_chart_html('Scoring vs luck',points_for,luck_index,x_label='Points scored',y_label='Luck Index'),
    ]
    return f'''<div class="analytics-subtabs" role="tablist" aria-label="Analytics sections">
        <button class="analytics-subtab active" type="button" onclick="showAnalyticsSubtab('insights', this)">McDraft Insights <span>{len(insight_rows[:13])}</span></button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('matrices', this)">Matrix Lab <span>{len(_matrix_cards)}</span></button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('ratings', this)">Rating Lab</button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('player', this)">Player Analytics <span>{len(player_charts)}</span></button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('relationships', this)">Player Relationships</button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('river-passport', this)">Transfer River + Player Passport</button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('club', this)">Club Analytics <span>{len(club_charts)}</span></button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('squad-strength', this)">Squad Strength <span>{len(squad_strength_charts)}</span></button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('squad-build', this)">Squad Construction <span>{len(squad_construction_charts)}</span></button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('decisions', this)">Manager Decisions <span>{len(decision_charts)}</span></button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('availability-impact', this)">Availability Impact</button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('fixtures-h2h', this)">Fixtures & H2H <span>{len(fixture_analytics_charts)}</span></button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('season', this)">Overall Season <span>{len(season_charts)}</span></button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('league-stats', this)">League Stats</button>
    </div>
    <div class="card analytics-manager-filter-card">
        <div class="analytics-manager-filter-head"><div><h2>Manager filter</h2><p class="card-description">Select multiple managers to filter every manager-based chart, including the Matrix Lab and currently-owned players in Player Analytics. Use Top 5, All or None for quick selections. Free agents affect Player Analytics, Player Relationships and the Transfer River; Premier League club charts remain league-wide.</p></div><span id="analytics-manager-count" class="muted"></span></div>
        <div id="analytics-manager-chips" class="chart-chip-row analytics-manager-chip-row"></div>
        <label class="analytics-average-toggle"><input id="analytics-average-toggle" type="checkbox" onchange="toggleAnalyticsLeagueAverage(this.checked)"> Compare with league average</label>
    </div>
    <div class="analytics-subpage active" id="analytics-sub-insights"><div class="card analytics-hero"><h2>McDraft Insights</h2><p class="card-description">Generated from the latest captured league, squad, fixture and transfer data.</p><div class="analytics-insight-grid">{insights}</div></div></div>
    <div class="analytics-subpage" id="analytics-sub-matrices">{matrix_html}</div>
    <div class="analytics-subpage" id="analytics-sub-ratings">{rating_lab_html()}</div>
    <div class="analytics-subpage" id="analytics-sub-player">
        <div class="analytics-player-summary"><p class="card-description">Use the shared Manager filter above to choose one or more current fantasy owners. Player dots and bars retain each team’s colour; free agents are grey. League-wide positional-scarcity comparisons remain unchanged.</p><span id="analytics-player-count" class="muted" aria-live="polite"></span></div>
        <div class="analytics-chart-grid">{''.join(player_charts)}</div>
    </div>
    <div class="analytics-subpage" id="analytics-sub-relationships">{player_relationship_html()}</div>
    <div class="analytics-subpage" id="analytics-sub-river-passport">{transfer_river_passport_html()}</div>
    <div class="analytics-subpage" id="analytics-sub-club"><div class="analytics-chart-grid">{''.join(club_charts)}</div></div>
    <div class="analytics-subpage" id="analytics-sub-squad-strength"><div class="analytics-chart-grid">{''.join(squad_strength_charts)}</div></div>
    <div class="analytics-subpage" id="analytics-sub-squad-build"><div class="analytics-chart-grid">{''.join(squad_construction_charts)}</div></div>
    <div class="analytics-subpage" id="analytics-sub-decisions"><div class="analytics-chart-grid">{''.join(decision_charts)}</div></div>
    <div class="analytics-subpage" id="analytics-sub-availability-impact">{_availability_impact_charts()}</div>
    <div class="analytics-subpage" id="analytics-sub-fixtures-h2h"><div class="analytics-chart-grid">{''.join(fixture_analytics_charts)}</div></div>
    <div class="analytics-subpage" id="analytics-sub-season"><div class="analytics-chart-grid">{''.join(season_charts)}</div></div>
    <div class="analytics-subpage" id="analytics-sub-league-stats">
        <div class="card"><h2>Fun Stats</h2>__FUN_STATS__</div>
        <div class="card"><h2>Manager Profiles</h2><div class="manager-profile-grid">__MANAGER_PROFILE_CARDS__</div></div>
        <div class="card"><h2>League &amp; Cup Records</h2><p class="card-description">League records plus Cup leg scores, aggregate margins, upsets and the GW26 final as they happen.</p><div class="records-grid">__LEAGUE_RECORDS__</div></div>
        <div class="card"><h2>League Summary</h2><div class="stats-grid">
            <div class="stat-card"><div class="stat-label">Managers</div><div class="stat-value">__MANAGER_COUNT__</div><div class="stat-description">Active league managers</div></div>
            <div class="stat-card"><div class="stat-label">Completed Gameweeks</div><div class="stat-value">__FINISHED_COUNT__</div><div class="stat-description">Gameweeks captured</div></div>
            <div class="stat-card"><div class="stat-label">Players Analysed</div><div class="stat-value">__PLAYER_COUNT__</div><div class="stat-description">Players appearing in the draft</div></div>
            <div class="stat-card"><div class="stat-label">Fixtures</div><div class="stat-value">__FIXTURE_COUNT__</div><div class="stat-description">Completed H2H fixtures</div></div>
        </div></div>
    </div>'''

# ---------------------------- Draft Centre ----------------------------
def draft_centre_page_html():
    original = history.get('original_draft_rank', {}) or {}
    points_lookup = {int(p.get('id')): float(p.get('season_points',0) or 0) for p in player_form_stats if p.get('id') is not None}
    name_lookup = {int(p.get('id')): p.get('name','Unknown') for p in player_form_stats if p.get('id') is not None}

    draft_rows=[]
    for pid_text, info in original.items():
        try:
            pid=int(pid_text)
        except (TypeError,ValueError):
            continue
        pick=int(info.get('overall_pick', UNDRAFTED_PLAYER_RANK) or UNDRAFTED_PLAYER_RANK)
        if pick>DRAFTED_PLAYER_COUNT:
            continue
        meta=elements.get(pid,{})
        name=name_lookup.get(pid) or meta.get('web_name') or f'Player {pid}'
        club=teams_lookup.get(meta.get('team'),'—')
        pos=positions_lookup.get(meta.get('element_type'),'—')
        original_manager=info.get('manager') or 'Unknown'
        current_owner=_dashboard_current_owner.get(pid)
        draft_rows.append({
            'id':pid,'pick':pick,'round':int(info.get('round',0) or 0),
            'round_pick':int(info.get('round_pick',0) or 0),'name':name,'club':club,
            'position':pos,'manager':original_manager,'current_owner':current_owner or 'Free Agent',
            'official_rank':_official_draft_rank(pid),
            'blended_rank':_blended_draft_rank(pid),
            'points':points_lookup.get(pid,float(meta.get('total_points',0) or 0)),
            'retained':current_owner==original_manager,
        })
    draft_rows.sort(key=lambda r:r['pick'])

    # Redraft today: rank every current FPL player by points to date, but display
    # the top 150 so it mirrors the original McDraft board size.
    all_players=[]
    for pid,meta in elements.items():
        all_players.append({
            'id':pid,'name':meta.get('web_name','Unknown'),'club':teams_lookup.get(meta.get('team'),'—'),
            'position':positions_lookup.get(meta.get('element_type'),'—'),
            'points':float(meta.get('total_points',0) or 0),
            'original_pick':int((original.get(str(pid),{}) or {}).get('overall_pick', UNDRAFTED_PLAYER_RANK) or UNDRAFTED_PLAYER_RANK),
        })
    all_players.sort(key=lambda r:(-r['points'],r['name']))
    for i,row in enumerate(all_players,1):
        row['redraft_pick']=i
        row['delta']=(row['original_pick']-i) if row['original_pick']<=DRAFTED_PLAYER_COUNT else None

    manager_summary={m:{'points':0.0,'retained':0,'picks':0,'delta_sum':0.0,'delta_n':0,'steals':0,'busts':0,'late_points':0.0,'early_points':0.0} for m in managers}
    perf_rank={row['id']:i for i,row in enumerate(sorted(draft_rows,key=lambda r:(-r['points'],r['name'])),1)}
    round_points=defaultdict(list)
    for row in draft_rows:
        sm=manager_summary.setdefault(row['manager'],{'points':0.0,'retained':0,'picks':0,'delta_sum':0.0,'delta_n':0,'steals':0,'busts':0,'late_points':0.0,'early_points':0.0})
        sm['points']+=row['points']; sm['picks']+=1; sm['retained']+=1 if row['retained'] else 0
        if row['round']<=5: sm['early_points']+=row['points']
        else: sm['late_points']+=row['points']
        pr=perf_rank.get(row['id'],row['pick'])
        delta=row['pick']-pr
        sm['delta_sum']+=delta; sm['delta_n']+=1
        if delta>=20: sm['steals']+=1
        if delta<=-20: sm['busts']+=1
        round_points[row['round']].append(row['points'])

    draft_points={m:v['points'] for m,v in manager_summary.items()}
    retained={m:v['retained'] for m,v in manager_summary.items()}
    avg_delta={m:(v['delta_sum']/v['delta_n'] if v['delta_n'] else 0) for m,v in manager_summary.items()}
    late_points={m:v['late_points'] for m,v in manager_summary.items()}
    early_points={m:v['early_points'] for m,v in manager_summary.items()}
    round_avg={f'Round {r}':(statistics.mean(vals) if vals else 0) for r,vals in sorted(round_points.items())}

    biggest_steals=[]; biggest_busts=[]
    for row in draft_rows:
        delta=row['pick']-perf_rank.get(row['id'],row['pick'])
        biggest_steals.append((row['name'],delta))
        biggest_busts.append((row['name'],delta))

    # A few generated draft-night observations.
    observations=[]
    if draft_points:
        best_mgr=max(draft_points,key=draft_points.get)
        observations.append(('Draft output leader',f"{best_mgr}'s original picks have produced {draft_points[best_mgr]:.0f} fantasy points so far."))
    if avg_delta:
        value_mgr=max(avg_delta,key=avg_delta.get)
        observations.append(('Best pick-value profile',f"{value_mgr}'s original selections are outperforming their draft slots by {avg_delta[value_mgr]:.1f} ranking places on average."))
    if retained:
        loyal=max(retained,key=retained.get)
        observations.append(('Most original picks retained',f"{loyal} still own {retained[loyal]} players from their original draft haul."))
    if all_players:
        undrafted=[r for r in all_players if r['original_pick']>DRAFTED_PLAYER_COUNT]
        if undrafted:
            gem=max(undrafted,key=lambda r:r['points'])
            observations.append(('Undrafted gem',f"{gem['name']} went undrafted and has since produced {gem['points']:.0f} FPL points."))

    insight_html=''.join(f'<div class="analytics-insight"><span>{escape_html(k)}</span><strong>{escape_html(v)}</strong></div>' for k,v in observations)
    charts=''.join([
        _bar_chart_html('Original draft output by manager',draft_points,'Season FPL points generated by each manager’s original 15 selections, wherever those players are now.',x_label='Manager',y_label='Points'),
        _bar_chart_html('Original picks still retained',retained,x_label='Manager',y_label='Players retained'),
        _bar_chart_html('Average draft-slot overperformance',avg_delta,'Positive means the original picks are, on average, performing above their draft slots.',x_label='Manager',y_label='Ranking places'),
        _bar_chart_html('First five rounds: points produced',early_points,x_label='Manager',y_label='Points'),
        _bar_chart_html('Rounds 6+: points produced',late_points,x_label='Manager',y_label='Points'),
        _category_bar_chart_html('Average output by draft round',list(round_avg.items()),'Average season points per player selected in each round.',x_label='Draft round',y_label='Average points',limit=20),
        _category_bar_chart_html('Biggest draft steals',biggest_steals,'Original pick minus current performance rank.',x_label='Player',y_label='Places above draft slot',limit=20),
        _category_bar_chart_html('Biggest draft busts',biggest_busts,'The most negative draft-slot deltas.',reverse=True,x_label='Player',y_label='Draft rank delta',limit=20),
    ])

    redraft_rows=''
    for row in all_players[:40]:
        original_label=f"#{row['original_pick']}" if row['original_pick']<=DRAFTED_PLAYER_COUNT else 'Undrafted'
        move='—' if row['delta'] is None else (f"+{row['delta']}" if row['delta']>0 else str(row['delta']))
        redraft_rows += f'''<tr><td><strong>#{row['redraft_pick']}</strong></td><td>{escape_html(row['name'])}</td><td>{escape_html(row['position'])}</td><td>{escape_html(row['club'])}</td><td>{row['points']:.0f}</td><td>{original_label}</td><td>{move}</td></tr>'''

    board_rows=''
    for row in draft_rows:
        owner=row['current_owner']
        status='Retained' if row['retained'] else ('Free Agent' if owner=='Free Agent' else f'Now: {owner}')
        _official = f"#{int(row['official_rank'])}" if row.get('official_rank') is not None else '—'
        board_rows += f'''<tr><td><strong>#{row['pick']}</strong></td><td>{_official}</td><td>{row['blended_rank']:.0f}</td><td>R{row['round']}</td><td>{escape_html(row['name'])}</td><td>{escape_html(row['position'])}</td><td>{escape_html(row['club'])}</td><td>{escape_html(row['manager'])}</td><td>{row['points']:.0f}</td><td>{escape_html(status)}</td></tr>'''

    return f'''<div class="analytics-subtabs draft-centre-tabs" role="tablist" aria-label="Draft Centre sections">
        <button class="analytics-subtab draft-centre-tab active" type="button" onclick="showDraftCentreSubtab('overview',this)">Draft Overview</button>
        <button class="analytics-subtab draft-centre-tab" type="button" onclick="showDraftCentreSubtab('redraft',this)">Redraft Today</button>
        <button class="analytics-subtab draft-centre-tab" type="button" onclick="showDraftCentreSubtab('board',this)">Original Draft Board</button>
    </div>
    <div class="draft-centre-subpage active" id="draft-centre-sub-overview">
        <div class="card analytics-hero"><h2>Draft Night, Revisited</h2><p class="card-description">The original 150 picks versus what actually happened afterwards, now shown alongside the official FPL Draft rank. Historical McDraft picks stay untouched; blended pedigree is used only for modelling.</p><div class="analytics-insight-grid">{insight_html}</div></div>
        <div class="analytics-chart-grid">{charts}</div>
    </div>
    <div class="draft-centre-subpage" id="draft-centre-sub-redraft"><div class="card"><h2>Redraft Today — Top 40</h2><p class="card-description">If McDraft drafted again today using season FPL points as the board.</p><div class="table-wrap"><table><thead><tr><th>Redraft</th><th>Player</th><th>Pos</th><th>Club</th><th>Pts</th><th>Original</th><th>Value Δ</th></tr></thead><tbody>{redraft_rows}</tbody></table></div></div></div>
    <div class="draft-centre-subpage" id="draft-centre-sub-board"><div class="card"><h2>Original Draft Board</h2><p class="card-description">Every original selection, current output and where that asset lives now.</p><div class="table-wrap"><table><thead><tr><th>McDraft Pick</th><th>FPL Rank</th><th>Blend</th><th>Round</th><th>Player</th><th>Pos</th><th>Club</th><th>Drafted by</th><th>Pts</th><th>Status</th></tr></thead><tbody>{board_rows}</tbody></table></div></div></div>'''

# ============================================================
# PAGE DATA
# ============================================================

