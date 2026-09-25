def apply_chart_layout(
    fig,
    title,
    x_title,
    y_title,
    height=430
):

    fig.update_layout(

        title=dict(
            text=title,
            x=0,
            xanchor="left",
            font=dict(size=18)
        ),

        xaxis_title=x_title,

        yaxis_title=y_title,

        template="plotly_dark",

        autosize=True,

        height=height,

        paper_bgcolor="#111827",

        plot_bgcolor="#111827",

        font=dict(
            color="#e5e7eb",
            size=12
        ),

        margin=dict(
            l=55,
            r=15,
            t=65,
            b=65
        ),

        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="left",
            x=0,
            font=dict(size=10),
            itemwidth=70
        ),

        hoverlabel=dict(
            font=dict(size=12)
        )

    )


# ============================================================
# MOBILE-FRIENDLY TREND CHART DATA (H2H points, rank, raw scores)
# ============================================================
#
# These three panels used to be dense multi-line Plotly charts, which
# work fine with a mouse but are hard to read on a phone: tiny legend
# text, ten-plus overlapping lines, and hover-only tooltips that don't
# work on touch. They are now rendered as lightweight custom SVG line
# charts (see the JS "MOBILE TREND CHARTS" section below) with:
#   - a manager chip picker (defaults to the current top 5) instead of
#     a crowded legend,
#   - fat, touch-friendly lines,
#   - tap-a-gameweek-column to reveal a big, sorted readout panel
#     instead of relying on hover tooltips.
#
# We just need to hand the raw per-manager time series to the page as
# JSON; the chart-building itself happens in JS so it can respond to
# taps without a full server round trip.

def serialize_history(series_by_manager):

    return {
        manager: [
            [gw, value]
            for gw, value in points
        ]
        for manager, points in series_by_manager.items()
    }


chart_h2h_json = json.dumps(
    serialize_history(h2h_points_history),
    ensure_ascii=False
)

chart_rank_json = json.dumps(
    serialize_history(rank_history),
    ensure_ascii=False
)

chart_scores_json = json.dumps(
    serialize_history(raw_score_by_gw),
    ensure_ascii=False
)

chart_cumulative_json = json.dumps(
    serialize_history(cumulative_score_history),
    ensure_ascii=False
)

manager_order_json = json.dumps(
    current_standings,
    ensure_ascii=False
)

manager_colors_json = json.dumps(
    MANAGER_COLOR_MAP,
    ensure_ascii=False
)


# ============================================================
# TRANSFER CHART
# ============================================================

transfer_chart_players = (
    most_transferred_players[
        :TOP_TRANSFERRED_COUNT
    ]
)


fig_transfers = go.Figure()


fig_transfers.add_trace(
    go.Bar(

        x=[
            p["transfers"]
            for p in transfer_chart_players
        ],

        y=[
            p["name"]
            for p in transfer_chart_players
        ],

        orientation="h"

    )
)


apply_chart_layout(
    fig_transfers,
    "Most Transferred Players",
    "Ownership Changes",
    "Player",
    550
)


fig_transfers.update_layout(
    yaxis=dict(
        autorange="reversed"
    )
)


# ============================================================
# TEAM HOPPER CHART
# ============================================================

team_hopper_players = (
    most_owned_managers[
        :TOP_TEAM_HOPPERS_COUNT
    ]
)


fig_team_hoppers = go.Figure()


fig_team_hoppers.add_trace(
    go.Bar(

        x=[
            p["owners"]
            for p in team_hopper_players
        ],

        y=[
            p["name"]
            for p in team_hopper_players
        ],

        orientation="h"

    )
)


apply_chart_layout(
    fig_team_hoppers,
    "Players Used By The Most Managers",
    "Different Managers",
    "Player",
    550
)


fig_team_hoppers.update_layout(
    yaxis=dict(
        autorange="reversed"
    )
)


# ============================================================
# PLOTLY HTML
# ============================================================

