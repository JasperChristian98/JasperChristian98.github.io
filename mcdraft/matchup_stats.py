"""Completed-fixture records and schedule luck from frozen league history."""
from collections import defaultdict
import json
import math


def build_stats(history, matches=None):
    weeks = history.get('gameweeks', {})
    fixtures = defaultdict(list)
    seen = set()
    for match in matches if matches is not None else history.get('matches', []):
        try:
            gw = int(match['event'])
            a, b = match['entry_1_name'], match['entry_2_name']
            pa, pb = float(match['entry_1_points']), float(match['entry_2_points'])
        except (KeyError, TypeError, ValueError):
            continue
        if not a or not b or a == b or not all(map(math.isfinite, (pa, pb))):
            continue
        if not weeks.get(str(gw), {}).get('finished') or match.get('finished') is False:
            continue
        key = (gw, *sorted((a, b)))
        if key in seen:
            continue
        seen.add(key)
        fixtures[gw].append((a, b, pa, pb))
    output = {}
    for gw, games in sorted(fixtures.items()):
        scores = {m: p for a, b, pa, pb in games for m, p in [(a, pa), (b, pb)]}
        squads = {t.get('manager'): t for t in weeks[str(gw)].get('teams', {}).values()}
        for a, b, pa, pb in games:
            for manager, opponent, points, against in [(a, b, pa, pb), (b, a, pb, pa)]:
                data = output.setdefault(manager, {'games': [], 'threats': {}, 'heroes': {}})
                peers = [p for m, p in scores.items() if m != manager]
                wins = sum(points > p for p in peers)
                draws = sum(points == p for p in peers)
                actual = 3 if points > against else 1 if points == against else 0
                expected = (wins * 3 + draws) / len(peers)
                game = dict(gw=gw, opponent=opponent, points=points, against=against,
                            result='W' if actual == 3 else 'D' if actual == 1 else 'L',
                            actual=actual, expected=expected, luck=actual-expected,
                            all_play=f'{wins}W {draws}D {len(peers)-wins-draws}L',
                            rank=1+sum(p > points for p in scores.values()), teams=len(scores),
                            average=sum(scores.values())/len(scores),
                            bench=sum(float(p.get('points', 0) or 0) for p in squads.get(manager, {}).get('bench', [])),
                            lineup_available=bool(squads.get(opponent, {}).get('starters')))
                data['games'].append(game)
                for field, owner in [('threats', opponent), ('heroes', manager)]:
                    for p in squads.get(owner, {}).get('starters', []):
                        pid = p.get('element_id')
                        key = str(pid) if pid is not None else (p.get('web_name', 'Unknown') + '|' + p.get('team', ''))
                        row = data[field].setdefault(key, dict(name=p.get('web_name', 'Unknown'),
                            position=p.get('position', ''), points=0, appearances=0, peak=None, peak_gw=gw))
                        value = float(p.get('points', 0) or 0)
                        row['points'] += value
                        row['appearances'] += 1
                        if row['peak'] is None or value > row['peak']:
                            row['peak'], row['peak_gw'] = value, gw
    for data in output.values():
        for field in ('threats', 'heroes'):
            data[field] = sorted(data[field].values(), key=lambda r: (-r['points'], -r['peak'], r['name']))
    return output


CSS = '''
#myteam-sub-stats .dashboard-grid>.card:first-child{grid-column:1/-1;min-width:0}
.mcd-stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:10px;margin:14px 0 22px}
.mcd-stat-grid>div{border:1px solid var(--border);border-radius:12px;background:var(--bg-secondary);padding:14px}
.mcd-stat-grid small,.mcd-stat-grid strong{display:block}.mcd-stat-grid strong{font-size:23px;margin:6px 0}.mcd-stat-grid small{color:var(--muted)}
.mcd-stats-positive{color:#16a374}.mcd-stats-negative{color:#dc6476}.mcd-stats-table{max-height:520px;overflow:auto}.mcd-stats-table th{white-space:nowrap}
.mcd-stats-players{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.mcd-stats-players>div{min-width:0}
@media(max-width:720px){.mcd-stats-players{grid-template-columns:1fr}}
'''

