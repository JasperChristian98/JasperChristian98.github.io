# Enhanced McDraft dashboard v53 — interactive Monte Carlo season simulator
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
import csv
import unicodedata

# ============================================================
# CONFIG
# ============================================================

LEAGUE_ID = 17288
HISTORY_FILE = "fpl_draft_history.json"

DRAFT_BASE = "https://draft.premierleague.com/api"
CLASSIC_BASE = "https://fantasy.premierleague.com/api"

# ============================================================
# CSV SOURCE OF TRUTH: DRAFT PLAYER ID -> CLASSIC FPL PLAYER ID
# ============================================================
# The Draft API owns roster / transfer / draft IDs; the Classic API owns
# player metadata, fitness, gameweek stats and projections. Those IDs are
# NOT guaranteed to identify the same real person.
# Put manual corrections in draft_player_mapping.csv next to this script.
# The audit CSV is REGENERATED on each build; never edit it as the source.
MAPPING_CSV = os.environ.get(
    "DRAFT_PLAYER_MAPPING_CSV",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "draft_player_mapping.csv"),
)
MAPPING_AUDIT_CSV = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "draft_player_mapping_audit.csv"
)


def load_draft_player_mapping(path):
    if not os.path.isfile(path):
        print(f"WARNING: {path} not found; using matching numeric IDs. "
              "Add draft_player_mapping.csv to correct mismatches.")
        return {}
    mapping = {}
    reverse = {}
    with open(path, newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        required = {"draft_player_id", "fpl_player_id"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError(f"{path}: CSV requires draft_player_id,fpl_player_id columns")
        for line, row in enumerate(reader, start=2):
            draft_text = str(row.get("draft_player_id") or "").strip()
            fpl_text = str(row.get("fpl_player_id") or "").strip()
            if not draft_text and not fpl_text:
                continue  # permit empty template rows
            try:
                draft_id, fpl_id = int(draft_text), int(fpl_text)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{path}:{line}: IDs must both be positive integers") from exc
            if min(draft_id, fpl_id) < 1:
                raise ValueError(f"{path}:{line}: IDs must be positive integers")
            if draft_id in mapping and mapping[draft_id] != fpl_id:
                raise ValueError(f"{path}:{line}: contradictory mappings for Draft ID {draft_id}")
            if fpl_id in reverse and reverse[fpl_id] != draft_id:
                raise ValueError(f"{path}:{line}: FPL ID {fpl_id} mapped to two Draft players")
            mapping[draft_id] = fpl_id
            reverse[fpl_id] = draft_id
    print(f"Loaded {len(mapping)} manual Draft/FPL player ID corrections from {path}")
    return mapping


PLAYER_ID_MAP = load_draft_player_mapping(MAPPING_CSV)


def fpl_id_for_draft(draft_id):
    """Use ONLY for Classic FPL API queries; never mutate Draft ownership IDs."""
    return PLAYER_ID_MAP.get(int(draft_id), int(draft_id))


def make_draft_keyed_elements(classic_by_id, draft_by_id):
    # Draft bootstrap is the authority for the IDs available in the Draft
    # player pool; fallback to Classic when Draft bootstrap is unavailable.
    pool_ids = set(draft_by_id) if draft_by_id else set(classic_by_id)
    pool_ids.update(PLAYER_ID_MAP)
    result = {}
    for draft_id in sorted(pool_ids):
        classic_id = fpl_id_for_draft(draft_id)
        source = classic_by_id.get(classic_id)
        if source is None:
            # No Classic record: keep Draft identity as a last-resort label,
            # but never silently borrow another player's Classic statistics.
            source = draft_by_id.get(draft_id, {})
            if not source:
                print(f"WARNING: Draft ID {draft_id} -> FPL ID {classic_id} "
                      "does not exist in either current API")
            if draft_id in PLAYER_ID_MAP:
                print(f"WARNING: mapped FPL ID {classic_id} for Draft ID "
                      f"{draft_id} not found in Classic API; no stats to attach")
        player = dict(source)
        player["id"] = draft_id
        player["draft_player_id"] = draft_id
        player["fpl_player_id"] = classic_id
        # Explicitly mapped historical IDs may no longer exist in today's
        # Draft player pool. Keep them for the archive, not free-agent offers.
        player["draft_active"] = not draft_by_id or draft_id in draft_by_id
        result[draft_id] = player
    return result


def _normalise_player_name(name):
    name = unicodedata.normalize("NFKD", str(name or "").casefold())
    return "".join(c for c in name if c.isalnum())


def _api_player_name(row):
    return (row.get("web_name") or
            " ".join(filter(None, (row.get("first_name"), row.get("second_name")))) or
            row.get("name") or "")


def export_player_mapping_audit(draft_by_id, classic_by_id, path):
    """Show ALL Draft IDs and plausible name matches; suggestions never apply automatically."""
    from collections import defaultdict as _defaultdict
    names = _defaultdict(list)
    for classic_id, row in classic_by_id.items():
        key = _normalise_player_name(_api_player_name(row))
        if key:
            names[key].append(int(classic_id))
    explicit_targets = {v: k for k, v in PLAYER_ID_MAP.items()}
    with open(path, "w", newline="", encoding="utf-8-sig") as output:
        writer = csv.DictWriter(output, fieldnames=[
            "draft_player_id", "draft_player_name", "current_fpl_player_id",
            "current_fpl_player_name", "suggested_fpl_player_id", "suggested_fpl_player_name",
            "status", "manual_override", "notes",
        ])
        writer.writeheader()
        for did in sorted(set(draft_by_id) | set(PLAYER_ID_MAP)):
            draft_row = draft_by_id.get(did, {})
            draft_name = _api_player_name(draft_row)
            fid = fpl_id_for_draft(did)
            fpl_row = classic_by_id.get(fid, {})
            fpl_name = _api_player_name(fpl_row)
            matches = names.get(_normalise_player_name(draft_name), []) if draft_name else []
            suggested = next((x for x in matches if x != fid), None) if len(matches) == 1 else None
            if fid not in classic_by_id:
                status = "MISSING FPL ID"
            elif did not in PLAYER_ID_MAP and fid in explicit_targets and explicit_targets[fid] != did:
                status = "POSSIBLE ID COLLISION - CHECK BOTH DRAFT PLAYERS"
            elif draft_name and _normalise_player_name(draft_name) != _normalise_player_name(fpl_name):
                status = "NAME MISMATCH - CHECK"
            elif did in PLAYER_ID_MAP:
                status = "MANUAL OVERRIDE"
            else:
                status = "MATCH / UNVERIFIED"
            writer.writerow({
                "draft_player_id": did, "draft_player_name": draft_name,
                "current_fpl_player_id": fid, "current_fpl_player_name": fpl_name,
                "suggested_fpl_player_id": suggested or "",
                "suggested_fpl_player_name": _api_player_name(classic_by_id.get(suggested, {})),
                "status": status, "manual_override": "yes" if did in PLAYER_ID_MAP else "no",
                "notes": "Suggestions use unique exact normalized names ONLY; verify manually.",
            })
    print(f"Draft/FPL ID audit written: {path}")


def sync_manual_mapping_with_history(data, player_lookup, team_names, position_names):
    """Correct old frozen pick identities, without losing their Draft roster IDs."""
    applied = data.setdefault("manual_player_id_mapping_applied", {})
    backups = data.setdefault("manual_player_mapping_pick_backups", {})
    pinned_scores = data.setdefault("player_scores", {})
    for draft_id in set(map(int, applied)) | set(PLAYER_ID_MAP):
        previous = applied.get(str(draft_id))
        now = PLAYER_ID_MAP.get(draft_id)
        if (previous is not None and previous != now) or (previous is None and now is not None):
            # Bad old Classic stats are pinned under the Draft ID. Removing just
            # these pins forces the correct Classic ID to be re-read below.
            pinned_scores.pop(str(draft_id), None)
            print(f"Invalidating stale score pins: Draft ID {draft_id} -> {now or 'default'}")

    corrected = 0
    for gw, snapshot in data.get("gameweeks", {}).items():
        for entry_id, squad in snapshot.get("teams", {}).items():
            for pick in squad.get("starters", []) + squad.get("bench", []):
                try:
                    draft_id = int(pick.get("element_id"))
                except (ValueError, TypeError):
                    continue
                key = f"{gw}:{entry_id}:{draft_id}"
                if draft_id in PLAYER_ID_MAP:
                    meta = player_lookup.get(draft_id, {})
                    if not meta or meta.get("fpl_player_id") != PLAYER_ID_MAP[draft_id]:
                        continue
                    if key not in backups:
                        backups[key] = {field: pick.get(field) for field in
                                        ("web_name", "team", "position", "points", "minutes", "in_dreamteam")}
                    old_name = str(pick.get("web_name") or "")
                    new_name = meta.get("web_name") or _api_player_name(meta)
                    if new_name:
                        pick["web_name"] = new_name
                    # Preserve the club on genuine historical transfers where
                    # the player identity already matched in that gameweek.
                    if (_normalise_player_name(old_name) != _normalise_player_name(new_name)
                            or not pick.get("team")):
                        pick["team"] = team_names.get(meta.get("team"), pick.get("team", ""))
                    pick["position"] = position_names.get(meta.get("element_type"), pick.get("position", ""))
                    pick["fpl_player_id"] = PLAYER_ID_MAP[draft_id]
                    corrected += 1
                elif key in backups and str(draft_id) in applied:
                    # If a line is deleted from the CSV, restore the original
                    # historical label rather than leaving the manual override.
                    for field, value in backups[key].items():
                        pick[field] = value
                    pick.pop("fpl_player_id", None)
                    del backups[key]
    data["manual_player_id_mapping_applied"] = {str(k): v for k, v in PLAYER_ID_MAP.items()}
    print(f"Applied CSV mappings to {corrected} historical/current roster picks")

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


classic_elements_by_fpl_id = {
    int(p["id"]): p for p in classic_static["elements"]
}
draft_bootstrap = fetch_json(f"{DRAFT_BASE}/bootstrap-static") or {}
draft_elements_by_id = {
    int(row["id"]): row for row in draft_bootstrap.get("elements", [])
    if isinstance(row, dict) and row.get("id") is not None
}
elements = make_draft_keyed_elements(classic_elements_by_fpl_id, draft_elements_by_id)
# The audit is exported below, after historical Draft player IDs are available.
_reverse_effective = {}
for _did in elements:
    _fid = fpl_id_for_draft(_did)
    if _fid in _reverse_effective:
        print(f"WARNING: possible duplicate Classic player {_fid} mapped from Draft "
              f"IDs {_reverse_effective[_fid]} and {_did}. Check audit CSV.")
    else:
        _reverse_effective[_fid] = _did

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

_LIVE_GW_CACHE = {}


def get_live_gw_data(gw):
    if gw in _LIVE_GW_CACHE:
        return _LIVE_GW_CACHE[gw]

    data = fetch_json(
        f"{CLASSIC_BASE}/event/{gw}/live/"
    )

    if not data:
        return {}

    classic_live = {
        int(el["id"]): {
            "points": el["stats"]["total_points"],
            "in_dreamteam": el["stats"]["in_dreamteam"],
            "minutes": el["stats"]["minutes"],
            "fpl_stats": el.get("stats", {}),  # historic component replay
        }
        for el in data.get("elements", [])
    }
    # Return DRAFT-ID keys throughout the existing dashboard so ownership,
    # lineups and player analytics continue to share the same keys.
    mapped_live = {
        draft_id: classic_live[fpl_id_for_draft(draft_id)]
        for draft_id in elements
        if fpl_id_for_draft(draft_id) in classic_live
    }
    _LIVE_GW_CACHE[gw] = mapped_live
    return mapped_live


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
# Include players from frozen seasons who have vanished from the current Draft
# pool in the audit. Their archived name helps identify the right FPL ID.
_audit_draft_rows = dict(draft_elements_by_id)
for _old_snapshot in history.get("gameweeks", {}).values():
    for _old_squad in _old_snapshot.get("teams", {}).values():
        for _old_pick in _old_squad.get("starters", []) + _old_squad.get("bench", []):
            try:
                _old_did = int(_old_pick["element_id"])
            except (KeyError, ValueError, TypeError):
                continue
            _audit_draft_rows.setdefault(_old_did, {
                "id": _old_did, "web_name": _old_pick.get("web_name", "")
            })
export_player_mapping_audit(_audit_draft_rows, classic_elements_by_fpl_id, MAPPING_AUDIT_CSV)
sync_manual_mapping_with_history(history, elements, teams_lookup, positions_lookup)
history["draft_player_id_to_fpl_player_id"] = {str(k): v for k, v in PLAYER_ID_MAP.items()}


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
                "fpl_player_id": fpl_id_for_draft(el_id),

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

