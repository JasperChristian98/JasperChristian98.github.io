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
# but it is blended with season output, draft pedigree and a position baseline,
# then adjusted for the player's real Premier League fixture in the target GW.
# Current ownership comes from Draft element-status, so waivers/trades and PL
# fixture runs both change the forecast immediately.

def _current_roster_by_manager():
    rosters = {manager: [] for manager in managers}
    for player_id, owner in current_owner_by_player.items():
        manager = _dashboard_owner_name(owner)
        if manager in rosters:
            rosters[manager].append(int(player_id))
    return rosters


# ============================================================
# PREMIER LEAGUE FIXTURE-AWARE PLAYER PROJECTIONS
# ============================================================
# FPL bootstrap-static exposes club attack/defence strength split by venue.
# Convert those values into a modest player-level fixture multiplier. The
# adjustment is deliberately capped: fixtures should move a projection, not
# completely erase player quality/form. Blank GWs project zero; double GWs
# naturally sum multiple fixture contributions.

_pl_team_meta_by_id = {
    int(t.get("id")): t
    for t in bootstrap.get("teams", [])
    if isinstance(t, dict) and t.get("id") is not None
}

# ------------------------------------------------------------------
# PREMIER LEAGUE CLUB STRENGTH MODEL
# ------------------------------------------------------------------
# Club strength deliberately blends several independent signals so future
# fixture difficulty is not driven by one rather flat FPL metadata field:
#   * actual Premier League table position / results to date
#   * total FPL points produced by every player at the club
#   * official FPL Draft pedigree of the club's best fantasy assets
#   * FPL's attack/defence strength metadata
# This score is also used as a small prior on an individual player's value:
# good players in strong teams generally have a healthier scoring environment.

def _minmax_map(values, higher_is_better=True, neutral=0.5):
    clean = [float(v) for v in values if v is not None]
    if not clean:
        return lambda x: neutral
    lo, hi = min(clean), max(clean)
    if abs(hi - lo) < 1e-9:
        return lambda x: neutral
    def _scale(x):
        if x is None:
            return neutral
        z = (float(x) - lo) / (hi - lo)
        z = min(1.0, max(0.0, z))
        return z if higher_is_better else (1.0 - z)
    return _scale

# Reconstruct the live Premier League table from completed fixtures. This avoids
# relying on an extra endpoint and gives us a real current league-position signal.
_pl_table_stats = {
    tid: {"pts": 0, "gf": 0, "ga": 0, "gd": 0, "played": 0}
    for tid in _pl_team_meta_by_id
}
for _fx in _all_pl_fixtures:
    if not isinstance(_fx, dict) or not _fx.get("finished"):
        continue
    try:
        _h = int(_fx.get("team_h")); _a = int(_fx.get("team_a"))
        _hs = int(_fx.get("team_h_score") or 0); _as = int(_fx.get("team_a_score") or 0)
    except (TypeError, ValueError):
        continue
    if _h not in _pl_table_stats or _a not in _pl_table_stats:
        continue
    for tid, gf, ga in ((_h, _hs, _as), (_a, _as, _hs)):
        st = _pl_table_stats[tid]
        st["played"] += 1; st["gf"] += gf; st["ga"] += ga; st["gd"] = st["gf"] - st["ga"]
    if _hs > _as:
        _pl_table_stats[_h]["pts"] += 3
    elif _as > _hs:
        _pl_table_stats[_a]["pts"] += 3
    else:
        _pl_table_stats[_h]["pts"] += 1; _pl_table_stats[_a]["pts"] += 1

_pl_table_order = sorted(
    _pl_table_stats,
    key=lambda tid: (
        -_pl_table_stats[tid]["pts"],
        -_pl_table_stats[tid]["gd"],
        -_pl_table_stats[tid]["gf"],
        teams_lookup.get(tid, ""),
    )
)
_pl_position = {tid: idx + 1 for idx, tid in enumerate(_pl_table_order)}

# Total FPL output by real Premier League club.
_pl_total_fpl_points = defaultdict(float)
_pl_official_ranks = defaultdict(list)
for _pid, _meta in elements.items():
    try:
        _tid = int(_meta.get("team"))
    except (TypeError, ValueError):
        continue
    _pl_total_fpl_points[_tid] += float(_meta.get("total_points", 0) or 0)
    _rank = _official_draft_rank(_pid)
    if _rank is not None:
        _pl_official_ranks[_tid].append(float(_rank))

# Use the best ten officially ranked assets from a club. This measures whether
# the club contains lots of valuable fantasy assets without being distorted by
# academy/fringe players who happen to have a very low draft ranking.
_pl_team_draft_rank = {}
for _tid in _pl_team_meta_by_id:
    ranks = sorted(_pl_official_ranks.get(_tid, []))[:10]
    _pl_team_draft_rank[_tid] = statistics.mean(ranks) if ranks else float(UNDRAFTED_PLAYER_RANK)

# Aggregate the FPL club metadata into one broad team-quality signal as well.
_pl_meta_strength = {}
for _tid, _meta in _pl_team_meta_by_id.items():
    vals = []
    for _field in (
        "strength_overall_home", "strength_overall_away",
        "strength_attack_home", "strength_attack_away",
        "strength_defence_home", "strength_defence_away",
    ):
        try:
            _v = float(_meta.get(_field, 0) or 0)
        except (TypeError, ValueError):
            _v = 0.0
        if _v > 0:
            vals.append(_v)
    _pl_meta_strength[_tid] = statistics.mean(vals) if vals else float(_meta.get("strength", 0) or 0)

# Pre-season / slow-moving priors. These are deliberately kept separate from
# in-season evidence because their influence should fade as the season matures.
_scale_draft = _minmax_map([_pl_team_draft_rank.get(t, UNDRAFTED_PLAYER_RANK) for t in _pl_team_meta_by_id], False)
_scale_meta = _minmax_map([_pl_meta_strength.get(t, 0) for t in _pl_team_meta_by_id], True)

_pl_strength_snapshot_cache = {}
_pl_table_snapshot_cache = {}
_pl_fpl_points_snapshot_cache = {}

def _pl_table_snapshot(as_of_gw):
    """Premier League table reconstructed using results up to a specific GW."""
    try:
        as_of_gw = max(0, int(as_of_gw))
    except (TypeError, ValueError):
        as_of_gw = max([int(g) for g in finished_gws] or [0])
    if as_of_gw in _pl_table_snapshot_cache:
        return _pl_table_snapshot_cache[as_of_gw]
    stats = {tid: {"pts":0,"gf":0,"ga":0,"gd":0,"played":0} for tid in _pl_team_meta_by_id}
    for fx in _all_pl_fixtures:
        if not isinstance(fx, dict) or not fx.get('finished'):
            continue
        try:
            event = int(fx.get('event') or 0)
            h = int(fx.get('team_h')); a = int(fx.get('team_a'))
            hs = int(fx.get('team_h_score') or 0); ass = int(fx.get('team_a_score') or 0)
        except (TypeError, ValueError):
            continue
        if event > as_of_gw or h not in stats or a not in stats:
            continue
        for tid,gf,ga in ((h,hs,ass),(a,ass,hs)):
            st=stats[tid]; st['played']+=1; st['gf']+=gf; st['ga']+=ga; st['gd']=st['gf']-st['ga']
        if hs>ass: stats[h]['pts']+=3
        elif ass>hs: stats[a]['pts']+=3
        else: stats[h]['pts']+=1; stats[a]['pts']+=1
    order=sorted(stats,key=lambda tid:(-stats[tid]['pts'],-stats[tid]['gd'],-stats[tid]['gf'],teams_lookup.get(tid,'')))
    out={'stats':stats,'position':{tid:i+1 for i,tid in enumerate(order)},'order':order}
    _pl_table_snapshot_cache[as_of_gw]=out
    return out

def _pl_fpl_points_snapshot(as_of_gw):
    """Cumulative FPL points generated by each real PL club through a GW."""
    try:
        as_of_gw=max(0,int(as_of_gw))
    except (TypeError,ValueError):
        as_of_gw=max([int(g) for g in finished_gws] or [0])
    if as_of_gw in _pl_fpl_points_snapshot_cache:
        return _pl_fpl_points_snapshot_cache[as_of_gw]
    totals=defaultdict(float)
    for pid,gw_map in all_player_gw_points.items():
        meta=elements.get(int(pid),{})
        try: tid=int(meta.get('team'))
        except (TypeError,ValueError): continue
        totals[tid]+=sum(float(pts or 0) for gw,pts in gw_map.items() if int(gw)<=as_of_gw)
    out={tid:float(totals.get(tid,0.0)) for tid in _pl_team_meta_by_id}
    _pl_fpl_points_snapshot_cache[as_of_gw]=out
    return out

def _pl_club_strength_snapshot(as_of_gw=None):
    """Return time-varying club strength as it would have looked at that point.

    Early season = mostly official Draft/FPL priors. As evidence accumulates,
    actual FPL production and the real league table progressively take over.
    """
    latest=max([int(g) for g in finished_gws] or [0])
    try: as_of_gw=latest if as_of_gw is None else max(0,min(int(as_of_gw),latest))
    except (TypeError,ValueError): as_of_gw=latest
    if as_of_gw in _pl_strength_snapshot_cache:
        return _pl_strength_snapshot_cache[as_of_gw]
    table=_pl_table_snapshot(as_of_gw)
    points=_pl_fpl_points_snapshot(as_of_gw)
    scale_points=_minmax_map([points.get(t,0) for t in _pl_team_meta_by_id],True)
    scale_position=_minmax_map([table['position'].get(t,len(_pl_team_meta_by_id)) for t in _pl_team_meta_by_id],False)
    # The handover is gradual: by ~GW12 the season itself dominates the priors.
    evidence=min(1.0,max(0.0,as_of_gw/12.0))
    w_points=0.12 + 0.30*evidence
    w_position=0.08 + 0.25*evidence
    w_draft=0.42 - 0.30*evidence
    w_meta=0.38 - 0.25*evidence
    scores={}
    for tid in _pl_team_meta_by_id:
        score=(w_points*scale_points(points.get(tid,0))
               +w_position*scale_position(table['position'].get(tid,len(_pl_team_meta_by_id)))
               +w_draft*_scale_draft(_pl_team_draft_rank.get(tid,UNDRAFTED_PLAYER_RANK))
               +w_meta*_scale_meta(_pl_meta_strength.get(tid,0)))
        scores[tid]=min(1.0,max(0.0,score))
    payload={'scores':scores,'points':points,'table':table,'evidence':evidence,
             'weights':{'fpl_points':w_points,'league_position':w_position,'draft_pedigree':w_draft,'fpl_metadata':w_meta}}
    _pl_strength_snapshot_cache[as_of_gw]=payload
    return payload

_latest_pl_strength_snapshot=_pl_club_strength_snapshot()
_pl_club_strength_score=_latest_pl_strength_snapshot['scores']
_pl_total_fpl_points=defaultdict(float,_latest_pl_strength_snapshot['points'])
_pl_table_stats=_latest_pl_strength_snapshot['table']['stats']
_pl_position=_latest_pl_strength_snapshot['table']['position']
_pl_table_order=_latest_pl_strength_snapshot['table']['order']


