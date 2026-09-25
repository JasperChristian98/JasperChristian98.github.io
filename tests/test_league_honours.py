import unittest
from mcdraft.league_honours import build_honours, render_awards, render_records, extra_manager_tags


def squad(manager, points, bench=0):
    return {'manager': manager, 'gw_points': points, 'bench_points': bench}


def match(gw, a, b, pa, pb):
    return {'event': gw, 'entry_1_name': a, 'entry_2_name': b,
            'entry_1_points': pa, 'entry_2_points': pb}


class HonoursTests(unittest.TestCase):
    def setUp(self):
        self.names = ['A', 'B', 'C', 'D']
        self.history = {'gameweeks': {
            '1': {'finished': True, 'teams': {
                'a': squad('A', 30, 3), 'b': squad('B', 55, 9),
                'c': squad('C', 60, 14), 'd': squad('D', 40, 2)}},
            '2': {'finished': True, 'teams': {
                'a': squad('A', 75, 19), 'b': squad('B', 50, 4),
                'c': squad('C', 30, 7), 'd': squad('D', 25, 8)}},
            '3': {'finished': False, 'teams': {
                'a': squad('A', 110, 44), 'b': squad('B', 0),
                'c': squad('C', 0), 'd': squad('D', 0)}}}}
        self.matches = [match(1, 'A', 'B', 30, 55), match(1, 'C', 'D', 60, 40),
                        match(2, 'A', 'C', 75, 30), match(2, 'B', 'D', 50, 25)]

    def test_weekly_improver_and_form_rocket_are_different(self):
        result = build_honours(self.history, self.matches, self.names)
        second = {a['label']: a for a in result['weeks'][1]['awards']}
        self.assertIn('🚀 Improver of the Week', second)
        self.assertIn('A', second['🚀 Improver of the Week']['managers'])
        self.assertEqual(second['📈 Form Rocket']['managers'], ['A'])
        self.assertIn('+45', second['📈 Form Rocket']['detail'])

    def test_no_live_values_enter_records(self):
        result = build_honours(self.history, self.matches, self.names)
        self.assertEqual(result['records']['high_score']['value'], 75)
        self.assertEqual(len(result['weeks']), 2)

    def test_ties_share_weekly_awards(self):
        self.matches[2] = match(2, 'A', 'C', 75, 75)
        self.matches[3] = match(2, 'B', 'D', 75, 25)
        result = build_honours(self.history, self.matches, self.names)
        best = [a for a in result['weeks'][1]['awards'] if 'Top of the Pops' in a['label']][0]
        self.assertEqual(best['managers'], ['A', 'B', 'C'])

    def test_escaped_user_supplied_names(self):
        name = '<script>x</script>'
        h = {'gameweeks': {'1': {'finished': True, 'teams': {'a': squad(name, 55), 'b': squad('B', 24)}}}}
        result = build_honours(h, [match(1, name, 'B', 55, 24)], [name, 'B'])
        html = render_awards(result) + render_records(result)
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)

    def test_no_premature_accolades_or_manager_tags(self):
        result = build_honours({'gameweeks': {}}, [], self.names)
        self.assertEqual(result['weeks'], [])
        self.assertEqual(extra_manager_tags(result, 'A'), [])
        self.assertIn('unlock', render_awards(result))


if __name__ == '__main__':
    unittest.main()
