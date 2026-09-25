"""Data-backed squad-radar explanations and additional McDraft editorial desks.

Designed as a post-stage integration: no changes to the audited original stages.
Never derives historical claims from current player data or unfinished matches.
"""
from __future__ import annotations

from collections import defaultdict
import random
import re

RADAR_CSS = r'''
.radar-explainer{margin-top:16px;display:grid;gap:12px}
.radar-explainer .radar-takeaway{padding:15px;border-radius:13px;background:var(--bg-secondary);border:1px solid var(--border)}
.radar-explainer h3{margin:0 0 8px;font-size:1rem}
.radar-explainer p{margin:6px 0;color:var(--muted);line-height:1.55;font-size:.86rem}
.radar-explainer .radar-explain-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(225px,1fr));gap:10px}
.radar-explainer .radar-explain-axis{padding:12px;border:1px solid var(--border);border-radius:10px;background:var(--bg-secondary)}
.radar-explainer .radar-explain-axis strong{display:flex;justify-content:space-between;gap:10px}
.radar-explainer .radar-explain-axis p{font-size:.79rem;margin:6px 0 0}
.radar-explainer .radar-score-meter{height:5px;border-radius:9px;background:var(--border);margin-top:10px;overflow:hidden}
.radar-explainer .radar-score-meter>span{display:block;height:100%;background:var(--accent);border-radius:9px}
.column-extra-label{font-weight:850;color:var(--accent)}
'''

# Added at the end of the existing client JS. Preserve the old radar renderer and
# the scores it computes rather than implementing a competing set of metrics.
RADAR_JS = r'''
/* McDraft Performance Radar: per-manager interpretation of the original six axes. */
const MCD_RADAR_EXPLANATIONS = {
 'Output':'Season-long FPL points per game versus players in the same position.',
 'Recent form':'Recent FPL form compared with players in the same position.',
 'Goals':'Goals per 90 minutes relative to the player’s position.',
 'Assists':'Assists per 90 minutes relative to the player’s position.',
 'Defending':'Defensive contributions, clean sheets and saves per 90, adjusted for position.',
 'Bonus':'FPL bonus points per 90 versus others in the same position.'
};
const mcdOriginalRenderMyTeamRadar = renderMyTeamRadar;
renderMyTeamRadar = function(){
 mcdOriginalRenderMyTeamRadar();
 const root=document.getElementById('myteam-radar');
 if(!root||!root.querySelector('.radar-layout'))return;
 const roster=playerSearchData.filter(p=>p.fantasy_team===currentMyTeamManager());
 const eligible=roster.filter(p=>Number(p.minutes||0)>=90);
 if(!eligible.length)return;
 const matrix=eligible.map(radarScores);
 const axes=RADAR_AXES.map(([name],i)=>({
   name, score:Math.round(matrix.reduce((sum,row)=>sum+row[i],0)/matrix.length), index:i
 }));
 const ranked=axes.slice().sort((a,b)=>b.score-a.score||a.index-b.index);
 const strongest=ranked.slice(0,2), weakest=ranked.slice(-2).reverse();
 const axisCard=axis=>'<div class="radar-explain-axis"><strong><span>'+
   escapePlayerHTML(axis.name)+'</span><span>'+axis.score+'/100</span></strong>'+
   '<div class="radar-score-meter"><span style="width:'+axis.score+'%"></span></div>'+
   '<p>'+escapePlayerHTML(MCD_RADAR_EXPLANATIONS[axis.name]||'Position-relative comparison.')+'</p></div>';
 const scoreRange=ranked[0].score-ranked[ranked.length-1].score;
 const overview=scoreRange<=10
   ?'This squad has a fairly balanced radar; the difference between its highest and lowest axis is only '+scoreRange+' percentile points.'
   :'The clearest relative strength is '+ranked[0].name.toLowerCase()+' ('+ranked[0].score+'/100), while '+
     ranked[ranked.length-1].name.toLowerCase()+' ('+ranked[ranked.length-1].score+'/100) is the lowest squad-wide axis.';
 const oldNote=root.querySelector('.card-description');
 if(oldNote)oldNote.textContent='Squad mean of each eligible player’s percentile against their own PL position. '+eligible.length+
   ' of '+roster.length+' players have played at least 90 PL minutes. Higher means stronger relative historical output, not a projection.';
 root.insertAdjacentHTML('beforeend','<section class="radar-explainer" aria-label="Squad radar explanation">'+
   '<div class="radar-takeaway"><h3>What does this radar say?</h3><p>'+escapePlayerHTML(overview)+'</p>'+
   '<p>These are averages of position-relative percentiles, not the squad’s actual total attacking or defensive output. A low score does not necessarily mean a bad fantasy selection.</p></div>'+
   '<div class="radar-explain-grid"><div class="radar-takeaway"><h3>Relative strengths</h3>'+
      strongest.map(axisCard).join('')+'</div><div class="radar-takeaway"><h3>Areas to investigate</h3>'+
      weakest.map(axisCard).join('')+'</div></div>'+
   '<details class="radar-takeaway"><summary><strong>How are the six axes calculated?</strong></summary>'+
   '<p>Each player with 90+ Premier League minutes receives a percentile within their own position. '+
   'Goals, assists, defending and bonus use per-90 rates. Output uses FPL points per game, and recent form uses the FPL form field. '+
   'The squad radar averages those six player percentiles equally across eligible players; it is descriptive, not a live fixture or injury forecast.</p></details></section>');
};
'''


