# Generated from: Scraper.ipynb
# Converted at: 2026-09-01T09:07:10.758Z
# Next step (optional): refactor into modules & generate tests with RunCell
# Quick start: pip install runcell

# DRAFT SCRAPER


import requests
import json
import os
import time
from datetime import datetime, timezone

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

latest_transfer_gw = max(finished_gws) if finished_gws else None


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
        return '<div class="notice">No completed gameweeks yet.</div>'

    rows_data = [row for row in transfer_movements if row["gw"] == latest_transfer_gw]
    if not rows_data:
        return f'<div class="notice">No ownership changes recorded for GW{latest_transfer_gw}.</div>'

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
# POWER RANKINGS
#
# Deliberately excludes actual results (league points, W-D-L) -
# the point is a ranking that can disagree with the real table.
# Each component is min-max normalised to 0-100 within the league
# so it stays relative to this league's own spread rather than an
# arbitrary fixed scale:
#
#   Recent Form      (40%) - average of the last 5 gw_scores entries
#                             (fewer early in the season - same
#                             graceful degradation used elsewhere)
#   Season Quality   (35%) - avg_points, the season-to-date average
#   Squad Management (25%) - average selection efficiency
#
# Only the resulting rank position is surfaced on the dashboard,
# not the underlying score - this is an editorial "who's actually
# playing well" call, not a stat with a defensible absolute value.

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

