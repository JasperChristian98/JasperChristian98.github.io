# Generated from: Scraper.ipynb
# Converted at: 2026-09-01T09:07:10.758Z
# Next step (optional): refactor into modules & generate tests with RunCell
# Quick start: pip install runcell

# DRAFT SCRAPER


import requests
import json
import os
import time
import math
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import calendar

# ============================================================
# CONFIG
# ============================================================

LEAGUE_ID = 17288
HISTORY_FILE = "fpl_draft_history.json"

DRAFT_BASE = "https://draft.premierleague.com/api"
CLASSIC_BASE = "https://fantasy.premierleague.com/api"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})


# ============================================================
# HELPER: FETCH JSON
# ============================================================

def fetch_json(url, retries=3, pause=1.5):

    for i in range(retries):

        try:
            r = session.get(url, timeout=15)
            r.raise_for_status()
            return r.json()

        except Exception as e:

            if i == retries - 1:
                print(f"FAILED: {url} -> {e}")
                return None

            time.sleep(pause)

    return None


# ============================================================
# 1. MASTER PLAYER / TEAM DATA
# ============================================================

classic_static = fetch_json(
    f"{CLASSIC_BASE}/bootstrap-static/"
)

if classic_static is None:
    raise RuntimeError("Could not fetch FPL classic API data.")


elements = {
    p["id"]: p
    for p in classic_static["elements"]
}

teams_lookup = {
    t["id"]: t["name"]
    for t in classic_static["teams"]
}

positions_lookup = {
    e["id"]: e["singular_name_short"]
    for e in classic_static["element_types"]
}


# ============================================================
# GAMEWEEKS
# ============================================================

events = classic_static["events"]

# ============================================================
# DRAFT GAME STATUS
# ============================================================

draft_game_status = fetch_json(
    f"{DRAFT_BASE}/game"
)

if draft_game_status is None:
    print("WARNING: Could not fetch Draft game status. Falling back to classic API finished events.")
    finished_events = [
        e["id"]
        for e in events
        if e["finished"]
    ]
    current_event = next(
        (
            e["id"]
            for e in events
            if e["is_current"]
        ),
        (finished_events[-1] + 1 if finished_events else 1)
    )
else:
    # Use Draft API to determine finished gameweeks
    current_event = draft_game_status.get("current_event", 1)
    current_event_finished = draft_game_status.get("current_event_finished", False)
    
    # All gameweeks before current are finished
    # Current gameweek is finished only if current_event_finished is True
    if current_event_finished:
        finished_events = list(range(1, current_event + 1))
    else:
        finished_events = list(range(1, current_event))
    
    print(
        f"Draft game status: GW{current_event} "
        f"({'FINISHED' if current_event_finished else 'IN PROGRESS'})"
    )

gws_to_capture = sorted(
    set(finished_events + [current_event])
)

print(
    f"Capturing gameweeks: {gws_to_capture} "
    f"(current live GW = {current_event}, "
    f"finished GWs = {finished_events})"
)


# ============================================================
# 2. LEAGUE DETAILS
# ============================================================

league_details = fetch_json(
    f"{DRAFT_BASE}/league/{LEAGUE_ID}/details"
)

if league_details is None:
    raise RuntimeError(
        "Could not fetch league details — "
        "check LEAGUE_ID and connectivity."
    )


league_entries = league_details.get(
    "league_entries",
    []
)

league_name = (
    league_details
    .get("league", {})
    .get("name", "FPL Draft League")
)

scoring = (
    league_details
    .get("league", {})
    .get("scoring", "h")
)


# ============================================================
# MANAGER NAME LOOKUP
#
# entry_id = actual FPL manager/team ID
# id       = Draft league-entry ID
# ============================================================

entry_id_to_name = {
    e["entry_id"]: (
        e.get("entry_name")
        or f"{e.get('player_first_name', '')} "
           f"{e.get('player_last_name', '')}"
    ).strip()

    for e in league_entries
    if e.get("entry_id")
}


# ============================================================
# MATCHES
# ============================================================

standings_now = league_details.get(
    "standings",
    []
)

matches = league_details.get(
    "matches",
    []
)

# Full live schedule retained for future-fixture browsing.
league_matches_all = list(matches)


# ============================================================
# ENRICH MATCHES WITH MANAGER NAMES
#
# IMPORTANT:
# matches use league_entry_1 / league_entry_2
# which refer to the league-entry "id", NOT entry_id.
# ============================================================

league_entry_id_to_name = {
    e["id"]: entry_id_to_name.get(
        e["entry_id"],
        "Unknown"
    )

    for e in league_entries
    if e.get("entry_id")
}


enriched_matches = []

for m in matches:

    # Only keep completed fixtures
    if not m.get("finished"):
        continue

    enriched_matches.append({
        "event": m.get("event"),

        "entry_1_name": league_entry_id_to_name.get(
            m.get("league_entry_1"),
            "Unknown"
        ),

        "entry_1_points": m.get(
            "league_entry_1_points",
            0
        ),

        "entry_2_name": league_entry_id_to_name.get(
            m.get("league_entry_2"),
            "Unknown"
        ),

        "entry_2_points": m.get(
            "league_entry_2_points",
            0
        ),
    })


print(
    f"Found {len(enriched_matches)} completed league matches."
)


# ============================================================
# 3. PER-GAMEWEEK LIVE PLAYER DATA
# ============================================================

def get_live_gw_data(gw):

    data = fetch_json(
        f"{CLASSIC_BASE}/event/{gw}/live/"
    )

    if not data:
        return {}

    return {
        el["id"]: {
            "points": el["stats"]["total_points"],
            "in_dreamteam": el["stats"]["in_dreamteam"],
            "minutes": el["stats"]["minutes"],
        }

        for el in data["elements"]
    }


# ============================================================
# 4. PER-MANAGER PICKS
# ============================================================

def get_entry_picks(entry_id, gw):

    return fetch_json(
        f"{DRAFT_BASE}/entry/{entry_id}/event/{gw}"
    )


# ============================================================
# 5. LOAD EXISTING HISTORY
# ============================================================