def _ordinal(rank: int) -> str:
    """English ordinal with correct 11th–13th and 1st/2nd/3rd endings."""
    rank = int(rank)
    suffix = 'th' if rank % 100 in (11, 12, 13) else {1: 'st', 2: 'nd', 3: 'rd'}.get(rank % 10, 'th')
    return f'{rank}{suffix}'


def _editorial_choice(gw, tag, choices):
    """Stable variety: refreshing the same archived edition won't rewrite it."""
    seed = gw * 1009 + sum((i + 1) * ord(ch) for i, ch in enumerate(tag))
    return random.Random(seed).choice(choices)


def column_desks(gw: int, honours: dict, matches: list, history: dict) -> list[str]:
    """Fact-checked standalone beats in natural prose, without section headings.

    The story assembler mixes these with the main match report. Completed GWs
    and saved weekly standings are the only sources of historical claims.
    """
    gw = int(gw)
    week = next((w for w in honours.get('weeks', []) if w.get('gw') == gw), None)
    snapshot = history.get('gameweeks', {}).get(str(gw), {})
    if not week or not snapshot.get('finished'):
        return []
    games = [m for m in matches if int(m.get('event') or 0) == gw]
    if not games:
        return []
    desks = []
    spotlights = [a for a in week.get('awards', []) if not a['label'].endswith('Top of the Pops')]
    if spotlights:
        chosen = spotlights[(gw * 7) % len(spotlights)]
        winners = ', '.join(chosen['managers'])
        # Labels carry an emoji and are useful on the awards page, but newspaper
        # prose should not read like a widget dumping its keys.
        award = re.sub(r'^[^\w]+', '', chosen['label']).strip()
        detail = str(chosen.get('detail') or '').strip().rstrip('.')
        desks.append(_editorial_choice(gw, 'award', [
            f"The {award} award goes to {winners}. {detail + '.' if detail else ''} Don't expect a modest acceptance speech.",
            f"{winners} have a little extra to celebrate: {award}. {detail + '.' if detail else ''} Their group-chat notification count could be about to rise.",
        ]))

    previous = next((w for w in reversed(honours['weeks']) if w['gw'] < gw), None)
    positions = week.get('positions', {})
    if previous:
        changes = [(previous['positions'][m] - rank, m, previous['positions'][m], rank)
                   for m, rank in positions.items() if m in previous.get('positions', {})]
        movers = sorted((x for x in changes if x[0] > 0), key=lambda x: (-x[0], x[1]))
        fallers = sorted((x for x in changes if x[0] < 0), key=lambda x: (x[0], x[1]))
        if movers:
            gain, manager, old, new = movers[0]
            move = f"{manager} rose {gain} place{'s' if gain != 1 else ''}, from {_ordinal(old)} to {_ordinal(new)}"
            if fallers:
                loss, down, was, now = fallers[0]
                move += f", while {down} slipped from {_ordinal(was)} to {_ordinal(now)}"
            desks.append(_editorial_choice(gw, 'table', [
                f"The table had a reshuffle, too: {move}. Somebody's going to be checking the standings every five minutes.",
                f"Away from the scores, {move}. No doubt both managers have very measured opinions about it.",
            ]))
        elif fallers:
            loss, down, was, now = fallers[0]
            desks.append(f"The table wasn't kind to {down}, who slipped from {_ordinal(was)} to {_ordinal(now)}. Time to avoid the standings page.")

    outcomes = []
    for m in games:
        a, b = m.get('entry_1_name'), m.get('entry_2_name')
        pa, pb = m.get('entry_1_points'), m.get('entry_2_points')
        if a and b and pa is not None and pb is not None:
            outcomes.append((abs(float(pa)-float(pb)), a, b, float(pa), float(pb)))
    if outcomes:
        margin, a, b, pa, pb = min(outcomes, key=lambda x: (x[0], x[1], x[2]))
        if 0 < margin <= 3:
            winner, loser = (a, b) if pa > pb else (b, a)
            ws, ls = max(pa, pb), min(pa, pb)
            desks.append(_editorial_choice(gw, 'close', [
                f"Elsewhere, {winner} edged {loser} {ws:g}–{ls:g}, a margin of just {margin:g}. There are less stressful ways to spend a Sunday.",
                f"A single good decision could have changed {winner}'s {ws:g}–{ls:g} escape against {loser}. A {margin:g}-point margin is hardly comfortable viewing.",
            ]))
        elif margin == 0:
            desks.append(f"{a} and {b} couldn't be separated, finishing {pa:g}–{pb:g}. The bragging rights will have to wait.")
        scores = [score for _, _, _, x, y in outcomes for score in (x, y)]
        threshold = sorted(scores)[max(0, int(len(scores) * .7) - 1)]
        losers = sorted([(pa, a, b, pb) for _, a, b, pa, pb in outcomes if pa < pb]
                        + [(pb, b, a, pa) for _, a, b, pa, pb in outcomes if pb < pa],
                        key=lambda x: (-x[0], x[1]))
        if losers and losers[0][0] >= threshold:
            score, manager, opponent, conceded = losers[0]
            desks.append(_editorial_choice(gw, 'unlucky', [
                f"Spare a thought for {manager}, whose {score:g} points still weren't enough against {opponent}'s {conceded:g}. Sometimes a perfectly respectable weekend gets you precisely nothing.",
                f"{manager} managed {score:g} points and still lost {score:g}–{conceded:g} to {opponent}. That's the sort of result that has you staring at the ceiling on Sunday night.",
            ]))

    results = defaultdict(list)
    complete = {w['gw'] for w in honours.get('weeks', []) if w['gw'] <= gw}
    for m in sorted(matches, key=lambda row: int(row.get('event') or 0)):
        event = int(m.get('event') or 0)
        if event not in complete:
            continue
        a, b = m.get('entry_1_name'), m.get('entry_2_name')
        x, y = float(m.get('entry_1_points') or 0), float(m.get('entry_2_points') or 0)
        if a and b:
            results[a].append((event, 'W' if x > y else 'D' if x == y else 'L'))
            results[b].append((event, 'W' if y > x else 'D' if x == y else 'L'))
    streaks = []
    for manager, rows in results.items():
        ordered = sorted(rows)
        if not ordered or ordered[-1][0] != gw:
            continue
        last = ordered[-1][1]
        length = 0
        for _, result in reversed(ordered):
            if result != last:
                break
            length += 1
        if length >= 3 and last in ('W', 'L'):
            streaks.append((length, last, manager))
    if streaks:
        length, result, manager = max(streaks, key=lambda x: (x[0], x[1] == 'W', x[2]))
        if result == 'W':
            desks.append(f"{manager}, meanwhile, have made it {length} wins on the bounce. It's getting harder to tell whether they're celebrating or just updating their profile picture.")
        else:
            desks.append(f"It's now {length} defeats in a row for {manager}. The next gameweek cannot arrive soon enough — or perhaps it can.")
    return desks[:5]


