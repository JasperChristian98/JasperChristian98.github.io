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
# CONSISTENT DRAFT-TEAM COLOURS
# ============================================================
# Stable across chart sorting and league-position changes. Shared with JS.
_MANAGER_PALETTE = [
    "#38bdf8", "#f472b6", "#4ade80", "#facc15", "#a78bfa",
    "#fb923c", "#2dd4bf", "#f87171", "#818cf8", "#e879f9",
    "#84cc16", "#22d3ee", "#fbbf24", "#c084fc", "#34d399", "#fca5a5",
]
_MANAGER_COLOR_OVERRIDES = {"NoRSNoRB No Chance": "#facc15"}
_manager_colour_order = sorted(set(managers), key=lambda name: str(name).casefold())
_reserved_colours = set(_MANAGER_COLOR_OVERRIDES.values())
_manager_palette_available = [c for c in _MANAGER_PALETTE if c not in _reserved_colours]
MANAGER_COLOR_MAP = {}
_palette_index = 0
for _manager in _manager_colour_order:
    if _manager in _MANAGER_COLOR_OVERRIDES:
        MANAGER_COLOR_MAP[_manager] = _MANAGER_COLOR_OVERRIDES[_manager]
    else:
        MANAGER_COLOR_MAP[_manager] = _manager_palette_available[_palette_index % len(_manager_palette_available)]
        _palette_index += 1

def manager_color(manager):
    return MANAGER_COLOR_MAP.get(manager, "#38bdf8")


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
        + norm_squad_management.get(manager, 0) * 0.10
        + norm_league_position.get(manager, 0) * 0.20
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
# ALL-PLAYER GAMEWEEK POINTS
# ============================================================
# FPL's event/{gw}/live endpoint contains every Premier League player,
# not just players who have appeared in McDraft. Use it as the canonical
# source for player-by-player GW scoring in the Player directory.
all_player_gw_points = defaultdict(dict)
for _gw in finished_gws:
    _live_all = get_live_gw_data(_gw) or {}
    for _pid, _stats in _live_all.items():
        all_player_gw_points[int(_pid)][int(_gw)] = int((_stats or {}).get("points", 0) or 0)

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

        "fpl_id":
            fpl_id_for_draft(player_id),

        "name":
            elements.get(player_id, {}).get("web_name", info["name"]) if player_id in PLAYER_ID_MAP else info["name"],

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

        points = all_player_gw_points.get(
            int(player_id),
            {}
        ).get(
            int(gw),
            player_form.get(player_id, {}).get(gw, 0)
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
                    "id": p.get("element_id"),
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
                    "id": p.get("element_id"),
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
        if not meta.get("draft_active", True):
            continue
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
            league_rank=_league_draft_rank(pid)
            official_rank=_official_draft_rank(pid)
            rank=float(_blended_draft_rank(pid))
            draft_strength=max(0.0,min(1.0,(UNDRAFTED_PLAYER_RANK-rank)/max(UNDRAFTED_PLAYER_RANK-1,1)))
            importance=0.55*(pts/roster_total)+0.45*(proj/roster_proj)
            _model=globals().get('_player_search_by_id',{}).get(int(pid), globals().get('_player_model_by_id',{}).get(int(pid),{}))
            _model_value=float(_model.get('player_value',50) or 50)/100.0
            _fixture=float(_model.get('fixture_run_score',1) or 1)
            _heat=float(_model.get('hot_cold_score',0) or 0)
            value=(0.24*(pts/max_points)+0.19*(form/max_form)+0.18*min(1.0,proj/8.0)+0.14*draft_strength+0.10*min(1.0,importance*8.0)+0.15*_model_value)*100.0
            value += max(-4.0,min(4.0,(_fixture-1.0)*18.0)) + max(-3.0,min(3.0,_heat*0.03))
            players.append({'id':int(pid),'name':meta.get('web_name','Unknown'),'position':POSITION_LABELS.get(meta.get('element_type'),positions_lookup.get(meta.get('element_type'),'—')),'club':teams_lookup.get(meta.get('team'),'—'),'points':round(pts,1),'form':round(form,2),'projection':round(proj,2),'draft_rank':round(rank,1),'league_draft_rank':league_rank,'official_draft_rank':official_rank,'importance':round(importance*100.0,1),'value':round(value,1),'avg5':round(float(metrics.get('avg_5') or 0),2),'season_projection':round(float(_model.get('projected_season_points',0) or 0),1),'heat':round(_heat,1),'fixture_run_score':round(_fixture,3)})
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

