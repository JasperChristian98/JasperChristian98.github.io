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


classic_elements_by_fpl_id = {
    int(p["id"]): p for p in bootstrap.get("elements", [])
}
elements = make_draft_keyed_elements(classic_elements_by_fpl_id, draft_elements_by_id)


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

# Live FPL status, probability estimates and dated audit snapshots.
# Retain the original player news verbatim: return-date prose is NOT treated
# as a confirmed medical clearance date.
_fpl_availability = {}
for _pid, _meta in elements.items():
    _fpl_availability[int(_pid)] = {
        "status": str(_meta.get("status") or "a"),
        "chance_next": _meta.get("chance_of_playing_next_round"),
        "chance_this": _meta.get("chance_of_playing_this_round"),
        "news": str(_meta.get("news") or "").strip(),
        "news_updated": _meta.get("news_added") or None,
    }
_availability_snapshots = history.setdefault("fpl_availability_snapshots", {})
_availability_stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
_availability_snapshots[_availability_stamp] = {
    str(_pid): row for _pid, row in _fpl_availability.items()
    if row["status"] != "a" or row["news"] or row["chance_next"] not in (None, 100)
}
# Cap storage: these snapshots are for retrospective forecast audits, not a
# second unbounded player-history database.
for _old_stamp in sorted(_availability_snapshots)[:-180]:
    del _availability_snapshots[_old_stamp]


# ============================================================
# OFFICIAL FPL DRAFT RANK
# ============================================================
# The Draft site publishes its own preseason player ordering via
# draft.premierleague.com/api/bootstrap-static. Keep that separate from the
# actual McDraft pick order, then blend the two only where we want a pedigree
# prior (predictions, trade value, squad-strength analytics).
#
# McDraft actual pick = 60%
# Official FPL Draft rank = 40%
#
# The raw McDraft pick remains untouched for Draft Centre/history.

OFFICIAL_DRAFT_WEIGHT = 0.40
MCDRAFT_DRAFT_WEIGHT = 0.60

# Cached above: this same Draft bootstrap defined the canonical Draft pool.

official_fpl_draft_rank = history.setdefault("official_fpl_draft_rank", {})
for _pid, _row in draft_elements_by_id.items():
    _rank = _row.get("draft_rank")
    try:
        _rank = int(_rank)
    except (TypeError, ValueError):
        continue
    if _rank <= 0:
        continue
    # Preserve the first official rank captured so this remains a preseason
    # pedigree signal even if the upstream site later changes its ordering.
    official_fpl_draft_rank.setdefault(str(_pid), _rank)

history["official_fpl_draft_rank"] = official_fpl_draft_rank

def _league_draft_rank(player_id):
    info = history.get("original_draft_rank", {}).get(str(player_id), {}) or {}
    try:
        rank = int(info.get("overall_pick", UNDRAFTED_PLAYER_RANK))
    except (TypeError, ValueError):
        rank = UNDRAFTED_PLAYER_RANK
    return min(max(rank, 1), UNDRAFTED_PLAYER_RANK)

def _official_draft_rank(player_id):
    try:
        rank = int((history.get("official_fpl_draft_rank", {}) or {}).get(str(player_id)))
    except (TypeError, ValueError):
        return None
    if rank <= 0:
        return None
    # McDraft is a 150-player board, so map anything below that cutoff to the
    # same explicit replacement/undrafted floor used by the existing model.
    return min(rank, UNDRAFTED_PLAYER_RANK)

def _blended_draft_rank(player_id):
    league_rank = _league_draft_rank(player_id)
    official_rank = _official_draft_rank(player_id)
    if official_rank is None:
        return float(league_rank)
    return (MCDRAFT_DRAFT_WEIGHT * league_rank) + (OFFICIAL_DRAFT_WEIGHT * official_rank)


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

# Full Premier League schedule used by the fixture-aware projection engine.
# The per-GW endpoint above remains useful for live-state detection; this full
# schedule lets future player/squad forecasts change with the actual PL run-in.
_all_pl_fixtures = fetch_json(
    f"{CLASSIC_BASE}/fixtures/"
) or []