# fig_transfers is now the first Plotly figure rendered on the page
# (the H2H / rank / scores panels are custom SVG, not Plotly), so it
# is responsible for pulling in plotly.js from the CDN.

transfers_div = pio.to_html(
    fig_transfers,
    full_html=False,
    include_plotlyjs="cdn",
    config={
        "responsive": True,
        "displayModeBar": False,
        "scrollZoom": False
    }
)


team_hoppers_div = pio.to_html(
    fig_team_hoppers,
    full_html=False,
    include_plotlyjs=False,
    config={
        "responsive": True,
        "displayModeBar": False,
        "scrollZoom": False
    }
)


# ============================================================
# HTML TABLE HELPERS
# ============================================================

def standings_table():

    rows = ""

    for position, manager in enumerate(
        current_standings,
        start=1
    ):

        previous_rank = (
            rank_history[manager][-2][1]
            if len(rank_history[manager]) >= 2
            else position
        )

        movement = previous_rank - position

        if movement > 0:
            movement_html = f'<span class="rank-up">↑ {movement}</span>'
        elif movement < 0:
            movement_html = f'<span class="rank-down">↓ {abs(movement)}</span>'
        else:
            movement_html = '<span class="rank-flat">—</span>'

        form = manager_form_data.get(manager, [])[-5:]

        form_html = "".join(
            f'<span class="form-badge form-{result.lower()}">{result}</span>'
            for result in form
        ) or '<span class="muted">—</span>'

        safe_manager = escape_html(manager)
        # A single horizontal line after sixth place; Cup seed details live
        # in the Cup tab, not beside every manager in the league table.
        cutline_class = 'cup-cutline-row' if position == 7 and len(current_standings) == 10 else ''
        rows += f"""
            <tr class="{cutline_class}">
                <td class="rank-cell">{position}</td>
                <td class="manager-name">{safe_manager}</td>
                <td>{movement_html}</td>
                <td><div class="form-badges">{form_html}</div></td>
                <td>{league_points[manager]:.0f}</td>
                <td>{matches_won[manager]}-{matches_drawn[manager]}-{matches_lost[manager]}</td>
                <td>{points_for[manager]:.0f}</td>
                <td>{points_against[manager]:.0f}</td>
                <td><b>{season_prediction.get(manager, {}).get("median_finish", position)}{_ordinal_suffix(season_prediction.get(manager, {}).get("median_finish", position))}</b></td>
                <td>{mathematical_finish_range.get(manager, {}).get("text", "—")}</td>
            </tr>
        """

    return f"""
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Manager</th>
                        <th>Move</th>
                        <th>Form</th>
                        <th>League Pts</th>
                        <th>W-D-L</th>
                        <th>Pts For</th>
                        <th>Pts Against</th>
                        <th>Pred. Finish</th>
                        <th>Possible Finish</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    """


def power_rankings_table():

    rows = ''
    for position, manager in enumerate(power_rankings, start=1):
        league_position = manager_current_rank.get(manager, position)
        movement = league_position - position
        if movement > 0:
            movement_html = f'<span class="rank-up">↑ {movement}</span>'
        elif movement < 0:
            movement_html = f'<span class="rank-down">↓ {abs(movement)}</span>'
        else:
            movement_html = '<span class="rank-flat">—</span>'

        rows += f'''
            <tr>
                <td class="rank-cell">{position}</td>
                <td class="manager-name">{escape_html(manager)}</td>
                <td><b>{power_score.get(manager, 0):.1f}</b></td>
                <td>{norm_recent_form.get(manager, 0):.0f}</td>
                <td>{norm_season_quality.get(manager, 0):.0f}</td>
                <td>{norm_fixture_aware_squad.get(manager, 0):.0f}</td>
                <td>{norm_squad_management.get(manager, 0):.0f}</td>
                <td>{norm_league_position.get(manager, 0):.0f}</td>
                <td>{movement_html}</td>
            </tr>
        '''

    return f'''
        <div class="power-formula">
            <b>Power score:</b> 25% recent 5GW scoring + 20% season scoring quality + 25% fixture-aware squad strength + 10% squad-management efficiency + 20% current league position. Club strength evolves as real PL/FPL evidence accumulates.
        </div>
        <div class="table-wrap">
            <table>
                <thead><tr><th>#</th><th>Manager</th><th>Power</th><th>5GW Form</th><th>Season</th><th>Fixture Squad</th><th>Management</th><th>Table</th><th>vs Table</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    '''


