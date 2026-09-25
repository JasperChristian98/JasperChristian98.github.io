"""Offline regression tests for the manager styles comparison page."""
import unittest

from mcdraft.manager_styles_page import build_manager_styles, PAGE_HTML, CSS, javascript_with_data


class ManagerStylesPageTests(unittest.TestCase):
    def setUp(self):
        self.profiles = {
            'Alpha': {'tags':[{'name':'Waiver Hawk','description':'Busy'}], 'activity_per_gw':2.0, 'pickups':4, 'trades':1, 'efficiency':93, 'bench_per_gw':3.2, 'volatility':7.0, 'recent_avg':58.0},
            'Beta': {'tags':[{'name':'Diamond Hands','description':'Still'}], 'activity_per_gw':0.2, 'pickups':0, 'trades':0, 'efficiency':88, 'bench_per_gw':9.1, 'volatility':13.0, 'recent_avg':42.0},
            'Gamma': {'tags':[], 'activity_per_gw':1.1, 'pickups':2, 'trades':3, 'efficiency':91, 'bench_per_gw':5.0, 'volatility':9.5, 'recent_avg':51.0},
        }

    def test_build_manager_styles_orders_by_position_and_shapes_cards(self):
        data = build_manager_styles(['Beta','Gamma','Alpha'], self.profiles.__getitem__, positions={'Alpha':1,'Gamma':2,'Beta':3})
        self.assertEqual([row['manager'] for row in data['managers']], ['Alpha','Gamma','Beta'])
        self.assertEqual(len(data['axes']), 6)
        self.assertEqual(len(data['managers'][0]['scores']), 6)
        self.assertIn('headline', data['managers'][0])
        self.assertEqual(data['managers'][0]['position'], 1)

    def test_normalised_axes_span_range(self):
        data = build_manager_styles(['Alpha','Beta'], self.profiles.__getitem__)
        alpha = next(row for row in data['managers'] if row['manager'] == 'Alpha')
        beta = next(row for row in data['managers'] if row['manager'] == 'Beta')
        self.assertGreater(alpha['score_map']['activity'], beta['score_map']['activity'])
        self.assertGreater(alpha['score_map']['bench_control'], beta['score_map']['bench_control'])
        self.assertGreater(alpha['score_map']['stability'], beta['score_map']['stability'])

    def test_static_assets_reference_page(self):
        self.assertIn('page-manager-styles', PAGE_HTML)
        self.assertIn('manager-styles-grid', PAGE_HTML)
        self.assertIn('manager-style-card', CSS)
        js = javascript_with_data(build_manager_styles(['Alpha'], self.profiles.__getitem__))
        self.assertIn('renderManagerStyles', js)
        self.assertIn('MANAGER_STYLES_DATA', js)


if __name__ == '__main__':
    unittest.main()
