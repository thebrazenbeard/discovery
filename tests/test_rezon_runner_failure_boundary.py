from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "candidates" / "REZON_RUNNER_BOUNDARY_V1.json"
RESULT = ROOT / "experiments" / "REZON_RUNNER_BOUNDARY_FAILURE_RESULT_V1.json"


class RezonRunnerFailureBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
        self.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_success_and_failure_share_unchanged_verifier(self):
        runner = self.result["runner"]
        self.assertFalse(runner["verifier_changed_from_success_path"])
        self.assertEqual(
            runner["verifier_git_blob_sha1"],
            "d7827dec743e69fff7f981d91d7a86f6cd4a4839",
        )
        self.assertEqual(runner["hosted_result"], "SUCCESS")
        self.assertEqual(runner["tests"], "228/228 PASS")

    def test_real_failure_is_bound_on_both_receipt_and_trace(self):
        rezon = self.result["rezon"]
        self.assertEqual(rezon["effect_state"], "plan")
        self.assertEqual(rezon["receipt_failures"], ["contract_violation"])
        self.assertEqual(rezon["trace_failures"], ["contract_violation"])
        self.assertEqual(rezon["output_bindings"], 0)
        self.assertEqual(rezon["producer_bindings"], 0)

    def test_failure_ontology_is_not_claimed_shared(self):
        self.assertIn("SHARED_FAILURE_ONTOLOGY", self.result["not_established"])
        self.assertIn(
            "RUNNER_CHECKS_FAILURE_COVERAGE_NOT_FAILURE_ONTOLOGY",
            self.result["established"],
        )

    def test_candidate_remains_experimenting(self):
        self.assertEqual(self.candidate["status"], "EXPERIMENTING")
        self.assertIn("PROVEN_REUSABLE", self.result["not_established"])

    def test_pair_is_paused_after_core_falsifier(self):
        self.assertEqual(
            self.result["disposition"],
            "PAUSE_REZON_RUNNER_EXPANSION_PENDING_SECOND_INDEPENDENT_CONSUMER_OR_MEASURED_MAINTENANCE_BENEFIT",
        )


if __name__ == "__main__":
    unittest.main()