def luck_index_table():
    ordered = sorted(managers, key=lambda m: (-luck_index.get(m, 0), m))
    rows = ''
    for manager in ordered:
        luck = luck_index.get(manager, 0.0)
        luck_class = 'rank-up' if luck > 0.05 else ('rank-down' if luck < -0.05 else 'rank-flat')
        sign = '+' if luck > 0 else ''
        rows += f'''
            <tr>
                <td class="manager-name">{escape_html(manager)}</td>
                <td>{actual_finished_league_points.get(manager, 0):.0f}</td>
                <td>{expected_league_points.get(manager, 0):.1f}</td>
                <td><span class="{luck_class}">{sign}{luck:.1f}</span></td>
                <td>{opponent_avg_score.get(manager, 0):.1f}</td>
            </tr>
        '''
    return f'''
        <div class="power-formula">
            <b>Luck Index:</b> actual league points minus expected league points after neutralising each starting XI for the difficulty of the real Premier League fixtures faced that GW. Positive = H2H results ahead of fixture-adjusted performance; negative = the rough end of the draw.
        </div>
        <div class="table-wrap">
            <table>
                <thead><tr><th>Manager</th><th>Actual LP</th><th>Expected LP</th><th>Luck</th><th>Opponent Avg</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    '''


def awards_table():

    rows = ""

    for award in weekly_awards:

        rows += f"""
            <tr>

                <td>
                    GW{award["gw"]}
                </td>

                <td>
                    {escape_html(award["motw"])}
                    <span class="muted">
                        ({award["motw_pts"]})
                    </span>
                </td>

                <td>
                    {escape_html(award["stinker"])}
                    <span class="muted">
                        ({award["stinker_pts"]})
                    </span>
                </td>

                <td>
                    {escape_html(award["bench"])}
                    <span class="muted">
                        ({award["bench_pts"]})
                    </span>
                </td>

                <td>
                    {escape_html(award["dt_king"])}
                    <span class="muted">
                        ({award["dt_count"]})
                    </span>
                </td>

            </tr>
        """

    return f"""
        <div class="table-wrap">

            <table>

                <thead>

                    <tr>

                        <th>GW</th>

                        <th>Manager of the Week</th>

                        <th>Stinker</th>

                        <th>Best Bench</th>

                        <th>Dream Team King</th>

                    </tr>

                </thead>

                <tbody>

                    {rows}

                </tbody>

            </table>

        </div>
    """


def top_players_table():

    rows = ""

    for index, player in enumerate(
        top_players_by_season[
            :TOP_PLAYERS_COUNT
        ],
        start=1
    ):

        avg5 = (
            f"{player['avg_5']:.1f}"
            if player["avg_5"] is not None
            else "—"
        )

        avg10 = (
            f"{player['avg_10']:.1f}"
            if player["avg_10"] is not None
            else "—"
        )

        trend = (
            f"{player['trend']:+.1f}"
            if player["trend"] is not None
            else "—"
        )

        trend_class = ""

        if player["trend"] is not None:

            if player["trend"] > 0:
                trend_class = "positive"

            elif player["trend"] < 0:
                trend_class = "negative"

        rows += f"""
            <tr>

                <td>
                    {index}
                </td>

                <td class="manager-name">
                    {escape_html(player["name"])}
                </td>

                <td>
                    {player["season_points"]}
                </td>

                <td>
                    {avg5}
                </td>

                <td>
                    {avg10}
                </td>

                <td class="{trend_class}">
                    {trend}
                </td>

                <td>
                    {player["owners"]}
                </td>

            </tr>
        """

    return f"""
        <div class="table-wrap">

            <table>

                <thead>

                    <tr>

                        <th>#</th>

                        <th>Player</th>

                        <th>Season Pts</th>

                        <th>5 GW Avg</th>

                        <th>10 GW Avg</th>

                        <th>Trend</th>

                        <th>Managers Used By</th>

                    </tr>

                </thead>

                <tbody>

                    {rows}

                </tbody>

            </table>

        </div>
    """


