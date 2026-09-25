"""Offline checks. Run: python -m unittest discover -s tests -v"""
import ast
import hashlib
import json
import unittest
from pathlib import Path

from mcdraft.pipeline import PACKAGE_DIR, stage_manifest, STAGES_DIR


class SourcePreservation(unittest.TestCase):
    def test_source_hash_and_line_contiguity(self):
        manifest = stage_manifest()
        stages = manifest["stages"]
        self.assertEqual(stages[0]["original_start"], 1)
        for left, right in zip(stages, stages[1:]):
            self.assertEqual(left["original_end"] + 1, right["original_start"])
        self.assertEqual(stages[-1]["original_end"], manifest["original_line_count"])
        combined = b"".join((STAGES_DIR / s["file"]).read_bytes() for s in stages)
        self.assertEqual(hashlib.sha256(combined).hexdigest(), manifest["source_sha256"])
        self.assertEqual(len(combined.decode().splitlines()), manifest["original_line_count"])

    def test_every_stage_parses(self):
        for stage in stage_manifest()["stages"]:
            p = STAGES_DIR / stage["file"]
            with self.subTest(stage=p.name):
                ast.parse(p.read_text(encoding="utf-8"), filename=str(p))

    def test_combined_code_parses(self):
        combined = "".join((STAGES_DIR / s["file"]).read_text(encoding="utf-8")
                           for s in stage_manifest()["stages"])
        ast.parse(combined)

    def test_required_features_retained(self):
        source = "".join((STAGES_DIR / s["file"]).read_text(encoding="utf-8")
                         for s in stage_manifest()["stages"])
        for feature in ("def build_mcdraft_cup(", "def _build_five_gw_planner(",
                        "def manager_war_room_html(", "def _waiver_intelligence_payload(",
                        "def analytics_page_html(", "def build_squad_vulnerability_data("):
            with self.subTest(feature=feature):
                self.assertIn(feature, source)


if __name__ == "__main__":
    unittest.main()