power_score = {
    manager: (
        norm_recent_form.get(manager, 0) * 0.40
        + norm_season_quality.get(manager, 0) * 0.35
        + norm_squad_management.get(manager, 0) * 0.25
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


def trades_table(gw=None):
    trades_to_show = normalised_trades
    if gw is not None:
        trades_to_show = [
            trade for trade in normalised_trades
            if str(trade.get("gw")) == str(gw)
        ]

    if not trades_to_show:
        return """
            <div class="notice">
                No trades returned by the Draft API yet.
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

        rows += f"""
            <div class="trade-card">
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
                <td>{movement_html}</td>
            </tr>
        '''

    return f'''
        <div class="power-formula">
            <b>Power score:</b> 40% recent 5GW scoring + 35% season scoring quality + 25% squad-management efficiency. Every component is normalised 0–100 within this league.
        </div>
        <div class="table-wrap">
            <table>
                <thead><tr><th>#</th><th>Manager</th><th>Power</th><th>5GW Form</th><th>Season</th><th>Management</th><th>vs Table</th></tr></thead>
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


def _ordinal_suffix(n):
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


def season_summary_html():
    if not finished_gws:
        return '<div class="notice">No completed gameweeks yet.</div>'
    blocks = []
    for gw in sorted(finished_gws, reverse=True):
        story = league_storyline_for_gw(gw)
        blocks.append('<article class="season-story"><div class="season-story-gw">GW' + str(gw) + '</div><div><p>' + escape_html(story) + '</p></div></article>')
    return ''.join(blocks)


def future_fixture_sections():
    last_finished = max(finished_gws) if finished_gws else 0
    future_gws = sorted(gw for gw in full_fixture_schedule if gw > last_finished)
    if not future_gws:
        return '<div class="notice">No future fixtures available yet.</div>'
    sections = []
    for index, gw in enumerate(future_gws):
        rows = []
        for fixture in full_fixture_schedule[gw]:
            derby = _derby_name(fixture["team1"], fixture["team2"])
            derby_html = f'<div class="fixture-derby">{escape_html(derby)}</div>' if derby else ''
            rows.append(
                '<div class="future-fixture-row">'
                f'<div class="future-fixture-team home">{escape_html(fixture["team1"])}</div>'
                f'<div class="future-fixture-v">vs{derby_html}</div>'
                f'<div class="future-fixture-team">{escape_html(fixture["team2"])}</div>'
                '</div>'
            )
        display = "block" if index == 0 else "none"
        sections.append(f'<div class="future-fixture-slide" id="future-gw-{gw}" style="display:{display};">{"".join(rows)}</div>')
    return ''.join(sections)


future_fixture_gameweeks = sorted(gw for gw in full_fixture_schedule if gw > (max(finished_gws) if finished_gws else 0))
gameweek_browser_gameweeks = sorted(set(result_gameweeks) | set(full_fixture_schedule.keys()))

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
                    <span><b>{manager_transfer_in.get(manager, 0) + manager_transfer_out.get(manager, 0)}</b> transfers</span>
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


# ============================================================
# RESULTS / FIXTURE BROWSER HTML
# ============================================================

results_sections = ""
latest_completed_for_browser = max(result_gameweeks) if result_gameweeks else None

for gw in gameweek_browser_gameweeks:
    display_mode = "block" if gw == latest_completed_for_browser else "none"
    fixtures_html = ""

    if gw in results_by_gw:
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
            fixtures_html += f"""
                <div class="fixture">
                    {derby_html}
                    <div class="fixture-team {team1_class}">
                        <span class="fixture-manager">{escape_html(fixture["team1"])}</span>
                        <span class="fixture-score">{fixture["score1"]}</span>
                    </div>
                    <div class="fixture-vs">VS</div>
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
        title = f"Gameweek {gw} · Upcoming Fixtures"
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
# PAGE DATA
# ============================================================

latest_results_gw = (
    result_gameweeks[-1]
    if result_gameweeks
    else None
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
    renderMyTeamFreeAgents();
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
    scores: __CHART_SCORES_DATA__
};

const TREND_CONFIG = {
    h2h: { invert: true, fixedRange: null, deltaGood: "up" },
    rank: { invert: false, fixedRange: null, deltaGood: "down" },
    scores: { invert: true, fixedRange: null, deltaGood: "up" }
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
    ["h2h", "rank", "scores"].forEach(initTrendChart);

    window.addEventListener("resize", function() {
        // SVG scales via viewBox automatically; nothing to recompute.
    });
}


/* ============================================================
   MY TEAM — SQUAD BY GAMEWEEK + PERSONAL TREND CHARTS
   ============================================================ */

const MY_TEAM_HISTORY = __MY_TEAM_HISTORY_DATA__;

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
let resultsIndex = latestCompletedGameweek !== null ? resultsGameweeks.indexOf(latestCompletedGameweek) : 0;
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

    safeInit("My Team charts", function() {
        renderMyTeamStatsCharts();
    });

    safeInit("trend charts", function() {
        initAllTrendCharts();
    });

    safeInit("My Team recommendations", function() {
        renderMyTeamFreeAgents();
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
                data-page="season-summary"
                onclick="showPage('season-summary')"
            >
                Season Summary
            </button>


            <button
                class="nav-button"
                data-page="stats"
                onclick="showPage('stats')"
            >
                Stats
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
                    <p class="card-description">Recent form, season quality and squad management — not the actual results. This can disagree with the table above on purpose.</p>
                    __POWER_RANKINGS_TABLE__
                </div>

            </div>

            <div class="card storyline-card">
                <h2>This Week in McDraft</h2>
                <p class="card-description">A dramatic league column: table swings, rivalries, trades, luck, player disasters and what comes next. The factual recap remains on Gameweeks.</p>
                __LATEST_LEAGUE_STORYLINE__
            </div>

            <div class="card">
                <h2>Luck Index</h2>
                __LUCK_INDEX_TABLE__
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

                <div class="card">
                    <h2>Free Agents Who Could Improve You</h2>
                    <p class="card-description">
                        Like-for-like recommendations from the current free-agent pool,
                        ranked by season points and recent form.
                    </p>
                    <div id="myteam-free-agents"></div>
                </div>

                <div class="card">
                    <h2>Head-to-Head Record</h2>
                    <p class="card-description">
                        Your record against every other manager in the league.
                    </p>
                    <div id="myteam-h2h-record"></div>
                </div>

                <div class="card trend-chart-card">
                    <h2>Score By Gameweek</h2>
                    <p class="card-description">Your points, gameweek by gameweek.</p>
                    <div class="trend-chart-svg-wrap" id="myteam-chart-scores"></div>
                </div>

                <div class="card trend-chart-card">
                    <h2>League Position By Gameweek</h2>
                    <p class="card-description">Where you've sat in the table over the season.</p>
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
            <div class="card">
                <h2>Season Diary</h2>
                <p class="card-description">Newest first. Each chunky weekly column is built from results, table movement, rivalries, trades, player performances, luck and the following week's fixtures.</p>
                <div class="season-summary-list">__SEASON_SUMMARY__</div>
            </div>
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

        <section
            class="page"
            id="page-transfers"
        >

            <div class="page-heading">

                <h1>
                    Transfers
                </h1>

                <p>
                    Ownership changes, manager hopping and transfer disasters.
                </p>

            </div>


            <div class="card">

                <h2>Recent Transfers · GW__LATEST_TRANSFER_GW__</h2>
                <p class="card-description">
                    Ownership moves effective for the latest completed gameweek. A GW2 pickup is counted as owned from GW2.
                </p>
                __RECENT_TRANSFER_ACTIVITY__

            </div>


            <div class="card">

                <h2>Search Transfer History</h2>
                <p class="card-description">
                    Search every captured ownership move by player or fantasy team.
                </p>
                <div class="player-filter-grid transfer-filter-grid">
                    <input id="transfer-player-search" class="player-search-box" type="search" placeholder="Search player…" oninput="filterTransfers()">
                    <select id="transfer-team-filter" class="player-filter" onchange="filterTransfers()">
                        <option value="">All fantasy teams</option>
                        __TRANSFER_TEAM_OPTIONS__
                    </select>
                </div>
                __TRANSFER_ARCHIVE__

            </div>


            <div class="card">

                <h2>Recent League Trades</h2>
                <p class="card-description">
                    Negotiated trades processed for GW__LATEST_TRANSFER_GW__, with running grades counting points from that GW onward.
                </p>
                __TRADES_TABLE__

            </div>


            <div class="card">

                <h2>
                    Most Transferred Players
                </h2>

                __TRANSFERS_CHART__

                __TRANSFER_TABLE__

            </div>


            <div class="card">

                <h2>
                    Players Used By The Most Managers
                </h2>

                __TEAM_HOPPERS_CHART__

            </div>


            <div class="card">

                <h2>
                    Transfer Market ROI
                </h2>

                <p class="card-description">
                    Points scored by players picked up after the draft,
                    minus points scored by players after they were dropped.
                </p>

                __TRANSFER_ROI__

            </div>


            <div class="card">

                <h2>
                    Transfer Hall of Shame
                </h2>

                <p class="card-description">
                    Players who were dropped and subsequently
                    scored points for the rest of the captured period.
                </p>

                __ABANDONED_ASSETS__

            </div>


            <div class="card">

                <h2>Best Historical Transfers</h2>
                <p class="card-description">
                    The best post-draft pickups so far, ranked by points delivered while the player was actually on that fantasy roster.
                    Acquisition-gameweek points are included.
                </p>
                __BEST_HISTORICAL_TRANSFERS__

            </div>

        </section>


        <!-- ==================================================
             STATS
             ================================================== -->

        <section
            class="page"
            id="page-stats"
        >

            <div class="page-heading">

                <h1>
                    League Stats
                </h1>

                <p>
                    The numbers nobody asked for but everybody needs.
                </p>

            </div>


            <div class="card">

                <h2>
                    Fun Stats
                </h2>

                __FUN_STATS__

            </div>


            <div class="card">
                <h2>Manager Profiles</h2>
                <div class="manager-profile-grid">
                    __MANAGER_PROFILE_CARDS__
                </div>
            </div>

            <div class="card">

                <h2>
                    League Records
                </h2>
                <div class="records-grid">
                    __LEAGUE_RECORDS__
                </div>
            </div>

            <div class="card">

                <h2>
                    League Summary
                </h2>


                <div class="stats-grid">

                    <div class="stat-card">

                        <div class="stat-label">
                            Managers
                        </div>

                        <div class="stat-value">
                            __MANAGER_COUNT__
                        </div>

                        <div class="stat-description">
                            Active league managers
                        </div>

                    </div>


                    <div class="stat-card">

                        <div class="stat-label">
                            Completed Gameweeks
                        </div>

                        <div class="stat-value">
                            __FINISHED_COUNT__
                        </div>

                        <div class="stat-description">
                            Gameweeks captured
                        </div>

                    </div>


                    <div class="stat-card">

                        <div class="stat-label">
                            Players Analysed
                        </div>

                        <div class="stat-value">
                            __PLAYER_COUNT__
                        </div>

                        <div class="stat-description">
                            Players appearing in the draft
                        </div>

                    </div>


                    <div class="stat-card">

                        <div class="stat-label">
                            Fixtures
                        </div>

                        <div class="stat-value">
                            __FIXTURE_COUNT__
                        </div>

                        <div class="stat-description">
                            Completed H2H fixtures
                        </div>

                    </div>

                </div>

            </div>

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

html = html_template

replacements = {

    "__LEAGUE_NAME__":
        escape_html(
            league_name
        ),

    "__LAST_UPDATED__":
        escape_html(
            history.get(
                "last_updated",
                ""
            )
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

    "__STANDINGS_TABLE__":
        standings_table(),

    "__POWER_RANKINGS_TABLE__":
        power_rankings_table(),

    "__LUCK_INDEX_TABLE__":
        luck_index_table(),

    "__LATEST_LEAGUE_STORYLINE__":
        latest_league_storyline_html(),

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

    "__RESULTS_SECTIONS__":
        results_sections,

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
            "__PLAYER_SEARCH_DATA__",
            safe_js_json(player_search_json)
        ).replace(
            "__FREE_AGENT_RECOMMENDATIONS__",
            safe_js_json(free_agent_recommendations_json)
        ).replace(
            "__H2H_RECORDS__",
            safe_js_json(h2h_records_json)
        ).replace(
            "__DEFAULT_MY_TEAM_INDEX__",
            str(default_my_team_index())
        ).replace(
            "__MY_TEAM_HISTORY_DATA__",
            safe_js_json(my_team_history_json)
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
            "__MANAGER_ORDER__",
            safe_js_json(manager_order_json)
        )

}


for placeholder, value in replacements.items():

    html = html.replace(
        placeholder,
        value
    )


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
    "  5. Stats"
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