def form_table():

    if len(finished_gws) < 5:

        return """
            <div class="notice">
                5-gameweek form will appear once
                Gameweek 5 has been completed.
            </div>
        """

    rows = ""

    for index, player in enumerate(
        top_players_by_5[
            :TOP_PLAYERS_COUNT
        ],
        start=1
    ):

        avg5 = (
            f"{player['avg_5']:.1f}"
            if player["avg_5"] is not None
            else "—"
        )

        avg10 = (
            f"{player['avg_10']:.1f}"
            if player["avg_10"] is not None
            else "—"
        )

        trend = (
            f"{player['trend']:+.1f}"
            if player["trend"] is not None
            else "—"
        )

        trend_class = ""

        if player["trend"] is not None:

            if player["trend"] > 0:
                trend_class = "positive"

            elif player["trend"] < 0:
                trend_class = "negative"

        rows += f"""
            <tr>

                <td>
                    {index}
                </td>

                <td class="manager-name">
                    {escape_html(player["name"])}
                </td>

                <td>
                    {avg5}
                </td>

                <td>
                    {avg10}
                </td>

                <td class="{trend_class}">
                    {trend}
                </td>

                <td>
                    {player["owners"]}
                </td>

            </tr>
        """

    ten_week_note = ""

    if len(finished_gws) < 10:

        ten_week_note = """
            <div class="notice">
                10-gameweek averages will appear once
                Gameweek 10 has been completed.
            </div>
        """

    return f"""
        {ten_week_note}

        <div class="table-wrap">

            <table>

                <thead>

                    <tr>

                        <th>#</th>

                        <th>Player</th>

                        <th>5 GW Avg</th>

                        <th>10 GW Avg</th>

                        <th>Trend</th>

                        <th>Managers Used By</th>

                    </tr>

                </thead>

                <tbody>

                    {rows}

                </tbody>

            </table>

        </div>
    """


def transfer_table():

    rows = ""

    for index, player in enumerate(
        most_transferred_players[
            :TOP_TRANSFERRED_COUNT
        ],
        start=1
    ):

        rows += f"""
            <tr>

                <td>
                    {index}
                </td>

                <td class="manager-name">
                    {escape_html(player["name"])}
                </td>

                <td>
                    {player["transfers"]}
                </td>

                <td>
                    {player["owners"]}
                </td>

            </tr>
        """

    return f"""
        <div class="table-wrap">

            <table>

                <thead>

                    <tr>

                        <th>#</th>

                        <th>Player</th>

                        <th>Ownership Changes</th>

                        <th>Managers Used By</th>

                    </tr>

                </thead>

                <tbody>

                    {rows}

                </tbody>

            </table>

        </div>
    """


def abandoned_assets_table():

    if not abandoned_assets:

        return """
            <div class="notice">
                No abandoned assets found yet.
            </div>
        """

    rows = ""

    for asset in abandoned_assets[:20]:

        rows += f"""
            <tr>

                <td class="manager-name">
                    {escape_html(asset["player"])}
                </td>

                <td>
                    {escape_html(asset["manager"])}
                </td>

                <td>
                    GW{asset["dropped_gw"]}
                </td>

                <td class="negative">
                    {asset["points_after"]}
                </td>

            </tr>
        """

    return f"""
        <div class="table-wrap">

            <table>

                <thead>

                    <tr>

                        <th>Player</th>

                        <th>Manager</th>

                        <th>Dropped</th>

                        <th>Points After</th>

                    </tr>

                </thead>

                <tbody>

                    {rows}

                </tbody>

            </table>

        </div>
    """


