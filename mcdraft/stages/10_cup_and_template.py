css += r"""
/* FIFA-style squad cards and dynamic player ratings */
.pedigree-cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px;margin:18px 0 22px}
.pedigree-fifa-card{background:linear-gradient(135deg,#233b51,#121b2d 70%);border:1px solid rgba(245,188,83,.35);border-radius:15px;overflow:hidden;min-width:0}
.pedigree-fifa-card[open]{border-color:rgba(245,188,83,.8)}
.pedigree-fifa-card summary{list-style:none;cursor:pointer;padding:16px}
.pedigree-fifa-card summary::-webkit-details-marker{display:none}
.pedigree-head{display:flex;align-items:center;gap:16px;margin-bottom:13px}
.pedigree-overall{flex:none;width:82px;height:97px;border:2px solid;border-radius:9px;display:flex;align-items:center;justify-content:center;flex-direction:column;box-shadow:0 3px 12px rgba(0,0,0,.25)}
.pedigree-overall.platinum,.player-rating-pill.platinum{background:linear-gradient(145deg,#f7ffff 0%,#bde8ee 32%,#8ebcc8 63%,#dff9fa 100%);border-color:#d8ffff;color:#153947;box-shadow:0 0 18px rgba(174,238,244,.22)}
.pedigree-overall.gold,.player-rating-pill.gold{background:linear-gradient(145deg,#ffe7a1,#d7a83d 58%,#9b6d17);border-color:#f7d36b;color:#33250a}
.pedigree-overall.silver,.player-rating-pill.silver{background:linear-gradient(145deg,#f2f5f7,#aeb8c2 58%,#6e7b89);border-color:#d7e0e7;color:#1d2a34}
.pedigree-overall.bronze,.player-rating-pill.bronze{background:linear-gradient(145deg,#e3ad7d,#a86536 58%,#6b3c20);border-color:#d99a68;color:#2f170c}
.rating-tier-number{font-weight:900}.rating-tier-number.platinum{color:#c9f8ff;text-shadow:0 0 10px rgba(172,239,247,.26)}.rating-tier-number.gold{color:#f5c95d}.rating-tier-number.silver{color:#d7e0e7}.rating-tier-number.bronze{color:#d89561}
.pedigree-overall strong{font-size:39px;line-height:1;font-weight:900;letter-spacing:-2px}
.pedigree-overall small{font-size:11px;font-weight:900;letter-spacing:2px;margin-top:4px}
.pedigree-identity{min-width:0}.pedigree-identity h3{margin:0 0 6px;font-size:18px;overflow-wrap:anywhere;color:var(--text)}
.pedigree-identity>small{font-size:11px;color:#c7d3e0}.pedigree-stars{font-size:20px;letter-spacing:1px;color:#f6c55c;margin-bottom:6px}
.pedigree-stars span{font-size:12px;letter-spacing:0;color:var(--text);margin-left:4px}
.pedigree-units{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px}
.pedigree-unit{display:grid;grid-template-columns:1fr auto;gap:6px;color:#d8e0eb;font-size:11px;font-weight:900;letter-spacing:.6px}
.pedigree-unit>b{font-size:18px;color:var(--text);line-height:1}
.pedigree-unit>i{grid-column:span 2;height:5px;background:#465268;border-radius:8px;overflow:hidden}
.pedigree-unit>i em{display:block;height:100%;background:linear-gradient(90deg,#5ce0b9,#f4ce73);border-radius:8px}
.pedigree-open-hint{display:block;color:#aebccf;font-size:10px;margin-top:13px;text-align:right}
.pedigree-detail{padding:0 14px 15px;border-top:1px solid rgba(255,255,255,.11)}
.pedigree-detail-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:13px 0}
.pedigree-detail-stats span{display:flex;flex-direction:column;background:#0d1829;border-radius:8px;padding:9px;font-size:10px;color:#9faebf}
.pedigree-detail-stats b{font-size:18px;color:#f4e0b2}.pedigree-players-table{font-size:11px}
.pedigree-players-table small{display:block;color:#95a9bd;margin-top:3px}
.pedigree-comparison-title{margin:18px 0 10px}.rating-up{color:#48d8a4!important}.rating-down{color:#ff8c8c!important}.rating-flat{color:#a9b4c4!important}
.player-rating-pill{display:inline-flex;align-items:center;gap:3px;width:max-content;margin-top:8px;border:1px solid;border-radius:8px;padding:5px 8px;font-size:21px;font-weight:900;line-height:1}
.player-rating-pill small{font-size:10px}.player-rating-pill em{font-size:10px;margin-left:3px;font-style:normal;background:#102339;padding:4px;border-radius:5px}
.rating-breakdown{flex:1 1 100%;min-width:220px;background:#0d192b;border-radius:10px;padding:12px;margin-top:8px}
.rating-breakdown>b{color:#e9d193}.rating-breakdown p{font-size:11px;line-height:1.6;color:#a8b8ca}
.rating-factor{display:grid;grid-template-columns:minmax(100px,1fr) minmax(65px,2fr) 30px;align-items:center;gap:8px;font-size:11px;margin-top:8px}
.rating-factor-track{height:6px;border-radius:6px;background:#263955;overflow:hidden}.rating-factor-track i{display:block;height:100%;background:linear-gradient(90deg,#3293ca,#80e6c5)}
.rating-factor strong{text-align:right;color:#e9eef5}
@media(max-width:850px){.pedigree-cards{grid-template-columns:1fr}.pedigree-detail-stats{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:520px){.pedigree-head{gap:11px}.pedigree-overall{width:65px;height:80px}.pedigree-overall strong{font-size:30px}.pedigree-identity h3{font-size:15px}.pedigree-stars{font-size:16px}.pedigree-detail-stats{grid-template-columns:repeat(2,minmax(0,1fr))}}
"""

# ============================================================
# MCDRAFT CUP — fixed, independently-scored knockout competition
# GW20–21 preliminary | GW22–23 QF | GW24–25 SF | GW26 final
# ============================================================

CUP_ROUNDS = (
    ('prelim', 'Preliminary round', (20, 21)),
    ('quarter', 'Quarter-finals', (22, 23)),
    ('semi', 'Semi-finals', (24, 25)),
    ('final', 'The final', (26,)),
)


def _cup_table_through(gw, entrants, completed_matches):
    """Rebuild seeding from *completed* league fixtures, never Cup games."""
    record = {name: {'league_points': 0, 'points_for': 0, 'played': 0} for name in entrants}
    eligible = set(entrants)
    for match in completed_matches:
        try:
            event = int(match.get('event') or 0)
            a = match['entry_1_name']; b = match['entry_2_name']
            x = int(match['entry_1_points']); y = int(match['entry_2_points'])
        except (KeyError, TypeError, ValueError):
            continue
        if not 1 <= event <= gw or a not in eligible or b not in eligible or a == b:
            continue
        record[a]['played'] += 1; record[b]['played'] += 1
        record[a]['points_for'] += x; record[b]['points_for'] += y
        if x > y:
            record[a]['league_points'] += 3
        elif y > x:
            record[b]['league_points'] += 3
        else:
            record[a]['league_points'] += 1; record[b]['league_points'] += 1
    ordered = sorted(entrants, key=lambda name: (
        -record[name]['league_points'], -record[name]['points_for'], name.casefold()
    ))
    return ordered, record


def _cup_score(manager, gw, snapshots, official_scores, finished, live_gw):
    """Cup points are GW totals, NOT the result against the league opponent.

    Once a GW finishes, prefer its frozen, official Draft match score. In a
    genuinely live GW use freshly captured player-pick totals, avoiding the
    occasionally stale official head-to-head endpoint.
    """
    if not manager:
        return None
    snapshot = snapshots.get(str(gw), {}) or {}
    team = next((t for t in (snapshot.get('teams') or {}).values()
                 if t.get('manager') == manager), None)
    bench = None
    if team:
        if team.get('bench_points') is not None:
            try:
                bench = int(team['bench_points'])
            except (TypeError, ValueError):
                bench = None
        elif team.get('bench') is not None:
            bench = sum(int(p.get('points') or 0) for p in team['bench'])
    if gw in finished:
        val = official_scores.get(manager, {}).get(gw)
        if val is not None:
            return {'points': int(val), 'bench': bench, 'source': 'official', 'finished': True}
        if team and snapshot.get('finished'):
            return {'points': int(team.get('gw_points') or 0), 'bench': bench,
                    'source': 'captured roster', 'finished': True}
        return None
    if gw == live_gw and team:
        return {'points': int(team.get('gw_points') or 0), 'bench': bench,
                'source': 'live player totals', 'finished': False}
    return None


def _cup_tie(key, label, first, second, weeks, seeds, snapshots, official, finished, live_gw):
    """Calculate leg and aggregate scores, advancing only after every leg."""
    legs = []
    for gw in weeks:
        a = _cup_score(first, gw, snapshots, official, finished, live_gw)
        b = _cup_score(second, gw, snapshots, official, finished, live_gw)
        legs.append({'gw': gw, 'a': a, 'b': b})
    known = first in seeds and second in seeds
    valid_scores = known and all(l['a'] is not None and l['b'] is not None for l in legs)
    all_finished = all(gw in finished for gw in weeks)
    decided = bool(valid_scores and all_finished)
    aggregate_a = (sum(l['a']['points'] for l in legs if l['a']) if known and
                   any(l['a'] is not None for l in legs) else None)
    aggregate_b = (sum(l['b']['points'] for l in legs if l['b']) if known and
                   any(l['b'] is not None for l in legs) else None)
    winner = None; decider = None
    if decided:
        if aggregate_a != aggregate_b:
            winner = first if aggregate_a > aggregate_b else second
            decider = 'aggregate' if len(weeks) > 1 else 'full-time score'
        else:
            # If a historical bench snapshot is genuinely missing, do not
            # manufacture zero bench points: fall back to the higher seed.
            bench_ready = all(l[side].get('bench') is not None
                              for l in legs for side in ('a', 'b'))
            if bench_ready:
                bench_a = sum(l['a']['bench'] for l in legs)
                bench_b = sum(l['b']['bench'] for l in legs)
            else:
                bench_a = bench_b = None
            if bench_ready and bench_a != bench_b:
                winner = first if bench_a > bench_b else second
                decider = 'aggregate bench points' if len(weeks) > 1 else 'bench points'
            else:
                winner = min((first, second), key=lambda name: seeds[name])
                decider = 'higher seed' if bench_ready else 'higher seed (bench data unavailable)'
    return {'key': key, 'label': label, 'teams': (first, second),
            'weeks': weeks, 'legs': legs, 'aggregate': (aggregate_a, aggregate_b),
            'decided': decided, 'winner': winner, 'decider': decider}


def build_mcdraft_cup(entrants, completed_matches, snapshots, official_scores,
                      finished_gws, current_live_gw=None, state=None):
    """Pure bracket builder except for persisting seeds in the supplied state.

    state['seed_order'] is frozen *once* after full GW19 results arrive. A
    partial GW19 cannot accidentally lock provisional seeds. Returned state
    contains no prediction of a future knockout winner.
    """
    entrants = list(dict.fromkeys(name for name in entrants if name and name != 'Unknown'))
    if len(entrants) != 10:
        return {'error': 'The McDraft Cup needs exactly 10 active managers.',
                'entrants': entrants, 'rounds': [], 'locked': False, 'newly_locked': False}
    finished = set(int(g) for g in finished_gws)
    state = state if state is not None else {}
    order, records = _cup_table_through(19, entrants, completed_matches)
    locked = state.get('seed_order')
    newly_locked = False
    if not (isinstance(locked, list) and len(locked) == 10 and set(locked) == set(entrants)):
        locked = None
    if locked is None and 19 in finished:
        # Each team must have a captured finished league result in GW19.
        gw19 = [m for m in completed_matches if int(m.get('event') or 0) == 19]
        complete = set()
        for match in gw19:
            a, b = match.get('entry_1_name'), match.get('entry_2_name')
            if a in entrants and b in entrants and a != b:
                complete.update((a, b))
        if complete == set(entrants):
            locked = list(order)
            state['seed_order'] = list(locked)
            state['locked_through_gw'] = 19
            state['seed_stats'] = {m: dict(records[m]) for m in locked}
            newly_locked = True
    seed_order = locked if locked is not None else order
    seed = {name: i for i, name in enumerate(seed_order, start=1)}
    # Preserve the pre-GW20 stats after seeding; never retroactively mutate.
    seed_records = state.get('seed_stats', records) if locked else records
    def s(n): return seed_order[n - 1]
    def resolved(t): return t['winner'] if t['decided'] and locked else None
    rounds = []
    prelim = [
        _cup_tie('P1', '7 v 10', s(7), s(10), (20, 21), seed, snapshots, official_scores, finished, current_live_gw),
        _cup_tie('P2', '8 v 9', s(8), s(9), (20, 21), seed, snapshots, official_scores, finished, current_live_gw),
    ]
    rounds.append({'key': 'prelim', 'title': 'Preliminary round', 'weeks': (20, 21), 'ties': prelim})
    quarter = [
        _cup_tie('QF1', '1 v winner 8/9', s(1), resolved(prelim[1]), (22, 23), seed, snapshots, official_scores, finished, current_live_gw),
        _cup_tie('QF2', '4 v 5', s(4), s(5), (22, 23), seed, snapshots, official_scores, finished, current_live_gw),
        _cup_tie('QF3', '3 v 6', s(3), s(6), (22, 23), seed, snapshots, official_scores, finished, current_live_gw),
        _cup_tie('QF4', '2 v winner 7/10', s(2), resolved(prelim[0]), (22, 23), seed, snapshots, official_scores, finished, current_live_gw),
    ]
    rounds.append({'key': 'quarter', 'title': 'Quarter-finals', 'weeks': (22, 23), 'ties': quarter})
    semi = [
        _cup_tie('SF1', 'QF1 v QF2', resolved(quarter[0]), resolved(quarter[1]), (24, 25), seed, snapshots, official_scores, finished, current_live_gw),
        _cup_tie('SF2', 'QF3 v QF4', resolved(quarter[2]), resolved(quarter[3]), (24, 25), seed, snapshots, official_scores, finished, current_live_gw),
    ]
    rounds.append({'key': 'semi', 'title': 'Semi-finals', 'weeks': (24, 25), 'ties': semi})
    final = [_cup_tie('FINAL', 'The final', resolved(semi[0]), resolved(semi[1]),
                      (26,), seed, snapshots, official_scores, finished, current_live_gw)]
    rounds.append({'key': 'final', 'title': 'The final', 'weeks': (26,), 'ties': final})
    latest_qualifying = max((g for g in finished if g <= 19), default=0)
    return {'rounds': rounds, 'locked': locked is not None,
            'newly_locked': newly_locked, 'order': seed_order,
            'records': seed_records, 'seed': seed, 'champion': resolved(final[0]),
            'as_of': 19 if locked else latest_qualifying,
            'awaiting_gw19': 19 in finished and locked is None}