if os.path.exists(HISTORY_FILE):

    with open(
        HISTORY_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        history = json.load(f)

else:

    history = {
        "league_id": LEAGUE_ID,
        "league_name": league_name,
        "scoring": scoring,
        "gameweeks": {}
    }


# ============================================================
# UPDATE LEAGUE METADATA
# ============================================================

history["league_id"] = LEAGUE_ID
history["league_name"] = league_name
history["scoring"] = scoring

history["last_updated"] = (
    datetime.now(timezone.utc)
    .isoformat()
)

history["entry_names"] = entry_id_to_name

history["league_entry_id_to_name"] = (
    league_entry_id_to_name
)

history["standings_latest"] = standings_now

history["matches"] = enriched_matches


# ============================================================
# ORIGINAL DRAFT RANK / PICK ORDER
# ============================================================
# McDraft has 150 drafted players. Any player who was not selected in the
# original draft is assigned rank 151. This gives every current player a
# comparable pre-season rank and makes team-level draft-rank totals easy to
# interpret: lower is stronger.
DRAFTED_PLAYER_COUNT = 150
UNDRAFTED_PLAYER_RANK = 151

# Pin the league's original draft board into history so player strength can
# use the actual McDraft selection order as an early-season prior. `pick`
# restarts within each round, so convert (round, pick) to an overall pick.
# Once captured, the original rank stays attached to the player even if they
# are later traded, waived or picked up by somebody else.

draft_choices_payload = fetch_json(
    f"{DRAFT_BASE}/draft/{LEAGUE_ID}/choices"
)

if isinstance(draft_choices_payload, dict):
    draft_choices = draft_choices_payload.get("choices", [])
elif isinstance(draft_choices_payload, list):
    draft_choices = draft_choices_payload
else:
    draft_choices = []

league_size = max(len(league_entries), 1)
original_draft_rank = history.setdefault("original_draft_rank", {})

for choice in draft_choices:
    if not isinstance(choice, dict):
        continue

    player_id = choice.get("element")
    round_no = choice.get("round")
    round_pick = choice.get("pick")

    if player_id is None or round_no is None or round_pick is None:
        continue

    try:
        player_id = int(player_id)
        round_no = int(round_no)
        round_pick = int(round_pick)
    except (TypeError, ValueError):
        continue

    overall_pick = ((round_no - 1) * league_size) + round_pick
    entry_ref = choice.get("entry")
    manager_name = (
        league_entry_id_to_name.get(entry_ref)
        or league_entry_id_to_name.get(str(entry_ref))
        or entry_id_to_name.get(entry_ref)
        or entry_id_to_name.get(str(entry_ref))
    )

    # Preserve the earliest pinned value if the endpoint is ever malformed or
    # changes later; original draft position is historical and immutable.
    original_draft_rank.setdefault(str(player_id), {
        "overall_pick": overall_pick,
        "round": round_no,
        "round_pick": round_pick,
        "manager": manager_name,
        "was_auto": bool(choice.get("was_auto", False)),
    })

history["original_draft_rank"] = original_draft_rank


# ============================================================
# PLAYER IDENTITY PINNING
#
# FPL's live player database (bootstrap-static) has no concept of
# history - it only ever answers "what does this element_id mean
# right now." An element_id can get reassigned to a completely
# different real player later in the season (a squad departure
# frees an ID that a new signing then reuses), which would silently
# rewrite a pick's name/team/position if it were re-resolved from a
# fresh bootstrap-static fetch on every run.
#
# The picks themselves (which element_id was on a manager's roster
# for a given gameweek) ARE a stable historical record - the Draft
# API's per-gameweek entry/event endpoint always returns the same
# answer for a past gameweek. So the fix is: the first time this
# script ever captures a given (gameweek, element_id) pairing, pin
# its name/team/position permanently. Every later run - even while
# that gameweek is still in progress and its live points keep
# updating - reuses the pinned identity instead of re-resolving it,
# so ID churn can never retroactively relabel a pick.
#
# This is deliberately scoped per gameweek, not per element_id
# globally: a real player legitimately moving clubs mid-season
# should still show their correct historical club for each past
# gameweek, just never have it silently swapped for a different
# person under the same ID.
# ============================================================

def get_pinned_pick_identity(gw, entry_id, el_id):
    """
    Return the previously-captured {web_name, team, position} for
    this exact (gameweek, manager, player) pick, if this gameweek has
    already been captured at least once before (even if it's still
    in progress). Returns None if this pick has never been seen for
    this gameweek, in which case the caller should resolve it fresh
    from the current bootstrap-static data and it will be pinned
    from that point on.
    """

    existing_gw_snapshot = history.get("gameweeks", {}).get(str(gw))

    if not existing_gw_snapshot:
        return None

    existing_team = existing_gw_snapshot.get("teams", {}).get(str(entry_id))

    if not existing_team:
        return None

    for existing_pick in existing_team.get("starters", []) + existing_team.get("bench", []):
        if existing_pick.get("element_id") == el_id:
            return {
                "web_name": existing_pick.get("web_name", "Unknown"),
                "team": existing_pick.get("team", ""),
                "position": existing_pick.get("position", ""),
            }

    return None


# ============================================================
# 6. BUILD GAMEWEEK SNAPSHOTS
# ============================================================

for gw in gws_to_capture:

    # --------------------------------------------------------
    # FREEZE ALREADY-FINISHED GAMEWEEKS
    #
    # Once a gameweek has been captured with "finished": true, its
    # picks and player metadata (name/team/position) are locked in
    # for good. FPL's live player database is not stable over the
    # season - an element_id can get reassigned to a different real
    # player later (e.g. a squad departure frees an ID that a new
    # signing then reuses), so re-resolving metadata for an
    # already-finished gameweek from a later run's fresh API data
    # can silently rewrite history to show the wrong player. Once a
    # gameweek is finished, it is written exactly once and never
    # touched again, using the player database as it stood when
    # that gameweek actually happened.
    # --------------------------------------------------------

    existing_snapshot = history.get("gameweeks", {}).get(str(gw))

    if existing_snapshot and existing_snapshot.get("finished"):

        print(f"\nGW{gw} already finished and frozen - skipping re-capture.")

        continue

    print(f"\nProcessing GW{gw}...")

    live = get_live_gw_data(gw)

    # Use Draft API status to determine if gameweek is finished
    is_finished = gw in finished_events

    print(f"   GW{gw} status: {'FINISHED' if is_finished else 'IN PROGRESS'}")

    gw_snapshot = {
        "finished": is_finished,
        "teams": {}
    }

    # Get matches for this gameweek from league details
    gw_matches = [
        m for m in matches
        if m.get("event") == gw
    ]

    # Build a lookup: league_entry_id -> match_points
    match_points_lookup = {}
    for match in gw_matches:
        entry_1 = match.get("league_entry_1")
        entry_2 = match.get("league_entry_2")
        
        if entry_1:
            match_points_lookup[entry_1] = match.get("league_entry_1_points", 0)
        if entry_2:
            match_points_lookup[entry_2] = match.get("league_entry_2_points", 0)


    # --------------------------------------------------------
    # EACH MANAGER
    # --------------------------------------------------------

    for entry_id, manager_name in entry_id_to_name.items():

        print(
            f"   {manager_name} ({entry_id})..."
        )

        picks_data = get_entry_picks(
            entry_id,
            gw
        )

        if not picks_data or "picks" not in picks_data:

            print(
                f"      No picks returned for GW{gw}"
            )

            continue


        picks = picks_data["picks"]

        starters = []
        bench = []

        starting_points = 0
        bench_points = 0
        dreamteam_starters = 0


        # ----------------------------------------------------
        # PROCESS PICKS
        # ----------------------------------------------------

        for p in picks:

            el_id = p["element"]

            stats = live.get(
                el_id,
                {
                    "points": 0,
                    "in_dreamteam": False,
                    "minutes": 0
                }
            )

            pinned_identity = get_pinned_pick_identity(
                gw,
                entry_id,
                el_id
            )

            if pinned_identity is not None:

                web_name = pinned_identity["web_name"]
                team_name = pinned_identity["team"]
                position_name = pinned_identity["position"]

            else:

                meta = elements.get(
                    el_id,
                    {}
                )

                web_name = meta.get(
                    "web_name",
                    "Unknown"
                )

                team_name = teams_lookup.get(
                    meta.get("team"),
                    ""
                )

                position_name = positions_lookup.get(
                    meta.get("element_type"),
                    ""
                )


            pick_info = {
                "element_id": el_id,

                "web_name": web_name,

                "team": team_name,

                "position": position_name,

                "points": stats["points"],

                "in_dreamteam": stats[
                    "in_dreamteam"
                ],

                "is_captain": p.get(
                    "is_captain",
                    False
                ),

                "is_vice_captain": p.get(
                    "is_vice_captain",
                    False
                ),

                "minutes": stats["minutes"],
            }


            # ------------------------------------------------
            # STARTER
            # ------------------------------------------------

            if p["position"] <= 11:

                starters.append(
                    pick_info
                )

                pts = (
                    stats["points"]
                    *
                    (
                        2
                        if p.get("is_captain")
                        else 1
                    )
                )

                starting_points += pts

                if stats["in_dreamteam"]:
                    dreamteam_starters += 1


            # ------------------------------------------------
            # BENCH
            # ------------------------------------------------

            else:

                bench.append(
                    pick_info
                )

                bench_points += stats["points"]


        # ----------------------------------------------------
        # SAVE MANAGER SNAPSHOT
        # ----------------------------------------------------

        # Get the league_entry_id for this manager
        league_entry_id = next(
            (
                e["id"]
                for e in league_entries
                if e.get("entry_id") == entry_id
            ),
            None
        )

        # Get match points if available
        live_points = match_points_lookup.get(league_entry_id, starting_points)

        gw_snapshot["teams"][str(entry_id)] = {

            "manager": manager_name,

            "starters": starters,

            "bench": bench,

            "gw_points": starting_points,

            "live_points": live_points,  # Official match score

            "bench_points": bench_points,

            "dreamteam_starters": dreamteam_starters,

        }

        time.sleep(0.15)


    # --------------------------------------------------------
    # SAVE GW
    # --------------------------------------------------------

    history["gameweeks"][str(gw)] = (
        gw_snapshot
    )


# ============================================================
# 7. SAVE EVERYTHING
# ============================================================

with open(
    HISTORY_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        history,
        f,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("HISTORY SAVED")
print("=" * 70)

print(
    f"League: {league_name}"
)

print(
    f"Managers: {len(entry_id_to_name)}"
)

print(
    f"Gameweeks: {list(history['gameweeks'].keys())}"
)

print(
    f"Completed matches: {len(enriched_matches)}"
)

print(
    f"File: {HISTORY_FILE}"
)

import json
import statistics
import random
import time
import requests

from collections import defaultdict

import plotly.graph_objects as go
import plotly.io as pio

from IPython.display import IFrame, display


# ============================================================
# CONFIG
# ============================================================

HISTORY_FILE = "fpl_draft_history.json"
CLASSIC_BASE = "https://fantasy.premierleague.com/api"

TOP_PLAYERS_COUNT = 20
TOP_TRANSFERRED_COUNT = 15
TOP_TEAM_HOPPERS_COUNT = 15
DEFAULT_MY_TEAM = "Kamararama FC"


# ============================================================
# LOAD HISTORY
# ============================================================

with open(HISTORY_FILE, encoding="utf-8") as f:
    history = json.load(f)


league_name = history.get(
    "league_name",
    "FPL Draft League"
)

entry_names = history.get(
    "entry_names",
    {}
)

managers = list(
    dict.fromkeys(entry_names.values())
)

gameweeks = sorted(
    history.get("gameweeks", {}).keys(),
    key=int
)

finished_gws = [
    int(gw)
    for gw in gameweeks
    if history["gameweeks"][gw].get(
        "finished",
        False
    )
]


# ============================================================
# FPL API
# ============================================================

session = requests.Session()

session.headers.update({
    "User-Agent": "Mozilla/5.0"
})


def fetch_json(
    url,
    retries=3,
    pause=1.0
):

    for attempt in range(retries):

        try:

            response = session.get(
                url,
                timeout=15
            )

            response.raise_for_status()

            return response.json()

        except Exception as e:

            if attempt == retries - 1:

                print(
                    f"FAILED: {url} -> {e}"
                )

                return None

            time.sleep(pause)

    return None


print("Fetching current FPL player data...")


bootstrap = fetch_json(
    f"{CLASSIC_BASE}/bootstrap-static/"
)


if bootstrap is None:

    raise RuntimeError(
        "Could not retrieve FPL player data."
    )


elements = {
    p["id"]: p
    for p in bootstrap.get(
        "elements",
        []
    )
}


teams_lookup = {
    t["id"]: t["name"]
    for t in bootstrap.get(
        "teams",
        []
    )
}


positions_lookup = {
    e["id"]: e["singular_name_short"]
    for e in bootstrap.get(
        "element_types",
        []
    )
}


# ============================================================
# CURRENT DRAFT OWNERSHIP
# ============================================================
# element-status is the authoritative league-wide ownership list.
# This prevents players owned by other managers being treated as free agents.

league_element_status = fetch_json(
    f"{DRAFT_BASE}/league/{LEAGUE_ID}/element-status"
)

current_owner_by_player = {}
if isinstance(league_element_status, dict):
    for row in league_element_status.get("element_status", []):
        if isinstance(row, dict) and row.get("element") is not None:
            current_owner_by_player[int(row["element"])] = row.get("owner")


# ============================================================
# DASHBOARD GAME STATE
# ============================================================
dashboard_last_finished_gw = max(finished_gws) if finished_gws else 0
dashboard_target_gw = dashboard_last_finished_gw + 1

_dashboard_events = {
    int(event.get("id")): event
    for event in bootstrap.get("events", [])
    if event.get("id") is not None
}
_dashboard_target_event = _dashboard_events.get(dashboard_target_gw, {})

dashboard_target_started = bool(_dashboard_target_event.get("started", False))
dashboard_target_finished = bool(_dashboard_target_event.get("finished", False))

# Do not rely on bootstrap-static's `started` flag alone. In practice the
# Draft/live endpoints can begin returning real scores before that flag is
# reflected in the dashboard build. Treat the target GW as genuinely live
# when ANY reliable live signal says football has started.
_dashboard_live_payload = fetch_json(
    f"{CLASSIC_BASE}/event/{dashboard_target_gw}/live/"
) or {}

_dashboard_live_elements = _dashboard_live_payload.get("elements", [])

_dashboard_pl_fixtures = fetch_json(
    f"{CLASSIC_BASE}/fixtures/?event={dashboard_target_gw}"
) or []

dashboard_live_player_activity = any(
    int((row.get("stats") or {}).get("minutes", 0) or 0) > 0
    or int((row.get("stats") or {}).get("total_points", 0) or 0) != 0
    for row in _dashboard_live_elements
    if isinstance(row, dict)
)

_dashboard_target_matches = [
    match
    for match in (league_matches_all or [])
    if int(match.get("event", 0) or 0) == int(dashboard_target_gw)
]

dashboard_live_match_activity = any(
    int(match.get("league_entry_1_points", 0) or 0) != 0
    or int(match.get("league_entry_2_points", 0) or 0) != 0
    for match in _dashboard_target_matches
)

dashboard_target_is_live = (
    not dashboard_target_finished
    and (
        dashboard_target_started
        or dashboard_live_player_activity
        or dashboard_live_match_activity
    )
)

_dashboard_league_entry_names = history.get("league_entry_id_to_name", {})

def _dashboard_owner_name(owner):
    if owner in (None, "", 0, "0"):
        return None

    name = (
        _dashboard_league_entry_names.get(owner)
        or _dashboard_league_entry_names.get(str(owner))
    )
    if name:
        return name

    try:
        return entry_id_to_name.get(int(owner))
    except (TypeError, ValueError):
        return None

_dashboard_previous_owner = {}

if dashboard_last_finished_gw:
    _previous_snapshot = history.get("gameweeks", {}).get(
        str(dashboard_last_finished_gw), {}
    )

    for _team_data in _previous_snapshot.get("teams", {}).values():
        _manager = _team_data.get("manager")
        if not _manager:
            continue

        for _player in (
            _team_data.get("starters", [])
            + _team_data.get("bench", [])
        ):
            _pid = _player.get("element_id")
            if _pid is not None:
                _dashboard_previous_owner[int(_pid)] = _manager

_dashboard_current_owner = {
    int(player_id): _dashboard_owner_name(owner)
    for player_id, owner in current_owner_by_player.items()
}

dashboard_market_changes = []

_all_market_player_ids = set(_dashboard_previous_owner) | set(
    _dashboard_current_owner
)

for _pid in sorted(_all_market_player_ids):
    _old_owner = _dashboard_previous_owner.get(_pid)
    _new_owner = _dashboard_current_owner.get(_pid)

    if _old_owner == _new_owner:
        continue

    if _old_owner is None and _new_owner is None:
        continue

    _meta = elements.get(_pid, {})
    _player_name = _meta.get("web_name", f"Player {_pid}")

    if _old_owner is None and _new_owner is not None:
        _move_type = "Pickup"
    elif _old_owner is not None and _new_owner is None:
        _move_type = "Drop"
    else:
        _move_type = "Transfer"

    dashboard_market_changes.append({
        "player_id": _pid,
        "player": _player_name,
        "from_team": _old_owner or "Free Agent",
        "to_team": _new_owner or "Free Agent",
        "move": _move_type,
    })

dashboard_market_active = bool(dashboard_market_changes)

if dashboard_target_is_live:
    dashboard_game_state = "live"
elif dashboard_market_active:
    dashboard_game_state = "upcoming"
else:
    dashboard_game_state = "completed"

print(
    "Dashboard state: "
    f"{dashboard_game_state.upper()} | "
    f"last completed GW={dashboard_last_finished_gw} | "
    f"target GW={dashboard_target_gw} | "
    f"bootstrap_started={dashboard_target_started} | "
    f"player_activity={dashboard_live_player_activity} | "
    f"draft_score_activity={dashboard_live_match_activity} | "
    f"market changes={len(dashboard_market_changes)}"
)


dashboard_display_gw = (
    dashboard_target_gw
    if dashboard_game_state in ("upcoming", "live")
    else dashboard_last_finished_gw
)


# ============================================================
# PLAYER OWNERSHIP / TRANSFER ANALYSIS
# ============================================================

print(
    "Analysing player ownership..."
)


player_ownership = {}


for gw in finished_gws:

    gw_data = history[
        "gameweeks"
    ][str(gw)].get(
        "teams",
        {}
    )

    for entry_id, team_data in gw_data.items():

        manager = team_data.get(
            "manager",
            "Unknown"
        )

        players = (
            team_data.get(
                "starters",
                []
            )
            +
            team_data.get(
                "bench",
                []
            )
        )

        for player in players:

            player_id = player.get(
                "element_id"
            )

            if player_id is None:
                continue

            meta = elements.get(
                player_id,
                {}
            )

            player_name = (
                player.get(
                    "web_name"
                )
                or meta.get(
                    "web_name",
                    "Unknown"
                )
            )

            if player_id not in player_ownership:

                player_ownership[player_id] = {

                    "name": player_name,

                    "owners": set(),

                    "ownership_by_gw": {},

                    "first_gw": gw,

                    "last_gw": gw

                }

            info = player_ownership[
                player_id
            ]

            info["owners"].add(
                manager
            )

            info[
                "ownership_by_gw"
            ].setdefault(
                gw,
                set()
            ).add(
                manager
            )

            info["first_gw"] = min(
                info["first_gw"],
                gw
            )

            info["last_gw"] = max(
                info["last_gw"],
                gw
            )


# ============================================================
# NORMALISE PLAYER OWNERSHIP DATA
# ============================================================
# Some players may have been present in older/partial ownership data
# without the newer ownership_by_gw field.  Normalise every record
# before any downstream analytics access it.
for _player_id, _info in player_ownership.items():
    if not isinstance(_info, dict):
        player_ownership[_player_id] = {
            "name": "Unknown",
            "owners": set(),
            "ownership_by_gw": {},
            "first_gw": None,
            "last_gw": None,
        }
        continue

    _info.setdefault("name", elements.get(_player_id, {}).get("web_name", "Unknown"))
    _info.setdefault("owners", set())
    _info.setdefault("ownership_by_gw", {})
    _info.setdefault("first_gw", None)
    _info.setdefault("last_gw", None)


# ============================================================
# NORMALISE PLAYER OWNERSHIP DATA
# ============================================================
# Older/partial ownership records may not contain ownership_by_gw.
# Ensure every record has the fields used by downstream analytics.
for _player_id, _info in list(player_ownership.items()):
    if not isinstance(_info, dict):
        player_ownership[_player_id] = {
            "name": elements.get(_player_id, {}).get("web_name", "Unknown"),
            "owners": set(),
            "ownership_by_gw": {},
            "first_gw": None,
            "last_gw": None,
        }
    else:
        _info.setdefault("name", elements.get(_player_id, {}).get("web_name", "Unknown"))
        _info.setdefault("owners", set())
        _info.setdefault("ownership_by_gw", {})
        _info.setdefault("first_gw", None)
        _info.setdefault("last_gw", None)

# ============================================================
# COUNT PLAYER TRANSFER EVENTS
# ============================================================

player_transfer_counts = defaultdict(
    int
)

player_transfer_details = defaultdict(
    list
)


for player_id, info in player_ownership.items():

    previous_owners = set()

    for i, gw in enumerate(finished_gws):

        current_owners = info[
            "ownership_by_gw"
        ].get(
            gw,
            set()
        )

        # Skip transfer counting for GW1 (initial draft)
        if i == 0:
            previous_owners = current_owners
            continue

        joined = (
            current_owners
            -
            previous_owners
        )

        left = (
            previous_owners
            -
            current_owners
        )

        # A genuine transfer requires BOTH a manager picking the
        # player up AND a manager dropping them in the same
        # gameweek transition - i.e. an actual hand-off between two
        # rosters. If only one side happened (e.g. a pure free-agent
        # pickup with nobody dropping them, or a pure drop with
        # nobody claiming them), that is not a transfer, so it isn't
        # counted. When it is a genuine transfer, it counts once -
        # not once for the incoming manager and again for the
        # outgoing manager.
        if joined and left:

            for manager in joined:

                player_transfer_details[
                    player_id
                ].append({

                    "gw": gw,

                    "type": "IN",

                    "manager": manager

                })

            for manager in left:

                player_transfer_details[
                    player_id
                ].append({

                    "gw": gw,

                    "type": "OUT",

                    "manager": manager

                })

            player_transfer_counts[
                player_id
            ] += 1

        previous_owners = (
            current_owners
        )


# ============================================================
# PLAYER FPL HISTORY
# ============================================================

print(
    f"Fetching history for "
    f"{len(player_ownership)} players..."
)


# ============================================================
# PIN PER-GAMEWEEK PLAYER STATS ONCE FINISHED
#
# element-summary/{id}/ is queried by CURRENT element_id and returns
# that id's whole-season history in one shot - the same "only ever
# answers what does this ID mean right now" problem the picks data
# had. If an id gets reassigned to a different real player mid-
# season, a later fetch would silently return the new player's
# historical stats for gameweeks that already happened under the
# old player. So once a real-world gameweek is finished, its
# per-player record is pinned into history["player_scores"] and
# never re-fetched again; only the still-in-progress gameweek keeps
# refreshing live (points/minutes genuinely change as it's played).
# ============================================================

player_scores = history.setdefault(
    "player_scores",
    {}
)


def get_pinned_player_gw_record(player_id, gw):

    if gw not in finished_gws:
        return None

    return player_scores.get(
        str(player_id),
        {}
    ).get(
        str(gw)
    )


player_form = {}

player_history = {}


for index, player_id in enumerate(
    player_ownership
):

    data = fetch_json(
        f"{CLASSIC_BASE}/element-summary/{player_id}/"
    )

    if not data:
        continue

    history_data = data.get(
        "history",
        []
    )

    points_by_gw = {}
    minutes_by_gw = {}
    opponent_by_gw = {}
    was_home_by_gw = {}

    for row in history_data:

        round_number = row.get(
            "round"
        )

        if round_number is None:
            continue

        gw = int(
            round_number
        )

        pinned = get_pinned_player_gw_record(
            player_id,
            gw
        )

        if pinned is not None:

            points_by_gw[gw] = pinned["points"]
            minutes_by_gw[gw] = pinned["minutes"]
            opponent_by_gw[gw] = pinned["opponent"]
            was_home_by_gw[gw] = pinned["was_home"]

        else:

            points_by_gw[gw] = row.get(
                "total_points",
                0
            )

            minutes_by_gw[gw] = row.get(
                "minutes",
                0
            )

            opponent_team_id = row.get(
                "opponent_team"
            )

            opponent_by_gw[gw] = (
                teams_lookup.get(
                    opponent_team_id,
                    ""
                )
            )

            was_home_by_gw[gw] = row.get(
                "was_home",
                False
            )

        # Persist this gameweek's record so it's available to pin
        # against on future runs once it's finished. Harmless to
        # re-write while still in progress - it'll keep being
        # refreshed until finished_gws locks it in above.
        player_scores.setdefault(
            str(player_id),
            {}
        )[str(gw)] = {
            "points": points_by_gw[gw],
            "minutes": minutes_by_gw[gw],
            "opponent": opponent_by_gw[gw],
            "was_home": was_home_by_gw[gw],
        }

    player_form[player_id] = (
        points_by_gw
    )

    player_history[player_id] = {

        "points": points_by_gw,

        "minutes": minutes_by_gw,

        "opponents": opponent_by_gw,

        "was_home": was_home_by_gw

    }

    time.sleep(0.03)


print(
    "Player history loaded."
)


# Persist the newly-pinned player_scores back to disk. The scraper
# section above already wrote and saved history once before this
# section re-loaded it from disk, so this section's copy needs its
# own save now that player_scores has been populated - otherwise
# every pin computed here would be discarded at the end of the run.
with open(
    HISTORY_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        history,
        f,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# PLAYER FORM STATS
# ============================================================

player_form_stats = []


for player_id, info in (
    player_ownership.items()
):

    points = player_form.get(
        player_id,
        {}
    )

    last_5 = []
    last_10 = []

    if len(finished_gws) >= 5:

        last_5 = [
            points[gw]
            for gw in finished_gws[-5:]
            if gw in points
        ]

    if len(finished_gws) >= 10:

        last_10 = [
            points[gw]
            for gw in finished_gws[-10:]
            if gw in points
        ]

    avg_5 = (
        statistics.mean(last_5)
        if last_5
        else None
    )

    avg_10 = (
        statistics.mean(last_10)
        if last_10
        else None
    )

    trend = (
        avg_5 - avg_10
        if avg_5 is not None
        and avg_10 is not None
        else None
    )

    season_points = sum(
        points.get(
            gw,
            0
        )
        for gw in finished_gws
    )

    appearances = sum(
        1
        for gw in finished_gws
        if gw in points
    )

    player_form_stats.append({

        "id": player_id,

        "name": info["name"],

        "avg_5": avg_5,

        "avg_10": avg_10,

        "trend": trend,

        "owners": len(
            info["owners"]
        ),

        "transfers":
            player_transfer_counts[
                player_id
            ],

        "season_points":
            season_points,

        "appearances":
            appearances

    })


# ============================================================
# SORTED PLAYER LISTS
# ============================================================

top_players_by_season = sorted(
    player_form_stats,
    key=lambda x: (
        -x["season_points"],
        x["name"]
    )
)


top_players_by_5 = sorted(
    [
        p
        for p in player_form_stats
        if p["avg_5"] is not None
    ],
    key=lambda x: (
        -x["avg_5"],
        x["name"]
    )
)


top_players_by_10 = sorted(
    [
        p
        for p in player_form_stats
        if p["avg_10"] is not None
    ],
    key=lambda x: (
        -x["avg_10"],
        x["name"]
    )
)


top_form_trend = sorted(
    [
        p
        for p in player_form_stats
        if p["trend"] is not None
    ],
    key=lambda x: (
        -x["trend"],
        x["name"]
    )
)


most_transferred_players = sorted(
    player_form_stats,
    key=lambda x: (
        -x["transfers"],
        x["name"]
    )
)


most_owned_managers = sorted(
    player_form_stats,
    key=lambda x: (
        -x["owners"],
        x["name"]
    )
)


# ============================================================
# KEY PLAYER PER MANAGER
#
# For each manager, this is the highest season-points player who
# is on their CURRENT roster (as of the most recently captured
# gameweek) - not just anyone they've ever owned this season. A
# player who racked up points earlier but has since been dropped
# or traded away doesn't qualify.
# ============================================================

season_points_by_player = {
    p["id"]: p["season_points"]
    for p in player_form_stats
}

player_name_by_id = {
    p["id"]: p["name"]
    for p in player_form_stats
}

_all_captured_gws = sorted(
    int(gw)
    for gw in history.get("gameweeks", {}).keys()
)

most_recent_gw = (
    _all_captured_gws[-1]
    if _all_captured_gws
    else None
)

roster_by_manager_most_recent_gw = defaultdict(list)

if most_recent_gw is not None:

    for player_id, info in player_ownership.items():

        owners_now = info.get("ownership_by_gw", {}).get(
            most_recent_gw,
            set()
        )

        for manager in owners_now:

            roster_by_manager_most_recent_gw[
                manager
            ].append(player_id)

key_player_by_manager = {}

for manager, roster in (
    roster_by_manager_most_recent_gw.items()
):

    if not roster:
        continue

    best_player_id = max(
        roster,
        key=lambda pid: (
            season_points_by_player.get(pid, 0),
            player_name_by_id.get(pid, "")
        )
    )

    key_player_by_manager[manager] = {

        "name": player_name_by_id.get(
            best_player_id,
            "Unknown"
        ),

        "points": season_points_by_player.get(
            best_player_id,
            0
        ),

    }


# ============================================================
# TRANSFER HALL OF SHAME
# ============================================================

abandoned_assets = []


for player_id, info in (
    player_ownership.items()
):

    points = player_form.get(
        player_id,
        {}
    )

    ownership = info[
        "ownership_by_gw"
    ]

    for i in range(
        1,
        len(finished_gws)
    ):

        previous_gw = (
            finished_gws[i - 1]
        )

        current_gw = (
            finished_gws[i]
        )

        previous_owners = (
            ownership.get(
                previous_gw,
                set()
            )
        )

        current_owners = (
            ownership.get(
                current_gw,
                set()
            )
        )

        dropped = (
            previous_owners
            -
            current_owners
        )

        if not dropped:
            continue

        future_points = sum(
            points.get(
                gw,
                0
            )
            for gw in finished_gws
            if gw >= current_gw
        )

        for manager in dropped:

            abandoned_assets.append({

                "player":
                    info["name"],

                "manager":
                    manager,

                "dropped_gw":
                    previous_gw,

                "points_after":
                    future_points

            })


abandoned_assets.sort(
    key=lambda x: (
        -x["points_after"],
        x["player"]
    )
)


# ============================================================
# TRANSFER MARKET ROI
#
# Points gained: for every player, split each manager's ownership
# into separate stints across the captured gameweeks (a manager can
# drop a player and pick them up again later - those are separate
# stints). Any stint starting at GW1 is the original draft squad,
# not a pickup, so it's excluded. Every other stint - a new manager
# grabbing them off waivers, or the same manager re-acquiring them
# later - counts, crediting that manager with everything the player
# scored during the stint.
#
# Points given away: reuses the Hall of Shame numbers above, grouped
# per manager instead of listed per player. Same known
# simplification applies: a player dropped more than once by the
# same manager has "points after" counted per drop event, which can
# overlap and slightly over-penalise repeat droppers.
#
# Net ROI = points gained - points given away.
# ============================================================

manager_points_gained = defaultdict(int)

if finished_gws:

    draft_gw = finished_gws[0]

    for player_id, info in player_ownership.items():

        points = player_form.get(player_id, {})
        ownership = info.get("ownership_by_gw", {})

        for manager in info["owners"]:

            run_start = None

            for gw in finished_gws:

                owned_now = manager in ownership.get(gw, set())

                if owned_now and run_start is None:
                    run_start = gw

                if not owned_now and run_start is not None:

                    if run_start != draft_gw:
                        manager_points_gained[manager] += sum(
                            points.get(g, 0)
                            for g in finished_gws
                            if run_start <= g < gw
                        )

                    run_start = None

            # a stint still open at the end of the captured season
            if run_start is not None and run_start != draft_gw:
                manager_points_gained[manager] += sum(
                    points.get(g, 0)
                    for g in finished_gws
                    if g >= run_start
                )

manager_points_given_away = defaultdict(int)

for asset in abandoned_assets:
    manager_points_given_away[asset["manager"]] += asset["points_after"]

transfer_roi = sorted(
    (
        {
            "manager": manager,
            "points_gained": manager_points_gained.get(manager, 0),
            "points_given_away": manager_points_given_away.get(manager, 0),
            "net_roi": (
                manager_points_gained.get(manager, 0)
                - manager_points_given_away.get(manager, 0)
            ),
        }
        for manager in managers
    ),
    key=lambda x: (-x["net_roi"], x["manager"])
)


# ============================================================
# TRANSFER ACTIVITY ARCHIVE
#
# Ownership changes are effective at the START of the labelled GW.
# Therefore a player acquired for GW2 contributes their GW2 points to
# that manager.  This archive includes hand-offs between managers plus
# pure free-agent pickups/drops, while GW1 remains the initial draft.
# ============================================================

transfer_activity = []
historical_pickups = []

for player_id, info in player_ownership.items():
    ownership_by_gw = info.get("ownership_by_gw", {})
    player_name = info.get("name") or elements.get(player_id, {}).get("web_name", "Unknown")
    previous_owners = set()

    # Track each manager's post-draft stint so individual pickups can be
    # ranked by the points actually delivered while on that roster.
    open_stints = {}

    for i, gw in enumerate(finished_gws):
        current_owners = set(ownership_by_gw.get(gw, set()) or set())

        if i == 0:
            previous_owners = current_owners
            continue

        joined = sorted(current_owners - previous_owners)
        left = sorted(previous_owners - current_owners)

        # Close outgoing stints before opening incoming ones. Points from
        # the new GW belong to the incoming manager, not the old manager.
        for manager in left:
            stint = open_stints.pop(manager, None)
            if stint is not None:
                start_gw = stint["start_gw"]
                stint_points = sum(
                    int(player_form.get(player_id, {}).get(g, 0) or 0)
                    for g in finished_gws
                    if start_gw <= g < gw
                )
                historical_pickups.append({
                    "player": player_name,
                    "player_id": player_id,
                    "manager": manager,
                    "from_team": stint.get("from_team", "Free Agent"),
                    "start_gw": start_gw,
                    "end_gw": gw - 1,
                    "points": stint_points,
                    "weeks": len([g for g in finished_gws if start_gw <= g < gw]),
                })

        if joined or left:
            # There should normally be one owner in Draft, but retain list
            # handling so the archive remains robust if the snapshots are odd.
            from_label = ", ".join(left) if left else "Free Agent"
            to_label = ", ".join(joined) if joined else "Free Agent"

            if joined:
                for manager in joined:
                    transfer_activity.append({
                        "gw": gw,
                        "player": player_name,
                        "player_id": player_id,
                        "team": manager,
                        "action": "IN",
                        "from_team": from_label,
                        "to_team": manager,
                    })
                    open_stints[manager] = {
                        "start_gw": gw,
                        "from_team": from_label,
                    }

            if left:
                for manager in left:
                    transfer_activity.append({
                        "gw": gw,
                        "player": player_name,
                        "player_id": player_id,
                        "team": manager,
                        "action": "OUT",
                        "from_team": manager,
                        "to_team": to_label,
                    })

        previous_owners = current_owners

    # Score any acquired stint still open at the end of captured history.
    for manager, stint in open_stints.items():
        start_gw = stint["start_gw"]
        stint_points = sum(
            int(player_form.get(player_id, {}).get(g, 0) or 0)
            for g in finished_gws
            if g >= start_gw
        )
        historical_pickups.append({
            "player": player_name,
            "player_id": player_id,
            "manager": manager,
            "from_team": stint.get("from_team", "Free Agent"),
            "start_gw": start_gw,
            "end_gw": max(finished_gws) if finished_gws else start_gw,
            "points": stint_points,
            "weeks": len([g for g in finished_gws if g >= start_gw]),
        })

transfer_activity.sort(key=lambda x: (-int(x["gw"]), x["player"], x["action"]))
historical_pickups.sort(key=lambda x: (-x["points"], -x["weeks"], x["player"]))

latest_transfer_gw = dashboard_display_gw if dashboard_display_gw else None


def canonical_transfer_movements():
    """Collapse paired IN/OUT ownership changes into one human-readable move."""
    seen = set()
    moves = []

    for row in transfer_activity:
        gw = int(row.get("gw", 0) or 0)
        player = row.get("player", "Unknown")
        player_id = row.get("player_id")
        from_team = row.get("from_team") or "Free Agent"
        to_team = row.get("to_team") or "Free Agent"

        key = (gw, player_id, from_team, to_team)
        if key in seen:
            continue
        seen.add(key)

        if from_team == "Free Agent" and to_team != "Free Agent":
            move_label = "Pickup"
        elif to_team == "Free Agent" and from_team != "Free Agent":
            move_label = "Drop"
        elif from_team != to_team:
            move_label = "Transfer"
        else:
            move_label = row.get("action", "Move")

        moves.append({
            "gw": gw,
            "player": player,
            "player_id": player_id,
            "from_team": from_team,
            "to_team": to_team,
            "move": move_label,
        })

    moves.sort(key=lambda x: (-x["gw"], x["player"], x["from_team"], x["to_team"]))
    return moves


transfer_movements = canonical_transfer_movements()


def recent_transfer_activity_table():
    if latest_transfer_gw is None:
        return '<div class="notice">No gameweek transfer activity available yet.</div>'

    rows_data = [
        row.copy()
        for row in transfer_movements
        if int(row.get("gw", 0) or 0) == int(latest_transfer_gw)
    ]

    # During Upcoming/Live, frozen finished-GW ownership does not yet include
    # this gameweek. Merge in current element-status changes immediately.
    if (
        dashboard_game_state in ("upcoming", "live")
        and int(latest_transfer_gw) == int(dashboard_target_gw)
    ):
        seen = {
            (
                int(row.get("player_id", 0) or 0),
                row.get("from_team"),
                row.get("to_team"),
            )
            for row in rows_data
        }

        for change in dashboard_market_changes:
            key = (
                int(change.get("player_id", 0) or 0),
                change.get("from_team"),
                change.get("to_team"),
            )
            if key in seen:
                continue

            rows_data.append({
                "gw": dashboard_target_gw,
                **change,
            })
            seen.add(key)

    if not rows_data:
        return (
            f'<div class="notice">No processed ownership changes '
            f'for GW{latest_transfer_gw} yet.</div>'
        )

    move_order = {"Transfer": 0, "Pickup": 1, "Drop": 2}
    rows_data.sort(
        key=lambda row: (
            move_order.get(row.get("move"), 9),
            row.get("player", ""),
        )
    )

    rows = ""
    for row in rows_data:
        rows += f"""
            <tr>
                <td class="manager-name">{escape_html(row['player'])}</td>
                <td>{escape_html(row['from_team'])}</td>
                <td>{escape_html(row['to_team'])}</td>
                <td>{escape_html(row['move'])}</td>
            </tr>
        """

    return f"""
        <div class="table-wrap recent-transfers-scroll">
            <table>
                <thead><tr><th>Player</th><th>From</th><th>To</th><th>Move</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    """


def transfer_archive_table():
    if not transfer_movements:
        return '<div class="notice">No transfer activity captured yet.</div>'

    rows = ""
    for row in transfer_movements:
        search_team = f"{row['from_team']} {row['to_team']}".lower()
        rows += f"""
            <tr class="transfer-archive-row"
                data-player="{escape_html(row['player'].lower())}"
                data-team="{escape_html(search_team)}">
                <td>GW{row['gw']}</td>
                <td class="manager-name">{escape_html(row['player'])}</td>
                <td>{escape_html(row['from_team'])}</td>
                <td>{escape_html(row['to_team'])}</td>
                <td>{escape_html(row['move'])}</td>
            </tr>
        """

    return f"""
        <div class="table-wrap transfer-history-scroll">
            <table>
                <thead><tr><th>GW</th><th>Player</th><th>From</th><th>To</th><th>Move</th></tr></thead>
                <tbody id="transfer-archive-body">{rows}</tbody>
            </table>
        </div>
        <div id="transfer-search-empty" class="notice" style="display:none; margin-top:12px;">
            No transfers match those filters.
        </div>
    """


def best_historical_transfers_table(limit=15):
    candidates = [row for row in historical_pickups if row.get("weeks", 0) > 0]
    if not candidates:
        return '<div class="notice">Not enough completed transfer history yet.</div>'

    rows = ""
    for index, row in enumerate(candidates[:limit], start=1):
        span = f"GW{row['start_gw']}" if row['start_gw'] == row['end_gw'] else f"GW{row['start_gw']}–{row['end_gw']}"
        rows += f"""
            <tr>
                <td>{index}</td>
                <td class="manager-name">{escape_html(row['player'])}</td>
                <td>{escape_html(row['manager'])}</td>
                <td>{span}</td>
                <td>{row['weeks']}</td>
                <td class="positive">{row['points']}</td>
            </tr>
        """

    return f"""
        <div class="table-wrap">
            <table>
                <thead><tr><th>#</th><th>Player</th><th>Fantasy Team</th><th>Owned</th><th>GWs</th><th>Points Delivered</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    """


# ============================================================
# H2H STANDINGS
# ============================================================

league_points = defaultdict(
    float
)

points_for = defaultdict(
    float
)

points_against = defaultdict(
    float
)

matches_played = defaultdict(
    int
)

matches_won = defaultdict(
    int
)

matches_drawn = defaultdict(
    int
)

matches_lost = defaultdict(
    int
)

h2h_points_history = defaultdict(
    list
)

rank_history = defaultdict(
    list
)

raw_score_by_gw = defaultdict(
    list
)


for manager in managers:

    league_points[manager] = 0
    points_for[manager] = 0
    points_against[manager] = 0


# ============================================================
# MATCH DATA
# ============================================================

matches = history.get(
    "matches",
    []
)


matches_sorted = sorted(
    matches,
    key=lambda x: int(
        x.get(
            "event",
            0
        )
    )
)


# Process ALL gameweeks with matches (finished and current)
all_match_gws = sorted(set(int(m.get("event", 0)) for m in matches_sorted if m.get("event")))

for gw in all_match_gws:

    gw_matches = [
        m
        for m in matches_sorted
        if int(
            m.get(
                "event",
                0
            )
        ) == gw
    ]

    for match in gw_matches:

        n1 = match.get(
            "entry_1_name",
            "Unknown"
        )

        p1 = match.get(
            "entry_1_points",
            0
        )

        n2 = match.get(
            "entry_2_name",
            "Unknown"
        )

        p2 = match.get(
            "entry_2_points",
            0
        )

        try:
            p1 = int(p1 or 0)
        except Exception:
            p1 = 0

        try:
            p2 = int(p2 or 0)
        except Exception:
            p2 = 0

        if n1 not in managers:
            managers.append(n1)

        if n2 not in managers:
            managers.append(n2)

        raw_score_by_gw[n1].append(
            (gw, p1)
        )

        raw_score_by_gw[n2].append(
            (gw, p2)
        )

        points_for[n1] += p1
        points_for[n2] += p2

        points_against[n1] += p2
        points_against[n2] += p1

        matches_played[n1] += 1
        matches_played[n2] += 1

        if p1 > p2:

            league_points[n1] += 3

            matches_won[n1] += 1
            matches_lost[n2] += 1

        elif p2 > p1:

            league_points[n2] += 3

            matches_won[n2] += 1
            matches_lost[n1] += 1

        else:

            league_points[n1] += 1
            league_points[n2] += 1

            matches_drawn[n1] += 1
            matches_drawn[n2] += 1

    ranked = sorted(
        managers,
        key=lambda m: (
            -league_points[m],
            -points_for[m]
        )
    )

    for position, manager in enumerate(
        ranked,
        start=1
    ):

        rank_history[
            manager
        ].append(
            (gw, position)
        )

    for manager in managers:

        h2h_points_history[
            manager
        ].append(
            (
                gw,
                league_points[manager]
            )
        )


current_standings = sorted(
    managers,
    key=lambda m: (
        -league_points[m],
        -points_for[m]
    )
)

# Cumulative fantasy points scored by manager across captured match weeks.
# This is deliberately separate from H2H league points: it shows raw scoring
# output accumulating through the season, regardless of whether those points
# happened to produce a win, draw or loss.
cumulative_score_history = defaultdict(list)
for manager in managers:
    running_total = 0
    for gw, score in sorted(raw_score_by_gw.get(manager, []), key=lambda item: item[0]):
        running_total += int(score or 0)
        cumulative_score_history[manager].append((gw, running_total))


# ============================================================
# OFFICIAL SCORE LOOKUP (source of truth = history["matches"])
#
# Picks-derived totals (gw_points / live_points on each team
# snapshot) can drift from the official score if the picks the
# scraper captured for a gameweek are wrong or stale (e.g. a
# live/in-progress gameweek re-scraped after a roster change).
# history["matches"] is populated straight from the Draft API's
# head-to-head match records and is not affected by that, so it's
# used as the source of truth for any *score* display. It does not
# fix a wrong player showing up in a squad list.
# ============================================================

official_score_by_manager_gw = defaultdict(dict)

for gw in all_match_gws:

    gw_matches = [
        m for m in matches_sorted
        if int(m.get("event", 0)) == gw
    ]

    for match in gw_matches:

        n1 = match.get("entry_1_name", "Unknown")
        n2 = match.get("entry_2_name", "Unknown")

        try:
            p1 = int(match.get("entry_1_points", 0) or 0)
        except (TypeError, ValueError):
            p1 = 0

        try:
            p2 = int(match.get("entry_2_points", 0) or 0)
        except (TypeError, ValueError):
            p2 = 0

        official_score_by_manager_gw[n1][gw] = p1
        official_score_by_manager_gw[n2][gw] = p2


def official_gw_score(manager, gw):
    """
    Official head-to-head score for this manager/gw, straight from
    history["matches"]. Returns None only if no match record exists
    yet for that manager/gw (e.g. the fixture hasn't been captured),
    in which case callers fall back to the picks-derived estimate.
    """
    return official_score_by_manager_gw.get(manager, {}).get(int(gw))


# ============================================================
# PHASE 1 MANAGER ANALYTICS
# ============================================================

manager_current_rank = {
    manager: position
    for position, manager in enumerate(
        current_standings,
        start=1
    )
}


def manager_form(manager):

    results = []

    for match in matches_sorted:

        if int(match.get("event", 0)) not in finished_gws:
            continue

        n1 = match.get("entry_1_name", "")
        n2 = match.get("entry_2_name", "")

        if manager not in (n1, n2):
            continue

        try:
            p1 = int(match.get("entry_1_points", 0) or 0)
            p2 = int(match.get("entry_2_points", 0) or 0)
        except (TypeError, ValueError):
            continue

        if p1 == p2:
            results.append("D")
        elif (manager == n1 and p1 > p2) or (manager == n2 and p2 > p1):
            results.append("W")
        else:
            results.append("L")

    return results


manager_form_data = {
    manager: manager_form(manager)
    for manager in managers
}


def current_streak(manager):

    form = manager_form_data.get(manager, [])

    if not form:
        return "No matches"

    last = form[-1]
    count = 0

    for result in reversed(form):
        if result == last:
            count += 1
        else:
            break

    labels = {
        "W": "win",
        "D": "draw",
        "L": "loss"
    }

    return f"{count} {labels[last]}{'s' if count != 1 else ''}"


manager_transfer_in = defaultdict(int)
manager_transfer_out = defaultdict(int)

for player_id, details in player_transfer_details.items():

    for event in details:

        manager = event.get("manager", "Unknown")

        if event.get("type") == "IN":
            manager_transfer_in[manager] += 1
        elif event.get("type") == "OUT":
            manager_transfer_out[manager] += 1


# ============================================================
# PICKS-BASED DATA
# ============================================================

gw_scores = defaultdict(
    list
)

bench_scores = defaultdict(
    list
)

dreamteam_counts = defaultdict(
    list
)


for gw in gameweeks:

    gw_snapshot = history[
        "gameweeks"
    ][gw]
    
    is_finished = gw_snapshot.get(
        "finished",
        False
    )
    
    gw_data = gw_snapshot.get(
        "teams",
        {}
    )

    for entry_id, team_data in (
        gw_data.items()
    ):

        manager = team_data.get(
            "manager",
            "Unknown"
        )

        # Prefer the official match score; only estimate from picks
        # when no match record exists yet for this manager/gw.
        official_points = official_gw_score(manager, gw)
        if official_points is not None:
            points = official_points
        elif is_finished:
            points = team_data.get("gw_points", 0)
        else:
            points = team_data.get("live_points", team_data.get("gw_points", 0))

        gw_scores[
            manager
        ].append(
            (
                int(gw),
                points
            )
        )

        bench_scores[
            manager
        ].append(
            (
                int(gw),
                team_data.get(
                    "bench_points",
                    0
                )
            )
        )

        dreamteam_counts[
            manager
        ].append(
            (
                int(gw),
                team_data.get(
                    "dreamteam_starters",
                    0
                )
            )
        )


# ============================================================
# WEEKLY AWARDS
# ============================================================

weekly_awards = []


for gw in finished_gws:

    gw_data = history[
        "gameweeks"
    ][str(gw)].get(
        "teams",
        {}
    )

    if not gw_data:
        continue

    motw = max(
        gw_data.values(),
        key=lambda t:
            t.get(
                "gw_points",
                0
            )
    )

    stinker = min(
        gw_data.values(),
        key=lambda t:
            t.get(
                "gw_points",
                0
            )
    )

    best_bench = max(
        gw_data.values(),
        key=lambda t:
            t.get(
                "bench_points",
                0
            )
    )

    dt_king = max(
        gw_data.values(),
        key=lambda t:
            t.get(
                "dreamteam_starters",
                0
            )
    )

    weekly_awards.append({

        "gw": gw,

        "motw":
            motw.get(
                "manager",
                "Unknown"
            ),

        "motw_pts":
            motw.get(
                "gw_points",
                0
            ),

        "stinker":
            stinker.get(
                "manager",
                "Unknown"
            ),

        "stinker_pts":
            stinker.get(
                "gw_points",
                0
            ),

        "bench":
            best_bench.get(
                "manager",
                "Unknown"
            ),

        "bench_pts":
            best_bench.get(
                "bench_points",
                0
            ),

        "dt_king":
            dt_king.get(
                "manager",
                "Unknown"
            ),

        "dt_count":
            dt_king.get(
                "dreamteam_starters",
                0
            )

    })


# ============================================================
# FUN STATS
# ============================================================

consistency = {

    manager:
        (
            statistics.pstdev(
                [
                    points
                    for _, points
                    in gw_scores[manager]
                ]
            )
            if len(
                gw_scores[manager]
            ) > 1
            else 0
        )

    for manager in managers
}


most_consistent = (
    min(
        consistency,
        key=consistency.get
    )
    if consistency
    else None
)


avg_points = {

    manager:
        statistics.mean(
            [
                points
                for _, points
                in gw_scores[manager]
            ]
        )

    for manager in managers
    if gw_scores[manager]
}


total_dreamteam = {

    manager:
        sum(
            count
            for _, count
            in dreamteam_counts[
                manager
            ]
        )

    for manager in managers
}


total_bench_wasted = {

    manager:
        sum(
            points
            for _, points
            in bench_scores[
                manager
            ]
        )

    for manager in managers
}


top_bench_waster = (
    max(
        total_bench_wasted,
        key=total_bench_wasted.get
    )
    if total_bench_wasted
    else None
)


# ============================================================
# TEAM OF THE WEEK
# ============================================================

totw_by_gw = {}


# Team of the Week is allowed to use any legal formation:
#   1 goalkeeper
#   3-5 defenders
#   3-5 midfielders
#   1-3 forwards
# The formation is chosen independently for each gameweek by
# maximising the total points of the XI.

LEGAL_FORMATIONS = []

for defenders in range(3, 6):

    for midfielders in range(3, 6):

        for forwards in range(1, 4):

            if (
                defenders
                + midfielders
                + forwards
                == 10
            ):

                LEGAL_FORMATIONS.append({

                    "GKP": 1,

                    "DEF": defenders,

                    "MID": midfielders,

                    "FWD": forwards

                })


def choose_best_formation(by_pos):
    """
    Pick the legal formation producing the highest-scoring XI.

    A formation is only considered if enough players are available
    in every position. Ties are resolved in favour of the formation
    with more forwards, then more midfielders, which keeps the result
    deterministic while favouring attacking line-ups.
    """

    best = None

    for formation in LEGAL_FORMATIONS:

        selected = []
        possible = True

        for position, required in formation.items():

            candidates = by_pos.get(position, [])

            if len(candidates) < required:
                possible = False
                break

            selected.extend(
                candidates[:required]
            )

        if not possible:
            continue

        total_points = sum(
            int(player.get("points", 0) or 0)
            for player in selected
        )

        score = (
            total_points,
            formation["FWD"],
            formation["MID"]
        )

        if best is None or score > best["score"]:

            best = {
                "formation": formation,
                "players": selected,
                "total_points": total_points,
                "score": score
            }

    return best


# ============================================================
# OPTIMAL XI / SELECTION EFFICIENCY
# ============================================================

optimal_xi_by_manager_gw = {}

for gw in finished_gws:

    optimal_xi_by_manager_gw[gw] = {}

    gw_data = history["gameweeks"][str(gw)].get("teams", {})

    for team_data in gw_data.values():

        manager = team_data.get("manager", "Unknown")

        squad = (
            team_data.get("starters", [])
            + team_data.get("bench", [])
        )

        by_pos = defaultdict(list)

        for player in squad:
            by_pos[player.get("position", "")].append(player)

        for position in by_pos:
            by_pos[position].sort(
                key=lambda x: int(x.get("points", 0) or 0),
                reverse=True
            )

        best = choose_best_formation(by_pos)

        actual_starter_points = sum(
            int(player.get("points", 0) or 0)
            for player in team_data.get("starters", [])
        )

        if best:
            optimal_points = best["total_points"]
            efficiency = (
                actual_starter_points / optimal_points * 100
                if optimal_points > 0
                else 100
            )
        else:
            optimal_points = actual_starter_points
            efficiency = 100 if actual_starter_points else 0

        optimal_xi_by_manager_gw[gw][manager] = {
            "actual": actual_starter_points,
            "optimal": optimal_points,
            "missed": max(0, optimal_points - actual_starter_points),
            "efficiency": efficiency,
            "formation": (
                f"{best['formation']['DEF']}-{best['formation']['MID']}-{best['formation']['FWD']}"
                if best else "—"
            )
        }


manager_selection = {}

for manager in managers:

    records = [
        optimal_xi_by_manager_gw[gw][manager]
        for gw in finished_gws
        if manager in optimal_xi_by_manager_gw.get(gw, {})
    ]

    manager_selection[manager] = {
        "missed": sum(r["missed"] for r in records),
        "efficiency": (
            statistics.mean(r["efficiency"] for r in records)
            if records else 0
        ),
        "best_efficiency": (
            max(r["efficiency"] for r in records)
            if records else 0
        )
    }




# ============================================================
# MANAGER STYLE PROFILES
# ============================================================
# Behavioural tags derived from actual season activity. These are descriptive
# rather than quality grades: thresholds are centred on league averages so the
# profile describes HOW a manager plays, not whether they are objectively good.

_manager_completed_weeks = max(len(finished_gws), 1)

manager_move_counts = {manager: {"pickups": 0, "drops": 0, "trades_in": 0, "trades_out": 0} for manager in managers}

# Include current upcoming/live market activity as well as frozen history, while
# deduplicating any ownership change already captured in transfer_movements.
_activity_movements = [dict(row) for row in transfer_movements]
_activity_seen = {
    (int(row.get("gw", 0) or 0), int(row.get("player_id", 0) or 0), row.get("from_team"), row.get("to_team"))
    for row in _activity_movements
}
if dashboard_game_state in ("upcoming", "live"):
    for _change in dashboard_market_changes:
        _key = (int(dashboard_target_gw), int(_change.get("player_id", 0) or 0), _change.get("from_team"), _change.get("to_team"))
        if _key not in _activity_seen:
            _activity_movements.append({"gw": dashboard_target_gw, **_change})
            _activity_seen.add(_key)

for _move in _activity_movements:
    _kind = _move.get("move")
    _from = _move.get("from_team")
    _to = _move.get("to_team")
    if _kind == "Pickup" and _to in manager_move_counts:
        manager_move_counts[_to]["pickups"] += 1
    elif _kind == "Drop" and _from in manager_move_counts:
        manager_move_counts[_from]["drops"] += 1
    elif _kind == "Transfer":
        if _to in manager_move_counts:
            manager_move_counts[_to]["trades_in"] += 1
        if _from in manager_move_counts:
            manager_move_counts[_from]["trades_out"] += 1

# Transaction-aware activity. Ownership history records individual player legs,
# but managers think in completed roster moves. A 2-for-2 negotiated trade is
# two incoming moves for each manager (not four IN+OUT legs), while a same-GW
# free-agent drop + pickup is one waiver move.
manager_transaction_counts = {manager: 0 for manager in managers}
_manager_moves_by_gw = defaultdict(lambda: defaultdict(lambda: {"pickups": 0, "drops": 0, "trades_in": 0}))
for _move in _activity_movements:
    _gw = int(_move.get("gw", 0) or 0)
    _kind = _move.get("move")
    _from = _move.get("from_team")
    _to = _move.get("to_team")
    if _kind == "Pickup" and _to in manager_transaction_counts:
        _manager_moves_by_gw[_gw][_to]["pickups"] += 1
    elif _kind == "Drop" and _from in manager_transaction_counts:
        _manager_moves_by_gw[_gw][_from]["drops"] += 1
    elif _kind == "Transfer" and _to in manager_transaction_counts:
        _manager_moves_by_gw[_gw][_to]["trades_in"] += 1

for _gw, _by_manager in _manager_moves_by_gw.items():
    for _manager, _counts in _by_manager.items():
        _waiver_moves = max(_counts["pickups"], _counts["drops"])
        manager_transaction_counts[_manager] += _waiver_moves + _counts["trades_in"]

_manager_activity_per_gw = {
    manager: manager_transaction_counts.get(manager, 0) / _manager_completed_weeks
    for manager in managers
}
_manager_bench_per_gw = {
    manager: float(total_bench_wasted.get(manager, 0) or 0) / _manager_completed_weeks
    for manager in managers
}
_manager_efficiency = {
    manager: float(manager_selection.get(manager, {}).get("efficiency", 0) or 0)
    for manager in managers
}
_manager_consistency = {
    manager: float(consistency.get(manager, 0) or 0)
    for manager in managers
}
_manager_dreamteam_per_gw = {
    manager: float(total_dreamteam.get(manager, 0) or 0) / _manager_completed_weeks
    for manager in managers
}

def _mean_metric(values):
    vals = list(values.values())
    return statistics.mean(vals) if vals else 0.0

_style_avg_activity = _mean_metric(_manager_activity_per_gw)
_style_avg_bench = _mean_metric(_manager_bench_per_gw)
_style_avg_eff = _mean_metric(_manager_efficiency)
_style_avg_consistency = _mean_metric(_manager_consistency)
_style_avg_dreamteam = _mean_metric(_manager_dreamteam_per_gw)

def manager_style_profile(manager):
    activity = _manager_activity_per_gw.get(manager, 0.0)
    bench_pg = _manager_bench_per_gw.get(manager, 0.0)
    eff = _manager_efficiency.get(manager, 0.0)
    vol = _manager_consistency.get(manager, 0.0)
    dt_pg = _manager_dreamteam_per_gw.get(manager, 0.0)
    pickups = manager_move_counts.get(manager, {}).get("pickups", 0)
    trades = manager_move_counts.get(manager, {}).get("trades_in", 0)

    recent_scores = [float(points) for _, points in gw_scores.get(manager, [])][-3:]
    recent_avg = statistics.mean(recent_scores) if recent_scores else float(avg_points.get(manager, 0) or 0)
    season_avg = float(avg_points.get(manager, 0) or 0)

    candidates = []

    if activity >= max(0.65, _style_avg_activity * 1.30):
        candidates.append((3.0, "Waiver Hawk", "Makes roster changes aggressively and keeps working the market."))
    elif activity <= min(0.30, _style_avg_activity * 0.65 if _style_avg_activity else 0.30):
        candidates.append((2.4, "Patient Planner", "Prefers stability and gives players longer runs before changing course."))

    if trades >= max(2, pickups):
        candidates.append((2.7, "Deal Maker", "Uses manager-to-manager trades as a meaningful part of squad building."))

    if eff >= max(92.0, _style_avg_eff + 2.0):
        candidates.append((3.2, "XI Surgeon", "Consistently converts a high share of the squad's available points into the starting XI."))
    elif eff <= min(84.0, _style_avg_eff - 3.0):
        candidates.append((2.8, "Selection Gambler", "Leaves more points outside the optimal XI than most managers."))

    if bench_pg >= max(6.0, _style_avg_bench * 1.25):
        candidates.append((2.6, "Bench Gambler", "Carries productive depth but frequently leaves useful points on the bench."))
    elif bench_pg <= min(3.0, _style_avg_bench * 0.70 if _style_avg_bench else 3.0):
        candidates.append((2.1, "Lean Bench", "Gets relatively little scoring stranded among the substitutes."))

    if len(gw_scores.get(manager, [])) >= 3:
        if vol <= min(7.0, _style_avg_consistency * 0.80 if _style_avg_consistency else 7.0):
            candidates.append((2.5, "Steady Hand", "Weekly scoring has been relatively consistent with fewer wild swings."))
        elif vol >= max(11.0, _style_avg_consistency * 1.20):
            candidates.append((2.5, "Chaos Merchant", "High weekly variance: dangerous ceiling, but the floor can disappear without warning."))

    if len(recent_scores) >= 2 and recent_avg >= season_avg + 4.0:
        candidates.append((2.4, "On the Charge", "Recent scoring is running clearly above the season baseline."))
    elif len(recent_scores) >= 2 and recent_avg <= season_avg - 4.0:
        candidates.append((2.0, "Searching for Form", "Recent scoring has slipped below the team's season baseline."))

    if dt_pg >= max(0.8, _style_avg_dreamteam * 1.25):
        candidates.append((2.3, "Ceiling Chaser", "Regularly gets high-upside players into the XI when they hit."))

    # Extra personality tags — still derived from behaviour, just with a bit more pub-chat flavour.
    total_completed_moves = manager_transaction_counts.get(manager, 0)
    if pickups >= 4 and trades == 0:
        candidates.append((2.45, "Waiver Goblin", "Lives in the free-agent pool and would rather rummage through waivers than negotiate a trade."))
    if trades >= 3:
        candidates.append((2.55, "Transfer Diplomat", "Regularly gets deals over the line with other managers rather than relying only on waivers."))
    if total_completed_moves >= max(5, _manager_completed_weeks * 1.2):
        candidates.append((2.7, "Tinkerman", "Treats the squad sheet as a living document and rarely leaves the roster alone for long."))
    if total_completed_moves <= 1 and _manager_completed_weeks >= 3:
        candidates.append((2.35, "Diamond Hands", "Has barely touched the original plan and is prepared to hold through noise and bad weeks."))
    if eff >= 90 and bench_pg >= max(5.0, _style_avg_bench):
        candidates.append((2.45, "Luxury Problems", "Owns enough depth to strand points on the bench while still selecting efficiently."))
    if activity >= _style_avg_activity and vol >= max(10.0, _style_avg_consistency):
        candidates.append((2.4, "Mad Scientist", "High activity and volatile results: lots of experimentation, occasionally followed by smoke."))
    if recent_avg >= season_avg + 6.0 and total_completed_moves >= 2:
        candidates.append((2.5, "Hot Hand Merchant", "Recent moves and selections have coincided with a sharp scoring upswing."))
    if bench_pg >= max(8.0, _style_avg_bench * 1.35):
        candidates.append((2.55, "Bench Museum Curator", "Keeps an impressive collection of points safely preserved where they cannot affect the result."))

    if not candidates:
        candidates.append((1.0, "Balanced Operator", "No extreme behavioural tendency yet; activity, selection and volatility are close to league norms."))

    candidates.sort(key=lambda item: (-item[0], item[1]))
    chosen = candidates[:4]

    return {
        "tags": [{"name": name, "description": desc} for _, name, desc in chosen],
        "activity_per_gw": activity,
        "pickups": pickups,
        "trades": trades,
        "efficiency": eff,
        "bench_per_gw": bench_pg,
        "volatility": vol,
        "recent_avg": recent_avg,
    }


# ============================================================
# POWER RANKINGS
#
# A blended measure of underlying scoring strength, recent form, squad
# management and actual league position.  League position now matters,
# but it does not dominate the model, so a team can still rank above or
# below its table place when the underlying performances justify it.
#
#   Recent Form      (30%) - average of the last 5 gw_scores entries
#   Season Quality   (25%) - avg_points, the season-to-date average
#   Squad Management (15%) - average selection efficiency
#   League Position  (30%) - current H2H table rank (1st = strongest)
#
# Every component is mapped to 0-100 before weighting.

# ============================================================
# LUCK INDEX
# ============================================================
# Expected league points = average H2H return the manager's weekly score
# would have earned against every other manager that same completed GW.

expected_league_points = {manager: 0.0 for manager in managers}
actual_finished_league_points = {manager: 0.0 for manager in managers}
opponent_score_totals = {manager: [] for manager in managers}

for gw in finished_gws:
    gw_scores_map = {}
    for manager in managers:
        score = official_gw_score(manager, gw)
        if score is not None:
            gw_scores_map[manager] = float(score)

    if len(gw_scores_map) >= 2:
        for manager, score in gw_scores_map.items():
            virtual_points = []
            for opponent, opponent_score in gw_scores_map.items():
                if opponent == manager:
                    continue
                if score > opponent_score:
                    virtual_points.append(3.0)
                elif score == opponent_score:
                    virtual_points.append(1.0)
                else:
                    virtual_points.append(0.0)
            if virtual_points:
                expected_league_points[manager] += statistics.mean(virtual_points)

    gw_matches = [m for m in matches_sorted if int(m.get('event', 0) or 0) == int(gw)]
    for match in gw_matches:
        t1, t2 = match.get('entry_1_name'), match.get('entry_2_name')
        s1 = float(match.get('entry_1_points', 0) or 0)
        s2 = float(match.get('entry_2_points', 0) or 0)
        if t1 in opponent_score_totals:
            opponent_score_totals[t1].append(s2)
        if t2 in opponent_score_totals:
            opponent_score_totals[t2].append(s1)
        if t1 in actual_finished_league_points and t2 in actual_finished_league_points:
            if s1 > s2:
                actual_finished_league_points[t1] += 3
            elif s2 > s1:
                actual_finished_league_points[t2] += 3
            else:
                actual_finished_league_points[t1] += 1
                actual_finished_league_points[t2] += 1

luck_index = {
    manager: actual_finished_league_points.get(manager, 0.0) - expected_league_points.get(manager, 0.0)
    for manager in managers
}

opponent_avg_score = {
    manager: (statistics.mean(scores) if scores else 0.0)
    for manager, scores in opponent_score_totals.items()
}

# ============================================================

def _normalize_0_100(values):
    """Min-max normalise a {manager: value} dict to 0-100. If every
    manager has the same value, everyone scores 100 (nobody's
    differentiated on this axis yet)."""

    if not values:
        return {}

    lo = min(values.values())
    hi = max(values.values())

    if hi == lo:
        return {manager: 100.0 for manager in values}

    return {
        manager: (value - lo) / (hi - lo) * 100
        for manager, value in values.items()
    }


recent_form_points = {}

for manager in managers:
    recent = [points for _, points in gw_scores.get(manager, [])][-5:]
    recent_form_points[manager] = statistics.mean(recent) if recent else 0

season_quality_points = {
    manager: avg_points.get(manager, 0)
    for manager in managers
}

squad_management_points = {
    manager: manager_selection.get(manager, {}).get("efficiency", 0)
    for manager in managers
}

norm_recent_form = _normalize_0_100(recent_form_points)
norm_season_quality = _normalize_0_100(season_quality_points)
norm_squad_management = _normalize_0_100(squad_management_points)

# Convert league position directly to a 0-100 component.  With ten teams,
# 1st receives 100, 10th receives 0, and the positions between are evenly
# spaced. This deliberately uses table *position* rather than league points
# so the component reflects the user's requested standing in the league.
_manager_count = max(len(managers), 1)
if _manager_count == 1:
    norm_league_position = {manager: 100.0 for manager in managers}
else:
    norm_league_position = {
        manager: ((_manager_count - manager_current_rank.get(manager, _manager_count)) / (_manager_count - 1)) * 100
        for manager in managers
    }

power_score = {
    manager: (
        norm_recent_form.get(manager, 0) * 0.30
        + norm_season_quality.get(manager, 0) * 0.25
        + norm_squad_management.get(manager, 0) * 0.15
        + norm_league_position.get(manager, 0) * 0.30
    )
    for manager in managers
}

power_rankings = sorted(
    managers,
    key=lambda m: (-power_score[m], m)
)


def escape_html(value):

    value = str(value)

    replacements = {

        "&": "&amp;",

        "<": "&lt;",

        ">": "&gt;",

        '"': "&quot;",

        "'": "&#39;"

    }

    for old, new in replacements.items():

        value = value.replace(
            old,
            new
        )

    return value


def player_chip(player):

    star = (
        " ★"
        if player.get(
            "in_dreamteam",
            False
        )
        else ""
    )

    name = escape_html(
        player.get(
            "web_name",
            "Unknown"
        )
    )

    manager = escape_html(
        player.get(
            "manager",
            "Unknown"
        )
    )

    points = player.get(
        "points",
        0
    )

    return f"""
        <div class="chip">

            <div class="chip-name">
                {name}{star}
            </div>

            <div class="chip-sub">
                {manager} · {points} pts
            </div>

        </div>
    """


for gw in finished_gws:

    gw_data = history[
        "gameweeks"
    ][str(gw)].get(
        "teams",
        {}
    )

    pool = []

    for team_data in (
        gw_data.values()
    ):

        for player in team_data.get(
            "starters",
            []
        ):

            pool.append({

                **player,

                "manager":
                    team_data.get(
                        "manager",
                        "Unknown"
                    )

            })

    by_pos = defaultdict(
        list
    )

    for player in pool:

        by_pos[
            player.get(
                "position",
                ""
            )
        ].append(
            player
        )

    for position in by_pos:

        by_pos[position].sort(
            key=lambda x:
                -x.get(
                    "points",
                    0
                )
        )

    best_totw = choose_best_formation(
        by_pos
    )

    if best_totw is None:

        # This should only happen if the captured gameweek does not
        # contain enough starters to construct a legal XI.
        totw = []
        chosen_formation = {
            "GKP": 1,
            "DEF": 4,
            "MID": 4,
            "FWD": 2
        }
        total_totw_points = 0

    else:

        totw = best_totw["players"]
        chosen_formation = best_totw["formation"]
        total_totw_points = best_totw["total_points"]

    rows = {

        "GKP": [],

        "DEF": [],

        "MID": [],

        "FWD": []

    }

    for player in totw:

        position = player.get(
            "position",
            ""
        )

        if position in rows:

            rows[position].append(
                player
            )

    formation_label = (
        f"{chosen_formation['DEF']}-"
        f"{chosen_formation['MID']}-"
        f"{chosen_formation['FWD']}"
    )

    totw_by_gw[gw] = f"""
        <div class="totw-summary">
            Best XI · {formation_label} · {total_totw_points} pts
        </div>

        <div class="pitch">

            <div class="row">
                {''.join(
                    player_chip(p)
                    for p in rows["FWD"]
                )}
            </div>

            <div class="row">
                {''.join(
                    player_chip(p)
                    for p in rows["MID"]
                )}
            </div>

            <div class="row">
                {''.join(
                    player_chip(p)
                    for p in rows["DEF"]
                )}
            </div>

            <div class="row">
                {''.join(
                    player_chip(p)
                    for p in rows["GKP"]
                )}
            </div>

        </div>
    """


# ============================================================
# RESULTS
# ============================================================

results_by_gw = defaultdict(
    list
)


league_entry_id_to_name = (
    history.get(
        "league_entry_id_to_name",
        {}
    )
)


for match in matches:

    gw = match.get(
        "event"
    )

    if gw is None:
        continue

    try:

        gw = int(gw)

    except (
        TypeError,
        ValueError
    ):

        continue

    team1 = match.get(
        "entry_1_name"
    )

    team2 = match.get(
        "entry_2_name"
    )

    score1 = match.get(
        "entry_1_points"
    )

    score2 = match.get(
        "entry_2_points"
    )

    if team1 is None:

        entry1 = match.get(
            "league_entry_1"
        )

        team1 = (
            league_entry_id_to_name.get(
                str(entry1),
                league_entry_id_to_name.get(
                    entry1,
                    "Unknown"
                )
            )
        )

    if team2 is None:

        entry2 = match.get(
            "league_entry_2"
        )

        team2 = (
            league_entry_id_to_name.get(
                str(entry2),
                league_entry_id_to_name.get(
                    entry2,
                    "Unknown"
                )
            )
        )

    if score1 is None:

        score1 = match.get(
            "league_entry_1_points",
            0
        )

    if score2 is None:

        score2 = match.get(
            "league_entry_2_points",
            0
        )

    try:

        score1 = int(
            score1 or 0
        )

    except (
        TypeError,
        ValueError
    ):

        score1 = 0

    try:

        score2 = int(
            score2 or 0
        )

    except (
        TypeError,
        ValueError
    ):

        score2 = 0

    if score1 > score2:

        result = "win1"

    elif score2 > score1:

        result = "win2"

    else:

        result = "draw"

    results_by_gw[gw].append({

        "team1":
            team1 or "Unknown",

        "score1":
            score1,

        "team2":
            team2 or "Unknown",

        "score2":
            score2,

        "result":
            result

    })


result_gameweeks = sorted(
    results_by_gw.keys()
)


# ============================================================
# PLAYER SEARCH DATA
# ============================================================

player_search_data = []


for player_id, player_meta in elements.items():

    info = player_ownership.get(
        player_id,
        {
            "name": player_meta.get("web_name", "Unknown"),
            "owners": set(),
            "ownership_by_gw": {},
            "first_gw": None,
            "last_gw": None
        }
    )

    # Older/free-agent players may not appear in player_ownership.
    # Keep the structure consistent so later analytics can safely
    # read ownership_by_gw for every player.
    info.setdefault("owners", set())
    info.setdefault("ownership_by_gw", {})
    info.setdefault("first_gw", None)
    info.setdefault("last_gw", None)

    history_entry = {

        "id":
            player_id,

        "name":
            info["name"],

        "owners":
            sorted(
                list(
                    info["owners"]
                )
            ),

        "transfers":
            player_transfer_counts[
                player_id
            ],

        "position":
            positions_lookup.get(
                player_meta.get("element_type"),
                "—"
            ),

        "team":
            teams_lookup.get(
                player_meta.get("team"),
                "—"
            ),

        "fantasy_team":
            "Free Agent",

        "total_points":
            int(player_meta.get("total_points", 0) or 0),

        "form":
            float(player_meta.get("form", 0) or 0),

        "points_per_game":
            float(player_meta.get("points_per_game", 0) or 0),

        "goals":
            player_meta.get(
                "goals_scored",
                0
            ),

        "assists":
            player_meta.get(
                "assists",
                0
            ),

        "clean_sheets":
            player_meta.get(
                "clean_sheets",
                0
            ),

        "defensive_contributions":
            player_meta.get(
                "defensive_contribution",
                0
            ),

        "goals_conceded":
            player_meta.get(
                "goals_conceded",
                0
            ),

        "saves":
            player_meta.get(
                "saves",
                0
            ),

        "bonus":
            player_meta.get(
                "bonus",
                0
            ),

        "yellow_cards":
            player_meta.get(
                "yellow_cards",
                0
            ),

        "red_cards":
            player_meta.get(
                "red_cards",
                0
            ),

        "minutes":
            player_meta.get(
                "minutes",
                0
            ),

        "history":
            []

    }

    for gw in finished_gws:

        owners = sorted(
            list(
                info.get(
                    "ownership_by_gw",
                    {}
                ).get(
                    gw,
                    set()
                )
            )
        )

        points = player_form.get(
            player_id,
            {}
        ).get(
            gw,
            0
        )

        history_entry[
            "history"
        ].append({

            "gw":
                gw,

            "owners":
                owners,

            "points":
                points

        })

    player_search_data.append(
        history_entry
    )


player_search_json = json.dumps(
    player_search_data,
    ensure_ascii=False
)


# ============================================================
# MY TEAM — SQUAD SELECTED BY GAMEWEEK
#
# Unlike latest_team_data() (which only surfaces the most recent
# captured gameweek), this walks every captured gameweek so the
# "My Team" page can let a manager flip back through their squad
# week by week, not just see the latest one.
# ============================================================

def _my_team_history_for_manager(manager):

    all_captured_gws = sorted(
        int(gw) for gw in history.get("gameweeks", {}).keys()
    )

    entries = []

    for gw in all_captured_gws:

        gw_snapshot = history["gameweeks"][str(gw)]
        teams = gw_snapshot.get("teams", {})

        team_data = next(
            (
                t for t in teams.values()
                if t.get("manager") == manager
            ),
            None
        )

        if not team_data:
            continue

        official_points = official_gw_score(manager, gw)
        is_finished = gw_snapshot.get("finished", False)

        if official_points is not None:
            points = official_points
        elif is_finished:
            points = team_data.get("gw_points", 0)
        else:
            points = team_data.get(
                "live_points",
                team_data.get("gw_points", 0)
            )

        starters = sorted(
            team_data.get("starters", []),
            key=lambda p: int(p.get("points", 0) or 0),
            reverse=True
        )

        bench = sorted(
            team_data.get("bench", []),
            key=lambda p: int(p.get("points", 0) or 0),
            reverse=True
        )

        captain = next(
            (
                p.get("web_name")
                for p in team_data.get("starters", [])
                if p.get("is_captain")
            ),
            None
        )

        entries.append({
            "gw": gw,
            "points": points,
            "finished": is_finished,
            "captain": captain,
            "starters": [
                {
                    "name": p.get("web_name", "Unknown"),
                    "team": p.get("team", "—"),
                    "position": p.get("position", "—"),
                    "points": p.get("points", 0),
                    "is_captain": bool(p.get("is_captain")),
                    "is_vice_captain": bool(p.get("is_vice_captain")),
                }
                for p in starters
            ],
            "bench": [
                {
                    "name": p.get("web_name", "Unknown"),
                    "team": p.get("team", "—"),
                    "position": p.get("position", "—"),
                    "points": p.get("points", 0),
                }
                for p in bench
            ],
        })

    return entries


my_team_history_json = json.dumps(
    {
        manager: _my_team_history_for_manager(manager)
        for manager in current_standings
    },
    ensure_ascii=False
)


# ============================================================
# FREE AGENTS + MY TEAM H2H
# ============================================================

all_captured_gws = sorted(
    int(gw) for gw in history.get("gameweeks", {}).keys()
)

latest_captured_gw = all_captured_gws[-1] if all_captured_gws else None

POSITION_LABELS = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}

current_rosters_by_manager = defaultdict(dict)

if latest_captured_gw is not None:
    latest_snapshot = history["gameweeks"].get(str(latest_captured_gw), {})
    for team_data in latest_snapshot.get("teams", {}).values():
        manager = team_data.get("manager")
        if not manager:
            continue
        for player in team_data.get("starters", []) + team_data.get("bench", []):
            player_id = player.get("element_id")
            if player_id is not None:
                current_rosters_by_manager[manager][player_id] = player


def _player_current_metrics(player_id):
    meta = elements.get(player_id, {})
    return {
        "id": player_id,
        "name": meta.get("web_name", "Unknown"),
        "team": teams_lookup.get(meta.get("team"), "—"),
        "position": POSITION_LABELS.get(
            meta.get("element_type"),
            positions_lookup.get(meta.get("element_type"), "—")
        ),
        "position_id": meta.get("element_type"),
        "total_points": int(meta.get("total_points", 0) or 0),
        "form": float(meta.get("form", 0) or 0),
        "points_per_game": float(meta.get("points_per_game", 0) or 0),
        "minutes": int(meta.get("minutes", 0) or 0),
        "goals": int(meta.get("goals_scored", 0) or 0),
        "assists": int(meta.get("assists", 0) or 0),
        "clean_sheets": int(meta.get("clean_sheets", 0) or 0),
        "bonus": int(meta.get("bonus", 0) or 0),
        "status": meta.get("status", "a")
    }


def build_free_agent_recommendations(manager):
    roster = current_rosters_by_manager.get(manager, {})
    if not roster:
        return []

    owned_ids = set(roster.keys())

    # IMPORTANT: a player is a free agent only if nobody in the league owns them.
    # The old logic only excluded the selected manager's roster, which meant
    # players belonging to the other nine managers could be recommended.
    league_owned_ids = {
        player_id
        for player_id, owner in current_owner_by_player.items()
        if owner not in (None, "", 0, "0")
    }

    # Safe fallback if element-status is unavailable.
    if not current_owner_by_player:
        for other_roster in current_rosters_by_manager.values():
            league_owned_ids.update(int(pid) for pid in other_roster.keys())

    candidates = []

    for player_id, meta in elements.items():
        if player_id in owned_ids or player_id in league_owned_ids:
            continue
        if meta.get("status") not in (None, "", "a"):
            continue

        position_id = meta.get("element_type")
        if position_id not in (1, 2, 3, 4):
            continue

        candidate = _player_current_metrics(player_id)

        same_position = [
            _player_current_metrics(owned_id)
            for owned_id in owned_ids
            if elements.get(owned_id, {}).get("element_type") == position_id
        ]
        if not same_position:
            continue

        weakest = min(
            same_position,
            key=lambda p: (
                p["total_points"],
                p["form"],
                p["points_per_game"]
            )
        )

        season_edge = candidate["total_points"] - weakest["total_points"]
        form_edge = candidate["form"] - weakest["form"]

        if season_edge <= 0 and form_edge <= 0:
            continue

        recommendation_score = (
            season_edge * 3
            + form_edge * 10
            + (candidate["points_per_game"] - weakest["points_per_game"]) * 2
        )

        candidates.append({
            **candidate,
            "replace_name": weakest["name"],
            "replace_id": weakest["id"],
            "replace_total_points": weakest["total_points"],
            "replace_form": weakest["form"],
            "season_edge": season_edge,
            "form_edge": form_edge,
            "recommendation_score": recommendation_score
        })

    candidates.sort(
        key=lambda x: (
            -x["recommendation_score"],
            -x["total_points"],
            -x["form"],
            x["name"]
        )
    )

    position_counts = defaultdict(int)
    selected = []
    for candidate in candidates:
        pos = candidate["position"]
        if position_counts[pos] >= 2:
            continue
        position_counts[pos] += 1
        selected.append(candidate)

    return selected[:8]


free_agent_recommendations = {
    manager: build_free_agent_recommendations(manager)
    for manager in current_standings
}


def build_h2h_records():
    records = {
        manager: {
            opponent: {
                "played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "for": 0,
                "against": 0
            }
            for opponent in managers
            if opponent != manager
        }
        for manager in managers
    }

    for match in matches_sorted:
        team1 = match.get("entry_1_name")
        team2 = match.get("entry_2_name")
        if team1 not in records or team2 not in records:
            continue

        try:
            score1 = int(match.get("entry_1_points", 0) or 0)
            score2 = int(match.get("entry_2_points", 0) or 0)
        except (TypeError, ValueError):
            continue

        r1 = records[team1][team2]
        r2 = records[team2][team1]

        r1["played"] += 1
        r1["for"] += score1
        r1["against"] += score2
        r2["played"] += 1
        r2["for"] += score2
        r2["against"] += score1

        if score1 > score2:
            r1["wins"] += 1
            r2["losses"] += 1
        elif score2 > score1:
            r2["wins"] += 1
            r1["losses"] += 1
        else:
            r1["draws"] += 1
            r2["draws"] += 1

    return records


h2h_records = build_h2h_records()

free_agent_recommendations_json = json.dumps(
    free_agent_recommendations,
    ensure_ascii=False
)

h2h_records_json = json.dumps(
    h2h_records,
    ensure_ascii=False
)


# Attach the current Draft fantasy-team owner to every player in the
# directory. Players not owned by any manager remain "Free Agent".
current_fantasy_team_by_player = {}

for manager, roster in current_rosters_by_manager.items():
    for player_id in roster:
        current_fantasy_team_by_player[player_id] = manager

for player in player_search_data:
    player["fantasy_team"] = current_fantasy_team_by_player.get(
        player["id"],
        "Free Agent"
    )

player_search_json = json.dumps(
    player_search_data,
    ensure_ascii=False
)


# ============================================================
# TRADES FROM THE DRAFT API
# ============================================================

trades_endpoint = f"{DRAFT_BASE}/draft/league/{LEAGUE_ID}/trades"

print("Fetching league trades...")
trades_response = fetch_json(trades_endpoint)


def _trade_list_from_response(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("trades", "trade_list", "trade", "results", "data"):
            value = data.get(key)
            if isinstance(value, list):
                return value
            if isinstance(value, dict):
                nested = _trade_list_from_response(value)
                if nested:
                    return nested
    return []


trades_raw = _trade_list_from_response(trades_response)


def _trade_player_name(value):
    try:
        numeric_id = int(value)
    except (TypeError, ValueError):
        return str(value)
    return elements.get(numeric_id, {}).get("web_name", f"Player #{numeric_id}")


def _trade_manager_name(value):
    if value is None:
        return None
    try:
        numeric_id = int(value)
    except (TypeError, ValueError):
        return str(value)
    return (
        entry_id_to_name.get(numeric_id)
        or league_entry_id_to_name.get(numeric_id)
        or entry_id_to_name.get(str(numeric_id))
        or league_entry_id_to_name.get(str(numeric_id))
        or str(value)
    )


def _trade_date(value):
    if value in (None, ""):
        return "—"
    try:
        # Draft trade timestamps are ISO-8601 strings such as
        # 2026-08-26T13:23:39.420369Z.
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y, %H:%M")
    except (TypeError, ValueError):
        return str(value)


def _trade_status(value):
    status_map = {
        "p": "Processed",
    }
    raw = str(value or "").strip()
    return status_map.get(raw.lower(), raw or "Unknown")


def _normalise_all_trades(rows):
    """Normalise the actual FPL Draft /draft/league/{id}/trades schema.

    Each object in `trades` is already one complete trade:
      offered_entry  -> manager who offered the trade
      received_entry -> manager who received the offer
      tradeitem_set  -> element_out from offered manager, element_in from receiver
    """
    result = []

    for trade in rows:
        if not isinstance(trade, dict):
            continue

        offered_entry = trade.get("offered_entry")
        received_entry = trade.get("received_entry")

        offered_manager = _trade_manager_name(offered_entry) or f"Manager {offered_entry}"
        received_manager = _trade_manager_name(received_entry) or f"Manager {received_entry}"

        offered_players = []
        received_players = []

        for item in trade.get("tradeitem_set", []) or []:
            if not isinstance(item, dict):
                continue

            element_out = item.get("element_out")
            element_in = item.get("element_in")

            if element_out is not None:
                offered_players.append(_trade_player_name(element_out))
            if element_in is not None:
                received_players.append(_trade_player_name(element_in))

        # Prefer response_time for processed trades; fall back to offer_time.
        display_time = trade.get("response_time") or trade.get("offer_time")

        result.append({
            "id": trade.get("id", "—"),
            "gw": trade.get("event", "—"),
            "date": _trade_date(display_time),
            "status": _trade_status(trade.get("state")),
            "manager1": offered_manager,
            "manager2": received_manager,
            # manager1 gives element_out and receives element_in.
            "players1": offered_players,
            "players2": received_players,
            "player_ids1": [item.get("element_out") for item in (trade.get("tradeitem_set", []) or []) if isinstance(item, dict) and item.get("element_out") is not None],
            "player_ids2": [item.get("element_in") for item in (trade.get("tradeitem_set", []) or []) if isinstance(item, dict) and item.get("element_in") is not None],
        })

    return result


normalised_trades = _normalise_all_trades(trades_raw)


def _trade_points_after(player_ids, trade_gw):
    """Finished-GW points from the trade GW onward.

    Draft trades processed for GW2 are active for GW2, so the acquired
    players' GW2 points belong to the receiving manager.
    """
    try:
        start_gw = int(trade_gw)
    except (TypeError, ValueError):
        return 0

    total = 0
    for player_id in player_ids:
        try:
            pid = int(player_id)
        except (TypeError, ValueError):
            continue
        points = player_form.get(pid, {})
        for gw, value in points.items():
            try:
                gw_num = int(gw)
                pts = int(value or 0)
            except (TypeError, ValueError):
                continue
            if gw_num >= start_gw and gw_num in finished_gws:
                total += pts
    return total


def _trade_grade(trade):
    """Transparent running grade based on post-trade points."""
    side1_received = _trade_points_after(trade.get("player_ids2", []), trade.get("gw"))
    side2_received = _trade_points_after(trade.get("player_ids1", []), trade.get("gw"))
    try:
        weeks = len([gw for gw in finished_gws if gw >= int(trade.get("gw"))])
    except (TypeError, ValueError):
        weeks = 0

    diff = side1_received - side2_received
    if weeks == 0:
        verdict = "Too early to call"
        grade1 = grade2 = "—"
    elif abs(diff) <= max(3, weeks * 2):
        verdict = "Dead even"
        grade1 = grade2 = "B+"
    else:
        winner1 = diff > 0
        margin = abs(diff)
        if margin >= max(25, weeks * 8):
            winner_grade, loser_grade = "A+", "C"
        elif margin >= max(15, weeks * 5):
            winner_grade, loser_grade = "A", "C+"
        elif margin >= max(8, weeks * 3):
            winner_grade, loser_grade = "A-", "B-"
        else:
            winner_grade, loser_grade = "B+", "B"
        grade1, grade2 = (winner_grade, loser_grade) if winner1 else (loser_grade, winner_grade)
        leader = trade["manager1"] if winner1 else trade["manager2"]
        verdict = f"{leader} +{margin} pts"

    return {
        "manager1_points": side1_received,
        "manager2_points": side2_received,
        "grade1": grade1,
        "grade2": grade2,
        "verdict": verdict,
        "weeks": weeks,
    }


def _render_trade_cards(trades_to_show, filterable=False):
    if not trades_to_show:
        return """
            <div class="notice">
                No negotiated trades match this section yet.
            </div>
        """

    rows = ""
    for trade in trades_to_show:
        side1 = ", ".join(escape_html(p) for p in trade["players1"]) or "—"
        side2 = ", ".join(escape_html(p) for p in trade["players2"]) or "—"
        status = escape_html(trade["status"])
        status_class = (
            "trade-status-complete"
            if trade["status"].lower() in ("complete", "completed", "accepted", "processed")
            else "trade-status-other"
        )
        grade = _trade_grade(trade)
        try:
            grade_start_gw = int(trade["gw"])
        except (TypeError, ValueError):
            grade_start_gw = "—"

        trade_grade_html = f"""
            <div class="trade-grade">
                <div class="trade-grade-title">Running Trade Grade <span>· points from GW{grade_start_gw} onward</span></div>
                <div class="trade-grade-grid">
                    <div><strong>{escape_html(trade['manager1'])}</strong><b>{grade['grade1']}</b><span>{grade['manager1_points']} pts received</span></div>
                    <div class="trade-grade-verdict"><strong>{escape_html(grade['verdict'])}</strong><span>{grade['weeks']} completed GW{'s' if grade['weeks'] != 1 else ''} measured</span></div>
                    <div><strong>{escape_html(trade['manager2'])}</strong><b>{grade['grade2']}</b><span>{grade['manager2_points']} pts received</span></div>
                </div>
            </div>
        """

        filter_attrs = ""
        extra_class = ""
        if filterable:
            team_search = f"{trade['manager1']} {trade['manager2']}".lower()
            player_search = " ".join(trade.get("players1", []) + trade.get("players2", [])).lower()
            extra_class = " historical-trade-card"
            filter_attrs = (
                f' data-team="{escape_html(team_search)}"'
                f' data-player="{escape_html(player_search)}"'
            )

        rows += f"""
            <div class="trade-card{extra_class}"{filter_attrs}>
                <div class="trade-card-top">
                    <div>
                        <div class="trade-managers">
                            {escape_html(trade["manager1"])}
                            <span>↔</span>
                            {escape_html(trade["manager2"])}
                        </div>
                        <div class="trade-meta">
                            {escape_html(trade["date"])}
                            · GW{escape_html(trade["gw"])}
                            · Trade #{escape_html(trade["id"])}
                        </div>
                    </div>
                    <span class="trade-status {status_class}">{status}</span>
                </div>

                <div class="trade-exchange">
                    <div class="trade-side">
                        <div class="trade-side-label">
                            {escape_html(trade["manager1"])} receives
                        </div>
                        <div class="trade-players">{side2}</div>
                    </div>

                    <div class="trade-arrow">↔</div>

                    <div class="trade-side">
                        <div class="trade-side-label">
                            {escape_html(trade["manager2"])} receives
                        </div>
                        <div class="trade-players">{side1}</div>
                    </div>
                </div>

                {trade_grade_html}
            </div>
        """

    return f'<div class="trades-list">{rows}</div>'


def trades_table(gw=None):
    trades_to_show = normalised_trades
    if gw is not None:
        trades_to_show = [
            trade for trade in normalised_trades
            if str(trade.get("gw")) == str(gw)
        ]

    if not trades_to_show:
        gw_text = f" for GW{gw}" if gw is not None else ""
        return f'<div class="notice">No negotiated trades processed{gw_text} yet.</div>'

    return _render_trade_cards(trades_to_show)


def historical_trades_table():
    """All negotiated trades before the currently displayed transfer GW."""
    if latest_transfer_gw is None:
        historical = list(normalised_trades)
    else:
        historical = []
        for trade in normalised_trades:
            try:
                trade_gw = int(trade.get("gw"))
                current_gw = int(latest_transfer_gw)
            except (TypeError, ValueError):
                historical.append(trade)
                continue
            if trade_gw < current_gw:
                historical.append(trade)

    historical.sort(
        key=lambda trade: (
            -int(trade.get("gw", 0) or 0),
            str(trade.get("manager1", "")),
            str(trade.get("manager2", "")),
        )
    )

    if not historical:
        return '<div class="notice">No historical negotiated trades yet.</div>'

    cards = _render_trade_cards(historical, filterable=True)
    return (
        cards
        + '<div id="historical-trade-search-empty" class="notice" '
          'style="display:none; margin-top:12px;">No historical trades match that team.</div>'
    )



# ============================================================
# WAIVER TRANSACTIONS + TRADE SIMULATOR
# ============================================================

def _all_activity_movements_for_market_pages():
    rows = [dict(row) for row in transfer_movements]
    seen = {(int(row.get('gw', 0) or 0), int(row.get('player_id', 0) or 0), row.get('from_team'), row.get('to_team')) for row in rows}
    if dashboard_game_state in ('upcoming', 'live'):
        for change in dashboard_market_changes:
            key = (int(dashboard_target_gw), int(change.get('player_id', 0) or 0), change.get('from_team'), change.get('to_team'))
            if key not in seen:
                rows.append({'gw': dashboard_target_gw, **change}); seen.add(key)
    return rows


def waiver_transactions():
    grouped = defaultdict(lambda: {'in': [], 'out': []})
    for row in _all_activity_movements_for_market_pages():
        kind, old, new = row.get('move'), row.get('from_team'), row.get('to_team')
        if kind == 'Pickup' and new in managers:
            grouped[(int(row.get('gw', 0) or 0), new)]['in'].append(row.get('player', 'Unknown'))
        elif kind == 'Drop' and old in managers:
            grouped[(int(row.get('gw', 0) or 0), old)]['out'].append(row.get('player', 'Unknown'))
    result=[]
    for (gw,manager),legs in grouped.items():
        ins,outs=sorted(legs['in']),sorted(legs['out'])
        for idx in range(max(len(ins),len(outs))):
            result.append({'gw':gw,'manager':manager,'player_in':ins[idx] if idx<len(ins) else None,'player_out':outs[idx] if idx<len(outs) else None})
    result.sort(key=lambda row:(-row['gw'],row['manager'],row.get('player_in') or '',row.get('player_out') or ''))
    return result


def waiver_activity_table(current_only=False):
    rows=waiver_transactions()
    if current_only and latest_transfer_gw is not None:
        rows=[r for r in rows if int(r.get('gw',0))==int(latest_transfer_gw)]
    if not rows:
        return '<div class="notice">No waiver/free-agent transactions captured for this section yet.</div>'
    body=''
    for row in rows:
        incoming=escape_html(row.get('player_in') or '—'); outgoing=escape_html(row.get('player_out') or '—')
        body += f'''<tr class="waiver-row" data-team="{escape_html(row['manager'].lower())}"><td>GW{row['gw']}</td><td><b>{escape_html(row['manager'])}</b></td><td class="positive-text">{incoming}</td><td class="negative-text">{outgoing}</td><td>1</td></tr>'''
    empty='' if current_only else '<div id="waiver-search-empty" class="notice" style="display:none; margin-top:12px;">No waiver moves match that team.</div>'
    return f'''<div class="table-wrap transfer-history-scroll"><table><thead><tr><th>GW</th><th>Manager</th><th>In</th><th>Out</th><th>Moves</th></tr></thead><tbody>{body}</tbody></table></div>{empty}'''


def _trade_simulator_payload():
    form_lookup={int(row.get('id')):row for row in player_form_stats if row.get('id') is not None}
    original=history.get('original_draft_rank',{}); payload={}
    all_points=[float(elements.get(pid,{}).get('total_points',0) or 0) for roster in current_rosters_by_manager.values() for pid in roster]
    all_forms=[float(elements.get(pid,{}).get('form',0) or 0) for roster in current_rosters_by_manager.values() for pid in roster]
    max_points=max(all_points+[1.0]); max_form=max(all_forms+[1.0])
    for manager in managers:
        roster_ids=list(current_rosters_by_manager.get(manager,{}).keys())
        roster_total=sum(float(elements.get(pid,{}).get('total_points',0) or 0) for pid in roster_ids) or 1.0
        roster_proj=sum(float(_trade_player_projection(pid) or 0) for pid in roster_ids) or 1.0
        players=[]
        for pid in roster_ids:
            meta=elements.get(pid,{}); metrics=form_lookup.get(int(pid),{})
            pts=float(meta.get('total_points',0) or 0); form=float(meta.get('form',0) or 0); proj=float(_trade_player_projection(pid) or 0)
            rank=int((original.get(str(pid),{}) or {}).get('overall_pick',UNDRAFTED_PLAYER_RANK) or UNDRAFTED_PLAYER_RANK)
            draft_strength=max(0.0,min(1.0,(UNDRAFTED_PLAYER_RANK-rank)/max(UNDRAFTED_PLAYER_RANK-1,1)))
            importance=0.55*(pts/roster_total)+0.45*(proj/roster_proj)
            value=(0.29*(pts/max_points)+0.24*(form/max_form)+0.20*min(1.0,proj/8.0)+0.15*draft_strength+0.12*min(1.0,importance*8.0))*100.0
            players.append({'id':int(pid),'name':meta.get('web_name','Unknown'),'position':POSITION_LABELS.get(meta.get('element_type'),positions_lookup.get(meta.get('element_type'),'—')),'club':teams_lookup.get(meta.get('team'),'—'),'points':round(pts,1),'form':round(form,2),'projection':round(proj,2),'draft_rank':rank,'importance':round(importance*100.0,1),'value':round(value,1),'avg5':round(float(metrics.get('avg_5') or 0),2)})
        players.sort(key=lambda row:(-row['value'],row['position'],row['name'])); payload[manager]=players
    return payload


def trade_simulator_html():
    opts=''.join(f'<option value="{escape_html(m)}">{escape_html(m)}</option>' for m in managers)
    return f'''
    <div class="trade-simulator">
      <div class="trade-sim-head"><div><div class="eyebrow">TRADE LAB</div><h2>Simulate a Trade</h2></div><div class="trade-sim-score" id="trade-sim-score"><span>Fairness</span><b>—</b></div></div>
      <p class="card-description">Build any position-balanced deal. A 1-for-1 must be the same position; bundles may mix positions only when both sides give the same positional combination.</p>
      <div class="trade-sim-manager-row"><label>Manager A<select id="trade-sim-manager-a" onchange="renderTradeSimulator()"><option value="">Choose manager</option>{opts}</select></label><div class="trade-sim-versus">↔</div><label>Manager B<select id="trade-sim-manager-b" onchange="renderTradeSimulator()"><option value="">Choose manager</option>{opts}</select></label></div>
      <div class="trade-sim-grid"><div><h3 id="trade-sim-title-a">Manager A gives</h3><div id="trade-sim-roster-a" class="trade-sim-roster"><div class="notice">Choose two different managers.</div></div></div><div><h3 id="trade-sim-title-b">Manager B gives</h3><div id="trade-sim-roster-b" class="trade-sim-roster"><div class="notice">Choose two different managers.</div></div></div></div>
      <div id="trade-sim-result" class="trade-sim-result notice">Select managers and players to evaluate a deal.</div>
    </div>'''

# ============================================================
# CHART HELPER
# ============================================================

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

        rows += f"""
            <tr>
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
                <td>{norm_squad_management.get(manager, 0):.0f}</td>
                <td>{norm_league_position.get(manager, 0):.0f}</td>
                <td>{movement_html}</td>
            </tr>
        '''

    return f'''
        <div class="power-formula">
            <b>Power score:</b> 30% recent 5GW scoring + 25% season scoring quality + 15% squad-management efficiency + 30% current league position. Components are normalised to 0–100.
        </div>
        <div class="table-wrap">
            <table>
                <thead><tr><th>#</th><th>Manager</th><th>Power</th><th>5GW Form</th><th>Season</th><th>Management</th><th>Table</th><th>vs Table</th></tr></thead>
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
            <b>Luck Index:</b> actual league points minus the points your weekly scores would be expected to earn against a random league opponent. Positive = results ahead of performances; negative = the rough end of the fixtures.
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

def _build_mathematical_finish_ranges():
    remaining_games = {manager: 0 for manager in managers}
    completed_gws = set(int(gw) for gw in finished_gws)

    for gw, fixtures in full_fixture_schedule.items():
        if int(gw) in completed_gws:
            continue
        for fixture in fixtures:
            t1 = fixture.get("team1")
            t2 = fixture.get("team2")
            if t1 in remaining_games:
                remaining_games[t1] += 1
            if t2 in remaining_games:
                remaining_games[t2] += 1

    max_points = {
        manager: float(league_points.get(manager, 0)) + 3 * remaining_games.get(manager, 0)
        for manager in managers
    }
    min_points = {manager: float(league_points.get(manager, 0)) for manager in managers}

    ranges = {}
    total_teams = len(managers)
    for manager in managers:
        best = 1 + sum(
            1 for other in managers
            if other != manager and min_points[other] > max_points[manager]
        )
        worst = 1 + sum(
            1 for other in managers
            if other != manager and max_points[other] >= min_points[manager]
        )
        worst = min(total_teams, worst)
        ranges[manager] = {
            "best": best,
            "worst": worst,
            "text": f"{_ordinal_text(best)}–{_ordinal_text(worst)}",
            "remaining_games": remaining_games.get(manager, 0),
            "max_league_points": max_points[manager],
        }
    return ranges


# ============================================================
# REST-OF-SEASON PREDICTION MODEL
# ============================================================

def _prediction_percentile(values, pct):
    if not values:
        return None
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    idx = (len(values) - 1) * float(pct)
    lo = int(idx)
    hi = min(lo + 1, len(values) - 1)
    frac = idx - lo
    return values[lo] * (1 - frac) + values[hi] * frac


def _ordinal_suffix(n):
    n = int(n)
    if 10 <= n % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def _ordinal_text(n):
    n = int(n)
    return f"{n}{_ordinal_suffix(n)}"



# ============================================================
# CURRENT SQUAD STRENGTH / MANAGER XI ABILITY
# ============================================================
# Player expectation is intentionally conservative: recent output matters most,
# but it is blended with season output and a position-level baseline so one hot
# week does not turn a player into prime Ronaldo. Current ownership comes from
# Draft element-status, so waivers/trades change the forecast immediately.

def _current_roster_by_manager():
    rosters = {manager: [] for manager in managers}
    for player_id, owner in current_owner_by_player.items():
        manager = _dashboard_owner_name(owner)
        if manager in rosters:
            rosters[manager].append(int(player_id))
    return rosters


def _player_weekly_projection(player_id, position_baselines, league_player_mean):
    history_points = player_form.get(player_id, {}) or {}
    season_scores = [float(history_points.get(gw, 0) or 0) for gw in finished_gws]
    recent_gws = finished_gws[-5:]
    recent_scores = [float(history_points.get(gw, 0) or 0) for gw in recent_gws]

    # Fallback for a player who has only just entered Draft ownership and has
    # therefore never appeared in our ownership-driven player history.
    if season_scores:
        season_mean = statistics.mean(season_scores)
    else:
        total_points = float(elements.get(player_id, {}).get("total_points", 0) or 0)
        season_mean = total_points / max(len(finished_gws), 1)

    recent_mean = statistics.mean(recent_scores) if recent_scores else season_mean
    position = positions_lookup.get(elements.get(player_id, {}).get("element_type"), "")
    position_mean = position_baselines.get(position, league_player_mean)

    sample = len(finished_gws)

    # Evidence-only projection before applying the pre-season draft prior.
    # Early season still gets a little more positional regression because the
    # player's own sample is tiny.
    if sample < 5:
        evidence_projection = (0.45 * recent_mean) + (0.30 * season_mean) + (0.25 * position_mean)
    else:
        evidence_projection = (0.50 * recent_mean) + (0.35 * season_mean) + (0.15 * position_mean)

    draft_info = history.get("original_draft_rank", {}).get(str(player_id), {})
    overall_pick = draft_info.get("overall_pick", UNDRAFTED_PLAYER_RANK)

    # Every player gets a rank. Original draft picks retain 1-150; anybody not
    # selected in the original draft is explicitly rank 151.
    try:
        overall_pick = int(overall_pick)
    except (TypeError, ValueError):
        overall_pick = UNDRAFTED_PLAYER_RANK
    overall_pick = min(max(overall_pick, 1), UNDRAFTED_PLAYER_RANK)

    # Convert rank 1..151 to a curved 0-1 quality prior. Rank 151 maps exactly
    # to zero, while the curve preserves more separation among elite picks than
    # among late-round/undrafted players.
    draft_percentile = 1.0 - ((overall_pick - 1) / (UNDRAFTED_PLAYER_RANK - 1))
    draft_percentile = min(1.0, max(0.0, draft_percentile))
    draft_strength = draft_percentile ** 0.70

    # Put the rank prior onto the same weekly-points scale as the player
    # projection. Top picks anchor near ~2x their positional baseline; an
    # undrafted rank-151 player anchors near ~0.7x. It remains a prior only.
    draft_prior_projection = position_mean * (0.70 + (1.30 * draft_strength))

    # Decay rapidly as actual gameweeks accumulate: roughly 35% after GW1,
    # 24% after GW4, 12% after GW9 and ~4% after GW18. By the back half of
    # the season the player's real output has almost completely taken over.
    draft_prior_weight = 0.40 * math.exp(-sample / 8.0)
    draft_prior_weight = min(0.40, max(0.0, draft_prior_weight))

    projection = (
        ((1.0 - draft_prior_weight) * evidence_projection)
        + (draft_prior_weight * draft_prior_projection)
    )

    return max(0.0, projection)


def _best_projected_xi(projected_players):
    by_pos = defaultdict(list)
    for player in projected_players:
        by_pos[player["position"]].append(player)
    for pos in by_pos:
        by_pos[pos].sort(key=lambda p: p["projection"], reverse=True)

    best = None
    for formation in LEGAL_FORMATIONS:
        selected = []
        possible = True
        for pos, required in formation.items():
            candidates = by_pos.get(pos, [])
            if len(candidates) < required:
                possible = False
                break
            selected.extend(candidates[:required])
        if not possible:
            continue
        total = sum(p["projection"] for p in selected)
        if best is None or total > best["total"]:
            best = {"formation": formation, "players": selected, "total": total}
    return best


def _build_current_squad_strength():
    rosters = _current_roster_by_manager()

    # Positional baselines across the live player database. Use season PPG per
    # completed GW as a stable regression anchor.
    positional_values = defaultdict(list)
    all_player_values = []
    for pid, meta in elements.items():
        position = positions_lookup.get(meta.get("element_type"), "")
        val = float(meta.get("total_points", 0) or 0) / max(len(finished_gws), 1)
        positional_values[position].append(val)
        all_player_values.append(val)

    league_player_mean = statistics.mean(all_player_values) if all_player_values else 2.5
    position_baselines = {
        pos: statistics.mean(vals) if vals else league_player_mean
        for pos, vals in positional_values.items()
    }

    eff_values = [
        float(manager_selection.get(m, {}).get("efficiency", 0) or 0)
        for m in managers
        if manager_selection.get(m, {}).get("efficiency", 0)
    ]
    league_eff = statistics.mean(eff_values) if eff_values else 90.0

    strength = {}
    for manager in managers:
        projected_players = []
        for pid in rosters.get(manager, []):
            meta = elements.get(pid, {})
            pos = positions_lookup.get(meta.get("element_type"), "")
            draft_info = history.get("original_draft_rank", {}).get(str(pid), {})
            try:
                player_draft_rank = int(draft_info.get("overall_pick", UNDRAFTED_PLAYER_RANK))
            except (TypeError, ValueError):
                player_draft_rank = UNDRAFTED_PLAYER_RANK
            player_draft_rank = min(max(player_draft_rank, 1), UNDRAFTED_PLAYER_RANK)

            projected_players.append({
                "id": pid,
                "name": meta.get("web_name", f"Player {pid}"),
                "position": pos,
                "projection": _player_weekly_projection(pid, position_baselines, league_player_mean),
                "draft_rank": player_draft_rank,
            })

        best = _best_projected_xi(projected_players)
        if best:
            selected_ids = {p["id"] for p in best["players"]}
            optimal_xi = best["total"]
            bench_projections = sorted(
                [p["projection"] for p in projected_players if p["id"] not in selected_ids],
                reverse=True,
            )
            # Small resilience bonus only: depth should not outweigh the XI.
            depth_bonus = 0.05 * sum(bench_projections[:4])
            formation = f"{best['formation']['DEF']}-{best['formation']['MID']}-{best['formation']['FWD']}"
        else:
            optimal_xi = 0.0
            depth_bonus = 0.0
            formation = "—"

        raw_eff = float(manager_selection.get(manager, {}).get("efficiency", league_eff) or league_eff)
        # Shrink manager ability towards league average, especially useful early
        # in the season when only a handful of selection decisions exist.
        shrunk_eff = (0.70 * raw_eff) + (0.30 * league_eff)
        selection_factor = min(1.0, max(0.75, shrunk_eff / 100.0))
        managed_xi = (optimal_xi * selection_factor) + depth_bonus

        # Sum all current roster ranks as a transparent pedigree indicator.
        # Lower is better. Every undrafted player contributes exactly 151.
        squad_draft_rank_total = sum(
            int(p.get("draft_rank", UNDRAFTED_PLAYER_RANK))
            for p in projected_players
        )

        strength[manager] = {
            "optimal_xi": optimal_xi,
            "managed_xi": managed_xi,
            "selection_efficiency": shrunk_eff,
            "raw_selection_efficiency": raw_eff,
            "depth_bonus": depth_bonus,
            "formation": formation,
            "squad_size": len(projected_players),
            "players": projected_players,
            "squad_draft_rank_total": squad_draft_rank_total,
        }

    return strength


current_squad_strength = _build_current_squad_strength()

def _prediction_confidence_meta(completed_count=None, forecast_range_width=None):
    """Human-readable confidence for season/fixture forecasts.

    Confidence is deliberately conservative early in the season. It uses the
    amount of completed evidence first, then nudges down one level when a
    manager's simulated finish range is especially wide.
    """
    if completed_count is None:
        completed_count = len(finished_gws)
    completed_count = max(0, int(completed_count or 0))

    if completed_count <= 3:
        level, cls, score = "Very low", "very-low", 20
    elif completed_count <= 6:
        level, cls, score = "Low", "low", 35
    elif completed_count <= 10:
        level, cls, score = "Moderate", "moderate", 55
    elif completed_count <= 18:
        level, cls, score = "Good", "good", 75
    else:
        level, cls, score = "High", "high", 90

    if forecast_range_width is not None:
        try:
            width = float(forecast_range_width)
        except (TypeError, ValueError):
            width = None
        if width is not None and width >= max(5, len(managers) * 0.5):
            order = [("Very low", "very-low", 20), ("Low", "low", 35), ("Moderate", "moderate", 55), ("Good", "good", 75), ("High", "high", 90)]
            idx = next((i for i, row in enumerate(order) if row[0] == level), 0)
            level, cls, score = order[max(0, idx - 1)]

    return {"label": level, "class": cls, "score": score}


def _confidence_badge(meta):
    if not meta:
        return ''
    label = escape_html(meta.get("label", "Low"))
    cls = escape_html(meta.get("class", "low"))
    return f'<span class="confidence-badge confidence-{cls}">{label} confidence</span>'


def _build_season_prediction(simulations=7500, seed=17288):
    if not managers:
        return {}, []

    historical_scores = {
        manager: [int(score or 0) for _, score in sorted(raw_score_by_gw.get(manager, []))]
        for manager in managers
    }
    all_scores = [score for scores in historical_scores.values() for score in scores]
    league_mean = statistics.mean(all_scores) if all_scores else 45.0
    league_sd = statistics.pstdev(all_scores) if len(all_scores) >= 2 else 12.0
    league_sd = max(league_sd, 6.0)

    scoring_profile = {}
    for manager in managers:
        scores = historical_scores.get(manager, [])
        season_mean = statistics.mean(scores) if scores else league_mean

        # React quickly to what has happened lately. The last three completed
        # gameweeks are exponentially weighted, with the newest result carrying
        # twice the weight of the oldest. This deliberately makes the forecast
        # less sticky than a flat last-five average.
        recent = scores[-3:]
        if recent:
            recent_weights = [1.0, 1.5, 2.0][-len(recent):]
            recent_mean = sum(score * weight for score, weight in zip(recent, recent_weights)) / sum(recent_weights)
        else:
            recent_mean = season_mean

        team_sd = statistics.pstdev(scores) if len(scores) >= 2 else league_sd
        squad = current_squad_strength.get(manager, {})
        squad_score = float(squad.get("managed_xi", recent_mean) or recent_mean)

        # Build a responsive raw forecast, then heavily regress it towards the
        # league mean while the sample is tiny. Five GWs should move the needle,
        # not convince us anybody has already conquered the known universe.
        raw_expected = (
            (0.40 * squad_score)
            + (0.30 * recent_mean)
            + (0.15 * season_mean)
            + (0.15 * league_mean)
        )
        completed_count = len(scores)
        evidence_weight = min(1.0, max(0.0, completed_count / 10.0))
        # Keep a modest league-mean anchor early, but let genuine squad/form
        # strength separate teams sooner. Strong teams should look strong; the
        # model just should not become certain after a handful of GWs.
        expected = (
            ((0.55 + (0.40 * evidence_weight)) * raw_expected)
            + ((0.45 - (0.40 * evidence_weight)) * league_mean)
        )

        # Retain an early uncertainty premium, but not enough to wash out clear
        # differences in squad strength and scoring profile.
        early_uncertainty = 1.0 + (0.45 * max(0, 10 - completed_count) / 9.0)
        base_volatility = max((0.55 * team_sd) + (0.45 * league_sd), 7.0)
        volatility = base_volatility * early_uncertainty
        scoring_profile[manager] = {
            "expected_score": expected,
            "volatility": volatility,
            "squad_score": squad_score,
            "optimal_xi": float(squad.get("optimal_xi", squad_score) or squad_score),
            "selection_efficiency": float(squad.get("selection_efficiency", 100.0) or 100.0),
            "squad_draft_rank_total": int(squad.get("squad_draft_rank_total", UNDRAFTED_PLAYER_RANK * 15) or 0),
        }

    completed_gws = set(int(gw) for gw in finished_gws)
    remaining_fixtures = []
    for gw, fixtures in sorted(full_fixture_schedule.items()):
        if int(gw) in completed_gws:
            continue
        for fixture in fixtures:
            t1 = fixture.get("team1")
            t2 = fixture.get("team2")
            if t1 in managers and t2 in managers:
                remaining_fixtures.append((int(gw), t1, t2))

    finish_samples = {m: [] for m in managers}
    lp_samples = {m: [] for m in managers}
    pf_samples = {m: [] for m in managers}
    w_samples = {m: [] for m in managers}
    d_samples = {m: [] for m in managers}
    l_samples = {m: [] for m in managers}
    rng = random.Random(seed)

    for _ in range(simulations):
        sim_lp = {m: float(league_points.get(m, 0)) for m in managers}
        sim_pf = {m: float(points_for.get(m, 0)) for m in managers}
        sim_w = {m: int(matches_won.get(m, 0)) for m in managers}
        sim_d = {m: int(matches_drawn.get(m, 0)) for m in managers}
        sim_l = {m: int(matches_lost.get(m, 0)) for m in managers}
        week_shock = {}

        for gw, t1, t2 in remaining_fixtures:
            if gw not in week_shock:
                week_shock[gw] = rng.gauss(0, league_sd * 0.18)
            p1 = scoring_profile[t1]
            p2 = scoring_profile[t2]
            s1 = max(0, round(rng.gauss(p1["expected_score"] + week_shock[gw], p1["volatility"])))
            s2 = max(0, round(rng.gauss(p2["expected_score"] + week_shock[gw], p2["volatility"])))
            sim_pf[t1] += s1
            sim_pf[t2] += s2
            if s1 > s2:
                sim_lp[t1] += 3; sim_w[t1] += 1; sim_l[t2] += 1
            elif s2 > s1:
                sim_lp[t2] += 3; sim_w[t2] += 1; sim_l[t1] += 1
            else:
                sim_lp[t1] += 1; sim_lp[t2] += 1; sim_d[t1] += 1; sim_d[t2] += 1

        ranking = sorted(managers, key=lambda m: (-sim_lp[m], -sim_pf[m], m))
        positions = {m: i for i, m in enumerate(ranking, start=1)}
        for m in managers:
            finish_samples[m].append(positions[m])
            lp_samples[m].append(sim_lp[m]); pf_samples[m].append(sim_pf[m])
            w_samples[m].append(sim_w[m]); d_samples[m].append(sim_d[m]); l_samples[m].append(sim_l[m])

    prediction = {}
    for m in managers:
        finishes = finish_samples[m]
        counts = {pos: finishes.count(pos) for pos in range(1, len(managers) + 1)}
        median_finish = int(round(_prediction_percentile(finishes, 0.50)))
        p10 = max(1, int(round(_prediction_percentile(finishes, 0.10))))
        p90 = min(len(managers), int(round(_prediction_percentile(finishes, 0.90))))
        lo, hi = min(p10, p90), max(p10, p90)
        raw_position_pct = {pos: 100.0 * counts.get(pos, 0) / simulations for pos in range(1, len(managers) + 1)}

        # Calibrate early-season probabilities back towards an uninformative
        # league baseline. This stops raw Monte Carlo frequencies from looking
        # far more certain than five or six completed GWs justify. The model
        # earns the right to become decisive gradually through the season.
        completed_count = len(historical_scores.get(m, []))
        probability_evidence = min(1.0, max(0.0, completed_count / 10.0))
        uniform_pos = 100.0 / max(len(managers), 1)
        calibrated_position_pct = {
            pos: (probability_evidence * raw_position_pct[pos]) + ((1.0 - probability_evidence) * uniform_pos)
            for pos in range(1, len(managers) + 1)
        }
        champion_pct = calibrated_position_pct.get(1, 0.0)
        top3_pct = sum(calibrated_position_pct.get(pos, 0.0) for pos in range(1, min(3, len(managers)) + 1))
        bottom3_pct = sum(calibrated_position_pct.get(pos, 0.0) for pos in range(max(1, len(managers) - 2), len(managers) + 1))
        confidence = _prediction_confidence_meta(completed_count, hi - lo + 1)

        prediction[m] = {
            "median_finish": median_finish,
            "forecast_range_text": f"{_ordinal_text(lo)}–{_ordinal_text(hi)}",
            "position_pct": calibrated_position_pct,
            "raw_position_pct": raw_position_pct,
            "probability_evidence": probability_evidence,
            "confidence": confidence,
            "expected_league_points": statistics.mean(lp_samples[m]),
            "expected_points_for": statistics.mean(pf_samples[m]),
            "expected_wins": statistics.mean(w_samples[m]),
            "expected_draws": statistics.mean(d_samples[m]),
            "expected_losses": statistics.mean(l_samples[m]),
            "champion_pct": champion_pct,
            "top3_pct": top3_pct,
            "bottom3_pct": bottom3_pct,
            "model_weekly_score": scoring_profile[m]["expected_score"],
            "model_volatility": scoring_profile[m]["volatility"],
            "squad_score": scoring_profile[m]["squad_score"],
            "optimal_xi": scoring_profile[m]["optimal_xi"],
            "selection_efficiency": scoring_profile[m]["selection_efficiency"],
            "squad_draft_rank_total": scoring_profile[m]["squad_draft_rank_total"],
        }

    ordered = sorted(managers, key=lambda m: (prediction[m]["median_finish"], -prediction[m]["expected_league_points"], m))
    return prediction, ordered


season_prediction, predicted_finish_order = _build_season_prediction()
mathematical_finish_range = _build_mathematical_finish_ranges()




# ============================================================
# PROJECTED FIXTURE ODDS
# ============================================================
# Uses the same weekly score distributions as the season Monte Carlo model.
# These are pre-GW probabilities: completed results are never re-simulated.

def _fixture_odds_for_match(team1, team2, simulations=10000, seed=17288):
    p1 = season_prediction.get(team1, {})
    p2 = season_prediction.get(team2, {})
    if not p1 or not p2:
        return None

    mu1 = float(p1.get("model_weekly_score", 45.0) or 45.0)
    mu2 = float(p2.get("model_weekly_score", 45.0) or 45.0)
    sd1 = max(float(p1.get("model_volatility", 10.0) or 10.0), 4.0)
    sd2 = max(float(p2.get("model_volatility", 10.0) or 10.0), 4.0)

    stable = sum((i + 1) * ord(ch) for i, ch in enumerate(f"{team1}|{team2}"))
    rng = random.Random(int(seed) + stable)
    league_week_sd = statistics.mean([sd1, sd2]) * 0.18

    wins1 = draws = wins2 = 0
    score1_samples = []
    score2_samples = []
    for _ in range(simulations):
        shared = rng.gauss(0, league_week_sd)
        s1 = max(0, round(rng.gauss(mu1 + shared, sd1)))
        s2 = max(0, round(rng.gauss(mu2 + shared, sd2)))
        score1_samples.append(s1)
        score2_samples.append(s2)
        if s1 > s2:
            wins1 += 1
        elif s2 > s1:
            wins2 += 1
        else:
            draws += 1

    raw_team1_win = 100.0 * wins1 / simulations
    raw_draw = 100.0 * draws / simulations
    raw_team2_win = 100.0 * wins2 / simulations
    completed_count = len(finished_gws)
    evidence = min(1.0, max(0.0, (completed_count / 12.0) ** 1.20))
    # Fixture odds keep a draw-aware neutral prior. As evidence grows, the raw
    # simulated matchup frequencies increasingly take over.
    neutral_win, neutral_draw = 42.5, 15.0
    team1_win = (evidence * raw_team1_win) + ((1.0 - evidence) * neutral_win)
    draw_pct = (evidence * raw_draw) + ((1.0 - evidence) * neutral_draw)
    team2_win = (evidence * raw_team2_win) + ((1.0 - evidence) * neutral_win)
    total = max(team1_win + draw_pct + team2_win, 0.001)
    scale = 100.0 / total

    return {
        "team1_win": team1_win * scale,
        "draw": draw_pct * scale,
        "team2_win": team2_win * scale,
        "confidence": _prediction_confidence_meta(completed_count),
        "team1_mean": statistics.mean(score1_samples),
        "team2_mean": statistics.mean(score2_samples),
        "team1_low": _prediction_percentile(score1_samples, 0.10),
        "team1_high": _prediction_percentile(score1_samples, 0.90),
        "team2_low": _prediction_percentile(score2_samples, 0.10),
        "team2_high": _prediction_percentile(score2_samples, 0.90),
    }


def projected_fixture_odds_table():
    target_gw = int(fixture_prediction_gw or 0)
    fixtures = [
        f for f in full_fixture_schedule.get(target_gw, [])
        if f.get("team1") in managers and f.get("team2") in managers
    ]
    if not fixtures:
        return '<div class="notice">No upcoming fixtures available for projection.</div>'

    rows = ""
    for fixture in fixtures:
        t1 = fixture["team1"]
        t2 = fixture["team2"]
        odds = _fixture_odds_for_match(t1, t2)
        if not odds:
            continue
        rows += f'''
<tr>
<td class="manager-name">{escape_html(t1)}</td>
<td><b>{odds["team1_win"]:.1f}%</b></td>
<td>{odds["draw"]:.1f}%</td>
<td><b>{odds["team2_win"]:.1f}%</b></td>
<td class="manager-name">{escape_html(t2)}</td>
<td>{odds["team1_mean"]:.1f}–{odds["team2_mean"]:.1f}</td>
<td>{odds["team1_low"]:.0f}–{odds["team1_high"]:.0f} / {odds["team2_low"]:.0f}–{odds["team2_high"]:.0f}</td>
<td>{_confidence_badge(odds.get("confidence"))}</td>
</tr>'''

    return f'''
<div class="table-wrap"><table>
<thead><tr><th>Team</th><th>Win</th><th>Draw</th><th>Win</th><th>Team</th><th>Avg Score</th><th>80% Score Range</th><th>Confidence</th></tr></thead>
<tbody>{rows}</tbody></table></div>'''


# ============================================================
# LIVE FIXTURE WIN PROBABILITIES
# ============================================================
# Current Draft H2H scores are locked in. Only unresolved contribution from
# the selected XI is simulated. Premier League fixture status determines how
# much football each starter still has available this gameweek.

def _live_element_stats_lookup():
    out = {}
    for row in _dashboard_live_elements:
        if not isinstance(row, dict) or row.get("id") is None:
            continue
        stats = row.get("stats") or {}
        out[int(row["id"])] = {
            "points": float(stats.get("total_points", 0) or 0),
            "minutes": float(stats.get("minutes", 0) or 0),
        }
    return out


def _club_fixture_remaining_fraction(club_id):
    fixtures = [
        f for f in _dashboard_pl_fixtures
        if int(f.get("team_h", 0) or 0) == int(club_id or 0)
        or int(f.get("team_a", 0) or 0) == int(club_id or 0)
    ]
    if not fixtures:
        return 0.0, "unknown"

    fractions = []
    states = []
    for f in fixtures:
        if f.get("finished") or f.get("finished_provisional"):
            fractions.append(0.0)
            states.append("finished")
        elif f.get("started"):
            try:
                mins = float(f.get("minutes", 0) or 0)
            except (TypeError, ValueError):
                mins = 0.0
            fractions.append(max(0.0, min(1.0, (90.0 - mins) / 90.0)))
            states.append("live")
        else:
            fractions.append(1.0)
            states.append("upcoming")

    frac = sum(fractions) / max(len(fractions), 1)
    if any(state == "upcoming" for state in states):
        state = "upcoming"
    elif any(state == "live" for state in states):
        state = "live"
    else:
        state = "finished"
    return frac, state


def _live_manager_remaining_profile(manager):
    snapshot = history.get("gameweeks", {}).get(str(dashboard_target_gw), {})
    team_data = next(
        (td for td in snapshot.get("teams", {}).values() if td.get("manager") == manager),
        None,
    )
    if not team_data:
        return {"mean": 0.0, "sd": 1.5, "players_left": 0, "details": []}

    projection_by_id = {
        int(p.get("id")): float(p.get("projection", 0) or 0)
        for p in current_squad_strength.get(manager, {}).get("players", [])
        if p.get("id") is not None
    }
    live_stats = _live_element_stats_lookup()

    total_mean = 0.0
    variances = []
    details = []
    players_left = 0

    for player in team_data.get("starters", []):
        pid = player.get("element_id")
        if pid is None:
            continue
        pid = int(pid)
        meta = elements.get(pid, {})
        remaining_fraction, state = _club_fixture_remaining_fraction(meta.get("team"))
        if remaining_fraction <= 0:
            continue

        projection = projection_by_id.get(pid)
        if projection is None:
            projection = float(meta.get("total_points", 0) or 0) / max(len(finished_gws), 1)

        player_live = live_stats.get(pid, {"points": 0.0, "minutes": 0.0})
        live_minutes = float(player_live.get("minutes", 0) or 0)
        appearance_factor = 0.35 if state == "live" and live_minutes <= 0 else 1.0

        remaining_mean = max(0.0, projection * remaining_fraction * appearance_factor)
        if remaining_mean <= 0.05:
            continue

        player_sd = max(1.2, 1.15 * (remaining_mean ** 0.65))
        total_mean += remaining_mean
        variances.append(player_sd ** 2)
        players_left += 1
        details.append({
            "name": player.get("web_name") or meta.get("web_name", f"Player {pid}"),
            "state": state,
            "remaining_mean": remaining_mean,
        })

    base_team_sd = float(season_prediction.get(manager, {}).get("model_volatility", 9.0) or 9.0)
    model_weekly = max(float(season_prediction.get(manager, {}).get("model_weekly_score", 45.0) or 45.0), 1.0)
    unresolved_scale = min(1.0, total_mean / model_weekly)
    team_residual_var = (base_team_sd * 0.25 * unresolved_scale) ** 2
    total_sd = max(1.5, math.sqrt(sum(variances) + team_residual_var))

    return {"mean": total_mean, "sd": total_sd, "players_left": players_left, "details": details}


def _live_manager_current_score(manager):
    """Build the live team score directly from selected-XI player scores.

    This deliberately avoids the Draft matchup-level team score because that
    field can lag behind the player live endpoint. The freshest FPL live player
    totals are summed for the manager's selected XI.
    """
    snapshot = history.get("gameweeks", {}).get(str(dashboard_target_gw), {})
    team_data = next(
        (td for td in snapshot.get("teams", {}).values() if td.get("manager") == manager),
        None,
    )
    if not team_data:
        return 0

    live_stats = _live_element_stats_lookup()
    total = 0.0
    for player in team_data.get("starters", []):
        pid = player.get("element_id")
        if pid is None:
            continue
        try:
            pid = int(pid)
        except (TypeError, ValueError):
            continue

        # Prefer the live endpoint; fall back to the snapshot's player points
        # only if that player is unexpectedly absent from the live payload.
        live_row = live_stats.get(pid)
        if live_row is not None:
            pts = float(live_row.get("points", 0) or 0)
        else:
            pts = float(player.get("points", 0) or 0)

        multiplier = 2.0 if player.get("is_captain") else 1.0
        total += pts * multiplier

    return int(round(total))


def _live_fixture_odds_for_match(match, simulations=12000, seed=17288):
    e1 = match.get("league_entry_1")
    e2 = match.get("league_entry_2")
    t1 = league_entry_id_to_name.get(e1, league_entry_id_to_name.get(str(e1), "Unknown"))
    t2 = league_entry_id_to_name.get(e2, league_entry_id_to_name.get(str(e2), "Unknown"))

    # Current score comes from the live scoring of the selected XI, not the
    # sometimes-laggy Draft matchup aggregate.
    current1 = _live_manager_current_score(t1)
    current2 = _live_manager_current_score(t2)

    r1 = _live_manager_remaining_profile(t1)
    r2 = _live_manager_remaining_profile(t2)
    stable = sum((i + 1) * ord(ch) for i, ch in enumerate(f"LIVE|{dashboard_target_gw}|{t1}|{t2}"))
    rng = random.Random(int(seed) + stable + current1 * 31 + current2 * 37)

    wins1 = draws = wins2 = 0
    finals1, finals2 = [], []
    shared_sd = 0.10 * statistics.mean([r1["sd"], r2["sd"]])

    for _ in range(simulations):
        shared = rng.gauss(0, shared_sd)
        rem1 = max(0, round(rng.gauss(r1["mean"] + shared, r1["sd"])))
        rem2 = max(0, round(rng.gauss(r2["mean"] + shared, r2["sd"])))
        final1 = current1 + rem1
        final2 = current2 + rem2
        finals1.append(final1)
        finals2.append(final2)
        if final1 > final2:
            wins1 += 1
        elif final2 > final1:
            wins2 += 1
        else:
            draws += 1

    return {
        "team1": t1, "team2": t2,
        "current1": current1, "current2": current2,
        "team1_win": 100.0 * wins1 / simulations,
        "draw": 100.0 * draws / simulations,
        "team2_win": 100.0 * wins2 / simulations,
        "players_left1": r1["players_left"], "players_left2": r2["players_left"],
        "final1_mean": statistics.mean(finals1), "final2_mean": statistics.mean(finals2),
    }


def live_fixture_odds_table():
    if dashboard_game_state != "live":
        return ""
    matches = [
        m for m in (league_matches_all or [])
        if int(m.get("event", 0) or 0) == int(dashboard_target_gw)
    ]
    if not matches:
        return '<div class="notice">Live fixtures are not available yet.</div>'

    rows = ""
    for match in matches:
        odds = _live_fixture_odds_for_match(match)
        rows += f"""<tr>
<td class="manager-name">{escape_html(odds['team1'])}</td>
<td>{odds['current1']}</td>
<td>{odds['players_left1']}</td>
<td><b>{odds['team1_win']:.1f}%</b></td>
<td>{odds['draw']:.1f}%</td>
<td><b>{odds['team2_win']:.1f}%</b></td>
<td>{odds['players_left2']}</td>
<td>{odds['current2']}</td>
<td class="manager-name">{escape_html(odds['team2'])}</td>
<td>{odds['final1_mean']:.1f}–{odds['final2_mean']:.1f}</td>
</tr>"""

    return f"""<div class="table-wrap"><table>
<thead><tr><th>Team</th><th>Now</th><th>Left</th><th>Win</th><th>Draw</th><th>Win</th><th>Left</th><th>Now</th><th>Team</th><th>Projected Final</th></tr></thead>
<tbody>{rows}</tbody></table></div>"""


# ============================================================
# SQUAD PEDIGREE
# ============================================================
# Absolute star bands based on the average original draft rank of the CURRENT
# roster. Undrafted players are fixed at rank 151. Fixed thresholds mean the
# weakest team is not automatically forced to zero stars.

def _pedigree_stars_from_average_rank(avg_rank):
    bands = [
        (45, 5.0), (55, 4.5), (65, 4.0), (75, 3.5), (85, 3.0),
        (95, 2.5), (105, 2.0), (115, 1.5), (125, 1.0), (140, 0.5),
        (999, 0.0),
    ]
    for ceiling, stars in bands:
        if avg_rank <= ceiling:
            return stars
    return 0.0


def _star_text(stars):
    full = int(stars)
    half = abs(stars - full - 0.5) < 1e-9
    return ("★" * full) + ("½" if half else "") + ("☆" * max(0, 5 - full - (1 if half else 0)))


def _form_stars_from_3gw_average(avg_score):
    """Absolute recent-form scale; no manager is forced to 0★ just for ranking last."""
    if avg_score is None:
        return 2.5
    bands = [
        (25, 0.5), (30, 1.0), (35, 1.5), (40, 2.0), (45, 2.5),
        (50, 3.0), (55, 3.5), (60, 4.0), (65, 4.5), (999, 5.0),
    ]
    for ceiling, stars in bands:
        if avg_score < ceiling:
            return stars
    return 5.0


def _round_half_star(value):
    return min(5.0, max(0.0, round(float(value) * 2.0) / 2.0))


def squad_pedigree_table():
    rows_data = []
    for manager in managers:
        p = season_prediction.get(manager, {})
        players = current_squad_strength.get(manager, {}).get("players", [])
        total = int(p.get("squad_draft_rank_total", UNDRAFTED_PLAYER_RANK * 15) or UNDRAFTED_PLAYER_RANK * 15)
        roster_size = len(players) or 15
        avg_rank = total / roster_size

        draft_stars = _pedigree_stars_from_average_rank(avg_rank)
        recent_scores = [
            float(score or 0)
            for _, score in sorted(raw_score_by_gw.get(manager, []))[-3:]
        ]
        form_3gw = statistics.mean(recent_scores) if recent_scores else None
        form_stars = _form_stars_from_3gw_average(form_3gw)

        # Pedigree remains mostly about underlying roster pedigree, but current
        # form now has a meaningful 30% say. Round only the final blended score
        # so the displayed rating stays on the requested 0.5★ increments.
        stars = _round_half_star((0.70 * draft_stars) + (0.30 * form_stars))

        undrafted_count = sum(
            1 for player in players
            if int(player.get("draft_rank", UNDRAFTED_PLAYER_RANK) or UNDRAFTED_PLAYER_RANK) >= UNDRAFTED_PLAYER_RANK
        )
        top30 = sum(
            1 for player in players
            if int(player.get("draft_rank", UNDRAFTED_PLAYER_RANK) or UNDRAFTED_PLAYER_RANK) <= 30
        )
        rows_data.append((stars, total, manager, avg_rank, form_3gw, top30, undrafted_count))

    rows_data.sort(key=lambda row: (-row[0], row[1], row[2]))
    rows = ""
    for stars, total, manager, avg_rank, form_3gw, top30, undrafted_count in rows_data:
        form_text = f"{form_3gw:.1f}" if form_3gw is not None else "—"
        rows += f'''
<tr>
<td class="manager-name">{escape_html(manager)}</td>
<td><b>{_star_text(stars)}</b> <span class="muted">{stars:.1f}</span></td>
<td>{form_text}</td>
<td><b>{total}</b></td>
<td>{avg_rank:.1f}</td>
<td>{top30}</td>
<td>{undrafted_count}</td>
</tr>'''

    return f'''
<div class="table-wrap"><table>
<thead><tr><th>Manager</th><th>Pedigree</th><th>3GW Form</th><th>Draft Rank Total ↓</th><th>Avg Rank ↓</th><th>Top-30 Picks</th><th>Undrafted</th></tr></thead>
<tbody>{rows}</tbody></table></div>'''


def season_prediction_table():
    if not season_prediction:
        return '<div class="notice">Not enough data to build a season prediction yet.</div>'
    rows = ""
    for manager in predicted_finish_order:
        p = season_prediction[manager]
        rows += f'''
<tr>
<td class="rank-cell">{p["median_finish"]}</td>
<td class="manager-name">{escape_html(manager)}</td>
<td>{manager_current_rank.get(manager, "—")}</td>
<td><b>{p["expected_league_points"]:.1f}</b></td>
<td>{p["expected_wins"]:.1f}-{p["expected_draws"]:.1f}-{p["expected_losses"]:.1f}</td>
<td>{p["expected_points_for"]:.0f}</td>
<td>{p["squad_score"]:.1f}</td>
<td><b>{p["squad_draft_rank_total"]}</b></td>
<td>{p["selection_efficiency"]:.1f}%</td>
<td>{p["forecast_range_text"]}<br>{_confidence_badge(p.get("confidence"))}</td>
<td>{p["champion_pct"]:.1f}%</td>
<td>{p["top3_pct"]:.1f}%</td>
<td>{p["bottom3_pct"]:.1f}%</td>
</tr>'''
    return f'''
<div class="power-formula"><b>Model:</b> 7,500 Monte Carlo simulations using the real remaining H2H schedule. Current squad strength and recent form still drive the forecast, but early-season weekly expectations are deliberately regressed hard towards the league mean and score volatility is widened. Finishing probabilities are then <b>calibrated back towards the league baseline</b> until enough gameweeks have been played, so five good weeks cannot create fake certainty. The calibration now fades through roughly the first 10 completed GWs, so stronger teams separate earlier while early-season confidence remains restrained. Squad strength still uses the best legal projected XI, recent/season output and original McDraft rank as a decaying prior. <b>Confidence badges</b> describe how much evidence the forecast currently has; they are not another prediction. Forecast Range is the central 80% of simulated finishes and remains separate from mathematical Possible Finish.</div>
<div class="table-wrap"><table>
<thead><tr><th>Pred.</th><th>Manager</th><th>Now</th><th>Exp. League Pts</th><th>Exp. W-D-L</th><th>Exp. Pts For</th><th>Squad XI</th><th>Draft Rank Total ↓</th><th>Pick Eff.</th><th>Forecast Range</th><th>1st</th><th>Top 3</th><th>Bottom 3</th></tr></thead>
<tbody>{rows}</tbody></table></div>'''



def position_probability_table():
    if not season_prediction:
        return '<div class="notice">Not enough data to calculate finishing-position probabilities yet.</div>'

    header_positions = "".join(
        f"<th>{_ordinal_text(pos)}</th>"
        for pos in range(1, len(managers) + 1)
    )

    rows = ""
    for manager in current_standings:
        probs = season_prediction.get(manager, {}).get("position_pct", {})
        cells = "".join(
            f'<td><b>{probs.get(pos, 0.0):.1f}%</b></td>'
            for pos in range(1, len(managers) + 1)
        )
        rows += f'''
<tr>
<td class="manager-name">{escape_html(manager)}</td>
{cells}
</tr>'''

    return f'''
<div class="power-formula"><b>How to read it:</b> each row sums to roughly 100%. These are <b>calibrated</b> model probabilities from the same 7,500 schedule-aware simulations. Early in the season they are intentionally pulled towards an even 10-team baseline instead of presenting raw simulation frequencies as certainty. Unlike Possible Finish, this is probabilistic rather than purely mathematical.</div>
<div class="table-wrap"><table>
<thead><tr><th>Manager</th>{header_positions}</tr></thead>
<tbody>{rows}</tbody></table></div>'''


def _ordinal_suffix_unused_old(n):
    n = int(n)
    if 10 <= n % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def _standings_through_gw(gw):
    lp = defaultdict(float)
    pf = defaultdict(float)
    played = set()
    for match in matches_sorted:
        try:
            event = int(match.get("event", 0) or 0)
        except (TypeError, ValueError):
            continue
        if event > int(gw):
            continue
        t1 = match.get("entry_1_name", "Unknown")
        t2 = match.get("entry_2_name", "Unknown")
        s1 = int(match.get("entry_1_points", 0) or 0)
        s2 = int(match.get("entry_2_points", 0) or 0)
        played.update((t1, t2))
        pf[t1] += s1
        pf[t2] += s2
        if s1 > s2:
            lp[t1] += 3
        elif s2 > s1:
            lp[t2] += 3
        else:
            lp[t1] += 1
            lp[t2] += 1
    ranked = sorted(played or managers, key=lambda m: (-lp[m], -pf[m], m))
    return ranked, {m: i for i, m in enumerate(ranked, 1)}


def _manager_result_streak_through(manager, gw):
    seq = []
    for match in matches_sorted:
        event = int(match.get("event", 0) or 0)
        if event > int(gw):
            continue
        t1, t2 = match.get("entry_1_name"), match.get("entry_2_name")
        if manager not in (t1, t2):
            continue
        s1 = int(match.get("entry_1_points", 0) or 0)
        s2 = int(match.get("entry_2_points", 0) or 0)
        if s1 == s2:
            seq.append("D")
        elif (manager == t1 and s1 > s2) or (manager == t2 and s2 > s1):
            seq.append("W")
        else:
            seq.append("L")
    if not seq:
        return None, 0
    last = seq[-1]
    count = 0
    for result in reversed(seq):
        if result != last:
            break
        count += 1
    return last, count


def _luck_through_gw(gw):
    expected = defaultdict(float)
    actual = defaultdict(float)
    against = defaultdict(list)
    for event in [g for g in finished_gws if g <= int(gw)]:
        scores = {m: official_gw_score(m, event) for m in managers}
        scores = {m: float(v) for m, v in scores.items() if v is not None}
        if len(scores) >= 2:
            for manager, score in scores.items():
                virtual = []
                for opponent, other in scores.items():
                    if opponent == manager:
                        continue
                    virtual.append(3.0 if score > other else 1.0 if score == other else 0.0)
                if virtual:
                    expected[manager] += statistics.mean(virtual)
        for match in [m for m in matches_sorted if int(m.get("event", 0) or 0) == event]:
            t1, t2 = match.get("entry_1_name"), match.get("entry_2_name")
            s1 = float(match.get("entry_1_points", 0) or 0)
            s2 = float(match.get("entry_2_points", 0) or 0)
            against[t1].append(s2)
            against[t2].append(s1)
            if s1 > s2:
                actual[t1] += 3
            elif s2 > s1:
                actual[t2] += 3
            else:
                actual[t1] += 1
                actual[t2] += 1
    luck = {m: actual[m] - expected[m] for m in managers}
    opp_avg = {m: statistics.mean(against[m]) if against[m] else 0.0 for m in managers}
    return luck, opp_avg


def _free_agents_high_in_chart(gw, limit=3):
    owned = set()
    gw_data = history.get("gameweeks", {}).get(str(gw), {}).get("teams", {})
    for team in gw_data.values():
        for player in (team.get("starters", []) or []) + (team.get("bench", []) or []):
            pid = player.get("element_id")
            if pid is not None:
                try:
                    owned.add(int(pid))
                except (TypeError, ValueError):
                    pass
    ranked = []
    for pid, meta in elements.items():
        if int(pid) in owned:
            continue
        total = 0
        for event, pts in player_form.get(pid, {}).items():
            try:
                if int(event) <= int(gw):
                    total += int(pts or 0)
            except (TypeError, ValueError):
                pass
        if total > 0:
            ranked.append((meta.get("web_name", f"Player {pid}"), total))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked[:limit]


def _starter_stinker(gw):
    candidates = []
    gw_data = history.get("gameweeks", {}).get(str(gw), {}).get("teams", {})
    for team in gw_data.values():
        manager = team.get("manager", "Unknown")
        for player in team.get("starters", []) or []:
            try:
                pts = int(player.get("points", 0) or 0)
            except (TypeError, ValueError):
                pts = 0
            name = player.get("web_name") or elements.get(player.get("element_id"), {}).get("web_name", "Unknown")
            if pts <= 1:
                candidates.append((pts, name, manager))
    return min(candidates, key=lambda x: x[0]) if candidates else None


def _trade_story_for_gw(gw, rng):
    trades = [t for t in normalised_trades if str(t.get("gw")) == str(gw) and str(t.get("status", "")).lower() == "processed"]
    if not trades:
        return ""
    trade = trades[rng.randrange(len(trades))]
    a_gives = ", ".join(trade.get("players1", [])) or "nobody"
    b_gives = ", ".join(trade.get("players2", [])) or "nobody"
    intros = [
        f"The transfer fax machine was also smoking: {trade['manager1']} sent {a_gives} to {trade['manager2']} for {b_gives}.",
        f"In the week's boardroom drama, {trade['manager1']} shipped {a_gives} to {trade['manager2']} and took back {b_gives}.",
        f"There was movement in the McDraft bazaar too, with {trade['manager1']} exchanging {a_gives} for {trade['manager2']}'s {b_gives}.",
        f"While everyone else was staring at scores, {trade['manager1']} and {trade['manager2']} were doing business: {a_gives} went one way, {b_gives} the other.",
        f"A trade grenade landed in GW{gw}: {trade['manager1']} gave up {a_gives}, with {trade['manager2']} parting with {b_gives} in return.",
        f"The market had its own subplot as {trade['manager1']} and {trade['manager2']} swapped {a_gives} for {b_gives}.",
        f"Somebody found the trade button: {trade['manager1']} moved {a_gives} to {trade['manager2']} for {b_gives}.",
        f"The league's wheeler-dealers got involved, {trade['manager1']} sending {a_gives} across the aisle for {b_gives} from {trade['manager2']}.",
        f"Negotiations apparently survived contact with reality: {trade['manager1']} traded {a_gives} to {trade['manager2']} for {b_gives}.",
        f"There was a little transfer-market arson too: {trade['manager1']} exchanged {a_gives} with {trade['manager2']} for {b_gives}.",
    ]
    tails = [
        "A bold bit of business — time will tell who has read the market better.",
        "One for the trade ledger; this could look inspired or ridiculous in a few weeks' time.",
        "The paperwork is done, and now the league gets to judge it every Saturday.",
        "That one has all the ingredients to be revisited later in the season.",
        "Who could possibly regret that? We shall find out.",
        "Future historians may call it genius. They may also call it evidence.",
        "Either somebody has seen the future, or somebody has made an almighty mess. Excellent.",
        "The early verdict is unknowable; the group-chat verdict will of course be immediate and definitive.",
        "Bookmark it now. Somebody will pretend they always knew how this would end.",
        "This is either the start of a masterclass or a future screenshot with several laughing emojis.",
        "No pressure, but every point those players score from here is now legally admissible banter.",
        "The trade grade can wait; the accusations absolutely cannot.",
        "One manager will eventually call this visionary. The other may quietly stop mentioning it.",
        "There is no such thing as a harmless trade in a ten-team draft league.",
        "The spreadsheet has recorded it. The spreadsheet does not forget.",
        "It has the unmistakable smell of a deal that will age either like wine or warm milk.",
        "For now it is Schrödinger's trade: both a robbery and a disaster until the points arrive.",
        "A perfectly normal transaction that definitely will not be weaponised months from now.",
    ]
    return _gw_story_choice(rng, intros) + " " + _gw_story_choice(rng, tails)


def _next_week_preview(gw, positions, rng):
    next_gw = int(gw) + 1
    fixtures = full_fixture_schedule.get(next_gw, [])
    if not fixtures:
        return ""
    derby_fixtures = [(f, _derby_name(f["team1"], f["team2"])) for f in fixtures]
    derby_fixtures = [(f, d) for f, d in derby_fixtures if d]
    if derby_fixtures:
        fixture, derby = derby_fixtures[0]
        p1, p2 = positions.get(fixture["team1"]), positions.get(fixture["team2"])
        context = ""
        if p1 and p2:
            context = f", with {fixture['team1']} sitting {p1}{_ordinal_suffix(p1)} and {fixture['team2']} {p2}{_ordinal_suffix(p2)}"
        return _gw_story_choice(rng, [
            f"Next up in GW{next_gw}, circle {derby} in red: {fixture['team1']} face {fixture['team2']}{context}. Form can go out of the window for this one.",
            f"GW{next_gw} brings {derby}, as {fixture['team1']} and {fixture['team2']} renew hostilities{context}. Expect absolutely no perspective whatsoever if this is close.",
            f"And then comes {derby}: {fixture['team1']} versus {fixture['team2']} in GW{next_gw}{context}. Bragging rights are very much on the table.",
            f"Clear the diary for {derby} in GW{next_gw}: {fixture['team1']} meet {fixture['team2']}{context}, and civility has already been ruled out.",
            f"The fixture computer has chosen violence for GW{next_gw}: {derby} pits {fixture['team1']} against {fixture['team2']}{context}. Nobody involved will overreact, obviously.",
            f"Next week's main event is unmistakable — {derby}, {fixture['team1']} against {fixture['team2']}{context}. The points matter; the bragging rights matter far more.",
            f"GW{next_gw} serves up {derby}{context}. {fixture['team1']} and {fixture['team2']} can forget subtlety and prepare for a week of completely proportionate chat.",
            f"All roads now lead to {derby}: {fixture['team1']} versus {fixture['team2']} in GW{next_gw}{context}. Losing this one tends to have a longer half-life than three league points.",
            f"There is spice waiting in GW{next_gw}, where {derby} brings {fixture['team1']} and {fixture['team2']} together{context}. Screenshots are already being prepared.",
            f"Next week has one fixture with its collar turned up and fists already clenched: {derby}, {fixture['team1']} v {fixture['team2']}{context}.",
            f"GW{next_gw} is headlined by {derby}{context}. {fixture['team1']} face {fixture['team2']}, and the loser may wish to mute the group chat for 48 hours.",
            f"The next chapter is {derby}: {fixture['team1']} meet {fixture['team2']} in GW{next_gw}{context}. Sensible analysis can resume afterwards.",
        ])
    fixture = min(fixtures, key=lambda f: positions.get(f["team1"], 99) + positions.get(f["team2"], 99))
    p1, p2 = positions.get(fixture["team1"]), positions.get(fixture["team2"])
    context = ""
    if p1 and p2:
        context = f" — currently {p1}{_ordinal_suffix(p1)} versus {p2}{_ordinal_suffix(p2)}"
    return _gw_story_choice(rng, [
        f"Looking ahead to GW{next_gw}, {fixture['team1']} against {fixture['team2']} is the fixture to watch{context}; another result there could reshape the table.",
        f"The attention now turns to GW{next_gw}, where {fixture['team1']} meet {fixture['team2']}{context} in the pick of the next set of fixtures.",
        f"Next week's slate is headed by {fixture['team1']} versus {fixture['team2']}{context}; there are useful points and potentially terrible vibes on offer.",
        f"GW{next_gw} already has a pressure point: {fixture['team1']} take on {fixture['team2']}{context}, with neither side likely to fancy giving the other a free shove up the table.",
        f"The circus rolls into GW{next_gw} with {fixture['team1']} v {fixture['team2']}{context} looking especially tasty.",
        f"Eyes forward: {fixture['team1']} and {fixture['team2']} collide in GW{next_gw}{context}, a fixture with enough table consequence to make everyone pretend they are not checking live points every four minutes.",
        f"GW{next_gw} offers {fixture['team1']} against {fixture['team2']}{context}; one of those matches that could look very important indeed by Monday night.",
        f"Next on the conveyor belt of nonsense is {fixture['team1']} v {fixture['team2']} in GW{next_gw}{context}. Somebody is about to feel much cleverer than they really are.",
        f"The table gets another shake in GW{next_gw}, with {fixture['team1']} facing {fixture['team2']}{context}. No promises of dignity have been made.",
        f"Coming up: {fixture['team1']} against {fixture['team2']} in GW{next_gw}{context}. On paper, fascinating; in practice, probably decided by a defender's 93rd-minute yellow card.",
        f"GW{next_gw} beckons, and {fixture['team1']} v {fixture['team2']}{context} is the one with the biggest potential to rearrange both the standings and several moods.",
        f"Next week's spotlight falls on {fixture['team1']} and {fixture['team2']}{context}. If the fantasy gods are feeling theatrical, this is where they will strike.",
    ])


def league_storyline_for_gw(gw):
    """A dramatic editorial column, deliberately separate from the factual GW summary."""
    gw = int(gw)
    rng = random.Random((LEAGUE_ID * 100000) + gw * 7919)
    fixtures = results_by_gw.get(gw, [])
    if not fixtures:
        return f"GW{gw} has no completed fixture data to write up yet."

    ranked_now, pos_now = _standings_through_gw(gw)
    _, pos_prev = _standings_through_gw(gw - 1) if gw > 1 else ([], {})
    biggest = max(fixtures, key=lambda f: abs(f["score1"] - f["score2"]))
    if biggest["score1"] >= biggest["score2"]:
        bw, bl, bs, ls = biggest["team1"], biggest["team2"], biggest["score1"], biggest["score2"]
    else:
        bw, bl, bs, ls = biggest["team2"], biggest["team1"], biggest["score2"], biggest["score1"]
    margin = bs - ls
    leader = ranked_now[0] if ranked_now else bw

    new_leader_openers = [
        f"{leader} stormed to the top of McDraft in GW{gw}, seizing first place after the latest round of chaos.",
        f"There is a new name at the summit: {leader} surged into first after GW{gw} turned the table on its head.",
        f"GW{gw} has a new league leader, with {leader} muscling their way into top spot when the dust settled.",
        f"Sound the summit klaxon: {leader} are top of McDraft after GW{gw}, barging their way into first while everyone else checks the tie-break rules.",
        f"The throne changed hands in GW{gw}. {leader} now sit top of the pile, having emerged from the weekend's wreckage in first place.",
        f"A fresh flag is flying over McDraft HQ: {leader} climbed into first in GW{gw} and suddenly everybody below them has opinions about sustainability.",
        f"Top spot has a new tenant. {leader} grabbed the keys in GW{gw}, turning the latest round into their own small regime change.",
        f"McDraft has a new overlord for the week: {leader} jumped to first after GW{gw}, a sentence they will presumably be forwarding to everyone immediately.",
        f"The table did a cartwheel in GW{gw} and {leader} landed on top, taking over first place at precisely the right moment for maximum smugness.",
        f"GW{gw} ended with {leader} perched at the summit, having climbed into first and discovered the air is apparently much nicer up there.",
        f"Leadership changed hands in GW{gw}: {leader} are now setting the pace, and the chase pack has acquired a slightly more anxious look.",
        f"Move over, previous leader. {leader} took control of McDraft in GW{gw}, climbing to first after another weekend of entirely normal fantasy behaviour.",
    ]
    demolition_openers = [
        f"{bw} delivered the statement of GW{gw}, absolutely flattening {bl} {bs}-{ls} in a {margin}-point demolition.",
        f"GW{gw} belonged to {bw}, who handed {bl} a full-scale hiding, {bs}-{ls}.",
        f"Someone check on {bl}: {bw} ran riot in a brutal {bs}-{ls} win that provided GW{gw}'s loudest result.",
        f"{bw} arrived with a flamethrower and left {bl} as a small pile of waiver claims, winning {bs}-{ls}.",
        f"The mercy rule does not exist in McDraft, which was unfortunate for {bl}: {bw} vaporised them {bs}-{ls}.",
        f"{bw} committed an administrative error on {bl}, filing them under 'absolutely battered' after a {bs}-{ls} rout.",
        f"There are wins, there are comfortable wins, and then there is what {bw} did to {bl}: {bs}-{ls}, thank you and goodnight.",
        f"GW{gw}'s crime scene was {bw} {bs}, {bl} {ls}. Detectives have described the margin as 'unnecessary'.",
        f"{bl} may wish to report GW{gw} missing after {bw} bulldozed them {bs}-{ls} without so much as looking in the rear-view mirror.",
        f"{bw} put on steel-toe boots and treated {bl} like a cardboard box, stomping to a {bs}-{ls} win.",
        f"The week's loudest thud came from {bw}, who dropped a {bs}-{ls} piano on {bl}.",
        f"{bw} did not so much beat {bl} as redecorate the room with them, running out {bs}-{ls} winners.",
        f"A small weather event formed over McDraft in GW{gw}, centred directly above {bl}, where {bw} won {bs}-{ls}.",
        f"{bw} chose violence, subtlety and moderation were unavailable, and {bl} were swept aside {bs}-{ls}.",
        f"If {bl} felt a sudden chill, it was probably the shadow of {bw}'s {bs}-{ls} score passing overhead.",
        f"{bw} produced the sort of {bs}-{ls} walloping that makes a manager close the app and develop an interest in gardening.",
    ]
    general_openers = [
        f"GW{gw} shuffled the McDraft pack again, with {bw}'s {bs}-{ls} win over {bl} providing the headline result.",
        f"Another week, another dose of McDraft nonsense: {bw} emerged with a {bs}-{ls} victory over {bl} as the standings shifted around them.",
        f"GW{gw} refused to be quiet, led by {bw} seeing off {bl} {bs}-{ls} in the round's defining result.",
        f"The McDraft washing machine completed another spin in GW{gw}, and {bw}'s {bs}-{ls} win over {bl} came tumbling out on top.",
        f"GW{gw} served another tray of nonsense, with {bw} beating {bl} {bs}-{ls} and several managers immediately rewriting what they had said on Friday.",
        f"The league table received another vigorous shake in GW{gw}; {bw}'s {bs}-{ls} victory over {bl} was the result with the biggest fingerprints on it.",
        f"McDraft's weekly experiment in controlled chaos continued as {bw} beat {bl} {bs}-{ls} and the standings rearranged themselves yet again.",
        f"GW{gw} came in wearing muddy boots and knocked over the furniture, with {bw}'s {bs}-{ls} win against {bl} at the centre of the mess.",
        f"Another seven days, another outbreak of fantasy football nonsense: {bw} defeated {bl} {bs}-{ls} in GW{gw}'s headline act.",
        f"GW{gw} has been weighed, measured and found deeply unserious; {bw}'s {bs}-{ls} victory over {bl} leads the evidence.",
        f"The latest McDraft chapter opened with calculators and ended with accusations, as {bw} beat {bl} {bs}-{ls}.",
        f"GW{gw} tossed the form book down the stairs and watched what happened. At the bottom of the pile: {bw} {bs}, {bl} {ls}.",
        f"The fantasy gods rattled their little tin again in GW{gw}, and {bw} came out smiling after a {bs}-{ls} win over {bl}.",
        f"McDraft completed another completely sensible weekend, headlined by {bw} taking down {bl} {bs}-{ls}.",
        f"GW{gw} arrived, caused several preventable arguments, and left {bw} celebrating a {bs}-{ls} victory over {bl}.",
    ]

    if pos_prev.get(leader) and pos_prev.get(leader) != 1:
        opening = _gw_story_choice(rng, new_leader_openers)
    elif margin >= 20:
        opening = _gw_story_choice(rng, demolition_openers)
    else:
        opening = _gw_story_choice(rng, general_openers)

    beats = []
    derby_games = [(f, _derby_name(f["team1"], f["team2"])) for f in fixtures]
    derby_games = [(f, derby) for f, derby in derby_games if derby]
    if derby_games:
        fixture, derby = derby_games[0]
        if fixture["score1"] == fixture["score2"]:
            beats.append(_gw_story_choice(rng, [
                f"And {derby} somehow ended with the bragging rights vacuum-packed: {fixture['team1']} and {fixture['team2']} drew {fixture['score1']}-{fixture['score2']}.",
                f"{derby} produced maximum tension and minimum closure, {fixture['team1']} and {fixture['team2']} finishing dead level at {fixture['score1']}-{fixture['score2']}.",
                f"Nobody gets to be unbearable after {derby}: {fixture['team1']} and {fixture['team2']} cancelled each other out {fixture['score1']}-{fixture['score2']}.",
                f"{derby} ended in a diplomatic incident rather than a victory, with {fixture['team1']} and {fixture['team2']} locked at {fixture['score1']}-{fixture['score2']}.",
                f"The sacred texts of {derby} will record a draw: {fixture['team1']} {fixture['score1']}, {fixture['team2']} {fixture['score2']}. Nobody happy, everybody loud.",
                f"{derby} refused to choose a side, leaving {fixture['team1']} and {fixture['team2']} stranded together on {fixture['score1']}-{fixture['score2']}.",
            ]))
        else:
            winner = fixture["team1"] if fixture["score1"] > fixture["score2"] else fixture["team2"]
            loser = fixture["team2"] if winner == fixture["team1"] else fixture["team1"]
            ws, loser_score = max(fixture["score1"], fixture["score2"]), min(fixture["score1"], fixture["score2"])
            beats.append(_gw_story_choice(rng, [
                f"Most importantly, {derby} went to {winner}, who claimed the bragging rights over {loser} {ws}-{loser_score}.",
                f"There will be no peace after {derby}: {winner} took it {ws}-{loser_score} against {loser} and can dine out on that until the rematch.",
                f"{derby} supplied its usual dignity and restraint, with {winner} beating {loser} {ws}-{loser_score} to own the bragging rights for now.",
                f"{winner} now hold the ceremonial keys to {derby} after seeing off {loser} {ws}-{loser_score}; expect this result to be mentioned far beyond its natural lifespan.",
                f"The latest edition of {derby} belongs to {winner}, {ws}-{loser_score} winners over {loser}. The bragging-rights department is now operating at full capacity.",
                f"{derby} ended with {winner} on top and {loser} staring at a {ws}-{loser_score} receipt they will be shown repeatedly until further notice.",
                f"There was blood on the carpet in {derby}, metaphorically speaking: {winner} beat {loser} {ws}-{loser_score} and secured the only currency that matters, bragging rights.",
                f"{winner} took {derby} {ws}-{loser_score} over {loser}, a result worth three points in the table and approximately nine months of unnecessary references.",
                f"{derby} has a temporary landlord and it is {winner}, who beat {loser} {ws}-{loser_score} and will absolutely behave normally about it.",
                f"In the ancient and deeply serious matter of {derby}, {winner} defeated {loser} {ws}-{loser_score}. Historians are already being insufferable.",
            ]))

    moves = []
    for manager, position in pos_now.items():
        if manager in pos_prev and pos_prev[manager] != position:
            moves.append((pos_prev[manager] - position, manager, pos_prev[manager], position))
    if moves:
        climber = max(moves)
        faller = min(moves)
        if climber[0] > 0:
            beats.append(_gw_story_choice(rng, [
                f"{climber[1]} were the week's big climbers, jumping from {climber[2]}{_ordinal_suffix(climber[2])} to {climber[3]}{_ordinal_suffix(climber[3])}.",
                f"The lift was working for {climber[1]}, who shot from {climber[2]}{_ordinal_suffix(climber[2])} to {climber[3]}{_ordinal_suffix(climber[3])} in one weekend.",
                f"{climber[1]} made the table look temporary, vaulting from {climber[2]}{_ordinal_suffix(climber[2])} to {climber[3]}{_ordinal_suffix(climber[3])}.",
                f"Nobody climbed faster than {climber[1]}, up from {climber[2]}{_ordinal_suffix(climber[2])} to {climber[3]}{_ordinal_suffix(climber[3])} and suddenly looking much taller.",
                f"{climber[1]} found the express lane, leaping {climber[0]} place{'s' if climber[0] != 1 else ''} to {climber[3]}{_ordinal_suffix(climber[3])}.",
                f"The week's social mobility award goes to {climber[1]}: {climber[2]}{_ordinal_suffix(climber[2])} became {climber[3]}{_ordinal_suffix(climber[3])} in a hurry.",
                f"{climber[1]} spent GW{gw} climbing over furniture and rivals alike, moving from {climber[2]}{_ordinal_suffix(climber[2])} to {climber[3]}{_ordinal_suffix(climber[3])}.",
                f"A very productive bit of ladder work from {climber[1]} carried them from {climber[2]}{_ordinal_suffix(climber[2])} to {climber[3]}{_ordinal_suffix(climber[3])}.",
            ]))
        if faller[0] < 0 and faller[1] != climber[1]:
            beats.append(_gw_story_choice(rng, [
                f"Going the other way, {faller[1]} slid from {faller[2]}{_ordinal_suffix(faller[2])} to {faller[3]}{_ordinal_suffix(faller[3])}, which is the sort of movement nobody puts in the group chat voluntarily.",
                f"{faller[1]} took the scenic route downward, dropping from {faller[2]}{_ordinal_suffix(faller[2])} to {faller[3]}{_ordinal_suffix(faller[3])}.",
                f"The trapdoor opened beneath {faller[1]}, who fell from {faller[2]}{_ordinal_suffix(faller[2])} to {faller[3]}{_ordinal_suffix(faller[3])}.",
                f"It was a less glamorous weekend for {faller[1]}, sliding from {faller[2]}{_ordinal_suffix(faller[2])} to {faller[3]}{_ordinal_suffix(faller[3])} and discovering gravity is undefeated.",
                f"{faller[1]} misplaced {abs(faller[0])} league place{'s' if abs(faller[0]) != 1 else ''}, tumbling to {faller[3]}{_ordinal_suffix(faller[3])}.",
                f"Somebody greased the ladder under {faller[1]}: {faller[2]}{_ordinal_suffix(faller[2])} became {faller[3]}{_ordinal_suffix(faller[3])} by Monday.",
                f"{faller[1]} went backwards at speed, from {faller[2]}{_ordinal_suffix(faller[2])} to {faller[3]}{_ordinal_suffix(faller[3])}, a journey best undertaken without witnesses.",
            ]))

    for manager in ranked_now:
        current_result, count = _manager_result_streak_through(manager, gw)
        prev_result, prev_count = _manager_result_streak_through(manager, gw - 1) if gw > 1 else (None, 0)
        if current_result == "W" and prev_result == "L" and prev_count >= 2:
            beats.append(_gw_story_choice(rng, [
                f"Relief, finally, for {manager}: victory ended a {prev_count}-match losing streak before it could become a full-blown crisis.",
                f"{manager} have remembered how winning works, snapping a {prev_count}-game losing run just as the word 'crisis' was being typeset.",
                f"Pop the tiny champagne: {manager} stopped a {prev_count}-match skid and finally put a W back on the board.",
                f"The losing streak is dead. {manager} ended {prev_count} straight defeats and may now safely reopen the league table.",
                f"After {prev_count} consecutive losses, {manager} finally found dry land with a win in GW{gw}.",
                f"{manager} dragged themselves out of a {prev_count}-game hole with victory, postponing the emergency meeting by at least seven days.",
                f"A pulse! {manager} ended a {prev_count}-match losing streak and rediscovered the sweet, unfamiliar taste of three points.",
            ]))
            break
        if current_result == "W" and count >= 3:
            beats.append(_gw_story_choice(rng, [
                f"{manager} are beginning to look ominous too — that is now {count} wins on the bounce.",
                f"{manager} have caught fire: {count} straight wins and counting.",
                f"The hottest streak in town belongs to {manager}, now winners of {count} in a row.",
                f"{manager} have stacked up {count} consecutive victories and are starting to develop that deeply irritating aura of inevitability.",
                f"Make it {count} on the spin for {manager}; whatever switch they flicked, somebody should probably unplug it.",
                f"{manager} keep rolling, a {count}-match winning streak now giving the rest of the league something unpleasant to think about.",
                f"That is {count} straight for {manager}, who are currently treating form like a subscription service.",
                f"{manager} have won {count} consecutive games and may soon need to be reminded that humility is technically available.",
            ]))
            break

    closest = min(fixtures, key=lambda f: abs(f["score1"] - f["score2"]))
    close_margin = abs(closest["score1"] - closest["score2"])
    if close_margin <= 3 and closest is not biggest:
        if closest["score1"] == closest["score2"]:
            beats.append(_gw_story_choice(rng, [
                f"The week's twitchiest finish came between {closest['team1']} and {closest['team2']}, who somehow landed dead level on {closest['score1']}-{closest['score2']}.",
                f"{closest['team1']} and {closest['team2']} produced a draw so precise it looked engineered, finishing {closest['score1']}-{closest['score2']}.",
                f"Not even a cigarette paper separated {closest['team1']} and {closest['team2']}: {closest['score1']}-{closest['score2']} and one point each.",
                f"The universe refused to choose between {closest['team1']} and {closest['team2']}, depositing them both on {closest['score1']} points.",
            ]))
        else:
            cw = closest["team1"] if closest["score1"] > closest["score2"] else closest["team2"]
            cl = closest["team2"] if cw == closest["team1"] else closest["team1"]
            cws = max(closest["score1"], closest["score2"])
            cls = min(closest["score1"], closest["score2"])
            beats.append(_gw_story_choice(rng, [
                f"At the other end of the margin scale, {cw} escaped with a {close_margin}-point win over {cl}; that one was decided by fingernails rather than dominance.",
                f"{cw} pinched the week's squeakiest win, edging {cl} {cws}-{cls} by just {close_margin}.",
                f"Somewhere a single bonus point is feeling extremely important: {cw} squeezed past {cl} {cws}-{cls}.",
                f"{cl} came within {close_margin} point{'s' if close_margin != 1 else ''} of changing the entire mood of the week, but {cw} survived {cws}-{cls}.",
                f"The cardiology fixture was {cw} against {cl}, decided {cws}-{cls} after a margin of only {close_margin}.",
                f"{cw} got out by the emergency exit against {cl}, sneaking a {cws}-{cls} victory that could hardly have been tighter.",
                f"A cough in the wrong direction could have changed {cw} v {cl}; instead {cw} held on {cws}-{cls}.",
                f"{cw} won the fantasy equivalent of a photo finish, pipping {cl} {cws}-{cls}.",
                f"There was no room for oxygen between {cw} and {cl}: {cws}-{cls} to {cw}, by the skin of several teeth.",
            ]))

    trade_text = _trade_story_for_gw(gw, rng)
    if trade_text:
        beats.append(trade_text)

    standout = _gameweek_player_standout(gw)
    if standout and standout.get("points", 0) >= 8:
        beats.append(_gw_story_choice(rng, [
            f"On the pitch, {standout['name']} was the week's main character, piling up {standout['points']} points for {standout['manager']}.",
            f"{standout['manager']} got a serious lift from {standout['name']}, whose {standout['points']}-point haul was the individual performance of the round.",
            f"Player honours belong to {standout['name']}: {standout['points']} points for {standout['manager']} and a sizeable chunk of the week's damage personally accounted for.",
            f"{standout['name']} turned up carrying a flamethrower, delivering {standout['points']} points for {standout['manager']}.",
            f"If {standout['manager']} are writing thank-you cards, {standout['name']} gets the first one after a monster {standout['points']}-point haul.",
            f"The individual wrecking ball was {standout['name']}, who dumped {standout['points']} points into {standout['manager']}'s total.",
            f"{standout['name']} spent GW{gw} behaving like a cheat code, producing {standout['points']} points for {standout['manager']}.",
            f"There were useful players and then there was {standout['name']}: {standout['points']} points for {standout['manager']}, thank you very much.",
            f"{standout['manager']} found a rocket booster in the shape of {standout['name']}, whose {standout['points']} points lit up the round.",
            f"Top billing among the players goes to {standout['name']}, a {standout['points']}-point menace in {standout['manager']}'s colours.",
            f"{standout['name']} woke up and chose statistical violence, returning {standout['points']} for {standout['manager']}.",
            f"The week's fantasy landlord was {standout['name']}, collecting {standout['points']} points and charging {standout['manager']} absolutely no rent.",
        ]))

    stinker = _starter_stinker(gw)
    if stinker:
        pts, player, manager = stinker
        beats.append(_gw_story_choice(rng, [
            f"Individual dishonour goes to {player}, whose {pts}-point contribution did precisely nothing for {manager}'s blood pressure.",
            f"{manager} will not be sending {player} flowers after a miserable {pts}-point showing in the starting XI.",
            f"Spare a thought for {manager}, who watched {player} serve up {pts} point{'s' if pts != 1 else ''} when selected to actually help.",
            f"At the opposite end of usefulness, {player} contributed {pts} for {manager}, a performance best described as physically present.",
            f"{player} dropped a majestic {pts} point{'s' if pts != 1 else ''} into {manager}'s XI, which is technically a contribution.",
            f"{manager} started {player} and received {pts} point{'s' if pts != 1 else ''} in return, the fantasy equivalent of opening a birthday card with no money in it.",
            f"A special mention for {player}: {pts} point{'s' if pts != 1 else ''} for {manager} and several minutes of staring blankly at the app.",
            f"{player} produced {pts} for {manager}, bringing all the explosive force of a damp party popper.",
            f"{manager}'s faith in {player} was rewarded with {pts} point{'s' if pts != 1 else ''}, because apparently loyalty is a punishable offence.",
            f"{player} clocked in for {manager}, left {pts} point{'s' if pts != 1 else ''} on the desk and went home.",
            f"The wooden spoon among starters goes to {player}, whose {pts}-point outing for {manager} had all the nutritional value of packing foam.",
        ]))

    luck, opp_avg = _luck_through_gw(gw)
    if luck:
        lucky = max(luck, key=luck.get)
        unlucky = min(luck, key=luck.get)
        if luck[lucky] >= 2.0:
            beats.append(_gw_story_choice(rng, [
                f"The fixture gods continue to smile on {lucky}, whose Luck Index sits at +{luck[lucky]:.1f}; results are running noticeably hotter than the weekly scores suggest.",
                f"{lucky} may wish to buy a lottery ticket: a +{luck[lucky]:.1f} Luck Index says the results have been kinder than the underlying scoring.",
                f"Fortune currently has {lucky} on speed dial. Their Luck Index is +{luck[lucky]:.1f}, which is beginning to look less like a bounce and more like a sponsorship deal.",
                f"{lucky} continue to surf the favourable side of variance at +{luck[lucky]:.1f} on the Luck Index. Long may the dark arts continue.",
                f"There is lucky and there is {lucky}: +{luck[lucky]:.1f} on the index and still finding the soft side of the weekly draw.",
                f"The fantasy gods have apparently added {lucky} to close friends; a +{luck[lucky]:.1f} Luck Index tells its own suspicious little story.",
                f"{lucky}'s horseshoe remains securely installed, with the Luck Index now reading +{luck[lucky]:.1f}.",
            ]))
        if luck[unlucky] <= -2.0:
            beats.append(_gw_story_choice(rng, [
                f"At the opposite end, {unlucky} can feel genuinely aggrieved at {luck[unlucky]:.1f} on the Luck Index, with opponents averaging {opp_avg.get(unlucky, 0):.1f} points against them.",
                f"If anyone is entitled to shake a fist at the fixture list, it is {unlucky}: {luck[unlucky]:.1f} luck and {opp_avg.get(unlucky, 0):.1f} opponent points per week.",
                f"{unlucky} appear to have offended a minor deity. Their Luck Index sits at {luck[unlucky]:.1f}, while opponents are averaging {opp_avg.get(unlucky, 0):.1f} against them.",
                f"Variance has put {unlucky} in a headlock: {luck[unlucky]:.1f} on the Luck Index and an opponent average of {opp_avg.get(unlucky, 0):.1f}.",
                f"The fixture computer owes {unlucky} an apology card. A {luck[unlucky]:.1f} Luck Index and {opp_avg.get(unlucky, 0):.1f} points against on average is grim reading.",
                f"{unlucky} continue to dine at the bad-luck buffet, currently {luck[unlucky]:.1f} on the index with opponents averaging {opp_avg.get(unlucky, 0):.1f}.",
                f"Nobody invite {unlucky} to a casino: the luck meter is at {luck[unlucky]:.1f}, and their opponents are averaging {opp_avg.get(unlucky, 0):.1f} points.",
            ]))

    free_agents = _free_agents_high_in_chart(gw, 3)
    if len(free_agents) >= 2:
        names = ", ".join(name for name, _ in free_agents[:-1]) + f" and {free_agents[-1][0]}"
        beats.append(_gw_story_choice(rng, [
            f"Meanwhile the waiver wire is refusing to stay quiet: {names} remain free agents despite sitting among the strongest unowned scorers at this point of the season.",
            f"There is still value just lying around, with {names} leading a surprisingly healthy group of free agents high up the scoring charts.",
            f"Recruitment departments, wake up: {names} are still unattached and are making the free-agent pool look far less barren than it has any right to be.",
            f"The free-agent cupboard is somehow not bare: {names} are still sitting there, scoring points and waiting for somebody to notice.",
            f"Scouting departments may want to put the kettle down: {names} remain unattached despite elbowing their way up the scoring lists.",
            f"There are points lying on the pavement. {names} are still free agents and increasingly difficult to explain away.",
            f"The waiver wire currently contains {names}, which is less 'scraps' and more 'unattended buffet'.",
            f"Some perfectly usable fantasy footballers remain mysteriously unemployed: {names} are still free and still scoring.",
            f"If anybody fancies doing some actual recruitment, {names} remain available and are making increasingly persuasive little noises in the scoring charts.",
            f"The free-agent pool has developed a suspicious bulge around {names}, all still unowned and all doing enough to deserve a raised eyebrow.",
            f"Waiver-watchers have homework: {names} are still on the shelf, and the shelf is beginning to look embarrassingly well stocked.",
            f"Apparently nobody wants free points: {names} remain available despite hanging around the upper reaches of the unowned scoring charts.",
        ]))

    if len(beats) > 7:
        fixed = beats[:2]
        rest = beats[2:]
        rng.shuffle(rest)
        beats = fixed + rest[:5]

    preview = _next_week_preview(gw, pos_now, rng)
    sentences = [opening] + beats + ([preview] if preview else [])
    return " ".join(sentence.strip() for sentence in sentences if sentence and sentence.strip())

def latest_league_storyline_html():
    if not finished_gws:
        return '<div class="notice">No completed gameweek story yet.</div>'
    gw = max(finished_gws)
    story = league_storyline_for_gw(gw)
    return f'<div class="storyline-latest"><div class="eyebrow">GW{gw} · THE McDRAFT COLUMN</div><p>{escape_html(story)}</p></div>'



def _dashboard_current_free_agents(limit=8):
    candidates = []

    for player_id, meta in elements.items():
        owner = current_owner_by_player.get(int(player_id))

        if owner not in (None, "", 0, "0"):
            continue

        if meta.get("status", "a") == "u":
            continue

        try:
            points = int(meta.get("total_points", 0) or 0)
        except (TypeError, ValueError):
            points = 0

        try:
            form = float(meta.get("form", 0) or 0)
        except (TypeError, ValueError):
            form = 0.0

        candidates.append({
            "id": int(player_id),
            "name": meta.get("web_name", "Unknown"),
            "club": teams_lookup.get(meta.get("team"), "—"),
            "position": positions_lookup.get(meta.get("element_type"), "—"),
            "points": points,
            "form": form,
        })

    candidates.sort(
        key=lambda row: (-row["form"], -row["points"], row["name"])
    )
    return candidates[:limit]


def _dashboard_market_changes_html():
    if not dashboard_market_changes:
        return '<div class="notice">No processed squad changes detected yet.</div>'

    rows = ""
    for row in dashboard_market_changes:
        rows += (
            "<tr>"
            f"<td class=\"manager-name\">{escape_html(row['player'])}</td>"
            f"<td>{escape_html(row['from_team'])}</td>"
            f"<td>{escape_html(row['to_team'])}</td>"
            f"<td>{escape_html(row['move'])}</td>"
            "</tr>"
        )

    return (
        '<div class="table-wrap"><table>'
        '<thead><tr><th>Player</th><th>From</th><th>To</th><th>Move</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div>'
    )


def _dashboard_free_agents_html():
    free_agents = _dashboard_current_free_agents()

    if not free_agents:
        return '<div class="notice">No free-agent recommendations available.</div>'

    rows = ""
    for player in free_agents:
        rows += (
            "<tr>"
            f"<td class=\"manager-name\">{escape_html(player['name'])}</td>"
            f"<td>{escape_html(player['position'])}</td>"
            f"<td>{escape_html(player['club'])}</td>"
            f"<td>{player['form']:.1f}</td>"
            f"<td>{player['points']}</td>"
            "</tr>"
        )

    return (
        '<div class="table-wrap"><table>'
        '<thead><tr><th>Player</th><th>Pos</th><th>Club</th><th>Form</th><th>Pts</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div>'
    )


def _dashboard_upcoming_fixtures_html():
    fixtures = full_fixture_schedule.get(dashboard_target_gw, [])

    if not fixtures:
        return '<div class="notice">Next-GW fixtures are not available yet.</div>'

    html = '<div class="fixtures-list">'

    for fixture in fixtures:
        derby = _derby_name(fixture.get("team1"), fixture.get("team2"))
        derby_html = (
            f'<div class="fixture-derby unified-derby">{escape_html(derby)}</div>'
            if derby
            else ''
        )

        html += (
            '<div class="fixture future-fixture-unified">'
            f'{derby_html}'
            '<div class="fixture-team">'
            f'<span class="fixture-manager">{escape_html(fixture.get("team1", "—"))}</span>'
            '</div>'
            '<div class="fixture-vs">VS</div>'
            '<div class="fixture-team">'
            f'<span class="fixture-manager">{escape_html(fixture.get("team2", "—"))}</span>'
            '</div></div>'
        )

    html += '</div>'
    return html


def _dashboard_live_scoreboard_html():
    raw_matches = [
        match
        for match in (league_matches_all or [])
        if int(match.get("event", 0) or 0) == dashboard_target_gw
    ]

    if not raw_matches:
        return '<div class="notice">GW has started; waiting for live Draft scores.</div>'

    html = '<div class="fixtures-list">'

    for match in raw_matches:
        entry1 = match.get("league_entry_1")
        entry2 = match.get("league_entry_2")

        team1 = league_entry_id_to_name.get(
            entry1,
            league_entry_id_to_name.get(str(entry1), "Unknown")
        )
        team2 = league_entry_id_to_name.get(
            entry2,
            league_entry_id_to_name.get(str(entry2), "Unknown")
        )

        try:
            score1 = int(match.get("league_entry_1_points", 0) or 0)
        except (TypeError, ValueError):
            score1 = 0

        try:
            score2 = int(match.get("league_entry_2_points", 0) or 0)
        except (TypeError, ValueError):
            score2 = 0

        html += (
            '<div class="fixture">'
            '<div class="fixture-team">'
            f'<span class="fixture-score">{score1}</span>'
            f'<span class="fixture-manager">{escape_html(team1)}</span>'
            '</div>'
            '<div class="fixture-vs">LIVE</div>'
            '<div class="fixture-team">'
            f'<span class="fixture-score">{score2}</span>'
            f'<span class="fixture-manager">{escape_html(team2)}</span>'
            '</div></div>'
        )

    html += '</div>'
    return html



def live_gameweek_rundown():
    """Build a short live editorial rundown from the current Draft H2H scores."""
    if dashboard_game_state != "live":
        return ""

    gw = int(dashboard_target_gw)
    raw_matches = [
        match for match in (league_matches_all or [])
        if int(match.get("event", 0) or 0) == gw
    ]

    if not raw_matches:
        return f"GW{gw} is underway, but the live Draft score feed has not populated yet."

    fixtures = []
    for match in raw_matches:
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

        fixtures.append({
            "team1": team1,
            "team2": team2,
            "score1": score1,
            "score2": score2,
            "margin": abs(score1 - score2),
            "total": score1 + score2,
            "derby": _derby_name(team1, team2),
        })

    rng = random.Random((LEAGUE_ID * 100000) + gw * 3571 + sum(f["total"] for f in fixtures))
    active = [f for f in fixtures if f["total"] > 0]
    if not active:
        return rng.choice([
            f"GW{gw} is officially live, although the scoreboard is still clearing its throat. Nobody has put a point on the board yet.",
            f"The curtain is up on GW{gw}, but the scores are still at zero. Calm before the inevitable spreadsheet violence.",
            f"GW{gw} has begun. The live feed says nil-nil everywhere for now, which is about as peaceful as McDraft ever gets.",
        ])

    paragraphs = []

    # Opening snapshot: how many ties are currently decided / level.
    leading = [f for f in active if f["score1"] != f["score2"]]
    level = [f for f in active if f["score1"] == f["score2"]]
    paragraphs.append(rng.choice([
        f"GW{gw} is properly alive now: {len(leading)} of the {len(active)} active ties currently have a leader" + (f", with {len(level)} level" if level else "") + ". The table is moving underneath everybody's feet.",
        f"The live scores are in for GW{gw}, and McDraft has started doing McDraft things. {len(leading)} matchups currently have someone in front" + (f" while {len(level)} remain dead level" if level else "") + ".",
        f"We are into the live meat of GW{gw}. {len(leading)} of the active head-to-heads have a leader right now" + (f" and {len(level)} are tied" if level else "") + ", so the provisional table is already getting a proper shake.",
    ]))

    # Biggest lead and closest contest.
    if leading:
        biggest = max(leading, key=lambda f: (f["margin"], f["total"]))
        if biggest["score1"] > biggest["score2"]:
            bw, bl, bs, ls = biggest["team1"], biggest["team2"], biggest["score1"], biggest["score2"]
        else:
            bw, bl, bs, ls = biggest["team2"], biggest["team1"], biggest["score2"], biggest["score1"]
        paragraphs.append(rng.choice([
            f"The biggest gap at the moment belongs to {bw}, who lead {bl} {bs}-{ls}. That one is beginning to look less like a contest and more like paperwork.",
            f"{bw} are currently dishing out the widest hiding of the round, {bs}-{ls} up on {bl}. Plenty of football left, but the emergency exits are being pointed out.",
            f"The loudest scoreline so far is {bw} {bs}, {bl} {ls}. A {bs-ls}-point cushion is the sort of thing that makes one manager refresh gleefully and the other suddenly remember they have hobbies.",
        ]))

        closest = min(leading, key=lambda f: (f["margin"], -f["total"]))
        if closest is not biggest or len(leading) > 1:
            if closest["score1"] > closest["score2"]:
                cw, cl, cs, cls = closest["team1"], closest["team2"], closest["score1"], closest["score2"]
            else:
                cw, cl, cs, cls = closest["team2"], closest["team1"], closest["score2"], closest["score1"]
            paragraphs.append(rng.choice([
                f"At the squeaky end, {cw} only have {cl} by {cs}-{cls}. One return can still turn that tie inside out.",
                f"The one to keep refreshing is {cw} against {cl}: just {cs}-{cls} as things stand. That is absolutely not safe territory.",
                f"Meanwhile {cw} lead {cl} {cs}-{cls} in the tightest live scrap. A single haul could send the whole thing sideways.",
            ]))

    # Derby callout, if one is live this week.
    derby_fixtures = [f for f in active if f.get("derby")]
    if derby_fixtures:
        d = derby_fixtures[0]
        if d["score1"] == d["score2"]:
            derby_line = f"{d['derby']} is locked at {d['score1']}-{d['score2']} between {d['team1']} and {d['team2']}"
        elif d["score1"] > d["score2"]:
            derby_line = f"{d['team1']} currently lead {d['team2']} {d['score1']}-{d['score2']} in {d['derby']}"
        else:
            derby_line = f"{d['team2']} currently lead {d['team1']} {d['score2']}-{d['score1']} in {d['derby']}"
        paragraphs.append(rng.choice([
            f"Derby watch: {derby_line}. Bragging rights are currently being priced in by the minute.",
            f"And because ordinary stress was apparently insufficient, {derby_line}. Lovely, poisonous stuff.",
            f"The rivalry desk reports that {derby_line}. Nobody involved will be behaving normally until this is settled.",
        ]))

    # Apply live results to completed standings to identify the provisional leader.
    live_lp = {m: float(league_points.get(m, 0)) for m in managers}
    live_pf = {m: float(points_for.get(m, 0)) for m in managers}
    for f in fixtures:
        t1, t2 = f["team1"], f["team2"]
        if t1 not in live_lp or t2 not in live_lp:
            continue
        live_pf[t1] += f["score1"]
        live_pf[t2] += f["score2"]
        if f["score1"] > f["score2"]:
            live_lp[t1] += 3
        elif f["score2"] > f["score1"]:
            live_lp[t2] += 3
        else:
            live_lp[t1] += 1
            live_lp[t2] += 1

    ranked_live = sorted(managers, key=lambda m: (-live_lp.get(m, 0), -live_pf.get(m, 0), m.lower()))
    old_leader = current_standings[0] if current_standings else None
    new_leader = ranked_live[0] if ranked_live else None
    if new_leader:
        if old_leader and new_leader != old_leader:
            paragraphs.append(rng.choice([
                f"Most importantly, the live table has a new provisional leader: {new_leader} have climbed above {old_leader}. If every score froze here, the summit would change hands.",
                f"As it stands, {new_leader} would take over at the top from {old_leader}. The throne is currently being moved while everyone is still playing.",
                f"The live standings have {new_leader} pinching first place from {old_leader}. Entirely provisional, naturally, which has never stopped anyone celebrating too early.",
            ]))
        else:
            paragraphs.append(rng.choice([
                f"At the top, {new_leader} still hold the provisional lead in the live table. The chasing pack has not managed to prise them off the summit yet.",
                f"The live table still has {new_leader} on top. For now, the throne remains exactly where it was.",
                f"As these scores stand, {new_leader} remain league leaders. Everybody below them is currently negotiating with mathematics.",
            ]))

    return "\n\n".join(paragraphs)


def _preview_projected_table(winner=None):
    """Provisional table after giving one team a win; current PF remains the tie-break."""
    projected_points = {manager: float(league_points.get(manager, 0)) for manager in managers}
    if winner in projected_points:
        projected_points[winner] += 3

    ranked = sorted(
        managers,
        key=lambda manager: (
            -projected_points.get(manager, 0),
            -float(points_for.get(manager, 0)),
            manager,
        )
    )
    return ranked, {manager: pos for pos, manager in enumerate(ranked, start=1)}, projected_points


def _preview_table_pressure(fixtures, rng):
    """Build lively standings-aware preview beats for close fixtures and possible movement."""
    if not fixtures or not current_standings:
        return []

    close = []
    movement = []

    for fixture in fixtures:
        team1 = fixture.get("team1", "Unknown")
        team2 = fixture.get("team2", "Unknown")
        if team1 not in manager_current_rank or team2 not in manager_current_rank:
            continue

        rank1 = manager_current_rank[team1]
        rank2 = manager_current_rank[team2]
        pts1 = float(league_points.get(team1, 0))
        pts2 = float(league_points.get(team2, 0))
        rank_gap = abs(rank1 - rank2)
        points_gap = abs(pts1 - pts2)

        if rank_gap <= 2 or points_gap <= 3:
            close.append({
                "team1": team1,
                "team2": team2,
                "rank1": rank1,
                "rank2": rank2,
                "pts1": pts1,
                "pts2": pts2,
                "rank_gap": rank_gap,
                "points_gap": points_gap,
            })

        for team, opponent, old_rank in (
            (team1, team2, rank1),
            (team2, team1, rank2),
        ):
            _, projected_ranks, projected_points = _preview_projected_table(team)
            new_rank = projected_ranks.get(team, old_rank)
            if new_rank < old_rank:
                movement.append({
                    "team": team,
                    "opponent": opponent,
                    "old_rank": old_rank,
                    "new_rank": new_rank,
                    "new_points": projected_points.get(team, 0),
                    "places": old_rank - new_rank,
                })

    bits = []

    if close:
        close.sort(key=lambda row: (row["points_gap"], row["rank_gap"], row["rank1"] + row["rank2"]))
        fixture = close[0]
        t1, t2 = fixture["team1"], fixture["team2"]
        r1, r2 = fixture["rank1"], fixture["rank2"]
        p1, p2 = fixture["pts1"], fixture["pts2"]
        if p1 == p2:
            table_context = f"level on {p1:.0f} league points"
        else:
            table_context = f"separated by only {abs(p1-p2):.0f} league point{'s' if abs(p1-p2) != 1 else ''}"

        bits.append(rng.choice([
            f"The table has a proper knife-edge fixture too: {t1} ({r1}{_ordinal_suffix(r1)}) face {t2} ({r2}{_ordinal_suffix(r2)}), with the pair {table_context}. That is less a fixture and more a small administrative knife fight.",
            f"Keep one eye on {t1} v {t2}. They sit {r1}{_ordinal_suffix(r1)} and {r2}{_ordinal_suffix(r2)}, {table_context}, so three points here could have the table doing furniture removal by Sunday night.",
            f"There is barely daylight between {t1} and {t2}: {r1}{_ordinal_suffix(r1)} plays {r2}{_ordinal_suffix(r2)}, {table_context}. A lovely little six-pointer, except technically it is still only worth three. Boring rules.",
            f"For pure table tension, {t1} against {t2} is filthy. They are {r1}{_ordinal_suffix(r1)} and {r2}{_ordinal_suffix(r2)} and {table_context}; somebody could leave this looking significantly taller in the standings.",
            f"The standings have thrown up a pressure cooker in {t1} v {t2}: {r1}{_ordinal_suffix(r1)} against {r2}{_ordinal_suffix(r2)}, {table_context}. Expect live-table refreshing of a medically unnecessary frequency.",
            f"{t1} v {t2} has all the ingredients of a table scrap: {r1}{_ordinal_suffix(r1)} meets {r2}{_ordinal_suffix(r2)}, with them {table_context}. One result could make the standings look very different indeed.",
            f"Circle {t1} against {t2}. They are packed together in {r1}{_ordinal_suffix(r1)} and {r2}{_ordinal_suffix(r2)}, {table_context}, and neither side has much room for a polite little defeat.",
            f"This week's congestion charge applies to {t1} and {t2}: {r1}{_ordinal_suffix(r1)} plays {r2}{_ordinal_suffix(r2)}, {table_context}. Someone is getting elbowed out of the queue.",
            f"There is a wonderfully unpleasant amount riding on {t1} v {t2}. They sit {r1}{_ordinal_suffix(r1)} and {r2}{_ordinal_suffix(r2)}, {table_context}, so even a narrow win could have a very loud effect on the table.",
            f"If you enjoy league-table claustrophobia, {t1} v {t2} is your fixture: {r1}{_ordinal_suffix(r1)} against {r2}{_ordinal_suffix(r2)}, {table_context}. Absolutely no personal space in there.",
        ]))

    # Prefer the biggest plausible jump, then teams nearer the top of the table.
    movement.sort(key=lambda row: (-row["places"], row["new_rank"], row["old_rank"], row["team"]))
    used = set()
    movement_bits = []
    for item in movement:
        if item["team"] in used:
            continue
        used.add(item["team"])
        team = item["team"]
        opponent = item["opponent"]
        old_rank = item["old_rank"]
        new_rank = item["new_rank"]
        movement_bits.append(rng.choice([
            f"If {team} get the job done against {opponent}, they could move provisionally from {old_rank}{_ordinal_suffix(old_rank)} to {new_rank}{_ordinal_suffix(new_rank)}. Suddenly this is not just about winning; it is about nicking somebody else's chair.",
            f"There is a route up the ladder for {team}: beat {opponent} and the current numbers would lift them provisionally from {old_rank}{_ordinal_suffix(old_rank)} to {new_rank}{_ordinal_suffix(new_rank)}, before the rest of the week's scores and tie-breaks have their say.",
            f"{team} have tangible upward mobility this week. A win over {opponent} would put them provisionally {new_rank}{_ordinal_suffix(new_rank)}, up from {old_rank}{_ordinal_suffix(old_rank)} on the present table. Tiny result, potentially enormous group-chat energy.",
            f"Things get spicy for {team}: three points against {opponent} could haul them from {old_rank}{_ordinal_suffix(old_rank)} to a provisional {new_rank}{_ordinal_suffix(new_rank)}. The lift doors are open; they merely need to avoid walking into the wall.",
            f"{team} can do some serious table-hopping here: victory over {opponent} would move them provisionally from {old_rank}{_ordinal_suffix(old_rank)} to {new_rank}{_ordinal_suffix(new_rank)}. One win, several bruised egos above them.",
            f"The arithmetic is very friendly to {team}. Beat {opponent} and they could be sitting provisionally {new_rank}{_ordinal_suffix(new_rank)} instead of {old_rank}{_ordinal_suffix(old_rank)} by the time the dust starts settling.",
            f"There is proper leverage in this one for {team}: take three points from {opponent} and the live picture would bump them from {old_rank}{_ordinal_suffix(old_rank)} to a provisional {new_rank}{_ordinal_suffix(new_rank)}. Efficient little robbery, that.",
            f"A win would do more than pad the record for {team}; against {opponent} it could send them provisionally up to {new_rank}{_ordinal_suffix(new_rank)} from {old_rank}{_ordinal_suffix(old_rank)}. Suddenly everyone above them is checking the rear-view mirror.",
            f"{team} have a genuine springboard fixture. Get past {opponent} and the current maths has them climbing from {old_rank}{_ordinal_suffix(old_rank)} to a provisional {new_rank}{_ordinal_suffix(new_rank)}. Mind the ceiling on the way up.",
        ]))
        if len(movement_bits) >= 2:
            break

    if movement_bits:
        bits.append(" ".join(movement_bits))

    leader = current_standings[0] if current_standings else None
    if leader:
        leader_pts = float(league_points.get(leader, 0))
        challengers = [
            manager for manager in current_standings[1:4]
            if leader_pts - float(league_points.get(manager, 0)) <= 3
        ]
        if challengers:
            challenger = challengers[0]
            gap = leader_pts - float(league_points.get(challenger, 0))
            gap_text = "level on points" if gap == 0 else f"only {gap:.0f} point{'s' if gap != 1 else ''} back"
            bits.append(rng.choice([
                f"And the summit is hardly fortified: {challenger} are {gap_text} behind leaders {leader}. One wobble at the top and the penthouse keys could be changing hands.",
                f"Upstairs, {leader} cannot exactly put the champagne on ice. {challenger} are {gap_text}, so this gameweek has genuine first-place nuisance potential.",
                f"The title race is already refusing to behave: {leader} lead, but {challenger} are {gap_text}. A favourable swing of results could turn the top of the table inside out.",
                f"{leader} have the view from the top, but not much privacy: {challenger} are {gap_text}. One badly timed stumble and the penthouse could become a timeshare.",
                f"There is no comfort blanket for {leader} this week. {challenger} sit {gap_text}, close enough to turn one ordinary result into a full-blown summit reshuffle.",
                f"The gap at the top is more suggestion than safety net: {leader} lead with {challenger} {gap_text}. This could get twitchy very quickly.",
                f"{leader} remain top dogs for now, but {challenger} are {gap_text}. A swing the wrong way and first place could develop a vacancy notice.",
                f"The summit battle is properly alive: {leader} are in front, {challenger} are {gap_text}, and nobody up there should be getting comfortable enough to put their feet on the desk.",
            ]))

    return bits


def upcoming_gameweek_preview_story():
    """Dramatic preview driven by fixtures, derbies and live market movement."""
    gw = dashboard_target_gw
    fixtures = full_fixture_schedule.get(gw, [])
    rng = random.Random(
        (LEAGUE_ID * 100003)
        + (gw * 104729)
        + len(dashboard_market_changes)
    )

    paragraphs = []

    openings = [
        f"GW{gw} is already rattling the cage. The scores are still on zero, but the market has moved and McDraft has entered that dangerous period where everybody thinks they have fixed their squad.",
        f"The dust from GW{dashboard_last_finished_gw} has barely settled and GW{gw} is already causing trouble. Waivers have landed, squads have shifted and optimism has once again become completely untethered from evidence.",
        f"Welcome to the GW{gw} build-up: no football yet, plenty of administrative violence. The waiver wire has fired, managers have gone shopping and the next round is beginning to smell faintly of chaos.",
        f"GW{gw} has not kicked a ball yet and somehow there is already drama. The market is moving, squads are being rewritten and several managers have plainly decided last week's problems were personnel rather than management.",
        f"The shutters are up on GW{gw}. Transfers are moving, free agents are disappearing from shelves and ten managers are simultaneously convincing themselves that this time they have absolutely nailed it.",
        f"GW{gw} is warming up nicely. The waiver smoke has cleared, the shopping bags are full and every manager has found at least one reason to believe this week will be different.",
        f"We have entered the dangerous pre-GW{gw} optimism window. Squads have been tinkered with, receipts have been hidden and everybody is temporarily undefeated again.",
        f"The run-up to GW{gw} is in full swing: deals done, waivers claimed and several deeply questionable masterplans now officially in circulation.",
        f"Before a single point has been scored in GW{gw}, the league has already produced movement, intrigue and the faint smell of panic-buying. Excellent conditions for nonsense.",
        f"GW{gw} approaches with the usual cocktail of hope and terrible judgement. The market has spoken; whether it knew what it was saying is another matter entirely.",
    ]
    paragraphs.append(rng.choice(openings))

    derby_bits = []
    for fixture in fixtures:
        derby = _derby_name(fixture.get("team1"), fixture.get("team2"))
        if not derby:
            continue

        t1 = fixture.get("team1", "Unknown")
        t2 = fixture.get("team2", "Unknown")

        derby_bits.append(rng.choice([
            f"Then there is {derby}: {t1} against {t2}. Three league points are available, but more importantly so is the right to be absolutely unbearable for a week.",
            f"Top billing belongs to {derby}, with {t1} and {t2} renewing hostilities. Form, reason and basic human decency may all be suspended until the final score is in.",
            f"The fixture computer has chosen violence: {derby} sends {t1} into {t2}. Expect screenshots, selective memory and forensic interpretation of every point.",
            f"Clear the diary for {derby}. {t1} meet {t2}, and losing this particular fixture tends to have a much longer half-life than an ordinary defeat.",
            f"The {derby} is back, dragging {t1} and {t2} into another beautifully unnecessary emotional crisis. Three points matter; the screenshots afterwards matter more.",
            f"No ordinary fixture here: it is {derby}, with {t1} facing {t2}. Expect tactical genius to be claimed retrospectively by whoever wins.",
            f"{derby} lands in GW{gw}, and {t1} against {t2} comes with enough baggage to require its own carousel at Bristol Airport.",
            f"Rivalry alert: {derby} pits {t1} against {t2}. Whoever loses can expect the result to be brought up at completely unrelated moments for the foreseeable future.",
            f"Forget calm, rational fantasy management: {derby} is on the card. {t1} and {t2} are playing for points, pride and control of the narrative.",
        ]))

    if derby_bits:
        paragraphs.append(" ".join(derby_bits[:2]))

    table_pressure = _preview_table_pressure(fixtures, rng)
    paragraphs.extend(table_pressure)

    pickups = [m for m in dashboard_market_changes if m.get("move") == "Pickup"]
    transfers = [m for m in dashboard_market_changes if m.get("move") == "Transfer"]
    drops = [m for m in dashboard_market_changes if m.get("move") == "Drop"]

    market_bits = []

    for move in transfers[:2]:
        market_bits.append(rng.choice([
            f"{move['player']} has crossed from {move['from_team']} to {move['to_team']}. Somebody will call it inspired recruitment; somebody else is quietly bookmarking this paragraph.",
            f"{move['player']} changes hands, leaving {move['from_team']} for {move['to_team']}. A perfectly sensible transaction right up until the player scores 2 or 14.",
            f"There has been an actual handover: {move['player']} moves from {move['from_team']} to {move['to_team']}. The trade-grade tribunal is already putting on its little wig.",
            f"{move['to_team']} have prised {move['player']} away from {move['from_team']}. One manager sees upside; the other is already preparing an alternative history of why they never wanted him anyway.",
            f"A proper piece of business sees {move['player']} go from {move['from_team']} to {move['to_team']}. Sensible roster management, reckless overreach, or both at once? Give it a week.",
            f"{move['player']} has swapped {move['from_team']} for {move['to_team']}. The paperwork is done; now comes the bit where everyone pretends they knew the exact outcome in advance.",
            f"Trade traffic: {move['player']} heads from {move['from_team']} to {move['to_team']}. One side will eventually call this a masterstroke and the other will insist context matters.",
            f"The market has delivered a live one: {move['player']} moves from {move['from_team']} to {move['to_team']}. Somewhere in the league, a future receipt is already being saved.",
        ]))

    for move in pickups[:3]:
        market_bits.append(rng.choice([
            f"{move['to_team']} have swooped for {move['player']} from free agency, which is either inspired scouting or tomorrow's evidence exhibit.",
            f"{move['to_team']} have grabbed {move['player']} off the wire. New toy acquired; unreasonable expectations activated.",
            f"{move['player']} is off the shelf and into {move['to_team']}. Nothing says 'new gameweek, new me' like immediate emotional dependence on a pickup.",
            f"{move['to_team']} have taken a punt on {move['player']} from the free-agent pool. Cheap, cheerful and currently undefeated as a decision.",
            f"Waiver wire business for {move['to_team']}: {move['player']} comes aboard. In twenty-four hours this will either look obvious or completely deranged.",
            f"{move['player']} has found a home with {move['to_team']}. A tidy bit of scavenging, provided the football gods do not immediately notice.",
            f"{move['to_team']} have beaten the room to {move['player']}. Whether they have discovered value or simply adopted a new problem remains deliciously unclear.",
            f"Fresh through the door at {move['to_team']} is {move['player']}. The honeymoon period officially lasts until his first two-pointer.",
        ]))

    if drops:
        move = drops[0]
        market_bits.append(rng.choice([
            f"{move['player']} has also been cut loose by {move['from_team']}, which is either ruthless squad management or the opening scene of a future Hall of Shame entry.",
            f"{move['from_team']} have shown {move['player']} the door. Cold-blooded efficiency if it works; premium-grade regret material if it does not.",
            f"There is no room at the inn for {move['player']}: {move['from_team']} have sent him back to free agency, where somebody else can now become emotionally attached.",
            f"{move['player']} has been jettisoned by {move['from_team']}. Every drop looks sensible until the first haul arrives elsewhere.",
            f"{move['from_team']} have pulled the plug on {move['player']}. The Hall of Shame department has opened a file but, for legal reasons, reached no conclusions.",
            f"Out goes {move['player']} from {move['from_team']}. Ruthless pruning, panic button, or an act of tremendous foresight? The league will decide loudly.",
        ]))

    if market_bits:
        paragraphs.append(" ".join(market_bits[:5]))

    free_agents = _dashboard_current_free_agents(5)
    if free_agents:
        names = [p["name"] for p in free_agents[:3]]
        if len(names) == 1:
            name_text = names[0]
        elif len(names) == 2:
            name_text = f"{names[0]} and {names[1]}"
        else:
            name_text = f"{names[0]}, {names[1]} and {names[2]}"

        paragraphs.append(rng.choice([
            f"And the cupboard is not bare: {name_text} remain among the more interesting free agents. Somewhere, a manager is staring at the app and talking themselves into something reckless.",
            f"Still sitting on the shelf are {name_text}, among the stronger available names. Bargains waiting to happen, or bait. Delicious, stat-shaped bait.",
            f"Free agency still has teeth: {name_text} remain unattached and worth a look before somebody else decides they discovered them first.",
            f"Meanwhile {name_text} are still wandering around free agency unsupervised. That feels less like depth and more like a dare.",
            f"There is still value on the pavement: {name_text} remain available. One good fixture is all it takes for restraint to disappear completely.",
            f"Nobody has claimed {name_text} yet, which means the waiver pool is still carrying a few live grenades with the pins only loosely attached.",
            f"For anyone already regretting their squad, {name_text} are among the names still sitting in free agency and quietly whispering 'go on then'.",
            f"The leftovers are suspiciously appetising: {name_text} remain free. This is exactly how perfectly sensible managers end up making 11pm roster decisions.",
        ]))

    paragraphs.append(rng.choice([
        f"GW{gw} is therefore set: grudges refreshed, squads tinkered with and confidence dangerously high. All that remains is for the actual football to ruin everybody's plans.",
        f"The pieces are on the board for GW{gw}. Now we wait for ninety minutes of football to make several days of careful squad planning look extremely silly.",
        f"That is the state of play before GW{gw}: rivalry, recruitment and rampant overconfidence. Lovely stuff.",
        f"So GW{gw} arrives with the table twitching, the market humming and several reputations already halfway onto the barbecue. Bring on the damage.",
        f"Everything is beautifully poised for GW{gw}: positions to steal, grudges to settle and enough fresh transfers to ensure somebody will look very clever by accident.",
        f"The preview verdict for GW{gw}: unstable table, active market, inflated confidence. In other words, ideal McDraft conditions.",
        f"GW{gw} now has all the required ingredients — rivalry, movement and wildly premature certainty. Time for the players to disrespect the spreadsheet.",
        f"And that is your GW{gw} launchpad. The plans are made, the traps are set and absolutely none of this is guaranteed to survive first kick-off.",
    ]))

    return "\n\n".join(paragraphs)


def homepage_game_state_title():
    if dashboard_game_state == "live":
        return f"GW{dashboard_target_gw} · Live"
    if dashboard_game_state == "upcoming":
        return f"GW{dashboard_target_gw} · Preview"
    if dashboard_last_finished_gw:
        return f"GW{dashboard_last_finished_gw} · Completed"
    return "McDraft"


def homepage_game_state_html():
    if dashboard_game_state == "live":
        live_story = live_gameweek_rundown()
        live_story_html = "".join(
            f"<p>{escape_html(paragraph)}</p>"
            for paragraph in live_story.split("\n\n")
            if paragraph.strip()
        )
        return (
            '<div class="storyline-latest">'
            f'<div class="eyebrow">GW{dashboard_target_gw} · LIVE AROUND McDRAFT</div>'
            f'{live_story_html}'
            '<h3 style="margin-top:18px;">Live head-to-head scores</h3>'
            f'{_dashboard_live_scoreboard_html()}'
            '<h3 style="margin-top:22px;">Live league table</h3>'
            '<p class="card-description">If every current score finished exactly as it stands, this would be the table.</p>'
            f'{live_as_it_stands_table()}'
            '</div>'
        )

    if dashboard_game_state == "upcoming":
        preview_story = upcoming_gameweek_preview_story()
        preview_html = "".join(
            f"<p>{escape_html(paragraph)}</p>"
            for paragraph in preview_story.split("\n\n")
            if paragraph.strip()
        )
        return (
            '<div class="storyline-latest">'
            f'<div class="eyebrow">GW{dashboard_target_gw} · THE McDRAFT PREVIEW</div>'
            f'{preview_html}'
            '<h3>Fixtures</h3>'
            f'{_dashboard_upcoming_fixtures_html()}'
            '<h3 style="margin-top:18px;">Waivers, pickups & transfers</h3>'
            f'{_dashboard_market_changes_html()}'
            '<h3 style="margin-top:18px;">Free agents to watch</h3>'
            f'{_dashboard_free_agents_html()}'
            '</div>'
        )


    return latest_league_storyline_html()


def season_summary_html():
    if not finished_gws:
        return '<div class="notice">No completed gameweeks yet.</div>'
    blocks = []
    for gw in sorted(finished_gws, reverse=True):
        story = league_storyline_for_gw(gw)
        blocks.append('<article class="season-story"><div class="season-story-gw">GW' + str(gw) + '</div><div><p>' + escape_html(story) + '</p></div></article>')
    return ''.join(blocks)



def _event_month_label(gw):
    event = next((e for e in bootstrap.get("events", []) if int(e.get("id", 0) or 0) == int(gw)), {})
    raw = event.get("deadline_time") or ""
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt.strftime("%B %Y")
    except Exception:
        return f"Through GW{gw}"


def manager_of_month_html():
    if not finished_gws:
        return '<div class="notice">No completed months yet.</div>'
    month_gws = defaultdict(list)
    for gw in finished_gws:
        month_gws[_event_month_label(gw)].append(int(gw))
    cards=[]
    for month,gws in month_gws.items():
        lp={m:0 for m in managers}; pf={m:0 for m in managers}; wins={m:0 for m in managers}; played={m:0 for m in managers}
        for match in matches_sorted:
            gw=int(match.get("event",0) or 0)
            if gw not in gws: continue
            a=match.get("entry_1_name"); b=match.get("entry_2_name")
            pa=int(match.get("entry_1_points",0) or 0); pb=int(match.get("entry_2_points",0) or 0)
            if a in lp: pf[a]+=pa; played[a]+=1
            if b in lp: pf[b]+=pb; played[b]+=1
            if pa>pb:
                if a in lp: lp[a]+=3; wins[a]+=1
            elif pb>pa:
                if b in lp: lp[b]+=3; wins[b]+=1
            else:
                if a in lp: lp[a]+=1
                if b in lp: lp[b]+=1
        ranked=sorted(managers,key=lambda m:(-lp[m],-pf[m],-wins[m],m))
        if not ranked: continue
        winner=ranked[0]
        avg=(pf[winner]/played[winner]) if played[winner] else 0
        cards.append(f'<div class="motm-card"><div class="eyebrow">{escape_html(month)}</div><h3>{escape_html(winner)}</h3><div class="motm-stat">{wins[winner]}W · {lp[winner]} league pts · {pf[winner]} scored</div><p>{avg:.1f} points per matchup across GW{min(gws)}–GW{max(gws)}.</p></div>')
    return ''.join(cards) if cards else '<div class="notice">No completed months yet.</div>'


def season_milestones_html():
    if not finished_gws:
        return '<div class="notice">No milestones yet.</div>'
    events=[]
    cum_pf={m:0 for m in managers}; cum_lp={m:0 for m in managers}; streak={m:0 for m in managers}
    hit_pf={m:set() for m in managers}; hit_lp={m:set() for m in managers}; hit_score={m:set() for m in managers}; hit_streak={m:set() for m in managers}
    pf_thresholds=(100,250,500,750,1000,1250,1500,2000)
    lp_thresholds=(10,20,30,40,50,60,75,90)
    score_thresholds=(50,60,70,80,90)
    streak_thresholds=(3,5,7,10)
    for gw in sorted(finished_gws):
        result={}
        for match in [m for m in matches_sorted if int(m.get('event',0) or 0)==int(gw)]:
            a=match.get('entry_1_name'); b=match.get('entry_2_name')
            pa=int(match.get('entry_1_points',0) or 0); pb=int(match.get('entry_2_points',0) or 0)
            for m,score in ((a,pa),(b,pb)):
                if m not in cum_pf: continue
                cum_pf[m]+=score
                for threshold in score_thresholds:
                    if score>=threshold and threshold not in hit_score[m]:
                        hit_score[m].add(threshold); events.append((gw,m,f"First {threshold}+ score",f"{score} points in GW{gw}"))
                for threshold in pf_thresholds:
                    if cum_pf[m]>=threshold and threshold not in hit_pf[m]:
                        hit_pf[m].add(threshold); events.append((gw,m,f"{threshold} points scored",f"Reached {cum_pf[m]} cumulative points in GW{gw}"))
            if pa>pb:
                result[a]='W'; result[b]='L'; cum_lp[a]+=3
            elif pb>pa:
                result[b]='W'; result[a]='L'; cum_lp[b]+=3
            else:
                result[a]=result[b]='D'; cum_lp[a]+=1; cum_lp[b]+=1
        for m in managers:
            for threshold in lp_thresholds:
                if cum_lp[m]>=threshold and threshold not in hit_lp[m]:
                    hit_lp[m].add(threshold); events.append((gw,m,f"{threshold} league points",f"Reached the mark after GW{gw}"))
            streak[m]=streak[m]+1 if result.get(m)=='W' else 0
            for threshold in streak_thresholds:
                if streak[m]>=threshold and threshold not in hit_streak[m]:
                    hit_streak[m].add(threshold); events.append((gw,m,f"{threshold}-win streak",f"Completed in GW{gw}"))
    events.sort(key=lambda x:(-x[0],x[1],x[2]))
    if not events:
        return '<div class="notice">No major milestones yet — give it a week or two.</div>'
    return ''.join(f'<div class="milestone-row"><div class="milestone-gw">GW{gw}</div><div><strong>{escape_html(manager)}</strong><span>{escape_html(title)}</span><small>{escape_html(detail)}</small></div></div>' for gw,manager,title,detail in events)


def season_evolution_data():
    out=[]; lp={m:0 for m in managers}; pf={m:0 for m in managers}; pa={m:0 for m in managers}; w={m:0 for m in managers}; d={m:0 for m in managers}; l={m:0 for m in managers}
    for gw in sorted(finished_gws):
        scores={}
        for match in [x for x in matches_sorted if int(x.get('event',0) or 0)==int(gw)]:
            a=match.get('entry_1_name'); b=match.get('entry_2_name'); sa=int(match.get('entry_1_points',0) or 0); sb=int(match.get('entry_2_points',0) or 0)
            scores[a]=sa; scores[b]=sb
            for m,own,opp in ((a,sa,sb),(b,sb,sa)):
                if m in pf: pf[m]+=own; pa[m]+=opp
            if sa>sb: lp[a]+=3; w[a]+=1; l[b]+=1
            elif sb>sa: lp[b]+=3; w[b]+=1; l[a]+=1
            else: lp[a]+=1; lp[b]+=1; d[a]+=1; d[b]+=1
        order=sorted(managers,key=lambda m:(-lp[m],-pf[m],m))
        rows=[{'rank':i+1,'manager':m,'league_points':lp[m],'pf':pf[m],'pa':pa[m],'record':f"{w[m]}-{d[m]}-{l[m]}",'gw_score':scores.get(m,0)} for i,m in enumerate(order)]
        vals=list(scores.values())
        out.append({'gw':gw,'rows':rows,'high_score':max(vals) if vals else 0,'average_score':round(statistics.mean(vals),1) if vals else 0,'leader':order[0] if order else ''})
    return out


def season_timeline_explorer_html():
    if not finished_gws:
        return '<div class="notice">No completed gameweeks yet.</div>'
    return f'<div class="season-slider-head"><div><h2>Season evolution</h2><p class="card-description">Scrub through completed gameweeks and watch the table take shape.</p></div><strong id="season-slider-label">GW{max(finished_gws)}</strong></div><input id="season-gw-slider" class="season-gw-slider" type="range" min="0" max="{len(finished_gws)-1}" value="{len(finished_gws)-1}" step="1" oninput="renderSeasonTimeline(this.value)"><div id="season-slider-summary" class="season-slider-summary"></div><div id="season-slider-table" class="table-wrap"></div>'


def future_fixture_sections():
    last_finished = max(finished_gws) if finished_gws else 0
    future_gws = [gw for gw in range(1, 39) if gw > last_finished]
    if not future_gws:
        return '<div class="notice">No future fixtures available yet.</div>'
    sections = []
    for index, gw in enumerate(future_gws):
        rows = []
        for fixture in full_fixture_schedule.get(gw, []):
            derby = _derby_name(fixture["team1"], fixture["team2"])
            derby_html = f'<div class="fixture-derby">{escape_html(derby)}</div>' if derby else ''
            rows.append(
                '<div class="future-fixture-row">'
                f'<div class="future-fixture-team home">{escape_html(fixture["team1"])}</div>'
                f'<div class="future-fixture-v">vs{derby_html}</div>'
                f'<div class="future-fixture-team">{escape_html(fixture["team2"])}</div>'
                '</div>'
            )
        if not rows:
            rows.append('<div class="notice">Fixture data is not available for this gameweek yet.</div>')
        display = "block" if index == 0 else "none"
        sections.append(f'<div class="future-fixture-slide" id="future-gw-{gw}" style="display:{display};">{"".join(rows)}</div>')
    return ''.join(sections)


# Keep the Gameweek browser independent from prediction/live-odds filtering.
# FPL seasons have 38 gameweeks, so every GW remains browseable even if a
# particular API response temporarily omits a future fixture block. Where
# schedule data exists it is rendered; otherwise the browser shows a small
# availability notice rather than removing the gameweek entirely.
_SEASON_GAMEWEEKS = list(range(1, 39))
future_fixture_gameweeks = [
    gw for gw in _SEASON_GAMEWEEKS
    if gw > (max(finished_gws) if finished_gws else 0)
]
gameweek_browser_gameweeks = sorted(
    set(_SEASON_GAMEWEEKS)
    | set(result_gameweeks)
    | set(full_fixture_schedule.keys())
)

def gameweek_summary_sections():
    sections = ""

    for index, gw in enumerate(finished_gws):
        gw_data = history["gameweeks"][str(gw)].get("teams", {})
        scores = []

        for team in gw_data.values():
            manager = team.get("manager", "Unknown")
            try:
                official_points = official_gw_score(manager, gw)
                points = official_points if official_points is not None else int(team.get("gw_points", 0) or 0)
                scores.append((manager, points))
            except (TypeError, ValueError):
                pass

        scores.sort(key=lambda x: x[1], reverse=True)
        highest = scores[0] if scores else ("—", 0)
        lowest = scores[-1] if scores else ("—", 0)
        average = statistics.mean([score for _, score in scores]) if scores else 0

        fixtures = results_by_gw.get(gw, [])
        margins = [abs(match["score1"] - match["score2"]) for match in fixtures]
        biggest_margin = max(margins) if margins else 0
        closest_margin = min(margins) if margins else 0
        standout = _gameweek_player_standout(gw)
        story = _gameweek_story(gw, scores, fixtures)
        story_html = "".join(f"<p>{escape_html(paragraph)}</p>" for paragraph in story.split("\n\n") if paragraph.strip())

        display_mode = "block" if index == len(finished_gws) - 1 else "none"

        sections += f"""
            <div class="gw-summary-slide" id="summary-gw-{gw}" style="display:{display_mode};">
                <div class="gw-story">
                    <div class="eyebrow">THE STORY OF GW{gw}</div>
                    <div class="gw-story-copy">{story_html}</div>
                </div>
                <div class="gw-summary-grid">
                    <div class="summary-stat"><span>Manager of the Week</span><strong>{escape_html(highest[0])}</strong><b>{highest[1]} pts</b></div>
                    <div class="summary-stat"><span>Stinker</span><strong>{escape_html(lowest[0])}</strong><b>{lowest[1]} pts</b></div>
                    <div class="summary-stat"><span>League Average</span><strong>{average:.1f}</strong><b>pts</b></div>
                    <div class="summary-stat"><span>Biggest Win</span><strong>{biggest_margin}</strong><b>point margin</b></div>
                    <div class="summary-stat"><span>Closest Game</span><strong>{closest_margin}</strong><b>point margin</b></div>
                    <div class="summary-stat"><span>Player of the Week</span><strong>{escape_html(standout['name']) if standout else '—'}</strong><b>{standout['points'] if standout else 0} pts</b></div>
                </div>
            </div>
        """

    return sections

def manager_profile_cards():

    cards = ""
    
    # Get all gameweeks (finished and current)
    all_captured_gws = sorted([int(gw) for gw in history.get("gameweeks", {}).keys()])

    for manager in current_standings:
        # Use all captured gameweeks, not just finished ones
        scores = [
            score for gw, score in gw_scores.get(manager, [])
            if gw in all_captured_gws
        ]
        max_score = max(scores) if scores else 0
        scale = max(max_score, 1)
        # Show last 10 captured gameweeks (including current if in progress)
        last_10_gws = all_captured_gws[-10:] if len(all_captured_gws) >= 10 else all_captured_gws
        
        bars = "".join(
            f'<span class="mini-bar" style="height:{max(8, int(score / scale * 100))}%" title="GW{gw}: {score} pts"></span>'
            for gw, score in gw_scores.get(manager, [])
            if gw in last_10_gws
        )
        form = manager_form_data.get(manager, [])[-5:]
        form_html = "".join(
            f'<span class="form-badge form-{r.lower()}">{r}</span>'
            for r in form
        ) or '<span class="muted">—</span>'

        selection = manager_selection.get(manager, {})

        key_player = key_player_by_manager.get(manager)

        key_player_html = (
            f'<span class="key-player-name">{escape_html(key_player["name"])}</span> '
            f'<span class="key-player-points">{key_player["points"]} pts</span>'
            if key_player
            else '<span class="muted">—</span>'
        )

        cards += f'''
            <div class="manager-profile-card">
                <div class="manager-profile-top">
                    <div>
                        <div class="manager-profile-rank">#{manager_current_rank.get(manager, "—")}</div>
                        <div class="manager-profile-name">{escape_html(manager)}</div>
                        <div class="form-badges">{form_html}</div>
                    </div>
                    <div class="manager-profile-points">{league_points[manager]:.0f}<small>league pts</small></div>
                </div>

                <div class="mini-chart">{bars}</div>

                <div class="manager-profile-stats">
                    <span><b>{avg_points.get(manager, 0):.1f}</b> avg</span>
                    <span><b>{matches_won[manager]}</b> wins</span>
                    <span><b>{manager_transaction_counts.get(manager, 0)}</b> moves</span>
                    <span><b>{selection.get("efficiency", 0):.1f}%</b> XI efficiency</span>
                </div>

                <div class="key-player-row">
                    <span class="key-player-label">Key Player</span>
                    {key_player_html}
                </div>
            </div>
        '''

    return cards


def league_records_html():

    all_scores = []
    for manager in managers:
        for gw, score in gw_scores.get(manager, []):
            if gw in finished_gws:
                all_scores.append((score, manager, gw))

    highest = max(all_scores, default=(0, "—", "—"))
    lowest = min(all_scores, default=(0, "—", "—"))

    match_records = []
    for gw, fixtures in results_by_gw.items():
        for fixture in fixtures:
            margin = abs(fixture["score1"] - fixture["score2"])
            match_records.append((margin, gw, fixture))

    biggest_win = max(match_records, default=(0, "—", {"team1":"—","score1":0,"team2":"—","score2":0}))
    closest = min(match_records, default=(0, "—", {"team1":"—","score1":0,"team2":"—","score2":0}))

    longest_win = (None, 0)
    for manager, form in manager_form_data.items():
        run = 0
        best = 0
        for r in form:
            run = run + 1 if r == "W" else 0
            best = max(best, run)
        if best > longest_win[1]:
            longest_win = (manager, best)

    best_selection = max(
        manager_selection.items(),
        key=lambda x: x[1].get("efficiency", 0),
        default=("—", {"efficiency": 0})
    )

    worst_selection = max(
        manager_selection.items(),
        key=lambda x: x[1].get("missed", 0),
        default=("—", {"missed": 0})
    )

    records = [
        ("Highest GW score", highest[1], f"{highest[0]} pts · GW{highest[2]}"),
        ("Lowest GW score", lowest[1], f"{lowest[0]} pts · GW{lowest[2]}"),
        ("Biggest victory", f'{biggest_win[2]["team1"]} {biggest_win[2]["score1"]}–{biggest_win[2]["score2"]} {biggest_win[2]["team2"]}', f'GW{biggest_win[1]} · {biggest_win[0]} pt margin'),
        ("Closest match", f'{closest[2]["team1"]} {closest[2]["score1"]}–{closest[2]["score2"]} {closest[2]["team2"]}', f'GW{closest[1]} · {closest[0]} pt margin'),
        ("Longest winning streak", longest_win[0] or "—", f'{longest_win[1]} consecutive wins'),
        ("Best XI selector", best_selection[0], f'{best_selection[1]["efficiency"]:.1f}% average efficiency'),
        ("Most points left behind", worst_selection[0], f'{worst_selection[1]["missed"]} points against optimal XIs'),
    ]

    return "".join(
        f'<div class="record-card"><div class="record-label">{escape_html(label)}</div><div class="record-value">{escape_html(value)}</div><div class="record-detail">{escape_html(detail)}</div></div>'
        for label, value, detail in records
    )



def live_as_it_stands_table():
    """Return a provisional H2H table with the current live GW applied."""
    if dashboard_game_state != "live":
        return '<div class="notice">The live table will appear once the gameweek starts.</div>'

    live_lp = {m: float(league_points.get(m, 0)) for m in managers}
    live_pf = {m: float(points_for.get(m, 0)) for m in managers}
    live_pa = {m: float(points_against.get(m, 0)) for m in managers}
    live_w = {m: int(matches_won.get(m, 0)) for m in managers}
    live_d = {m: int(matches_drawn.get(m, 0)) for m in managers}
    live_l = {m: int(matches_lost.get(m, 0)) for m in managers}

    raw_matches = [
        match for match in (league_matches_all or [])
        if int(match.get("event", 0) or 0) == int(dashboard_target_gw)
    ]

    if not raw_matches:
        return '<div class="notice">Waiting for live Draft standings data.</div>'

    for match in raw_matches:
        e1 = match.get("league_entry_1")
        e2 = match.get("league_entry_2")
        t1 = league_entry_id_to_name.get(e1, league_entry_id_to_name.get(str(e1), "Unknown"))
        t2 = league_entry_id_to_name.get(e2, league_entry_id_to_name.get(str(e2), "Unknown"))

        if t1 == "Unknown" or t2 == "Unknown":
            continue

        try:
            p1 = int(match.get("league_entry_1_points", 0) or 0)
        except (TypeError, ValueError):
            p1 = 0
        try:
            p2 = int(match.get("league_entry_2_points", 0) or 0)
        except (TypeError, ValueError):
            p2 = 0

        for team in (t1, t2):
            live_lp.setdefault(team, 0.0)
            live_pf.setdefault(team, 0.0)
            live_pa.setdefault(team, 0.0)
            live_w.setdefault(team, 0)
            live_d.setdefault(team, 0)
            live_l.setdefault(team, 0)

        live_pf[t1] += p1
        live_pf[t2] += p2
        live_pa[t1] += p2
        live_pa[t2] += p1

        # Provisional result: this is deliberately "as it stands".
        if p1 > p2:
            live_lp[t1] += 3
            live_w[t1] += 1
            live_l[t2] += 1
        elif p2 > p1:
            live_lp[t2] += 3
            live_w[t2] += 1
            live_l[t1] += 1
        else:
            live_lp[t1] += 1
            live_lp[t2] += 1
            live_d[t1] += 1
            live_d[t2] += 1

    ranked = sorted(
        live_lp,
        key=lambda m: (-live_lp[m], -live_pf[m], m.lower())
    )

    previous_positions = {m: i for i, m in enumerate(current_standings, start=1)}
    rows = ""

    for position, manager in enumerate(ranked, start=1):
        previous = previous_positions.get(manager, position)
        movement = previous - position
        if movement > 0:
            movement_html = f'<span class="rank-up">↑ {movement}</span>'
        elif movement < 0:
            movement_html = f'<span class="rank-down">↓ {abs(movement)}</span>'
        else:
            movement_html = '<span class="rank-flat">—</span>'

        rows += f"""
            <tr>
                <td class="rank-cell">{position}</td>
                <td class="manager-name">{escape_html(manager)}</td>
                <td>{movement_html}</td>
                <td>{live_lp[manager]:.0f}</td>
                <td>{live_w[manager]}-{live_d[manager]}-{live_l[manager]}</td>
                <td>{live_pf[manager]:.0f}</td>
                <td>{live_pa[manager]:.0f}</td>
            </tr>
        """

    return f"""
        <div class="live-table-banner">AS IT STANDS · GW{dashboard_target_gw}</div>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>#</th><th>Manager</th><th>Move</th><th>Pts</th>
                        <th>W-D-L</th><th>PF</th><th>PA</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        <div class="muted" style="margin-top:10px;">Provisional table using the current live head-to-head scores.</div>
    """


# ============================================================

# RESULTS / FIXTURE BROWSER HTML
# ============================================================

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


def fixture_difficulty(manager, opponent):
    raw = float(fixture_strength_score.get(opponent, 50.0))
    return 1.0 + (raw / 100.0) * 4.0


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
                "difficulty": fixture_difficulty(manager, opp),
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
            d1 = fixture_difficulty(t1, t2)
            d2 = fixture_difficulty(t2, t1)
            rivalry = _rivalry_label(t1, t2)
            rivalry_html = f'<div class="fixture-rivalry-banner">🔥 {escape_html(rivalry)}</div>' if rivalry else ""
            cards += f'''<div class="fixture-planner-card">
                {rivalry_html}
                <div class="fixture-planner-gw">GW{gw}</div>
                <div class="fixture-planner-match"><strong>{escape_html(t1)}</strong><span>vs</span><strong>{escape_html(t2)}</strong></div>
                <div class="fixture-difficulty-row">
                    <span class="fixture-difficulty-pill {_difficulty_class(d1)}">{escape_html(t1)} · {d1:.1f}/5</span>
                    <span class="fixture-difficulty-pill {_difficulty_class(d2)}">{escape_html(t2)} · {d2:.1f}/5</span>
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
            cells += f'<td><div class="fixture-run-cell {_difficulty_class(r["difficulty"])}"><b>{escape_html(r["opponent"])}</b><span>{badge} {r["difficulty"]:.1f}</span></div></td>'
        rows += f'<tr><td class="manager-name">{escape_html(manager)}</td>{cells}<td><b>{run_avg:.2f}</b></td></tr>'
    run_scores.sort(reverse=True)
    hardest = run_scores[0] if run_scores else (0, "—")
    easiest = run_scores[-1] if run_scores else (0, "—")
    summary = f'''<div class="analytics-insight-grid">
        <div class="analytics-insight"><span>Hardest upcoming run</span><strong>{escape_html(hardest[1])}</strong><small>{hardest[0]:.2f}/5 average difficulty</small></div>
        <div class="analytics-insight"><span>Kindest upcoming run</span><strong>{escape_html(easiest[1])}</strong><small>{easiest[0]:.2f}/5 average difficulty</small></div>
    </div>'''
    return f'''{summary}
        <div class="card"><h2>Upcoming fixtures</h2><p class="card-description">Difficulty is opponent strength on a 1–5 scale using projected squad strength, recent form, season scoring and current power rating. Rivalries are flagged automatically.</p>{fixture_sections or '<div class="notice">No future fixtures available.</div>'}</div>
        <div class="card"><h2>Upcoming run · next five</h2><p class="card-description">Lower is kinder. Higher is filthier.</p><div class="table-wrap fixture-run-table"><table><thead><tr><th>Manager</th>{head}<th>Run</th></tr></thead><tbody>{rows}</tbody></table></div></div>'''


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
            fit = 0.28*upgrade_score + 0.30*need + 0.17*attainability + 0.08*seller_flex + 0.09*diversification + 0.08*form_score
            realism = 0.55*attainability + 0.25*seller_flex + 0.20*diversification

            targets.append({
                **cand, "owner": seller, "projection": target_proj,
                "replace_name": weakest["name"], "replace_projection": replace_proj,
                "upgrade": upgrade, "fit_score": round(fit,1), "realism_score": round(realism,1),
                "offer_name": best_offer["name"], "offer_projection": own_proj.get(best_offer["id"],0),
                "same_club_owned": existing_same_club,
                "position_need": round(need, 1),
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
        bars += f'''<div class="analytics-bar-row" data-analytics-manager="{escape_html(m)}"><div class="analytics-bar-label">{escape_html(m)}</div><div class="analytics-bar-track"><div class="analytics-bar-fill" style="width:{width:.1f}%"></div><div class="analytics-average-marker" style="left:{avg_pct:.1f}%" title="League average: {league_avg:.1f}{value_suffix}"></div></div><div class="analytics-bar-value">{v:.1f}{value_suffix}<span class="analytics-average-delta"> ({delta:+.1f} vs avg)</span></div></div>'''
    return f'''<div class="card analytics-chart-card analytics-average-capable" data-league-average="{league_avg:.3f}"><h2>{escape_html(title)}</h2>{f'<p class="card-description">{escape_html(description)}</p>' if description else ''}<div class="analytics-axis-title analytics-axis-y">{escape_html(y_label)}</div><div class="analytics-bar-chart">{bars}</div><div class="analytics-average-key">League average: {league_avg:.1f}{value_suffix}</div><div class="analytics-axis-title analytics-axis-x">{escape_html(x_label)}</div></div>'''


def _category_bar_chart_html(title, rows, description="", value_suffix="", x_label="Player", y_label="Value", limit=20, reverse=False):
    clean=[]
    for label,value in rows:
        try:
            v=float(value or 0)
        except (TypeError,ValueError):
            continue
        clean.append((str(label),v))
    clean.sort(key=lambda x:x[1], reverse=not reverse)
    clean=clean[:limit]
    maximum=max([abs(v) for _,v in clean]+[1.0])
    bars=""
    for label,v in clean:
        width=max(2.0,abs(v)/maximum*100.0)
        bars += f'''<div class="analytics-bar-row"><div class="analytics-bar-label" title="{escape_html(label)}">{escape_html(label)}</div><div class="analytics-bar-track"><div class="analytics-bar-fill" style="width:{width:.1f}%"></div></div><div class="analytics-bar-value">{v:.1f}{value_suffix}</div></div>'''
    body = bars or '<div class="notice">Not enough data yet.</div>'
    return f'''<div class="card analytics-chart-card"><h2>{escape_html(title)}</h2>{f'<p class="card-description">{escape_html(description)}</p>' if description else ''}<div class="analytics-axis-title analytics-axis-y">{escape_html(y_label)}</div><div class="analytics-bar-chart">{body}</div><div class="analytics-axis-title analytics-axis-x">{escape_html(x_label)}</div></div>'''



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
        dots += f'<g class="analytics-manager-mark" data-analytics-manager="{escape_html(m)}"><circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="{color}"><title>{escape_html(m)}: {x:.1f}, {y:.1f}</title></circle><text class="trend-chart-axis-label" x="{cx+9:.1f}" y="{cy+4:.1f}">{escape_html(m[:12])}</text></g>'
    axis_titles=(f'<text class="analytics-svg-axis-title" x="{PL+pw/2:.1f}" y="{H-3}" text-anchor="middle">{escape_html(x_label)}</text>'
                 f'<text class="analytics-svg-axis-title" transform="translate(14 {PT+ph/2:.1f}) rotate(-90)" text-anchor="middle">{escape_html(y_label)}</text>')
    return f'''<div class="card analytics-chart-card"><h2>{escape_html(title)}</h2>{f'<p class="card-description">{escape_html(description)}</p>' if description else ''}<div class="trend-chart-svg-wrap"><svg viewBox="0 0 {W} {H}">{grid}{labels}{dots}{axis_titles}</svg></div></div>'''


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
        # Positive = outperforming original draft slot; negative = underperforming.
        row['draft_rank_delta'] = float(row.get('draft_rank', UNDRAFTED_PLAYER_RANK)) - float(perf_rank)
        # Ratio is useful for spotting extreme late-round/undrafted breakouts.
        row['draft_value_ratio'] = float(row.get('draft_rank', UNDRAFTED_PLAYER_RANK)) / max(float(perf_rank), 1.0)

    season_pts=[(p['name'],p.get('season_points',0)) for p in player_rows]
    form5=[(p['name'],p.get('avg_5') or 0) for p in player_rows if p.get('avg_5') is not None]
    form10=[(p['name'],p.get('avg_10') or 0) for p in player_rows if p.get('avg_10') is not None]
    trend=[(p['name'],p.get('trend') or 0) for p in player_rows if p.get('trend') is not None]
    transfer_freq=[(p['name'],p.get('transfers',0)) for p in player_rows]
    owner_count=[(p['name'],p.get('owners',0)) for p in player_rows]
    appearances=[(p['name'],p.get('appearances',0)) for p in player_rows]
    projections=[(p['name'],p.get('projection',0)) for p in player_rows]
    fa_points=[]
    for p in player_rows:
        if current_owner_by_player.get(int(p['id'])) in (None,"",0,"0"):
            fa_points.append((p['name'],p.get('season_points',0)))
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
    draft_overperformers=[(p['name'],p['draft_rank_delta']) for p in player_rows if p.get('drafted')]
    draft_underperformers=[(p['name'],p['draft_rank_delta']) for p in player_rows if p.get('drafted')]
    undrafted_gems=[(p['name'],p.get('season_points',0)) for p in player_rows if not p.get('drafted')]
    goals=[(p['name'],p.get('goals',0)) for p in player_rows if p.get('goals',0)>0]
    assists_data=[(p['name'],p.get('assists',0)) for p in player_rows if p.get('assists',0)>0]
    goal_involvements=[(p['name'],p.get('goal_involvements',0)) for p in player_rows if p.get('goal_involvements',0)>0]
    clean_sheets=[(p['name'],p.get('clean_sheets',0)) for p in player_rows if p.get('clean_sheets',0)>0]
    bonus_points=[(p['name'],p.get('bonus',0)) for p in player_rows if p.get('bonus',0)>0]
    saves_data=[(p['name'],p.get('saves',0)) for p in player_rows if p.get('saves',0)>0]
    defensive_contrib=[(p['name'],p.get('defensive_contributions',0)) for p in player_rows if p.get('defensive_contributions',0)>0]
    points_per90=[(p['name'],p.get('points_per_90',0)) for p in player_rows if p.get('minutes',0)>=180]
    goals_per90=[(p['name'],p.get('goals_per_90',0)) for p in player_rows if p.get('minutes',0)>=180 and p.get('goals',0)>0]
    assists_per90=[(p['name'],p.get('assists_per_90',0)) for p in player_rows if p.get('minutes',0)>=180 and p.get('assists',0)>0]
    draft_x={p['name']:p['draft_rank'] for p in player_rows if p.get('drafted')}
    perf_y={p['name']:p['performance_rank'] for p in player_rows if p.get('drafted')}
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
        extra_obs.append(('Draft steal', f"{steal['name']} was drafted #{int(steal['draft_rank'])} but currently ranks #{int(steal['performance_rank'])} for fantasy output — {int(steal['draft_rank_delta'])} places above draft expectation."))
        extra_obs.append(('Draft underperformer', f"{bust['name']} was drafted #{int(bust['draft_rank'])} but currently ranks #{int(bust['performance_rank'])} for fantasy output — {abs(int(bust['draft_rank_delta']))} places below draft expectation."))
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
    insight_rows = _analytics_observations() + extra_obs
    insights=''.join(f'<div class="analytics-insight"><span>{escape_html(k)}</span><strong>{escape_html(v)}</strong></div>' for k,v in insight_rows[:13])
    player_charts=[
        _category_bar_chart_html('Top season scorers',season_pts,x_label='Player',y_label='Fantasy points'),
        _category_bar_chart_html('Best 5GW form',form5,x_label='Player',y_label='Points per GW'),
        _category_bar_chart_html('Best 10GW form',form10,x_label='Player',y_label='Points per GW'),
        _category_bar_chart_html('Fastest-rising form',trend,x_label='Player',y_label='5GW minus 10GW form'),
        _category_bar_chart_html('Projected player strength',projections,x_label='Player',y_label='Projection'),
        _category_bar_chart_html('Most transferred players',transfer_freq,x_label='Player',y_label='Ownership hand-offs'),
        _category_bar_chart_html('Most widely owned players',owner_count,x_label='Player',y_label='Different managers'),
        _category_bar_chart_html('Most appearances',appearances,x_label='Player',y_label='Captured GWs'),
        _category_bar_chart_html('Best available free agents',fa_points,'Unowned players ranked by season scoring.',x_label='Player',y_label='Fantasy points'),
        _category_bar_chart_html('Points by position',list(pos_points.items()),x_label='Position',y_label='Total points',limit=10),
        _category_bar_chart_html('Biggest draft steals',draft_overperformers,'Positive values mean the player is outperforming their original McDraft pick by this many ranking places.',x_label='Player',y_label='Places above draft rank',limit=20),
        _category_bar_chart_html('Biggest draft busts',draft_underperformers,'Most negative draft-rank deltas: early selections currently performing well below their original slot.',reverse=True,x_label='Player',y_label='Draft rank delta',limit=20),
        _category_bar_chart_html('Undrafted gems',undrafted_gems,'Players outside the original 150-player draft ranked by fantasy points.',x_label='Player',y_label='Fantasy points',limit=20),
        _scatter_chart_html('Draft pick vs current performance rank',draft_x,perf_y,x_label='Original draft pick',y_label='Current points rank'),
        _scatter_chart_html('Draft pick vs fantasy points',draft_x,points_y,x_label='Original draft pick',y_label='Fantasy points'),
        _scatter_chart_html('Draft pick vs goal involvements',draft_x,gi_y,x_label='Original draft pick',y_label='Goals + assists'),
        _scatter_chart_html('Draft pick vs minutes played',draft_x,minutes_y,x_label='Original draft pick',y_label='Minutes'),
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
        _scatter_chart_html('Expected vs actual goal involvements',xgi_x,actual_gi_y,x_label='Expected goal involvements',y_label='Actual goals + assists'),
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
    squad_construction_charts=[
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
        _bar_chart_html('Current squad draft-rank total',draft_total,'Lower is stronger pre-season pedigree.',reverse=True,x_label='Manager',y_label='Draft rank total'),
        _scatter_chart_html('Star reliance vs scoring',top3_reliance_overall,points_for,x_label='Top 3 reliance (%)',y_label='Points scored'),
        _scatter_chart_html('Star reliance vs league position',top3_reliance_overall,{m:manager_current_rank.get(m,0) for m in managers},x_label='Top 3 reliance (%)',y_label='League position',invert_y=True),
        _scatter_chart_html('Club concentration vs scoring',club_conc,points_for,x_label='Largest same-club group',y_label='Points scored'),
        _scatter_chart_html('Squad strength vs league position',squad_strength,{m:manager_current_rank.get(m,0) for m in managers},x_label='Squad strength',y_label='League position',invert_y=True),
    ]
    decision_charts=[
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
    return f'''<div class="card analytics-hero"><h2>McDraft Insights</h2><p class="card-description">Generated from the latest captured league, squad, fixture and transfer data.</p><div class="analytics-insight-grid">{insights}</div></div>
    <div class="analytics-subtabs" role="tablist" aria-label="Analytics sections">
        <button class="analytics-subtab active" type="button" onclick="showAnalyticsSubtab('player', this)">Player Analytics <span>{len(player_charts)}</span></button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('club', this)">Club Analytics <span>{len(club_charts)}</span></button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('squad-strength', this)">Squad Strength <span>{len(squad_strength_charts)}</span></button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('squad-build', this)">Squad Construction <span>{len(squad_construction_charts)}</span></button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('decisions', this)">Manager Decisions <span>{len(decision_charts)}</span></button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('fixtures-h2h', this)">Fixtures & H2H <span>{len(fixture_analytics_charts)}</span></button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('season', this)">Overall Season <span>{len(season_charts)}</span></button>
        <button class="analytics-subtab" type="button" onclick="showAnalyticsSubtab('league-stats', this)">League Stats</button>
    </div>
    <div class="card analytics-manager-filter-card">
        <div class="analytics-manager-filter-head"><div><h2>Manager filter</h2><p class="card-description">Filter manager-based Analytics charts. Player and Premier League club charts stay unchanged.</p></div><span id="analytics-manager-count" class="muted"></span></div>
        <div id="analytics-manager-chips" class="chart-chip-row analytics-manager-chip-row"></div>
        <label class="analytics-average-toggle"><input id="analytics-average-toggle" type="checkbox" onchange="toggleAnalyticsLeagueAverage(this.checked)"> Compare with league average</label>
    </div>
    <div class="analytics-subpage active" id="analytics-sub-player"><div class="analytics-chart-grid">{''.join(player_charts)}</div></div>
    <div class="analytics-subpage" id="analytics-sub-club"><div class="analytics-chart-grid">{''.join(club_charts)}</div></div>
    <div class="analytics-subpage" id="analytics-sub-squad-strength"><div class="analytics-chart-grid">{''.join(squad_strength_charts)}</div></div>
    <div class="analytics-subpage" id="analytics-sub-squad-build"><div class="analytics-chart-grid">{''.join(squad_construction_charts)}</div></div>
    <div class="analytics-subpage" id="analytics-sub-decisions"><div class="analytics-chart-grid">{''.join(decision_charts)}</div></div>
    <div class="analytics-subpage" id="analytics-sub-fixtures-h2h"><div class="analytics-chart-grid">{''.join(fixture_analytics_charts)}</div></div>
    <div class="analytics-subpage" id="analytics-sub-season"><div class="analytics-chart-grid">{''.join(season_charts)}</div></div>
    <div class="analytics-subpage" id="analytics-sub-league-stats">
        <div class="card"><h2>Fun Stats</h2>__FUN_STATS__</div>
        <div class="card"><h2>Manager Profiles</h2><div class="manager-profile-grid">__MANAGER_PROFILE_CARDS__</div></div>
        <div class="card"><h2>League Records</h2><div class="records-grid">__LEAGUE_RECORDS__</div></div>
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
        board_rows += f'''<tr><td><strong>#{row['pick']}</strong></td><td>R{row['round']}</td><td>{escape_html(row['name'])}</td><td>{escape_html(row['position'])}</td><td>{escape_html(row['club'])}</td><td>{escape_html(row['manager'])}</td><td>{row['points']:.0f}</td><td>{escape_html(status)}</td></tr>'''

    return f'''<div class="card analytics-hero"><h2>Draft Night, Revisited</h2><p class="card-description">The original 150 picks versus what actually happened afterwards. A living audit of steals, busts, retention and late-round gold.</p><div class="analytics-insight-grid">{insight_html}</div></div>
    <div class="analytics-chart-grid">{charts}</div>
    <div class="card"><h2>Redraft Today — Top 40</h2><p class="card-description">If McDraft drafted again today using season FPL points as the board.</p><div class="table-wrap"><table><thead><tr><th>Redraft</th><th>Player</th><th>Pos</th><th>Club</th><th>Pts</th><th>Original</th><th>Value Δ</th></tr></thead><tbody>{redraft_rows}</tbody></table></div></div>
    <div class="card"><h2>Original Draft Board</h2><p class="card-description">Every original selection, current output and where that asset lives now.</p><div class="table-wrap"><table><thead><tr><th>Pick</th><th>Round</th><th>Player</th><th>Pos</th><th>Club</th><th>Drafted by</th><th>Pts</th><th>Status</th></tr></thead><tbody>{board_rows}</tbody></table></div></div>'''

# ============================================================
# PAGE DATA
# ============================================================

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
    color: white;
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
.global-search-input { width:100%; background:#0b1120; color:white; border:1px solid var(--border-light); border-radius:10px; padding:11px 14px; font-size:14px; }
.global-search-input:focus { outline:2px solid var(--accent); outline-offset:1px; }
.global-search-results { display:none; position:absolute; top:calc(100% + 7px); left:0; right:0; background:#111827; border:1px solid var(--border-light); border-radius:12px; box-shadow:0 16px 45px rgba(0,0,0,.4); max-height:360px; overflow:auto; z-index:500; }
.global-search-results.active { display:block; }
.global-search-result { display:flex; justify-content:space-between; gap:14px; padding:11px 13px; cursor:pointer; border-bottom:1px solid var(--border); }
.global-search-result:last-child { border-bottom:none; }
.global-search-result:hover { background:#172033; }
.global-search-result strong { color:white; font-size:13px; }
.global-search-result span { color:var(--muted); font-size:11px; text-align:right; }
.search-hit { outline:2px solid var(--accent); outline-offset:3px; transition:outline .2s ease; }
.global-search-tabs { display:flex; gap:5px; padding-top:6px; }
.global-search-tab { border:1px solid var(--border); background:#0f172a; color:var(--muted); border-radius:999px; padding:5px 9px; font-size:10px; font-weight:800; cursor:pointer; }
.global-search-tab.active { color:white; border-color:var(--accent); background:#172033; }
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
.motm-card { border:1px solid var(--border); background:#0f172a; border-radius:12px; padding:15px; }
.motm-card h3 { margin:5px 0 6px; }
.motm-card p { margin:7px 0 0; color:var(--muted); font-size:12px; }
.motm-stat { font-weight:800; color:#e2e8f0; font-size:12px; }
.milestone-list { display:flex; flex-direction:column; gap:8px; max-height:520px; overflow:auto; }
.milestone-row { display:grid; grid-template-columns:58px 1fr; gap:10px; align-items:start; padding:10px 12px; border:1px solid var(--border); border-radius:10px; background:#0f172a; }
.milestone-gw { color:var(--accent); font-weight:900; font-size:12px; }
.milestone-row strong,.milestone-row span,.milestone-row small { display:block; }
.milestone-row span { color:#e2e8f0; font-weight:800; }
.milestone-row small { color:var(--muted); margin-top:2px; }
.season-slider-head { display:flex; justify-content:space-between; gap:12px; align-items:flex-start; }
.season-slider-head h2 { margin-bottom:4px; }
.season-gw-slider { width:100%; accent-color:var(--accent); margin:10px 0 16px; }
.season-slider-summary { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin-bottom:14px; }
.season-slider-summary div { background:#0f172a; border:1px solid var(--border); border-radius:10px; padding:10px; }
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
    background: #172033;
    color: white;
}

.nav-button.active {
    background: var(--card);
    color: white;
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
    color: white;
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
    color: white;
}

.card h3 {
    margin: 0 0 15px;
    color: white;
}

.card-description {
    color: var(--muted);
    font-size: 14px;
    margin: -8px 0 18px;
}

.notice {
    background: #172033;
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
    background: #172033;
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
    background: #172033;
}

.rank-cell {
    color: var(--muted-dark);
    width: 50px;
}

.manager-name {
    font-weight: 650;
    color: white;
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
    background: #172033;
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
    color: white;
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
    background: #172033;
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
    color: white;
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
    color: white;
    font-size: 28px;
    font-weight: 800;
    margin: 4px 0 10px;
}

.my-team-rank { text-align: right; }
.my-team-rank span { display: block; font-size: 30px; font-weight: 850; color: white; }
.my-team-rank small { color: var(--muted); }

.compact-stats { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.compact-stats .stat-card { min-height: 105px; padding: 14px; }
.compact-stats .stat-value { font-size: 20px; }

.squad-card {
    background: #172033;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
}

.squad-card h3 { margin-bottom: 12px; }
.squad-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.squad-heading { color: var(--accent); font-size: 11px; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; }
.squad-row { display: flex; justify-content: space-between; gap: 8px; padding: 7px 0; border-bottom: 1px solid var(--border); font-size: 12px; }
.squad-row b { color: white; }
.bench-row { color: var(--muted); }


.manager-style-card {
    margin-top: 14px;
    background: #172033;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 15px;
}
.manager-style-header { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; margin-bottom:12px; }
.manager-style-header h3 { margin:3px 0 0; color:white; font-size:16px; }
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
.manager-style-explainer b { color:white; }
.manager-style-explainer span { color:var(--muted); line-height:1.45; }
.manager-style-metrics { display:flex; flex-wrap:wrap; gap:8px 14px; margin-top:10px; padding-top:10px; border-top:1px solid var(--border); color:var(--muted); font-size:10px; }
.manager-style-metrics b { color:var(--accent); }

.gw-summary-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 10px;
}

.summary-stat {
    background: #172033;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 13px;
    min-width: 0;
}

.summary-stat span { display: block; color: var(--muted); font-size: 10px; text-transform: uppercase; letter-spacing: .5px; }
.summary-stat strong { display: block; color: white; font-size: 14px; margin: 6px 0 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.summary-stat b { color: var(--accent); font-size: 17px; }

.manager-profile-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
    gap: 14px;
}

.manager-profile-card {
    background: #172033;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 15px;
}

.manager-profile-top { display: flex; justify-content: space-between; gap: 12px; }
.manager-profile-rank { color: var(--accent); font-size: 11px; font-weight: 800; }
.manager-profile-name { color: white; font-size: 17px; font-weight: 750; margin: 3px 0 8px; }
.manager-profile-points { color: white; font-size: 22px; font-weight: 850; text-align: right; }
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
.manager-profile-stats b { color: white; }

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
    color: white;
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

.record-card { background: #172033; border: 1px solid var(--border); border-radius: 11px; padding: 15px; }
.record-label { color: var(--muted); font-size: 10px; text-transform: uppercase; letter-spacing: .5px; }
.record-value { color: white; font-size: 17px; font-weight: 800; margin: 7px 0 4px; }
.record-detail { color: var(--muted-dark); font-size: 12px; }

/* ============================================================
   MY TEAM SELECTOR
   ============================================================ */
.my-team-selector-row { display:flex; justify-content:space-between; align-items:flex-end; gap:18px; margin-bottom:18px; }
.my-team-selector-row h2 { margin-bottom:4px; }
.my-team-selector-row .card-description { margin-bottom:0; }
.my-team-select-wrap { display:flex; flex-direction:column; gap:6px; min-width:230px; }
.my-team-select-wrap span { color:var(--muted); font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:.5px; }
#my-team-select { background:#172033; color:white; border:1px solid var(--border-light); border-radius:8px; padding:10px 12px; font-size:14px; min-width:230px; cursor:pointer; }
#my-team-select:focus { outline:2px solid var(--accent); outline-offset:2px; }

.squad-gw-heading {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 12px;
}

.squad-gw-heading b {
    color: white;
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
    background: #111827;
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
    background: #0b1120;
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
    color: white;
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
    background: #172033;
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
    color: white;
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
    background: #172033;
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
    color: white;
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
    color: white;
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
    background: #172033;
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
    color: white;
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
    background: #172033;
    color: white;
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
    color: white;
    font-weight: 750;
}



.fixture-clickable { cursor:pointer; transition:border-color .15s ease, transform .15s ease, background .15s ease; }
.fixture-clickable:hover,.fixture-clickable:focus-visible { border-color:var(--border-light); background:#1b263b; outline:none; transform:translateY(-1px); }
.fixture-vs small { display:inline-block; margin-top:3px; font-size:9px; color:var(--muted); }
.fixture-detail-overlay { position:fixed; inset:0; z-index:10000; background:rgba(3,7,18,.88); padding:24px; overflow:auto; }
.fixture-detail-overlay[hidden],.fixture-detail-panel[hidden] { display:none; }
.fixture-detail-dialog { position:relative; width:min(1180px,100%); margin:0 auto; background:var(--card); border:1px solid var(--border-light); border-radius:16px; padding:26px; }
.fixture-detail-close { position:absolute; right:14px; top:12px; border:0; background:transparent; color:white; font-size:30px; cursor:pointer; line-height:1; }
.fixture-detail-scoreline { display:grid; grid-template-columns:1fr auto 1fr; align-items:center; gap:18px; padding:4px 42px 20px 0; }
.fixture-detail-scoreline>div:first-child,.fixture-detail-scoreline>div:last-child { display:flex; align-items:baseline; gap:12px; font-size:18px; }
.fixture-detail-scoreline>div:last-child { justify-content:flex-end; }
.fixture-detail-scoreline span { font-size:30px; font-weight:850; color:white; }
.fixture-detail-state { color:var(--muted); font-size:12px; font-weight:750; text-align:center; }
.fixture-xi-grid { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:18px; }
.fixture-xi-heading { display:flex; justify-content:space-between; align-items:baseline; gap:12px; margin-bottom:9px; }
.fixture-xi-heading strong { color:white; font-size:16px; }
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
    background: #0b1120;
    color: white;
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
    background: #172033;
    border: 1px solid var(--border);
    border-radius: 11px;
    padding: 16px;
    margin-bottom: 14px;
}

.player-history-title {
    font-size: 19px;
    font-weight: 750;
    color: white;
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
    color: white;
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
    background: #0b1120;
    color: white;
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
    background: #172033;
    border: 1px solid var(--border);
    border-radius: 11px;
    padding: 13px;
    display: grid;
    grid-template-columns: minmax(160px, 1fr) auto auto;
    gap: 12px;
    align-items: center;
}

.player-directory-name {
    color: white;
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
    color: white;
    font-size: 14px;
}

.player-directory-stats span {
    color: var(--muted-dark);
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: .4px;
}

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
    background: #172033;
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
    color: white;
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
    color: white;
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
    color: white;
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
    background: #172033;
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
    color: white;
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
    color: white;
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
   MOBILE
   ============================================================ */

@media (
    max-width: 900px
) {
    .global-search-wrap { order:3; width:100%; max-width:none; margin-left:0; }
    .header-top { flex-wrap:wrap; }
    .my-team-selector-row { flex-direction:column; align-items:stretch; }
    .my-team-select-wrap, #my-team-select { width:100%; min-width:0; box-sizing:border-box; }


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

.analytics-chart-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:18px; }

.transfer-subtabs { display:flex; gap:8px; margin:0 0 20px; overflow-x:auto; padding-bottom:3px; }
.transfer-subtab { border:1px solid var(--border); background:#0f172a; color:var(--muted); border-radius:10px; padding:10px 14px; cursor:pointer; font-weight:800; white-space:nowrap; }
.transfer-subtab.active { color:white; border-color:var(--accent); background:#172033; box-shadow:inset 0 -2px 0 var(--accent); }
.transfer-subpanel { display:none; } .transfer-subpanel.active { display:block; }

.myteam-position-need-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:14px}
.position-need-card{border:1px solid var(--border);border-radius:12px;padding:13px;background:#0f172a;position:relative;overflow:hidden}
.position-need-card:before{content:"";position:absolute;inset:0;opacity:.12;pointer-events:none;background:var(--need-colour,#64748b)}
.position-need-top{display:flex;justify-content:space-between;gap:8px;align-items:center;position:relative}
.position-need-pos{font-size:12px;font-weight:900;letter-spacing:.08em}.position-need-score{font-size:22px;font-weight:900}
.position-need-label{font-size:11px;font-weight:850;margin-top:5px;position:relative}.position-need-meta{font-size:10px;color:var(--muted);margin-top:5px;position:relative}
.position-need-track{height:7px;border-radius:999px;background:#0b1220;border:1px solid var(--border);overflow:hidden;margin-top:10px;position:relative}
.position-need-fill{height:100%;border-radius:999px;background:var(--need-colour,#64748b)}
@media(max-width:720px){.myteam-position-need-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
.trade-sim-player.position-match{animation:positionPulse 1s ease-in-out 2}
.trade-sim-player.position-match .trade-sim-position{background:var(--accent);color:#07111f}
@keyframes positionPulse{0%,100%{transform:translateX(0)}50%{transform:translateX(3px)}}
.trade-sim-head { display:flex; justify-content:space-between; gap:16px; align-items:flex-start; } .trade-sim-score{text-align:right;min-width:110px}.trade-sim-score span{display:block;color:var(--muted);font-size:11px;text-transform:uppercase}.trade-sim-score b{font-size:28px}
.trade-sim-manager-row{display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:end;margin:18px 0}.trade-sim-manager-row label{font-size:12px;color:var(--muted);font-weight:800}.trade-sim-manager-row select{width:100%;margin-top:6px;background:#0b1220;border:1px solid var(--border);color:white;border-radius:9px;padding:10px}.trade-sim-versus{font-size:22px;padding-bottom:9px}.trade-sim-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.trade-sim-roster{display:grid;gap:7px}.trade-sim-player{display:grid;grid-template-columns:auto 1fr auto;gap:9px;align-items:center;padding:9px 10px;border:1px solid var(--border);border-radius:9px;background:#0f172a;cursor:pointer}.trade-sim-player small{display:block;color:var(--muted);margin-top:2px}.trade-sim-position{appearance:none;border:0;background:rgba(96,165,250,.12);color:var(--accent);font:inherit;font-size:10px;font-weight:900;padding:2px 6px;border-radius:999px;cursor:pointer;margin-right:3px}.trade-sim-position:hover{background:rgba(96,165,250,.22)}.trade-sim-player.position-match{border-color:var(--accent);box-shadow:0 0 0 2px rgba(96,165,250,.18);background:rgba(96,165,250,.08)}.trade-sim-player-value{text-align:right}.trade-sim-player-value b{display:block}.trade-sim-player-value span{font-size:10px;color:var(--muted)}.trade-sim-result{margin-top:16px}.trade-sim-result.valid{border-color:#2f855a}.trade-sim-result.invalid{border-color:#b45309}.trade-sim-summary{margin-top:14px;padding-top:12px;border-top:1px solid var(--border)}.trade-sim-summary p{margin:7px 0 0;color:var(--muted);line-height:1.55}.trade-sim-breakdown{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:10px}.trade-sim-breakdown>div{background:#0f172a;border:1px solid var(--border);border-radius:9px;padding:10px}.positive-text{color:#86efac}.negative-text{color:#fca5a5}@media(max-width:720px){.trade-sim-manager-row,.trade-sim-grid,.trade-sim-breakdown{grid-template-columns:1fr}.trade-sim-versus{text-align:center;padding:0}}

.analytics-subtabs { display:flex; gap:8px; margin:0 0 20px; overflow-x:auto; padding-bottom:3px; }
.analytics-subtab { border:1px solid var(--border); background:#0f172a; color:var(--muted); border-radius:10px; padding:10px 14px; cursor:pointer; font-weight:800; white-space:nowrap; }
.analytics-subtab span { color:var(--accent); margin-left:5px; font-size:11px; }
.analytics-subtab.active { color:white; border-color:var(--accent); background:#172033; box-shadow:inset 0 -2px 0 var(--accent); }
.analytics-subpage { display:none; }
.analytics-subpage.active { display:block; }
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
.analytics-bar-chart { display:flex; flex-direction:column; gap:9px; margin-top:14px; }
.analytics-bar-row { display:grid; grid-template-columns:minmax(100px,160px) minmax(80px,1fr) 58px; gap:10px; align-items:center; }
.analytics-bar-label { font-size:12px; font-weight:750; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.analytics-bar-track { height:9px; border-radius:999px; background:#0b1220; border:1px solid var(--border); overflow:hidden; }
.analytics-bar-fill { height:100%; border-radius:999px; background:linear-gradient(90deg,var(--accent-dark),var(--accent)); }
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
@media (max-width:760px) { .analytics-chart-grid,.analytics-insight-grid,.fixture-planner-grid{grid-template-columns:1fr;} .analytics-bar-row{grid-template-columns:100px minmax(70px,1fr) 50px;} .analytics-dual-row{grid-template-columns:1fr;} .analytics-dual-series{grid-template-columns:100px 1fr 38px;} .trade-target-row{grid-template-columns:1fr;} .trade-target-offer{text-align:left;} }

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

"""


# ============================================================
# JAVASCRIPT
# ============================================================

javascript = r"""
/* ============================================================
   MY TEAM SELECTOR
   ============================================================ */

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
    renderMyTeamStatsCharts();
    renderMyTeamPositionNeeds();
    renderMyTeamFreeAgents();
    renderMyTeamTradeTargets();
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
const GLOBAL_PAGES=[['Overview','overview'],['My Team','myteam'],['Gameweeks','gameweeks'],['Fixtures','fixtures'],['Players','players'],['Transfers','transfers'],['Analytics','analytics'],['Draft Centre','draft-centre'],['Season Summary','season-summary']];

function ensureSearchTargetId(el, idx){
    if(!el.id) el.id='global-search-target-'+idx;
    return el.id;
}

function buildDashboardSearchIndex(){
    const results=[];
    GLOBAL_PAGES.forEach(r=>results.push({type:'page',label:r[0],value:r[1],meta:'Page'}));
    (MANAGER_ORDER||[]).forEach(m=>results.push({type:'manager',label:m,value:m,meta:'Manager'}));
    (playerSearchData||[]).forEach(p=>results.push({type:'player',label:p.name,value:String(p.id),meta:(p.position||'')+' · '+(p.team||'')}));

    let idx=0;
    document.querySelectorAll('.analytics-subtab').forEach(btn=>{
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
        const analyticsSub=sub ? (sub.id||'').replace(/^analytics-sub-/,'') : '';
        results.push({type:'section',label:label,value:targetId,page:pageName,subtab:analyticsSub,meta:(pageName==='analytics'?'Analytics chart/section':'Section')});
    });
    return results;
}

function globalSearchSelect(type,value,label,pageName,subtab){
    const box=document.getElementById('global-search-results'),input=document.getElementById('global-search');
    if(box){box.classList.remove('active');box.innerHTML='';} if(input)input.value='';
    if(type==='page'){showPage(value);return;}
    if(type==='manager'){showPage('myteam');const select=document.getElementById('my-team-select');if(select){for(let i=0;i<select.options.length;i++){if(select.options[i].text===label){select.value=String(i);changeMyTeam();break;}}}return;}
    if(type==='player'){showPage('players');const p=document.getElementById('player-search');if(p){p.value=label;filterPlayers();}return;}
    if(type==='analytics-subtab'){
        showPage('analytics');
        const btn=Array.from(document.querySelectorAll('.analytics-subtab')).find(b=>(b.getAttribute('onclick')||'').includes("'"+value+"'"));
        showAnalyticsSubtab(value,btn||null);
        return;
    }
    if(type==='section'){
        showPage(pageName||'overview');
        if(pageName==='analytics'&&subtab){
            const btn=Array.from(document.querySelectorAll('.analytics-subtab')).find(b=>(b.getAttribute('onclick')||'').includes("'"+subtab+"'"));
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


const analyticsManagerState = { visible: new Set() };

function initAnalyticsManagerFilter() {
    analyticsManagerState.visible = new Set(MANAGER_ORDER);
    renderAnalyticsManagerChips();
    applyAnalyticsManagerFilter();
}

function setAnalyticsManagerPreset(preset) {
    if (preset === "top5") {
        analyticsManagerState.visible = new Set(MANAGER_ORDER.slice(0, Math.min(5, MANAGER_ORDER.length)));
    } else if (preset === "all") {
        analyticsManagerState.visible = new Set(MANAGER_ORDER);
    } else if (preset === "none") {
        analyticsManagerState.visible = new Set();
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
        button.addEventListener("click", function(){ toggleAnalyticsManager(manager); });
        container.appendChild(button);
    });
    const count = document.getElementById("analytics-manager-count");
    if (count) count.textContent = analyticsManagerState.visible.size + " of " + MANAGER_ORDER.length + " managers selected";
}

function applyAnalyticsManagerFilter() {
    document.querySelectorAll("#page-analytics [data-analytics-manager]").forEach(function(el) {
        const manager = el.getAttribute("data-analytics-manager");
        el.classList.toggle("analytics-manager-hidden", !analyticsManagerState.visible.has(manager));
    });
}

function toggleAnalyticsLeagueAverage(enabled) {
    const page=document.getElementById('page-analytics');
    if(page) page.classList.toggle('show-league-average', !!enabled);
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

function showAnalyticsSubtab(name, button) {
    document.querySelectorAll('.analytics-subpage').forEach(function(page) { page.classList.remove('active'); });
    document.querySelectorAll('.analytics-subtab').forEach(function(tab) { tab.classList.remove('active'); });
    var target = document.getElementById('analytics-sub-' + name);
    if (target) target.classList.add('active');
    if (button) button.classList.add('active');
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

const MANAGER_COLORS = {};
MANAGER_ORDER.forEach(function(manager, index) {
    MANAGER_COLORS[manager] = TREND_PALETTE[index % TREND_PALETTE.length];
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

let myTeamSquadIndex = -1;
let myTeamSquadManager = null;

function currentMyTeamManager() {
    const select = document.getElementById("my-team-select");
    if (!select) return null;
    return MANAGER_ORDER[Number(select.value)] || null;
}

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
        return '<div class="squad-row"><span>' + escapePlayerHTML(p.name) + tag + '</span><b>' + p.points + '</b></div>';
    }).join("") || '<div class="muted">No starting XI captured.</div>';

    const benchRows = entry.bench.map(function(p) {
        return '<div class="squad-row bench-row"><span>' + escapePlayerHTML(p.name) + '</span><b>' + p.points + '</b></div>';
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


/* ============================================================
   PLAYER SEARCH
   ============================================================ */

const playerSearchData =
    __PLAYER_SEARCH_DATA__;


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


function renderPlayerDirectoryCard(player) {
    const historyAvailable = Array.isArray(player.history) && player.history.length > 0;
    const owner = player.fantasy_team || "Free Agent";
    const ownerClass = owner === "Free Agent" ? "free-agent" : "";

    return '<div class="player-directory-card">' +
        '<div class="player-directory-main">' +
            '<div class="player-directory-name">' + escapePlayerHTML(player.name) + '</div>' +
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
            '<div class="player-stat-chips">' +
                '<span class="player-stat-chip"><b>' + player.total_points + '</b> Season points</span>' +
                '<span class="player-stat-chip"><b>' + Number(player.form || 0).toFixed(1) + '</b> 5 GW form</span>' +
                '<span class="player-stat-chip"><b>' + Number(player.points_per_game || 0).toFixed(1) + '</b> PPG</span>' +
                '<span class="player-stat-chip"><b>' + player.goals + '</b> Goals</span>' +
                '<span class="player-stat-chip"><b>' + player.assists + '</b> Assists</span>' +
                '<span class="player-stat-chip"><b>' + player.clean_sheets + '</b> Clean Sheets</span>' +
                '<span class="player-stat-chip"><b>' + player.minutes + '</b> Minutes</span>' +
                '<span class="player-stat-chip"><b>' + player.bonus + '</b> Bonus</span>' +
            '</div>' +
            (historyAvailable
                ? '<div class="player-history-chart-heading">Draft ownership & points history</div>' +
                  '<div class="player-gw-chart-wrap trend-chart-svg-wrap">' +
                    buildPlayerHistoryChart(player.history) +
                  '</div>' +
                  '<div class="player-gw-table">' +
                    '<table><thead><tr><th>GW</th><th>Manager(s)</th><th>Points</th></tr></thead><tbody>' +
                    player.history.map(function(row) {
                        const ownerNames = row.owners.length
                            ? row.owners.map(escapePlayerHTML).join(", ")
                            : "Not owned";
                        return '<tr><td>GW' + row.gw + '</td><td>' + ownerNames + '</td><td>' + row.points + '</td></tr>';
                    }).join("") +
                    '</tbody></table></div>'
                : '<div class="notice">No draft ownership history has been captured for this player yet.</div>') +
        '</div>' +
    '</div>';
}



function showTransferSubtab(name, button) {
 document.querySelectorAll('.transfer-subpanel').forEach(p=>p.classList.remove('active')); document.querySelectorAll('.transfer-subtab').forEach(t=>t.classList.remove('active')); const p=document.getElementById('transfer-subpanel-'+name); if(p)p.classList.add('active'); if(button)button.classList.add('active');
}
const TRADE_SIMULATOR_DATA = __TRADE_SIMULATOR_DATA__;
function renderTradeSimulator(){const a=document.getElementById('trade-sim-manager-a'),b=document.getElementById('trade-sim-manager-b'),ra=document.getElementById('trade-sim-roster-a'),rb=document.getElementById('trade-sim-roster-b');if(!a||!b||!ra||!rb)return;const ma=a.value,mb=b.value;document.getElementById('trade-sim-title-a').textContent=(ma||'Manager A')+' gives';document.getElementById('trade-sim-title-b').textContent=(mb||'Manager B')+' gives';if(!ma||!mb||ma===mb){ra.innerHTML=rb.innerHTML='<div class="notice">Choose two different managers.</div>';evaluateTradeSimulator();return;}ra.innerHTML=tradeSimRosterHtml(ma,'a');rb.innerHTML=tradeSimRosterHtml(mb,'b');evaluateTradeSimulator();}
function tradeSimRosterHtml(manager,side){return(TRADE_SIMULATOR_DATA[manager]||[]).map(p=>'<label class="trade-sim-player" data-side="'+side+'" data-position="'+p.position+'" onclick="tradeSimPlayerClicked(event, \''+side+'\', \''+p.position+'\')"><input type="checkbox" class="trade-sim-check" data-side="'+side+'" data-id="'+p.id+'" onchange="tradeSimSelectionChanged(\''+side+'\')"><span><b>'+escapePlayerHTML(p.name)+'</b><small><button type="button" class="trade-sim-position" onclick="highlightOpposingTradePosition(event, \''+side+'\', \''+p.position+'\')">'+p.position+'</button> · '+escapePlayerHTML(p.club)+' · '+p.points+' pts · form '+Number(p.form).toFixed(1)+'</small></span><span class="trade-sim-player-value"><b>'+Number(p.value).toFixed(1)+'</b><span>value</span></span></label>').join('');}
function tradeSimSelectedCount(side){return document.querySelectorAll('.trade-sim-check[data-side="'+side+'"]:checked').length;}
function clearTradePositionHighlights(){document.querySelectorAll('.trade-sim-player.position-match').forEach(el=>el.classList.remove('position-match'));}
function tradeSimSelectionChanged(side){
    evaluateTradeSimulator();
    if(tradeSimSelectedCount(side)>=2){clearTradePositionHighlights();}
}
function tradeSimPlayerClicked(event, side, position){
    // Once two players have been chosen from a side, stop nudging the user with
    // positional highlights. Multi-player trades remain possible; the visual
    // prompt simply gets out of the way after the second selection.
    if(event && event.target && event.target.classList && event.target.classList.contains('trade-sim-position')) return;
    if(tradeSimSelectedCount(side)>=2){clearTradePositionHighlights();return;}
    highlightOpposingTradePosition(null, side, position);
}
function highlightOpposingTradePosition(event, side, position){
    if(event){event.preventDefault();event.stopPropagation();}
    if(tradeSimSelectedCount(side)>=2){clearTradePositionHighlights();return;}
    clearTradePositionHighlights();
    const opposingSide=side==='a'?'b':'a';
    document.querySelectorAll('.trade-sim-player[data-side="'+opposingSide+'"][data-position="'+position+'"]').forEach(el=>el.classList.add('position-match'));
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
        who+' is giving up the stronger original draft pedigree.',
        'Draft-night expectations were materially higher for the package leaving '+who+'.',
        who+' is parting with the assets McDraft valued more highly before the season.',
        'Original draft capital favours the players being sent by '+who+'.',
        'On pre-season pedigree, '+who+' is contributing the more expensive package.',
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
    if(avgDraftB<avgDraftA-10) acceptA.push(pick(['upgrades original draft pedigree','buys back into stronger pre-season pedigree','receives the more highly drafted package','improves draft-capital quality']));

    if(sa.form>sb.form+0.75) acceptB.push(pick(['gets the hotter recent form','buys more short-term momentum','lands the stronger recent performers','improves current form']));
    if(sa.proj>sb.proj+0.5) acceptB.push(pick(['raises projected weekly output','improves the near-term forecast','adds more projected points','wins on forward projection']));
    if(sa.points>sb.points+5) acceptB.push(pick(['brings in more proven season points','adds more banked production','gets the stronger season-to-date output','trades into the better established scoring record']));
    if(sa.importance<sb.importance-5) acceptB.push(pick(['can exchange highly important pieces for assets the other side relies on less','turns heavily-relied-upon assets into a less structurally costly package','may reduce dependence on a small core','gets comparable value without inheriting the same owner-dependence']));
    if(avgDraftA<avgDraftB-10) acceptB.push(pick(['upgrades original draft pedigree','buys back into stronger pre-season pedigree','receives the more highly drafted package','improves draft-capital quality']));

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
    result.innerHTML='<b>'+escapePlayerHTML(lean)+'.</b> The score blends form, total points, projection, original draft pedigree and importance to the current owner.'+
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
    const sortValue = sort ? sort.value : "points";

    let matches = playerSearchData.filter(function(player) {
        return (!query || player.name.toLowerCase().includes(query)) &&
               (!positionValue || player.position === positionValue) &&
               (!clubValue || player.team === clubValue) &&
               (!fantasyValue || (player.fantasy_team || "Free Agent") === fantasyValue);
    });

    matches.sort(function(a, b) {
        if (sortValue === "name") return a.name.localeCompare(b.name);
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
                '</div>' +
                '<div class="free-agent-comparison">' +
                    '<span class="free-agent-label">Over ' + escapePlayerHTML(player.replace_name) + '</span>' +
                    seasonArrow +
                    formArrow +
                '</div>' +
                '<div class="free-agent-stats">' +
                    '<b>' + player.total_points + '</b><span>Pts</span>' +
                    '<b>' + player.form.toFixed(1) + '</b><span>5GW</span>' +
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
            '<div class="trade-target-reason">Projects ' + Number(t.upgrade || 0).toFixed(2) + ' pts/GW above ' + escapePlayerHTML(t.replace_name) + ' · positional need ' + Number(t.position_need || 0).toFixed(0) + '/100' + clubNote + '</div></div>' +
            '<div class="trade-target-scores"><div class="trade-target-score"><span>Target fit</span><b>' + Number(t.fit_score || 0).toFixed(0) + '</b></div>' +
            '<div class="trade-target-score"><span>Realism</span><b>' + Number(t.realism_score || 0).toFixed(0) + '</b></div>' +
            '<div class="trade-target-score"><span>Projection</span><b>' + Number(t.projection || 0).toFixed(1) + '</b></div></div>' +
            '<div class="trade-target-offer"><span>Comparable outgoing asset</span><b>' + escapePlayerHTML(t.offer_name) + '</b><span>' + Number(t.offer_projection || 0).toFixed(1) + ' projected</span></div>' +
            '</div>';
    });
    html += '</div>';
    wrap.innerHTML = html;
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

function initialiseDashboard() {
    safeInit("page navigation", function() {
        showPage("overview");
    });

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
if ((SEASON_TIMELINE_DATA||[]).length) renderSeasonTimeline(SEASON_TIMELINE_DATA.length-1);
    });

    safeInit("My Team recommendations", function() {
        renderMyTeamFreeAgents();
        renderMyTeamTradeTargets();
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


# ============================================================
# HTML TEMPLATE
# ============================================================

html_template = r"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="utf-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>

<title>
    __LEAGUE_NAME__ — FPL Draft Dashboard
</title>

<style>

__CSS__

</style>

</head>


<body>


<div class="app-shell">


    <!-- ====================================================
         HEADER
         ==================================================== -->

    <header class="header">

        <div class="header-top">

            <div class="logo">
                __LEAGUE_NAME__
                <span>FPL Draft</span>
            </div>


            <div class="global-search-wrap">
                <input id="global-search" class="global-search-input" type="search" placeholder="Search everything — players, managers, charts, pages…" autocomplete="off" oninput="runGlobalSearch()" onfocus="runGlobalSearch()">
                <div id="global-search-results" class="global-search-results"></div>
            </div>

            <div class="header-meta">

                Last updated:
                __LAST_UPDATED__

                <br>

                __FINISHED_COUNT__
                completed gameweeks

            </div>

        </div>


        <nav class="nav">

            <button
                class="nav-button active"
                data-page="overview"
                onclick="showPage('overview')"
            >
                Overview
            </button>


            <button
                class="nav-button"
                data-page="myteam"
                onclick="showPage('myteam')"
            >
                My Team
            </button>


            <button
                class="nav-button"
                data-page="gameweeks"
                onclick="showPage('gameweeks')"
            >
                Gameweeks
            </button>


            <button
                class="nav-button"
                data-page="fixtures"
                onclick="showPage('fixtures')"
            >
                Fixtures
            </button>


            <button
                class="nav-button"
                data-page="players"
                onclick="showPage('players')"
            >
                Players
            </button>


            <button
                class="nav-button"
                data-page="transfers"
                onclick="showPage('transfers')"
            >
                Transfers
            </button>


            <button
                class="nav-button"
                data-page="analytics"
                onclick="showPage('analytics')"
            >
                Analytics
            </button>


            <button
                class="nav-button"
                data-page="draft-centre"
                onclick="showPage('draft-centre')"
            >
                Draft Centre
            </button>


            <button
                class="nav-button"
                data-page="season-summary"
                onclick="showPage('season-summary')"
            >
                Season Summary
            </button>

        </nav>

    </header>


    <main class="main">


        <!-- ==================================================
             OVERVIEW
             ================================================== -->

        <section
            class="page active"
            id="page-overview"
        >

            <div class="page-heading">

                <h1>
                    League Overview
                </h1>

                <p>
                    Head-to-head standings,
                    performance and league trends.
                </p>

            </div>


            <div class="dashboard-grid">

                <div class="card">
                    <h2>Current Standings</h2>
                    __STANDINGS_TABLE__
                </div>

                <div class="card">
                    <h2>Power Rankings</h2>
                    __POWER_RANKINGS_TABLE__
                </div>

            </div>

            <div class="card storyline-card">
                <h2>__HOME_GAME_STATE_TITLE__</h2>
                __HOME_GAME_STATE_PANEL__
            </div>

            <div class="card">
                <h2>Luck Index</h2>
                __LUCK_INDEX_TABLE__
            </div>

            <div class="card">
                <h2>Rest-of-Season Prediction</h2>
                <p class="card-description">A schedule-aware Monte Carlo forecast of the remaining season. Model estimate, not destiny — one monster haul can still make a right bloody mess of it.</p>
                __SEASON_PREDICTION_TABLE__
            </div>

            <div class="card">
                <h2>Finish Probability Matrix</h2>
                __POSITION_PROBABILITY_TABLE__
            </div>

            <div class="card">
                <h2>Squad Pedigree</h2>
                __SQUAD_PEDIGREE_TABLE__
            </div>


            <div class="dashboard-grid">


                <div class="card trend-chart-card">

                    <h2>
                        H2H League Points
                    </h2>

                    <div class="chip-row" id="chips-h2h"></div>
                    <div class="trend-chart-svg-wrap" id="chart-h2h"></div>
                    <div id="legend-h2h"></div>

                </div>


                <div class="card trend-chart-card">

                    <h2>
                        League Position
                    </h2>

                    <div class="chip-row" id="chips-rank"></div>
                    <div class="trend-chart-svg-wrap" id="chart-rank"></div>
                    <div id="legend-rank"></div>

                </div>


                <div class="card trend-chart-card full">

                    <h2>
                        Cumulative Points Scored
                    </h2>

                    <div class="chip-row" id="chips-cumulative"></div>
                    <div class="trend-chart-svg-wrap" id="chart-cumulative"></div>
                    <div id="legend-cumulative"></div>

                </div>

                <div class="card trend-chart-card full">

                    <h2>
                        Points Per Gameweek
                    </h2>

                    <div class="chip-row" id="chips-scores"></div>
                    <div class="trend-chart-svg-wrap" id="chart-scores"></div>
                    <div id="legend-scores"></div>

                </div>


            </div>

        </section>


        <!-- ==================================================
             MY TEAM
             ================================================== -->

        <section
            class="page"
            id="page-myteam"
        >

            <div class="page-heading">

                <h1>
                    My Team
                </h1>

                <p>
                    Your squad, your gameweek-by-gameweek picks,
                    and how your season is trending.
                </p>

            </div>


            <div class="card">
                <div class="my-team-selector-row">
                    <div><h2>My Team</h2><p class="card-description">Choose your team to see your squad and personal league stats.</p></div>
                    <label class="my-team-select-wrap" for="my-team-select"><span>Selected team</span><select id="my-team-select" onchange="changeMyTeam()">__MY_TEAM_OPTIONS__</select></label>
                </div>
                <div id="my-team-cards">__MY_TEAM_CARDS__</div>
            </div>


            <div class="card">

                <h2>
                    Squad By Gameweek
                </h2>

                <p class="card-description">
                    Your starting XI and bench for every captured gameweek —
                    flip back through the season to see who you picked.
                </p>

                <div id="myteam-squad-wrap"></div>

                <div class="results-navigation">

                    <button
                        class="results-button"
                        id="myteam-squad-prev"
                        onclick="changeMyTeamSquadGw(-1)"
                    >
                        ← Previous
                    </button>

                    <div
                        class="results-gw-display"
                        id="myteam-squad-gw-display"
                    >
                        —
                    </div>

                    <button
                        class="results-button"
                        id="myteam-squad-next"
                        onclick="changeMyTeamSquadGw(1)"
                    >
                        Next →
                    </button>

                </div>

            </div>


            <div class="dashboard-grid">

                <div class="card full">
                    <h2>Positional Need</h2>
                    <p class="card-description">How urgently this squad needs help at each position, graded against the other McDraft teams. Red means a genuine weakness; green means you are already stacked. This directly influences trade-target ranking.</p>
                    <div id="myteam-position-needs"></div>
                </div>

                <div class="card">
                    <h2>Free Agents Who Could Improve You</h2>
                    <p class="card-description">
                        Like-for-like recommendations from the current free-agent pool,
                        ranked by season points and recent form.
                    </p>
                    <div id="myteam-free-agents"></div>
                </div>

                <div class="card full">
                    <h2>Realistic Transfer Targets</h2>
                    <p class="card-description">Players owned elsewhere who fit your squad, improve a weak slot and are not completely deranged trade targets. Club concentration is penalised so you do not accidentally build Aston Villa in a fake moustache.</p>
                    <div id="myteam-trade-targets"></div>
                </div>

                <div class="card">
                    <h2>Head-to-Head Record</h2>
                    <div id="myteam-h2h-record"></div>
                </div>

                <div class="card trend-chart-card">
                    <h2>Score By Gameweek</h2>
                    <div class="trend-chart-svg-wrap" id="myteam-chart-scores"></div>
                </div>

                <div class="card trend-chart-card">
                    <h2>League Position By Gameweek</h2>
                    <div class="trend-chart-svg-wrap" id="myteam-chart-rank"></div>
                </div>

            </div>

        </section>


        <!-- ==================================================
             GAMEWEEKS
             ================================================== -->

        <section
            class="page"
            id="page-gameweeks"
        >

            <div class="page-heading">

                <h1>
                    Gameweeks
                </h1>

                <p>
                    A fresh match report, results, Team of the Week and weekly awards.
                </p>

            </div>


            <!-- GAMEWEEK SUMMARY -->

            <div class="card" id="gameweek-summary-card">
                <h2>Gameweek Summary</h2>
                <div class="results-container">
                    __GAMEWEEK_SUMMARY_SECTIONS__
                </div>
            </div>

            <!-- PROJECTED FIXTURE ODDS -->

            <div class="card" id="fixture-odds-card" style="display:none;">
                <div id="upcoming-fixture-odds">
                    <h2>Projected Fixture Odds</h2>
                    __PROJECTED_FIXTURE_ODDS__
                </div>
                <div id="live-fixture-odds" style="display:none;">
                    <h2>Live Win Probabilities</h2>
                    __LIVE_FIXTURE_ODDS__
                </div>
            </div>

            <!-- LIVE AS-IT-STANDS TABLE -->

            __LIVE_AS_IT_STANDS_CARD__

            <!-- RESULTS -->

            <div class="card">

                <h2>
                    Gameweek Results
                </h2>


                <div class="results-container">

                    __RESULTS_SECTIONS__


                    <div class="results-navigation">

                        <button
                            class="results-button"
                            id="results-prev"
                            onclick="changeResults(-1)"
                        >
                            ← Previous
                        </button>


                        <div
                            class="results-gw-display"
                            id="results-gw-display"
                        >
                            GW__LATEST_RESULTS_GW__
                        </div>


                        <button
                            class="results-button"
                            id="results-next"
                            onclick="changeResults(1)"
                        >
                            Next →
                        </button>

                    </div>

                </div>

            </div>


            <!-- FIXTURE XI DRILLDOWN -->
            <div class="fixture-detail-overlay" id="fixture-detail-overlay" hidden aria-hidden="true">
                <div class="fixture-detail-dialog" role="dialog" aria-modal="true" aria-label="Fixture lineups">
                    <button type="button" class="fixture-detail-close" id="fixture-detail-close" aria-label="Close fixture lineups">×</button>
                    <div id="fixture-detail-panels">__FIXTURE_DETAIL_SECTIONS__</div>
                </div>
            </div>

            <!-- TEAM OF THE WEEK -->

            <div class="card" id="totw-card">

                <h2>
                    Team of the Week
                </h2>


                <div class="totw-container">

                    __TOTW_SECTIONS__


                    <div class="totw-navigation">

                        <button
                            class="totw-button"
                            id="totw-prev"
                            onclick="changeTOTW(-1)"
                        >
                            ← Previous
                        </button>


                        <div
                            class="totw-gw-display"
                            id="totw-gw-display"
                        >
                            GW__LATEST_TOTW_GW__
                        </div>


                        <button
                            class="totw-button"
                            id="totw-next"
                            onclick="changeTOTW(1)"
                        >
                            Next →
                        </button>

                    </div>

                </div>

            </div>


            <!-- WEEKLY AWARDS -->

            <div class="card">

                <h2>
                    Weekly Awards
                </h2>

                __AWARDS_TABLE__

            </div>

        </section>


        <!-- ==================================================
             SEASON SUMMARY
             ================================================== -->

        <section class="page" id="page-season-summary">
            <div class="page-heading">
                <h1>Season Summary</h1>
                <p>The story of McDraft, one completed gameweek at a time.</p>
            </div>
            <div class="card">__SEASON_TIMELINE_EXPLORER__</div>
            <div class="card"><h2>Manager of the Month</h2><p class="card-description">Calendar-month honours based on H2H league points, with points scored and wins as tiebreakers. The archive grows through the season.</p><div class="motm-grid">__MANAGERS_OF_MONTH__</div></div>
            <div class="card"><h2>Milestones</h2><p class="card-description">Firsts, scoring landmarks, league-point landmarks and winning streaks. Newest first.</p><div class="milestone-list">__SEASON_MILESTONES__</div></div>
            <div class="card">
                <h2>Season Diary</h2>
                <p class="card-description">Newest first. Each chunky weekly column is built from results, table movement, rivalries, trades, player performances, luck and the following week's fixtures.</p>
                <div class="season-summary-list">__SEASON_SUMMARY__</div>
            </div>
        </section>


        <!-- ==================================================
             FIXTURES
             ================================================== -->
        <section class="page" id="page-fixtures">
            <div class="page-heading"><h1>Fixtures</h1><p>Upcoming schedule, rivalry flags and the runs that look suspiciously pleasant or absolutely horrible.</p></div>
            __FIXTURES_PAGE__
        </section>


        <!-- ==================================================
             PLAYERS
             ================================================== -->

        <section
            class="page"
            id="page-players"
        >

            <div class="page-heading">

                <h1>
                    Players
                </h1>

                <p>
                    Season leaders, form and player ownership history.
                </p>

            </div>


            <div class="card">

                <h2>
                    Top Players
                </h2>

                <div class="top-player-grid">

                    __TOP_PLAYER_CARDS__

                </div>

            </div>


            <div class="card">

                <h2>
                    Top Players By Season Points
                </h2>

                __TOP_PLAYERS_TABLE__

            </div>


            <div class="card">

                <h2>
                    Player Form
                </h2>

                __FORM_TABLE__

            </div>


            <div class="card">

                <div class="player-directory-heading">
                    <div>
                        <h2>Player Directory</h2>
                        <p class="card-description">
                            Search the full player pool and filter by position,
                            Premier League club or your draft fantasy team.
                        </p>
                    </div>
                    <div class="player-directory-count" id="player-directory-count"></div>
                </div>

                <div class="player-filter-grid">
                    <input
                        type="text"
                        id="player-search"
                        class="player-search-box"
                        placeholder="Search player..."
                        oninput="filterPlayers()"
                    />

                    <select id="player-position-filter" class="player-filter" onchange="filterPlayers()">
                        <option value="">All positions</option>
                        <option value="GKP">Goalkeepers</option>
                        <option value="DEF">Defenders</option>
                        <option value="MID">Midfielders</option>
                        <option value="FWD">Forwards</option>
                    </select>

                    <select id="player-club-filter" class="player-filter" onchange="filterPlayers()">
                        <option value="">All clubs</option>
                        __PLAYER_CLUB_OPTIONS__
                    </select>

                    <select id="player-fantasy-filter" class="player-filter" onchange="filterPlayers()">
                        <option value="">All fantasy teams</option>
                        <option value="Free Agent">Free Agents</option>
                        __PLAYER_FANTASY_OPTIONS__
                    </select>

                    <select id="player-sort" class="player-filter" onchange="filterPlayers()">
                        <option value="points">Season points</option>
                        <option value="form">5 GW form</option>
                        <option value="goals">Goals</option>
                        <option value="assists">Assists</option>
                        <option value="name">Name</option>
                    </select>
                </div>

                <div
                    id="player-search-results"
                    class="player-search-results player-directory-results"
                    style="display:block;"
                ></div>

            </div>

        </section>


        <!-- ==================================================
             TRANSFERS
             ================================================== -->
        <section class="page" id="page-transfers">
            <div class="page-heading"><h1>Transfers</h1><p>Waivers, free-agent churn, negotiated deals and a mildly dangerous trade laboratory.</p></div>
            <div class="transfer-subtabs" role="tablist" aria-label="Transfer sections"><button class="transfer-subtab active" type="button" onclick="showTransferSubtab('waivers', this)">Waivers</button><button class="transfer-subtab" type="button" onclick="showTransferSubtab('trades', this)">Trades</button></div>
            <div class="transfer-subpanel active" id="transfer-subpanel-waivers">
              <div class="card"><h2>Latest Waiver Activity · GW__LATEST_TRANSFER_GW__</h2><p class="card-description">A same-gameweek drop and pickup is shown as one completed waiver move.</p>__RECENT_WAIVER_ACTIVITY__</div>
              <div class="card"><h2>Waiver History</h2><p class="card-description">All captured free-agent ins and outs, paired into manager transactions rather than double-counted player legs.</p><div class="player-filter-grid transfer-filter-grid"><select id="waiver-team-filter" class="player-filter" onchange="filterWaivers()"><option value="">All fantasy teams</option>__TRANSFER_TEAM_OPTIONS__</select></div>__WAIVER_ARCHIVE__</div>
              <div class="card"><h2>Most Moved Players</h2>__TRANSFERS_CHART____TRANSFER_TABLE__</div><div class="card"><h2>Players Used By The Most Managers</h2>__TEAM_HOPPERS_CHART__</div><div class="card"><h2>Waiver / Market ROI</h2><p class="card-description">Points gained from post-draft acquisitions minus points subsequently scored by players after they were dropped.</p>__TRANSFER_ROI__</div><div class="card"><h2>Hall of Shame</h2>__ABANDONED_ASSETS__</div><div class="card"><h2>Best Historical Pickups</h2>__BEST_HISTORICAL_TRANSFERS__</div>
            </div>
            <div class="transfer-subpanel" id="transfer-subpanel-trades">
              <div class="card">__TRADE_SIMULATOR__</div><div class="card"><h2>Recent League Trades · GW__LATEST_TRANSFER_GW__</h2><p class="card-description">Negotiated manager-to-manager trades only.</p>__TRADES_TABLE__</div><div class="card"><h2>Historical Trades</h2><div class="player-filter-grid transfer-filter-grid"><select id="historical-trade-team-filter" class="player-filter" onchange="filterHistoricalTrades()"><option value="">All fantasy teams</option>__TRANSFER_TEAM_OPTIONS__</select></div>__HISTORICAL_TRADES__</div>
            </div>
        </section>


        <!-- ==================================================
             DRAFT CENTRE
             ================================================== -->
        <section class="page" id="page-draft-centre">
            <div class="page-heading"><h1>Draft Centre</h1><p>The original draft board, re-ranked by reality: steals, busts, retention, round value and a live redraft.</p></div>
            __DRAFT_CENTRE__
        </section>


        <!-- ==================================================
             ANALYTICS LAB
             ================================================== -->
        <section class="page" id="page-analytics">
            <div class="page-heading"><h1>Analytics Lab</h1><p>Thirty-plus views of performance, luck, squad construction, the market and all the other numbers that can ruin a perfectly civil group chat.</p></div>
            __ANALYTICS_PAGE__
        </section>


    </main>

</div>


<script>

__JAVASCRIPT__

</script>


</body>

</html>
"""


# ============================================================
# REPLACE PLACEHOLDERS
# ============================================================

# JSON is embedded inside a <script> block. Escape characters that can
# accidentally terminate that block (for example a player/team name
# containing </script>) while keeping the values valid JavaScript.
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

    "__STANDINGS_TABLE__":
        standings_table(),

    "__POWER_RANKINGS_TABLE__":
        power_rankings_table(),

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

    "__CSS__":
        css,

    "__JAVASCRIPT__":
        javascript.replace(
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
            "__FREE_AGENT_RECOMMENDATIONS__",
            safe_js_json(free_agent_recommendations_json)
        ).replace(
            "__H2H_RECORDS__",
            safe_js_json(h2h_records_json)
        ).replace(
            "__TRADE_TARGETS__",
            safe_js_json(trade_targets_json)
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
