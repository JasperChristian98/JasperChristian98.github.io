"""Regression tests for side-by-side mobile controls and header kickoff timer."""
from datetime import datetime, timezone
import unittest
from mcdraft.mobile_header_and_war_countdown import (
    CSS, HEADER_COUNTDOWN_HTML, countdown_javascript,
    insert_header_countdown, next_gameweek_kickoff,
)

META = '''            <div class="header-meta">

                Last updated:
                __LAST_UPDATED__

                <br>

                __FINISHED_COUNT__
                completed gameweeks

            </div>'''

class CompactHeaderCountdownTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 25, 12, tzinfo=timezone.utc)
        self.fixtures = [
            {'event': 6, 'kickoff_time': '2026-09-26T14:00:00Z'},
            {'event': 6, 'kickoff_time': '2026-09-26T11:30:00Z'},
            {'event': 7, 'kickoff_time': '2026-10-03T14:00:00Z'},
        ]

    def test_next_gw_uses_earliest_kickoff(self):
        result = next_gameweek_kickoff(self.fixtures, current_gw=6, live=False, now=self.now)
        self.assertEqual(result['gw'], 6)
        self.assertEqual(result['kickoff'], '2026-09-26T11:30:00Z')
        self.assertFalse(result['live'])

    def test_live_week_flags_countdown_as_hidden(self):
        result = next_gameweek_kickoff(self.fixtures, current_gw=6, live=True, now=self.now)
        self.assertTrue(result['live'])
        self.assertEqual(result['gw'], 7)
        self.assertEqual(result['kickoff'], '2026-10-03T14:00:00Z')
        html = insert_header_countdown(META, live=True)
        self.assertNotIn('id="mcd-kickoff-countdown"', html)
        self.assertIn('__LAST_UPDATED__', html)

    def test_missing_kickoff_is_tbc(self):
        result = next_gameweek_kickoff([{'event': 6, 'kickoff_time': None}],
                                       current_gw=6, live=False, now=self.now)
        self.assertIsNone(result['kickoff'])
        self.assertIn('Date TBC', countdown_javascript(result))

    def test_insert_once_next_to_last_updated(self):
        template = '<div class="header-top">' + META + '</div>'
        result = insert_header_countdown(template)
        self.assertEqual(result.count('id="mcd-kickoff-countdown"'), 1)
        self.assertIn('mcd-updated-info', result)
        self.assertLess(result.index('__LAST_UPDATED__'), result.index('mcd-kickoff-countdown'))
        with self.assertRaises(RuntimeError):
            insert_header_countdown(result)
        with self.assertRaises(RuntimeError):
            insert_header_countdown('')

    def test_grid_places_search_and_manager_on_same_row(self):
        self.assertIn('display:grid!important', CSS)
        self.assertIn('"search manager"', CSS)
        self.assertIn('grid-area:search', CSS)
        self.assertIn('grid-area:manager', CSS)
        self.assertIn('flex-direction:row!important', CSS)
        self.assertIn('mcd-kickoff-countdown', CSS)

    def test_timer_hides_when_live_or_kickoff_passes(self):
        js=countdown_javascript({'gw':6,'kickoff':'2026-09-26T11:30:00Z','live':False})
        self.assertIn('Date.now()', js)
        self.assertIn('setInterval', js)
        self.assertIn('info.live', js)
        self.assertIn('ms<=0', js)
        self.assertIn('HEADER_KICKOFF', js)
        self.assertIn('NEXT KICKOFF', HEADER_COUNTDOWN_HTML)

if __name__=='__main__': unittest.main()
