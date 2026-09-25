def safe_js_json(raw):
    text = raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=True)
    return (
        text
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def _last_sunday(year, month):
    """Return the day number of the last Sunday in a month."""
    last_day = calendar.monthrange(year, month)[1]
    dt = datetime(year, month, last_day)
    return last_day - ((dt.weekday() + 1) % 7)


def format_london_timestamp(raw):
    """Format an ISO UTC timestamp as UK local time without requiring tzdata.

    Prefer the system IANA database when it exists. Pydroid installations often
    omit it, so fall back to the UK DST rule: BST runs from 01:00 UTC on the
    last Sunday in March until 01:00 UTC on the last Sunday in October.
    """
    if not raw:
        return ""

    dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt_utc = dt.astimezone(timezone.utc)

    try:
        return dt_utc.astimezone(ZoneInfo("Europe/London")).strftime(
            "%d %b %Y, %H:%M %Z"
        )
    except Exception:
        year = dt_utc.year
        bst_start = datetime(
            year, 3, _last_sunday(year, 3), 1, 0, tzinfo=timezone.utc
        )
        bst_end = datetime(
            year, 10, _last_sunday(year, 10), 1, 0, tzinfo=timezone.utc
        )
        is_bst = bst_start <= dt_utc < bst_end
        local_dt = dt_utc + (timedelta(hours=1) if is_bst else timedelta(0))
        return local_dt.strftime("%d %b %Y, %H:%M") + (" BST" if is_bst else " GMT")


html = html_template

replacements = {

    "__LEAGUE_NAME__":
        escape_html(
            league_name
        ),

    "__LAST_UPDATED__":
        escape_html(
            format_london_timestamp(history.get("last_updated", ""))
        ),

    "__FINISHED_COUNT__":
        str(
            len(finished_gws)
        ),

    "__MANAGER_COUNT__":
        str(
            len(managers)
        ),

    "__PLAYER_COUNT__":
        str(
            len(player_ownership)
        ),

    "__FIXTURE_COUNT__":
        str(
            len(matches)
        ),

    "__MY_TEAM_OPTIONS__":
        "".join(
            f'<option value="{index}" {"selected" if index == default_my_team_index() else ""}>{escape_html(manager)}</option>'
            for index, manager in enumerate(current_standings)
        ),

    "__MY_TEAM_CARDS__":
        my_team_cards(),

    "__SQUAD_VULNERABILITY_DATA__":
        safe_js_json(squad_vulnerability_json),

    "__TRADES_TABLE__":
        trades_table(latest_transfer_gw),

    "__TRADE_SIMULATOR__":
        trade_simulator_html(),

    "__TRADE_SIMULATOR_DATA__":
        json.dumps(_trade_simulator_payload(), ensure_ascii=False),

    "__RECENT_WAIVER_ACTIVITY__":
        waiver_activity_table(current_only=True),

    "__WAIVER_ARCHIVE__":
        waiver_activity_table(current_only=False),

    "__HISTORICAL_TRADES__":
        historical_trades_table(),

    "__LATEST_TRANSFER_GW__":
        str(latest_transfer_gw if latest_transfer_gw is not None else "—"),

    "__RECENT_TRANSFER_ACTIVITY__":
        recent_transfer_activity_table(),

    "__TRANSFER_ARCHIVE__":
        transfer_archive_table(),

    "__TRANSFER_TEAM_OPTIONS__":
        "".join(
            f'<option value="{escape_html(manager)}">{escape_html(manager)}</option>'
            for manager in sorted(managers)
        ),

    "__BEST_HISTORICAL_TRANSFERS__":
        best_historical_transfers_table(),

    "__PLAYER_CLUB_OPTIONS__":
        "".join(
            f'<option value="{escape_html(club)}">{escape_html(club)}</option>'
            for club in sorted(
                {
                    teams_lookup.get(
                        p.get("team"),
                        "—"
                    )
                    for p in elements.values()
                    if p.get("team") in teams_lookup
                }
            )
        ),

    "__PLAYER_FANTASY_OPTIONS__":
        "".join(
            f'<option value="{escape_html(manager)}">{escape_html(manager)}</option>'
            for manager in current_standings
        ),

    "__FIXTURES_PAGE__":
        fixtures_page_html(),

    "__DRAFT_CENTRE__":
        draft_centre_page_html(),

    "__ANALYTICS_PAGE__":
        analytics_page_html(),
    "__PLAYER_RELATIONSHIPS__": safe_js_json(player_relationships_json),
    "__WAIVER_INTELLIGENCE_HTML__": waiver_intelligence_html(),
    "__MANAGER_WAR_ROOM__": safe_js_json(manager_war_room_json),
    "__TRANSFER_RIVER_PASSPORT__": safe_js_json(transfer_river_passport_json),
    "__HEALTH_OWNER_OPTIONS__": "".join(f'<option value="{escape_html(m)}">{escape_html(m)}</option>' for m in managers),
    "__HEALTH_CLUB_OPTIONS__": "".join(f'<option value="{escape_html(t)}">{escape_html(t)}</option>' for t in sorted(set(teams_lookup.values()))),

    "__STANDINGS_TABLE__":
        standings_table(),

    "__MANAGER_WAR_ROOM_HTML__":
        manager_war_room_html(),

    "__LIVE_CENTRE_PAGE__": (
        '<section class="page" id="page-live-centre"><div class="page-heading"><h1>Live Centre</h1><p>Matchday control room for the whole McDraft league.</p></div>' + live_centre_html() + '</section>'
        if dashboard_game_state == "live" else ""
    ),

    "__LIVE_CENTRE_MENU_ITEM__": (
        "['Live Centre','live-centre']," if dashboard_game_state == "live" else ""
    ),

    "__SEASON_SIMULATOR_HTML__":
        season_simulator_html(),

    "__OVERVIEW_UPCOMING_FIXTURES__":
        overview_next_fixtures_html(),

    "__POWER_RANKINGS_TABLE__":
        power_rankings_table(),

    "__PREMIER_LEAGUE_TABLE__":
        premier_league_table_html(),

    "__LUCK_INDEX_TABLE__":
        luck_index_table(),

    "__SEASON_PREDICTION_TABLE__":
        season_prediction_table(),

    "__POSITION_PROBABILITY_TABLE__":
        position_probability_table(),

    "__SQUAD_PEDIGREE_TABLE__":
        squad_pedigree_table(),

    "__PROJECTED_FIXTURE_ODDS__":
        projected_fixture_odds_table(),

    "__LIVE_FIXTURE_ODDS__":
        live_fixture_odds_table(),

    "__LATEST_LEAGUE_STORYLINE__":
        latest_league_storyline_html(),

    "__HOME_GAME_STATE_TITLE__":
        escape_html(homepage_game_state_title()),

    "__HOME_GAME_STATE_PANEL__":
        homepage_game_state_html(),

    "__SEASON_TIMELINE_EXPLORER__":
        season_timeline_explorer_html(),

    "__MANAGERS_OF_MONTH__":
        manager_of_month_html(),

    "__SEASON_MILESTONES__":
        season_milestones_html(),

    "__RECORD_CHASE__":
        record_chase_html(),

    "__SHARE_CARDS__":
        share_cards_html(),

    "__SEASON_TIMELINE_DATA__":
        json.dumps(season_evolution_data(), ensure_ascii=False),

    "__SEASON_SUMMARY__":
        season_summary_html(),

    "__GAMEWEEK_SUMMARY_SECTIONS__":
        gameweek_summary_sections(),

    "__FUTURE_FIXTURE_SECTIONS__":
        future_fixture_sections(),

    "__FUTURE_FIXTURE_GAMEWEEKS__":
        json.dumps(future_fixture_gameweeks),

    "__FIRST_FUTURE_GW__":
        str(future_fixture_gameweeks[0] if future_fixture_gameweeks else "—"),

    "__MANAGER_PROFILE_CARDS__":
        manager_profile_cards(),

    "__LEAGUE_RECORDS__":
        league_records_html(),

    "__LIVE_AS_IT_STANDS_CARD__": (
        f'''<div class="card live-standings-card"><h2>Live League Table</h2>{live_as_it_stands_table()}</div>'''
        if dashboard_game_state == "live"
        else ""
    ),

    "__RESULTS_SECTIONS__":
        results_sections,

    "__FIXTURE_DETAIL_SECTIONS__":
        fixture_detail_sections,

    "__LATEST_RESULTS_GW__":
        str(
            latest_results_gw
            if latest_results_gw is not None
            else "—"
        ),

    "__TOTW_SECTIONS__":
        totw_sections,

    "__LATEST_TOTW_GW__":
        str(
            latest_totw_gw
            if latest_totw_gw is not None
            else "—"
        ),

    "__AWARDS_TABLE__":
        awards_table(),

    "__TOP_PLAYER_CARDS__":
        top_player_cards,

    "__TOP_PLAYERS_TABLE__":
        top_players_table(),

    "__FORM_TABLE__":
        form_table(),

    "__TRANSFERS_CHART__":
        transfers_div,

    "__TRANSFER_TABLE__":
        transfer_table(),

    "__TEAM_HOPPERS_CHART__":
        team_hoppers_div,

    "__TRANSFER_ROI__":
        transfer_roi_table(),

    "__ABANDONED_ASSETS__":
        abandoned_assets_table(),

    "__FUN_STATS__":
        fun_stats_html,

    "__MCDRAFT_CUP_HTML__": cup_page_html(mcdraft_cup, dashboard_target_gw, dashboard_game_state),

    "__CSS__":
        css + radar_health_css + vulnerability_css + relationship_css + river_passport_css + war_room_css + simulator_css + wi_css + cup_css,

    "__JAVASCRIPT__":
        javascript.replace("__WAIVER_INTELLIGENCE_DATA__", safe_js_json(waiver_intelligence_json)).replace("__SEASON_SIMULATOR_DATA__", safe_js_json(season_simulator_json)).replace("__HEALTH_ANALYTICS__", safe_js_json(json.dumps(health_analytics_data, ensure_ascii=False))).replace(
            "__TOTW_GAMEWEEKS__",
            safe_js_json(json.dumps(finished_gws))
        ).replace(
            "__RESULT_GAMEWEEKS__",
            safe_js_json(json.dumps(gameweek_browser_gameweeks))
        ).replace(
            "__DASHBOARD_DISPLAY_GW__",
            str(dashboard_display_gw or 0)
        ).replace(
            "__FIXTURE_PREDICTION_GW__",
            str(fixture_prediction_gw or 0)
        ).replace(
            "__DASHBOARD_GAME_STATE__",
            dashboard_game_state
        ).replace(
            "__DASHBOARD_TARGET_GW__",
            str(dashboard_target_gw or 0)
        ).replace(
            "__PLAYER_SEARCH_DATA__",
            safe_js_json(player_search_json)
        ).replace(
            "__INJURY_LIST__", safe_js_json(injury_list_json)
        ).replace(
            "__CLUB_EXPLORER_DATA__", safe_js_json(club_explorer_json)
        ).replace(
            "__PL_FIXTURE_BROWSER__",
            safe_js_json(pl_fixture_browser_json)
        ).replace(
            "__FREE_AGENT_RECOMMENDATIONS__",
            safe_js_json(free_agent_recommendations_json)
        ).replace(
            "__H2H_RECORDS__",
            safe_js_json(h2h_records_json)
        ).replace(
            "__TRADE_TARGETS__",
            safe_js_json(trade_targets_json)
        ).replace(
            "__SELL_HIGH_CANDIDATES__",
            safe_js_json(sell_high_candidates_json)
        ).replace(
            "__DEFAULT_MY_TEAM_INDEX__",
            str(default_my_team_index())
        ).replace(
            "__MY_TEAM_HISTORY_DATA__",
            safe_js_json(my_team_history_json)
        ).replace(
            "__MY_TEAM_POSITION_NEEDS__",
            safe_js_json(positional_need_json)
        ).replace(
            "__FIVE_GW_PLANNER__",
            safe_js_json(five_gw_planner_json)
        ).replace(
            "__TRADE_SIMULATOR_DATA__",
            safe_js_json(json.dumps(_trade_simulator_payload(), ensure_ascii=False))
        ).replace(
            "__CHART_H2H_DATA__",
            safe_js_json(chart_h2h_json)
        ).replace(
            "__CHART_RANK_DATA__",
            safe_js_json(chart_rank_json)
        ).replace(
            "__CHART_SCORES_DATA__",
            safe_js_json(chart_scores_json)
        ).replace(
            "__CHART_CUMULATIVE_DATA__",
            safe_js_json(chart_cumulative_json)
        ).replace(
            "__MANAGER_ORDER__",
            safe_js_json(manager_order_json)
        ).replace(
            "__MANAGER_COLORS__",
            safe_js_json(manager_colors_json)
        ).replace(
            "__CUP_DETAIL_DATA__",
            safe_js_json(json.dumps(cup_detail_payload(mcdraft_cup, history.get("gameweeks", {})), ensure_ascii=False))
        )

}


# Run more than one pass because some generated page fragments contain
# placeholders of their own (for example League Stats is injected by the
# Analytics page). A single ordered pass can therefore leave literal
# __PLACEHOLDER__ text behind if the inner placeholder was processed first.
for _ in range(3):
    changed = False
    for placeholder, value in replacements.items():
        updated = html.replace(placeholder, value)
        if updated != html:
            changed = True
            html = updated
    if not changed:
        break


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE = (
    "index.html"
)


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        html
    )


# ============================================================
# OUTPUT
# ============================================================

print()
print("=" * 70)
print("FPL DRAFT DASHBOARD GENERATED")
print("=" * 70)
print()
print(
    f"Dashboard saved to: {OUTPUT_FILE}"
)
print()
print(
    f"Completed GWs: {finished_gws}"
)
print(
    f"Result GWs: {result_gameweeks}"
)
print(
    f"Managers: {len(managers)}"
)
print(
    f"Players analysed: {len(player_ownership)}"
)
print(
    f"Fixtures: {len(matches)}"
)
print()
print(
    "Pages:"
)
print(
    "  1. Overview"
)
print(
    "  2. Gameweeks"
)
print(
    "  3. Players"
)
print(
    "  4. Transfers"
)
print(
    "  5. Analytics"
)
print()


# ============================================================
# DISPLAY
# ============================================================

display(
    IFrame(
        OUTPUT_FILE,
        width="100%",
        height=1000
    )
)
