import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "discovery_candidate_v1.schema.json"


class DiscoveryPromotionGateTests(unittest.TestCase):
    def test_proven_reusable_has_fail_closed_schema_gate(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        gates = schema.get("allOf", [])
        proven = [
            gate for gate in gates
            if gate.get("if", {}).get("properties", {}).get("status", {}).get("const")
            == "PROVEN_REUSABLE"
        ]
        self.assertEqual(
            1,
            len(proven),
            "PROVEN_REUSABLE must have an explicit conditional evidence gate",
        )
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


if __name__ == "__main__":
    unittest.main()
