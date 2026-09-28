import unittest
from mcdraft.watchlist import integrate_template


class WatchlistTests(unittest.TestCase):
    def test_build_integration(self):
        source='''<body><button type="button" class="analytics-subtab player-page-tab" onclick="showPlayerSubtab('directory',this)">Player Directory</button><div class="player-subpage" id="player-sub-directory"></div></body>'''
        result=integrate_template(source)
        self.assertEqual(result.count('id="player-sub-watchlist"'),1)
        self.assertIn('assets/watchlist.js',result)
        with self.assertRaises(RuntimeError):
            integrate_template(result)