def premier_league_table_html():
    rows=[]
    ordered=sorted(_pl_team_meta_by_id, key=lambda tid:_pl_position.get(tid,99))
    for tid in ordered:
        st=_pl_table_stats.get(tid,{})
        rows.append(f"<tr><td>{_pl_position.get(tid,'—')}</td><td><b>{escape_html(_pl_team_meta_by_id.get(tid,{}).get('name','—'))}</b></td><td>{int(st.get('played',0))}</td><td><b>{int(st.get('pts',0))}</b></td><td>{int(st.get('gd',0)):+d}</td><td>{int(round(_pl_total_fpl_points.get(tid,0)))}</td><td>{_pl_club_strength_score.get(tid,0.5)*100:.0f}</td></tr>")
    return '<div class="table-wrap"><table><thead><tr><th>#</th><th>Premier League</th><th>P</th><th>Pts</th><th>GD</th><th>FPL pts</th><th>Fantasy strength</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'


def _pl_fixture_browser_payload():
    data={}
    latest=max([int(g) for g in finished_gws] or [0])
    for fx in _all_pl_fixtures:
        if not isinstance(fx,dict) or fx.get('event') is None: continue
        gw=int(fx.get('event'))
        h=int(fx.get('team_h') or 0); a=int(fx.get('team_a') or 0)
        hname=_pl_team_meta_by_id.get(h,{}).get('name',teams_lookup.get(h,'—'))
        aname=_pl_team_meta_by_id.get(a,{}).get('name',teams_lookup.get(a,'—'))
        finished=bool(fx.get('finished'))
        score=(f"{fx.get('team_h_score',0)}–{fx.get('team_a_score',0)}" if finished else 'vs')
        # Historical browser = cumulative club FPL output through that selected GW.
        # Future browser = current season-to-date total (there are no future points yet).
        point_gw=min(gw,latest)
        pts=_pl_fpl_points_snapshot(point_gw)
        strength=_pl_club_strength_snapshot(min(max(gw-1,0),latest))['scores']
        data.setdefault(str(gw),[]).append({
            'home':hname,'away':aname,'score':score,'finished':finished,
            'kickoff':fx.get('kickoff_time'),
            'home_fpl_points':round(pts.get(h,0),0),'away_fpl_points':round(pts.get(a,0),0),
            'home_model_strength':round(strength.get(h,0.5)*100,1),
            'away_model_strength':round(strength.get(a,0.5)*100,1),
        })
    return data


pl_fixture_browser_json=json.dumps(_pl_fixture_browser_payload(),ensure_ascii=False)


def _safe_strength_values(field):
    vals = []
    for team in _pl_team_meta_by_id.values():
        try:
            val = float(team.get(field, 0) or 0)
        except (TypeError, ValueError):
            continue
        if val > 0:
            vals.append(val)
    return vals

_pl_strength_reference = {}
for _field in (
    "strength_attack_home", "strength_attack_away",
    "strength_defence_home", "strength_defence_away",
):
    _vals = _safe_strength_values(_field)
    _pl_strength_reference[_field] = {
        "mean": statistics.mean(_vals) if _vals else 1000.0,
        "sd": max(statistics.pstdev(_vals), 1.0) if len(_vals) >= 2 else 100.0,
    }


def _fixture_strength_z(opponent_id, field):
    meta = _pl_team_meta_by_id.get(int(opponent_id), {})
    ref = _pl_strength_reference.get(field, {"mean": 1000.0, "sd": 100.0})
    try:
        value = float(meta.get(field, ref["mean"]) or ref["mean"])
    except (TypeError, ValueError):
        value = ref["mean"]
    return (value - ref["mean"]) / max(ref["sd"], 1.0)


def _club_projection_multiplier(club_id, position=None, target_gw=None):
    """Small persistent value bump/penalty from the player's own PL club quality.

    Uses the strength snapshot appropriate to the target GW so club quality evolves
    over the season instead of being a frozen preseason label.
    """
    try:
        club_id = int(club_id)
    except (TypeError, ValueError):
        return 1.0
    latest=max([int(g) for g in finished_gws] or [0])
    try: strength_gw=latest if target_gw is None else min(max(int(target_gw)-1,0),latest)
    except (TypeError,ValueError): strength_gw=latest
    strength = float(_pl_club_strength_snapshot(strength_gw)['scores'].get(club_id, 0.5) or 0.5)
    # +/-8% across the entire league. Attackers receive a touch more of the
    # environment effect; keepers/defenders a touch less because individual
    # clean-sheet scoring is already heavily affected by the opponent model.
    position_weight = {"GK": 0.75, "DEF": 0.85, "MID": 1.05, "FWD": 1.10}.get(position, 1.0)
    delta = (strength - 0.5) * 0.16 * position_weight
    return min(1.10, max(0.90, 1.0 + delta))


def _player_fixture_components(player_id, gw):
    """Return fixture detail + multiplier for a player in one PL gameweek."""
    try:
        gw = int(gw)
    except (TypeError, ValueError):
        return []

    meta = elements.get(int(player_id), {})
    club_id = meta.get("team")
    element_type = int(meta.get("element_type", 0) or 0)
    position = positions_lookup.get(element_type, "")
    if club_id is None:
        return []

    # For a historical GW, use only information known before that GW; for a future GW,
    # use the latest available snapshot. This prevents hindsight leakage.
    _latest_strength_gw = max([int(g) for g in finished_gws] or [0])
    _strength_as_of = min(max(gw - 1, 0), _latest_strength_gw)
    _strength_snapshot = _pl_club_strength_snapshot(_strength_as_of)['scores']
    own_strength = float(_strength_snapshot.get(int(club_id), 0.5) or 0.5)
    fixtures = _pl_fixtures_by_event_team.get((gw, int(club_id)), [])
    components = []
    for item in fixtures:
        opp_id = int(item["opponent"])
        is_home = bool(item["is_home"])

        opp_strength = float(_strength_snapshot.get(opp_id, 0.5) or 0.5)
        # We still retain FPL's venue-specific positional signal, but it is no
        # longer the whole model. That was what caused most fixtures to look amber.
        opp_venue = "away" if is_home else "home"
        attack_field = f"strength_attack_{opp_venue}"
        defence_field = f"strength_defence_{opp_venue}"
        attack_z = _fixture_strength_z(opp_id, attack_field)
        defence_z = _fixture_strength_z(opp_id, defence_field)

        if position in ("GK", "DEF"):
            metadata_challenge = attack_z
        elif position == "MID":
            metadata_challenge = (0.70 * defence_z) + (0.30 * attack_z)
        else:
            metadata_challenge = defence_z

        # Composite difficulty has deliberately wider separation than the old
        # metadata-only model. Opponent club quality supplies the main signal;
        # relative club strength makes strong sides less frightened of middling
        # opposition; venue is an explicit material adjustment.
        relative_challenge = opp_strength - own_strength
        multiplier = 1.0
        multiplier -= 0.30 * (opp_strength - 0.5)          # +/-15%
        multiplier -= 0.13 * relative_challenge            # stronger own club helps
        multiplier -= 0.035 * max(-2.0, min(2.0, metadata_challenge))
        multiplier *= 1.075 if is_home else 0.945          # home good, away worse
        multiplier = min(1.32, max(0.70, multiplier))

        components.append({
            "opponent_id": opp_id,
            "opponent": teams_lookup.get(opp_id, f"Team {opp_id}"),
            "is_home": is_home,
            "multiplier": multiplier,
            "challenge_z": metadata_challenge,
            "opponent_strength": opp_strength,
            "own_club_strength": own_strength,
            "opponent_position": _pl_position.get(opp_id),
            "opponent_total_fpl_points": round(float(_pl_total_fpl_points.get(opp_id, 0) or 0), 1),
            "opponent_team_draft_rank": round(float(_pl_team_draft_rank.get(opp_id, UNDRAFTED_PLAYER_RANK)), 1),
        })
    return components


def _player_fixture_multiplier(player_id, gw):
    components = _player_fixture_components(player_id, gw)
    if not components:
        try:
            gw_int = int(gw)
        except (TypeError, ValueError):
            return 1.0
        schedule_has_event = any(
            isinstance(fx, dict) and fx.get("event") is not None and int(fx.get("event")) == gw_int
            for fx in _all_pl_fixtures
            if isinstance(fx, dict)
        )
        return 0.0 if schedule_has_event else 1.0
    return sum(float(c.get("multiplier", 1.0) or 1.0) for c in components)


def _fixture_difficulty_from_multiplier(multiplier):
    """Map fixture projection multiplier to 1 easy .. 5 brutal with useful spread."""
    try:
        m = float(multiplier)
    except (TypeError, ValueError):
        return 3
    if m <= 0:
        return 5
    if m >= 1.15:
        return 1
    if m >= 1.045:
        return 2
    if m >= 0.955:
        return 3
    if m >= 0.86:
        return 4
    return 5

def _player_next_fixture_run(player_id, count=3, start_gw=None):
    """Compact next-N PL fixture run for UI cards and recommendation models."""
    if start_gw is None:
        start_gw = int(dashboard_target_gw or ((max(finished_gws) + 1) if finished_gws else 1))
    else:
        start_gw = int(start_gw)

    scheduled_events = sorted({
        int(fx.get("event"))
        for fx in _all_pl_fixtures
        if isinstance(fx, dict) and fx.get("event") is not None and int(fx.get("event")) >= start_gw
    })[:max(1, int(count))]

    run = []
    for gw in scheduled_events:
        comps = _player_fixture_components(player_id, gw)
        if not comps:
            run.append({
                "gw": gw, "label": "Blank", "difficulty": 5, "multiplier": 0.0,
                "fixtures": [], "is_blank": True, "is_double": False,
            })
            continue

        fixture_labels = []
        difficulties = []
        multipliers = []
        for comp in comps:
            label = f"{comp.get('opponent','—')} ({'H' if comp.get('is_home') else 'A'})"
            fixture_labels.append(label)
            mult = float(comp.get("multiplier", 1.0) or 1.0)
            multipliers.append(mult)
            difficulties.append(_fixture_difficulty_from_multiplier(mult))

        # For doubles, average difficulty but retain both labels. Projection uses
        # the sum of multipliers elsewhere, so this is presentation-only.
        avg_diff = round(sum(difficulties) / len(difficulties)) if difficulties else 3
        run.append({
            "gw": gw,
            "label": " + ".join(fixture_labels),
            "difficulty": int(max(1, min(5, avg_diff))),
            "multiplier": round(sum(multipliers), 3),
            "fixtures": fixture_labels,
            "is_blank": False,
            "is_double": len(comps) > 1,
        })
    return run

def _fixture_run_score(player_id, count=3):
    run = _player_next_fixture_run(player_id, count=count)
    if not run:
        return 1.0
    vals = [float(r.get("multiplier", 1.0) or 0.0) for r in run]
    # Keep recommendation impact modest; this should break ties, not dominate talent.
    return sum(vals) / max(len(vals), 1)