def cup_page_html(cup, next_gw=None, game_state=None):
    """Responsive, connected bracket. Detail views use captured, frozen GW squads."""
    import json
    if cup.get('error'):
        return '<div class="card notice">' + escape_html(cup['error']) + '</div>'
    seed = cup['seed']
    order = cup['order']
    if next_gw is None:
        next_gw = max(1, int(cup.get('as_of', 0) or 0) + 1)
    next_gw = int(next_gw)
    game_state = game_state or 'completed'
    countdown = max(0, 20 - next_gw)
    def team_html(name, fallback):
        if name not in seed:
            return '<span class="cup-placeholder">' + escape_html(fallback) + '</span>'
        return (f'<span class="cup-seed">#{seed[name]}</span>'
                f'<strong class="cup-team-name">{escape_html(name)}</strong>')
    def show_points(value):
        return '—' if value is None else str(value)
    fallbacks = {
        'QF1': ('Seed 1', 'Winner P2'), 'QF4': ('Seed 2', 'Winner P1'),
        'SF1': ('Winner QF1', 'Winner QF2'),
        'SF2': ('Winner QF3', 'Winner QF4'),
        'FINAL': ('Winner SF1', 'Winner SF2'),
    }
    def card_html(tie):
        a, b = tie['teams']
        alt = fallbacks.get(tie['key'], ('TBC', 'TBC'))
        agg_a, agg_b = tie['aggregate']
        legs = []
        js_key = escape_html(json.dumps(tie["key"]))
        for i, leg in enumerate(tie['legs']):
            sa, sb = leg['a'], leg['b']
            live = bool((sa and not sa['finished']) or (sb and not sb['finished']))
            complete = bool(sa and sb and sa['finished'] and sb['finished'])
            score = (f'{show_points(sa["points"] if sa else None)} – '
                     f'{show_points(sb["points"] if sb else None)}')
            leg_status = 'LIVE' if live else 'FT' if complete else 'SCHEDULED'
            legs.append(
                f'<button type="button" class="cup-leg-button{" cup-leg-live" if live else ""}" '
                f'onclick="event.stopPropagation();openCupTie({js_key}, {leg["gw"]})" '
                f'aria-label="View {escape_html(tie["key"])} gameweek {leg["gw"]} leg details">'
                f'<span>GW{leg["gw"]} <small>{leg_status}</small></span><b>{score}</b>'
                '</button>'
            )
        def team_row(name, fallback, score):
            advancing = bool(tie['decided'] and tie['winner'] == name)
            return (f'<div class="cup-entrant{" cup-entrant-winner" if advancing else ""}">'
                    f'<div class="cup-entrant-identity">{team_html(name, fallback)}</div>'
                    f'<span class="cup-aggregate">{show_points(score)}</span></div>')
        played = sum(bool(l['a'] and l['b'] and l['a']['finished'] and l['b']['finished'])
                     for l in tie['legs'])
        live_legs = [l for l in tie['legs'] if (l['a'] and not l['a']['finished'])
                     or (l['b'] and not l['b']['finished'])]
        status = ('CHAMPION DECIDED' if tie['decided'] and tie['key'] == 'FINAL'
                  else 'AGG · FT' if tie['decided'] and len(tie['legs']) > 1
                  else 'FULL TIME' if tie['decided']
                  else f'GW{live_legs[-1]["gw"]} LIVE' if live_legs
                  else 'HALF TIME' if played and len(tie['legs']) > 1
                  else 'UPCOMING' if a and b else 'AWAITING QUALIFIERS')
        filter_teams = '|'.join(escape_html(str(x)) for x in (a, b) if x)
        decider = (f'<div class="cup-decider">Through on {escape_html(tie["decider"])}'
                     f'</div>' if tie['decider'] and tie['decider'] not in ('aggregate', 'full-time score') else '')
        return (f'<article class="cup-tie" data-tie="{tie["key"]}" data-cup-teams="{filter_teams}" '
                f'tabindex="0" role="button" '
                f'aria-label="Open {tie["key"]} cup tie details" '
                f'onclick="openCupTie({js_key})" '
                f'onkeydown="cupTieKeydown(event,{js_key})">'
                f'<div class="cup-tie-head"><b>{tie["key"]}</b><span>{status}</span></div>'
                f'{team_row(a, alt[0], agg_a)}{team_row(b, alt[1], agg_b)}'
                f'<div class="cup-legs">{"".join(legs)}</div>{decider}'
                '<span class="cup-tie-more">Tap a leg for lineup &amp; points ↗</span></article>')
    seed_rows = []
    for i, manager in enumerate(order, start=1):
        rec = cup['records'].get(manager, {})
        # Fixed route: seed 7 plays 10, seed 8 plays 9.
        opponent = {7: 10, 8: 9, 9: 8, 10: 7}.get(i)
        route = 'Bye to quarter-finals' if i <= 6 else f'Prelim · v #{opponent}'
        seed_rows.append(f'<tr><td class="cup-seed-rank">{i}</td>'
                         f'<td class="manager-name">{escape_html(manager)}</td>'
                         f'<td>{rec.get("league_points",0)}</td>'
                         f'<td>{rec.get("points_for",0)}</td>'
                         f'<td>{route}</td></tr>')
    stages = []
    for info in cup['rounds']:
        weeks = info['weeks']
        gw_label = '–'.join(map(str, weeks))
        stages.append(f'<section class="cup-stage" data-round="{info["key"]}" id="cup-round-{info["key"]}">'
                      f'<header class="cup-stage-head"><h3>{escape_html(info["title"])}</h3>'
                      f'<span>GW{gw_label} · {"ONE LEG" if len(weeks)==1 else "TWO LEGS"}</span></header>'
                      f'<div class="cup-stage-ties">{"".join(card_html(t) for t in info["ties"])}</div>'
                      '</section>')
    if cup['champion']:
        hero = (f'<div class="cup-champion"><span>🏆 MCDRAFT CUP CHAMPION</span>'
                f'<strong>{escape_html(cup["champion"])}</strong>'
                '<small>GW26 single-leg final · cup honours secured</small></div>')
    else:
        if countdown:
            banner = (f'<div class="cup-countdown"><strong>{countdown}</strong>'
                      f'<span>GW{"s" if countdown != 1 else ""} until kickoff</span>'
                      '<small>Starts GW20</small></div>')
        elif next_gw == 20 and game_state != 'live':
            banner = ('<div class="cup-countdown"><strong>0</strong>'
                      '<span>GWs until kickoff</span><small>Starts this GW · GW20</small></div>')
        else:
            active = next((r for r in cup['rounds'] if next_gw in r['weeks']), None)
            banner = ('<div class="cup-countdown cup-countdown-active"><strong>LIVE</strong>'
                      f'<span>{escape_html(active["title"]) if active else "Cup underway"}</span>'
                      f'<small>GW{next_gw}</small></div>' if next_gw <= 26 else
                      '<div class="cup-countdown"><strong>…</strong><span>Awaiting final result</span></div>')
        hero = ('<div class="cup-hero"><div><span>🏆 MCDRAFT CUP</span>'
                '<h2>One trophy. Two legs. No mercy.</h2>'
                '<p>Prelims GW20–21 · quarters GW22–23 · semis GW24–25 · '
                'one-leg final GW26. Separate from your league head-to-heads.</p></div>'
                f'{banner}</div>')
    lock = ('<span class="cup-lock locked">Seeds locked · GW19</span>' if cup['locked']
            else f'<span class="cup-lock">Provisional seedings · through GW{cup["as_of"]}</span>')
    warning = ('<p class="cup-warning">GW19 is marked finished, but not every league fixture '
               'was captured. Seeds cannot freeze until all ten managers have a result.</p>'
               if cup['awaiting_gw19'] else '')
    options = ''.join('<option value="' + escape_html(m) + '">' + escape_html(m) + '</option>' for m in order)
    modal = ('<div id="cup-detail-overlay" class="cup-detail-overlay" hidden '
             'onclick="if(event.target===this)closeCupTie()">'
             '<section class="cup-detail-dialog" role="dialog" aria-modal="true" '
             'aria-labelledby="cup-detail-title" tabindex="-1">'
             '<div class="cup-detail-top"><span class="cup-detail-eyebrow">🏆 MCDRAFT CUP · MATCH CENTRE</span>'
             '<button type="button" class="cup-detail-close" onclick="closeCupTie()" '
             'aria-label="Close Cup match details">✕</button></div>'
             '<h2 id="cup-detail-title"></h2><div id="cup-detail-body"></div>'
             '</section></div>')
    return (hero + '<div class="cup-intro-row"><div>' + lock + warning +
            '<p>Seeds 1–6 skip the prelims. Aggregate score decides two-legged ties; '
            'if level, combined bench points then higher seed. In the GW26 final '
            'those tiebreakers apply to that gameweek only.</p></div>'
            '<label class="cup-filter-label" for="cup-team-filter">Follow a team '
            '<select id="cup-team-filter" onchange="filterCupTeams()">'
            '<option value="">All teams</option>' + options + '</select></label></div>'
            '<p class="cup-bracket-hint">← Swipe sideways to explore the knockout bracket. '
            'Tap a matchup or individual GW leg for the full scorecard. →</p>'
            '<div class="cup-bracket-viewport" tabindex="0" aria-label="Scrollable Cup bracket">'
            '<div class="cup-bracket" aria-label="Connected Cup knockout bracket">' + ''.join(stages) +
            '</div></div>'
            '<div class="card cup-seeding"><h2>Pre-Cup league seedings</h2>'
            '<p class="card-description">League points, then points scored, then manager name. '
            'Frozen once all GW19 fixtures finish.</p>'
            '<div class="table-wrap"><table><thead><tr><th>Seed</th><th>Manager</th>'
            '<th>League pts</th><th>Pts scored</th><th>Route</th></tr></thead><tbody>' +
            ''.join(seed_rows) + '</tbody></table></div></div>' + modal)


def cup_detail_payload(cup, snapshots):
    """Use the actual historical roster in each GW, never today's roster."""
    out = {}
    if cup.get('error'):
        return out
    for info in cup['rounds']:
        for tie in info['ties']:
            obj = {'id': tie['key'], 'round': info['title'], 'teams': list(tie['teams']),
                   'seeds': [cup['seed'].get(n) for n in tie['teams']],
                   'aggregate': list(tie['aggregate']), 'winner': tie['winner'],
                   'decided': tie['decided'], 'decider': tie['decider'], 'legs': []}
            for i, leg in enumerate(tie['legs']):
                week = (snapshots.get(str(leg['gw']), {}) or {})
                score_a, score_b = leg['a'], leg['b']
                lineups = []
                for name in tie['teams']:
                    squad = next((team for team in (week.get('teams') or {}).values()
                                  if team.get('manager') == name), None)
                    def players(rows):
                        return [{'name': p.get('web_name') or 'Unknown',
                                 'position': p.get('position') or '',
                                 'club': p.get('team') or '',
                                 'points': p.get('points'),
                                 'minutes': p.get('minutes'),
                                 'captain': bool(p.get('is_captain'))}
                                for p in (rows or [])]
                    lineups.append({'name': name, 'xi': players(squad.get('starters')) if squad else [],
                                    'bench': players(squad.get('bench')) if squad else [],
                                    'captured': squad is not None})
                obj['legs'].append({'gw': leg['gw'], 'number': i + 1,
                                    'scores': [score_a['points'] if score_a else None,
                                               score_b['points'] if score_b else None],
                                    'benches': [score_a['bench'] if score_a else None,
                                                score_b['bench'] if score_b else None],
                                    'sources': [score_a['source'] if score_a else None,
                                                score_b['source'] if score_b else None],
                                    'finished': bool(score_a and score_b and score_a['finished'] and score_b['finished']),
                                    'live': bool((score_a and not score_a['finished'])
                                                 or (score_b and not score_b['finished'])),
                                    'lineups': lineups})
            out[tie['key']] = obj
    return out


def _cup_column_for_gw(gw, phase='completed'):
    """Cup match facts and colour for the McDraft editorial, starting GW20 only."""
    gw = int(gw)
    if gw < 20 or gw > 26:
        return ''
    cup = globals().get('mcdraft_cup') or {}
    if not cup.get('locked'):
        return ''
    stage = next((r for r in cup.get('rounds', []) if gw in r['weeks']), None)
    if not stage:
        return ''
    active = [t for t in stage['ties'] if all(n in cup['seed'] for n in t['teams'])]
    if not active:
        return ''
    rng = random.Random(LEAGUE_ID * 13 + gw * 12011)
    title = stage['title'].lower()
    second_leg = len(stage['weeks']) > 1 and gw == stage['weeks'][-1]
    if phase == 'upcoming':
        if gw == 20:
            pairs = '; '.join(f'#{cup["seed"][a]} {a} v #{cup["seed"][b]} {b}'
                              for a, b in (t['teams'] for t in active))
            return rng.choice([
                f'🏆 CUP WATCH: A second competition barges into McDraft in GW20. The two-legged preliminaries open with {pairs}. Six teams sit smugly on byes; four have to earn their place in the quarter-finals.',
                f'🏆 CUP FEVER: The McDraft Cup kicks off in GW20! Opening fixtures: {pairs}. GW21 finishes the job, with six higher seeds already watching from the quarter-finals.',
            ])
        if second_leg:
            close = sorted((t for t in active if all(l['a'] and l['b'] for l in t['legs'][:1])),
                           key=lambda t: abs(t['legs'][0]['a']['points']-t['legs'][0]['b']['points']))
            if close:
                t = close[0]; a, b = t['teams']; leg = t['legs'][0]
                return (f'🏆 CUP WATCH: The {title} reach their second legs in GW{gw}. '
                        f'{a} and {b} resume at {leg["a"]["points"]}–{leg["b"]["points"]} after the opener. '
                        'Aggregate scores decide who goes through; bench points are lurking as the tiebreak.')
        focus = active[0]; a, b = focus['teams']
        return (f'🏆 CUP WATCH: GW{gw} brings the {title}: {a} versus {b} '
                f'{"in the one-off final" if gw == 26 else "is on the knockout card"}. '
                'League results mean nothing here; this is an entirely separate scrap for silverware.')
    visible = [t for t in active if any(l['gw'] == gw and l['a'] and l['b'] for l in t['legs'])]
    if not visible:
        return ''
    scored = [(t, next(l for l in t['legs'] if l['gw'] == gw)) for t in visible]
    tightest = min(scored, key=lambda item: abs(item[1]['a']['points']-item[1]['b']['points']))
    t, leg = tightest; a, b = t['teams']; x, y = leg['a']['points'], leg['b']['points']
    live = phase == 'live'
    if second_leg:
        agg_a, agg_b = t['aggregate']
        result = (f'{a} {agg_a}–{agg_b} {b} on aggregate' if agg_a is not None and agg_b is not None
                  else f'{a} and {b} still trading punches')
    else:
        result = f'{a} {x}–{y} {b}'
    if live:
        if gw == 26:
            return (f'🏆 CUP LIVE: The one-leg GW26 final is on! {result} as it stands. '
                    'No aggregate safety net, no second chance; the trophy stays undecided until full-time.')
        return (f'🏆 CUP LIVE: The {title} are happening alongside the league. '
                f'The closest cup battle right now is {result}. '
                f'{"This is leg two; aggregate decides the survivors" if second_leg else "This is leg one; next GW brings the return fixtures"}. '
                'Those scores are provisional while football is still being played.')
    if gw == 26:
        final = active[0]
        if final['decided']:
            return (f'🏆 CUP FINAL: {final["winner"]} have lifted the McDraft Cup after '
                    f'{a} {x}–{y} {b} in the one-off GW26 final! '
                    f'{"The tiebreak was " + final["decider"] + "." if final["decider"] not in ("full-time score",) else "One game, one trophy, endless group-chat material."}')
    decided = [t for t in active if t['decided'] and t['weeks'][-1] == gw]
    if decided:
        winners = [f'{t["winner"]} ({t["aggregate"][0]}–{t["aggregate"][1]} agg)' for t in decided]
        shock = next((t for t in decided if t['winner'] != min(t['teams'],key=lambda n:cup['seed'][n])), None)
        shock_note = (f' Seed #{cup["seed"][shock["winner"]]} {shock["winner"]} have taken out '
                      f'a higher seed — the Cup has its upset!' if shock else '')
        if len(winners) > 2:
            winners_text = ', '.join(w.split(' (')[0] for w in winners)
        else:
            winners_text = ' and '.join(winners)
        return (f'🏆 CUP WATCH: The {title} are settled after GW{gw}: {winners_text} advance. '
                f'{result} was the closest tie this week.{shock_note} '
                'The Cup bracket marches on regardless of what happened in the league.')
    if second_leg:
        return (f'🏆 CUP WATCH: GW{gw} saw the second legs of the {title}, with {result}. '
                'Advancement is still awaiting complete, final scores.')
    return (f'🏆 CUP WATCH: Opening legs of the {title} have been played: {result} '
            f'in GW{gw}. Nothing is settled yet; the return legs are in GW{gw + 1}, '
            'and a narrow first-leg lead is about as safe as a chocolate teapot.')


mcdraft_cup_state = history.setdefault('mcdraft_cup', {})
_mcdraft_cup_entrants = list(dict.fromkeys(entry_names.values()))
_mcdraft_live_gw = (dashboard_target_gw if dashboard_game_state == 'live'
                        and dashboard_target_is_live else None)
mcdraft_cup = build_mcdraft_cup(
    _mcdraft_cup_entrants,
    history.get('matches', []),
    history.get('gameweeks', {}),
    official_score_by_manager_gw,
    finished_gws,
    _mcdraft_live_gw,
    mcdraft_cup_state,
)
if mcdraft_cup.get('newly_locked'):
    # The scraper writes history earlier in this script. Persist immutable
    # seed order immediately so later league movement cannot change the Cup.
    with open(HISTORY_FILE, 'w', encoding='utf-8') as _cup_history_out:
        json.dump(history, _cup_history_out, indent=2, ensure_ascii=False)
    print('McDraft Cup seedings frozen at the completed GW19 league standings.')


# ============================================================
# MCDRAFT EDITORIAL DESK / CUP AWARDS / LEAGUE CUT LINE
# ============================================================

def _cup_milestone_events():
    cup = globals().get('mcdraft_cup') or {}
    if cup.get('error') or not cup.get('locked'):
        return []
    finished = {int(g) for g in finished_gws}
    events = []
    for stage in cup.get('rounds', []):
        for tie in stage.get('ties', []):
            a, b = tie['teams']
            if not a or not b:
                continue
            if stage['key'] == 'prelim':
                leg = tie['legs'][0]
                if 20 in finished and leg['a'] and leg['b'] and leg['a']['finished'] and leg['b']['finished']:
                    events.append((20, a, '🏆 Cup debut', f'Opened the Cup against {b}: {leg["a"]["points"]}–{leg["b"]["points"]} in the first leg.'))
                    events.append((20, b, '🏆 Cup debut', f'Opened the Cup against {a}: {leg["b"]["points"]}–{leg["a"]["points"]} in the first leg.'))
            if not tie.get('decided') or tie['weeks'][-1] not in finished:
                continue
            gw = int(tie['weeks'][-1])
            winner = tie['winner']
            loser = b if winner == a else a
            sa, sb = tie['aggregate']
            score_text = f'{sa}–{sb}' + (' aggregate' if len(tie['weeks']) > 1 else ' in the one-leg final')
            title = {'prelim':'🏆 Preliminary winner', 'quarter':'🏆 Cup semi-finalist',
                     'semi':'🏆 Cup finalist', 'final':'🏆 McDraft Cup champion'}[stage['key']]
            detail = f'Beat {loser}, {score_text} in GW{gw}.'
            if tie.get('decider') not in ('aggregate', 'full-time score'):
                detail += f' Tiebreak: {tie["decider"]}.'
            events.append((gw, winner, title, detail))
            if stage['key'] == 'final':
                events.append((gw, loser, '🥈 Cup runner-up', f'Finished as runner-up to {winner} in GW26 ({score_text}).'))
            if cup['seed'].get(winner, 0) > cup['seed'].get(loser, 0):
                events.append((gw, winner, '🏆 Cup giant-killing',
                               f'Seed #{cup["seed"][winner]} knocked out #{cup["seed"][loser]} {loser} in the {stage["title"].lower()}.'))
            if len(tie['legs']) == 2 and all(l['a'] and l['b'] and l['a']['finished'] and l['b']['finished'] for l in tie['legs']):
                first = tie['legs'][0]
                first_a, first_b = first['a']['points'], first['b']['points']
                if (winner == a and first_a < first_b) or (winner == b and first_b < first_a):
                    deficit = abs(first_a - first_b)
                    events.append((gw, winner, '🏆 Second-leg comeback',
                                   f'Overturned a {deficit}-point first-leg deficit against {loser} to progress.'))
    return events