def transfer_roi_table():

    if not transfer_roi:

        return """
            <div class="notice">
                No transfer activity captured yet.
            </div>
        """

    rows = ""

    for entry in transfer_roi:

        net_class = "positive" if entry["net_roi"] > 0 else ("negative" if entry["net_roi"] < 0 else "")

        rows += f"""
            <tr>

                <td class="manager-name">
                    {escape_html(entry["manager"])}
                </td>

                <td>
                    {entry["points_gained"]}
                </td>

                <td class="negative">
                    {entry["points_given_away"]}
                </td>

                <td class="{net_class}">
                    {"+" if entry["net_roi"] > 0 else ""}{entry["net_roi"]}
                </td>

            </tr>
        """

    return f"""
        <div class="table-wrap">

            <table>

                <thead>

                    <tr>

                        <th>Manager</th>

                        <th>Points Gained</th>

                        <th>Points Given Away</th>

                        <th>Net ROI</th>

                    </tr>

                </thead>

                <tbody>

                    {rows}

                </tbody>

            </table>

        </div>
    """


# ============================================================
# PHASE 1 UI DATA
# ============================================================


def latest_team_data(manager):
    
    # Try to get the most recent gameweek (finished or current)
    all_gws = sorted([int(gw) for gw in history.get("gameweeks", {}).keys()], reverse=True)
    
    for gw in all_gws:
        gw_snapshot = history["gameweeks"][str(gw)]
        teams = gw_snapshot.get("teams", {})
        is_finished = gw_snapshot.get("finished", False)
        
        for team_data in teams.values():
            if team_data.get("manager") == manager:
                return gw, team_data, is_finished

    return None, None, False