_pl_fixtures_by_event_team = defaultdict(list)
for _fx in _all_pl_fixtures:
    if not isinstance(_fx, dict):
        continue
    _event = _fx.get("event")
    _home = _fx.get("team_h")
    _away = _fx.get("team_a")
    if _event is None or _home is None or _away is None:
        continue
    try:
        _event = int(_event); _home = int(_home); _away = int(_away)
    except (TypeError, ValueError):
        continue
    _pl_fixtures_by_event_team[(_event, _home)].append({
        "opponent": _away, "is_home": True, "fixture": _fx
    })
    _pl_fixtures_by_event_team[(_event, _away)].append({
        "opponent": _home, "is_home": False, "fixture": _fx
    })

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
        f"{CLASSIC_BASE}/element-summary/{fpl_id_for_draft(player_id)}/"
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

    from collections import defaultdict as _defaultdict
    _round_rows = _defaultdict(list)
    for row in history_data:
        if row.get("round") is not None:
            _round_rows[int(row["round"])].append(row)

    for gw, fixture_rows in _round_rows.items():
        pinned = get_pinned_player_gw_record(player_id, gw)
        if pinned is not None:
            points_by_gw[gw] = pinned["points"]
            minutes_by_gw[gw] = pinned["minutes"]
            opponent_by_gw[gw] = pinned.get("opponent", "")
            was_home_by_gw[gw] = pinned.get("was_home", False)
        else:
            # A double GW has multiple element-summary rows; sum them rather
            # than silently using just the last fixture's score.
            points_by_gw[gw] = sum(int(row.get("total_points", 0) or 0) for row in fixture_rows)
            minutes_by_gw[gw] = sum(int(row.get("minutes", 0) or 0) for row in fixture_rows)
            opponent_by_gw[gw] = " + ".join(
                teams_lookup.get(row.get("opponent_team"), "")
                for row in fixture_rows
            )
            was_home_by_gw[gw] = fixture_rows[0].get("was_home", False)

        player_scores.setdefault(str(player_id), {})[str(gw)] = {
            "points": points_by_gw[gw],
            "minutes": minutes_by_gw[gw],
            "opponent": opponent_by_gw[gw],
            "was_home": was_home_by_gw[gw],
            "fpl_player_id": fpl_id_for_draft(player_id),
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

# Repair scores and minutes in frozen historical picks for MANUALLY mapped
# players. Match winners / Draft official live_points remain authoritative.
_corrected_picks = 0
_mapped_live_cache = {}
for _gw_text, _snapshot in history.get("gameweeks", {}).items():
    _gw = int(_gw_text)
    for _squad in _snapshot.get("teams", {}).values():
        _changed = False
        for _pick in _squad.get("starters", []) + _squad.get("bench", []):
            _did = int(_pick.get("element_id") or 0)
            if _did not in PLAYER_ID_MAP:
                continue
            _resolved = player_history.get(_did, {})
            if _gw not in _resolved.get("points", {}):
                # Correct identity remains visible; do not replace unavailable
                # historical stats with an invented zero.
                continue
            _pick["points"] = _resolved["points"][_gw]
            _pick["minutes"] = _resolved["minutes"].get(_gw, _pick.get("minutes", 0))
            _historical_live = get_live_gw_data(_gw)
            if _did in _historical_live:
                _pick["in_dreamteam"] = _historical_live[_did].get("in_dreamteam", False)
            _pick["fpl_player_id"] = PLAYER_ID_MAP[_did]
            _changed = True
            _corrected_picks += 1
        if _changed:
            _squad["gw_points"] = sum(
                float(p.get("points", 0) or 0) * (2 if p.get("is_captain") else 1)
                for p in _squad.get("starters", [])
            )
            _squad["bench_points"] = sum(
                float(p.get("points", 0) or 0) for p in _squad.get("bench", [])
            )
            _squad["dreamteam_starters"] = sum(
                bool(p.get("in_dreamteam")) for p in _squad.get("starters", [])
            )
print(f"Reconciled {_corrected_picks} mapped historical player appearances")


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