def _availability_factor(player_id, target_gw=None):
    """Conservative availability estimate, NOT a medical return-date forecast.

    Official FPL probabilities apply to the next GW only. For later weeks,
    gradually regress uncertain/injured/suspended players toward availability
    rather than incorrectly holding today's 0% throughout the season.
    """
    row = _fpl_availability.get(int(player_id), {})
    status = row.get("status", "a")
    if target_gw is None:
        target_gw = dashboard_target_gw
    gap = max(0, int(target_gw or 0) - int(dashboard_target_gw or 0))
    raw_chance = row.get("chance_this") if gap == 0 and dashboard_game_state == "live" else row.get("chance_next")
    try:
        chance = None if raw_chance is None else max(0.0, min(1.0, float(raw_chance) / 100.0))
    except (TypeError, ValueError):
        chance = None
    if status == "a":
        base = 1.0 if chance is None else chance
    elif status == "d":
        base = 0.65 if chance is None else chance
    elif status in ("i", "s", "u"):
        base = 0.05 if chance is None else chance
    elif status == "n":
        base = 0.0 if chance is None else chance
    else:
        base = 0.85 if chance is None else chance
    if gap == 0 or status == "a":
        return max(0.0, min(1.0, base))
    # Not a claim about injury recovery or suspension length: explicit
    # uncertainty in future GWs until we receive updated official data.
    recovery = {"d": 0.25, "i": 0.17, "s": 0.29, "u": 0.12, "n": 0.05}.get(status, 0.2)
    return max(0.0, min(1.0, base + (1.0 - base) * (1.0 - (1.0 - recovery) ** gap)))


def _player_weekly_projection(player_id, position_baselines, league_player_mean, target_gw=None, apply_availability=True):
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

    # Pedigree prior is a blend of this league's real draft behaviour and the
    # official FPL Draft preseason ordering. McDraft remains the larger share.
    overall_pick = _blended_draft_rank(player_id)

    # Convert blended rank 1..151 to a curved 0-1 quality prior. Rank 151 maps exactly
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

    # Fold in the real Premier League fixture when a target GW is supplied.
    # This is the key bridge from individual PL schedules into McDraft squad
    # forecasts, trade values and season simulations.
    # The strength of the player's own Premier League club is a persistent,
    # modest value prior. It affects both future projection and downstream trade
    # value because stronger real teams create more scoring/clean-sheet upside.
    if target_gw is None:
        target_gw = dashboard_target_gw
    projection *= _club_projection_multiplier(
        elements.get(player_id, {}).get("team"), position, target_gw=target_gw
    )
    if target_gw is not None:
        projection *= _player_fixture_multiplier(player_id, target_gw)
    # Apply once at the common projection layer to avoid inconsistencies
    # between the five-GW planner, trade value and season simulations.
    if apply_availability:
        projection *= _availability_factor(player_id, target_gw)

    # A small, bounded rating adjustment for ONLY the imminent GW. Long-term
    # fixture projections keep the original forward-looking model unchanged.
    ratings = globals().get("_player_ratings_by_id", {})
    if (ratings and target_gw is not None
            and int(target_gw) == int(dashboard_target_gw)
            and int(target_gw) > int(dashboard_last_finished_gw)):
        rating = ratings.get(int(player_id), {}).get("rating")
        if rating is not None:
            projection *= 1.0 + max(-0.07, min(0.07, (float(rating) - 65.0) / 250.0))

    return max(0.0, projection)


def _historical_fixture_multiplier(player_id, gw):
    """Fixture multiplier for a completed GW, bounded for form normalisation."""
    mult = float(_player_fixture_multiplier(player_id, gw) or 0.0)
    if mult <= 0:
        return 1.0
    return max(0.65, min(1.45, mult))


def _player_heat_metrics(player_id):
    """Fixture-adjusted hot/cold signal from recent scoring versus season baseline."""
    if not finished_gws:
        return {"score": 0.0, "label": "Neutral", "recent_adjusted": 0.0, "season_adjusted": 0.0}
    neutralised=[]
    for gw in finished_gws:
        pts=float(all_player_gw_points.get(int(player_id),{}).get(int(gw),0) or 0)
        neutralised.append((int(gw), pts/_historical_fixture_multiplier(player_id, gw)))
    season_vals=[v for _,v in neutralised]
    recent_vals=[v for _,v in neutralised[-3:]]
    season_avg=statistics.mean(season_vals) if season_vals else 0.0
    recent_avg=statistics.mean(recent_vals) if recent_vals else season_avg
    # Blend relative and absolute change so low-baseline players do not look
    # absurdly hot after one two-point appearance.
    rel=((recent_avg-season_avg)/max(1.5,season_avg))*100.0
    abs_component=(recent_avg-season_avg)*8.0
    score=max(-100.0,min(100.0,(0.72*rel)+(0.28*abs_component)))
    if score >= 22: label='Running hot'
    elif score >= 8: label='Warm'
    elif score <= -22: label='Running cold'
    elif score <= -8: label='Cool'
    else: label='Neutral'
    return {"score":round(score,1),"label":label,"recent_adjusted":round(recent_avg,2),"season_adjusted":round(season_avg,2)}


def _future_pl_gameweeks():
    last=max(finished_gws) if finished_gws else 0
    return sorted({int(fx.get('event')) for fx in _all_pl_fixtures if isinstance(fx,dict) and fx.get('event') is not None and int(fx.get('event'))>last})


def _player_season_projection(player_id):
    actual=float(elements.get(player_id,{}).get('total_points',0) or 0)
    remaining=0.0
    for gw in _future_pl_gameweeks():
        remaining += float(_player_weekly_projection(player_id, _global_position_baselines, _global_league_player_mean, target_gw=gw) or 0)
    return actual + remaining, remaining


# Global positional baselines reused by player season projections.
_global_position_values=defaultdict(list)
_global_all_player_values=[]
for _pid,_meta in elements.items():
    _pos=positions_lookup.get(_meta.get('element_type'),'')
    _val=float(_meta.get('total_points',0) or 0)/max(len(finished_gws),1)
    _global_position_values[_pos].append(_val); _global_all_player_values.append(_val)
_global_league_player_mean=statistics.mean(_global_all_player_values) if _global_all_player_values else 2.5
_global_position_baselines={p:(statistics.mean(v) if v else _global_league_player_mean) for p,v in _global_position_values.items()}


def _club_strength_label(club_id):
    score=float(_pl_club_strength_score.get(int(club_id),0.5) if club_id else 0.5)
    if score>=0.80:return 'Elite club'
    if score>=0.63:return 'Strong club'
    if score>=0.42:return 'Mid-tier club'
    if score>=0.25:return 'Weak club'
    return 'Very weak club'


# Enrich every player — including players never owned in McDraft.
_player_value_raw={}
for _row in player_search_data:
    _pid=int(_row.get('id',0) or 0)
    _meta=elements.get(_pid,{})
    _heat=_player_heat_metrics(_pid)
    _season_proj,_remaining_proj=_player_season_projection(_pid)
    _next3=_player_next_fixture_run(_pid,3)
    _next3_proj=sum(float(_player_weekly_projection(_pid,_global_position_baselines,_global_league_player_mean,target_gw=r.get('gw')) or 0) for r in _next3)
    _fixture_score=float(_fixture_run_score(_pid,3) or 1.0)
    _club_id=_meta.get('team')
    _club_strength=float(_pl_club_strength_score.get(int(_club_id),0.5) if _club_id else 0.5)
    _blended=float(_blended_draft_rank(_pid) or UNDRAFTED_PLAYER_RANK)
    _draft_quality=1.0-min(1.0,max(0.0,(_blended-1)/(UNDRAFTED_PLAYER_RANK-1)))
    _availability=_fpl_availability.get(_pid, {})
    _row.update({
        'availability':_availability,
        'availability_next':round(_availability_factor(_pid, dashboard_target_gw), 3),
        'hot_cold_score':_heat['score'],'hot_cold_label':_heat['label'],
        'fixture_adjusted_recent':_heat['recent_adjusted'],'fixture_adjusted_season':_heat['season_adjusted'],
        'projected_season_points':round(_season_proj,1),'projected_remaining_points':round(_remaining_proj,1),
        'next3_projected_points':round(_next3_proj,1),'club_strength':round(_club_strength*100.0,1),
        'club_strength_label':_club_strength_label(_club_id),'blended_draft_rank':round(_blended,1),
        'fixture_run_score':round(_fixture_score,3),
    })
    # Add fixture context to every historical GW row.
    for _hist in _row.get('history',[]):
        _gw=int(_hist.get('gw',0) or 0)
        _comps=_player_fixture_components(_pid,_gw)
        if _comps:
            _labels=[]; _diffs=[]
            for _c in _comps:
                _labels.append(f"{_c.get('opponent','—')} ({'H' if _c.get('is_home') else 'A'})")
                _diffs.append(_fixture_difficulty_from_multiplier(float(_c.get('multiplier',1.0) or 1.0)))
            _hist['fixture']=' + '.join(_labels); _hist['fixture_difficulty']=round(statistics.mean(_diffs),1) if _diffs else 3
        else:
            _hist['fixture']='Blank'; _hist['fixture_difficulty']=5
    _player_value_raw[_pid]=(
        0.34*_season_proj + 0.20*_next3_proj + 18.0*_draft_quality +
        14.0*_club_strength + 10.0*max(0.0,min(1.5,_fixture_score)) + 0.05*max(-40.0,min(40.0,_heat['score']))
    )

if _player_value_raw:
    _lo=min(_player_value_raw.values()); _hi=max(_player_value_raw.values()); _span=max(1e-9,_hi-_lo)
    for _row in player_search_data:
        _raw=_player_value_raw.get(int(_row.get('id',0) or 0),_lo)
        _availability_discount = 0.80 + 0.20 * _availability_factor(int(_row.get('id',0) or 0), dashboard_target_gw)
        _row['player_value']=round((25.0+75.0*((_raw-_lo)/_span)) * _availability_discount,1)

# ============================================================
# DYNAMIC FIFA-STYLE PLAYER RATINGS / 100
# ============================================================
# Current, positional FPL performance ratings; *not* the trade-value score.
# Rebuilt on every GitHub run from the current API and live PL club form.
# Every component is inspectable in Player Directory and squad pedigree.
# Individual percentiles compare players at the SAME position; low-minute
# newcomers retain a draft prior rather than receiving an invented PPG.
import bisect as _rating_bisect


def _rating_num(value, fallback=0.0):
    try:
        val = float(value)
        return val if math.isfinite(val) else fallback
    except (ValueError, TypeError):
        return fallback


def _rating_clamp(value, low=0.0, high=1.0):
    return min(high, max(low, float(value)))


def _club_last_five_form():
    records = defaultdict(list)
    for fx in _all_pl_fixtures:
        if not isinstance(fx, dict) or not fx.get('finished'):
            continue
        try:
            home = int(fx['team_h']); away = int(fx['team_a'])
            hs = int(fx['team_h_score']); aws = int(fx['team_a_score'])
        except (KeyError, TypeError, ValueError):
            continue
        order = (int(fx.get('event') or 0), str(fx.get('kickoff_time') or ''))
        records[home].append((order, 3 if hs > aws else 1 if hs == aws else 0))
        records[away].append((order, 3 if aws > hs else 1 if hs == aws else 0))
    result = {}
    for club in _pl_team_meta_by_id:
        last = sorted(records.get(club, []), key=lambda x: x[0])[-5:]
        # Prior-neutral until the first actual Premier League results exist.
        result[club] = sum(v for _, v in last) / (3.0 * len(last)) if last else 0.5
    return result