def _cup_record_cards():
    """Cup-only awards from completed legs/ties; omit unknown future records."""
    cup = globals().get('mcdraft_cup') or {}
    if cup.get('error') or not cup.get('locked'):
        return []
    finished = {int(g) for g in finished_gws}
    legs = []
    decided = []
    upsets = []
    comebacks = []
    for stage in cup.get('rounds', []):
        for tie in stage.get('ties', []):
            a, b = tie['teams']
            if not a or not b:
                continue
            for leg in tie['legs']:
                if (int(leg['gw']) in finished and leg['a'] and leg['b']
                        and leg['a']['finished'] and leg['b']['finished']):
                    for name, result, opponent in ((a, leg['a'], b), (b, leg['b'], a)):
                        legs.append((int(result['points']), name, int(leg['gw']), opponent))
            if not tie.get('decided') or int(tie['weeks'][-1]) not in finished:
                continue
            winner = tie['winner']
            loser = b if winner == a else a
            sa, sb = tie['aggregate']
            diff = abs(sa - sb)
            decided.append((diff, winner, loser, stage['title'], sa, sb))
            gap = cup['seed'].get(winner, 0) - cup['seed'].get(loser, 0)
            if gap > 0:
                upsets.append((gap, winner, loser, stage['title']))
            if len(tie['legs']) == 2 and all(l['a'] and l['b'] for l in tie['legs']):
                first = tie['legs'][0]
                deficit = ((first['b']['points'] - first['a']['points']) if winner == a
                           else (first['a']['points'] - first['b']['points']))
                if deficit > 0:
                    comebacks.append((deficit, winner, loser, stage['title']))
    records = []
    if legs:
        score, manager, gw, opponent = max(legs, key=lambda row: (row[0], -row[2]))
        records.append(('🏆 Highest Cup leg score', manager,
                        f'{score} pts against {opponent} · GW{gw}'))
    if decided:
        biggest = max(decided, key=lambda row: row[0])
        closest = min(decided, key=lambda row: row[0])
        records.append(('🏆 Biggest Cup knockout win', biggest[1],
                        f'{biggest[0]}-pt margin v {biggest[2]} · {biggest[3]}'))
        records.append(('🏆 Closest Cup knockout tie', f'{closest[1]} v {closest[2]}',
                        f'{closest[4]}–{closest[5]} · {closest[3]}'))
    if upsets:
        gap, winner, loser, round_name = max(upsets, key=lambda row: row[0])
        records.append(('🏆 Biggest Cup seed upset', winner,
                        f'#{cup["seed"][winner]} beat #{cup["seed"][loser]} {loser} · {round_name}'))
    if comebacks:
        deficit, winner, loser, round_name = max(comebacks, key=lambda row: row[0])
        records.append(('🏆 Biggest Cup comeback', winner,
                        f'Overturned {deficit} pts v {loser} · {round_name}'))
    if cup.get('champion') and 26 in finished:
        final = cup['rounds'][-1]['ties'][0]
        runner = next((n for n in final['teams'] if n != cup['champion']), '—')
        score_a, score_b = final['aggregate']
        records.append(('🏆 McDraft Cup winner', cup['champion'],
                        f'GW26 final v {runner} · {score_a}–{score_b}'))
    return records


def _mcdraft_column_intelligence(gw, phase='completed'):
    """Evidence-led, deterministic editorial beats. No current data in old GWs."""
    gw = int(gw)
    rng = random.Random(LEAGUE_ID * 7919 + gw * 31337 + {'completed':1,'upcoming':2,'live':3}.get(phase,0))
    beats = []
    if phase == 'completed':
        if gw not in finished_gws:
            return []
        week = history.get('gameweeks', {}).get(str(gw), {}) or {}
        if not week.get('finished'):
            return []
        squads = list((week.get('teams') or {}).values())
        bench_stories = []
        club_stories = []
        for squad in squads:
            manager = squad.get('manager') or 'Unknown'
            starter = squad.get('starters', []) or []
            bench = squad.get('bench', []) or []
            if starter and bench:
                best_bench = max(bench, key=lambda p: int(p.get('points', 0) or 0))
                if int(best_bench.get('points', 0) or 0) >= 8:
                    bench_stories.append((int(best_bench['points']), manager, best_bench.get('web_name','Unknown')))
            by_club = defaultdict(int)
            by_club_count = defaultdict(int)
            for pick in starter:
                club = str(pick.get('team') or '').strip()
                if not club:
                    continue
                by_club[club] += int(pick.get('points', 0) or 0)
                by_club_count[club] += 1
            for club, score in by_club.items():
                if by_club_count[club] >= 2 and score >= 12:
                    club_stories.append((score, manager, club, by_club_count[club]))
        if bench_stories:
            score, manager, player = max(bench_stories)
            beats.append(rng.choice([
                f'🪑 SELECTION DESK: {manager} left {player} and {score} points on the bench in GW{gw}. The substitutes have requested a meeting with the manager.',
                f'🪑 BENCH WATCH: {player} produced {score} points from {manager}’s bench. A rather expensive view of the action.'
            ]))
        if club_stories:
            score, manager, club, count = max(club_stories)
            beats.append(rng.choice([
                f'⚽ CLUB CONNECTION: {manager} fielded {count} players from {club}, who combined for {score} points in GW{gw}. The Premier League club double-up paid its rent.',
                f'⚽ CLUB WATCH: A {club} contingent of {count} starters delivered {score} points for {manager} this week. Sometimes the same-club gamble comes off.'
            ]))
        # Archived editions report only observed completed GW facts.
        return beats[:2]
    if gw != int(dashboard_target_gw) or phase not in ('upcoming','live'):
        return []
    owned = [(int(pid), name, elements.get(int(pid), {}),
              _player_ratings_by_id.get(int(pid), {}))
             for pid, name in _dashboard_current_owner.items() if name in managers]
    status_groups = defaultdict(list)
    for pid, manager, meta, detail in owned:
        status = _fpl_availability.get(pid, {}) or {}
        flag = status.get('status')
        if flag not in ('i', 's', 'd', 'u'):
            continue
        chance = status.get('chance_next')
        label = {'i':'injured','s':'suspended','d':'doubtful','u':'unavailable'}[flag]
        rating = int(detail.get('rating', 35) or 35)
        status_groups[manager].append((rating, meta.get('web_name', f'Player {pid}'), label, chance))
    if status_groups:
        # Prioritise a manager whose flagged assets carry significant rating.
        manager = max(status_groups, key=lambda m: sum(x[0] for x in status_groups[m]))
        issues = sorted(status_groups[manager], reverse=True)
        high = issues[0]
        suspension_count = sum(1 for x in issues if x[2] == 'suspended')
        snippet = f'{high[1]} ({high[0]}/100) is officially flagged {high[2]}'
        if high[3] is not None:
            snippet += f' with a {high[3]}% next-round playing chance'
        if len(issues) > 1:
            snippet += f'; {len(issues)-1} other squad member(s) are flagged'
        if suspension_count:
            snippet += f', including {suspension_count} suspension(s)'
        beats.append(rng.choice([
            f'🚑 TREATMENT ROOM: {manager} have availability questions: {snippet}. These are the current FPL flags, not confirmed lineups.',
            f'🚑 SQUAD ALERT: The FPL status board has a headache for {manager}: {snippet}. The selection spreadsheet is sweating.'
        ]))
    # Fixture context is drawn from the current PL schedule and existing club
    # strength model; highlight a high-rated player's opponent and location.
    opportunities = []
    hazards = []
    for pid, manager, meta, detail in owned:
        rating = int(detail.get('rating', 35) or 35)
        if rating < 68:
            continue
        try:
            club = int(meta.get('team'))
        except (ValueError, TypeError):
            continue
        club_strength = float(_pl_club_strength_score.get(club, .5))
        for scheduled in _pl_fixtures_by_event_team.get((gw, club), []):
            fixture = scheduled['fixture']
            if phase == 'live' and fixture.get('finished'):
                continue
            opponent = int(scheduled['opponent'])
            difficulty = float(_pl_club_strength_score.get(opponent, .5))
            venue = 'at home' if scheduled['is_home'] else 'away'
            row = (club_strength - difficulty, rating, manager,
                   meta.get('web_name', f'Player {pid}'),
                   teams_lookup.get(opponent, f'club {opponent}'), venue)
            if row[0] >= .12:
                opportunities.append(row)
            elif row[0] <= -.12:
                hazards.append(row)
    if opportunities:
        _, rating, manager, player, opponent, venue = max(opportunities)
        beats.append(rng.choice([
            f'📅 FIXTURE RADAR: {manager} have a possible fixture opening: {player} ({rating}/100) faces {opponent} {venue} in GW{gw}. The PL club-strength model rates that matchup favourably, not a guaranteed haul.',
            f'📅 FIXTURE WATCH: The schedule gives {manager} a potential edge through {player} ({rating}/100), whose club meet {opponent} {venue}. Mind you, fixtures do not score points by themselves.'
        ]))
    if hazards and not opportunities:
        _, rating, manager, player, opponent, venue = min(hazards)
        beats.append(f'📅 FIXTURE RADAR: {manager}’s {player} ({rating}/100) faces a tough PL-club matchup with {opponent} {venue} in GW{gw}, according to the current club-strength model.')
    if phase == 'upcoming' and int(fixture_prediction_gw or 0) == gw:
        fixtures = full_fixture_schedule.get(gw, []) or []
        candidates = []
        for item in fixtures:
            a, b = item.get('team1'), item.get('team2')
            if a not in season_prediction or b not in season_prediction:
                continue
            fa = season_prediction[a]; fb = season_prediction[b]
            pa = float((fa.get('model_weekly_score_by_gw') or {}).get(gw, fa.get('model_weekly_score', 0)) or 0)
            pb = float((fb.get('model_weekly_score_by_gw') or {}).get(gw, fb.get('model_weekly_score', 0)) or 0)
            if pa > 0 and pb > 0:
                candidates.append((abs(pa-pb), a, b, pa, pb))
        if candidates:
            gap, a, b, pa, pb = max(candidates)
            if gap >= 3:
                beats.append(rng.choice([
                    f'🔮 PREDICTION DESK: The current model projects {a} {pa:.0f}–{pb:.0f} {b} in GW{gw}, a {gap:.1f}-point projected gap. That is a forecast, not a result.',
                    f'🔮 MODEL WATCH: Of this week’s H2Hs, {a} v {b} shows the widest projected scoring difference: {pa:.0f}–{pb:.0f}. Please do not laminate the prediction before kick-off.'
                ]))
            else:
                beats.append(f'🔮 PREDICTION DESK: {a} v {b} is one of the tight projected matchups at {pa:.0f}–{pb:.0f}. The model can barely get a cigarette paper between them.')
    if phase == 'live':
        raw = [m for m in league_matches_all if int(m.get('event',0) or 0) == gw]
        ongoing = []
        for match in raw:
            e1, e2 = match.get('league_entry_1'), match.get('league_entry_2')
            a = league_entry_id_to_name.get(e1, league_entry_id_to_name.get(str(e1)))
            b = league_entry_id_to_name.get(e2, league_entry_id_to_name.get(str(e2)))
            if a not in managers or b not in managers:
                continue
            xa, xb = _live_manager_current_score(a), _live_manager_current_score(b)
            ra, rb = _live_manager_remaining_profile(a), _live_manager_remaining_profile(b)
            left_a, left_b = int(ra.get('players_left', 0)), int(rb.get('players_left', 0))
            ongoing.append((abs(xa-xb), a, b, xa, xb, left_a, left_b))
        if ongoing:
            _, a, b, xa, xb, left_a, left_b = min(ongoing)
            beats.append(f'🔮 LIVE SWING WATCH: {a} {xa}–{xb} {b} from the live XI totals, with {left_a} and {left_b} players still to finish respectively. This is provisional; neither side has booked the three points yet.')
    rising = []
    for pid, manager, meta, detail in owned:
        change = detail.get('change')
        if isinstance(change, (int,float)) and change >= 3:
            rising.append((change, int(detail.get('rating',35)), manager, meta.get('web_name', f'Player {pid}')))
    if rising:
        change, rating, manager, player = max(rising)
        beats.append(f'📈 RATING MARKET: {player} of {manager} is up {int(change)} points since the previous rating update, now {rating}/100. The form model has noticed; the rest of McDraft might soon follow.')
    # Cap at three extra beats to preserve the character of one shared column.
    if phase == 'live':
        priority = ('🚑', '🔮', '📅', '📈')
    else:
        priority = ('🔮', '🚑', '📅', '📈')
    return sorted(beats, key=lambda b: next((i for i, p in enumerate(priority) if b.startswith(p)), 99))[:3]

