import unittest
from pathlib import Path
from mcdraft.club_badges import integrate_template


class ClubBadgeTests(unittest.TestCase):
    def test_build_integration(self):
        result = integrate_template('<body></body>')
        self.assertEqual(result.count('assets/club-badges.js'), 1)
        self.assertIn('assets/club-badges.css', result)
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / 'assets/club-badges.js').is_file())
        with self.assertRaises(RuntimeError):
            integrate_template(result)
        with self.assertRaises(RuntimeError):
            integrate_template('')
