import copy
import json
import unittest
from pathlib import Path

from tools.validate_candidates import validate_candidate


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "discovery_candidate_v1.schema.json"


def proven_candidate():
    return {
        "schema_version": "DISCOVERY_CANDIDATE_V1",
        "candidate_id": "TEST_REUSE_V1",
        "title": "test",
        "status": "PROVEN_REUSABLE",
        "claim": "bounded reuse",
        "consumers": [
            {"repo": "thebrazenbeard/a", "role": "one", "ref": "a" * 40},
            {"repo": "thebrazenbeard/b", "role": "two", "ref": "b" * 40},
        ],
        "preserved_boundaries": ["semantics remain local"],
        "promotion_evidence": ["integration:a", "integration:b"],
        "rejection_conditions": ["rollback failure"],
        "hostile_review": {"status": "PASS", "critical_objections": []},
    }


class DiscoveryPromotionGateTests(unittest.TestCase):
    def test_schema_has_explicit_proven_reusable_gate(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        proven = [
            gate for gate in schema.get("allOf", [])
            if gate.get("if", {}).get("properties", {}).get("status", {}).get("const")
            == "PROVEN_REUSABLE"
        ]
        self.assertEqual(1, len(proven))
        then = proven[0]["then"]["properties"]
        self.assertGreaterEqual(then["promotion_evidence"]["minItems"], 2)
        self.assertEqual(
            ["PASS", "PASS_WITH_LIMITS"],
            then["hostile_review"]["properties"]["status"]["enum"],
        )
        self.assertEqual(
            0,
            then["hostile_review"]["properties"]["critical_objections"]["maxItems"],
        )
        self.assertEqual(
            "^[0-9a-f]{40}$",
            then["consumers"]["items"]["properties"]["ref"]["pattern"],
        )

    def test_valid_proven_reusable_passes_runtime_gate(self):
        self.assertEqual([], validate_candidate(proven_candidate()))

    def test_unreviewed_reusable_candidate_fails(self):
        candidate = proven_candidate()
        candidate["hostile_review"] = {
            "status": "NOT_RUN",
            "critical_objections": [],
        }
        self.assertIn(
            "proven_hostile_review_not_passed",
            validate_candidate(candidate),
        )

    def test_reusable_candidate_requires_exact_consumer_refs(self):
        candidate = proven_candidate()
        candidate["consumers"][0]["ref"] = None
        self.assertIn(
            "proven_consumer_ref_not_exact:0",
            validate_candidate(candidate),
        )

    def test_reusable_candidate_requires_real_distinct_consumers(self):
        candidate = proven_candidate()
        candidate["consumers"][1]["repo"] = candidate["consumers"][0]["repo"]
        self.assertIn(
            "proven_consumers_not_materially_distinct",
            validate_candidate(candidate),
        )
        candidate = proven_candidate()
        candidate["consumers"][1]["repo"] = "TBD_SECOND_CONSUMER"
        self.assertIn(
            "proven_consumer_not_real:1",
            validate_candidate(candidate),
        )

    def test_reusable_candidate_requires_promotion_evidence(self):
        candidate = proven_candidate()
        candidate["promotion_evidence"] = []
        self.assertIn(
            "proven_promotion_evidence_insufficient",
            validate_candidate(candidate),
        )

    def test_reusable_candidate_cannot_keep_critical_objections(self):
        candidate = proven_candidate()
        candidate["hostile_review"]["status"] = "PASS_WITH_LIMITS"
        candidate["hostile_review"]["critical_objections"] = ["single point of failure"]
        self.assertIn(
            "proven_unresolved_critical_objections",
            validate_candidate(candidate),
        )


if __name__ == "__main__":
    unittest.main()
