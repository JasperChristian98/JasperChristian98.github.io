import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from mcdraft.prediction_accuracy import capture_forecast, evaluate, read_store, atomic_save, render_report


class PredictionAccuracyTests(unittest.TestCase):
    def setUp(self):
        self.store = {'schema_version': 1, 'gameweeks': {}}
        self.now = datetime(2026,9,25,9,0,tzinfo=timezone.utc)
        self.fixture = [{'team1':'A','team2':'B','finished':False}]
        self.odds = {'team1_win':60,'draw':5,'team2_win':35,'team1_mean':54,
                     'team2_mean':45,'team1_low':33,'team1_high':68,
                     'team2_low':30,'team2_high':60}

    def capture(self, **overrides):
        args = dict(gw=6,deadline=self.now+timedelta(hours=1),now=self.now,
                    started=False,fixtures=self.fixture,forecast=lambda a,b:self.odds)
        args.update(overrides)
        return capture_forecast(self.store,**args)

    def test_capture_only_once_and_no_leakage(self):
        self.assertTrue(self.capture())
        original = self.store['gameweeks']['6']['fixtures'][0]['team1_mean']
        self.odds['team1_mean'] = 99
        self.assertFalse(self.capture())
        self.assertEqual(original, 54)

    def test_no_postdeadline_or_live_capture(self):
        self.assertFalse(self.capture(now=self.now+timedelta(hours=2)))
        self.assertFalse(self.capture(started=True))
        self.assertFalse(self.capture(deadline=None))
        self.assertEqual(self.store['gameweeks'], {})

    def test_metrics_and_unmatched_results(self):
        self.assertTrue(self.capture())
        report = evaluate(self.store,[{'event':6,'entry_1_name':'A', 'entry_2_name':'B',
                                     'entry_1_points':56,'entry_2_points':42}])
        self.assertEqual(report['summary']['matches'],1)
        self.assertEqual(report['summary']['prediction_accuracy'],1)
        self.assertAlmostEqual(report['summary']['score_mae'],2.5)
        self.assertAlmostEqual(report['summary']['brier'],.285)
        self.assertEqual(report['summary']['interval_coverage'],1)
        self.assertEqual(len(evaluate(self.store,[])['rows']),0)

    def test_reverse_fixture_and_html_escapes(self):
        self.fixture[0]['team1'] = '<script>'
        self.assertTrue(self.capture())
        report = evaluate(self.store,[{'event':6,'entry_1_name':'B','entry_2_name':'<script>',
                                      'entry_1_points':42,'entry_2_points':56}])
        self.assertEqual(len(report['rows']),1)
        self.assertNotIn('<script>',render_report(report))
        self.assertIn('&lt;script&gt;',render_report(report))

    def test_persistence(self):
        self.assertTrue(self.capture())
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'mcdraft_prediction_history.json'
            atomic_save(path,self.store)
            self.assertEqual(read_store(path),self.store)

    def test_empty_report(self):
        self.assertIn('No completed matches',render_report(evaluate(self.store,[])))

if __name__=='__main__': unittest.main()
