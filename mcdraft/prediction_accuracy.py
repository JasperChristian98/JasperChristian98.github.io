"""Immutable pre-deadline forecast snapshots and retrospective McDraft model audit.

Snapshots are captured only while the deadline is in the future and before any
reliable match-start indicator. Existing snapshots are never overwritten; absent
historical forecasts are NOT backfilled from today's model.
"""
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json
import math
import os
import tempfile

MODEL_VERSION = 'mcdraft-forecast-original-v1'
STORE_NAME = 'mcdraft_prediction_history.json'


def _utc(value):
    if not value:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        try:
            dt = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        except (TypeError, ValueError):
            return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def read_store(path):
    path = Path(path)
    if not path.exists():
        return {'schema_version': 1, 'gameweeks': {}}
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('schema_version') != 1 or not isinstance(data.get('gameweeks'), dict):
        raise ValueError('Unknown prediction history schema; refusing to overwrite it')
    return data


def atomic_save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.prediction-history-', suffix='.json', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False, allow_nan=False)
            fh.write('\n')
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def capture_forecast(store, *, gw, deadline, now, started, fixtures, forecast, model_version=MODEL_VERSION):
    """Capture once, strictly before deadline; forecast(team1, team2)->odds dict."""
    gw = int(gw or 0)
    now_dt, deadline_dt = _utc(now), _utc(deadline)
    if gw <= 0 or str(gw) in store['gameweeks']:
        return False
    if started or not now_dt or not deadline_dt or now_dt >= deadline_dt:
        return False
    records = []
    eligible = 0
    for fixture in fixtures:
        team1, team2 = fixture.get('team1'), fixture.get('team2')
        if not team1 or not team2 or team1 == team2 or fixture.get('finished'):
            continue
        eligible += 1
        odds = forecast(team1, team2)
        if not odds:
            continue
        keys = ('team1_win', 'draw', 'team2_win', 'team1_mean', 'team2_mean',
                'team1_low', 'team1_high', 'team2_low', 'team2_high')
        try:
            measures = {key: float(odds[key]) for key in keys}
        except (KeyError, ValueError, TypeError):
            continue
        if not all(math.isfinite(v) for v in measures.values()):
            continue
        if any(measures[key] < 0 for key in ('team1_win', 'draw', 'team2_win')):
            continue
        if abs(sum(measures[key] for key in ('team1_win', 'draw', 'team2_win')) - 100) > .2:
            continue
        records.append({'team1': team1, 'team2': team2, **measures})
    # Never freeze an incomplete week if one manager lacks projection data.
    if not records or len(records) != eligible:
        return False
    store['gameweeks'][str(gw)] = {
        'captured_at': now_dt.isoformat(), 'deadline': deadline_dt.isoformat(),
        'model_version': str(model_version), 'fixtures': records,
    }
    return True


def _actual_result(row):
    if not row.get('finished'):
        return None
    try:
        return float(row['league_entry_1_points']), float(row['league_entry_2_points'])
    except (KeyError, TypeError, ValueError):
        return None


def evaluate(store, actual_matches):
    """Only exact fixture/GW identity matches, and only completed actual results."""
    lookup = {}
    for m in actual_matches:
        try:
            gw = int(m['event'])
            team1, team2 = m['entry_1_name'], m['entry_2_name']
            scores = (float(m['entry_1_points']), float(m['entry_2_points']))
        except (KeyError, ValueError, TypeError):
            continue
        if not m.get('finished', True):
            continue
        lookup[(gw, team1, team2)] = scores
        lookup[(gw, team2, team1)] = scores[::-1]
    rows = []
    for key, snap in store.get('gameweeks', {}).items():
        try:
            gw = int(key)
        except ValueError:
            continue
        for predicted in snap.get('fixtures', []):
            t1, t2 = predicted['team1'], predicted['team2']
            scores = lookup.get((gw, t1, t2))
            if scores is None:
                continue
            a, b = scores
            result = 0 if a > b else 2 if a < b else 1
            probs = [predicted['team1_win']/100, predicted['draw']/100, predicted['team2_win']/100]
            brier = sum((p - int(i == result))**2 for i,p in enumerate(probs))
            # Exclude unresolved ties in selecting the maximum-probability prediction.
            chosen = max(range(3), key=lambda idx: probs[idx])
            rows.append({
                'gw': gw, 'team1': t1, 'team2': t2, 'actual1': a, 'actual2': b,
                'predicted1': predicted['team1_mean'], 'predicted2': predicted['team2_mean'],
                'p1': probs[0], 'pd': probs[1], 'p2': probs[2],
                'correct': chosen == result, 'brier': brier,
                'score_error': (abs(predicted['team1_mean']-a)+abs(predicted['team2_mean']-b))/2,
                'covered': (int(predicted['team1_low'] <= a <= predicted['team1_high'])+
                            int(predicted['team2_low'] <= b <= predicted['team2_high']))/2,
                'model_version': snap.get('model_version','unknown'),
                'captured_at': snap.get('captured_at',''),
                'outcome': result,
            })
    rows.sort(key=lambda r: (r['gw'], r['team1'], r['team2']))
    n = len(rows)
    summary = None
    if n:
        summary = {
            'matches': n, 'prediction_accuracy': sum(r['correct'] for r in rows)/n,
            'brier': sum(r['brier'] for r in rows)/n,
            'score_mae': sum(r['score_error'] for r in rows)/n,
            'interval_coverage': sum(r['covered'] for r in rows)/n,
        }
    # Home and away binary probabilities counted separately; matches are not
    # independent but this makes the calibration plot use both predicted sides.
    buckets = []
    for lower in range(0, 100, 20):
        observations = []
        for row in rows:
            for prob, actual in ((row['p1'], row['outcome']==0),(row['p2'],row['outcome']==2)):
                if lower/100 <= prob < (lower+20)/100 or (lower==80 and prob==1):
                    observations.append((prob, int(actual)))
        if observations:
            buckets.append({'label': f'{lower}–{lower+20}%', 'n': len(observations),
                            'expected': sum(x for x,_ in observations)/len(observations),
                            'observed': sum(y for _,y in observations)/len(observations)})
    by_week = []
    for gw in sorted({r['gw'] for r in rows}):
        week = [r for r in rows if r['gw'] == gw]
        by_week.append({'gw': gw, 'matches': len(week),
                        'accuracy': sum(r['correct'] for r in week)/len(week),
                        'mae': sum(r['score_error'] for r in week)/len(week),
                        'brier': sum(r['brier'] for r in week)/len(week)})
    return {'summary': summary, 'rows': rows, 'calibration': buckets,
            'by_week': by_week, 'snapshot_count': len(store.get('gameweeks', {}))}