def manager_team_card(manager, card_index):
    gw, team_data, is_finished = latest_team_data(manager)
    if not team_data:
        return f"""<div class="my-team-card" data-manager-index="{card_index}"><div class="notice">Could not find {escape_html(manager)} in the captured data.</div></div>"""
    
    # Prefer the official match score; only estimate from picks when
    # no match record exists yet for this manager/gw.
    official_points = official_gw_score(manager, gw)
    if official_points is not None:
        latest_gw_points = official_points
    elif is_finished:
        latest_gw_points = team_data.get("gw_points", 0)
    else:
        latest_gw_points = team_data.get("live_points", team_data.get("gw_points", 0))
    selection = optimal_xi_by_manager_gw.get(gw, {}).get(manager, {})
    form = manager_form_data.get(manager, [])[-5:]
    form_html = "".join(f'<span class="form-badge form-{r.lower()}">{r}</span>' for r in form) or '<span class="muted">—</span>'
    starters = team_data.get("starters", [])
    bench = team_data.get("bench", [])
    starter_html = "".join(f'<div class="squad-row"><span>{escape_html(p.get("web_name", "Unknown"))}</span><b>{p.get("points", 0)}</b></div>' for p in sorted(starters, key=lambda x: int(x.get("points", 0) or 0), reverse=True)) or '<div class="muted">No starting XI captured.</div>'
    bench_html = "".join(f'<div class="squad-row bench-row"><span>{escape_html(p.get("web_name", "Unknown"))}</span><b>{p.get("points", 0)}</b></div>' for p in sorted(bench, key=lambda x: int(x.get("points", 0) or 0), reverse=True)) or '<div class="muted">No bench captured.</div>'
    rank = manager_current_rank.get(manager, "—")
    style = manager_style_profile(manager)
    style_tags_html = "".join(
        '<span class="manager-style-tag" title="{}">{}</span>'.format(
            escape_html(tag["description"]), escape_html(tag["name"])
        )
        for tag in style["tags"]
    )
    style_descriptions_html = "".join(
        '<div class="manager-style-explainer"><b>{}</b><span>{}</span></div>'.format(
            escape_html(tag["name"]), escape_html(tag["description"])
        )
        for tag in style["tags"]
    )
    style_metrics_html = (
        '<div class="manager-style-metrics">'
        f'<span><b>{style["activity_per_gw"]:.2f}</b> moves/GW</span>'
        f'<span><b>{style["efficiency"]:.1f}%</b> XI efficiency</span>'
        f'<span><b>{style["bench_per_gw"]:.1f}</b> bench pts/GW</span>'
        f'<span><b>{style["volatility"]:.1f}</b> score volatility</span>'
        '</div>'
    )
    return f"""
        <div class="my-team-card" data-manager-index="{card_index}" style="display:none;">
            <div class="my-team-grid">
                <div>
                    <div class="my-team-hero">
                        <div>
                            <div class="eyebrow">MY TEAM · GW{gw}</div>
                            <div class="my-team-name">{escape_html(manager)}</div>
                            <div class="form-badges">{form_html}</div>
                        </div>
                        <div class="my-team-rank"><span>#{rank}</span><small>{league_points.get(manager, 0):.0f} league pts</small></div>
                    </div>
                    <div class="stats-grid compact-stats">
                        <div class="stat-card"><div class="stat-label">Latest GW</div><div class="stat-value">{latest_gw_points}</div><div class="stat-description">Team points</div></div>
                        <div class="stat-card"><div class="stat-label">Avg Score</div><div class="stat-value">{avg_points.get(manager, 0):.1f}</div><div class="stat-description">Per gameweek</div></div>
                        <div class="stat-card"><div class="stat-label">Selection Efficiency</div><div class="stat-value">{selection.get("efficiency", 0):.1f}%</div><div class="stat-description">Latest GW optimal XI</div></div>
                        <div class="stat-card"><div class="stat-label">Points Missed</div><div class="stat-value">{manager_selection.get(manager, {}).get("missed", 0)}</div><div class="stat-description">Against optimal XIs</div></div>
                    </div>
                    <div class="manager-style-card">
                        <div class="manager-style-header"><div><div class="eyebrow">MANAGER STYLE</div><h3>Season profile</h3></div><div class="manager-style-tags">{style_tags_html}</div></div>
                        {style_descriptions_html}
                        {style_metrics_html}
                    </div>
                </div>
                <div class="squad-card"><h3>Latest Squad</h3><div class="squad-columns"><div><div class="squad-heading">Starting XI</div>{starter_html}</div><div><div class="squad-heading">Bench</div>{bench_html}</div></div></div>
            </div>
        </div>
    """


def my_team_cards():
    return "".join(manager_team_card(manager, index) for index, manager in enumerate(current_standings))


def default_my_team_index():
    if DEFAULT_MY_TEAM in current_standings:
        return current_standings.index(DEFAULT_MY_TEAM)
    return 0 if current_standings else -1


def _gw_story_choice(rng, options):
    return options[rng.randrange(len(options))] if options else ""


def _gameweek_player_standout(gw):
    """Return the highest-scoring owned player captured for a completed GW."""
    best = None
    seen = set()
    gw_data = history.get("gameweeks", {}).get(str(gw), {}).get("teams", {})

    for team_data in gw_data.values():
        manager = team_data.get("manager", "Unknown")
        players = (team_data.get("starters", []) or []) + (team_data.get("bench", []) or [])
        for player in players:
            player_id = player.get("element_id")
            if player_id in seen:
                continue
            seen.add(player_id)
            try:
                pts = int(player.get("points", 0) or 0)
            except (TypeError, ValueError):
                pts = 0
            name = player.get("web_name") or elements.get(player_id, {}).get("web_name", "Unknown")
            if best is None or pts > best["points"]:
                best = {"name": name, "points": pts, "manager": manager}

    return best


