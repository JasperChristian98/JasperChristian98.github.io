"""Run the extracted McDraft stages in their original execution order.

This is an incremental modularisation of a notebook-derived script, not a claim
that the legacy stages are independently importable yet. Each stage remains
normal Python source, and a single explicit context preserves all of the
original script's shared global bindings across stages. The manifest and tests
check that the extraction is lossless.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import traceback
from datetime import datetime, timezone

from .league_honours import (
    build_honours,
    render_awards,
    render_records,
    render_record_chase,
    extra_manager_tags,
    CSS as HONOURS_CSS,
)
from .decision_centre import (
    make_decisions,
    DECISION_CENTRE_HTML,
    DECISION_CENTRE_CSS,
    javascript_with_data,
)
from .prediction_accuracy import (
    read_store,
    capture_forecast,
    evaluate,
    render_report,
    PREDICTION_ACCURACY_CSS,
    STORE_NAME,
)
from .manager_preference import (
    MANAGER_WELCOME_HTML,
    MANAGER_HEADER_HTML,
    MANAGER_PICKER_CSS,
    integrate_client,
)
from .war_room_layout import move_war_room, WAR_ROOM_NAV_JS
from .layout_and_odds import update_layout, shared_fixture_odds, CSS as LAYOUT_CSS, JS as LAYOUT_JS
from .editorial_expansion import RADAR_CSS, RADAR_JS, add_column_desks, humanise_column_story
from .manager_styles_page import (
    build_manager_styles,
    PAGE_HTML as MANAGER_STYLES_HTML,
    CSS as MANAGER_STYLES_CSS,
    javascript_with_data as manager_styles_js,
)

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_DIR = PACKAGE_DIR.parent
STAGES_DIR = PACKAGE_DIR / "stages"


def stage_manifest() -> dict:
    return json.loads((PACKAGE_DIR / "manifest.json").read_text(encoding="utf-8"))


def run(*, root: Path = REPO_DIR, skip_display: bool = True) -> Path:
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    original_cwd = Path.cwd()
    original_ipython_display = None
    state = {
        "__name__": "__main__",
        # Mapping CSV is resolved using __file__ in the preserved original.
        "__file__": str(root / "Draft.py"),
        "__package__": None,
    }
    output = root / "index.html"
    # The original writes directly to index.html. Preserve the last known good
    # published page if rendering fails, while allowing original code to run.
    previous_html = output.read_bytes() if output.exists() else None
    try:
        os.chdir(root)
        for stage in stage_manifest()["stages"]:
            file = STAGES_DIR / stage["file"]
            print(f"\n>>> McDraft: {file.name} — {stage['description']}", flush=True)
            try:
                # Run code in the same explicit namespace as the original script.
                exec(compile(file.read_bytes(), str(file), "exec"), state)
                # An independently tested integration layer; legacy stages stay
                # byte-for-byte intact, retaining the original-source audit.
                if file.name == '03_match_analytics.py':
                    state['league_honours'] = build_honours(
                        state['history'], state.get('enriched_matches', []), state['managers'])
                    original_style_profile = state['manager_style_profile']
                    honours = state['league_honours']

                    def extended_style_profile(manager):
                        profile = original_style_profile(manager)
                        existing = {tag['name'] for tag in profile['tags']}
                        profile['tags'].extend(
                            tag for tag in extra_manager_tags(honours, manager)
                            if tag['name'] not in existing)
                        return profile

                    state['manager_style_profile'] = extended_style_profile
                    positions = {}
                    weeks = honours.get('weeks', []) if isinstance(honours, dict) else []
                    if weeks:
                        positions = dict(weeks[-1].get('positions', {}) or {})
                    state['manager_styles_data'] = build_manager_styles(
                        state['managers'], state['manager_style_profile'], positions=positions)
                elif file.name == '04_visualisations.py':
                    original_awards = state['awards_table']
                    honours = state['league_honours']

                    def expanded_awards_table():
                        return (original_awards() + '<h3>Extra Gameweek Accolades</h3>'
                                + render_awards(honours))

                    state['awards_table'] = expanded_awards_table
                elif file.name == '05_forecasts.py':
                    # Canonical, order-independent fixture forecast for all pages.
                    state['_fixture_odds_for_match'] = shared_fixture_odds(state['_fixture_odds_for_match'])
                    audit_path = root / STORE_NAME
                    audit_store = read_store(audit_path)
                    target = int(state.get('fixture_prediction_gw') or 0)
                    event = state.get('_dashboard_events', {}).get(target, {})
                    fixtures = state.get('full_fixture_schedule', {}).get(target, [])
                    # The existing model function must be available at stage 05.
                    if capture_forecast(
                        audit_store,
                        gw=target,
                        deadline=event.get('deadline_time'),
                        now=datetime.now(timezone.utc),
                        started=(bool(event.get('started')) or
                                 (target == state.get('dashboard_target_gw') and
                                  bool(state.get('dashboard_target_is_live')))),
                        fixtures=fixtures,
                        forecast=state['_fixture_odds_for_match'],
                    ):
                        from .prediction_accuracy import atomic_save
                        atomic_save(audit_path, audit_store)
                        print(f'Saved immutable GW{target} prediction snapshot')
                    # Match rows from the authoritative Draft endpoint; already
                    # enriched by stage 01 with exact manager names and scores.
                    state['prediction_accuracy_report'] = evaluate(
                        audit_store, state.get('enriched_matches', []))
                elif file.name == '06_live_and_planning.py':
                    original_records = state['league_records_html']
                    honours = state['league_honours']

                    def expanded_league_records():
                        return original_records() + render_records(honours)

                    state['league_records_html'] = expanded_league_records
                    original_chase = state['record_chase_html']

                    def expanded_chase():
                        return original_chase() + render_record_chase(honours)

                    state['record_chase_html'] = expanded_chase
                elif file.name == '07_pages.py':
                    state['decision_centre_data'] = make_decisions(
                        state['five_gw_planner_data'], json.loads(state['manager_war_room_json']),
                        state.get('dashboard_game_state', 'upcoming'))
                elif file.name == '09_client_assets.py':
                    state['css'] += (
                        DECISION_CENTRE_CSS + MANAGER_PICKER_CSS + PREDICTION_ACCURACY_CSS
                        + HONOURS_CSS + LAYOUT_CSS + RADAR_CSS + MANAGER_STYLES_CSS
                    )
                    state['javascript'] = integrate_client(state['javascript'])
                    state['javascript'] += '\n' + javascript_with_data(state['decision_centre_data'])
                    state['javascript'] += '\n' + WAR_ROOM_NAV_JS + '\n' + LAYOUT_JS + '\n' + RADAR_JS
                    state['javascript'] += '\n' + manager_styles_js(state['manager_styles_data'])
                elif file.name == '10_cup_and_template.py':
                    state['_mcdraft_column_intelligence'] = add_column_desks(
                        state['_mcdraft_column_intelligence'], state['league_honours'],
                        state.get('enriched_matches', []), state['history'])
                    state['league_storyline_for_gw'] = humanise_column_story(
                        state['league_storyline_for_gw'], state['league_honours'])
                    state['html_template'] = update_layout(move_war_room(state['html_template']))
                    analytics_anchor = '__ANALYTICS_PAGE__'
                    if state['html_template'].count(analytics_anchor) != 1:
                        raise RuntimeError('Analytics insertion point changed')
                    state['html_template'] = state['html_template'].replace(
                        analytics_anchor,
                        render_report(state['prediction_accuracy_report']) + '\n' + analytics_anchor,
                        1,
                    )
                    manager_styles_anchor = '<section class="page" id="page-analytics">'
                    if state['html_template'].count(manager_styles_anchor) != 1:
                        raise RuntimeError('Manager Styles insertion point changed')
                    state['html_template'] = state['html_template'].replace(
                        manager_styles_anchor,
                        MANAGER_STYLES_HTML + '\n\n        ' + manager_styles_anchor,
                        1,
                    )
                    styles_nav_entry = "['Manager Decisions','analytics','analytics','decisions'],"
                    if state['html_template'].count(styles_nav_entry) != 1:
                        raise RuntimeError('Manager Styles nav insertion point changed')
                    state['html_template'] = state['html_template'].replace(
                        styles_nav_entry,
                        "['Manager Styles','manager-styles'],\n  " + styles_nav_entry,
                        1,
                    )
                    anchor = '<div class="overview-subpage active" id="overview-sub-standings">'
                    if state['html_template'].count(anchor) != 1:
                        raise RuntimeError('Decision Centre standings insertion point changed')
                    state['html_template'] = state['html_template'].replace(
                        anchor,
                        DECISION_CENTRE_HTML + '\n' + anchor,
                        1,
                    )
                    body_anchor = '<body>'
                    if state['html_template'].count(body_anchor) != 1:
                        raise RuntimeError('Manager welcome body insertion point changed')
                    state['html_template'] = state['html_template'].replace(
                        body_anchor,
                        body_anchor + '\n' + MANAGER_WELCOME_HTML,
                        1,
                    )
                    # The selector belongs in the permanent header, directly
                    # after global search and before the light/dark mode control.
                    header_search = '''                <div id="global-search-results" class="global-search-results"></div>
            </div>'''
                    if state['html_template'].count(header_search) != 1:
                        raise RuntimeError('Global search/header insertion point changed')
                    state['html_template'] = state['html_template'].replace(
                        header_search,
                        header_search + '\n' + MANAGER_HEADER_HTML,
                        1,
                    )
            except Exception as exc:
                print(f"FAILED at stage {file.name}: {exc}", flush=True)
                raise
        if not output.is_file() or output.stat().st_size < 100_000:
            raise RuntimeError("index.html is missing or unexpectedly small")
        if b"</html>" not in output.read_bytes().lower():
            raise RuntimeError("index.html does not contain a closing HTML tag")
        print(f"\nSuccessful McDraft build: {output} ({output.stat().st_size:,} bytes)")
        return output
    except BaseException:
        # Do not leave GitHub Pages with a partial output on a failed build.
        if previous_html is not None:
            output.write_bytes(previous_html)
        elif output.exists():
            output.unlink()
        raise
    finally:
        os.chdir(original_cwd)
