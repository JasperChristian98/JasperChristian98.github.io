"""Regression tests for compact mobile header and War Room kickoff countdown."""
from datetime import datetime, timezone
import unittest
from mcdraft.mobile_header_and_war_countdown import (
    CSS, WAR_ROOM_COUNTDOWN_HTML, countdown_javascript,
    insert_war_room_countdown, next_gameweek_kickoff,
)

class CompactHeaderAndWarRoomTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 25, 12, tzinfo=timezone.utc)
        self.fixtures = [
            {'event': 6, 'kickoff_time': '2026-09-26T14:00:00Z'},
            {'event': 6, 'kickoff_time': '2026-09-26T11:30:00Z'},
            {'event': 7, 'kickoff_time': '2026-10-03T14:00:00Z'},
        ]

    def test_next_gw_uses_first_kickoff_not_deadline(self):
        result = next_gameweek_kickoff(self.fixtures, current_gw=6, live=False, now=self.now)
        self.assertEqual(result['gw'], 6)
        self.assertEqual(result['kickoff'], '2026-09-26T11:30:00Z')

    def test_live_week_skips_remaining_games_in_current_week(self):
        result = next_gameweek_kickoff(self.fixtures, current_gw=6, live=True, now=self.now)
        self.assertEqual(result['gw'], 7)
        self.assertEqual(result['kickoff'], '2026-10-03T14:00:00Z')

    def test_missing_kickoff_is_tbc(self):
        result = next_gameweek_kickoff([{'event': 6, 'kickoff_time': None}],
                                       current_gw=6, live=False, now=self.now)
        self.assertEqual(result, {'gw': 6, 'kickoff': None})

    def test_insert_once_only_into_myteam(self):
        template = '<div class="myteam-subpage" id="myteam-sub-war-room"><div class="war-room-shell"></div></div>'
        result = insert_war_room_countdown(template)
        self.assertEqual(result.count('id="wr-next-gw-countdown"'), 1)
        self.assertLess(result.index('id="wr-next-gw-countdown"'),result.index('war-room-shell'))
        with self.assertRaises(RuntimeError):
            insert_war_room_countdown(result)
        with self.assertRaises(RuntimeError):
            insert_war_room_countdown('')

    def test_mobile_controls_share_row(self):
        self.assertIn('.header .global-search-wrap', CSS)
        self.assertIn('.header .mcd-header-manager', CSS)
        self.assertIn('order:10', CSS)
        self.assertIn('order:11', CSS)
        self.assertIn('flex:1 1 0', CSS)

    def test_countdown_is_built_from_fixture_data(self):
        js=countdown_javascript({'gw':6,'kickoff':'2026-09-26T11:30:00Z'})
        self.assertIn('2026-09-26T11:30:00Z',js)
        self.assertIn('Date.now()',js)
        self.assertIn('setInterval',js)
        self.assertIn('NEXT GAMEWEEK',WAR_ROOM_COUNTDOWN_HTML)

if __name__=='__main__':unittest.main()