def _gameweek_story(gw, scores, fixtures):
    """Create a deterministic, varied recap from the actual captured GW data."""
    rng = random.Random((LEAGUE_ID * 1000) + int(gw))
    if not scores:
        return "No completed scoring data was captured for this gameweek."

    ranked = sorted(scores, key=lambda x: x[1], reverse=True)
    highest = ranked[0]
    lowest = ranked[-1]
    average = statistics.mean([score for _, score in ranked])
    standout = _gameweek_player_standout(gw)

    decided = [m for m in fixtures if m.get("score1") != m.get("score2")]
    biggest = max(decided, key=lambda m: abs(m["score1"] - m["score2"])) if decided else None
    closest = min(decided, key=lambda m: abs(m["score1"] - m["score2"])) if decided else None

    opener = _gw_story_choice(rng, [
        f"GW{gw} belonged to {highest[0]}, who set the pace with {highest[1]} points.",
        f"{highest[0]} topped the GW{gw} scoring charts on {highest[1]} points.",
        f"Nobody could match {highest[0]} in GW{gw}: {highest[1]} points was the week's best return.",
        f"The headline score in GW{gw} came from {highest[0]}, finishing on {highest[1]} points.",
        f"{highest[0]} came flying out of GW{gw} with a league-best {highest[1]} points.",
        f"GW{gw} saw {highest[0]} lead the way, banking {highest[1]} points.",
    ])

    fixture_sentence = ""
    if biggest:
        if biggest["score1"] > biggest["score2"]:
            winner, loser, ws, ls = biggest["team1"], biggest["team2"], biggest["score1"], biggest["score2"]
        else:
            winner, loser, ws, ls = biggest["team2"], biggest["team1"], biggest["score2"], biggest["score1"]
        margin = ws - ls
        if margin >= 20:
            fixture_sentence = _gw_story_choice(rng, [
                f"The week's biggest hiding came as {winner} absolutely dismantled {loser} {ws}-{ls}.",
                f"{winner} ran riot against {loser}, handing out a {ws}-{ls} spanking.",
                f"There was no mercy from {winner}, who steamrolled {loser} {ws}-{ls}.",
                f"{loser} had a week to forget after {winner} blew them away {ws}-{ls}.",
                f"{winner} made very short work of {loser}, thumping them {ws}-{ls}.",
                f"The demolition job of the week belonged to {winner}: {ws}-{ls} over {loser}.",
            ])
        elif margin >= 10:
            fixture_sentence = _gw_story_choice(rng, [
                f"{winner} were comfortable winners over {loser}, taking it {ws}-{ls}.",
                f"{winner} put {loser} firmly away with a {ws}-{ls} victory.",
                f"A strong {winner} performance saw off {loser} {ws}-{ls}.",
                f"{winner} had too much for {loser}, winning {ws}-{ls}.",
            ])
        else:
            fixture_sentence = _gw_story_choice(rng, [
                f"{winner} edged {loser} {ws}-{ls} in the week's tightest scrap.",
                f"{winner} just about escaped with the points, squeezing past {loser} {ws}-{ls}.",
                f"Fine margins decided it as {winner} nicked a {ws}-{ls} win over {loser}.",
                f"{loser} pushed them all the way, but {winner} survived {ws}-{ls}.",
            ])

    extras = []
    if closest and closest is not biggest:
        if closest["score1"] > closest["score2"]:
            cw, cl, cws, cls = closest["team1"], closest["team2"], closest["score1"], closest["score2"]
        else:
            cw, cl, cws, cls = closest["team2"], closest["team1"], closest["score2"], closest["score1"]
        extras.append(_gw_story_choice(rng, [
            f"At the other end of the drama scale, {cw} scraped past {cl} {cws}-{cls}.",
            f"The nail-biter went to {cw}, who pinched it {cws}-{cls} against {cl}.",
            f"Only {cws-cls} point{'s' if cws-cls != 1 else ''} separated {cw} and {cl}, with {cw} coming out on top.",
        ]))

    if standout and standout["points"] > 0:
        extras.append(_gw_story_choice(rng, [
            f"On the player front, {standout['name']} was the standout with {standout['points']} points for {standout['manager']}.",
            f"{standout['name']} produced the individual performance of the week, returning {standout['points']} points for {standout['manager']}.",
            f"No player in the captured squads bettered {standout['name']}'s {standout['points']}-point haul for {standout['manager']}.",
            f"{standout['manager']} had {standout['name']} to thank for a superb {standout['points']}-point contribution.",
        ]))

    if lowest[1] < average - 8:
        extras.append(_gw_story_choice(rng, [
            f"Down at the other end, {lowest[0]} endured a stinker on {lowest[1]} points, well below the league average of {average:.1f}.",
            f"It was rough going for {lowest[0]}: just {lowest[1]} points against a league average of {average:.1f}.",
            f"{lowest[0]} brought up the rear with {lowest[1]} points and will probably be happy to see the back of GW{gw}.",
        ]))

    paragraphs = [opener]
    if fixture_sentence:
        paragraphs.append(fixture_sentence)
    if extras:
        rng.shuffle(extras)
        paragraphs.append(" ".join(extras[:2]))
    return "\n\n".join(paragraphs)



