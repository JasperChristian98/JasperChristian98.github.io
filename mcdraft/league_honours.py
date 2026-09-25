"""Deterministic, completed-GW-only McDraft accolades, tags and record cards.

No FPL calls and no changes to the original extracted source.  This module
consumes frozen gameweek snapshots and official completed league fixtures.
"""
from __future__ import annotations
from collections import defaultdict
from html import escape


def _num(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _fmt(value):
    return str(int(value)) if float(value).is_integer() else f"{value:.1f}"


def build_honours(history, matches, managers):
    """Build per-week awards, lifetime records and manager-level indicators.

    Only use snapshots explicitly marked finished and matches explicitly
    marked finished by the upstream collector (enriched_matches).
    """
    managers = list(dict.fromkeys(managers))
    completed = sorted((int(gw), snap) for gw, snap in history.get('gameweeks', {}).items()
                       if snap.get('finished'))
    fixtures = defaultdict(list)
    for row in matches:
        try:
            gw = int(row['event'])
        except (TypeError, ValueError, KeyError):
            continue
        a, b = row.get('entry_1_name'), row.get('entry_2_name')
        if a in managers and b in managers and a != b:
            fixtures[gw].append((a, b, _num(row.get('entry_1_points')),
                                 _num(row.get('entry_2_points'))))
    weeks, records = [], {}
    position = {}
    prev_scores = {}
    season = {m: {'played': 0, 'wins': 0, 'draws': 0, 'losses': 0,
                  'league_points': 0, 'points_for': 0, 'points_against': 0,
                  '50_plus': 0, 'streak_win': 0, 'streak_loss': 0,
                  'best_win': 0, 'best_loss': 0, 'bench_total': 0,
                  'top_score_weeks': 0, 'comeback_weeks': 0} for m in managers}

    def record(key, title, value, manager, gw, detail='', low=False):
        if key not in records or (value < records[key]['value'] if low else
                                  value > records[key]['value']):
            records[key] = dict(title=title, value=value, manager=manager,
                                gw=gw, detail=detail)
        elif value == records[key]['value']:
            records[key]['joint'] = True

    for gw, snap in completed:
        # Final frozen picks identify bench and previous scores. Official
        # completed fixtures remain authoritative for the match result.
        squads = {t.get('manager'): t for t in snap.get('teams', {}).values()
                  if t.get('manager') in season}
        games = fixtures.get(gw, [])
        if not games:
            continue
        scores, opponents, results = {}, {}, {}
        for a, b, pa, pb in games:
            scores[a], scores[b] = pa, pb
            opponents[a], opponents[b] = (b, pb), (a, pa)
            results[a] = 'W' if pa > pb else 'D' if pa == pb else 'L'
            results[b] = 'W' if pb > pa else 'D' if pa == pb else 'L'
        active = sorted(scores)
        # Award a weekly title only when its value is meaningful. Use all tied
        # winners, sorted alphabetically, so results never depend on API order.
        awards = []

        def award(label, winners, detail):
            if winners:
                awards.append(dict(label=label, managers=sorted(winners), detail=detail))

        top = max(scores.values())
        award('👑 Top of the Pops', [m for m in active if scores[m] == top],
              f'{_fmt(top)} points scored')
        for m in active:
            if scores[m] == top:
                season[m]['top_score_weeks'] += 1
            season[m]['50_plus'] += scores[m] >= 50
            s = season[m]
            opp, conceded = opponents[m]
            s['played'] += 1
            s['points_for'] += scores[m]
            s['points_against'] += conceded
            outcome = results[m]
            s[{'W': 'wins', 'D': 'draws', 'L': 'losses'}[outcome]] += 1
            s['league_points'] += {'W': 3, 'D': 1, 'L': 0}[outcome]
            s['streak_win'] = s['streak_win'] + 1 if outcome == 'W' else 0
            s['streak_loss'] = s['streak_loss'] + 1 if outcome == 'L' else 0
            s['best_win'] = max(s['best_win'], s['streak_win'])
            s['best_loss'] = max(s['best_loss'], s['streak_loss'])
            bench = _num(squads.get(m, {}).get('bench_points'))
            s['bench_total'] += bench
            record('biggest_bench', 'Bench Museum', bench, m, gw,
                   'Most points left on a bench in one gameweek')
            if outcome == 'L':
                record('points_in_defeat', 'Glorious Defeat', scores[m], m, gw,
                       f'Scored {_fmt(scores[m])} but still lost to {opp}')
            if outcome == 'W':
                record('smallest_winning_margin', 'By the Skin of Their Teeth', scores[m]-conceded,
                       m, gw, f'Beat {opp} by {_fmt(scores[m]-conceded)}', low=True)
                record('biggest_win_margin', 'Absolute Drubbing', scores[m]-conceded,
                       m, gw, f'Beat {opp} by {_fmt(scores[m]-conceded)}')
            record('high_score', 'Highest Weekly Score', scores[m], m, gw)
            record('low_score', 'Lowest Weekly Score', scores[m], m, gw, low=True)
            record('win_streak', 'Winning Machine', s['best_win'], m, gw,
                   'Longest consecutive winning streak')
            record('losing_streak', 'The Long Winter', s['best_loss'], m, gw,
                   'Longest consecutive losing streak')
        # League positions AFTER this week, compared with the previous week.
        order = sorted(managers, key=lambda m: (-season[m]['league_points'],
                                                -(season[m]['points_for']-season[m]['points_against']),
                                                -season[m]['points_for'], m))
        ranks = {m: i+1 for i, m in enumerate(order)}
        changes = {m: position[m]-ranks[m] for m in active if m in position}
        climbers = {m: d for m, d in changes.items() if d > 0}
        if climbers:
            biggest = max(climbers.values())
            winners = [m for m, d in climbers.items() if d == biggest]
            award('🚀 Improver of the Week', winners,
                  f'Climbed {biggest} league place{"s" if biggest != 1 else ""}')
            for m in winners:
                season[m]['comeback_weeks'] += 1
            record('biggest_climb', 'Elevator Express', biggest, ', '.join(sorted(winners)), gw,
                   'Largest one-week climb in league position')
        jump = {m: scores[m]-prev_scores[m] for m in active if m in prev_scores}
        if jump:
            best = max(jump.values())
            if best > 0:
                winners = [m for m, d in jump.items() if d == best]
                award('📈 Form Rocket', winners, f'+{_fmt(best)} points versus previous GW')
                record('score_improvement', 'Biggest Bounce Back', best,
                       ', '.join(sorted(winners)), gw, 'Largest week-on-week score improvement')
        wins = [m for m in active if results[m] == 'W']
        if wins:
            margins = {m: scores[m]-opponents[m][1] for m in wins}
            close = min(margins.values())
            award('😅 Squeaky Bum Time', [m for m in wins if margins[m] == close],
                  f'Won by {_fmt(close)} point{"s" if close != 1 else ""}')
            dominant = max(margins.values())
            if dominant >= 10:
                award('💀 Statement Victory', [m for m in wins if margins[m] == dominant],
                      f'Won by {_fmt(dominant)} points')
        benches = {m: _num(squads.get(m, {}).get('bench_points')) for m in active
                   if m in squads}
        if benches:
            high = max(benches.values())
            if high > 0:
                award('🪑 Bench Museum Curator', [m for m, v in benches.items() if v == high],
                      f'{_fmt(high)} points on the bench')
        if position:
            # A genuine prior-round underdog must beat a better-placed manager.
            upsets = [(position[m]-position[opponents[m][0]], m, opponents[m][0])
                      for m in wins if m in position and opponents[m][0] in position
                      and position[m] > position[opponents[m][0]]]
            if upsets:
                gap = max(x[0] for x in upsets)
                award('🪓 Giant Slayer', [m for d, m, _ in upsets if d == gap],
                      f'Beat a team {gap} place{"s" if gap != 1 else ""} higher before kick-off')
                record('giant_killing', 'Biggest Giant Killing', gap,
                       ', '.join(sorted(m for d, m, _ in upsets if d == gap)), gw,
                       'Largest prior-table position gap overcome')
        record('most_50s', 'Half-Century Collector', max(season[m]['50_plus'] for m in active),
               ', '.join(sorted(m for m in active if season[m]['50_plus'] == max(season[x]['50_plus'] for x in active))),
               gw, 'Most 50+ scoring weeks this season')
        record('most_top_scores', 'Weekly Crown Collector', max(season[m]['top_score_weeks'] for m in active),
               ', '.join(sorted(m for m in active if season[m]['top_score_weeks'] == max(season[x]['top_score_weeks'] for x in active))),
               gw, 'Most weekly top scores')
        position = ranks
        prev_scores.update(scores)
        weeks.append(dict(gw=gw, awards=awards, positions=dict(ranks)))
    return dict(weeks=weeks, records=records, season=season,
                last_positions=position)


def render_awards(data, limit=6):
    if not data['weeks']:
        return '<div class="notice">The extra accolades unlock after a completed gameweek.</div>'
    cards = []
    for week in reversed(data['weeks'][-limit:]):
        honours = ''.join('<div class="honour-pill"><span>{}</span><strong>{}</strong>'
                          '<small>{}</small></div>'.format(escape(a['label']),
                            escape(', '.join(a['managers'])), escape(a['detail']))
                          for a in week['awards'])
        cards.append(f'<details class="honour-week" {"open" if week == data["weeks"][-1] else ""}>'
                     f'<summary>GW{week["gw"]} · {len(week["awards"])} accolades</summary>'
                     f'<div class="honour-grid">{honours}</div></details>')
    return ('<div class="honour-intro">New awards based on completed scores, standings and benches. '
            'Tied winners share the accolade.</div>' + ''.join(cards))


def render_records(data):
    rows = []
    for key, r in data['records'].items():
        if key in ('win_streak', 'losing_streak') and not r['value']:
            continue
        if key == 'biggest_bench' and not r['value']:
            continue
        joint = ' · joint record' if r.get('joint') else ''
        rows.append('<div class="record-card"><div class="record-label">{}</div>'
                    '<div class="record-value">{}</div><div class="record-detail">{} · GW{}{} {}</div></div>'.format(
                        escape(r['title']), escape(r['manager']), _fmt(r['value']),
                        r['gw'], joint, escape(r['detail'])))
    return ''.join(rows)



def render_record_chase(data):
    """Additional current-season chases without rewriting legacy records."""
    season = data['season']
    played = {m: s for m, s in season.items() if s['played']}
    if not played:
        return ''
    challenges = [
        ('50+ scoring weeks', '50_plus', 'week'),
        ('Weekly top scores', 'top_score_weeks', 'crown'),
        ('Total stranded bench points', 'bench_total', 'pt'),
        ('Longest winning run', 'best_win', 'win'),
    ]
    blocks = ['<h3>More Records to Chase</h3>']
    for heading, key, unit in challenges:
        leader = max(s[key] for s in played.values())
        leading = sorted(m for m, s in played.items() if s[key] == leader)
        next_up = sorted(((leader - s[key], m, s[key]) for m, s in played.items()
                          if s[key] < leader), key=lambda item: (item[0], item[1]))[:2]
        challengers = (' · '.join(f'{escape(m)}: {_fmt(value)} ({_fmt(gap)} behind)'
                                  for gap, m, value in next_up) or 'Joint leaders or no challengers yet')
        blocks.append('<div class="record-chase-row"><div><strong>{}</strong>'
                      '<span>Closest challengers: {}</span></div><div><b>{} {}</b>'
                      '<small>{}</small></div></div>'.format(
                          escape(heading), challengers, _fmt(leader), unit + ('s' if leader != 1 else ''),
                          escape(', '.join(leading))))
    return ''.join(blocks)


def extra_manager_tags(data, manager):
    s = data['season'].get(manager)
    if not s or s['played'] < 2:
        return []
    scores = [next((a for a in week['awards'] if a['label'].endswith('Improver of the Week')
                   and manager in a['managers']), None) for week in data['weeks']]
    tags = []
    if s['best_win'] >= 3:
        tags.append(('Steamroller', f"Has won {s['best_win']} consecutive matches."))
    if s['50_plus'] >= 3:
        tags.append(('Half-Century Club', f"Has scored 50+ in {s['50_plus']} gameweeks."))
    if s['top_score_weeks'] >= 2:
        tags.append(('Box Office', f"Has topped the weekly scoring in {s['top_score_weeks']} gameweeks."))
    if sum(v is not None for v in scores) >= 2:
        tags.append(('Social Climber', 'Has won Improver of the Week more than once.'))
    if s['bench_total'] / s['played'] >= 10:
        tags.append(('Bench Hoarder', f"Averages {s['bench_total']/s['played']:.1f} bench points per completed GW."))
    if s['wins'] == 0 and s['played'] >= 3:
        tags.append(('Still Loading', f"Still waiting for a first win after {s['played']} matches."))
    if s['losses'] == 0 and s['played'] >= 3:
        tags.append(('Unbeaten Menace', f"Unbeaten across {s['played']} completed games."))
    return [{'name': a, 'description': b} for a,b in tags]


CSS = '''
.honour-intro {color:var(--muted);font-size:13px;margin:0 0 12px}
.honour-week {border:1px solid var(--border);border-radius:12px;margin:10px 0;background:var(--bg-secondary);padding:10px 14px}
.honour-week summary {cursor:pointer;font-weight:800;color:var(--accent)}
.honour-grid {display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px;margin-top:12px}
.honour-pill {border:1px solid var(--border);border-radius:10px;padding:12px;display:flex;flex-direction:column;gap:4px;min-width:0}
.honour-pill span {font-size:12px;color:var(--muted)}
.honour-pill strong {font-size:15px;overflow-wrap:anywhere}
.honour-pill small {font-size:12px;color:var(--muted)}
'''
