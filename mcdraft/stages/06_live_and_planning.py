def _live_full_stats_lookup():
    """Return the Classic live payload keyed by Draft player id."""
    classic = {}
    for row in _dashboard_live_elements:
        if not isinstance(row, dict) or row.get("id") is None:
            continue
        classic[int(row["id"])] = row.get("stats") or {}
    return {
        int(draft_id): classic[fpl_id_for_draft(draft_id)]
        for draft_id in elements
        if fpl_id_for_draft(draft_id) in classic
    }


def _live_centre_team_snapshot(manager):
    snapshot = history.get("gameweeks", {}).get(str(dashboard_target_gw), {})
    return next(
        (td for td in snapshot.get("teams", {}).values() if td.get("manager") == manager),
        None,
    ) or {}


def _live_centre_player_row(player, starter=True):
    try:
        pid = int(player.get("element_id"))
    except (TypeError, ValueError):
        return ""
    meta = elements.get(pid, {})
    stats = _live_full_stats_lookup().get(pid, {})
    pts = int(stats.get("total_points", player.get("points", 0)) or 0)
    mins = int(stats.get("minutes", player.get("minutes", 0)) or 0)
    club = teams_lookup.get(meta.get("team"), player.get("team", "—"))
    pos = positions_lookup.get(meta.get("element_type"), player.get("position", "—"))
    remaining, fixture_state = _club_fixture_remaining_fraction(meta.get("team"))
    if fixture_state == "finished":
        state_label = "FT"
    elif fixture_state == "live":
        state_label = "LIVE"
    else:
        state_label = "TO PLAY"

    stat_labels = [
        ("goals_scored", "G"), ("assists", "A"), ("clean_sheets", "CS"),
        ("goals_conceded", "GC"), ("own_goals", "OG"),
        ("penalties_saved", "Pens saved"), ("penalties_missed", "Pens missed"),
        ("yellow_cards", "YC"), ("red_cards", "RC"), ("saves", "Saves"),
        ("bonus", "Bonus"), ("bps", "BPS"),
    ]
    stat_bits = []
    for key, label in stat_labels:
        value = stats.get(key)
        if value not in (None, 0, 0.0, "0"):
            stat_bits.append(f'<span><b>{escape_html(label)}</b> {escape_html(value)}</span>')
    if not stat_bits:
        stat_bits.append('<span class="live-centre-stat-muted">No event stats yet</span>')

    captain = " · C" if player.get("is_captain") else (" · VC" if player.get("is_vice_captain") else "")
    player_name = player.get("web_name") or meta.get("web_name", f"Player {pid}")
    return f'''
<details class="live-centre-player {'starter' if starter else 'bench'}">
  <summary>
    <span class="live-centre-player-main"><b>{escape_html(player_name)}</b><small>{escape_html(pos)} · {escape_html(club)}{captain}</small></span>
    <span class="live-centre-player-state state-{fixture_state}">{state_label}</span>
    <span class="live-centre-player-mins">{mins}'</span>
    <strong class="live-centre-player-pts">{pts}</strong>
  </summary>
  <div class="live-centre-player-stats">{''.join(stat_bits)}</div>
</details>'''


def _live_centre_team_panel(manager, side_label):
    squad = _live_centre_team_snapshot(manager)
    starters = list(squad.get("starters", []) or [])
    bench = list(squad.get("bench", []) or [])
    by_pos = {"GKP": [], "DEF": [], "MID": [], "FWD": []}
    for player in starters:
        pos = player.get("position") or positions_lookup.get(elements.get(player.get("element_id"), {}).get("element_type"), "")
        if pos in by_pos:
            by_pos[pos].append(player)
    formation = f"{len(by_pos['DEF'])}-{len(by_pos['MID'])}-{len(by_pos['FWD'])}"

    def chip(player):
        try:
            pid = int(player.get("element_id"))
        except (TypeError, ValueError):
            pid = -1
        stats = _live_full_stats_lookup().get(pid, {})
        pts = int(stats.get("total_points", player.get("points", 0)) or 0)
        mins = int(stats.get("minutes", player.get("minutes", 0)) or 0)
        remaining, state = _club_fixture_remaining_fraction(elements.get(pid, {}).get("team"))
        state_text = "FT" if state == "finished" else ("LIVE" if state == "live" else "TO PLAY")
        return (
            f'<div class="live-centre-pitch-player state-{state}" title="{escape_html(state_text)} · {mins} minutes">'
            f'<b>{escape_html(player.get("web_name", "Unknown"))}</b>'
            f'<span>{pts} pts</span><small>{state_text}</small></div>'
        )

    pitch = f'''
<div class="live-centre-pitch">
  <div class="live-centre-pitch-line forwards">{''.join(chip(p) for p in by_pos['FWD'])}</div>
  <div class="live-centre-pitch-line mids">{''.join(chip(p) for p in by_pos['MID'])}</div>
  <div class="live-centre-pitch-line defs">{''.join(chip(p) for p in by_pos['DEF'])}</div>
  <div class="live-centre-pitch-line keepers">{''.join(chip(p) for p in by_pos['GKP'])}</div>
</div>'''
    detail_rows = "".join(_live_centre_player_row(p, True) for p in starters)
    bench_rows = "".join(_live_centre_player_row(p, False) for p in bench)
    return f'''
<div class="live-centre-team-column">
  <div class="live-centre-team-head"><span>{escape_html(side_label)}</span><h3>{escape_html(manager)}</h3><small>{formation}</small></div>
  {pitch}
  <div class="live-centre-squad-detail"><h4>Starting XI · tap a player for live stats</h4>{detail_rows}</div>
  <div class="live-centre-bench"><h4>Bench</h4>{bench_rows or '<div class="notice">Bench not captured.</div>'}</div>
</div>'''


def _live_centre_swing_score(odds):
    """Higher = tighter and with more unresolved football, therefore worth watching."""
    margin = abs(float(odds["current1"]) - float(odds["current2"]))
    unresolved = int(odds["players_left1"]) + int(odds["players_left2"])
    closeness = max(0.0, 35.0 - margin)
    probability_tension = 100.0 - abs(float(odds["team1_win"]) - float(odds["team2_win"]))
    return (closeness * 1.8) + (unresolved * 5.0) + (probability_tension * 0.35)


def _live_centre_threats(manager):
    profile = _live_manager_remaining_profile(manager)
    details = sorted(profile.get("details", []), key=lambda r: r.get("remaining_mean", 0), reverse=True)
    if not details:
        return '<span class="live-centre-no-threat">Nobody with meaningful projected output left.</span>'
    return "".join(
        f'<span class="live-centre-threat"><b>{escape_html(r.get("name", "Unknown"))}</b> +{float(r.get("remaining_mean", 0)):.1f} exp.</span>'
        for r in details[:5]
    )