DERBY_RIVALRIES = [
    ("The Christian Classico", "Kamararama FC", "Buendophilia"),
    ("The Brammer Derby", "NoRSNoRB No Chance", "Backstreet Moyes"),
    ("The Cheltenham Derby", "Ollie Gonna Squashya", "No Weimann No Cry"),
    ("The Sadly Broke Scuffle", "danny’s doggy dudes", "PAUer Rangers"),
    ("The Bald Derby", "Jaap? Best Stam", "Backstreet Moyes"),
    ("The Shit Beard Rivalry", "Jacquet Potato", "No Weimann No Cry"),
]


def _norm_team_name(value):
    return " ".join(str(value or "").replace("’", "'").lower().split())


def _derby_name(team1, team2):
    pair = {_norm_team_name(team1), _norm_team_name(team2)}
    for derby, a, b in DERBY_RIVALRIES:
        if pair == {_norm_team_name(a), _norm_team_name(b)}:
            return derby
    return None


def _all_schedule_by_gw():
    schedule = defaultdict(list)
    for match in league_matches_all:
        try:
            gw = int(match.get("event"))
        except (TypeError, ValueError):
            continue
        e1 = match.get("league_entry_1")
        e2 = match.get("league_entry_2")
        t1 = league_entry_id_to_name.get(e1, league_entry_id_to_name.get(str(e1), "Unknown"))
        t2 = league_entry_id_to_name.get(e2, league_entry_id_to_name.get(str(e2), "Unknown"))
        schedule[gw].append({"team1": t1, "team2": t2, "finished": bool(match.get("finished"))})
    return schedule


full_fixture_schedule = _all_schedule_by_gw()

# Fixture odds belong only to the next UNPLAYED gameweek. If a gameweek is
# already live, skip it and project the following one instead.
_fixture_odds_after_gw = (
    int(dashboard_target_gw or 0)
    if dashboard_target_is_live
    else int(dashboard_last_finished_gw or 0)
)
fixture_prediction_gw = next(
    (
        gw for gw in sorted(full_fixture_schedule)
        if int(gw) > _fixture_odds_after_gw
        and any(not fixture.get("finished") for fixture in full_fixture_schedule.get(gw, []))
    ),
    None,
)


# ============================================================
# MATHEMATICAL FINISH RANGE
# ============================================================
# Separate from the prediction model: this uses current league points plus
# the maximum 3 points still available from each remaining H2H fixture.