def render_report(report):
    metrics = report['summary']
    if not metrics:
        body = ('<div class="notice">No completed matches with saved pre-deadline forecasts yet. '
                'Forecasts will be frozen automatically before future gameweeks; '
                'historical predictions cannot be reconstructed fairly.</div>')
    else:
        def metric(name, value, hint):
            return f'<div class="pa-metric"><span>{escape(name)}</span><strong>{value}</strong><small>{escape(hint)}</small></div>'
        body = '<div class="pa-grid">' + ''.join((
            metric('Matches evaluated',str(metrics['matches']),'Pre-deadline forecasts only'),
            metric('Outcome accuracy',f"{metrics['prediction_accuracy']:.0%}",'Most probable of win/draw/loss'),
            metric('Score error',f"{metrics['score_mae']:.1f} pts",'Mean absolute team-score error'),
            metric('Brier score',f"{metrics['brier']:.3f}",'3-outcome score; lower is better'),
            metric('80% interval coverage',f"{metrics['interval_coverage']:.0%}",'How often real scores land in predicted ranges'),
        )) + '</div>'
        if report['calibration']:
            body += '<h3>Probability calibration</h3><p class="card-description">If the model says 60% over many matches, roughly 60% should win. Each match contributes both teams.</p>'
            for bucket in report['calibration']:
                body += (f'<div class="pa-cal-row"><span>{bucket["label"]} (n={bucket["n"]})</span>'
                         f'<div class="pa-track"><i style="width:{bucket["expected"]*100:.1f}%" title="Predicted"></i>'
                         f'<b style="width:{bucket["observed"]*100:.1f}%" title="Actual"></b></div>'
                         f'<span>{bucket["expected"]:.0%} predicted / {bucket["observed"]:.0%} actual</span></div>')
        body += '<h3>Gameweek-by-gameweek performance</h3><div class="table-wrap"><table><thead><tr><th>GW</th><th>Matches</th><th>Outcome accuracy</th><th>Score MAE</th><th>Brier</th></tr></thead><tbody>'
        for week in reversed(report['by_week']):
            body += (f'<tr><td>GW{week["gw"]}</td><td>{week["matches"]}</td>'
                     f'<td>{week["accuracy"]:.0%}</td><td>{week["mae"]:.1f}</td>'
                     f'<td>{week["brier"]:.3f}</td></tr>')
        body += '</tbody></table></div>'
        body += '<h3>Recent audited predictions</h3><div class="table-wrap"><table><thead><tr><th>GW</th><th>Fixture</th><th>Prediction</th><th>Actual</th><th>Win / Draw / Loss</th><th>Score error</th></tr></thead><tbody>'
        for row in reversed(report['rows'][-15:]):
            body += (f'<tr><td>{row["gw"]}</td><td>{escape(row["team1"])} vs {escape(row["team2"])}</td>'
                     f'<td>{row["predicted1"]:.1f}–{row["predicted2"]:.1f}</td>'
                     f'<td>{row["actual1"]:g}–{row["actual2"]:g}</td>'
                     f'<td>{row["p1"]:.0%} / {row["pd"]:.0%} / {row["p2"]:.0%}</td>'
                     f'<td>{row["score_error"]:.1f}</td></tr>')
        body += '</tbody></table></div>'
    return ('<section class="pa-panel"><div class="card"><h2>Prediction Accuracy · model audit</h2>'
            '<p class="card-description">Every prediction is frozen before the official gameweek deadline. '
            'Live and post-match revisions are excluded; draws count as their own outcome. '
            'Early samples may be noisy and this report does not imply predictive certainty.</p>'
            + body + '</div></section>')

PREDICTION_ACCURACY_CSS = '''
.pa-panel{margin:0 0 24px}.pa-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(165px,1fr));gap:12px;margin:16px 0 24px}
.pa-metric{border:1px solid var(--border);background:var(--bg-secondary);border-radius:12px;padding:14px;display:flex;flex-direction:column;gap:6px}
.pa-metric span{font-size:12px;color:var(--muted)}.pa-metric strong{font-size:24px}.pa-metric small{font-size:11px;color:var(--muted)}
.pa-cal-row{display:grid;grid-template-columns:130px minmax(80px,1fr) 190px;gap:10px;align-items:center;margin:10px 0;font-size:12px}
.pa-track{background:var(--bg-secondary);height:22px;position:relative;border-radius:4px;overflow:hidden}
.pa-track i{display:block;height:9px;background:#60a5fa;position:absolute;top:1px;left:0}.pa-track b{display:block;height:9px;background:#23bd86;position:absolute;bottom:1px;left:0}
@media(max-width:720px){.pa-cal-row{grid-template-columns:1fr}.pa-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
'''