cup_css = r'''
/* Inspectable analytical charts with persistently readable mobile details. */
.analytics-chart-card [data-chart-detail],.analytics-chart-card .analytics-bar-row,
.time-machine-svg circle,.rating-lab-trend circle,.matrix-manager-point{cursor:pointer;touch-action:manipulation}
.analytics-chart-card [data-chart-detail]:focus-visible,.analytics-chart-card .analytics-bar-row:focus-visible,
.analytics-pie-legend-row:focus-visible,.time-machine-svg circle:focus-visible{outline:2px solid var(--accent,#38bdf8);outline-offset:3px}
.analytics-chart-card .analytics-bar-row.mcdraft-chart-selected{background:rgba(56,189,248,.09);border-radius:6px}
.analytics-pie{cursor:pointer;touch-action:manipulation}
.analytics-pie-legend-row{width:100%;text-align:left;background:transparent;border:1px solid transparent;border-radius:6px;padding:6px 5px;color:var(--text,#e2e8f0);cursor:pointer;font:inherit}
.analytics-pie-legend-row.mcdraft-chart-selected{background:rgba(56,189,248,.12);border-color:var(--accent,#38bdf8)}
.mcdraft-chart-inspector{position:fixed;z-index:10080;bottom:22px;right:22px;width:min(370px,calc(100vw - 28px));padding:14px 16px;background:var(--card,#172033);color:var(--text,#fff);border:2px solid var(--accent,#38bdf8);box-shadow:0 14px 40px rgba(0,0,0,.35);border-radius:14px;line-height:1.45;overflow-wrap:anywhere}
.mcdraft-chart-inspector[hidden]{display:none}
.mcdraft-chart-inspector-head{display:flex;justify-content:space-between;align-items:center;gap:10px}
.mcdraft-chart-inspector-title{font-size:12px;letter-spacing:.03em}
.mcdraft-chart-inspector-head button{font:inherit;font-size:23px;line-height:1;cursor:pointer;color:var(--text,#fff);border:0;background:transparent;padding:2px 5px}
.mcdraft-chart-inspector-value{font-size:14px;font-weight:750;color:var(--text,#fff);margin:10px 0 0}
[data-theme="light"] .mcdraft-chart-inspector{background:#fff;color:#26384e;box-shadow:0 11px 35px rgba(21,37,62,.2)}
@media(max-width:620px){.mcdraft-chart-inspector{bottom:max(12px,env(safe-area-inset-bottom));left:12px;right:12px;width:auto;padding:14px}}

/* McDraft Cup: colour tokens work in the existing dark and light themes. */
.cup-hero,.cup-champion{border:1px solid var(--border,#334155);border-radius:16px;padding:25px 23px;margin-bottom:16px;background:linear-gradient(115deg,rgba(223,180,73,.17),rgba(105,148,189,.06));color:var(--text,#e2e8f0)}
.cup-hero>span,.cup-champion>span{font-size:11px;letter-spacing:.16em;font-weight:900;color:#c9922e}
.cup-hero h2{font-size:clamp(23px,4vw,36px);margin:8px 0;color:var(--text,#f1f5f9)}
.cup-hero p,.cup-intro-row p{font-size:13px;line-height:1.65;color:var(--muted,#94a3b8);margin:7px 0}
.cup-champion strong{display:block;font-size:clamp(26px,5vw,42px);margin:9px 0;color:var(--text,#fff)}
.cup-champion small{color:var(--muted,#94a3b8)}
.cup-intro-row{display:flex;flex-wrap:wrap;gap:13px;align-items:center;justify-content:space-between;margin:0 0 15px}
.cup-intro-row>div{max-width:780px}.cup-lock{display:inline-flex;padding:5px 10px;font-size:11px;font-weight:850;color:#b7791f;border:1px solid #ac793b;border-radius:20px;background:rgba(180,133,35,.08)}
.cup-lock.locked{color:#328c68;border-color:#328c68}
.cup-warning{color:#bd8323!important;font-weight:700}
.cup-filter-label{display:flex;flex-direction:column;gap:5px;font-size:11px;font-weight:800;color:var(--text,#e2e8f0)}
.cup-filter-label select{min-width:180px;padding:10px;border-radius:9px;border:1px solid var(--border,#334155);background:var(--card,#172033);color:var(--text,#e2e8f0)}
.cup-bracket{display:grid;grid-template-columns:repeat(4,minmax(215px,1fr));gap:12px;align-items:start;margin-bottom:18px}
.cup-stage{border:1px solid var(--border,#334155);border-radius:13px;background:var(--card,#172033);padding:12px;min-width:0}
.cup-stage-head{min-height:63px;border-bottom:1px solid var(--border,#334155);margin-bottom:12px}
.cup-stage-head h3{font-size:14px;margin:3px 0 5px;color:var(--text,#f8fafc)}
.cup-stage-head span{font-size:10px;font-weight:800;letter-spacing:.045em;color:var(--muted,#94a3b8)}
.cup-stage-ties{display:flex;flex-direction:column;gap:10px}
.cup-tie{border:1px solid var(--border,#334155);border-radius:10px;padding:10px;background:var(--surface,#111827);transition:opacity .2s,border-color .2s}
.cup-tie.cup-dim{opacity:.27}.cup-tie.cup-highlight{border-color:#e2b760;box-shadow:inset 0 0 0 1px rgba(225,183,91,.3)}
.cup-tie-head{display:flex;align-items:center;justify-content:space-between;margin:0 0 10px;gap:5px;font-size:10px;color:var(--muted,#94a3b8)}
.cup-tie-head b{color:#d7a84d}.cup-tie-head span{font-size:10px}
.cup-entrant{display:flex;align-items:center;justify-content:space-between;gap:5px;min-height:40px;border-bottom:1px solid var(--border,#334155)}
.cup-entrant-winner .cup-team-name{color:#369e79}.cup-entrant-winner .cup-aggregate{border:1px solid #359c74;color:#369e79}
.cup-entrant-identity{display:flex;align-items:center;gap:6px;min-width:0}
.cup-team-name{font-size:11px;line-height:1.25;overflow-wrap:anywhere;color:var(--text,#f8fafc)}
.cup-seed{font-size:10px;font-weight:850;color:#e2b760;flex-shrink:0}.cup-placeholder{color:var(--muted,#94a3b8);font-style:italic;font-size:11px}
.cup-aggregate{font-size:16px;font-weight:950;padding:2px 5px;border-radius:6px;color:var(--text,#f8fafc);flex-shrink:0}
.cup-legs{display:grid;gap:5px;padding-top:9px}.cup-leg{display:flex;justify-content:space-between;gap:8px;font-size:10px;color:var(--muted,#94a3b8)}
.cup-leg b{font-variant-numeric:tabular-nums;color:var(--text,#f8fafc)}.cup-decider{display:block;margin-top:8px;color:#b68f4a;font-size:10px;font-weight:700}
.cup-seeding{margin-top:10px}.cup-seed-rank{font-weight:900;color:#ae862f}
.cup-seeding .table-wrap{display:block;max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}
.cup-seeding table{min-width:570px;width:100%;border-collapse:collapse}
.cup-seeding th,.cup-seeding td{padding:9px 10px;white-space:normal;text-align:left}
.cup-seeding th:nth-child(1),.cup-seeding td:nth-child(1){width:42px}
@media(max-width:1140px){.cup-bracket{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:620px){.cup-bracket{grid-template-columns:1fr}.cup-stage{padding:12px}.cup-stage-head{min-height:unset;padding-bottom:11px}.cup-intro-row{align-items:stretch}.cup-filter-label select{width:100%}}
/* Explicit light-mode colour support: legacy tiles can retain dark fallbacks. */
[data-theme="light"] .cup-stage,[data-theme="light"] .cup-seeding{background:#fff;border-color:#d9e2eb;color:#23354b}
[data-theme="light"] .cup-tie{background:#f8fafc;border-color:#dce5ef}
[data-theme="light"] .cup-hero,[data-theme="light"] .cup-champion{background:linear-gradient(120deg,#fff8e4,#f3f7fc);border-color:#e8d8a9}
[data-theme="light"] .cup-hero h2,[data-theme="light"] .cup-champion strong,[data-theme="light"] .cup-team-name,[data-theme="light"] .cup-aggregate,[data-theme="light"] .cup-stage-head h3,[data-theme="light"] .cup-leg b{color:#223249}
[data-theme="light"] .cup-filter-label select{background:#fff;color:#223249;border-color:#cbd5e1}


/* The connected four-stage bracket uses identical 4-row slots in every round. */
.cup-bracket-viewport{overflow-x:auto;max-width:100%;overscroll-behavior-x:contain;-webkit-overflow-scrolling:touch;padding:4px 3px 14px;scrollbar-color:#9c8141 transparent}
.cup-bracket{display:grid;grid-template-columns:repeat(4,minmax(245px,1fr));min-width:1060px;gap:24px;align-items:stretch;margin:0}
.cup-stage{display:flex;flex-direction:column;min-height:780px;overflow:visible;position:relative}
.cup-stage-head{min-height:68px;flex:0 0 auto}
.cup-stage-ties{display:grid;grid-template-rows:repeat(4,minmax(164px,1fr));gap:11px;flex:1;position:relative}
.cup-stage[data-round="prelim"] .cup-tie[data-tie="P2"]{grid-row:1}
.cup-stage[data-round="prelim"] .cup-tie[data-tie="P1"]{grid-row:4}
.cup-stage[data-round="quarter"] .cup-tie[data-tie="QF1"]{grid-row:1}
.cup-stage[data-round="quarter"] .cup-tie[data-tie="QF2"]{grid-row:2}
.cup-stage[data-round="quarter"] .cup-tie[data-tie="QF3"]{grid-row:3}
.cup-stage[data-round="quarter"] .cup-tie[data-tie="QF4"]{grid-row:4}
.cup-stage[data-round="semi"] .cup-tie[data-tie="SF1"]{grid-row:1 / 3;align-self:center}
.cup-stage[data-round="semi"] .cup-tie[data-tie="SF2"]{grid-row:3 / 5;align-self:center}
.cup-stage[data-round="final"] .cup-tie[data-tie="FINAL"]{grid-row:1 / 5;align-self:center}
.cup-tie{cursor:pointer;min-width:0;position:relative;isolation:isolate;width:100%;box-sizing:border-box;align-self:center;box-shadow:0 3px 13px rgba(0,0,0,.065)}
.cup-tie:hover,.cup-tie:focus-visible{outline:2px solid #dcac4c;outline-offset:2px;border-color:#dcac4c}
.cup-tie-more{font-size:10px;font-weight:800;color:var(--accent,#38bdf8);display:block;margin:7px 0 0}
.cup-legs{padding-top:7px;display:grid;gap:5px}
.cup-leg-button{display:flex;justify-content:space-between;align-items:center;gap:9px;padding:6px 5px;min-height:32px;border-radius:7px;border:1px solid var(--border,#334155);background:var(--card,#172033);color:var(--text,#e2e8f0);font:inherit;font-size:10px;cursor:pointer;text-align:left;width:100%;touch-action:manipulation}
.cup-leg-button:hover,.cup-leg-button:focus-visible{border-color:#d6ac57;background:rgba(220,174,72,.10);outline:none}
.cup-leg-button small{font-weight:900;font-size:9px;color:var(--muted,#94a3b8)}
.cup-leg-button.cup-leg-live small{color:#30a97e}
.cup-leg-button b{font-variant-numeric:tabular-nums;font-size:11px}
.cup-tie::after{content:"";position:absolute;left:100%;top:50%;width:25px;border-top:2px solid rgba(201,154,57,.57);pointer-events:none;z-index:-1}
.cup-stage[data-round="final"] .cup-tie::after{display:none}
.cup-stage[data-round="quarter"]::before,.cup-stage[data-round="quarter"]::after,.cup-stage[data-round="semi"]::after{content:"";position:absolute;right:-12px;border-right:2px solid rgba(201,154,57,.37);pointer-events:none}
.cup-stage[data-round="quarter"]::before{top:21%;height:22%}
.cup-stage[data-round="quarter"]::after{top:63%;height:22%}
.cup-stage[data-round="semi"]::after{top:32%;height:42%}
.cup-bracket-hint{font-size:12px;font-weight:650;color:var(--muted,#94a3b8);margin:5px 0 10px}
.cup-hero{display:flex;align-items:center;justify-content:space-between;gap:18px;flex-wrap:wrap}
.cup-hero>div:first-child{max-width:650px}
.cup-countdown{flex:0 0 auto;min-width:180px;display:flex;flex-direction:column;gap:2px;align-items:center;justify-content:center;border:1px solid #c7973d;background:rgba(202,161,69,.13);padding:12px 20px;border-radius:13px;text-align:center}
.cup-countdown strong{font-size:clamp(35px,5vw,55px);font-weight:950;line-height:1;color:#d6a148}
.cup-countdown span{font-weight:900;font-size:12px;color:var(--text,#e2e8f0)}
.cup-countdown small{color:var(--muted,#94a3b8);font-size:11px}
.cup-detail-overlay{position:fixed;inset:0;z-index:10140;background:rgba(4,12,24,.82);display:flex;align-items:center;justify-content:center;padding:12px;box-sizing:border-box}
.cup-detail-overlay[hidden]{display:none}
.cup-detail-dialog{background:var(--card,#172033);color:var(--text,#e2e8f0);border:1px solid var(--border,#334155);border-radius:18px;width:min(960px,100%);max-height:min(90vh,850px);overflow:auto;overscroll-behavior:contain;padding:20px 23px;box-sizing:border-box;box-shadow:0 30px 80px rgba(0,0,0,.38)}
.cup-detail-top{display:flex;justify-content:space-between;gap:10px;align-items:center}
.cup-detail-eyebrow{font-size:10px;letter-spacing:.12em;color:#c39a4e;font-weight:900}
.cup-detail-close{min-width:38px;min-height:38px;font-weight:900;color:var(--text,#fff);background:transparent;border:1px solid var(--border,#334155);border-radius:8px;cursor:pointer}
.cup-detail-dialog h2{font-size:clamp(18px,3.5vw,25px);margin:7px 0 15px}
.cup-detail-leg-tabs{display:flex;gap:8px;flex-wrap:wrap;margin:9px 0 13px}
.cup-detail-leg-tabs button{padding:9px 12px;min-height:40px;border-radius:9px;background:var(--bg-secondary,#142339);border:1px solid var(--border,#334155);color:var(--text,#fff);font:inherit;font-weight:800;font-size:12px;cursor:pointer}
.cup-detail-leg-tabs button[aria-pressed="true"]{border-color:#c9922e;background:rgba(202,161,69,.16)}
.cup-detail-scoreboard{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);align-items:center;gap:10px;padding:13px;border:1px solid var(--border,#334155);border-radius:11px;background:var(--surface,#111827)}
.cup-detail-side{display:flex;flex-direction:column;min-width:0;gap:5px}.cup-detail-side:last-child{text-align:right}
.cup-detail-side b{font-size:clamp(12px,2.4vw,18px);overflow-wrap:anywhere}.cup-detail-side small{font-size:11px;color:var(--muted,#94a3b8)}
.cup-detail-score{white-space:nowrap;font-size:clamp(20px,5vw,33px);font-weight:950;font-variant-numeric:tabular-nums;color:var(--text,#fff)}
.cup-detail-meta{color:var(--muted,#94a3b8);font-size:12px;line-height:1.55;margin:10px 0}
.cup-detail-squads{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:13px 0}
.cup-detail-roster{min-width:0;background:var(--surface,#111827);border:1px solid var(--border,#334155);border-radius:12px;padding:13px}
.cup-detail-roster h3{margin:0 0 11px;font-size:14px;line-height:1.3}
.cup-detail-roster h4{font-size:10px;letter-spacing:.08em;color:var(--muted,#94a3b8);text-transform:uppercase;margin:13px 0 5px}
.cup-detail-player{display:grid;grid-template-columns:35px minmax(0,1fr) auto;gap:7px;align-items:center;border-top:1px solid var(--border,#334155);padding:7px 0;font-size:12px}
.cup-detail-player .cup-position{color:#b18d4b;font-size:10px;font-weight:900}
.cup-detail-player strong{display:block;font-size:12px;overflow-wrap:anywhere}
.cup-detail-player small{font-size:10px;color:var(--muted,#94a3b8);display:block}
.cup-detail-player .cup-player-points{font-weight:950;font-size:15px;font-variant-numeric:tabular-nums}
.cup-detail-note{padding:11px 12px;font-size:11px;border-radius:10px;border:1px solid var(--border,#334155);background:var(--bg-secondary,#172033);color:var(--muted,#94a3b8)}
body.cup-modal-open{overflow:hidden}
[data-theme="light"] .cup-detail-dialog{background:#fff;color:#213147;border-color:#d9e2eb}
[data-theme="light"] .cup-leg-button,[data-theme="light"] .cup-detail-leg-tabs button{background:#fff;color:#223249;border-color:#dce5ef}
[data-theme="light"] .cup-detail-scoreboard,[data-theme="light"] .cup-detail-roster{background:#f5f7fb;color:#23354b}
[data-theme="light"] .cup-countdown span{color:#27364c}
@media(max-width:720px){.cup-bracket{min-width:960px;grid-template-columns:repeat(4,228px);gap:16px}.cup-bracket-viewport{margin-right:-12px}.cup-stage{min-height:775px}.cup-stage-ties{grid-template-rows:repeat(4,minmax(166px,1fr))}.cup-tie::after{width:17px}.cup-stage[data-round="quarter"]::after,.cup-stage[data-round="semi"]::after{right:-8px}.cup-detail-dialog{padding:15px 12px;max-height:95vh}.cup-detail-squads{grid-template-columns:1fr}.cup-hero{align-items:stretch}.cup-countdown{width:100%;box-sizing:border-box}}

'''

cup_css += r'''
/* McDraft Column headlines + a single understated bye/prelim line. */
.mcdraft-column-headline{margin:11px 0 16px;font-size:clamp(21px,3vw,31px);line-height:1.17;
 font-weight:950;letter-spacing:-.025em;color:var(--text,#e2e8f0);overflow-wrap:anywhere}
.season-story .mcdraft-column-headline{font-size:clamp(17px,2.3vw,23px);margin:1px 0 12px}
.storyline-latest .eyebrow + .mcdraft-column-headline{margin-top:11px}
.storyline-latest p + p,.season-story p + p{margin-top:15px}
/* Attach the line to the seventh row rather than adding a fake table row. */
.table-wrap tbody tr.cup-cutline-row > td{border-top:3px solid #c69d4d!important}
[data-theme="light"] .table-wrap tbody tr.cup-cutline-row > td{border-top-color:#a77521!important}

'''

cup_detail_js = r'''

/* Cup match centre: activate a tie or one GW leg with pointer or keyboard. */
const CUP_DETAIL_DATA = __CUP_DETAIL_DATA__;
let cupLastFocus = null;
let cupActiveTie = null;
function cupEscapeHTML(v){return String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function cupNumber(v){return v===null||v===undefined?'—':String(v);}
function cupTieKeydown(event,key){if(event.target.closest('button'))return;if(event.key==='Enter'||event.key===' '){event.preventDefault();openCupTie(key);}}
function cupPlayerRows(players){
    if(!players||!players.length)return '<p class="cup-detail-meta">Lineup not yet captured for this GW.</p>';
    const order={GKP:0,GK:0,DEF:1,MID:2,FWD:3,ATT:3};
    return players.slice().sort((a,b)=>(order[a.position]??4)-(order[b.position]??4)).map(p=>
      '<div class="cup-detail-player"><span class="cup-position">'+cupEscapeHTML(p.position||'–')+'</span>'+
      '<span><strong>'+cupEscapeHTML(p.name||'Unknown')+(p.captain?' ©':'')+'</strong><small>'+cupEscapeHTML(p.club||'')+
      (p.minutes==null?'':' · '+Number(p.minutes)+' min')+'</small></span>'+
      '<span class="cup-player-points">'+cupNumber(p.points)+'</span></div>').join('');
}
function cupRenderDetail(key,gw){
    const tie=CUP_DETAIL_DATA[key];if(!tie)return;
    const leg=tie.legs.find(l=>l.gw===Number(gw))||tie.legs[0];if(!leg)return;
    cupActiveTie=key;
    const teams=tie.teams.map((n,i)=>n||('Winner TBC'));
    const header=document.getElementById('cup-detail-title');
    header.textContent=tie.round+' · '+teams[0]+' v '+teams[1];
    const buttons=tie.legs.map(l=>'<button type="button" aria-pressed="'+(l.gw===leg.gw)+'" onclick="cupRenderDetail('+cupEscapeHTML(JSON.stringify(key))+','+l.gw+')">'+
      'GW'+l.gw+' · '+(tie.legs.length>1?'Leg '+l.number:'The final')+'</button>').join('');
    const score=leg.scores.map(cupNumber);
    const meta=leg.live?'LIVE · provisional player-pick scores':leg.finished?'FULL TIME · completed GW':'SCHEDULED · no score yet';
    const agg= tie.legs.length>1?' · Two-legged tie · '+(tie.aggregate.some(v=>v!==null)?'Current aggregate '+tie.aggregate.map(cupNumber).join('–'):'Aggregate pending'):' · One-leg final';
    const rosters=leg.lineups.map((r,i)=>'<div class="cup-detail-roster"><h3>'+(tie.seeds[i]?'#'+tie.seeds[i]+' ':'')+cupEscapeHTML(r.name||'Awaiting qualifier')+'</h3>'+
        '<h4>Starting XI</h4>'+cupPlayerRows(r.xi)+'<h4>Bench</h4>'+cupPlayerRows(r.bench)+'</div>').join('');
    document.getElementById('cup-detail-body').innerHTML=
       '<div class="cup-detail-leg-tabs" role="group" aria-label="Select cup leg">'+buttons+'</div>'+
       '<div class="cup-detail-scoreboard"><div class="cup-detail-side"><b>'+cupEscapeHTML(teams[0])+'</b><small>'+(tie.seeds[0]?'Seed #'+tie.seeds[0]:'Qualifier TBC')+'</small></div>'+
       '<div class="cup-detail-score">'+score.join(' : ')+'</div>'+
       '<div class="cup-detail-side"><b>'+cupEscapeHTML(teams[1])+'</b><small>'+(tie.seeds[1]?'Seed #'+tie.seeds[1]:'Qualifier TBC')+'</small></div></div>'+
       '<p class="cup-detail-meta">GW'+leg.gw+' · '+meta+agg+(tie.decided?' · '+cupEscapeHTML(tie.winner)+' advance'+(tie.decider?' ('+cupEscapeHTML(tie.decider)+')':''):'')+'</p>'+
       '<div class="cup-detail-squads">'+rosters+'</div>'+
       '<div class="cup-detail-note">Scores use the official Draft GW total once a gameweek finishes, and captured live player points during play. '+
       'Each historical lineup belongs to that specific GW, not the current squad. '+
       'A bench tiebreak applies only if aggregate scores finish level.'+
       '</div>';
}
function openCupTie(key,gw){
    const tie=CUP_DETAIL_DATA[key];if(!tie)return;
    const box=document.getElementById('cup-detail-overlay');if(!box)return;
    if(box.hidden)cupLastFocus=document.activeElement;
    box.hidden=false;document.body.classList.add('cup-modal-open');
    const selected=gw===undefined?(tie.legs.find(l=>l.live)?.gw||tie.legs.filter(l=>l.scores.some(v=>v!==null)).at(-1)?.gw||tie.legs[0].gw):gw;
    cupRenderDetail(key,selected);
    box.querySelector('.cup-detail-close')?.focus();
}
function closeCupTie(){
    const box=document.getElementById('cup-detail-overlay');if(!box)return;
    box.hidden=true;document.body.classList.remove('cup-modal-open');
    if(cupLastFocus&&cupLastFocus.focus)cupLastFocus.focus();
}
document.addEventListener('keydown',event=>{
  const box=document.getElementById('cup-detail-overlay');if(!box||box.hidden)return;
  if(event.key==='Escape'){event.preventDefault();closeCupTie();return;}
  if(event.key==='Tab'){
    const controls=Array.from(box.querySelectorAll('button:not([disabled])'));
    if(!controls.length)return;
    if(event.shiftKey&&document.activeElement===controls[0]){event.preventDefault();controls.at(-1).focus();}
    if(!event.shiftKey&&document.activeElement===controls.at(-1)){event.preventDefault();controls[0].focus();}
  }
});
'''
javascript += "\n" + cup_detail_js


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