_rating_club_form = _club_last_five_form()
_rating_sample_gws = len(finished_gws)
_rating_features = {}
_rating_distributions = defaultdict(lambda: defaultdict(list))

for _entry in player_search_data:
    pid = int(_entry['id'])
    meta = elements.get(pid, {})
    pos = _entry.get('position', '')
    minutes = max(0.0, _rating_num(meta.get('minutes')))
    played = max(0.0, _rating_num(meta.get('starts')))
    per90 = 90.0 / max(270.0, minutes)  # stabilise tiny samples
    history_pts = player_form.get(pid, {}) or {}
    if history_pts and finished_gws:
        three = statistics.mean([_rating_num(history_pts.get(gw)) for gw in finished_gws[-3:]])
        five = statistics.mean([_rating_num(history_pts.get(gw)) for gw in finished_gws[-5:]])
    else:
        # FPL's own rolling form covers the full player pool, even unowned FAs.
        three = five = _rating_num(meta.get('form'))
    season_ppgw = _rating_num(meta.get('total_points')) / max(1, _rating_sample_gws)
    xgi = _rating_num(meta.get('expected_goal_involvements')) * per90
    goals = _rating_num(meta.get('goals_scored')) * per90
    assists = _rating_num(meta.get('assists')) * per90
    bonus = _rating_num(meta.get('bonus')) * per90
    bps = _rating_num(meta.get('bps')) * per90
    defensive = _rating_num(meta.get('defensive_contribution')) * per90
    clean = _rating_num(meta.get('clean_sheets')) * per90
    saves = _rating_num(meta.get('saves')) * per90
    xgc = _rating_num(meta.get('expected_goals_conceded')) * per90
    if pos == 'GKP':
        advanced = 0.42 * clean + 0.24 * saves + 0.20 * bonus + 0.14 * bps / 20.0
    elif pos == 'DEF':
        advanced = 0.30 * clean + 0.24 * defensive + 0.20 * xgi + 0.14 * bonus + 0.12 * bps / 20.0
    elif pos == 'MID':
        advanced = 0.41 * xgi + 0.22 * goals + 0.16 * assists + 0.13 * defensive + 0.08 * bonus
    else:
        advanced = 0.49 * xgi + 0.28 * goals + 0.17 * assists + 0.06 * bonus
    club = meta.get('team')
    try:
        club = int(club)
    except (ValueError, TypeError):
        club = None
    club_played = _pl_table_stats.get(club, {}).get('played', _rating_sample_gws)
    # Game-time is a distinct reliability signal; an injury does not erase talent.
    minutes_share = _rating_clamp(minutes / max(1.0, float(club_played) * 90.0))
    availability = _rating_clamp(_availability_factor(pid, dashboard_target_gw))
    draft_rank = _rating_num(_blended_draft_rank(pid), UNDRAFTED_PLAYER_RANK)
    draft_score = _rating_clamp(1.0 - (draft_rank - 1.0) / (UNDRAFTED_PLAYER_RANK - 1)) ** 0.70
    club_quality = _rating_clamp(0.65 * _pl_club_strength_score.get(club, 0.5) + 0.35 * _rating_club_form.get(club, 0.5))
    _rating_features[pid] = dict(position=pos, three=three, five=five, season=season_ppgw,
                                 advanced=advanced, availability=availability, minutes_share=minutes_share,
                                 draft=draft_score, club=club_quality, club_form=_rating_club_form.get(club, 0.5),
                                 minutes=minutes, starts=played)
    if minutes >= 90:
        for key in ('three', 'five', 'season', 'advanced'):
            _rating_distributions[pos][key].append(_rating_features[pid][key])

for _pos_groups in _rating_distributions.values():
    for _values in _pos_groups.values():
        _values.sort()


def _rating_percentile(pos, key, value):
    vals = _rating_distributions[pos].get(key, [])
    if len(vals) < 2 or abs(vals[-1] - vals[0]) < 1e-8:
        return 0.5
    # A percentile (rather than the largest/minimum) resists single-GW outliers.
    return _rating_bisect.bisect_right(vals, value) / len(vals)


# Rating calibration v2: raise the floor while preserving the elite ceiling.
# v1 used 26 + 72*w; v2 uses 35 + 63*w. This compresses the lower half upward
# without turning middling assets into 80+ players.
PLAYER_RATING_CALIBRATION_VERSION = 2
PLAYER_RATING_FLOOR = 35.0
PLAYER_RATING_SPAN = 63.0

def _calibrated_player_rating(weighted):
    return int(round(PLAYER_RATING_FLOOR + PLAYER_RATING_SPAN * _rating_clamp(weighted)))

def _legacy_rating_to_v2(value):
    try:
        old = float(value)
    except (TypeError, ValueError):
        return value
    # Inverse old scale (26..98) then apply v2 (35..98).
    weight = _rating_clamp((old - 26.0) / 72.0)
    return _calibrated_player_rating(weight)

def _rating_tier(value):
    try:
        score = float(value)
    except (TypeError, ValueError):
        score = 0.0
    if score >= 90: return 'platinum'
    if score >= 80: return 'gold'
    if score >= 70: return 'silver'
    return 'bronze'

_player_ratings_by_id = {}
_rating_previous = history.get('player_rating_previous', {}) or {}
_rating_old_version = int(history.get('player_rating_calibration_version', 1) or 1)
if _rating_old_version < PLAYER_RATING_CALIBRATION_VERSION:
    for _key, _prev in list(_rating_previous.items()):
        if isinstance(_prev, dict) and _prev.get('rating') is not None:
            _prev['rating'] = _legacy_rating_to_v2(_prev['rating'])
        elif isinstance(_prev, (int, float)):
            _rating_previous[_key] = _legacy_rating_to_v2(_prev)
for _entry in player_search_data:
    pid = int(_entry['id'])
    f = _rating_features[pid]
    pos = f['position']
    recent3 = _rating_percentile(pos, 'three', f['three'])
    recent5 = _rating_percentile(pos, 'five', f['five'])
    season = _rating_percentile(pos, 'season', f['season'])
    advanced = _rating_percentile(pos, 'advanced', f['advanced'])
    # Cap what a single strong appearance can do before we trust the numbers.
    sample_confidence = _rating_clamp(f['minutes'] / 720.0)
    prior = 0.65 * f['draft'] + 0.35 * f['club']
    recent3 = sample_confidence * recent3 + (1.0 - sample_confidence) * prior
    recent5 = sample_confidence * recent5 + (1.0 - sample_confidence) * prior
    season = sample_confidence * season + (1.0 - sample_confidence) * prior
    advanced = sample_confidence * advanced + (1.0 - sample_confidence) * prior
    # Availability and minutes are different: a brilliant but injured player
    # can retain talent while his current usable squad rating moves down.
    reliability = 0.60 * f['availability'] + 0.40 * f['minutes_share']
    components = {
        '3GW form': round(100 * recent3, 1),
        '5GW form': round(100 * recent5, 1),
        'Season output': round(100 * season, 1),
        'Draft pedigree': round(100 * f['draft'], 1),
        'PL club & form': round(100 * f['club'], 1),
        'Availability & minutes': round(100 * reliability, 1),
        'Underlying stats': round(100 * advanced, 1),
    }
    weighted = (0.23 * recent3 + 0.10 * recent5 + 0.20 * season
                + 0.14 * f['draft'] + 0.13 * f['club']
                + 0.11 * reliability + 0.09 * advanced)
    # Fixed calibration: scores do not artificially inflate just because the
    # weakest player in today's pool is poor or many players are injured.
    rating = _calibrated_player_rating(weighted)
    prior_rating = _rating_previous.get(str(pid), {})
    previous = prior_rating.get('rating') if isinstance(prior_rating, dict) else prior_rating
    delta = rating - int(previous) if isinstance(previous, (int, float)) else None
    detail = {'rating': rating, 'change': delta, 'breakdown': components,
              'club_form': round(100 * f['club_form'], 1),
              'minutes_share': round(100 * f['minutes_share'], 1),
              'matches_missed_estimate': max(0, int(_pl_table_stats.get(elements.get(pid, {}).get('team'), {}).get('played', 0)) - int(f['starts'])),
              'as_of': history.get('last_updated')}
    _player_ratings_by_id[pid] = detail
    _entry.update(player_rating=rating, rating_change=delta, rating_tier=_rating_tier(rating),
                  rating_breakdown=components,
                  club_form_score=detail['club_form'],
                  minutes_share=detail['minutes_share'],
                  matches_missed_estimate=detail['matches_missed_estimate'])

# Existing trade and value calculations remain independent of the /100 rating.
# Store the previous build for up/down indicators after the next scheduled run.
history['player_rating_previous'] = {str(pid): {'rating': r['rating']} for pid, r in _player_ratings_by_id.items()}

# ============================================================
# PERSISTENT PLAYER RATING HISTORY / RETROSPECTIVE TREND ESTIMATES
# ============================================================
# New GWs are observed ONCE, on the first build that sees them completed.
# Already-finished weeks from before this feature launched are reconstructed
# from per-GW FPL live statistics and the historical Premier League results.
# Historical medical availability, mid-season unowned club transfers and some
# older underlying metrics cannot always be recovered: mark those points as
# ESTIMATED, never pretend they are previously-recorded rating snapshots.
_RATING_COMPONENT_NAMES = ('3GW form', '5GW form', 'Season output',
                           'Draft pedigree', 'PL club & form',
                           'Availability & minutes', 'Underlying stats')
_rating_archive = history.setdefault('player_rating_history', {})
if _rating_old_version < PLAYER_RATING_CALIBRATION_VERSION:
    for _player_points in _rating_archive.values():
        if not isinstance(_player_points, dict):
            continue
        for _snapshot in _player_points.values():
            if isinstance(_snapshot, dict) and _snapshot.get('rating') is not None:
                _snapshot['rating'] = _legacy_rating_to_v2(_snapshot['rating'])
history['player_rating_calibration_version'] = PLAYER_RATING_CALIBRATION_VERSION
_rating_completed = sorted(set(int(g) for g in finished_gws))
_rating_latest_completed = _rating_completed[-1] if _rating_completed else 0


def _historic_club_last_five(as_of_gw):
    records = defaultdict(list)
    for fixture in _all_pl_fixtures:
        if not isinstance(fixture, dict) or not fixture.get('finished'):
            continue
        try:
            gw = int(fixture.get('event') or 0)
            if not gw or gw > as_of_gw:
                continue
            home, away = int(fixture['team_h']), int(fixture['team_a'])
            hs, aws = int(fixture['team_h_score']), int(fixture['team_a_score'])
        except (ValueError, KeyError, TypeError):
            continue
        order = (gw, str(fixture.get('kickoff_time') or ''))
        records[home].append((order, 3 if hs > aws else 1 if hs == aws else 0))
        records[away].append((order, 3 if aws > hs else 1 if hs == aws else 0))
    return {club: (sum(v for _, v in last) / (3.0 * len(last)) if last else 0.5)
            for club in _pl_team_meta_by_id
            for last in [sorted(records.get(club, []), key=lambda r: r[0])[-5:]]}