def add_column_desks(original, honours, matches, history):
    """Augment the existing editorial without touching live or preview copy."""
    def expanded(gw, phase='completed'):
        current = original(gw, phase)
        if phase != 'completed':
            return current
        return list(current or []) + column_desks(gw, honours, matches, history)
    return expanded


def _split_sentences(paragraph):
    """Preserve decimal statistics and abbreviations such as J.Timber."""
    return re.split(r'(?<=[.!?])\s+(?=[A-Z🪑⚽])', paragraph.strip())


def humanise_column_story(original, honours):
    """Recompose an existing completed-GW story as a varied newspaper article.

    The underlying source still writes all factual beats. Here we remove duplicate
    coverage of the same result, shuffle secondary stories deterministically,
    and distribute them between short natural paragraphs. Cup and next-GW
    previews stay in sensible positions at the end of the piece.
    """
    def expanded(gw):
        story = original(gw)
        pieces = [p.strip() for p in story.split('\n\n') if p.strip()]
        if len(pieces) < 2:
            return story
        body = pieces[0]
        sentences = _split_sentences(body)
        extras = []
        cup = []
        preview = []
        for part in pieces[1:]:
            if re.search(r'\bGW' + str(int(gw) + 1) + r'\b', part) and part == pieces[-1]:
                preview.append(part)
            elif part.startswith(('🏆 ', 'CUP ', 'THE McDRAFT CUP')):
                cup.append(part)
            else:
                extras.append(part)

        # Detect overlap with original lead: do not print an additional
        # table move, streak or photo finish if the main writer covered it.
        lead = body.casefold()
        filtered = []
        for item in extras:
            plain = re.sub(r'^[🪑⚽]\s*(?:BENCH WATCH|SELECTION DESK|CLUB CONNECTION|CLUB WATCH):\s*', '', item)
            # Also gracefully handle earlier saved-style editorial snippets.
            old_section = re.match(r'^(THE TABLE SHUFFLE|THE FORM WATCH|THE NERVE CENTRE|ROUGH JUSTICE|THE AWARDS DESK)\s*[—:]\s*', plain)
            section_name = old_section.group(1) if old_section else ''
            if old_section:
                plain = plain[old_section.end():]
            low = plain.casefold()
            if section_name == 'THE TABLE SHUFFLE' and any(
                    term in lead for term in ('moving from', 'climbing', 'climb', 'rose ', 'slipped', 'top of mcdraft')):
                continue
            if section_name == 'THE FORM WATCH' and any(
                    term in lead for term in ('wins in a row', 'wins on the bounce', 'lost in a row', 'winning streak')):
                continue
            if section_name == 'THE NERVE CENTRE' and any(
                    term in lead for term in ('squeezed past', 'photo finish', 'closest', 'point between')):
                continue
            if ('table had a reshuffle' in low or 'away from the scores' in low or
                    "table wasn't kind" in low) and any(
                        term in lead for term in ('moving from', 'climbing', 'climb', 'rose ', 'slipped', 'top of mcdraft')):
                continue
            if ('wins on the bounce' in low or 'defeats in a row' in low) and any(
                        term in lead for term in ('wins in a row', 'wins on the bounce', 'lost in a row', 'winning streak')):
                continue
            if ('edged' in low or 'escape against' in low or "couldn't be separated" in low) and any(
                        term in lead for term in ('squeezed past', 'photo finish', 'closest', 'point between')):
                continue
            filtered.append(plain)
        rng = random.Random(int(gw) * 10007 + 733)
        # The lead and event chronology stay intact. Secondary human-interest
        # items vary in placement, not their facts, on every published edition.
        rng.shuffle(filtered)
        groups = []
        # Keep the first two or three sentences as the strong opening.
        lead_end = min(3, len(sentences))
        groups.append(sentences[:lead_end])
        remaining = sentences[lead_end:]
        while remaining:
            groups.append(remaining[:3])
            remaining = remaining[3:]
        # At most two extra beats in a paragraph. Spread the rest across
        # short new paragraphs instead of dumping a labelled list at the end.
        for idx, item in enumerate(filtered):
            target = 1 + idx if 1 + idx < len(groups) else len(groups)
            if target == len(groups):
                groups.append([])
            groups[target].append(item)
        paragraphs = [' '.join(group) for group in groups if group]
        paragraphs.extend(cup)
        paragraphs.extend(preview)
        return '\n\n'.join(paragraphs)
    return expanded
