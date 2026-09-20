from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "candidates" / "REZON_RUNNER_BOUNDARY_V1.json"
RESULT = ROOT / "experiments" / "REZON_RUNNER_BOUNDARY_RESULT_V1.json"


class RezonRunnerBoundaryDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
        self.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_candidate_is_experimenting_not_proven_reusable(self):
        self.assertEqual(self.candidate["status"], "EXPERIMENTING")
        self.assertIn("PROVEN_REUSABLE", self.result["not_established"])
        self.assertTrue(
            self.result["claim_ceiling"].endswith("NOT_PROVEN_REUSABLE")
        )

    def test_exact_producer_and_runner_heads_are_bound(self):
        self.assertEqual(
            self.result["rezon"]["exact_head"],
            "8289914ec500a1392b10fe1a3774dee166e73b40",
        )
        self.assertEqual(
            self.result["runner"]["exact_head"],
            "4de0f6148b3d7d04ccdb4e0057435fa0d904590a",
        )
        self.assertEqual(self.result["runner"]["hosted_result"], "SUCCESS")

    def test_evidence_classes_are_not_laundered(self):
        self.assertEqual(
            self.result["rezon"]["hosted_ci"],
            "NOT_PRESENT_ON_EXACT_FINAL_HEAD",
        )
        self.assertEqual(
            self.result["rezon"]["fresh_local_exact_source"]["full_tests"],
            "275/275 PASS",
        )
        self.assertEqual(
            self.result["runner"]["tests"],
            "222/222 PASS",
        )

    def test_epistemic_authority_is_explicitly_not_established(self):
        missing = set(self.result["not_established"])
        self.assertTrue(
            {
                "REZON_TRUTH",
                "REZON_ADMISSION",
                "REZON_QUALIFICATION",
                "REZON_AUTHORITY",
                "RUNNER_AUTHORITY_OVER_REZON",
                "EXTERNAL_EFFECT_AUTHORIZATION",
            } <= missing
        )

    def test_transport_normalization_is_explicit(self):
        fixture = self.result["real_fixture"]
        self.assertEqual(
            fixture["transport_normalization"],
            "CRLF_TO_LF_ONLY",
        )
        self.assertNotEqual(
            fixture["source_generated_sha256_windows_crlf"],
            fixture["persisted_fixture_sha256_lf"],
        )

    def test_failed_runner_predecessors_are_preserved(self):
        failures = self.result["failed_predecessor_provenance"]
        self.assertEqual(len(failures), 2)
        self.assertEqual(
            {row["head"] for row in failures},
            {
                "41ffcde85ba49c86d7f70375b694011e64151c49",
                "d000cfd39f1cf74c7a911cf08928f0d29ab4d6aa",
            },
        )


if __name__ == "__main__":
    unittest.main()