def _historical_rating_club_hints(gw):
    # When this player was actually rostered in the frozen GW, use that week's
    # pinned club instead of today's club. For previously-unowned players the
    # FPL live feed has no historical-club field; use the present club and
    # explicitly mark the entire reconstructed history as estimated.
    hints = {}
    reverse = {str(name): int(cid) for cid, name in teams_lookup.items()}
    for squad in (history.get('gameweeks', {}).get(str(gw), {}) or {}).get('teams', {}).values():
        for pick in squad.get('starters', []) + squad.get('bench', []):
            try:
                pid = int(pick['element_id'])
            except (TypeError, KeyError, ValueError):
                continue
            club = reverse.get(str(pick.get('team') or ''))
            if club:
                hints[pid] = club
    return hints


def _retrospective_player_rating_points(missing_gws):
    """Backfill missing finished GWs without future results leaking into scores."""
    if not missing_gws:
        return
    from collections import defaultdict as _defaultdict
    cumulative = _defaultdict(lambda: _defaultdict(float))
    gw_points = _defaultdict(dict)
    eligible = {int(row['id']): row for row in player_search_data}
    official_keys = ('expected_goal_involvements', 'goals_scored', 'assists',
                     'bonus', 'bps', 'defensive_contribution',
                     'clean_sheets', 'saves')

    for gw in _rating_completed:
        live = get_live_gw_data(gw)
        if not live:
            # An unavailable old API response must not become an invented
            # zero-scoring week in any historical rating.
            continue
        for pid, record in live.items():
            if pid not in eligible:
                continue
            stats = record.get('fpl_stats', {}) or {}
            acc = cumulative[pid]
            pts = _rating_num(record.get('points'))
            minutes = max(0.0, _rating_num(record.get('minutes')))
            gw_points[pid][gw] = pts
            acc['points'] += pts
            acc['minutes'] += minutes
            for key in official_keys:
                if key in stats:
                    acc[key] += _rating_num(stats.get(key))
                    acc['_available_' + key] += 1.0

        if gw not in missing_gws:
            continue
        club_hint = _historical_rating_club_hints(gw)
        club_form = _historic_club_last_five(gw)
        club_strength = _pl_club_strength_snapshot(gw)['scores']
        club_played = _pl_table_snapshot(gw)['stats']
        positions = _defaultdict(lambda: _defaultdict(list))
        per_player = {}
        elapsed = [g for g in _rating_completed if g <= gw]
        for pid, row in eligible.items():
            pos = row.get('position', '')
            acc = cumulative[pid]
            minutes = acc['minutes']
            three = statistics.mean([gw_points[pid].get(g, 0.0) for g in elapsed[-3:]])
            five = statistics.mean([gw_points[pid].get(g, 0.0) for g in elapsed[-5:]])
            season = acc['points'] / max(1, len(elapsed))
            per90 = 90.0 / max(270.0, minutes)
            has_advanced = any(acc.get('_available_' + k, 0) for k in official_keys)
            xgi = acc['expected_goal_involvements'] * per90
            goals = acc['goals_scored'] * per90
            assists = acc['assists'] * per90
            bonus = acc['bonus'] * per90
            bps = acc['bps'] * per90
            defensive = acc['defensive_contribution'] * per90
            clean = acc['clean_sheets'] * per90
            saves = acc['saves'] * per90
            if pos == 'GKP':
                advanced = .42 * clean + .24 * saves + .20 * bonus + .14 * bps / 20
            elif pos == 'DEF':
                advanced = .30 * clean + .24 * defensive + .20 * xgi + .14 * bonus + .12 * bps / 20
            elif pos == 'MID':
                advanced = .41 * xgi + .22 * goals + .16 * assists + .13 * defensive + .08 * bonus
            else:
                advanced = .49 * xgi + .28 * goals + .17 * assists + .06 * bonus
            club = club_hint.get(pid, elements.get(pid, {}).get('team'))
            try:
                club = int(club)
            except (TypeError, ValueError):
                club = None
            rank = _rating_num(_blended_draft_rank(pid), UNDRAFTED_PLAYER_RANK)
            draft = _rating_clamp(1 - (rank - 1) / (UNDRAFTED_PLAYER_RANK - 1)) ** .70
            quality = _rating_clamp(.65 * club_strength.get(club, .5) + .35 * club_form.get(club, .5))
            played = club_played.get(club, {}).get('played', len(elapsed))
            game_time = _rating_clamp(minutes / max(1, played * 90))
            per_player[pid] = dict(pos=pos, three=three, five=five, season=season,
                                   advanced=advanced, has_advanced=has_advanced,
                                   draft=draft, club=quality, club_form=club_form.get(club, .5),
                                   game_time=game_time, minutes=minutes, points=gw_points[pid].get(gw, 0))
            if minutes >= 90:
                for key in ('three', 'five', 'season'):
                    positions[pos][key].append(per_player[pid][key])
                if has_advanced:
                    positions[pos]['advanced'].append(advanced)
        for bucket in positions.values():
            for arr in bucket.values():
                arr.sort()

        def pct(pos, key, value):
            vals = positions[pos].get(key, [])
            if len(vals) < 2 or abs(vals[-1] - vals[0]) < 1e-8:
                return .5
            return _rating_bisect.bisect_right(vals, value) / len(vals)

        for pid, f in per_player.items():
            prior = .65 * f['draft'] + .35 * f['club']
            confidence = _rating_clamp(f['minutes'] / 720)
            def shrink(key):
                return confidence * pct(f['pos'], key, f[key]) + (1 - confidence) * prior
            recent3 = shrink('three')
            recent5 = shrink('five')
            season = shrink('season')
            advanced = shrink('advanced') if f['has_advanced'] else .5
            # Retrospective medical/suspension information was never captured;
            # use a neutral availability assumption, but preserve historical
            # actual minutes. These are estimates, not the historical API state.
            reliability = .6 * 1.0 + .4 * f['game_time']
            weighted = (.23 * recent3 + .10 * recent5 + .20 * season
                        + .14 * f['draft'] + .13 * f['club']
                        + .11 * reliability + .09 * advanced)
            components = (recent3, recent5, season, f['draft'], f['club'],
                          reliability, advanced)
            _rating_archive.setdefault(str(pid), {}).setdefault(str(gw), {
                'gw': gw, 'rating': _calibrated_player_rating(weighted),
                'source': 'estimated',
                'components': [int(round(100 * v)) for v in components],
                'club_form': int(round(100 * f['club_form'])),
                'points': int(round(f['points'])),
            })


# The current API is observed at the present build, not retroactively applied
# to a past GW. Earlier missing weeks are explicitly historical estimates.
_retro_gws = {gw for gw in _rating_completed if gw < _rating_latest_completed and
              any(str(gw) not in _rating_archive.get(str(pid), {})
                  for pid in _player_ratings_by_id)}
_retrospective_player_rating_points(_retro_gws)

for _pid, _detail in _player_ratings_by_id.items():
    _series = _rating_archive.setdefault(str(_pid), {})
    _actual = {
        'gw': _rating_latest_completed, 'rating': _detail['rating'],
        'source': 'observed',
        'components': [int(round(_detail['breakdown'][k])) for k in _RATING_COMPONENT_NAMES],
        'club_form': int(round(_detail['club_form'])),
        'points': int(_rating_num(all_player_gw_points.get(_pid, {}).get(_rating_latest_completed))),
    }
    # Once observed at GW close, lock it; a transfer, new status or next GW's
    # form must never silently rewrite the earlier snapshot.
    if _rating_latest_completed and str(_rating_latest_completed) not in _series:
        _series[str(_rating_latest_completed)] = dict(_actual)
    _actual['source'] = 'latest'
    _actual['captured_at'] = history.get('last_updated')
    _ordered = [_series[k] for k in sorted(_series, key=int)
                if int(k) <= _rating_latest_completed]
    # Always include the genuinely current rating, separately from the
    # frozen end-of-GW snapshot when the rating/components have moved.
    if not _ordered or any(_actual[k] != _ordered[-1][k]
                           for k in ('rating', 'components', 'club_form')):
        _ordered.append(_actual)
    _entry = _player_model_by_id.get(_pid) if '_player_model_by_id' in globals() else None
    # The model-by-id index is normally built later. The loop below instead
    # writes directly into the already available player_search_data records.
    _detail['historical_samples'] = _ordered

for _entry in player_search_data:
    _pid = int(_entry['id'])
    _points = _player_ratings_by_id.get(_pid, {})
    _entry['rating_history'] = _points.get('historical_samples', [])
    _entry['draft_active'] = bool(elements.get(_pid, {}).get('draft_active', True))
    _series = _entry['rating_history']
    # Movement uses the preceding GW, NOT the last hourly refresh.
    past = [p for p in _series if p.get('source') != 'latest']
    base = past[-2] if len(past) > 1 else None
    _entry['rating_gw_delta'] = (_entry['player_rating'] - base['rating']) if base else None

history['player_rating_history'] = _rating_archive


# Rebuild now that projection/value/heat/history fixture context has been added.
player_search_json=json.dumps(player_search_data,ensure_ascii=False)

# Capture departed/removed identities before enriching medical analytics.
# An absent bootstrap record is not in itself proof of a completed overseas transfer.
_departed_by_id = {}
for _gw_key, _snapshot in sorted(
    (history.get('gameweeks', {}) or {}).items(), key=lambda item: int(item[0])
):
    for _squad in (_snapshot.get('teams', {}) or {}).values():
        for _pick in (_squad.get('starters', []) or []) + (_squad.get('bench', []) or []):
            try:
                _old_id = int(_pick.get('element_id'))
            except (ValueError, TypeError):
                continue
            if _old_id in elements and fpl_id_for_draft(_old_id) in classic_elements_by_fpl_id:
                continue
            _departed_by_id[_old_id] = {
                'id': _old_id,
                'name': _pick.get('web_name') or f'Player {_old_id}',
                'team': _pick.get('team') or 'Former PL club unknown',
                'position': _pick.get('position') or '—',
                'fantasy_team': _squad.get('manager') or 'Former owner unknown',
                'last_seen_gw': int(_gw_key),
            }
_departed_player_rows = sorted(
    _departed_by_id.values(),
    key=lambda row: (row['team'], row['name'])
)

# Every flagged FPL player, including undrafted/unowned assets.
injury_list_rows = []
for _row in player_search_data:
    _availability = _row.get('availability', {}) or {}
    _status = _availability.get('status', 'a')
    _chance = _availability.get('chance_next')
    if _status == 'a' and not _availability.get('news') and _chance in (None, 100):
        continue
    _pid = int(_row.get('id') or 0)
    _healthy_next = _player_weekly_projection(
        _pid, _global_position_baselines, _global_league_player_mean,
        target_gw=dashboard_target_gw, apply_availability=False
    )
    _actual_next = _healthy_next * _availability_factor(_pid, dashboard_target_gw)
    injury_list_rows.append({
        'points_at_risk': round(max(0.0, _healthy_next - _actual_next), 2),
        'healthy_next_points': round(_healthy_next, 2),
        'id':_row.get('id'), 'name':_row.get('name'),
        'team':_row.get('team'), 'position':_row.get('position'),
        'fantasy_team':_row.get('fantasy_team') or 'Free Agent',
        'status':_status, 'news':_availability.get('news',''),
        'news_updated':_availability.get('news_updated'),
        'chance_next':_chance,
        'availability_next':_row.get('availability_next',1),
        'projected_remaining_points':_row.get('projected_remaining_points',0),
        'next_fixtures':_player_next_fixture_run(_row.get('id'),3),
    })