JS = r'''
function mcdStatsTable(headers, rows){return '<div class="table-wrap mcd-stats-table"><table><thead><tr>'+headers.map(h=>'<th scope="col">'+h+'</th>').join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+row.map(v=>'<td>'+v+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>';}
function renderMyTeamH2H(){
 const wrap=document.getElementById('myteam-h2h-record');if(!wrap)return;
 const manager=currentMyTeamManager(),data=MCD_MATCHUP_STATS[manager],e=escapePlayerHTML;
 if(!data?.games.length){wrap.innerHTML='<div class="notice">No completed head-to-head fixtures captured for this team yet.</div>';return;}
 const games=data.games,sum=k=>games.reduce((s,g)=>s+g[k],0),n=games.length;
 const wins=games.filter(g=>g.result==='W').length,draws=games.filter(g=>g.result==='D').length;
 const signed=v=>(v>0?'+':'')+v.toFixed(2);
 const luck=v=>'<span class="'+(v>.001?'mcd-stats-positive':v<-.001?'mcd-stats-negative':'')+'">'+signed(v)+'</span>';
 let longest=0,run=0;games.forEach(g=>{run=g.result==='W'?run+1:0;longest=Math.max(longest,run);});
 const last=games[n-1];let streak=0;for(let i=n-1;i>=0&&games[i].result===last.result;i--)streak++;
 const best=games.reduce((a,b)=>a.points>=b.points?a:b),worst=games.reduce((a,b)=>a.points<=b.points?a:b);
 const victories=games.filter(g=>g.result==='W'),defeats=games.filter(g=>g.result==='L');
 const biggest=victories.length?victories.reduce((a,b)=>a.points-a.against>=b.points-b.against?a:b):null;
 const heaviest=defeats.length?defeats.reduce((a,b)=>a.against-a.points>=b.against-b.points?a:b):null;
 const metrics=[['Overall record',wins+'W '+draws+'D '+(n-wins-draws)+'L',n+' completed games'],
 ['League points',sum('actual'),(100*wins/n).toFixed(1)+'% win rate'],
 ['Points scored',sum('points').toFixed(0),(sum('points')/n).toFixed(1)+' per game'],
 ['Points conceded',sum('against').toFixed(0),(sum('against')/n).toFixed(1)+' per game'],
 ['Expected league points',sum('expected').toFixed(2),'Against a random opponent each week'],
 ['Fixture luck',luck(sum('luck')),'Actual minus expected league points'],
 ['Highest / lowest score',best.points+' / '+worst.points,'GW'+best.gw+' / GW'+worst.gw],
 ['Current run',streak+last.result,'Longest winning streak: '+longest],
 ['Close games',games.filter(g=>Math.abs(g.points-g.against)<=5).length,'Margin of five points or fewer'],
 ['Recent form',games.slice(-5).map(g=>g.result).join(' '),'Oldest to newest, last five games'],
 ['Biggest win',biggest?'+'+(biggest.points-biggest.against):'—',biggest?'GW'+biggest.gw+' vs '+e(biggest.opponent):'No wins yet'],
 ['Heaviest defeat',heaviest?heaviest.points-heaviest.against:'—',heaviest?'GW'+heaviest.gw+' vs '+e(heaviest.opponent):'No defeats yet']];
 let html='<div class="mcd-stat-grid">'+metrics.map(m=>'<div><small>'+m[0]+'</small><strong>'+m[1]+'</strong><small>'+m[2]+'</small></div>').join('')+'</div>';
 const opponents={};games.forEach(g=>{(opponents[g.opponent]??=[]).push(g);});
 html+='<h3>Opponent records</h3>'+mcdStatsTable(['Opponent','W–D–L','Win %','For / against','Avg margin','Luck'],Object.entries(opponents).sort((a,b)=>a[0].localeCompare(b[0])).map(([name,rows])=>{
 const w=rows.filter(g=>g.result==='W').length,d=rows.filter(g=>g.result==='D').length,pf=rows.reduce((s,g)=>s+g.points,0),pa=rows.reduce((s,g)=>s+g.against,0);
 return [e(name),w+'–'+d+'–'+(rows.length-w-d),(100*w/rows.length).toFixed(0)+'%',pf+' / '+pa,signed((pf-pa)/rows.length),luck(rows.reduce((s,g)=>s+g.luck,0))];}));
 html+='<h3>How lucky were you each game?</h3><p class="card-description">Fixture luck measures the draw of opponents, not player performance against a forecast. Expected league points = (3 × opponents you would beat + opponents you would draw with) ÷ other teams with completed scores that GW. Positive luck means the fixture earned you more points than that average; negative means fewer. All-play shows your record against every other available score, including your actual opponent. Live and future games are excluded.</p>';
 html+=mcdStatsTable(['GW','Opponent','Score','Result','GW rank','League avg','All-play W/D/L','Expected LP','Actual LP','Luck'],[...games].reverse().map(g=>[g.gw,e(g.opponent),g.points+'–'+g.against,g.result,g.rank+'/'+g.teams,g.average.toFixed(1),g.all_play,g.expected.toFixed(2),g.actual,luck(g.luck)]));
 html+='<div class="mcd-stats-players">';
 for(const [field,title] of [['threats','Players who scored most against you'],['heroes','Your biggest contributors']]){
 html+='<div><h3>'+title+'</h3>'+ (data[field].length?mcdStatsTable(['Player','Pos','Points','Games','Pts/game','Biggest haul'],data[field].slice(0,20).map(p=>[e(p.name),e(p.position),p.points,p.appearances,(p.points/p.appearances).toFixed(1),p.peak+' (GW'+p.peak_gw+')'])):'<p class="notice">Historical lineups are unavailable.</p>')+'</div>';}
 html+='</div><p class="card-description">Player totals use captured starting lineups for these fixtures; bench points are excluded. Historical lineups available for '+games.filter(g=>g.lineup_available).length+' of '+n+' opponent games. Official fixture totals determine results and can differ from captured player totals after substitutions or corrections.</p>';
 wrap.innerHTML=html;
}
'''


def javascript_with_data(data):
    payload = json.dumps(data, ensure_ascii=True, allow_nan=False).replace('<', '\\u003c')
    return '\nconst MCD_MATCHUP_STATS = ' + payload + ';\n' + JS
