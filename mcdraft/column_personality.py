"""Translate dated manager profiles into evidence-led column prose."""
import copy
import hashlib
import math
import re

STORE_NAME = 'mcdraft_column_profiles.json'
MASTHEAD = '<div class="mcd-column-masthead"><img src="assets/jasp-sports-news.png" alt="Jasp Sports News" width="2172" height="724"></div>'
STYLE = '''<style id="mcd-column-branding">
.mcd-column-masthead{display:flex;justify-content:flex-end;margin:0 0 14px}
.mcd-column-masthead img{display:block;width:min(100%,380px);height:auto;object-fit:contain}
@media(max-width:600px){.mcd-column-masthead img{width:min(100%,280px)}}
</style>'''


def snapshot(store, league, gw, profiles):
    """Only capture the latest completed week; never backfill old reputations."""
    if store.get('league') != league or max(map(int, store.get('weeks', {}) or {'0': {}})) > gw:
        store.clear()
        store.update(league=league, weeks={})
    store.setdefault('weeks', {}).setdefault(str(gw), copy.deepcopy(profiles))


def tendency_lines(gw, phase, profiles, matches):
    candidates = []
    games = [m for m in matches if int(m.get('event') or 0) == int(gw)]
    for name, profile in sorted(profiles.items()):
        tags = {t.get('name') for t in profile.get('tags', []) if isinstance(t, dict)}
        game = next((m for m in games if name in (m.get('entry_1_name'), m.get('entry_2_name'))), None)
        if not game:
            continue
        a = game.get('entry_1_name') == name
        score = game.get('entry_1_points' if a else 'entry_2_points')
        against = game.get('entry_2_points' if a else 'entry_1_points')
        def metric(key):
            try:
                value = float(profile[key])
                return value if math.isfinite(value) else None
            except (KeyError, ValueError, TypeError):
                return None
        options = []
        activity, bench, efficiency = metric('activity_per_gw'), metric('bench_per_gw'), metric('efficiency')
        if tags & {'Waiver Hawk', 'Waiver Goblin', 'Tinkerman', 'Mad Scientist'} and activity is not None:
            options.append(f"{name} rarely leave the squad sheet alone for long: their recorded activity averages {activity:.1f} moves per gameweek. The next answer is often sought in the player pool.")
        if tags & {'Patient Planner', 'Diamond Hands'} and activity is not None:
            options.append(f"{name} tend to give a plan time to breathe, averaging {activity:.1f} moves per gameweek. A disappointing afternoon is not usually followed by a wholesale reshuffle.")
        if 'Luxury Problems' in tags and bench is not None and efficiency is not None:
            options.append(f"{name} have had more useful players than starting places: {bench:.1f} bench points per completed gameweek, despite {efficiency:.1f}% selection efficiency. Some weekends, even a sensible team sheet leaves a little regret behind.")
        elif tags & {'Bench Gambler', 'Bench Museum Curator', 'Bench Hoarder'} and bench is not None:
            options.append(f"{name} have useful depth, but getting it onto the pitch has been another matter: an average of {bench:.1f} points per completed gameweek has stayed on the bench. There is often a second story hiding among their substitutes.")
        if tags & {'XI Surgeon', 'Lean Bench'} and efficiency is not None and efficiency >= 88:
            options.append(f"{name} have generally made good use of the squad at hand, converting {efficiency:.1f}% of the available optimal-XI points into their selected side. Their quieter selection calls deserve some of the attention.")
        if tags & {'Selection Gambler'} and efficiency is not None:
            options.append(f"For {name}, the team sheet has offered room for improvement: selection efficiency stands at {efficiency:.1f}%. The answer may be among the players already in the building.")
        trades = metric('trades')
        if tags & {'Deal Maker', 'Transfer Diplomat'} and trades is not None:
            options.append(f"{name} have brought players in through {trades:g} recorded trades. When the squad needs a new direction, another manager's inbox is rarely far from the conversation.")
        recent = metric('recent_avg')
        if tags & {'On the Charge', 'Hot Hand Merchant'} and recent is not None:
            options.append(f"The recent scoring has given {name} something to build on, averaging {recent:.1f} points over their latest recorded run. There is more conviction behind the current plan than there was before.")
        elif tags & {'Searching for Form'} and recent is not None:
            options.append(f"{name} have been looking for a response, with their latest recorded scoring run averaging {recent:.1f} points. The familiar choices have not been delivering quite as comfortably.")
        volatility = metric('volatility')
        if 'Steady Hand' in tags and volatility is not None:
            options.append(f"{name} have usually kept the weekly swings under control: the standard deviation of their recorded scores is {volatility:.1f} points. Their story has been more about repeatable returns than one spectacular afternoon.")
        elif tags & {'Chaos Merchant', 'Mad Scientist'} and volatility is not None:
            options.append(f"It has been difficult to know which version of {name} will turn up, with a {volatility:.1f}-point standard deviation in their recorded scores. There is potential for fireworks, but the quieter weeks belong in the reckoning too.")
        if not options:
            continue
        seed = int(hashlib.sha256(f'{gw}:{name}'.encode()).hexdigest()[:8], 16)
        line = options[seed % len(options)]
        if phase == 'completed' and score is not None and against is not None:
            score, against = float(score), float(against)
            if not all(map(math.isfinite, (score, against))):
                continue
            result = 'a win' if score > against else 'a defeat' if score < against else 'a draw'
            line += f" This week brought {result}, {score:g}–{against:g}; one result is only part of that longer picture."
        candidates.append((seed, line))
    return [line for _, line in sorted(candidates)[:2]]


def integrate_writer(original, snapshots, current_profiles, matches):
    def expanded(gw, phase='completed'):
        lines = list(original(gw, phase) or [])
        profiles = snapshots.get(str(gw), {}) if phase == 'completed' else current_profiles
        return lines + tendency_lines(gw, phase, profiles, matches)
    return expanded


def brand_column(document):
    if 'id="mcd-column-branding"' not in document:
        document = document.replace('</head>', STYLE + '\n</head>', 1)
    return re.sub(r'(<div class="storyline-latest">)(?!<div class="mcd-column-masthead">)',
                  lambda m: m[0] + MASTHEAD, document)