# Newly flagged since the previous successful dashboard build; retain the
# previous set across rebuilds and do not report all cases as new on first run.
_prior_health = history.get('analytics_health_previous')
_current_health = {str(r['id']): {'status':r['status'], 'news':r['news']}
                   for r in injury_list_rows}
new_health_events = []
if isinstance(_prior_health, dict):
    for _row in injury_list_rows:
        _before = _prior_health.get(str(_row['id']))
        if _before is None or _before.get('status') != _row['status'] or _before.get('news') != _row['news']:
            new_health_events.append({**_row, 'change_type': 'New flag' if _before is None else 'Updated report'})
history['analytics_health_previous'] = _current_health
# Historical ID re-use is possible: only list deleted identities, not current
# IDs with a different name, which require manual confirmation.
_prior_removed = set(map(str, history.get('analytics_departures_previous', [])))
new_departure_events = [r for r in _departed_player_rows if str(r['id']) not in _prior_removed] if 'analytics_departures_previous' in history else []
history['analytics_departures_previous'] = [r['id'] for r in _departed_player_rows]
health_analytics_data = {
    'flagged': injury_list_rows,
    'new': new_health_events,
    'removed': _departed_player_rows,
    'new_removed': new_departure_events,
    'pl_clubs': sorted(set(teams_lookup.values())),
    'fantasy_teams': list(managers),
    'target_gw': dashboard_target_gw,
    'generated_at': datetime.now(timezone.utc).isoformat(timespec='seconds')
}
injury_list_json = json.dumps(injury_list_rows, ensure_ascii=False)
# Health change tracking must persist across scheduled dashboard runs.
with open(HISTORY_FILE, 'w', encoding='utf-8') as _health_out:
    json.dump(history, _health_out, indent=2, ensure_ascii=False)


# Enrich player-facing datasets now that real PL fixture helpers are available.
_player_model_by_id={int(r.get('id',0) or 0):r for r in player_search_data}
for _row in player_search_data:
    _pid = int(_row.get("id", 0) or 0)
    _row["next_fixtures"] = _player_next_fixture_run(_pid, 3)
player_search_json = json.dumps(player_search_data, ensure_ascii=False)

# Club Explorer: the full player pool, including players never selected in McDraft.
# Store independent per-GW totals so old clubs remain comparable after ownership churn.
club_explorer_data = {}
for _club_id, _club_meta in _pl_team_meta_by_id.items():
    _club_name = _club_meta.get('name', teams_lookup.get(_club_id, str(_club_id)))
    _club_players = [r for r in player_search_data if int(elements.get(int(r.get('id',0)), {}).get('team') or 0) == int(_club_id)]
    _gw_points = {}
    for _pid, _scores in all_player_gw_points.items():
        if int(elements.get(int(_pid), {}).get('team') or 0) != int(_club_id):
            continue
        for _gw, _pts in _scores.items():
            _gw_points[int(_gw)] = _gw_points.get(int(_gw), 0) + float(_pts or 0)
    _fixtures = []
    for _fx in _all_pl_fixtures:
        if not isinstance(_fx, dict) or _fx.get('event') is None:
            continue
        _home, _away = int(_fx.get('team_h') or 0), int(_fx.get('team_a') or 0)
        if _club_id not in (_home, _away):
            continue
        _gw = int(_fx.get('event'))
        _is_home = _home == _club_id
        _opp = _away if _is_home else _home
        _known_gw = min(max(0, _gw - 1), max([int(g) for g in finished_gws] or [0]))
        _str = _pl_club_strength_snapshot(_known_gw)['scores']
        _relative = _str.get(_opp,0.5) - _str.get(_club_id,0.5)
        # Ratings are display-only: predictive player projections continue to use the shared model.
        _difficulty = max(1.0, min(5.0, 3.0 + 2.4*_relative + (-0.35 if _is_home else 0.35)))
        _fixtures.append({'gw': _gw, 'opponent': _pl_team_meta_by_id.get(_opp,{}).get('short_name',teams_lookup.get(_opp,'—')),
                          'home': _is_home, 'difficulty': round(round(_difficulty*4)/4,2),
                          'finished': bool(_fx.get('finished')),
                          'score': (str(_fx.get('team_h_score',0))+'–'+str(_fx.get('team_a_score',0))) if _fx.get('finished') else None})
    _tab = _pl_table_stats.get(_club_id,{})
    club_explorer_data[str(_club_id)] = {
        'id':int(_club_id),'name':_club_name,'short':_club_meta.get('short_name',_club_name),
        'position':_pl_position.get(_club_id,0),'pl_points':_tab.get('pts',0),
        'fpl_points':round(_pl_total_fpl_points.get(_club_id,0),1),
        'fantasy_strength':round(_pl_club_strength_score.get(_club_id,0.5)*100,1),
        'official_draft_rank':round(_pl_team_draft_rank.get(_club_id,UNDRAFTED_PLAYER_RANK),1),
        'gw_points':[{'gw':_gw,'points':round(_gw_points.get(_gw,0),1)} for _gw in range(1,max([int(g) for g in finished_gws] or [0])+1)],
        'fixtures':sorted(_fixtures,key=lambda f:f['gw']),
        'player_ids':[int(r['id']) for r in _club_players]
    }
club_explorer_json = json.dumps(club_explorer_data, ensure_ascii=False)

for _manager, _recs in free_agent_recommendations.items():
    for _rec in _recs:
        _pid = int(_rec.get("id", 0) or 0)
        _rec["next_fixtures"] = _player_next_fixture_run(_pid, 3)
        _rec["fixture_run_score"] = round(_fixture_run_score(_pid, 3), 3)
        _model=_player_model_by_id.get(_pid,{})
        _rec["hot_cold_score"] = _model.get("hot_cold_score",0)
        _rec["hot_cold_label"] = _model.get("hot_cold_label","Neutral")
        _rec["projected_season_points"] = _model.get("projected_season_points",0)
        _rec["player_value"] = _model.get("player_value",50)
        # Fixtures, long-run value and current heat nudge the ranking, but do not overwhelm player quality.
        _rec["recommendation_score"] = (float(_rec.get("recommendation_score", 0) or 0)
            + ((_rec["fixture_run_score"] - 1.0) * 18.0)
            + (float(_rec.get("player_value",50))-50.0)*0.10
            + max(-8.0,min(8.0,float(_rec.get("hot_cold_score",0) or 0)*0.08)))
    _recs.sort(key=lambda x: (-float(x.get("recommendation_score",0) or 0), -float(x.get("total_points",0) or 0), -float(x.get("form",0) or 0), x.get("name","")))
free_agent_recommendations_json = json.dumps(free_agent_recommendations, ensure_ascii=False)

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


