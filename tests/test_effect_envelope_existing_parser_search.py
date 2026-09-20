from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "experiments"
    / "EFFECT_ENVELOPE_EXISTING_PARSER_REPLACEMENT_SEARCH_V1.json"
)
CANDIDATE = ROOT / "candidates" / "RUNNER_WIP_EXECUTION_INTEGRITY_V1.json"


class ExistingParserReplacementSearchTests(unittest.TestCase):
    def setUp(self):
        self.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_no_replacement_target_is_claimed(self):
        result = self.result["result"]
        self.assertFalse(result["actual_parser_replacement_target_exists"])
        self.assertEqual(result["actual_removable_parser_lines_identified"], 0)
        self.assertFalse(result["additional_centralization_authorized_by_evidence"])

    def test_native_authority_candidates_are_rejected(self):
        rows = {row["candidate"]: row for row in self.result["examined_candidates"]}
        self.assertEqual(
            rows["Project Runner recovery"]["disposition"],
            "REJECT_NATIVE_AUTHORITY",
        )
        self.assertEqual(
            rows["BT2 BugOps operation lifecycle"]["disposition"],
            "REJECT_NATIVE_AUTHORITY",
        )

    def test_projection_currentness_is_not_laundered_into_effect_parsing(self):
        rows = {row["candidate"]: row for row in self.result["examined_candidates"]}
        self.assertEqual(
            rows["Radar operator GitHub/provider reconciliation"]["disposition"],
            "REJECT_DIFFERENT_SEMANTIC_DOMAIN",
        )
        self.assertEqual(
            rows["Vera provider/currentness reconciliation and audit"]["disposition"],
            "REJECT_DIFFERENT_SEMANTIC_DOMAIN",
        )

    def test_disposition_stops_further_centralization(self):
        self.assertEqual(
            self.result["result"]["disposition"],
            "STOP_EFFECT_ENVELOPE_CENTRALIZATION_PENDING_ORGANIC_REPLACEMENT_TARGET",
        )
        self.assertEqual(self.result["result"]["candidate_status"], "EXPERIMENTING")
        self.assertEqual(self.result["result"]["proven_reusable"], "NOT_ESTABLISHED")
        self.assertEqual(self.result["result"]["shared_runtime_library"], "NOT_JUSTIFIED")

    def test_candidate_keeps_experimenting_ceiling(self):
        candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
        self.assertEqual(candidate["status"], "EXPERIMENTING")
        self.assertTrue(
            any(
                "NO_CURRENT_EXISTING_PARSER_REPLACEMENT_TARGET" in note
                for note in candidate["notes"]
            )
        )


if __name__ == "__main__":
    unittest.main()
