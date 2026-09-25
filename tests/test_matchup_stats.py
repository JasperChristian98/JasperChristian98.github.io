import unittest
from mcdraft.matchup_stats import build_stats, javascript_with_data


def fixture(a, b, pa, pb, gw=1, **extra):
    return dict(event=gw, entry_1_name=a, entry_2_name=b,
                entry_1_points=pa, entry_2_points=pb, **extra)


class MatchupStatsTests(unittest.TestCase):
    def setUp(self):
        self.history = {'gameweeks': {'1': {'finished': True, 'teams': {
            '1': {'manager': 'B', 'starters': [
                {'element_id': 7, 'web_name': 'Scorer', 'points': 12, 'position': 'MID'}],
                'bench': [{'element_id': 8, 'web_name': 'Benched', 'points': 20}]}}}},
            'matches': [fixture('A', 'B', 50, 60), fixture('C', 'D', 20, 30)]}

    def test_unlucky_loss_and_lucky_win(self):
        data = build_stats(self.history)
        game = data['A']['games'][0]
        self.assertEqual(game['actual'], 0)
        self.assertEqual(game['expected'], 2)
        self.assertEqual(game['luck'], -2)
        self.assertEqual(game['rank'], 2)
        self.assertEqual(game['all_play'], '2W 0D 1L')
        self.assertEqual(data['D']['games'][0]['luck'], 2)

    def test_only_opposing_starters_contribute(self):
        data = build_stats(self.history)
        self.assertEqual(len(data['A']['threats']), 1)
        self.assertEqual(data['A']['threats'][0]['points'], 12)
        self.assertEqual(data['B']['heroes'][0]['points'], 12)
        self.assertFalse(data['C']['games'][0]['lineup_available'])

    def test_draws_use_one_league_point_and_share_rank(self):
        self.history['matches'][0] = fixture('A', 'B', 30, 30)
        game = build_stats(self.history)['A']['games'][0]
        self.assertAlmostEqual(game['expected'], 5/3)
        self.assertAlmostEqual(game['luck'], 1-5/3)
        self.assertEqual(game['rank'], 1)

    def test_excludes_live_future_invalid_and_duplicate_matches(self):
        self.history['gameweeks']['2'] = {'finished': False, 'teams': {}}
        self.history['matches'] += [fixture('A', 'B', 999, 0, 2),
            fixture('A', 'B', 999, 0, 3), fixture('A', 'B', 50, 60),
            fixture('X', 'Y', 20, 0, finished=False), fixture('X', 'Y', 'bad', 1)]
        data = build_stats(self.history)
        self.assertEqual(len(data['A']['games']), 1)
        self.assertNotIn('X', data)

    def test_player_identity_survives_transfer_and_negative_haul(self):
        self.history['gameweeks']['2'] = {'finished': True, 'teams': {'2': {
            'manager': 'C', 'starters': [{'element_id': 7, 'web_name': 'Scorer', 'points': -2}]}}}
        self.history['matches'].append(fixture('A', 'C', 10, 9, 2))
        player = build_stats(self.history)['A']['threats'][0]
        self.assertEqual(player['points'], 10)
        self.assertEqual(player['appearances'], 2)
        self.assertEqual(player['peak'], 12)

    def test_empty_history_and_script_escape(self):
        self.assertEqual(build_stats({}), {})
        self.assertNotIn('</script>', javascript_with_data({'</script>': {}}))


if __name__ == '__main__':
    unittest.main()
