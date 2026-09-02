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

        owners_now = info["ownership_by_gw"].get(
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
        ownership = info["ownership_by_gw"]

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


for player_id, info in (
    player_ownership.items()
):

    player_meta = elements.get(
        player_id,
        {}
    )

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
                info[
                    "ownership_by_gw"
                ].get(
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

    rows = ""

    for position, manager in enumerate(power_rankings, start=1):

        league_position = manager_current_rank.get(manager, position)
        movement = league_position - position

        if movement > 0:
            movement_html = f'<span class="rank-up">↑ {movement}</span>'
        elif movement < 0:
            movement_html = f'<span class="rank-down">↓ {abs(movement)}</span>'
        else:
            movement_html = '<span class="rank-flat">—</span>'

        safe_manager = escape_html(manager)

        rows += f"""
            <tr>
                <td class="rank-cell">{position}</td>
                <td class="manager-name">{safe_manager}</td>
                <td>{movement_html}</td>
            </tr>
        """

    return f"""
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Manager</th>
                        <th>vs League Table</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    """


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

        margins = []
        for match in results_by_gw.get(gw, []):
            margins.append(abs(match["score1"] - match["score2"]))

        biggest_margin = max(margins) if margins else 0
        closest_margin = min(margins) if margins else 0

        display_mode = "block" if index == len(finished_gws) - 1 else "none"

        sections += f'''
            <div class="gw-summary-slide" id="summary-gw-{gw}" style="display:{display_mode};">
                <div class="gw-summary-grid">
                    <div class="summary-stat"><span>Highest Score</span><strong>{escape_html(highest[0])}</strong><b>{highest[1]}</b></div>
                    <div class="summary-stat"><span>Lowest Score</span><strong>{escape_html(lowest[0])}</strong><b>{lowest[1]}</b></div>
                    <div class="summary-stat"><span>League Average</span><strong>{average:.1f}</strong><b>pts</b></div>
                    <div class="summary-stat"><span>Biggest Win</span><strong>{biggest_margin}</strong><b>point margin</b></div>
                    <div class="summary-stat"><span>Closest Game</span><strong>{closest_margin}</strong><b>point margin</b></div>
                </div>
            </div>
        '''

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
# RESULTS HTML
# ============================================================

results_sections = ""


for index, gw in enumerate(
    result_gameweeks
):

    display_mode = (
        "block"
        if index == len(
            result_gameweeks
        ) - 1
        else "none"
    )

    fixtures_html = ""

    for fixture in (
        results_by_gw[gw]
    ):

        team1_class = ""
        team2_class = ""

        if fixture["result"] == "win1":

            team1_class = "winner"
            team2_class = "loser"

        elif fixture["result"] == "win2":

            team1_class = "loser"
            team2_class = "winner"

        else:

            team1_class = "draw"
            team2_class = "draw"

        fixtures_html += f"""
            <div class="fixture">

                <div class="fixture-team {team1_class}">

                    <span class="fixture-manager">
                        {escape_html(fixture["team1"])}
                    </span>

                    <span class="fixture-score">
                        {fixture["score1"]}
                    </span>

                </div>

                <div class="fixture-vs">
                    VS
                </div>

                <div class="fixture-team {team2_class}">

                    <span class="fixture-score">
                        {fixture["score2"]}
                    </span>

                    <span class="fixture-manager">
                        {escape_html(fixture["team2"])}
                    </span>

                </div>

            </div>
        """

    results_sections += f"""
        <div
            class="results-slide"
            id="results-gw-{gw}"
            style="display:{display_mode};"
        >

            <div class="results-title">
                Gameweek {gw}
            </div>

            <div class="fixtures-list">
                {fixtures_html}
            </div>

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

}
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

    const newIndex =
        totwIndex +
        direction;


    if (
        newIndex < 0 ||
        newIndex >=
            totwGameweeks.length
    ) {

        return;

    }


    totwIndex =
        newIndex;


    updateTOTW();

}


/* ============================================================
   RESULTS
   ============================================================ */

const resultsGameweeks =
    __RESULT_GAMEWEEKS__;


let resultsIndex =
    resultsGameweeks.length - 1;


function updateResults() {

    if (
        resultsGameweeks.length === 0
    ) {

        return;

    }


    resultsGameweeks.forEach(
        function(gw) {

            const slide =
                document.getElementById(
                    "results-gw-" + gw
                );


            if (slide) {

                slide.style.display =
                    "none";

            }

        }
    );


    const selectedGW =
        resultsGameweeks[
            resultsIndex
        ];


    const summarySlides =
        document.querySelectorAll(
            ".gw-summary-slide"
        );

    summarySlides.forEach(
        function(slide) {
            slide.style.display = "none";
        }
    );

    const selectedSummary =
        document.getElementById(
            "summary-gw-" + selectedGW
        );

    if (selectedSummary) {
        selectedSummary.style.display = "block";
    }


    const selectedSlide =
        document.getElementById(
            "results-gw-" + selectedGW
        );


    if (selectedSlide) {

        selectedSlide.style.display =
            "block";

    }


    const display =
        document.getElementById(
            "results-gw-display"
        );


    if (display) {

        display.innerText =
            "GW" + selectedGW;

    }


    const prev =
        document.getElementById(
            "results-prev"
        );


    const next =
        document.getElementById(
            "results-next"
        );


    if (prev) {

        prev.disabled =
            resultsIndex === 0;

    }


    if (next) {

        next.disabled =
            resultsIndex ===
            resultsGameweeks.length - 1;

    }

}


function changeResults(
    direction
) {

    const newIndex =
        resultsIndex +
        direction;


    if (
        newIndex < 0 ||
        newIndex >=
            resultsGameweeks.length
    ) {

        return;

    }


    resultsIndex =
        newIndex;


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


function searchPlayers() {

    const input =
        document.getElementById(
            "player-search"
        );


    const results =
        document.getElementById(
            "player-search-results"
        );


    const query =
        input.value
            .trim()
            .toLowerCase();


    if (
        query.length < 2
    ) {

        results.style.display =
            "none";

        results.innerHTML =
            "";

        return;

    }


    const matches =
        playerSearchData
            .filter(
                function(player) {

                    return player.name
                        .toLowerCase()
                        .includes(query);

                }
            )
            .slice(
                0,
                10
            );


    if (
        matches.length === 0
    ) {

        results.style.display =
            "block";

        results.innerHTML =
            "<div class='notice'>No players found.</div>";

        return;

    }


    results.style.display =
        "block";


    let searchHtml = "";


    matches.forEach(
        function(player) {

            searchHtml +=
                '<div class="player-history-card">';


            searchHtml +=
                '<div class="player-history-title">' +
                escapePlayerHTML(
                    player.name
                ) +
                '</div>';


            searchHtml +=
                '<div class="player-meta">' +
                escapePlayerHTML(player.position) +
                ' · ' +
                escapePlayerHTML(player.team) +
                ' · Used by ' +
                player.owners.length +
                ' different managers' +
                ' · ' +
                player.transfers +
                ' transfers' +
                '</div>';


            searchHtml +=
                '<div class="player-stat-chips">' +
                '<span class="player-stat-chip"><b>' + player.goals + '</b> Goals</span>' +
                '<span class="player-stat-chip"><b>' + player.assists + '</b> Assists</span>' +
                '<span class="player-stat-chip"><b>' + player.clean_sheets + '</b> Clean Sheets</span>' +
                '<span class="player-stat-chip"><b>' + player.defensive_contributions + '</b> Def. Contributions</span>' +
                '<span class="player-stat-chip"><b>' + player.bonus + '</b> Bonus</span>' +
                '<span class="player-stat-chip"><b>' + player.saves + '</b> Saves</span>' +
                '<span class="player-stat-chip"><b>' + player.goals_conceded + '</b> Conceded</span>' +
                '<span class="player-stat-chip"><b>' + player.minutes + '</b> Mins</span>' +
                '<span class="player-stat-chip"><b>' + player.yellow_cards + '</b> Yellow</span>' +
                '<span class="player-stat-chip"><b>' + player.red_cards + '</b> Red</span>' +
                '</div>';


            searchHtml +=
                '<div class="player-history-chart-heading">Score By Gameweek</div>' +
                '<div class="player-gw-chart-wrap trend-chart-svg-wrap">' +
                buildPlayerHistoryChart(player.history) +
                '</div>';


            searchHtml +=
                '<div class="player-gw-table">' +
                '<table>' +
                '<thead>' +
                '<tr>' +
                '<th>GW</th>' +
                '<th>Manager(s)</th>' +
                '<th>Points</th>' +
                '</tr>' +
                '</thead>' +
                '<tbody>';


            player.history.forEach(
                function(row) {

                    const ownerNames =
                        row.owners.length
                        ? row.owners
                            .map(
                                escapePlayerHTML
                            )
                            .join(
                                ", "
                            )
                        : "Not owned";


                    searchHtml +=
                        '<tr>' +
                        '<td>GW' +
                        row.gw +
                        '</td>' +
                        '<td>' +
                        ownerNames +
                        '</td>' +
                        '<td>' +
                        row.points +
                        '</td>' +
                        '</tr>';

                }
            );


            searchHtml +=
                '</tbody>' +
                '</table>' +
                '</div>' +
                '</div>';

        }
    );


    results.innerHTML =
        searchHtml;

}


/* ============================================================
   INITIALISE
   ============================================================ */

initialiseMyTeam();

updateTOTW();

updateResults();

changeMyTeam();

initAllTrendCharts();

showPage(
    "overview"
);

window.addEventListener(
    "resize",
    resizeCharts
);

setTimeout(
    resizeCharts,
    150
);
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
                    Results, Team of the Week and weekly awards.
                </p>

            </div>


            <!-- GAMEWEEK SUMMARY -->

            <div class="card">
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

            <div class="card">

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

                <h2>
                    Player History
                </h2>


                <input
                    type="text"
                    id="player-search"
                    class="player-search-box"
                    placeholder="Search for a player..."
                    oninput="searchPlayers()"
                />


                <div
                    id="player-search-results"
                    class="player-search-results"
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

    "__STANDINGS_TABLE__":
        standings_table(),

    "__POWER_RANKINGS_TABLE__":
        power_rankings_table(),

    "__GAMEWEEK_SUMMARY_SECTIONS__":
        gameweek_summary_sections(),

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
            json.dumps(
                finished_gws
            )
        ).replace(
            "__RESULT_GAMEWEEKS__",
            json.dumps(
                result_gameweeks
            )
        ).replace(
            "__PLAYER_SEARCH_DATA__",
            player_search_json
        ).replace(
            "__DEFAULT_MY_TEAM_INDEX__",
            str(default_my_team_index())
        ).replace(
            "__MY_TEAM_HISTORY_DATA__",
            my_team_history_json
        ).replace(
            "__CHART_H2H_DATA__",
            chart_h2h_json
        ).replace(
            "__CHART_RANK_DATA__",
            chart_rank_json
        ).replace(
            "__CHART_SCORES_DATA__",
            chart_scores_json
        ).replace(
            "__MANAGER_ORDER__",
            manager_order_json
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
