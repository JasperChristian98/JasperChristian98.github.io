import json
import unittest
from mcdraft.decision_centre import make_decisions, javascript_with_data, DECISION_CENTRE_HTML


class DecisionCentreTest(unittest.TestCase):
    def setUp(self):
        self.planner = {'A': {'weeks': [
            {'gw': 6, 'opponent': 'B', 'xi': 50, 'starters': [{'id': 1}], 'bench': []},
            {'gw': 7, 'opponent': 'B', 'xi': 41, 'starters': [], 'bench': []}],
            'suggestions': [{'id': 4, 'name': 'Four', 'drop_id': 3, 'drop_name': 'Three', 'gain': 9}]}}
        self.room = {'A': {'opponent': 'B', 'you': {'flags': [
            {'id': 1, 'name': 'One', 'availability': .5},
            {'id': 2, 'name': 'Two', 'availability': .1}]},
            'upgrades': [{'in_id': 4, 'in_name': 'Four', 'out_id': 3, 'out_name': 'Three', 'gain': 3.2}],
            'positional': [{'position': 'DEF', 'edge': -3}]}}

    def test_prioritises_starter_flags_not_bench(self):
        items = make_decisions(self.planner, self.room)['A']['items']
        self.assertEqual(items[0]['kind'], 'availability')
        self.assertIn('One', items[0]['title'])
        self.assertFalse(any('Two' in c['title'] for c in items))

    def test_deduplicates_identical_waiver(self):
        items = make_decisions(self.planner, self.room)['A']['items']
        self.assertEqual(sum(c['kind'] == 'waiver' for c in items), 1)
        self.assertFalse(any(c['kind'] == 'planning' and 'Four' in c['title'] for c in items))
        self.assertTrue(any(c['kind'] == 'planning' and 'GW7' in c['title'] for c in items))

    def test_unavailable_schedule_and_html(self):
        self.assertEqual(make_decisions({'A': {'weeks': []}}, {})['A']['items'], [])
        self.assertIn('id="decision-centre"', DECISION_CENTRE_HTML)

    def test_script_escapes_untrusted_player_names(self):
        js = javascript_with_data({'evil': {'message': '</script><script>alert(1)</script>'}})
        self.assertNotIn('</script>', js)
        self.assertIn('\\u003c/script', js)

    def test_output_json_serialisable(self):
        json.dumps(make_decisions(self.planner, self.room))

if __name__ == '__main__':
    unittest.main()