def _live_centre_pl_fixture_board():
    live_stats = _live_full_stats_lookup()
    starters_by_club = defaultdict(list)
    snapshot = history.get("gameweeks", {}).get(str(dashboard_target_gw), {})
    for squad in snapshot.get("teams", {}).values():
        manager = squad.get("manager", "Unknown")
        for player in squad.get("starters", []) or []:
            try:
                pid = int(player.get("element_id"))
            except (TypeError, ValueError):
                continue
            club_id = elements.get(pid, {}).get("team")
            if club_id is None:
                continue
            stats = live_stats.get(pid, {})
            starters_by_club[int(club_id)].append({
                "name": player.get("web_name") or elements.get(pid, {}).get("web_name", "Unknown"),
                "manager": manager,
                "points": int(stats.get("total_points", player.get("points", 0)) or 0),
            })

    cards = []
    for fx in sorted(_dashboard_pl_fixtures, key=lambda f: (str(f.get("kickoff_time") or ""), int(f.get("id", 0) or 0))):
        home_id, away_id = int(fx.get("team_h", 0) or 0), int(fx.get("team_a", 0) or 0)
        home, away = teams_lookup.get(home_id, str(home_id)), teams_lookup.get(away_id, str(away_id))
        if fx.get("finished") or fx.get("finished_provisional"):
            status = "FT"
        elif fx.get("started"):
            mins = fx.get("minutes")
            status = f"{mins}'" if mins not in (None, "") else "LIVE"
        else:
            ko = str(fx.get("kickoff_time") or "")
            status = "UPCOMING"
            if ko:
                try:
                    kdt = datetime.fromisoformat(ko.replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/London"))
                    status = kdt.strftime("%a %H:%M")
                except Exception:
                    pass
        hs = fx.get("team_h_score")
        aw = fx.get("team_a_score")
        score = f"{hs if hs is not None else '–'} – {aw if aw is not None else '–'}"
        relevant = starters_by_club.get(home_id, []) + starters_by_club.get(away_id, [])
        chips = "".join(
            f'<span class="live-centre-pl-player"><b>{escape_html(r["name"])}</b><small>{escape_html(r["manager"])} · {r["points"]} pts</small></span>'
            for r in relevant
        ) or '<span class="live-centre-pl-none">No McDraft starters in this fixture.</span>'
        cards.append(f'''
<div class="live-centre-pl-fixture">
  <div class="live-centre-pl-score"><span>{escape_html(home)}</span><strong>{score}</strong><span>{escape_html(away)}</span><em>{escape_html(status)}</em></div>
  <div class="live-centre-pl-assets">{chips}</div>
</div>''')
    return "".join(cards) or '<div class="notice">Premier League live fixtures are not available yet.</div>'


def live_centre_html():
    if dashboard_game_state != "live":
        return ""
    matches = [
        m for m in (league_matches_all or [])
        if int(m.get("event", 0) or 0) == int(dashboard_target_gw)
    ]
    if not matches:
        return '<div class="notice">The gameweek is live, but matchup data has not arrived yet.</div>'

    matchup_rows = []
    for match in matches:
        odds = _live_fixture_odds_for_match(match)
        odds["match"] = match
        odds["derby"] = _derby_name(odds["team1"], odds["team2"])
        odds["swing"] = _live_centre_swing_score(odds)
        matchup_rows.append(odds)
    matchup_rows.sort(key=lambda row: row["swing"], reverse=True)

    switchers, panels = [], []
    for i, odds in enumerate(matchup_rows):
        active = " active" if i == 0 else ""
        derby = odds.get("derby")
        title = derby or f'{odds["team1"]} vs {odds["team2"]}'
        diff = abs(int(odds["current1"]) - int(odds["current2"]))
        left = int(odds["players_left1"]) + int(odds["players_left2"])
        switchers.append(f'''
<button class="live-centre-switch{active}" type="button" data-live-match="{i}" onclick="showLiveCentreMatch({i},this)">
  <span>{escape_html(title)}</span><b>{odds['current1']}–{odds['current2']}</b><small>{left} left · margin {diff}</small>
</button>''')
        derby_html = f'<b class="live-centre-derby">{escape_html(derby)}</b>' if derby else ''
        panels.append(f'''
<section class="live-centre-match{active}" id="live-centre-match-{i}">
  <div class="live-centre-scoreboard">
    <div class="live-centre-score-team"><span>{escape_html(odds['team1'])}</span><strong>{odds['current1']}</strong><small>{odds['players_left1']} left</small></div>
    <div class="live-centre-score-middle"><span class="live-pill">LIVE · GW{dashboard_target_gw}</span>{derby_html}<small>Projected final</small><strong>{odds['final1_mean']:.1f} – {odds['final2_mean']:.1f}</strong></div>
    <div class="live-centre-score-team away"><span>{escape_html(odds['team2'])}</span><strong>{odds['current2']}</strong><small>{odds['players_left2']} left</small></div>
  </div>
  <div class="live-centre-probs">
    <div style="--p:{odds['team1_win']:.2f}%"><span>{escape_html(odds['team1'])}</span><b>{odds['team1_win']:.1f}%</b></div>
    <div class="draw" style="--p:{odds['draw']:.2f}%"><span>Draw</span><b>{odds['draw']:.1f}%</b></div>
    <div style="--p:{odds['team2_win']:.2f}%"><span>{escape_html(odds['team2'])}</span><b>{odds['team2_win']:.1f}%</b></div>
  </div>
  <div class="live-centre-threat-grid">
    <div><h4>{escape_html(odds['team1'])} threats</h4>{_live_centre_threats(odds['team1'])}</div>
    <div><h4>{escape_html(odds['team2'])} threats</h4>{_live_centre_threats(odds['team2'])}</div>
  </div>
  <div class="live-centre-xi-grid">
    {_live_centre_team_panel(odds['team1'], 'HOME')}
    {_live_centre_team_panel(odds['team2'], 'AWAY')}
  </div>
</section>''')

    top = matchup_rows[0]
    top_title = top.get("derby") or f'{top["team1"]} vs {top["team2"]}'
    return f'''
<div class="live-centre-hero card">
  <div><span class="live-centre-kicker">MCDRAFT LIVE CENTRE · GW{dashboard_target_gw}</span><h2>Every matchup. Every relevant player. One mildly unhinged control room.</h2><p>The most volatile tie right now is <b>{escape_html(top_title)}</b>. Matchups below are ordered by how close they are and how much football remains.</p></div>
  <div class="live-centre-pulse"><i></i><span>LIVE</span></div>
</div>
<div class="live-centre-switcher">{''.join(switchers)}</div>
{''.join(panels)}
<div class="card live-centre-pl-card"><div class="live-centre-section-head"><div><span class="live-centre-kicker">PREMIER LEAGUE FEED</span><h2>What can still swing McDraft?</h2></div><p>All PL fixtures in GW{dashboard_target_gw}, with every McDraft starter involved and their current FPL points.</p></div><div class="live-centre-pl-grid">{_live_centre_pl_fixture_board()}</div></div>
<div class="card live-centre-table-card"><div class="live-centre-section-head"><div><span class="live-centre-kicker">AS IT STANDS</span><h2>Live McDraft Table</h2></div><p>Provisional standings if every matchup froze right now.</p></div>{live_as_it_stands_table()}</div>
'''


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


def _pedigree_line_score(players, position, starters, fallback=45):
    """FIFA-esque positional unit: best starting assets 85%, genuine depth 15%."""
    scores = sorted((int(_player_ratings_by_id.get(int(p['id']), {}).get('rating', fallback))
                     for p in players if p.get('position') == position), reverse=True)
    top = scores[:starters]
    # Missing legal starter slots lower a position's score; a zero-player
    # position must not look stronger than a merely below-average unit.
    first = (sum(top) + fallback * max(0, starters - len(top))) / float(starters)
    depth = statistics.mean(scores[starters:]) if len(scores) > starters else first
    return round(0.85 * first + 0.15 * depth, 1), scores


def squad_pedigree_table():
    """Every current squad's evolving player ratings, FIFA-style positional OVR."""
    all_cards = []
    rows_data = []
    for manager in managers:
        players = current_squad_strength.get(manager, {}).get('players', [])
        if not players:
            continue
        gk, gk_scores = _pedigree_line_score(players, 'GKP', 1)
        defenders, def_scores = _pedigree_line_score(players, 'DEF', 4)
        mid, mid_scores = _pedigree_line_score(players, 'MID', 4)
        att, att_scores = _pedigree_line_score(players, 'FWD', 2)
        # Goalkeepers explicitly contribute to DEF, as in a squad-strength
        # measure; they are also displayed as a separate unit in the breakdown.
        defense = round(0.80 * defenders + 0.20 * gk, 1)
        ovr = round(0.34 * defense + 0.38 * mid + 0.28 * att, 1)
        # Absolute bands: 35 OVR = 1★, 50 = 2★, 65 = 3★, 80 = 4★,
        # 95 = 5★. No league-rank forcing or min/max stretching.
        stars = _round_half_star(max(0.5, (ovr - 20.0) / 15.0))
        p = season_prediction.get(manager, {})
        rank_total = int(p.get('squad_draft_rank_total', sum(int(x.get('draft_rank', 151)) for x in players)) or 0)
        avg_rank = rank_total / len(players)
        recent = [float(score or 0) for _,score in sorted(raw_score_by_gw.get(manager, []))[-3:]]
        recent_form = statistics.mean(recent) if recent else None
        top30 = sum(1 for x in players if _league_draft_rank(x['id']) <= 30)
        undrafted = sum(1 for x in players if _league_draft_rank(x['id']) >= UNDRAFTED_PLAYER_RANK)
        all_ratings = [int(_player_ratings_by_id.get(int(x['id']),{}).get('rating',38)) for x in players]
        squad_mean = statistics.mean(all_ratings)
        club_mean = statistics.mean([_rating_features.get(int(x['id']),{}).get('club',0.5) for x in players])
        rows_data.append(dict(manager=manager,ovr=ovr,stars=stars,defense=defense,mid=mid,att=att,
                              gk=gk,defenders=defenders,avg=squad_mean,rank_total=rank_total,
                              avg_rank=avg_rank,form=recent_form,top30=top30,
                              undrafted=undrafted,club=club_mean,players=players))
    rows_data.sort(key=lambda r: (-r['ovr'], r['manager']))
    table_rows=[]
    for idx, entry in enumerate(rows_data):
        name=escape_html(entry['manager'])
        score=entry['ovr']
        tier=_rating_tier(score)
        star_label=_star_text(entry['stars'])
        form_text=f"{entry['form']:.1f}" if entry['form'] is not None else '—'
        table_rows.append(f"""<tr><td class="manager-name">{name}</td>
<td><b>{score:.0f}</b></td><td>{entry['defense']:.0f}</td><td>{entry['mid']:.0f}</td><td>{entry['att']:.0f}</td>
<td title="{entry['stars']:.1f} out of 5">{star_label} <span class="muted">{entry['stars']:.1f}</span></td>
<td>{entry['avg']:.0f}</td><td>{entry['rank_total']}</td><td>{form_text}</td></tr>""")
        units=[('DEF',entry['defense']),('MID',entry['mid']),('ATT',entry['att'])]
        bars=''.join(f'<div class="pedigree-unit"><span>{label}</span><b>{val:.0f}</b><i><em style="width:{val:.0f}%"></em></i></div>' for label,val in units)
        players_sorted = sorted(entry['players'], key=lambda x: (
            ['GKP','DEF','MID','FWD'].index(x.get('position')) if x.get('position') in ('GKP','DEF','MID','FWD') else 4,
            -_player_ratings_by_id.get(int(x['id']),{}).get('rating',0)))
        player_rows=[]
        for player in players_sorted:
            pid=int(player['id']); detail=_player_ratings_by_id.get(pid,{})
            rating=int(detail.get('rating',45)); delta=detail.get('change'); rating_tier=_rating_tier(rating)
            trend=('+'+str(delta) if delta>0 else str(delta)) if delta is not None else '—'
            club=teams_lookup.get(elements.get(pid,{}).get('team'),'—')
            delta_class='rating-up' if delta is not None and delta>0 else 'rating-down' if delta is not None and delta<0 else 'rating-flat'
            player_rows.append(f'<tr><td>{escape_html(player.get("position") or "—")}</td>'
                f'<td><b>{escape_html(player.get("name") or "Unknown")}</b><small>{escape_html(club)}</small></td>'
                f'<td><strong class="rating-tier-number {rating_tier}">{rating}</strong></td><td class="{delta_class}">{trend}</td>'
                f'<td>{detail.get("club_form",50):.0f}</td>'
                f'<td>{detail.get("minutes_share",0):.0f}%</td></tr>')
        summary=f"""<summary class="pedigree-summary"><div class="pedigree-head">
<div class="pedigree-overall {tier}"><strong>{score:.0f}</strong><small>OVR</small></div>
<div class="pedigree-identity"><h3>{name}</h3><div class="pedigree-stars">{star_label} <span>{entry['stars']:.1f}/5</span></div>
<small>{len(entry['players'])} players · Avg rating {entry['avg']:.0f} · 3GW {form_text} pts</small></div></div>
<div class="pedigree-units">{bars}</div><span class="pedigree-open-hint">View all players &amp; unit breakdown ▾</span></summary>"""
        breakdown=f"""<div class="pedigree-detail"><div class="pedigree-detail-stats">
<span><b>{entry['gk']:.0f}</b> GK</span><span><b>{entry['defenders']:.0f}</b> Outfield DEF</span>
<span><b>{entry['club']*100:.0f}</b> Club/form</span><span><b>{entry['top30']}</b> Top-30 picks</span>
<span><b>{entry['undrafted']}</b> Undrafted</span><span><b>{entry['avg_rank']:.1f}</b> Avg draft pick</span></div>
<div class="table-wrap"><table class="pedigree-players-table"><thead><tr><th>Pos</th><th>Player / PL club</th>
<th>OVR</th><th>Change</th><th>Club form</th><th>Game-time</th></tr></thead><tbody>{''.join(player_rows)}</tbody></table></div>
<p class="card-description">DEF = 80% best 4 defenders + 20% goalkeeper; each unit values its leading starters 85% and position depth 15%.
OVR = 34% DEF, 38% MID, 28% ATT. Player ratings automatically follow recent FPL statistics and changing PL club form.</p></div>"""
        all_cards.append(f'<details class="pedigree-fifa-card">{summary}{breakdown}</details>')
    return f"""<p class="card-description">Live, FIFA-inspired squad ratings out of 100. Each team uses its current players, not its original draft-day lineup; transfers, player form, injury availability, game-time and real PL club results update the ratings each dashboard run. Click a team to see every individual rating and its positional makeup.</p>
<div class="pedigree-cards">{''.join(all_cards)}</div>
<h3 class="pedigree-comparison-title">League-wide squad comparison</h3>
<div class="table-wrap"><table><thead><tr><th>Manager</th><th>OVR</th><th>DEF</th><th>MID</th><th>ATT</th><th>Stars /5</th><th>Avg player</th><th>Draft rank ↓</th><th>3GW pts</th></tr></thead>
<tbody>{''.join(table_rows)}</tbody></table></div>
<p class="card-description">Five-star bands are fixed to the /100 scale (35 = ★, 50 = ★★, 65 = ★★★, 80 = ★★★★, 95 = ★★★★★). Rating colours are Bronze <70, Silver 70–79, Gold 80–89 and Platinum 90+, never forced relative to this league. Player ratings influence the immediately upcoming GW projection by at most ±7%; later-GW projections keep the original fixture model.</p>"""


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
<div class="power-formula"><b>Model:</b> 7,500 Monte Carlo simulations using the real remaining H2H schedule. Current squad strength and recent form still drive the forecast, but early-season weekly expectations are deliberately regressed hard towards the league mean and score volatility is widened. Finishing probabilities are then <b>calibrated back towards the league baseline</b> until enough gameweeks have been played, so five good weeks cannot create fake certainty. The calibration now fades through roughly the first 10 completed GWs, so stronger teams separate earlier while early-season confidence remains restrained. Squad strength still uses the best legal projected XI, recent/season output and a decaying pedigree prior blending 60% actual McDraft pick order with 40% official FPL Draft rank. <b>Confidence badges</b> describe how much evidence the forecast currently has; they are not another prediction. Forecast Range is the central 80% of simulated finishes and remains separate from mathematical Possible Finish.</div>
<div class="table-wrap"><table>
<thead><tr><th>Pred.</th><th>Manager</th><th>Now</th><th>Exp. League Pts</th><th>Exp. W-D-L</th><th>Exp. Pts For</th><th>Squad XI</th><th>Blended Draft Rank ↓</th><th>Pick Eff.</th><th>Forecast Range</th><th>1st</th><th>Top 3</th><th>Bottom 3</th></tr></thead>
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

    # Open the article on the same event the headline prioritises, so a
    # giant-killing or monster haul is not buried under an unrelated result.
    upset_games = []
    if gw > 1:
        for fixture in fixtures:
            a, b = fixture['team1'], fixture['team2']
            sa, sb = fixture['score1'], fixture['score2']
            if sa == sb:
                continue
            winner, loser = (a, b) if sa > sb else (b, a)
            gap = pos_prev.get(winner, 0) - pos_prev.get(loser, 0)
            if gap >= 3:
                upset_games.append((gap, abs(sa - sb), winner, loser, max(sa,sb), min(sa,sb)))
    headline_upset = max(upset_games) if upset_games else None
    headline_haul = _gameweek_player_standout(gw)
    headline_close = min(fixtures, key=lambda f: (abs(f['score1'] - f['score2']),
                                                  -(f['score1'] + f['score2'])))
    close_gap = abs(headline_close['score1'] - headline_close['score2'])
    if pos_prev.get(leader) and pos_prev.get(leader) != 1:
        opening = _gw_story_choice(rng, new_leader_openers)
    elif headline_upset:
        _, _, underdog, favourite, won, lost = headline_upset
        opening = _gw_story_choice(rng, [
            f"{underdog} ripped up the form book in GW{gw}, toppling higher-ranked {favourite} {won}-{lost} in the week's biggest table upset.",
            f"The shock of GW{gw} came courtesy of {underdog}, who ambushed {favourite} {won}-{lost} and sent the predictions to the shredder.",
        ])
    elif headline_haul and headline_haul.get('points', 0) >= 15:
        opening = _gw_story_choice(rng, [
            f"{headline_haul['name']} stole GW{gw}'s spotlight with a colossal {headline_haul['points']}-point haul for {headline_haul['manager']}.",
            f"Forget the league office: GW{gw} belonged to {headline_haul['name']}, who went nuclear for {headline_haul['points']} points.",
        ])
    elif close_gap <= 2:
        opening = _gw_story_choice(rng, [
            f"GW{gw}'s headline drama came from {headline_close['team1']} and {headline_close['team2']}, separated by just {close_gap} point{'s' if close_gap != 1 else ''} in a {headline_close['score1']}-{headline_close['score2']} thriller.",
            f"A photo finish stole the show in GW{gw}: {headline_close['team1']} and {headline_close['team2']} finished {headline_close['score1']}-{headline_close['score2']}.",
        ])
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
    cup_paragraph = _cup_column_for_gw(gw, 'completed') if '_cup_column_for_gw' in globals() else ''
    extra = _mcdraft_column_intelligence(gw, 'completed') if '_mcdraft_column_intelligence' in globals() else []
    # Keep the regular newspaper write-up intact, but give Bench Watch and
    # Club Watch their own readable lines, followed by Cup and preview desks.
    body = " ".join(sentence.strip() for sentence in [opening] + beats if sentence and sentence.strip())
    sections = [body] + [beat for beat in extra if beat] + ([cup_paragraph] if cup_paragraph else []) + ([preview] if preview else [])
    return "\n\n".join(section.strip() for section in sections if section and section.strip())


def _mcdraft_column_paragraphs_html(story):
    """One escaped HTML paragraph per editorial section on every surface."""
    return "".join(
        f'<p>{escape_html(paragraph.strip())}</p>'
        for paragraph in (story or '').split("\n\n") if paragraph.strip()
    )


def _headline_pick(options, *seed_parts):
    """Stable variety: the same event keeps the same headline across rebuilds."""
    options = [str(x) for x in options if x]
    if not options:
        return ''
    seed = '|'.join(str(x) for x in seed_parts)
    checksum = sum((i + 1) * ord(ch) for i, ch in enumerate(seed))
    return options[checksum % len(options)]


def _mcdraft_column_headline(gw, phase='completed'):
    """Data-grounded tabloid headline with lots of stable wording variation.

    Priority: new #1 > Cup winner > sizeable table upset > 15+ player haul >
    two-point thriller > demolition > ordinary standout result.
    """
    gw = int(gw)

    if phase == 'upcoming':
        if 20 <= gw <= 26:
            stage = ('PRELIMS' if gw <= 21 else 'QUARTER-FINALS' if gw <= 23
                     else 'SEMI-FINALS' if gw <= 25 else 'THE FINAL')
            return _headline_pick([
                f'CUP FEVER: {stage} AWAIT',
                f'KNOCKOUT FOOTBALL RETURNS: {stage} NEXT',
                f'NO SECOND CHANCES: {stage} LOOM',
                f'THE ROAD TO GLORY: {stage} UP NEXT',
                f'CUP WEEK: {stage} TAKE CENTRE STAGE',
                f'BRACKET PRESSURE BUILDS: {stage} AWAIT',
                f'McDRAFT CUP CALLING: {stage} ARE HERE',
                f'ALL EYES ON THE CUP: {stage} NEXT',
            ], gw, phase, stage)
        return _headline_pick([
            f'GW{gw}: THE STAGE IS SET',
            f'GW{gw}: HERE WE GO AGAIN',
            f'GW{gw}: ANOTHER WEEK, ANOTHER SCRAP',
            f'GW{gw}: THE NEXT CHAPTER AWAITS',
            f'GW{gw}: TEN TEAMS, FIVE FIGHTS',
            f'GW{gw}: POINTS, PANIC AND POSSIBILITY',
            f'GW{gw}: THE WEEKEND BECKONS',
            f'GW{gw}: FRESH FIXTURES, FRESH CHAOS',
            f'GW{gw}: SOMEBODY IS ABOUT TO REGRET SOMETHING',
            f'GW{gw}: THE GROUP CHAT AWAITS ITS NEXT VICTIM',
        ], gw, phase)

    if phase == 'live':
        return _headline_pick([
            f'GW{gw}: THE DRAMA IS LIVE',
            f'GW{gw}: LIVE AND ABSOLUTELY UNHINGED',
            f'GW{gw}: EVERYTHING STILL TO PLAY FOR',
            f'GW{gw}: THE TABLE IS MOVING',
            f'GW{gw}: SCORES FLY, NERVES FRAY',
            f'GW{gw}: LIVE CHAOS ACROSS McDRAFT',
            f'GW{gw}: THIS ONE IS FAR FROM OVER',
            f'GW{gw}: THE SWING-O-METER IS MELTING',
            f'GW{gw}: FIVE MATCHUPS, ZERO PEACE',
            f'GW{gw}: THE WEEKEND HAS TEETH',
        ], gw, phase)

    fixtures = results_by_gw.get(gw, [])
    if not fixtures:
        return _headline_pick([
            f'GW{gw}: THE VERDICT AWAITS',
            f'GW{gw}: SCORECARDS STILL PENDING',
            f'GW{gw}: NO FINAL WHISTLE YET',
            f'GW{gw}: THE STORY IS STILL BEING WRITTEN',
        ], gw, phase)

    ranked, _ = _standings_through_gw(gw)
    older, older_pos = _standings_through_gw(gw - 1) if gw > 1 else ([], {})
    if ranked and (not older or older[0] != ranked[0]):
        leader = ranked[0]
        if not older:
            return _headline_pick([
                f'FIRST BLOOD: {leader} CLAIM TOP SPOT',
                f'EARLY PACESETTERS: {leader} HIT THE SUMMIT',
                f'FIRST TO THE THRONE: {leader} LEAD McDRAFT',
                f'{leader} DRAW FIRST BLOOD AT THE TOP',
                f'TABLE TOPPERS: {leader} SET THE EARLY PACE',
            ], gw, leader, 'leader-first')
        return _headline_pick([
            f'NEW KINGS OF McDRAFT: {leader} TAKE FIRST',
            f'CHANGING OF THE GUARD: {leader} GO TOP',
            f'SUMMIT STORMED: {leader} SEIZE FIRST PLACE',
            f'THERE IS A NEW NUMBER ONE: {leader} HIT THE TOP',
            f'TOP OF THE PILE: {leader} TAKE CONTROL',
            f'{leader} KNOCK THE DOOR DOWN AND GO FIRST',
            f'THRONE TAKEN: {leader} RULE McDRAFT',
            f'NEW LEADERS IN TOWN: {leader} CLIMB TO FIRST',
            f'{leader} COMPLETE THE CLIMB TO NUMBER ONE',
            f'McDRAFT HAS NEW LEADERS: {leader} TAKE THE SUMMIT',
            f'POWER SHIFT: {leader} MOVE INTO FIRST',
            f'OUT IN FRONT: {leader} GRAB TOP SPOT',
        ], gw, leader, 'leader')

    cup = globals().get('mcdraft_cup') or {}
    if gw == 26 and cup.get('champion') and not cup.get('error'):
        champ = cup['champion']
        return _headline_pick([
            f'CUP GLORY: {champ} LIFT THE McDRAFT CUP',
            f'CHAMPIONS: {champ} CONQUER THE McDRAFT CUP',
            f'ONE GAME, ONE TROPHY: {champ} ARE CUP WINNERS',
            f'ETERNAL GLORY: {champ} WIN THE McDRAFT CUP',
            f'THE CUP IS THEIRS: {champ} RULE GW26',
            f'KNOCKOUT KINGS: {champ} CLAIM THE TROPHY',
            f'CHAMPAGNE TIME: {champ} WIN THE McDRAFT CUP',
            f'CROWNED IN THE CUP: {champ} TAKE THE TITLE',
        ], gw, champ, 'cup-winner')

    upsets = []
    if older and len(older_pos) >= 2:
        for fixture in fixtures:
            a, b = fixture['team1'], fixture['team2']
            sa, sb = int(fixture['score1']), int(fixture['score2'])
            if sa == sb:
                continue
            winner, loser = (a, b) if sa > sb else (b, a)
            if winner not in older_pos or loser not in older_pos:
                continue
            position_gap = older_pos[winner] - older_pos[loser]
            if position_gap >= 3:
                upsets.append((position_gap, abs(sa - sb), max(sa, sb), winner, loser))
    if upsets:
        gap, margin, high_score, winner, loser = max(upsets)
        if gap >= 6 or margin >= 15:
            opts = [
                f'SHOCKWAVE: {winner} HUMBLE {loser}',
                f'FORM BOOK TORCHED: {winner} STUN {loser}',
                f'GIANT-KILLING: {winner} TAKE DOWN {loser}',
                f'UPSET OF THE SEASON? {winner} FLOOR {loser}',
                f'RANKINGS BE DAMNED: {winner} BEAT {loser}',
                f'NO RESPECT FOR THE TABLE: {winner} TOPPLE {loser}',
                f'DAVID MEETS GOLIATH: {winner} SHOCK {loser}',
                f'THE TABLE LIED: {winner} DISMANTLE {loser}',
            ]
        else:
            opts = [
                f'GIANT-KILLING: {winner} STUN {loser}',
                f'UPSET ALERT: {winner} DOWN {loser}',
                f'AGAINST THE ODDS: {winner} BEAT {loser}',
                f'FORM BOOK RIPPED UP: {winner} EDGE {loser}',
                f'TABLE TURNED: {winner} TAKE OUT {loser}',
                f'UNDERDOGS BITE: {winner} SHOCK {loser}',
                f'RANK MEANS NOTHING: {winner} BEAT {loser}',
                f'SURPRISE PACKAGE: {winner} TOPPLE {loser}',
                f'UPSET CITY: {winner} GET IT DONE AGAINST {loser}',
                f'NOT IN THE SCRIPT: {winner} DEFEAT {loser}',
            ]
        return _headline_pick(opts, gw, winner, loser, gap, margin, 'upset')

    standout = _gameweek_player_standout(gw)
    if standout and int(standout.get('points', 0) or 0) >= 15:
        name, pts = standout['name'], int(standout['points'])
        snapshot = history.get('gameweeks', {}).get(str(gw), {}).get('teams', {})
        benched = any(p.get('web_name') == name and int(p.get('points', 0) or 0) == pts
                      for squad in snapshot.values() for p in squad.get('bench', []))
        if benched:
            return _headline_pick([
                f'BENCH BOMBSHELL: {name} HAULS {pts} POINTS',
                f'{pts} POINTS, ZERO USE: {name} ROT ON THE BENCH',
                f'BENCH PAIN: {name} DROP A {pts}-POINT MASTERCLASS',
                f'WRONG SEAT: {name} EXPLODE FOR {pts} FROM THE BENCH',
                f'THE BENCH OF SHAME: {name} SCORE {pts}',
                f'OUCH: {name} BANK {pts} POINTS FROM THE SIDELINES',
                f'BENCHED AND BRUTAL: {name} DELIVER {pts}',
                f'{name} GO NUCLEAR — FROM THE BLOODY BENCH',
                f'BENCH NIGHTMARE: {name} LEAVE {pts} POINTS UNUSED',
                f'{pts} POINTS WATCHED FROM AFAR: {name} PUNISH THE BENCH',
            ], gw, name, pts, 'bench-haul')
        if pts >= 20:
            opts = [
                f'NUCLEAR: {name} ERUPTS FOR {pts}',
                f'ABSOLUTE MONSTER: {name} SMASH {pts} POINTS',
                f'{name} GO SUPERNOVA WITH {pts}',
                f'ONE-MAN WRECKING CREW: {name} HIT {pts}',
                f'{pts}! {name} BREAK THE GAMEWEEK',
                f'RIDICULOUS SCENES: {name} DROP {pts}',
                f'{name} TURN GW{gw} INTO THEIR PERSONAL HIGHLIGHT REEL',
                f'POINTS AVALANCHE: {name} PILE UP {pts}',
            ]
        else:
            opts = [
                f'ABSOLUTE SCENES: {name} EXPLODES FOR {pts}',
                f'HAUL OF FAME: {name} BANK {pts}',
                f'{name} STEAL THE SHOW WITH {pts} POINTS',
                f'BIG-GAME ENERGY: {name} DELIVER {pts}',
                f'PLAYER OF THE WEEK: {name} FIRE IN {pts}',
                f'{name} LIGHT UP GW{gw} WITH {pts}',
                f'HAUL ALERT: {name} SMASH {pts}',
                f'{pts} POINTS OF PURE CHAOS FROM {name}',
                f'{name} PUT ON A {pts}-POINT CLINIC',
                f'STAR TURN: {name} RUN RIOT FOR {pts}',
                f'{name} OWN THE WEEKEND WITH {pts}',
                f'POINTS MACHINE: {name} CLOCK {pts}',
            ]
        return _headline_pick(opts, gw, name, pts, 'haul')

    closest = min(fixtures, key=lambda f: (abs(f['score1'] - f['score2']),
                                            -(f['score1'] + f['score2'])))
    margin = abs(closest['score1'] - closest['score2'])
    if margin <= 2:
        a, b = closest['team1'], closest['team2']
        if margin == 0:
            return _headline_pick([
                f'DEAD HEAT: {a} AND {b} CANNOT BE SEPARATED',
                f'NOTHING BETWEEN THEM: {a} AND {b} DRAW',
                f'ALL SQUARE: {a} AND {b} SHARE THE SPOILS',
                f'STANDOFF: {a} AND {b} FINISH LEVEL',
                f'LOCKED TOGETHER: {a} AND {b} END DEAD EVEN',
                f'NO WINNER HERE: {a} AND {b} CANCEL EACH OTHER OUT',
            ], gw, a, b, 'draw')
        winner, loser = ((a, b) if closest['score1'] > closest['score2'] else (b, a))
        if margin == 1:
            return _headline_pick([
                f'ONE-POINT WONDER: {winner} EDGE {loser}',
                f'BY A WHISKER: {winner} NICK IT FROM {loser}',
                f'ONE BLOODY POINT: {winner} SURVIVE {loser}',
                f'HEARTBREAKER: {winner} BEAT {loser} BY ONE',
                f'FINE MARGINS: {winner} SQUEEZE PAST {loser}',
                f'PHOTO FINISH: {winner} BEAT {loser} BY A SINGLE POINT',
                f'NAIL-BITER: {winner} ESCAPE {loser}',
                f'BARELY BREATHING: {winner} HOLD OFF {loser}',
                f'ONE POINT, ALL THE DIFFERENCE: {winner} TAKE IT',
                f'CRUEL GAME: {winner} DENY {loser} BY ONE',
                f'EDGE OF THE SEAT: {winner} PINCH IT',
                f'NO ROOM TO BREATHE: {winner} SNEAK PAST {loser}',
            ], gw, winner, loser, 'one-point')
        return _headline_pick([
            f'PHOTO FINISH: {winner} SNEAK PAST {loser}',
            f'TWO-POINT TIGHTROPE: {winner} HOLD OFF {loser}',
            f'CLOSE CALL: {winner} EDGE {loser}',
            f'NAIL-BITER: {winner} JUST ABOUT BEAT {loser}',
            f'FINE MARGINS: {winner} TAKE IT BY TWO',
            f'HEARTS IN MOUTHS: {winner} SURVIVE {loser}',
            f'ALMOST TOO CLOSE: {winner} GET PAST {loser}',
            f'TWO POINTS OF DAYLIGHT: {winner} DENY {loser}',
            f'WHITE-KNUCKLE WIN: {winner} EDGE {loser}',
            f'JUST ENOUGH: {winner} SQUEEZE PAST {loser}',
        ], gw, winner, loser, 'two-point')

    widest = max(fixtures, key=lambda f: (abs(f['score1'] - f['score2']),
                                            f['score1'] + f['score2']))
    margin = abs(widest['score1'] - widest['score2'])
    winner, loser = ((widest['team1'], widest['team2']) if widest['score1'] >= widest['score2']
                     else (widest['team2'], widest['team1']))
    if margin >= 30:
        return _headline_pick([
            f'ABSOLUTE PASTING: {winner} DESTROY {loser}',
            f'NO CONTEST: {winner} DEMOLISH {loser}',
            f'SLAUGHTERHOUSE: {winner} ROUT {loser}',
            f'CALL THE STEWARDS: {winner} BATTER {loser}',
            f'MERCY RULE NEEDED: {winner} CRUSH {loser}',
            f'BRUTAL: {winner} BLOW {loser} AWAY',
            f'{winner} LEAVE {loser} IN PIECES',
            f'ONE-WAY TRAFFIC: {winner} HAMMER {loser}',
        ], gw, winner, loser, margin, 'rout30')
    if margin >= 20:
        return _headline_pick([
            f'NO MERCY: {winner} THRASH {loser}',
            f'DOMINATION: {winner} SWEEP ASIDE {loser}',
            f'COMPREHENSIVE: {winner} HAMMER {loser}',
            f'BIG WIN ENERGY: {winner} CRUSH {loser}',
            f'RUNAWAY WINNERS: {winner} ROUT {loser}',
            f'{winner} PUT {loser} TO THE SWORD',
            f'THUMPING: {winner} MAKE LIGHT WORK OF {loser}',
            f'STATEMENT WIN: {winner} BATTER {loser}',
            f'ALL {winner}: {loser} SWEPT ASIDE',
            f'HEAVY METAL McDRAFT: {winner} SMASH {loser}',
        ], gw, winner, loser, margin, 'rout20')

    # Ordinary weeks still get variety rather than the same fallback every time.
    high_fixture = max(fixtures, key=lambda f: (max(f['score1'], f['score2']),
                                                 f['score1'] + f['score2']))
    hw, hl = ((high_fixture['team1'], high_fixture['team2'])
              if high_fixture['score1'] >= high_fixture['score2']
              else (high_fixture['team2'], high_fixture['team1']))
    hs = max(high_fixture['score1'], high_fixture['score2'])
    return _headline_pick([
        f'GW{gw}: {hw} LEAD THE WEEKEND CHAOS',
        f'WEEKEND WARRIORS: {hw} SET THE PACE',
        f'{hw} TAKE TOP BILLING IN GW{gw}',
        f'GW{gw} BELONGS TO {hw}',
        f'{hw} EMERGE FROM THE WEEKEND SCRAP',
        f'POINTS ON THE BOARD: {hw} HEADLINE GW{gw}',
        f'ANOTHER WEEK OF NONSENSE: {hw} COME OUT SMILING',
        f'GW{gw}: {hw} WIN THE WEEKEND',
        f'{hw} GRAB THE SPOTLIGHT IN GW{gw}',
        f'CHAOS, POINTS, AND A WIN FOR {hw}',
        f'{hw} TAKE CENTRE STAGE WITH {hs} POINTS',
        f'GW{gw}: {hw} PROVIDE THE MAIN EVENT',
        f'THE DUST SETTLES WITH {hw} ON TOP OF THE WEEKEND BILL',
        f'{hw} WALK AWAY WITH GW{gw} BRAGGING RIGHTS',
        f'NO FIREWORKS, JUST BUSINESS: {hw} GET IT DONE',
        f'GW{gw}: {hw} DO ENOUGH AND THEN SOME',
    ], gw, hw, hl, hs, 'ordinary')


def latest_league_storyline_html():
    if not finished_gws:
        return '<div class="notice">No completed gameweek story yet.</div>'
    gw = max(finished_gws)
    story = league_storyline_for_gw(gw)
    return (f'<div class="storyline-latest"><div class="eyebrow">GW{gw} · THE McDRAFT COLUMN</div>'
            f'<h2 class="mcdraft-column-headline">{escape_html(_mcdraft_column_headline(gw))}</h2>'
            f'{_mcdraft_column_paragraphs_html(story)}</div>')



def _dashboard_current_free_agents(limit=8):
    candidates = []

    for player_id, meta in elements.items():
        if not meta.get("draft_active", True):
            continue
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


def overview_next_fixtures_html():
    """Next unplayed McDraft fixture GW, without prediction or difficulty."""
    upcoming = [int(gw) for gw in full_fixture_schedule if int(gw) > int(dashboard_last_finished_gw or 0)]
    if not upcoming:
        return '<div class="notice">No upcoming McDraft fixtures available.</div>'
    next_gw = min(upcoming)
    html = [f'<p class="card-description">Gameweek {next_gw}</p>', '<div class="fixtures-list">']
    for fixture in full_fixture_schedule.get(next_gw, full_fixture_schedule.get(str(next_gw), [])):
        team1, team2 = fixture.get('team1', '—'), fixture.get('team2', '—')
        rivalry = _derby_name(team1, team2)
        banner = f'<div class="fixture-derby unified-derby">{escape_html(rivalry)}</div>' if rivalry else ''
        html.append(f'<div class="fixture future-fixture-unified">{banner}<div class="fixture-team"><span class="fixture-manager">{escape_html(team1)}</span></div><div class="fixture-vs">VS</div><div class="fixture-team"><span class="fixture-manager">{escape_html(team2)}</span></div></div>')
    html.append('</div>')
    return ''.join(html)


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
        live_intel = _mcdraft_column_intelligence(dashboard_target_gw, 'live')
        if live_intel:
            live_story += "\n\n" + "\n\n".join(live_intel)
        cup_live = _cup_column_for_gw(dashboard_target_gw, 'live')
        if cup_live:
            live_story += "\n\n" + cup_live
        live_story_html = "".join(
            f"<p>{escape_html(paragraph)}</p>"
            for paragraph in live_story.split("\n\n")
            if paragraph.strip()
        )
        return (
            '<div class="storyline-latest">'
            f'<div class="eyebrow">GW{dashboard_target_gw} · LIVE AROUND McDRAFT</div>'
            f'<h2 class="mcdraft-column-headline">{escape_html(_mcdraft_column_headline(dashboard_target_gw, "live"))}</h2>'
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
        preview_intel = _mcdraft_column_intelligence(dashboard_target_gw, 'upcoming')
        if preview_intel:
            preview_story += "\n\n" + "\n\n".join(preview_intel)
        cup_preview = _cup_column_for_gw(dashboard_target_gw, 'upcoming')
        if cup_preview:
            preview_story += "\n\n" + cup_preview
        preview_html = "".join(
            f"<p>{escape_html(paragraph)}</p>"
            for paragraph in preview_story.split("\n\n")
            if paragraph.strip()
        )
        return (
            '<div class="storyline-latest">'
            f'<div class="eyebrow">GW{dashboard_target_gw} · THE McDRAFT PREVIEW</div>'
            f'<h2 class="mcdraft-column-headline">{escape_html(_mcdraft_column_headline(dashboard_target_gw, "upcoming"))}</h2>'
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
        blocks.append('<article class="season-story"><div class="season-story-gw">GW' + str(gw) +
                      '</div><div><h3 class="mcdraft-column-headline">' +
                      escape_html(_mcdraft_column_headline(gw)) + '</h3>' +
                      _mcdraft_column_paragraphs_html(story) + '</div></article>')
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
    if '_cup_milestone_events' in globals():
        events.extend(_cup_milestone_events())
    events.sort(key=lambda x:(-x[0],x[1],x[2]))
    if not events:
        return '<div class="notice">No major milestones yet — give it a week or two.</div>'
    return ''.join(f'<div class="milestone-row"><div class="milestone-gw">GW{gw}</div><div><strong>{escape_html(manager)}</strong><span>{escape_html(title)}</span><small>{escape_html(detail)}</small></div></div>' for gw,manager,title,detail in events)



def record_chase_html():
    if not finished_gws:
        return '<div class="notice">No records to chase yet.</div>'
    best_by_manager={}
    all_scores=[]
    for manager in managers:
        vals=[(int(gw),float(score or 0)) for gw,score in gw_scores.get(manager,[]) if int(gw) in finished_gws]
        if vals:
            gw,score=max(vals,key=lambda x:x[1]); best_by_manager[manager]=(score,gw); all_scores.append((score,manager,gw))
    record_score,record_owner,record_gw=max(all_scores,default=(0,'—','—'))
    historical_best=0; historical_owner='—'; active_runs={}
    for manager in managers:
        form=manager_form_data.get(manager,[]); run=0; best=0
        for r in form:
            run=run+1 if r=='W' else 0; best=max(best,run)
        if best>historical_best: historical_best=best; historical_owner=manager
        active=0
        for r in reversed(form):
            if r=='W': active+=1
            else: break
        active_runs[manager]=active
    moves={m:int(manager_transaction_counts.get(m,0) or 0) for m in managers}
    move_record=max(moves.values(),default=0); move_owner=max(moves,key=moves.get) if moves else '—'
    rows=[]
    for manager in managers:
        best_score,_=best_by_manager.get(manager,(0,'—')); score_gap=max(0.0,record_score-best_score)
        active=active_runs.get(manager,0); streak_gap=max(0,historical_best-active); move_gap=max(0,move_record-moves.get(manager,0))
        rows.append((score_gap,f'<div class="record-chase-row"><div><strong>{escape_html(manager)}</strong><span>Single-GW score</span></div><div><b>{best_score:.0f}</b><small>{score_gap:.0f} pts off record {record_score:.0f}</small></div></div>'))
        if active>0 and historical_best>0:
            plural='s' if streak_gap!=1 else ''
            rows.append((float(streak_gap),f'<div class="record-chase-row"><div><strong>{escape_html(manager)}</strong><span>Active win streak</span></div><div><b>{active}</b><small>{streak_gap} win{plural} off record {historical_best}</small></div></div>'))
        plural='s' if move_gap!=1 else ''
        rows.append((float(move_gap)+0.25,f'<div class="record-chase-row"><div><strong>{escape_html(manager)}</strong><span>Roster activity</span></div><div><b>{moves.get(manager,0)}</b><small>{move_gap} move{plural} off leader {move_record}</small></div></div>'))
    rows.sort(key=lambda x:x[0])
    header=f'<div class="record-chase-summary"><span>GW score record: <strong>{escape_html(record_owner)} · {record_score:.0f} (GW{record_gw})</strong></span><span>Win-streak record: <strong>{escape_html(historical_owner)} · {historical_best}</strong></span><span>Move leader: <strong>{escape_html(move_owner)} · {move_record}</strong></span></div>'
    return header+''.join(html for _,html in rows[:12])


def share_cards_html():
    if not finished_gws:
        return '<div class="notice">Share cards will appear once the season has some history.</div>'
    cards=[]
    leader=current_standings[0] if current_standings else '—'
    cards.append(('Table Setter',leader,f"{league_points.get(leader,0):.0f} league pts · {points_for.get(leader,0):.0f} PF",f"McDraft: {leader} currently lead the league on {league_points.get(leader,0):.0f} points."))
    all_scores=[(float(score or 0),m,int(gw)) for m in managers for gw,score in gw_scores.get(m,[]) if int(gw) in finished_gws]
    if all_scores:
        score,m,gw=max(all_scores); cards.append(('Peak Performance',m,f"{score:.0f} pts · GW{gw}",f"McDraft record watch: {m} posted {score:.0f} points in GW{gw}."))
    original=history.get('original_draft_rank',{}) or {}; ranked=[]
    current_rank={int(pid):i+1 for i,(pid,meta) in enumerate(sorted(elements.items(),key=lambda kv:(-float(kv[1].get('total_points',0) or 0),kv[1].get('web_name',''))))}
    for pid_txt,info in original.items():
        try: pid=int(pid_txt); pick=int(info.get('overall_pick',UNDRAFTED_PLAYER_RANK) or UNDRAFTED_PLAYER_RANK)
        except Exception: continue
        if pick>DRAFTED_PLAYER_COUNT or pid not in current_rank: continue
        ranked.append((pick-current_rank[pid],pid,pick,current_rank[pid]))
    if ranked:
        delta,pid,pick,pr=max(ranked); name=elements.get(pid,{}).get('web_name',f'Player {pid}')
        cards.append(('Draft Steal',name,f"Pick #{pick} → performance rank #{pr}",f"McDraft draft steal: {name} is performing {delta} places above their original pick #{pick}."))
    latest=finished_gws[-1]; score_map={m:float(dict(gw_scores.get(m,[])).get(latest,0) or 0) for m in managers}
    if score_map:
        high=max(score_map,key=score_map.get); cards.append(('Latest Hot Hand',high,f"GW{latest}: {score_map[high]:.0f} pts",f"McDraft GW{latest}: {high} top-scored with {score_map[high]:.0f} points."))
    return ''.join(f'<div class="share-card"><div class="eyebrow">{escape_html(e)}</div><h3>{escape_html(t)}</h3><p>{escape_html(d)}</p><button type="button" class="share-card-button" data-share-text="{escape_html(txt)}" onclick="shareMcDraftCard(this)">Share card</button></div>' for e,t,d,txt in cards[:4])

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
    if '_cup_record_cards' in globals():
        records.extend(_cup_record_cards())

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

        cutline_class = 'cup-cutline-row' if position == 7 and len(ranked) == 10 else ''
        rows += f"""
            <tr class="{cutline_class}">
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

