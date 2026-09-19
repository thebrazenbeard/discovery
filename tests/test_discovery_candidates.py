from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_candidates", ROOT / "tools" / "validate_candidates.py"
)
module = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)


def load_candidate(name: str) -> dict:
    return json.loads((ROOT / "candidates" / name).read_text(encoding="utf-8"))


class DiscoveryCandidateValidationTests(unittest.TestCase):
    def test_current_hypotheses_are_valid(self):
        for path in sorted((ROOT / "candidates").glob("*.json")):
            with self.subTest(path=path.name):
                candidate = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual([], module.validate_candidate(candidate))

    def test_schema_contains_active_and_proven_lifecycle_gates(self):
        schema = json.loads(
            (ROOT / "schemas" / "discovery_candidate_v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        gates = schema.get("allOf", [])
        self.assertEqual(2, len(gates))
        active = gates[0]["then"]["properties"]
        self.assertEqual(1, active["promotion_evidence"]["minItems"])
        self.assertEqual(
            ["FAIL", "PASS_WITH_LIMITS", "PASS"],
            active["hostile_review"]["properties"]["status"]["enum"],
        )
        proven = gates[1]["then"]["properties"]
        self.assertEqual(2, proven["promotion_evidence"]["minItems"])
        self.assertEqual(
            "PASS",
            proven["hostile_review"]["properties"]["status"]["const"],
        )
        self.assertEqual(
            0,
            proven["hostile_review"]["properties"]["critical_objections"]["maxItems"],
        )

    def test_proven_reusable_cannot_be_self_promoted_without_evidence(self):
        candidate = load_candidate("REZON_RUNNER_BOUNDARY_V1.json")
        candidate["status"] = "PROVEN_REUSABLE"
        failures = module.validate_candidate(candidate)
        self.assertIn("ACTIVE_CONSUMER_REF_NOT_EXACT:0", failures)
        self.assertIn("ACTIVE_CONSUMER_REF_NOT_EXACT:1", failures)
        self.assertIn("ACTIVE_PROMOTION_EVIDENCE_REQUIRED", failures)
        self.assertIn("PROVEN_HOSTILE_PASS_REQUIRED", failures)

    def test_placeholder_consumer_cannot_become_active(self):
        candidate = load_candidate("LANTERN_EVIDENCE_INTERCHANGE_V1.json")
        candidate["status"] = "EXPERIMENTING"
        candidate["promotion_evidence"] = ["experiment-subject"]
        candidate["hostile_review"]["status"] = "FAIL"
        candidate["consumers"][0]["ref"] = "a" * 40
        candidate["consumers"][1]["ref"] = "b" * 40
        failures = module.validate_candidate(candidate)
        self.assertIn("ACTIVE_CONSUMER_PLACEHOLDER:1", failures)

    def test_proven_requires_distinct_real_consumers_and_clean_hostile_pass(self):
        candidate = load_candidate("REZON_RUNNER_BOUNDARY_V1.json")
        candidate["status"] = "PROVEN_REUSABLE"
        candidate["consumers"][0]["ref"] = "a" * 40
        candidate["consumers"][1]["ref"] = "b" * 40
        candidate["promotion_evidence"] = ["integration-a", "integration-b"]
        candidate["hostile_review"] = {
            "status": "PASS",
            "critical_objections": [],
        }
        self.assertEqual([], module.validate_candidate(candidate))

        duplicate = copy.deepcopy(candidate)
        duplicate["consumers"][1]["repo"] = duplicate["consumers"][0]["repo"]
        failures = module.validate_candidate(duplicate)
        self.assertIn("CONSUMER_REPOSITORIES_NOT_DISTINCT", failures)
        self.assertIn("PROVEN_TWO_REAL_CONSUMERS_REQUIRED", failures)

    def test_pass_with_limits_cannot_be_promoted_as_proven(self):
        candidate = load_candidate("REZON_RUNNER_BOUNDARY_V1.json")
        candidate["status"] = "PROVEN_REUSABLE"
        for index, consumer in enumerate(candidate["consumers"]):
            consumer["ref"] = str(index + 1) * 40
        candidate["promotion_evidence"] = ["integration-a", "integration-b"]
        candidate["hostile_review"] = {
            "status": "PASS_WITH_LIMITS",
            "critical_objections": ["unresolved coupling"],
        }
        failures = module.validate_candidate(candidate)
        self.assertIn("PROVEN_HOSTILE_PASS_REQUIRED", failures)
        self.assertIn("PROVEN_UNRESOLVED_CRITICAL_OBJECTIONS", failures)


if __name__ == "__main__":
    unittest.main()