def _build_current_squad_strength(target_gw=None):
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
            league_draft_rank = _league_draft_rank(pid)
            official_draft_rank = _official_draft_rank(pid)
            blended_draft_rank = _blended_draft_rank(pid)

            projected_players.append({
                "id": pid,
                "name": meta.get("web_name", f"Player {pid}"),
                "position": pos,
                "projection": _player_weekly_projection(
                    pid, position_baselines, league_player_mean,
                    target_gw=(dashboard_target_gw if target_gw is None else target_gw),
                ),
                "draft_rank": blended_draft_rank,
                "league_draft_rank": league_draft_rank,
                "official_draft_rank": official_draft_rank,
                "fixture_multiplier": _player_fixture_multiplier(
                    pid, (dashboard_target_gw if target_gw is None else target_gw)
                ),
                "fixtures": _player_fixture_components(
                    pid, (dashboard_target_gw if target_gw is None else target_gw)
                ),
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

        # Sum the blended McDraft/FPL Draft pedigree ranks. Lower is better.
        # Players without an official rank fall back to their McDraft rank.
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


current_squad_strength = _build_current_squad_strength(dashboard_target_gw)


# ============================================================
# FIXTURE-AWARE LUCK + POWER RECALIBRATION
# ============================================================
# These metrics are defined earlier for backwards compatibility, then refined
# here once the evolving PL-strength model and fixture projections exist.
def _manager_historical_pl_fixture_factor(manager, gw):
    """Average real-PL fixture multiplier faced by the manager's starting XI."""
    snap=history.get('gameweeks',{}).get(str(gw),{})
    team_data=next((t for t in snap.get('teams',{}).values() if t.get('manager')==manager),None)
    if not team_data:
        return 1.0
    weights=[]
    for p in (team_data.get('starters',[]) or []):
        try: pid=int(p.get('element_id'))
        except (TypeError,ValueError): continue
        mult=float(_player_fixture_multiplier(pid,gw) or 1.0)
        # Captain gets a little extra representation because twice the score is exposed.
        w=2.0 if p.get('is_captain') else 1.0
        weights.extend([mult]*int(w))
    return statistics.mean(weights) if weights else 1.0

fixture_neutral_expected_league_points={m:0.0 for m in managers}
manager_pl_fixture_factor_by_gw={m:{} for m in managers}
for _gw in finished_gws:
    _neutral={}
    for _m in managers:
        _score=official_gw_score(_m,_gw)
        if _score is None: continue
        _factor=_manager_historical_pl_fixture_factor(_m,_gw)
        manager_pl_fixture_factor_by_gw[_m][int(_gw)]=_factor
        # Only neutralise a sensible range: fixture context matters, but should
        # never erase what actually happened on the pitch.
        _factor=max(0.82,min(1.18,float(_factor or 1.0)))
        _neutral[_m]=float(_score)/_factor
    if len(_neutral)>=2:
        for _m,_score in _neutral.items():
            _vp=[]
            for _opp,_opp_score in _neutral.items():
                if _opp==_m: continue
                _vp.append(3.0 if _score>_opp_score else (1.0 if abs(_score-_opp_score)<1e-9 else 0.0))
            if _vp: fixture_neutral_expected_league_points[_m]+=statistics.mean(_vp)

# Luck now asks: how many league points did you get versus what your performance
# would normally earn after allowing for the strength of the PL fixtures faced?
expected_league_points=fixture_neutral_expected_league_points
luck_index={m:actual_finished_league_points.get(m,0.0)-expected_league_points.get(m,0.0) for m in managers}

# Power rankings now include forward-looking, fixture-aware current squad strength.
fixture_aware_squad_points={m:float(current_squad_strength.get(m,{}).get('managed_xi',0) or 0) for m in managers}
norm_fixture_aware_squad=_normalize_0_100(fixture_aware_squad_points)
power_score={
    m:(norm_recent_form.get(m,0)*0.25
       +norm_season_quality.get(m,0)*0.20
       +norm_fixture_aware_squad.get(m,0)*0.25
       +norm_squad_management.get(m,0)*0.10
       +norm_league_position.get(m,0)*0.20)
    for m in managers
}
power_rankings=sorted(managers,key=lambda m:(-power_score[m],m))

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

    completed_gws = set(int(gw) for gw in finished_gws)
    future_gws = sorted(
        int(gw) for gw in full_fixture_schedule
        if int(gw) not in completed_gws
    )
    # Rebuild optimal XIs for every remaining fantasy GW using the actual PL
    # fixtures in that week. This lets a manager's expected score rise/fall as
    # their players hit easy runs, hard runs, blanks or doubles.
    squad_strength_by_gw = {
        gw: _build_current_squad_strength(gw)
        for gw in future_gws
    }

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
        expected_by_gw = {}
        for _gw in future_gws:
            _gw_squad = squad_strength_by_gw.get(_gw, {}).get(manager, {})
            _gw_squad_score = float(_gw_squad.get("managed_xi", squad_score) or squad_score)
            _gw_raw = (
                (0.52 * _gw_squad_score)
                + (0.23 * recent_mean)
                + (0.10 * season_mean)
                + (0.15 * league_mean)
            )
            # Same early-season calibration, but fixture-aware squad strength is
            # deliberately the largest component of the future-week forecast.
            expected_by_gw[_gw] = (
                ((0.55 + (0.40 * evidence_weight)) * _gw_raw)
                + ((0.45 - (0.40 * evidence_weight)) * league_mean)
            )

        scoring_profile[manager] = {
            "expected_score": expected,
            "expected_score_by_gw": expected_by_gw,
            "volatility": volatility,
            "squad_score": squad_score,
            "optimal_xi": float(squad.get("optimal_xi", squad_score) or squad_score),
            "selection_efficiency": float(squad.get("selection_efficiency", 100.0) or 100.0),
            "squad_draft_rank_total": int(squad.get("squad_draft_rank_total", UNDRAFTED_PLAYER_RANK * 15) or 0),
        }

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
            mu1 = float(p1.get("expected_score_by_gw", {}).get(gw, p1["expected_score"]))
            mu2 = float(p2.get("expected_score_by_gw", {}).get(gw, p2["expected_score"]))
            s1 = max(0, round(rng.gauss(mu1 + week_shock[gw], p1["volatility"])))
            s2 = max(0, round(rng.gauss(mu2 + week_shock[gw], p2["volatility"])))
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
            "model_weekly_score_by_gw": scoring_profile[m].get("expected_score_by_gw", {}),
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
# SEASON SIMULATOR — shared fixture-aware Monte Carlo inputs
# ============================================================
# The simulation itself runs inside the generated static HTML, so changing
# scenarios never calls the FPL API, rewrites history, or needs a server.
def _season_simulator_payload():
    manager_names = list(current_standings)
    completed = {int(gw) for gw in finished_gws}
    fixtures = []
    for gw, rows in sorted(full_fixture_schedule.items()):
        if int(gw) in completed:
            continue
        for fixture in rows:
            a, b = fixture.get('team1'), fixture.get('team2')
            if a in manager_names and b in manager_names and a != b:
                fixtures.append({'gw': int(gw), 'home': a, 'away': b})
    fixtures.sort(key=lambda r: (r['gw'], r['home'], r['away']))

    # Current LP/PF are reconstructed from final results only: ongoing scores
    # should not become permanent points when the current GW is simulated.
    actual_lp = {m: 0 for m in manager_names}
    actual_pf = {m: 0 for m in manager_names}
    actual_wdl = {m: {'wins': 0, 'draws': 0, 'losses': 0} for m in manager_names}
    seen = set()
    for match in matches_sorted:
        try:
            gw = int(match.get('event', 0) or 0)
        except (TypeError, ValueError):
            continue
        if gw not in completed:
            continue
        a, b = match.get('entry_1_name'), match.get('entry_2_name')
        if a not in actual_lp or b not in actual_lp or a == b:
            continue
        # A duplicate refresh should not count a fixture twice.
        key = (gw, tuple(sorted((a, b))))
        if key in seen:
            continue
        seen.add(key)
        s1 = round(float(match.get('entry_1_points', 0) or 0))
        s2 = round(float(match.get('entry_2_points', 0) or 0))
        actual_pf[a] += s1
        actual_pf[b] += s2
        if s1 > s2:
            actual_lp[a] += 3
            actual_wdl[a]['wins'] += 1
            actual_wdl[b]['losses'] += 1
        elif s2 > s1:
            actual_lp[b] += 3
            actual_wdl[b]['wins'] += 1
            actual_wdl[a]['losses'] += 1
        else:
            actual_lp[a] += 1
            actual_lp[b] += 1
            actual_wdl[a]['draws'] += 1
            actual_wdl[b]['draws'] += 1

    profiles = {}
    for manager in manager_names:
        pred = season_prediction.get(manager, {})
        raw_by_gw = pred.get('model_weekly_score_by_gw', {}) or {}
        profiles[manager] = {
            'weekly_mean': round(float(pred.get('model_weekly_score', 45.0) or 45.0), 3),
            'by_gw': {str(int(gw)): round(float(value), 3) for gw, value in raw_by_gw.items()},
            'sd': round(max(4.0, float(pred.get('model_volatility', 12.0) or 12.0)), 3),
            'completed_samples': len(raw_score_by_gw.get(manager, [])),
            'current_lp': actual_lp[manager],
            'current_pf': actual_pf[manager],
            'current_wdl': actual_wdl[manager],
            'current_rank': (manager_names.index(manager) + 1),
        }

    # Current Draft IDs and fixture-aware player projections power bespoke
    # trade/waiver/injury scenarios without mutating actual league rosters.
    rosters = _current_roster_by_manager()
    upcoming_gws = sorted({int(f['gw']) for f in fixtures})
    player_pool = []
    for pid, meta in sorted(elements.items()):
        pid = int(pid)
        pos = positions_lookup.get(meta.get('element_type'), '')
        if pos not in ('GKP', 'DEF', 'MID', 'FWD'):
            continue
        player_pool.append({
            'id': pid,
            'name': meta.get('web_name') or f'Player {pid}',
            'position': pos,
            'club': teams_lookup.get(meta.get('team'), '—'),
            'owner': next((m for m, ids in rosters.items() if pid in ids), 'Free Agent'),
            'by_gw': {
                str(gw): round(float(_player_weekly_projection(
                    pid, _global_position_baselines, _global_league_player_mean,
                    target_gw=gw
                ) or 0), 3)
                for gw in upcoming_gws
            },
        })

    return {
        'managers': manager_names,
        'colors': {name: MANAGER_COLOR_MAP.get(name, '#38bdf8') for name in manager_names},
        'last_completed_gw': max(completed) if completed else 0,
        'fixtures': fixtures,
        'profiles': profiles,
        'all_fixture_gws': sorted(set(int(gw) for gw in full_fixture_schedule.keys())),
        'in_progress_gw': int(dashboard_target_gw or 0) if dashboard_game_state == 'live' else None,
        'confidence': _prediction_confidence_meta(len(completed)).get('label', 'Unknown'),
        'seed': int(LEAGUE_ID) + 2026,
        'rosters': {m: sorted(set(int(pid) for pid in ids)) for m, ids in rosters.items()},
        'player_pool': player_pool,
        'formations': LEGAL_FORMATIONS,
    }


season_simulator_json = json.dumps(_season_simulator_payload(), ensure_ascii=False, separators=(',', ':'))


def season_simulator_html():
    return '''<div class="simulator-shell">
      <div class="card sim-hero">
        <div><span class="relationship-eyebrow">MONTE CARLO · REMAINING MATCHES</span>
          <h2>McDraft Season Simulator</h2>
          <p class="card-description">Replay every remaining scheduled McDraft fixture thousands of times using the same weekly player-and-fixture-aware squad projections behind your existing season forecast. Change the assumptions, explore each manager's possible finishing positions, and compare the effects of different scenarios. All simulations run locally in this page.</p>
        </div>
        <div class="sim-status-puck" id="sim-run-status" aria-live="polite">Ready to simulate</div>
      </div>
      <div class="card sim-controls-card">
        <div class="sim-controls-grid">
          <label>Focus manager<select id="sim-manager" onchange="seasonSimConfigurationChanged()"></select></label>
          <label>Scenario effect lasts<select id="sim-horizon" onchange="seasonSimConfigurationChanged()"><option value="3">Next 3 gameweeks</option><option value="5" selected>Next 5 gameweeks</option><option value="10">Next 10 gameweeks</option><option value="999">Rest of the season</option></select></label>
          <label>Monte Carlo samples<select id="sim-samples" onchange="seasonSimConfigurationChanged()"><option value="1500">1,500 · quick</option><option value="3000" selected>3,000 · balanced</option><option value="7500">7,500 · detailed</option></select></label>
          <button class="sim-run-button" type="button" onclick="runSeasonScenarios()">↻ Run scenarios</button>
        </div>
        <div class="sim-custom-controls">
          <div><strong>Custom points adjustment</strong><p class="card-description">Apply a hypothetical change to your chosen manager's expected points in each affected gameweek. Useful for testing a proposed transfer or lineup change, without pretending any move has actually happened.</p></div>
          <label><input type="range" id="sim-custom-delta" min="-12" max="12" step="0.5" value="3" oninput="seasonSimCustomChanged(this.value)" onchange="seasonSimConfigurationChanged()"><b id="sim-custom-delta-value">+3.0 pts/GW</b></label>
        </div>
        <div class="sim-scenario-switcher" id="sim-scenario-switcher" role="group" aria-label="Simulation scenarios"></div>
        <div class="sim-model-note" id="sim-model-note"></div>
      </div>
      <div class="card sim-builder-card">
        <div class="sim-section-head"><div><span class="relationship-eyebrow">WHAT-IF WORKSHOP · YOUR OWN TRANSFER UNIVERSE</span>
          <h2>Build a custom season</h2><p class="card-description">Stack up to six hypothetical moves and run them as one extra Monte Carlo scenario. Trades affect both managers; injuries trigger the best available bench cover; waiver moves replace one squad player with a free agent. No actual rosters or results are changed.</p></div>
          <span class="sim-builder-count" id="sim-builder-count">No moves added</span>
        </div>
        <div class="sim-builder-controls">
          <label>What if…<select id="sim-action-type" onchange="simBuilderTypeChanged()">
            <option value="trade">Two managers make a trade</option>
            <option value="injury">A player is unavailable</option>
            <option value="waiver">A team signs a free agent</option>
            <option value="points">A team's scoring changes</option>
          </select></label>
          <label>Starting from<select id="sim-action-start" onchange="simBuilderOptionsChanged()"><option value="0">Next unplayed GW</option><option value="1">One GW later</option><option value="2">Two GWs later</option><option value="4">Four GWs later</option></select></label>
        </div>
        <div class="sim-builder-type-panel" id="sim-builder-trade">
          <div class="sim-builder-controls sim-builder-trade-controls">
            <label>First manager<select id="sim-trade-team-a" onchange="simBuilderOptionsChanged()"></select></label>
            <label>Player they send<select id="sim-trade-player-a" onchange="simBuilderOptionsChanged()"></select></label>
            <label>Second manager<select id="sim-trade-team-b" onchange="simBuilderOptionsChanged()"></select></label>
            <label>Player they send<select id="sim-trade-player-b"></select></label>
          </div><p class="sim-helper-note">Same-position swaps preserve legal squad composition; both managers' projected optimal XIs are recalculated.</p>
        </div>
        <div class="sim-builder-type-panel" id="sim-builder-injury" hidden>
          <div class="sim-builder-controls">
            <label>Affected manager<select id="sim-injury-team" onchange="simBuilderOptionsChanged()"></select></label>
            <label>Unavailable player<select id="sim-injury-player"></select></label>
            <label>Gameweeks missed<select id="sim-injury-weeks"><option value="1">1 GW</option><option value="2">2 GWs</option><option value="3" selected>3 GWs</option><option value="5">5 GWs</option><option value="8">8 GWs</option><option value="999">Rest of season</option></select></label>
          </div><p class="sim-helper-note">Models complete absence for the chosen period; it does not predict a real injury or recovery date.</p>
        </div>
        <div class="sim-builder-type-panel" id="sim-builder-waiver" hidden>
          <div class="sim-builder-controls sim-builder-trade-controls">
            <label>Manager<select id="sim-waiver-team" onchange="simBuilderOptionsChanged()"></select></label>
            <label>Drop<select id="sim-waiver-out" onchange="simBuilderOptionsChanged()"></select></label>
            <label>Sign free agent<select id="sim-waiver-in"></select></label>
          </div><p class="sim-helper-note">Only current free agents in the same position are offered as replacements.</p>
        </div>
        <div class="sim-builder-type-panel" id="sim-builder-points" hidden>
          <div class="sim-builder-controls">
            <label>Manager<select id="sim-points-team"></select></label>
            <label>Extra / fewer expected points per GW<input type="number" id="sim-points-delta" min="-20" max="20" step="0.5" value="3"></label>
            <label>Effect lasts<select id="sim-points-weeks"><option value="3">3 GWs</option><option value="5" selected>5 GWs</option><option value="10">10 GWs</option><option value="999">Rest of season</option></select></label>
          </div>
        </div>
        <div class="sim-builder-actions"><button type="button" class="sim-build-add" onclick="simAddCustomAction()">＋ Add to scenario</button>
          <button type="button" class="sim-build-run" onclick="simRunCustomMoves()">▶ Simulate my moves</button>
          <button type="button" class="sim-build-clear" onclick="simClearCustomActions()">Clear all</button></div>
        <div class="sim-save-variant-row"><label>Save a comparison version<input id="sim-variant-name" type="text" maxlength="50" placeholder="e.g. Haaland trade only"></label><button type="button" class="sim-save-variant" onclick="simSaveCustomVariant()">Save simulated version</button><span class="sim-helper-note">Keep up to four named custom scenarios for side-by-side comparison in this browser session.</span></div>
        <div id="sim-saved-variants" class="sim-saved-variants" aria-label="Saved what-if scenarios"></div>
        <div class="sim-builder-feedback" id="sim-builder-feedback" aria-live="polite"></div>
        <div class="sim-build-list" id="sim-build-list" aria-label="Hypothetical moves"></div>
        <div id="sim-custom-effects" class="sim-custom-effects"></div>
      </div>
      <div class="sim-metric-grid" id="sim-selected-metrics"></div>
      <div class="sim-dual-grid">
        <div class="card sim-chart-card"><h2>Finishing-position distribution</h2><p class="card-description" id="sim-distribution-desc">Select a scenario to compare outcomes against the baseline.</p><div id="sim-position-chart"></div></div>
        <div class="card sim-chart-card sim-trajectory-card"><h2>All managers · projected league points</h2><p class="card-description">Every manager's mean simulated league-points path, coloured by team. Select several managers to compare their trajectories. The focused manager's 10th–90th percentile range can be shown separately.</p>
          <div class="sim-team-filter" id="sim-trajectory-filter" aria-label="Filter league-point trajectories"></div>
          <label class="sim-band-toggle"><input id="sim-trajectory-band" type="checkbox" checked onchange="simRenderTrajectoryOnly()"> Focus team's 10th–90th range</label>
          <div id="sim-trajectory-chart"></div>
        </div>
      </div>
      <div class="card"><div class="sim-section-head"><div><h2>Scenario comparison</h2><p class="card-description">The same random draws are reused across scenarios so differences reflect your assumptions, rather than different lucky simulation runs. Each row tracks your selected manager.</p></div><span id="sim-compare-count" class="muted"></span></div><div class="sim-table-wrap" id="sim-compare-table"></div></div>
      <div class="card"><h2>Whole-league outcomes</h2><p class="card-description">Projected total league points, simulated 10th–90th finishing-position ranges and finishing-position heatmap for every manager under the selected scenario. Sort order follows expected league points; these are scenario-model results, not guarantees.</p><div id="sim-league-table" class="sim-table-wrap"></div></div>
      <div class="card"><h2>How the simulator works</h2><div class="sim-method-grid"><div><b>Actual standings are locked</b><p>Only completed gameweeks contribute fixed results. Live scores are not locked: an active gameweek is simulated from its full pre-match forecast.</p></div><div><b>Each future matchup is played</b><p>Both teams receive a score sampled from their GW-specific expected points and historical volatility, with shared league-wide weekly shocks.</p></div><div><b>Rankings use real tie-breakers</b><p>Every sampled season awards 3/1/0 league points and orders tied managers by total points scored; draws occur only for tied simulated integer scores.</p></div><div><b>Scenarios are hypothetical</b><p>Presets change expected scores. Custom moves recompute optimal projected XIs using the current snapshot and legal formations; injuries remove players temporarily, trades and waiver changes last from their chosen start. Future real transfers and shocks remain unknown.</p></div></div></div>
    </div>'''





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

    target_gw = int(fixture_prediction_gw or dashboard_target_gw or 0)
    mu1 = float((p1.get("model_weekly_score_by_gw", {}) or {}).get(target_gw, p1.get("model_weekly_score", 45.0)) or 45.0)
    mu2 = float((p2.get("model_weekly_score_by_gw", {}) or {}).get(target_gw, p2.get("model_weekly_score", 45.0)) or 45.0)
    # A little extra match-to-match variance avoids overconfident favourites.
    sd1 = max(float(p1.get("model_volatility", 10.0) or 10.0), 4.0) * 1.15
    sd2 = max(float(p2.get("model_volatility", 10.0) or 10.0), 4.0) * 1.15

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
    # Start less certain about the favourite, then let actual season data
    # gradually replace the neutral prior. A draw is an exact integer-score
    # tie in Draft, NOT the ~15% frequency typical of football match results.
    evidence = min(1.0, max(0.0, (completed_count / 15.0) ** 1.15))
    neutral_draw = 3.0
    neutral_win = (100.0 - neutral_draw) / 2.0
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


def _fair_fractional_odds(probability_pct):
    """Convert a model percentage into approximate fair UK fractional odds.

    Use familiar betting-price fractions for readability, selecting the one
    whose implied probability is closest to the actual model probability.
    These are display prices, not actual bookmaker odds or model adjustments.
    """
    try:
        pct = float(probability_pct)
    except (TypeError, ValueError):
        return "—"
    if not math.isfinite(pct) or pct <= 0.0:
        return "—"
    if pct >= 100.0:
        return "0/1"
    exact_ratio = (100.0 - pct) / pct
    # Prevent a finite but extreme price being rounded up to zero/one.
    if exact_ratio < 1.0 / 100.0:
        return f"1/{min(999999, max(101, round(1.0 / exact_ratio)))}"
    if exact_ratio > 1000.0:
        return f"{min(999999, round(exact_ratio))}/1"

    standard_prices = [
        (1,100),(1,80),(1,66),(1,50),(1,40),(1,33),(1,28),
        (1,25),(1,20),(1,16),(1,14),(1,12),(1,10),(1,8),
        (1,7),(1,6),(1,5),(2,9),(1,4),(2,7),(3,10),(1,3),
        (4,11),(2,5),(4,9),(1,2),(8,15),(4,7),(3,5),
        (8,13),(4,6),(8,11),(4,5),(5,6),(10,11),
        (1,1),(11,10),(6,5),(5,4),(11,8),(6,4),
        (13,8),(7,4),(15,8),(2,1),(9,4),(5,2),(11,4),
        (3,1),(10,3),(7,2),(4,1),(9,2),(5,1),(11,2),
        (6,1),(13,2),(7,1),(15,2),(8,1),(17,2),(9,1),
        (10,1),(11,1),(12,1),(14,1),(16,1),(18,1),
        (20,1),(22,1),(25,1),(28,1),(33,1),(40,1),
        (50,1),(66,1),(80,1),(100,1),(125,1),(150,1),
        (200,1),(250,1),(500,1),(1000,1),
    ]
    numerator, denominator = min(
        standard_prices,
        key=lambda ratio: abs(100.0 * ratio[1] / (ratio[0] + ratio[1]) - pct),
    )
    return f"{numerator}/{denominator}"


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
<td title="Model probability: {odds['team1_win']:.1f}%"><b>{_fair_fractional_odds(odds['team1_win'])}</b></td>
<td title="Model probability: {odds['draw']:.1f}%">{_fair_fractional_odds(odds['draw'])}</td>
<td title="Model probability: {odds['team2_win']:.1f}%"><b>{_fair_fractional_odds(odds['team2_win'])}</b></td>
<td class="manager-name">{escape_html(t2)}</td>
<td>{odds["team1_mean"]:.1f}–{odds["team2_mean"]:.1f}</td>
<td>{odds["team1_low"]:.0f}–{odds["team1_high"]:.0f} / {odds["team2_low"]:.0f}–{odds["team2_high"]:.0f}</td>
<td>{_confidence_badge(odds.get("confidence"))}</td>
</tr>'''

    return f'''
<p class="card-description">Fair fractional odds (no bookmaker margin), converted from the same model percentages shown in the War Room. Hover over a price for its underlying probability. Lower odds indicate a more likely outcome.</p>
<div class="table-wrap"><table>
<thead><tr><th>Team</th><th>Win odds</th><th>Draw odds</th><th>Win odds</th><th>Team</th><th>Avg Score</th><th>80% Score Range</th><th>Confidence</th></tr></thead>
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
    return {
        draft_id: out[fpl_id_for_draft(draft_id)]
        for draft_id in elements
        if fpl_id_for_draft(draft_id) in out
    }


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
<td title="Model probability: {odds['team1_win']:.1f}%"><b>{_fair_fractional_odds(odds['team1_win'])}</b></td>
<td title="Model probability: {odds['draw']:.1f}%">{_fair_fractional_odds(odds['draw'])}</td>
<td title="Model probability: {odds['team2_win']:.1f}%"><b>{_fair_fractional_odds(odds['team2_win'])}</b></td>
<td>{odds['players_left2']}</td>
<td>{odds['current2']}</td>
<td class="manager-name">{escape_html(odds['team2'])}</td>
<td>{odds['final1_mean']:.1f}–{odds['final2_mean']:.1f}</td>
</tr>"""

    return f"""<p class="card-description">Live fair fractional odds (no bookmaker margin), based on current XI points and remaining players. Hover over a price for the model probability. A late live draw may legitimately be much more likely than a pre-match draw.</p>
<div class="table-wrap"><table>
<thead><tr><th>Team</th><th>Now</th><th>Left</th><th>Win odds</th><th>Draw odds</th><th>Win odds</th><th>Left</th><th>Now</th><th>Team</th><th>Projected Final</th></tr></thead>
<tbody>{rows}</tbody></table></div>"""

# ============================================================
# MCDRAFT LIVE CENTRE
# ============================================================
# Matchday-only hub. It deliberately reuses the same XI-derived score and
# Monte Carlo functions as the Gameweeks page so there is one source of truth.