/* v57: player rating evolution and FIFA analytics */
.rating-lab-intro{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;border-color:rgba(235,186,103,.45)}
.rating-lab-intro h2{color:#f0cf81}
.rating-lab-stamp{border:1px solid #705e38;background:#322b21;color:#f1d69c;border-radius:8px;padding:8px 11px;font-weight:800;font-size:11px}
.rating-lab-trend-card{border:1px solid rgba(224,186,111,.5)}
.rating-lab-searchbar{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-top:14px}
.rating-lab-searchbar label,.rating-lab-driver-controls label{font-size:11px;font-weight:800;color:#b8cce1}
.rating-lab-searchbar input{flex:1;min-width:165px;max-width:400px;background:#121f32;border:1px solid #435776;color:#f1f4fb;border-radius:8px;padding:10px 12px;font-size:13px}
.rating-lab-searchbar button,.rating-lab-directory-link button{border:1px solid #a68a51;background:#313348;color:#f7dca7;padding:10px 12px;border-radius:8px;font-size:11px;font-weight:800;cursor:pointer}
.rating-lab-searchbar button:hover,.rating-lab-directory-link button:hover{background:#464054}
.rating-lab-suggestions{display:flex;gap:5px;flex-wrap:wrap;margin:11px 0}
.rating-lab-suggestions button{display:flex;gap:8px;align-items:center;background:#172639;border:1px solid #344b62;color:#eaf0fc;border-radius:7px;cursor:pointer;padding:7px 9px;font-size:11px}
.rating-lab-suggestions button small{color:#a7bed2}.rating-lab-suggestions button strong{color:#f4cd77}
.rating-lab-selected{display:flex;gap:8px;flex-wrap:wrap;margin:13px 0;min-height:33px;align-items:center}
.rating-lab-chip{display:flex;align-items:center;gap:9px;color:#f1f4fd;background:#19283a;border:1px solid var(--chip);border-left:5px solid var(--chip);border-radius:9px;padding:8px 11px;font-weight:700;font-size:12px;cursor:pointer}
.rating-lab-chip b{font-size:17px;color:var(--chip)}.rating-lab-chip span{color:#aab4c8}
.rating-lab-trend{width:100%;overflow-x:auto;background:#0c1626;border:1px solid #2d4058;border-radius:12px;padding:10px 6px}
.rating-lab-trend svg{display:block;width:100%;min-width:400px;max-height:375px}
.rating-lab-grid{stroke:#293d53;stroke-width:1;stroke-dasharray:3 5}
.rating-lab-axis{font-size:11px;fill:#aebbd0;font-weight:600}
.rating-lab-legend{display:flex;gap:20px;flex-wrap:wrap;color:#adbed2;font-size:11px;margin-top:10px}
.rating-lab-legend span{display:flex;align-items:center;gap:7px}
.rating-lab-legend i{display:inline-block;width:27px;border-top:3px solid #edbd68}
.rating-lab-legend i.estimated{border-top-style:dashed}
.rating-lab-detailed{margin-top:14px}
.rating-lab-driver-controls{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:10px 0 16px}
.rating-lab-driver-controls select{background:#142339;border:1px solid #47617a;border-radius:8px;color:#ebeff8;padding:8px 10px;max-width:180px}
.rating-lab-driver-summary{display:flex;justify-content:space-between;gap:15px;flex-wrap:wrap;padding:13px;border:1px solid #3a4b60;border-radius:11px;background:#101e2e;margin-bottom:13px}
.rating-lab-driver-summary>div{display:flex;flex-direction:column;gap:3px}
.rating-lab-driver-summary strong{font-size:32px;line-height:1;color:#f1cb7e}
.rating-lab-driver-summary small{font-size:11px;color:#b0c4d6}.rating-lab-driver-summary b{font-size:21px;color:#a5dbf3}
.rating-lab-driver-summary span{font-size:11px;font-weight:800}
.rating-lab-factor{margin:13px 0}.rating-lab-factor>div{display:flex;justify-content:space-between;gap:9px;font-size:12px;margin-bottom:5px}
.rating-lab-factor strong{white-space:nowrap}.rating-lab-factor strong small{font-weight:800;margin-left:4px}
.rating-lab-factor>i{display:block;position:relative;height:11px;border-radius:9px;background:#2d4257;overflow:visible}
.rating-lab-factor>i>em{display:block;height:100%;background:linear-gradient(90deg,#3d9eaf,#efc777);border-radius:9px}
.rating-lab-factor>i>b{position:absolute;top:-2px;bottom:-2px;width:2px;background:#fff;box-shadow:0 0 0 1px #243345}
.rating-lab-caution{font-size:11px;color:#f3cd91;background:#392b20;border:1px solid #685033;padding:9px;border-radius:7px;margin:13px 0 0}
.rating-lab-position-chips{display:flex;gap:7px;flex-wrap:wrap;margin:12px 0}
.rating-lab-position-chips button{border:1px solid #455970;color:#c8d7e7;background:#172739;padding:7px 10px;border-radius:8px;cursor:pointer;font-weight:700;font-size:11px}
.rating-lab-position-chips button.active{border-color:#e3b860;color:#f7d28b;background:#39402e}
.rating-lab-hist-row{display:grid;grid-template-columns:62px 1fr 26px;align-items:center;gap:12px;font-size:12px;margin:15px 0}
.rating-lab-hist-row>i{height:16px;background:#24344a;border-radius:4px;overflow:hidden}
.rating-lab-hist-row>i>em{display:block;height:100%;border-radius:4px}.rating-hist-platinum{background:linear-gradient(90deg,#8ebcc8,#e1fbfd)}.rating-hist-gold{background:linear-gradient(90deg,#a87820,#f3cf68)}.rating-hist-silver{background:linear-gradient(90deg,#748493,#dce4ea)}.rating-hist-bronze{background:linear-gradient(90deg,#7a4528,#d48c58)}
.rating-lab-hist-row strong{text-align:right}.rating-lab-hist-total{margin-top:15px;font-size:11px;color:#aebdd0}
.rating-lab-team-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin-top:15px}
.rating-lab-team{border:1px solid #344758;border-radius:10px;background:linear-gradient(110deg,#182b3e,#101b2b);padding:13px}.rating-lab-team.platinum{border-color:#bde8ee}.rating-lab-team.gold{border-color:#d7a83d}.rating-lab-team.silver{border-color:#9daab6}.rating-lab-team.bronze{border-color:#9b633e}
.rating-lab-team>div:first-child{display:flex;justify-content:space-between;gap:8px;align-items:center;margin-bottom:10px}
.rating-lab-team>div:first-child strong{font-size:12px}.rating-lab-team>div:first-child span{font-size:19px;font-weight:900;color:#f0c872}
.rating-lab-team-units{display:flex;flex-direction:column;gap:7px}
.rating-lab-team-units>div{display:grid;grid-template-columns:34px 1fr 28px;align-items:center;gap:9px}
.rating-lab-team-units small{font-size:10px;font-weight:800;color:#9fb9d0}
.rating-lab-team-units i{height:8px;background:#293e52;border-radius:5px;overflow:hidden}
.rating-lab-team-units em{display:block;height:100%;background:linear-gradient(90deg,#288ebd,#b4bc6a,#efbc67)}
.rating-lab-team-units b{text-align:right;font-size:12px}
.rating-lab-directory-link{margin:7px 0 16px}
@media(max-width:620px){
 .rating-lab-trend-card{padding:12px}.rating-lab-trend svg{min-width:390px}
 .rating-lab-driver-controls{align-items:flex-start}.rating-lab-driver-controls select{max-width:100%}
 .rating-lab-searchbar input{max-width:none;flex-basis:100%}
 .rating-lab-team-grid{grid-template-columns:1fr}
}


/* McDraft Live Centre */
.live-centre-hero{display:flex;align-items:center;justify-content:space-between;gap:20px;overflow:hidden;position:relative;background:linear-gradient(135deg,color-mix(in srgb,var(--card) 82%,#ef4444),var(--card))}
.live-centre-hero h2{margin:6px 0 8px;font-size:clamp(22px,3vw,34px)}.live-centre-hero p{margin:0;max-width:850px;color:var(--muted);line-height:1.55}.live-centre-kicker{font-size:10px;font-weight:900;letter-spacing:.14em;color:#fb7185}.live-centre-pulse{display:flex;align-items:center;gap:8px;border:1px solid rgba(251,113,133,.45);background:rgba(244,63,94,.12);border-radius:999px;padding:9px 13px;font-weight:900;color:#fb7185}.live-centre-pulse i{width:9px;height:9px;border-radius:50%;background:#fb7185;box-shadow:0 0 0 0 rgba(251,113,133,.55);animation:livePulse 1.6s infinite}@keyframes livePulse{70%{box-shadow:0 0 0 9px rgba(251,113,133,0)}100%{box-shadow:0 0 0 0 rgba(251,113,133,0)}}
.live-centre-switcher{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;margin:14px 0 18px;overflow-x:auto;padding-bottom:3px}.live-centre-switch{appearance:none;border:1px solid var(--border);background:var(--card);color:var(--text);border-radius:12px;padding:12px;text-align:left;cursor:pointer;min-width:160px;font:inherit}.live-centre-switch span,.live-centre-switch small{display:block}.live-centre-switch span{font-size:11px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.live-centre-switch b{display:block;font-size:22px;margin:4px 0}.live-centre-switch small{font-size:10px;color:var(--muted)}.live-centre-switch.active{border-color:#fb7185;box-shadow:inset 0 0 0 1px #fb7185;background:color-mix(in srgb,var(--card) 90%,#fb7185)}
.live-centre-match{display:none}.live-centre-match.active{display:block}.live-centre-scoreboard{display:grid;grid-template-columns:minmax(0,1fr) minmax(180px,.65fr) minmax(0,1fr);align-items:center;gap:14px;border:1px solid var(--border);background:var(--card);border-radius:18px;padding:20px;margin-bottom:10px}.live-centre-score-team{display:grid;grid-template-columns:1fr auto;gap:4px 14px;align-items:center}.live-centre-score-team span{font-weight:900;font-size:clamp(14px,2vw,21px)}.live-centre-score-team strong{grid-row:1/3;grid-column:2;font-size:clamp(42px,6vw,70px);line-height:1}.live-centre-score-team small{color:var(--muted)}.live-centre-score-team.away{text-align:right;grid-template-columns:auto 1fr}.live-centre-score-team.away strong{grid-column:1}.live-centre-score-team.away span,.live-centre-score-team.away small{grid-column:2}.live-centre-score-middle{text-align:center;display:flex;flex-direction:column;align-items:center;gap:5px}.live-pill{font-size:10px;font-weight:900;letter-spacing:.12em;color:#fb7185}.live-centre-score-middle small{color:var(--muted);margin-top:3px}.live-centre-score-middle strong{font-size:19px}.live-centre-derby{font-size:12px;color:#fbbf24}
.live-centre-probs{display:grid;grid-template-columns:1fr .45fr 1fr;gap:8px;margin-bottom:12px}.live-centre-probs>div{position:relative;overflow:hidden;border:1px solid var(--border);background:var(--card);border-radius:11px;padding:10px 12px;display:flex;justify-content:space-between;gap:10px}.live-centre-probs>div:before{content:"";position:absolute;inset:auto 0 0;height:3px;width:var(--p);background:#38bdf8}.live-centre-probs .draw:before{background:#fbbf24}.live-centre-probs span{font-size:11px;color:var(--muted)}.live-centre-probs b{font-size:15px}
.live-centre-threat-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px}.live-centre-threat-grid>div{border:1px solid var(--border);border-radius:12px;padding:12px;background:var(--card)}.live-centre-threat-grid h4{margin:0 0 8px;font-size:12px}.live-centre-threat{display:inline-flex;gap:4px;margin:3px 5px 3px 0;padding:5px 7px;border-radius:999px;background:var(--bg-secondary);font-size:10px;color:var(--muted)}.live-centre-threat b{color:var(--text)}.live-centre-no-threat{font-size:11px;color:var(--muted)}
.live-centre-xi-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:18px}.live-centre-team-column{min-width:0}.live-centre-team-head{display:flex;align-items:baseline;gap:8px;margin:0 2px 8px}.live-centre-team-head span{font-size:9px;font-weight:900;color:var(--muted);letter-spacing:.12em}.live-centre-team-head h3{margin:0;flex:1;font-size:17px}.live-centre-team-head small{color:var(--muted);font-weight:800}.live-centre-pitch{min-height:470px;border-radius:18px;padding:18px 9px;display:flex;flex-direction:column;justify-content:space-around;gap:8px;background:linear-gradient(90deg,rgba(16,185,129,.16),rgba(16,185,129,.08)),repeating-linear-gradient(0deg,transparent,transparent 62px,rgba(255,255,255,.05) 63px,rgba(255,255,255,.05) 64px);border:1px solid rgba(52,211,153,.28);box-shadow:inset 0 0 0 2px rgba(255,255,255,.03)}.live-centre-pitch-line{display:flex;justify-content:space-evenly;gap:5px;align-items:center}.live-centre-pitch-player{min-width:65px;max-width:105px;flex:1;text-align:center;background:rgba(7,18,32,.88);border:1px solid rgba(255,255,255,.13);border-radius:9px;padding:7px 4px;box-shadow:0 4px 12px rgba(0,0,0,.18)}.live-centre-pitch-player b,.live-centre-pitch-player span,.live-centre-pitch-player small{display:block}.live-centre-pitch-player b{font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.live-centre-pitch-player span{font-size:14px;font-weight:900;margin:2px 0}.live-centre-pitch-player small{font-size:8px;color:var(--muted);font-weight:900}.live-centre-pitch-player.state-live{border-color:#fb7185}.live-centre-pitch-player.state-upcoming{border-color:#38bdf8}.live-centre-pitch-player.state-finished{opacity:.72}
.live-centre-squad-detail,.live-centre-bench{margin-top:10px;border:1px solid var(--border);background:var(--card);border-radius:13px;padding:11px}.live-centre-squad-detail h4,.live-centre-bench h4{margin:0 0 8px;font-size:11px;color:var(--muted)}.live-centre-player{border-top:1px solid var(--border)}.live-centre-player:first-of-type{border-top:0}.live-centre-player summary{display:grid;grid-template-columns:minmax(0,1fr) auto 42px 30px;gap:8px;align-items:center;padding:8px 2px;cursor:pointer;list-style:none}.live-centre-player summary::-webkit-details-marker{display:none}.live-centre-player-main b,.live-centre-player-main small{display:block}.live-centre-player-main b{font-size:11px}.live-centre-player-main small{font-size:9px;color:var(--muted)}.live-centre-player-state{font-size:8px;font-weight:900;border-radius:999px;padding:4px 6px;background:var(--bg-secondary)}.live-centre-player-state.state-live{color:#fb7185}.live-centre-player-state.state-upcoming{color:#38bdf8}.live-centre-player-state.state-finished{color:var(--muted)}.live-centre-player-mins{font-size:9px;color:var(--muted);text-align:right}.live-centre-player-pts{text-align:right;font-size:15px}.live-centre-player-stats{display:flex;gap:5px;flex-wrap:wrap;padding:0 0 9px}.live-centre-player-stats span{font-size:9px;padding:4px 6px;border-radius:6px;background:var(--bg-secondary);color:var(--muted)}.live-centre-player-stats b{color:var(--text)}
.live-centre-section-head{display:flex;align-items:end;justify-content:space-between;gap:18px;margin-bottom:14px}.live-centre-section-head h2{margin:3px 0 0}.live-centre-section-head p{margin:0;color:var(--muted);font-size:11px;max-width:520px;text-align:right}.live-centre-pl-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.live-centre-pl-fixture{border:1px solid var(--border);border-radius:12px;background:var(--bg-secondary);padding:11px}.live-centre-pl-score{display:grid;grid-template-columns:1fr auto 1fr auto;gap:8px;align-items:center}.live-centre-pl-score span:last-of-type{text-align:right}.live-centre-pl-score strong{font-size:16px}.live-centre-pl-score em{font-size:9px;font-style:normal;font-weight:900;color:#fb7185}.live-centre-pl-assets{display:flex;gap:5px;flex-wrap:wrap;margin-top:8px}.live-centre-pl-player{display:flex;flex-direction:column;background:var(--card);border:1px solid var(--border);border-radius:8px;padding:5px 7px}.live-centre-pl-player b{font-size:9px}.live-centre-pl-player small,.live-centre-pl-none{font-size:8px;color:var(--muted)}
@media(max-width:980px){.live-centre-switcher{grid-template-columns:repeat(5,minmax(155px,1fr))}.live-centre-xi-grid{grid-template-columns:1fr}.live-centre-scoreboard{grid-template-columns:1fr auto 1fr}.live-centre-pl-grid{grid-template-columns:1fr}.live-centre-pitch{min-height:430px}.live-centre-section-head{align-items:flex-start;flex-direction:column}.live-centre-section-head p{text-align:left}}
@media(max-width:620px){.live-centre-hero{align-items:flex-start}.live-centre-pulse{padding:7px 9px}.live-centre-scoreboard{padding:13px 9px;gap:7px}.live-centre-score-team{display:flex;flex-direction:column;gap:3px}.live-centre-score-team.away{display:flex}.live-centre-score-team strong{font-size:38px}.live-centre-score-middle{font-size:9px}.live-centre-score-middle strong{font-size:13px}.live-centre-probs{grid-template-columns:1fr .5fr 1fr}.live-centre-probs>div{padding:8px 6px;display:block;text-align:center}.live-centre-threat-grid{grid-template-columns:1fr}.live-centre-pitch{min-height:390px;padding:11px 5px}.live-centre-pitch-player{min-width:48px;padding:6px 3px}.live-centre-pitch-player b{font-size:9px}.live-centre-pitch-player span{font-size:12px}.live-centre-player summary{grid-template-columns:minmax(0,1fr) auto 34px 26px;gap:5px}.live-centre-pl-score{grid-template-columns:1fr auto 1fr}.live-centre-pl-score em{grid-column:1/-1;text-align:center}}


/* McDraft navigation v1: the original pages and subtab handlers are preserved. */
.mcd-workspace{display:grid;grid-template-columns:254px minmax(0,1fr);max-width:1770px;margin:0 auto;min-width:0;transition:grid-template-columns .2s ease}
.mcd-workspace.mcd-compact{grid-template-columns:66px minmax(0,1fr)}
.mcd-workspace>.main{max-width:none;width:100%;min-width:0;padding:24px clamp(14px,2.5vw,32px)}
.header .nav{display:none!important}
.header{padding-bottom:0!important}
.header-top{padding-bottom:16px!important}
.mcd-sidebar{position:sticky;top:95px;align-self:start;height:calc(100dvh - 108px);min-height:340px;border-right:1px solid var(--border);background:var(--bg-secondary);padding:13px 9px;overflow-y:auto;overflow-x:hidden;scrollbar-width:thin;z-index:55}
.mcd-sidebar-head{display:flex;justify-content:space-between;align-items:center;gap:9px;padding:6px 9px 15px;border-bottom:1px solid var(--border);margin-bottom:10px}
.mcd-sidebar-head strong{font-size:11px;letter-spacing:.11em;color:var(--muted);text-transform:uppercase}
.mcd-sidebar-collapse{appearance:none;display:grid;place-items:center;min-width:34px;min-height:34px;border-radius:9px;border:1px solid var(--border);background:var(--card);color:var(--text);cursor:pointer;font-size:17px}
.mcd-nav-section{border-radius:10px;margin:3px 0;overflow:hidden}
.mcd-nav-section>summary{display:flex;align-items:center;gap:11px;min-height:43px;cursor:pointer;color:var(--text);font-weight:760;padding:10px 11px;list-style:none;border-radius:9px;user-select:none}
.mcd-nav-section>summary::-webkit-details-marker{display:none}
.mcd-nav-section>summary:hover,.mcd-nav-section[open]>summary{background:var(--card-hover)}
.mcd-nav-section.is-current>summary{color:var(--accent)}
.mcd-nav-icon{display:inline-grid;place-items:center;width:22px;min-width:22px;font-size:19px;line-height:1;font-weight:900;color:var(--muted)}
.mcd-nav-section.is-current .mcd-nav-icon{color:var(--accent)}
.mcd-nav-label{font-size:13px;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mcd-nav-chevron{font-size:13px;color:var(--muted);transition:transform .2s ease}
.mcd-nav-section[open] .mcd-nav-chevron{transform:rotate(90deg)}
.mcd-nav-children{display:grid;gap:2px;padding:3px 0 10px 34px}
.mcd-nav-link{appearance:none;border:0;display:block;width:100%;text-align:left;background:transparent;color:var(--muted);border-radius:8px;padding:10px 8px;min-height:38px;font:600 12px/1.25 inherit;font-family:inherit;cursor:pointer;transition:background .15s ease,color .15s ease}
.mcd-nav-link:hover{background:var(--card-hover);color:var(--text)}
.mcd-nav-link.is-active{background:color-mix(in srgb,var(--accent) 14%,var(--card));color:var(--accent);font-weight:800;box-shadow:inset 3px 0 0 var(--accent)}
.mcd-sidebar button:focus-visible,.mcd-sidebar summary:focus-visible,.mcd-mobile-bottom button:focus-visible,.mcd-mobile-sheet button:focus-visible,.mcd-mobile-current button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.mcd-workspace.mcd-compact .mcd-sidebar{padding:13px 5px;overflow-x:visible}
.mcd-workspace.mcd-compact .mcd-sidebar-head{padding:5px 6px 14px}
.mcd-workspace.mcd-compact .mcd-sidebar-head strong,.mcd-workspace.mcd-compact .mcd-nav-label,.mcd-workspace.mcd-compact .mcd-nav-chevron,.mcd-workspace.mcd-compact .mcd-nav-children{display:none}
.mcd-workspace.mcd-compact .mcd-sidebar-collapse{min-width:37px}
.mcd-workspace.mcd-compact .mcd-nav-section>summary{justify-content:center;padding:10px 4px}
.mcd-workspace.mcd-compact .mcd-nav-icon{font-size:20px}
.mcd-mobile-bottom,.mcd-mobile-current,.mcd-mobile-sheet{display:none}
.mcd-analytics-directory{padding:18px;border:1px solid var(--border);border-radius:14px;background:var(--card);margin:0 0 22px}
.mcd-analytics-directory h3{font-size:18px;color:var(--text);margin:0 0 6px}
.mcd-analytics-directory>p{color:var(--muted);font-size:13px;margin:0 0 15px}
.mcd-analytics-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,198px),1fr));gap:10px}
.mcd-analytics-quick{display:block;text-align:left;border-radius:11px;border:1px solid var(--border);background:var(--bg-secondary);padding:14px;color:var(--text);cursor:pointer;font:inherit;min-width:0}
.mcd-analytics-quick:hover{border-color:var(--accent);background:var(--card-hover)}
.mcd-analytics-quick strong{display:block;font-size:13px;color:var(--text);margin-bottom:5px}
.mcd-analytics-quick small{font-size:11px;color:var(--muted);line-height:1.45;display:block}
body[data-theme=light] .mcd-sidebar,body[data-theme=light] .mcd-mobile-sheet{background:#fff;color:#172033}
body[data-theme=light] .mcd-nav-link.is-active{background:#e6f3fd;color:#0369a1}
@media(max-width:850px){
 .mcd-workspace,.mcd-workspace.mcd-compact{display:block}
 .mcd-sidebar{display:none!important}
 .mcd-workspace>.main{padding:14px 12px calc(100px + env(safe-area-inset-bottom))!important;max-width:100%;overflow-x:hidden}
 .mcd-mobile-current{display:flex;align-items:center;justify-content:space-between;gap:9px;margin:0 0 15px;padding:10px 12px;background:var(--card);border:1px solid var(--border);border-radius:12px;color:var(--text);font-size:12px}
 .mcd-mobile-current span{color:var(--muted)}
 .mcd-mobile-current strong{color:var(--text);font-size:13px}
 .mcd-mobile-current button{border:1px solid var(--border);border-radius:9px;background:var(--bg-secondary);color:var(--text);font:700 12px inherit;font-family:inherit;padding:9px;cursor:pointer;min-height:38px}
 .mcd-mobile-bottom{position:fixed;inset:auto 0 0;z-index:130;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));align-items:stretch;min-height:65px;padding:5px 3px calc(5px + env(safe-area-inset-bottom));border-top:1px solid var(--border);background:var(--card);box-shadow:0 -4px 20px rgba(0,0,0,.12)}
 .mcd-mobile-bottom button{appearance:none;border:0;border-radius:11px;background:transparent;color:var(--muted);font:700 10px/1.25 inherit;font-family:inherit;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;min-width:0;padding:6px 2px;cursor:pointer}
 .mcd-mobile-bottom button.is-current{background:var(--card-hover);color:var(--accent)}
 .mcd-mobile-bottom .mcd-nav-icon{font-size:23px;min-height:25px;color:inherit}
 .mcd-mobile-sheet:not([hidden]){display:flex;position:fixed;inset:0;z-index:180;align-items:flex-end;justify-content:center;background:rgba(4,12,28,.55);backdrop-filter:blur(2px)}
 .mcd-mobile-sheet-panel{width:100%;max-width:650px;max-height:min(82dvh,760px);display:flex;flex-direction:column;border-radius:20px 20px 0 0;background:var(--card);color:var(--text);border:1px solid var(--border);border-bottom:none;box-shadow:0 -18px 55px rgba(0,0,0,.3);padding-bottom:env(safe-area-inset-bottom)}
 .mcd-mobile-sheet-head{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:18px;border-bottom:1px solid var(--border)}
 .mcd-mobile-sheet-head h2{font-size:19px;margin:0;color:var(--text)}
 .mcd-mobile-sheet-head button{display:grid;place-items:center;background:var(--bg-secondary);border:1px solid var(--border);color:var(--text);border-radius:10px;font-size:20px;min-width:38px;min-height:38px;cursor:pointer}
 .mcd-mobile-sheet-content{overflow-y:auto;padding:12px 17px 22px;overscroll-behavior:contain}
 .mcd-mobile-sheet-group{margin:8px 0 20px}
 .mcd-mobile-sheet-group h3{font-size:13px;color:var(--muted);letter-spacing:.05em;text-transform:uppercase;margin:7px 0 10px}
 .mcd-mobile-sheet-links{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
 .mcd-mobile-sheet-links button{font:700 12px/1.3 inherit;font-family:inherit;text-align:left;min-height:46px;padding:10px 12px;border:1px solid var(--border);background:var(--bg-secondary);color:var(--text);border-radius:10px;cursor:pointer}
 .mcd-mobile-sheet-links button.is-active{color:var(--accent);border-color:var(--accent);background:var(--card-hover)}
 .mcd-mobile-sheet[hidden]{display:none!important}
 body.mcd-mobile-sheet-open{overflow:hidden}
 .header{padding:10px 12px 0!important;position:relative}
 .header-top{padding-bottom:8px!important}
 .mcd-analytics-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media(max-width:410px){.mcd-mobile-sheet-links{grid-template-columns:1fr 1fr}.mcd-analytics-grid{grid-template-columns:1fr 1fr}.mcd-analytics-quick{padding:10px}}
@media(min-width:851px){.mcd-mobile-bottom,.mcd-mobile-current,.mcd-mobile-sheet{display:none!important}}
@media(prefers-reduced-motion:reduce){.mcd-workspace{transition:none}}

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

            <div class="theme-control" aria-label="Dashboard colour theme">
                <button id="theme-toggle" class="theme-toggle" type="button" onclick="toggleDashboardTheme()" aria-pressed="false" title="Switch to light mode">
                    <span class="theme-toggle-icon" aria-hidden="true">☀</span>
                    <span class="theme-toggle-label">Light</span>
                </button>
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
                data-page="war-room"
                onclick="showPage('war-room')"
            >
                War Room
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
            <button class="nav-button" data-page="clubs" onclick="showPage('clubs')">Clubs</button>


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

            <button class="nav-button" data-page="mcdraft-cup" onclick="showPage('mcdraft-cup')">McDraft Cup</button>

            <button
                class="nav-button"
                data-page="season-simulator"
                onclick="showPage('season-simulator')"
            >
                Season Simulator
            </button>

        </nav>

    </header>


<div class="mcd-workspace" id="mcd-workspace">
    <aside class="mcd-sidebar" id="mcd-sidebar" aria-label="Main navigation">
      <div class="mcd-sidebar-head"><strong>Explore McDraft</strong><button id="mcd-sidebar-collapse" class="mcd-sidebar-collapse" type="button" title="Collapse sidebar" aria-label="Collapse sidebar" aria-expanded="true">«</button></div>
      <nav id="mcd-sidebar-sections" aria-label="Dashboard sections"></nav>
    </aside>
    <main class="main">
<div class="mcd-mobile-current" id="mcd-mobile-current"><span>YOU ARE HERE · <strong id="mcd-mobile-location">Home</strong></span><button type="button" id="mcd-current-browse" aria-haspopup="dialog">Browse section ▾</button></div>



        <!-- ==================================================
             OVERVIEW
             ================================================== -->

        <section class="page active" id="page-overview">
            <div class="page-heading"><h1>League Overview</h1><p>Standings and fixtures, or the full McDraft numbers behind them.</p></div>
            <div class="analytics-subtabs overview-tabs" role="tablist" aria-label="Overview sections">
                <button type="button" class="analytics-subtab overview-tab active" onclick="showOverviewSubtab('standings',this)" aria-selected="true">McDraft Tables & Fixtures</button>
                <button type="button" class="analytics-subtab overview-tab" onclick="showOverviewSubtab('intelligence',this)" aria-selected="false">Predictions & Analytics</button>
            </div>
            <div class="overview-subpage active" id="overview-sub-standings">
                <div class="card"><h2>McDraft League Table</h2>__STANDINGS_TABLE__</div>
                <div class="card storyline-card"><h2>__HOME_GAME_STATE_TITLE__</h2>__HOME_GAME_STATE_PANEL__</div>
                <div class="card"><h2>Upcoming McDraft Fixtures</h2><p class="card-description">Fixtures only — predictions and difficulty live in the Fixtures tab.</p>__OVERVIEW_UPCOMING_FIXTURES__</div>
                <div class="card"><h2>Premier League Table</h2><p class="card-description">Real PL standings, total FPL points generated by each club, and its evolving fantasy-strength score.</p>__PREMIER_LEAGUE_TABLE__</div>
            </div>
            <div class="overview-subpage" id="overview-sub-intelligence">
                <div class="dashboard-grid"><div class="card"><h2>Power Rankings</h2>__POWER_RANKINGS_TABLE__</div>
                <div class="card"><h2>Luck Index</h2>__LUCK_INDEX_TABLE__</div></div>
                <div class="card"><h2>Rest-of-Season Prediction</h2><p class="card-description">Fixture-aware Monte Carlo forecast based on evolving PL club strength and the remaining real PL schedule.</p>__SEASON_PREDICTION_TABLE__</div>
                <div class="card"><h2>Finish Probability Matrix</h2>__POSITION_PROBABILITY_TABLE__</div>
                <div class="card"><h2>Squad Pedigree</h2>__SQUAD_PEDIGREE_TABLE__</div>
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

            </div>
        </section>


        __LIVE_CENTRE_PAGE__


        <!-- ==================================================
             MANAGER WAR ROOM
             ================================================== -->
        <section class="page" id="page-war-room">
            <div class="page-heading"><h1>Manager War Room</h1><p>Next-opponent preparation, projected formations, player risk and matchup-specific decisions.</p></div>
            __MANAGER_WAR_ROOM_HTML__
        </section>


        <!-- ==================================================
             MY TEAM
             ================================================== -->

        <section class="page" id="page-myteam">
            <div class="page-heading"><h1>My Team</h1><p>Your squad, targets, decisions and season trends.</p></div>

            <div class="card">
                <div class="my-team-selector-row">
                    <div><h2>My Team</h2><p class="card-description">Choose your team, then move between squad, targets and stats without losing the selection.</p></div>
                    <label class="my-team-select-wrap" for="my-team-select"><span>Selected team</span><select id="my-team-select" onchange="changeMyTeam()">__MY_TEAM_OPTIONS__</select></label>
                </div>
                <div id="my-team-cards">__MY_TEAM_CARDS__</div>
            </div>

            <div class="card"><h2>Squad Performance Radar</h2><p class="card-description">Live squad profile, benchmarked within each player's Premier League position.</p><div id="myteam-radar"></div></div>
            <div class="card" id="myteam-vulnerability-card"><h2>Squad Vulnerability Radar</h2><p class="card-description">Where could your current squad come unstuck? Six exposure scores from the real squad, next-GW projections and upcoming PL schedule. Tap a point or metric to see why.</p><div id="myteam-vulnerability"></div></div>

            <div class="analytics-subtabs myteam-tabs" role="tablist" aria-label="My Team sections">
                <button type="button" class="analytics-subtab myteam-tab active" onclick="showMyTeamSubtab('squad',this)">Squad</button>
                <button type="button" class="analytics-subtab myteam-tab" onclick="showMyTeamSubtab('planner',this)">Five-GW Planner</button>
                <button type="button" class="analytics-subtab myteam-tab" onclick="showMyTeamSubtab('medical',this)">Medical Room</button>
                <button type="button" class="analytics-subtab myteam-tab" onclick="showMyTeamSubtab('targets',this)">Targets</button>
                <button type="button" class="analytics-subtab myteam-tab" onclick="showMyTeamSubtab('scout',this)">Player Scout</button>
                <button type="button" class="analytics-subtab myteam-tab" onclick="showMyTeamSubtab('stats',this)">Stats</button>
            </div>

            <div class="myteam-subpage active" id="myteam-sub-squad">
                <div class="card">
                    <h2>Squad By Gameweek</h2>
                    <p class="card-description">Your starting XI and bench for every captured gameweek — flip back through the season to see who you picked.</p>
                    <div id="myteam-squad-wrap"></div>
                    <div class="results-navigation">
                        <button class="results-button" id="myteam-squad-prev" onclick="changeMyTeamSquadGw(-1)">← Previous</button>
                        <div class="results-gw-display" id="myteam-squad-gw-display">—</div>
                        <button class="results-button" id="myteam-squad-next" onclick="changeMyTeamSquadGw(1)">Next →</button>
                    </div>
                </div>
            </div>

            <div class="myteam-subpage" id="myteam-sub-planner">
                <div class="card"><h2>Five-GW Squad Planner</h2><p class="card-description">Projected optimal starting XIs from your current squad using the real PL schedule, with each week's McDraft opponent, bench cover, blank/double warnings and suggested waiver upgrades. Projections are estimates, not guaranteed returns.</p>
                    <div id="myteam-planner-summary"></div>
                    <div id="myteam-planner-chart" class="planner-chart" aria-label="Projected starting eleven points for each of the next five gameweeks"></div>
                    <div id="myteam-planner-weeks"></div>
                </div>
                <div class="card"><h2>Five-GW Free-Agent Upgrades</h2><p class="card-description">Best like-for-like free-agent swaps by improvement to your projected starting XI over all five weeks. They do not account for waiver priority or ownership changes after this refresh.</p><div id="myteam-planner-upgrades"></div></div>
            </div>
            <div class="myteam-subpage" id="myteam-sub-medical">
                <div class="card"><h2>Squad Medical Room</h2><p class="card-description">Official FPL flags for your current squad, next-GW playing estimates and upcoming fixture risk. The planner already adjusts point projections for these risks.</p><div id="myteam-medical-results"></div></div>
            </div>
            <div class="myteam-subpage" id="myteam-sub-targets">
                <div class="dashboard-grid">
                    <div class="card full"><h2>Positional Need</h2><p class="card-description">How urgently this squad needs help at each position, graded against the other McDraft teams. This directly influences trade-target ranking.</p><div id="myteam-position-needs"></div></div>
                    <div class="card"><h2>Free Agents Who Could Improve You</h2><p class="card-description">Like-for-like recommendations from the current free-agent pool, ranked using player value, form, fixture run and positional need.</p><div id="myteam-free-agents"></div></div>
                    <div class="card full"><h2>Realistic Transfer Targets</h2><p class="card-description">Owned players who fit your weak slots and are plausible trade targets, with fixture and club-strength context included.</p><div id="myteam-trade-targets"></div></div>
                    <div class="card full"><h2>Sell High / Move-On Candidates</h2><p class="card-description">Assets whose fixture-adjusted output is running hot, whose fixtures worsen, or whose position is already a strength.</p><div id="myteam-sell-high"></div></div>
                </div>
            </div>

            <div class="myteam-subpage" id="myteam-sub-scout">
                <div class="card"><h2>Player Scout · Squad Suitability</h2>
                    <p class="card-description">Search the entire FPL player pool. Scores account for your positional needs, projection, club exposure, future fixtures and whether you can realistically obtain the player. For owned players, draft an offer in Trade Lab with the target preselected.</p>
                    <div class="player-filter-grid">
                        <input type="search" id="scout-player-search" class="player-search-box" placeholder="Search any player…" oninput="renderPlayerScout()" />
                        <select id="scout-position" class="player-filter" onchange="renderPlayerScout()"><option value="">All positions</option><option value="GKP">GK</option><option value="DEF">DEF</option><option value="MID">MID</option><option value="FWD">FWD</option></select>
                        <select id="scout-ownership" class="player-filter" onchange="renderPlayerScout()"><option value="">Owned &amp; free agents</option><option value="owned">Owned players</option><option value="free">Free agents</option></select>
                        <select id="scout-sort" class="player-filter" onchange="renderPlayerScout()"><option value="fit">Best squad fit</option><option value="value">Player value</option><option value="projection">Next 3 GW projection</option><option value="points">Season points</option></select>
                    </div>
                    <div id="scout-count" class="card-description"></div><div id="myteam-scout-results" class="trade-target-list"></div>
                </div>
            </div>
            <div class="myteam-subpage" id="myteam-sub-stats">
                <div class="dashboard-grid">
                    <div class="card"><h2>Head-to-Head Record</h2><div id="myteam-h2h-record"></div></div>
                    <div class="card trend-chart-card"><h2>Score By Gameweek</h2><div class="trend-chart-svg-wrap" id="myteam-chart-scores"></div></div>
                    <div class="card trend-chart-card"><h2>League Position By Gameweek</h2><div class="trend-chart-svg-wrap" id="myteam-chart-rank"></div></div>
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

            <div class="card">
                <h2>Premier League Fixtures</h2>
                <p class="card-description">Browse the real PL schedule by FPL gameweek, including completed results and future fixtures.</p>
                <div class="results-gw-display" id="pl-fixture-gw-display">—</div>
                <div id="pl-fixture-browser"></div>
                <p class="card-description" style="margin-top:10px;">Synced to the main Gameweek selector below — changing GW updates McDraft results, summary, Team of the Week and these Premier League fixtures together.</p>
            </div>

            <!-- PROJECTED FIXTURE ODDS -->

            <div class="card" id="fixture-odds-card" style="display:none;">
                <div id="upcoming-fixture-odds">
                    <h2>Projected Fixture Odds · Fractional</h2>
                    __PROJECTED_FIXTURE_ODDS__
                </div>
                <div id="live-fixture-odds" style="display:none;">
                    <h2>Live Fixture Odds · Fractional</h2>
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
            <div class="analytics-subtabs season-summary-tabs" role="tablist" aria-label="Season Summary sections">
                <button type="button" class="analytics-subtab season-summary-tab active" aria-selected="true" onclick="showSeasonSummarySubtab('evolution',this)">Season Evolution</button>
                <button type="button" class="analytics-subtab season-summary-tab" aria-selected="false" onclick="showSeasonSummarySubtab('diary',this)">Diary</button>
                <button type="button" class="analytics-subtab season-summary-tab" aria-selected="false" onclick="showSeasonSummarySubtab('milestones',this)">Milestones</button>
                <button type="button" class="analytics-subtab season-summary-tab" aria-selected="false" onclick="showSeasonSummarySubtab('records',this)">Records</button>
                <button type="button" class="analytics-subtab season-summary-tab" aria-selected="false" onclick="showSeasonSummarySubtab('share',this)">Share Cards</button>
            </div>
            <div class="season-summary-subpage active" id="season-summary-sub-evolution"><div class="card">__SEASON_TIMELINE_EXPLORER__</div></div>
            <div class="season-summary-subpage" id="season-summary-sub-diary">
                <div class="card"><h2>Manager of the Month</h2><p class="card-description">Calendar-month honours based on H2H league points, with points scored and wins as tiebreakers.</p><div class="motm-grid">__MANAGERS_OF_MONTH__</div></div>
                <div class="card"><h2>Season Diary</h2><p class="card-description">The week-by-week story: results, table movement, rivalries, trades, player performances, luck and upcoming fixtures.</p><div class="season-summary-list">__SEASON_SUMMARY__</div></div>
            </div>
            <div class="season-summary-subpage" id="season-summary-sub-milestones">
                <div class="card"><h2>Milestones</h2><p class="card-description">League achievements and, from GW20, Cup debuts, upsets, knockout progression and the eventual champion. Newest first.</p><div class="milestone-list">__SEASON_MILESTONES__</div></div>
            </div>
            <div class="season-summary-subpage" id="season-summary-sub-records">
                <div class="card"><h2>League &amp; Cup Records</h2><p class="card-description">League records plus Cup leg scores, aggregate margins, upsets and the GW26 final as they happen.</p><div class="records-grid">__LEAGUE_RECORDS__</div></div>
                <div class="card"><h2>Record Chase</h2><p class="card-description">Who is closest to the live McDraft records for scoring, winning streaks and roster activity?</p><div class="record-chase-list">__RECORD_CHASE__</div></div>
            </div>
            <div class="season-summary-subpage" id="season-summary-sub-share">
                <div class="card"><h2>Share Cards</h2><p class="card-description">Season talking points built for the group chat. Share on supported devices, or copy the text.</p><div class="share-card-grid">__SHARE_CARDS__</div></div>
            </div>
        </section>


        <!-- ==================================================
             FIXTURES
             ================================================== -->
        <section class="page" id="page-fixtures">
            <div class="page-heading"><h1>Fixtures</h1><p>Hardest and kindest upcoming runs, then the next five McDraft fixtures in one compact matrix.</p></div>
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
                <h1>Players</h1>
                <p>Season leaders, form, fixture-aware player intelligence and the full player pool.</p>
            </div>

            <div class="analytics-subtabs player-page-tabs" role="tablist" aria-label="Player sections">
                <button type="button" class="analytics-subtab player-page-tab active" onclick="showPlayerSubtab('leaders',this)">Leaders &amp; Form</button>
                <button type="button" class="analytics-subtab player-page-tab" onclick="showPlayerSubtab('directory',this)">Player Directory</button>
                <button type="button" class="analytics-subtab player-page-tab" onclick="showPlayerSubtab('injuries',this)">Injuries &amp; Suspensions</button>
                <button type="button" class="analytics-subtab player-page-tab" onclick="showPlayerSubtab('availability',this)">Availability &amp; Departures</button>
            </div>

            <div class="player-subpage active" id="player-sub-leaders">
                <div class="card"><h2>Top Players</h2><div class="top-player-grid">__TOP_PLAYER_CARDS__</div></div>
                <div class="card"><h2>Top Players By Season Points</h2>__TOP_PLAYERS_TABLE__</div>
                <div class="card"><h2>Player Form</h2>__FORM_TABLE__</div>
            </div>

            <div class="player-subpage" id="player-sub-directory">
                <div class="card">
                    <div class="player-directory-heading">
                        <div><h2>Player Directory</h2><p class="card-description">Live /100 ratings across the full player pool (Bronze <70 · Silver 70–79 · Gold 80–89 · Platinum 90+). Filter by position, Premier League club or your draft fantasy team, then open Details for the seven-factor breakdown.</p></div>
                        <div class="player-directory-count" id="player-directory-count"></div>
                    </div>
                    <div class="player-filter-grid">
                        <input type="text" id="player-search" class="player-search-box" placeholder="Search player..." oninput="filterPlayers()" />
                        <select id="player-position-filter" class="player-filter" onchange="filterPlayers()"><option value="">All positions</option><option value="GKP">Goalkeepers</option><option value="DEF">Defenders</option><option value="MID">Midfielders</option><option value="FWD">Forwards</option></select>
                        <select id="player-club-filter" class="player-filter" onchange="filterPlayers()"><option value="">All clubs</option>__PLAYER_CLUB_OPTIONS__</select>
                        <select id="player-fantasy-filter" class="player-filter" onchange="filterPlayers()"><option value="">All fantasy teams</option><option value="Free Agent">Free Agents</option>__PLAYER_FANTASY_OPTIONS__</select>
                        <select id="player-sort" class="player-filter" onchange="filterPlayers()"><option value="rating" selected>Rating /100</option><option value="points">Season points</option><option value="form">5 GW form</option><option value="goals">Goals</option><option value="assists">Assists</option><option value="name">Name</option></select>
                    </div>
                    <div id="player-search-results" class="player-search-results player-directory-results" style="display:block;"></div>
                </div>
            </div>
            <div class="player-subpage" id="player-sub-injuries">
              <div class="card"><h2>Injuries &amp; Suspensions</h2><p class="card-description">Latest official FPL status and reported playing probability. News may be unconfirmed; future-week recovery is modelled, not guaranteed.</p>
                <div class="player-filter-grid">
                  <input id="injury-search" type="search" class="player-search-box" placeholder="Search player or club…" oninput="renderInjuryList()" />
                  <select id="injury-status-filter" class="player-filter" onchange="renderInjuryList()"><option value="">All flagged players</option><option value="i">Injured</option><option value="s">Suspended</option><option value="d">Doubtful</option><option value="u">Unavailable</option><option value="n">Not eligible</option><option value="a">Available with news</option></select>
                  <select id="injury-ownership-filter" class="player-filter" onchange="renderInjuryList()"><option value="">All ownership</option><option value="Free Agent">Free agents</option><option value="Owned">McDraft owned</option></select>
                </div>
                <div id="injury-count" class="player-directory-count"></div>
                <div id="injury-list-results"></div>
              </div>
            </div>
    <div class="player-subpage" id="player-sub-availability"><div class="card">
      <h2>Availability &amp; departures · club vs fantasy team</h2>
      <p class="card-description">Side-by-side Premier League club and McDraft fantasy-team analytics, sourced from official FPL status flags. Click any bar to inspect its players. Removals mean absent from the current FPL player pool; they do not prove a transfer out of the Premier League.</p>
      <div class="health-metric-switch" role="group" aria-label="Availability metric">
        <button type="button" class="health-metric-btn active" data-health-view="flags" aria-pressed="true" onclick="healthSetView('flags')">Current flags</button>
        <button type="button" class="health-metric-btn" data-health-view="risk" aria-pressed="false" onclick="healthSetView('risk')">GW points at risk</button>
        <button type="button" class="health-metric-btn" data-health-view="new" aria-pressed="false" onclick="healthSetView('new')">New / updated reports</button>
        <button type="button" class="health-metric-btn" data-health-view="removed" aria-pressed="false" onclick="healthSetView('removed')">Departures / removals</button>
      </div>
      <div class="player-filter-grid health-filters">
        <select id="health-club-filter" class="player-filter" onchange="healthFiltersChanged()" aria-label="Filter Premier League club"><option value="">All Premier League clubs</option>__HEALTH_CLUB_OPTIONS__</select>
        <select id="health-owner" class="player-filter" onchange="healthFiltersChanged()" aria-label="Filter McDraft fantasy team"><option value="">All fantasy teams</option><option value="Free Agent">Free agents</option>__HEALTH_OWNER_OPTIONS__</select>
        <select id="health-status-filter" class="player-filter" onchange="healthFiltersChanged()" aria-label="Filter injury or suspension status"><option value="">All official statuses</option><option value="i">Injured</option><option value="s">Suspended</option><option value="d">Doubtful</option><option value="u">Unavailable</option><option value="n">Not eligible</option><option value="a">Available with news</option></select>
        <input id="health-query" class="player-search-box" type="search" placeholder="Search player, PL club or fantasy team…" aria-label="Search availability data" oninput="healthFiltersChanged()">
      </div>
      <label class="health-free-agent-toggle"><input type="checkbox" id="health-free-agent-chart" onchange="healthFiltersChanged()"> Include free agents in fantasy-team chart</label>
      <div id="analytics-health-root" aria-live="polite"></div>
    </div></div>

        </section>


        <!-- ==================================================
             PREMIER LEAGUE CLUB EXPLORER
             ================================================== -->
        <section class="page" id="page-clubs">
            <div class="page-heading"><h1>Premier League Clubs</h1><p>All 20 clubs: club FPL production, squad assets, free agents, and the actual fixture schedule.</p></div>
            <div class="card">
                <div class="my-team-selector-row"><div><h2>Club Explorer</h2><p class="card-description">Select any club. Scores include every PL player, not only players owned in McDraft.</p></div>
                    <label class="my-team-select-wrap" for="club-explorer-select"><span>Premier League club</span><select id="club-explorer-select" onchange="renderClubExplorer()"></select></label>
                </div>
                <div id="club-explorer-summary" class="club-explorer-summary"></div>
            </div>
            <div class="analytics-subtabs club-explorer-tabs" role="tablist" aria-label="Club Explorer sections">
                <button type="button" class="analytics-subtab club-explorer-tab active" onclick="showClubSubtab('overview',this)">Overview</button>
                <button type="button" class="analytics-subtab club-explorer-tab" onclick="showClubSubtab('gameweeks',this)">Points by GW</button>
                <button type="button" class="analytics-subtab club-explorer-tab" onclick="showClubSubtab('players',this)">Top Players</button>
                <button type="button" class="analytics-subtab club-explorer-tab" onclick="showClubSubtab('agents',this)">Free Agents</button>
                <button type="button" class="analytics-subtab club-explorer-tab" onclick="showClubSubtab('fixtures',this)">Fixtures</button>
            </div>
            <div class="club-explorer-panel active" id="club-sub-overview"><div class="dashboard-grid"><div class="card full"><h2>Club Output & Draft Pedigree</h2><div id="club-overview-content"></div></div><div class="card full"><h2>Five-Gameweek Outlook</h2><div id="club-overview-fixtures"></div></div></div></div>
            <div class="club-explorer-panel" id="club-sub-gameweeks"><div class="card"><h2>FPL Points by Gameweek</h2><p class="card-description">All club players' official FPL points, regardless of McDraft ownership or team selection.</p><div id="club-gw-chart"></div><div id="club-gw-table" class="table-wrap"></div></div></div>
            <div class="club-explorer-panel" id="club-sub-players"><div class="card"><h2>Top Club Assets</h2><div id="club-top-players"></div></div></div>
            <div class="club-explorer-panel" id="club-sub-agents"><div class="card"><h2>Available Free Agents</h2><div id="club-free-agents"></div></div></div>
            <div class="club-explorer-panel" id="club-sub-fixtures"><div class="card"><h2>Real Premier League Fixtures</h2><p class="card-description">Past results and future fixtures, with venue and changing difficulty.</p><div id="club-all-fixtures"></div></div></div>
        </section>

        <!-- ==================================================
             TRANSFERS
             ================================================== -->
        <section class="page" id="page-transfers">
            <div class="page-heading"><h1>Transfers</h1><p>Waivers, free-agent churn, negotiated deals and a mildly dangerous trade laboratory.</p></div>
            <div class="transfer-subtabs" role="tablist" aria-label="Transfer sections"><button class="transfer-subtab active" type="button" onclick="showTransferSubtab('waivers', this)">Waivers</button><button class="transfer-subtab" type="button" onclick="showTransferSubtab('trades', this)">Trades</button><button class="transfer-subtab" type="button" onclick="showTransferSubtab('intelligence', this)">Waiver Intelligence</button></div>
            <div class="transfer-subpanel active" id="transfer-subpanel-waivers">
              <div class="card"><h2>Latest Waiver Activity · GW__LATEST_TRANSFER_GW__</h2><p class="card-description">A same-gameweek drop and pickup is shown as one completed waiver move.</p>__RECENT_WAIVER_ACTIVITY__</div>
              <div class="card"><h2>Waiver History</h2><p class="card-description">All captured free-agent ins and outs, paired into manager transactions rather than double-counted player legs.</p><div class="player-filter-grid transfer-filter-grid"><select id="waiver-team-filter" class="player-filter" onchange="filterWaivers()"><option value="">All fantasy teams</option>__TRANSFER_TEAM_OPTIONS__</select></div>__WAIVER_ARCHIVE__</div>
              <div class="card"><h2>Most Moved Players</h2>__TRANSFERS_CHART____TRANSFER_TABLE__</div><div class="card"><h2>Players Used By The Most Managers</h2>__TEAM_HOPPERS_CHART__</div><div class="card"><h2>Waiver / Market ROI</h2><p class="card-description">Points gained from post-draft acquisitions minus points subsequently scored by players after they were dropped.</p>__TRANSFER_ROI__</div><div class="card"><h2>Hall of Shame</h2>__ABANDONED_ASSETS__</div><div class="card"><h2>Best Historical Pickups</h2>__BEST_HISTORICAL_TRANSFERS__</div>
            </div>
            <div class="transfer-subpanel" id="transfer-subpanel-intelligence">__WAIVER_INTELLIGENCE_HTML__</div>
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

        <!-- ==================================================
             MCDRAFT CUP · INDEPENDENT KNOCKOUT COMPETITION
             ================================================== -->
        <section class="page" id="page-mcdraft-cup">
            <div class="page-heading"><h1>McDraft Cup</h1><p>Two-legged knockouts, one-leg final, forever on the group chat.</p></div>
            __MCDRAFT_CUP_HTML__
        </section>

        <!-- ==================================================
             SEASON SIMULATOR · FINAL MAIN TAB
             ================================================== -->
        <section class="page" id="page-season-simulator">
            <div class="page-heading"><h1>Season Simulator</h1><p>Thousands of possible McDraft seasons. Eight scenarios, including your own transfer-market multiverse.</p></div>
            __SEASON_SIMULATOR_HTML__
        </section>


    </main>
</div><!-- /.mcd-workspace -->

<nav class="mcd-mobile-bottom" id="mcd-mobile-bottom" aria-label="Mobile sections">
  <button type="button" data-mcd-mobile="home"><span class="mcd-nav-icon" aria-hidden="true">⌂</span>Home</button>
  <button type="button" data-mcd-mobile="myteam"><span class="mcd-nav-icon" aria-hidden="true">♜</span>My Team</button>
  <button type="button" data-mcd-mobile="league"><span class="mcd-nav-icon" aria-hidden="true">♛</span>League</button>
  <button type="button" data-mcd-mobile="market"><span class="mcd-nav-icon" aria-hidden="true">⇄</span>Market</button>
  <button type="button" data-mcd-mobile="more"><span class="mcd-nav-icon" aria-hidden="true">☷</span>More</button>
</nav>
<div class="mcd-mobile-sheet" id="mcd-mobile-sheet" role="presentation" hidden>
  <div class="mcd-mobile-sheet-panel" role="dialog" aria-modal="true" aria-labelledby="mcd-sheet-title" tabindex="-1">
    <div class="mcd-mobile-sheet-head"><h2 id="mcd-sheet-title">Browse McDraft</h2><button id="mcd-sheet-close" type="button" aria-label="Close navigation">×</button></div>
    <div class="mcd-mobile-sheet-content" id="mcd-sheet-content"></div>
  </div>
</div>

</div>


<script>

__JAVASCRIPT__


/* Navigation only: every destination routes through EXISTING showPage/subtab handlers. */
const MCD_MENU = [
 {id:'home',title:'Home',icon:'⌂',page:'overview',items:[
  ['League overview','overview','overview','standings'],
  __LIVE_CENTRE_MENU_ITEM__
  ['Predictions & power rankings','overview','overview','intelligence'],
  ['Manager War Room','war-room'],
 ]},
 {id:'myteam',title:'My Team',icon:'♜',page:'myteam',items:[
  ['My squad & FIFA pedigree','myteam','myteam','squad'],
  ['Vulnerability radar','myteam','myteam','squad','myteam-vulnerability-card'],
  ['Five-GW planner','myteam','myteam','planner'],
  ['Medical room','myteam','myteam','medical'],
  ['Transfer targets','myteam','myteam','targets'],
  ['Player Scout','myteam','myteam','scout'],
  ['Head-to-head & stats','myteam','myteam','stats'],
 ]},
 {id:'league',title:'League',icon:'♛',page:'gameweeks',items:[
  ['Results & Team of the Week','gameweeks'],
  ['Fixtures & predictions','fixtures'],
  ['McDraft Cup','mcdraft-cup'],
  ['Season evolution','season-summary','season-summary','evolution'],
  ['McDraft Column archive','season-summary','season-summary','diary'],
  ['Milestones','season-summary','season-summary','milestones'],
  ['Records','season-summary','season-summary','records'],
  ['Share cards','season-summary','season-summary','share'],
  ['Season Simulator','season-simulator'],
 ]},
 {id:'market',title:'Market',icon:'⇄',page:'transfers',items:[
  ['Waivers & pickups','transfers','transfers','waivers'],
  ['Waiver Intelligence','transfers','transfers','intelligence'],
  ['Trades & Trade Lab','transfers','transfers','trades'],
  ['Draft Centre','draft-centre','draft-centre','overview'],
  ['Redraft Today','draft-centre','draft-centre','redraft'],
  ['Original draft board','draft-centre','draft-centre','board'],
 ]},
 {id:'players',title:'Players & Clubs',icon:'♙',page:'players',items:[
  ['Leaders & form','players','players','leaders'],
  ['Player Directory & ratings','players','players','directory'],
  ['Injuries & suspensions','players','players','injuries'],
  ['Availability & departures','players','players','availability'],
  ['Premier League club overview','clubs','clubs','overview'],
  ['Club points by gameweek','clubs','clubs','gameweeks'],
  ['Top players by club','clubs','clubs','players'],
  ['Free agents by club','clubs','clubs','agents'],
  ['PL club fixtures','clubs','clubs','fixtures'],
 ]},
 {id:'analytics',title:'Analytics',icon:'▥',page:'analytics',items:[
  ['McDraft Insights','analytics','analytics','insights'],
  ['Matrix Lab','analytics','analytics','matrices'],
  ['Rating Lab & Squad Time Machine','analytics','analytics','ratings'],
  ['Player Analytics','analytics','analytics','player'],
  ['Player Relationships','analytics','analytics','relationships'],
  ['Transfer River & Passport','analytics','analytics','river-passport'],
  ['PL Club Analytics','analytics','analytics','club'],
  ['Squad Strength','analytics','analytics','squad-strength'],
  ['Squad Construction','analytics','analytics','squad-build'],
  ['Manager Decisions','analytics','analytics','decisions'],
  ['Availability Impact','analytics','analytics','availability-impact'],
  ['Fixtures & H2H Analytics','analytics','analytics','fixtures-h2h'],
  ['Season Analytics','analytics','analytics','season'],
  ['League Stats','analytics','analytics','league-stats'],
 ]},
];
let mcdSelectedGroup='home';
let mcdMobilePreviousFocus=null;
function showLiveCentreMatch(index,button){
 document.querySelectorAll('.live-centre-match').forEach((panel,i)=>panel.classList.toggle('active',i===Number(index)));
 document.querySelectorAll('.live-centre-switch').forEach((btn,i)=>btn.classList.toggle('active',i===Number(index)));
 if(button && window.matchMedia('(max-width:850px)').matches){document.getElementById('live-centre-match-'+index)?.scrollIntoView({behavior:'smooth',block:'start'});}
}
function mcdTabSelector(kind){return ({overview:'.overview-tab',myteam:'.myteam-tab',players:'.player-page-tab',clubs:'.club-explorer-tab',transfers:'.transfer-subtab','season-summary':'.season-summary-tab','draft-centre':'.draft-centre-tab',analytics:'#page-analytics .analytics-subtab'})[kind];}
function mcdSubtabHandler(kind){return ({overview:showOverviewSubtab,myteam:showMyTeamSubtab,players:showPlayerSubtab,clubs:showClubSubtab,transfers:showTransferSubtab,'season-summary':showSeasonSummarySubtab,'draft-centre':showDraftCentreSubtab,analytics:showAnalyticsSubtab})[kind];}
function mcdActivePage(){return (document.querySelector('.page.active')?.id||'page-overview').replace(/^page-/,'');}
function mcdActualSubtab(kind){
 const name=({overview:'overview-sub-',myteam:'myteam-sub-',players:'player-sub-',clubs:'club-sub-',transfers:'transfer-subpanel-','season-summary':'season-summary-sub-','draft-centre':'draft-centre-sub-',analytics:'analytics-sub-'})[kind];
 if(!name)return null;
 const active=document.querySelector('[id^="'+name+'"].active');
 return active?active.id.slice(name.length):null;
}
function mcdNavGoto(groupId,entry){
 const group=MCD_MENU.find(g=>g.id===groupId);if(!group)return;
 const dest=entry||group.items[0];
 const [label,page,kind,tab,anchor]=dest;
 if(!document.getElementById('page-'+page))return;
 mcdSelectedGroup=groupId;
 mcdCloseSheet();
 showPage(page);
 if(kind && tab){
  const sel=mcdTabSelector(kind);
  const btn=sel?Array.from(document.querySelectorAll(sel)).find(b=>(b.getAttribute('onclick')||'').includes("'"+tab+"'")):null;
  const handler=mcdSubtabHandler(kind);if(typeof handler==='function')handler(tab,btn||null);
 }
 mcdNavSync(page);
 if(anchor){setTimeout(()=>{const el=document.getElementById(anchor);if(el)el.scrollIntoView({behavior:'smooth',block:'start'});},150);}
}
function mcdElement(tag,classes,text){const el=document.createElement(tag);if(classes)el.className=classes;if(text!=null)el.textContent=text;return el;}
function mcdBuildMenu(){
 const sidebar=document.getElementById('mcd-sidebar-sections');if(!sidebar)return;
 MCD_MENU.forEach(group=>{
  const details=mcdElement('details','mcd-nav-section');details.dataset.mcdGroup=group.id;
  if(group.id==='home')details.open=true;
  const summary=mcdElement('summary');summary.title=group.title;summary.setAttribute('aria-label',group.title);
  const ico=mcdElement('span','mcd-nav-icon',group.icon);ico.setAttribute('aria-hidden','true');summary.appendChild(ico);
  summary.appendChild(mcdElement('span','mcd-nav-label',group.title));summary.appendChild(mcdElement('span','mcd-nav-chevron','›'));
  details.appendChild(summary);
  const children=mcdElement('div','mcd-nav-children');
  group.items.forEach((entry,i)=>{
   const btn=mcdElement('button','mcd-nav-link',entry[0]);btn.type='button';btn.dataset.mcdPage=entry[1];btn.dataset.mcdRoute=group.id+':'+i;
   btn.addEventListener('click',()=>mcdNavGoto(group.id,entry));children.appendChild(btn);
  });
  details.appendChild(children);sidebar.appendChild(details);
 });
 const collapse=document.getElementById('mcd-sidebar-collapse');
 collapse?.addEventListener('click',()=>{
  const shell=document.getElementById('mcd-workspace'),compact=!shell.classList.contains('mcd-compact');shell.classList.toggle('mcd-compact',compact);
  collapse.textContent=compact?'»':'«';collapse.setAttribute('aria-expanded',String(!compact));collapse.setAttribute('aria-label',compact?'Expand sidebar':'Collapse sidebar');collapse.title=compact?'Expand sidebar':'Collapse sidebar';
  if(compact)sidebar.querySelectorAll('details').forEach(d=>d.open=false);
  else sidebar.querySelector('[data-mcd-group="'+mcdSelectedGroup+'"]')?.setAttribute('open','');
  setTimeout(()=>{if(typeof resizeCharts==='function')resizeCharts();window.dispatchEvent(new Event('resize'));},230);
 });
 sidebar.addEventListener('click',event=>{
  if(!event.target.closest('summary'))return;
  const shell=document.getElementById('mcd-workspace');
  if(shell.classList.contains('mcd-compact')){
   event.preventDefault();shell.classList.remove('mcd-compact');collapse.textContent='«';collapse.setAttribute('aria-expanded','true');collapse.setAttribute('aria-label','Collapse sidebar');
   const sect=event.target.closest('details');sect.open=true;
   setTimeout(()=>{resizeCharts();window.dispatchEvent(new Event('resize'));},230);
  }
 });
 document.querySelectorAll('[data-mcd-mobile]').forEach(btn=>btn.addEventListener('click',()=>{
  const id=btn.dataset.mcdMobile;
  if(id==='more'){mcdOpenSheet('more');return;}
  if(id==='league'||id==='market'){mcdOpenSheet(id);return;}
  if(mcdSelectedGroup===id && mcdActivePage()===(id==='home'?'overview':'myteam'))mcdOpenSheet(id);
  else mcdNavGoto(id);
 }));
 document.getElementById('mcd-current-browse')?.addEventListener('click',()=>mcdOpenSheet(mcdSelectedGroup));
 document.getElementById('mcd-sheet-close')?.addEventListener('click',mcdCloseSheet);
 document.getElementById('mcd-mobile-sheet')?.addEventListener('click',ev=>{if(ev.target.id==='mcd-mobile-sheet')mcdCloseSheet();});
 document.addEventListener('keydown',ev=>{if(ev.key==='Escape')mcdCloseSheet();});
 document.addEventListener('click',ev=>{if(ev.target.closest('.overview-tab,.myteam-tab,.player-page-tab,.club-explorer-tab,.transfer-subtab,.season-summary-tab,.draft-centre-tab,#page-analytics .analytics-subtab'))requestAnimationFrame(()=>mcdNavSync());});
 const insights=document.getElementById('analytics-sub-insights');
 if(insights){
  const directory=mcdElement('div','mcd-analytics-directory');
  const h=mcdElement('h3',null,'Analytics directory');const p=mcdElement('p',null,'Pick a collection. All existing charts and filters are exactly where they were.');directory.append(h,p);
  const grid=mcdElement('div','mcd-analytics-grid');
  const featured=[
   ['ratings','Rating Lab & Squad Time Machine','Player evolution, squad rating race, DEF / MID / ATT.'],
   ['squad-strength','Squad Strength','Quality, depth and positional comparisons.'],
   ['player','Player Analytics','Output, form, scarcity and free agents.'],
   ['matrices','Matrix Lab','Manager comparisons and interactive scatter plots.'],
   ['decisions','Manager Decisions','Bench calls, transfers and manager performance.'],
   ['availability-impact','Availability Impact','Injuries, suspensions and squad exposure.'],
   ['relationships','Player Relationships','Who played with whom and ownership history.'],
   ['league-stats','League Stats','League-wide trends and analytical records.'],
  ];
  featured.forEach(([tab,title,desc])=>{
   const card=mcdElement('button','mcd-analytics-quick');card.type='button';card.append(mcdElement('strong',null,title),mcdElement('small',null,desc));
   card.addEventListener('click',()=>mcdNavGoto('analytics',['', 'analytics','analytics',tab]));grid.appendChild(card);
  });directory.appendChild(grid);insights.prepend(directory);
 }
 // Existing search results continue using the original showPage functions.
 mcdNavSync(mcdActivePage());
}
function mcdNavSync(page){
 const activePage=page||mcdActivePage();
 const preferred=MCD_MENU.find(g=>g.id===mcdSelectedGroup&&g.items.some(e=>e[1]===activePage));
 const group=preferred||MCD_MENU.find(g=>g.items.some(e=>e[1]===activePage))||MCD_MENU[0];
 mcdSelectedGroup=group.id;
 document.querySelectorAll('.mcd-nav-section').forEach(d=>{
  const is=d.dataset.mcdGroup===group.id;d.classList.toggle('is-current',is);
  if(is&&!document.getElementById('mcd-workspace')?.classList.contains('mcd-compact'))d.open=true;
 });
 document.querySelectorAll('.mcd-nav-link').forEach(b=>{
  const g=MCD_MENU.find(g=>g.id===b.dataset.mcdRoute?.split(':')[0]);
  const item=g?.items[Number(b.dataset.mcdRoute?.split(':')[1])];
  const active=!!item&&item[1]===activePage&&(!item[2]||mcdActualSubtab(item[2])===item[3]);
  b.classList.toggle('is-active',active);
  if(active)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');
 });
 const loc=document.getElementById('mcd-mobile-location');if(loc)loc.textContent=group.title;
 document.querySelectorAll('[data-mcd-mobile]').forEach(btn=>{
  const id=btn.dataset.mcdMobile;const selected=(group.id===id||(id==='more'&&['players','analytics'].includes(group.id)));
  btn.classList.toggle('is-current',selected);if(selected)btn.setAttribute('aria-current','page');else btn.removeAttribute('aria-current');
 });
}
function mcdOpenSheet(groupId){
 const sheet=document.getElementById('mcd-mobile-sheet'),content=document.getElementById('mcd-sheet-content');if(!sheet||!content)return;
 const groups=groupId==='more'?MCD_MENU.filter(g=>['players','analytics'].includes(g.id)):MCD_MENU.filter(g=>g.id===groupId);
 const title=groupId==='more'?'Players & Analytics':(groups[0]?.title||'Browse McDraft');
 document.getElementById('mcd-sheet-title').textContent=title;
 content.replaceChildren();
 groups.forEach(group=>{
  const wrap=mcdElement('section','mcd-mobile-sheet-group');wrap.append(mcdElement('h3',null,group.title));
  const links=mcdElement('div','mcd-mobile-sheet-links');
  group.items.forEach(entry=>{
   const btn=mcdElement('button',null,entry[0]);btn.type='button';
   const active=mcdActivePage()===entry[1]&&(!entry[2]||mcdActualSubtab(entry[2])===entry[3]);
   btn.classList.toggle('is-active',active);btn.addEventListener('click',()=>mcdNavGoto(group.id,entry));links.appendChild(btn);
  });wrap.appendChild(links);content.appendChild(wrap);
 });
 mcdMobilePreviousFocus=document.activeElement;
 sheet.hidden=false;document.body.classList.add('mcd-mobile-sheet-open');
 document.getElementById('mcd-sheet-close').focus();
}
function mcdCloseSheet(){
 const sheet=document.getElementById('mcd-mobile-sheet');if(!sheet||sheet.hidden)return;
 sheet.hidden=true;document.body.classList.remove('mcd-mobile-sheet-open');
 if(mcdMobilePreviousFocus&&document.contains(mcdMobilePreviousFocus))mcdMobilePreviousFocus.focus();
 mcdMobilePreviousFocus=null;
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mcdBuildMenu);
else mcdBuildMenu();

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
