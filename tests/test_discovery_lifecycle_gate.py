from __future__ import annotations

import copy
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_discovery", ROOT / "tools" / "validate_discovery.py"
)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(validator)


def load_candidate(name: str) -> dict:
    return json.loads((ROOT / "candidates" / name).read_text(encoding="utf-8"))


def proven_candidate() -> dict:
    candidate = load_candidate("RUNNER_WIP_EXECUTION_INTEGRITY_V1.json")
    candidate["status"] = "PROVEN_REUSABLE"
    candidate["hostile_review"] = {"status": "PASS", "critical_objections": []}
    return candidate


class DiscoveryLifecycleGateTests(unittest.TestCase):
    def test_current_discovery_source_validates(self):
        self.assertEqual([], validator.validate())

    def test_current_experiment_accepts_refname_at_exact_sha(self):
        candidate = load_candidate("RUNNER_WIP_EXECUTION_INTEGRITY_V1.json")
        self.assertEqual(
            [],
            validator._validate_candidate_lifecycle(
                candidate,
                filename="RUNNER_WIP_EXECUTION_INTEGRITY_V1.json",
            ),
        )

    def test_bare_exact_sha_is_also_an_exact_subject(self):
        candidate = load_candidate("RUNNER_WIP_EXECUTION_INTEGRITY_V1.json")
        candidate["consumers"][0]["ref"] = "a" * 40
        failures = validator._validate_candidate_lifecycle(
            candidate,
            filename="synthetic.json",
        )
        self.assertNotIn(
            "active candidate consumer ref not exact: synthetic.json:0",
            failures,
        )

    def test_active_candidate_rejects_null_and_placeholder_consumer(self):
        candidate = load_candidate("RUNNER_WIP_EXECUTION_INTEGRITY_V1.json")
        candidate["consumers"][0]["ref"] = None
        candidate["consumers"][1]["repo"] = "TBD_SECOND_CONSUMER"
        failures = validator._validate_candidate_lifecycle(
            candidate,
            filename="synthetic.json",
        )
        self.assertIn(
            "active candidate consumer ref not exact: synthetic.json:0",
            failures,
        )
        self.assertIn(
            "active candidate consumer is placeholder: synthetic.json:1",
            failures,
        )

    def test_experimenting_accepts_digest_bound_private_opaque_consumer(self):
        candidate = load_candidate("RUNNER_WIP_EXECUTION_INTEGRITY_V1.json")
        candidate["consumers"][1] = {
            "repo": "PRIVATE_OPAQUE_ALPHA",
            "role": "private experimental consumer",
            "ref": None,
            "visibility": "PRIVATE_OPAQUE",
            "private_attestation": {
                "schema": "DISCOVERY_PRIVATE_SUBJECT_ATTESTATION_V1",
                "consumer_commitment_sha256": "1" * 64,
                "subject_commitment_sha256": "2" * 64,
                "receipt_sha256": "3" * 64,
                "verifier_class": "PRIVATE_OWNER_REGISTRY",
                "status": "EXACT_PRIVATE_SUBJECT_ATTESTED",
            },
        }
        self.assertEqual(
            [],
            validator._validate_candidate_lifecycle(
                candidate,
                filename="synthetic-private.json",
            ),
        )

    def test_active_private_consumer_rejects_raw_ref_and_malformed_attestation(self):
        candidate = load_candidate("RUNNER_WIP_EXECUTION_INTEGRITY_V1.json")
        candidate["consumers"][1] = {
            "repo": "PRIVATE_OPAQUE_ALPHA",
            "role": "private experimental consumer",
            "ref": "main@" + "a" * 40,
            "visibility": "PRIVATE_OPAQUE",
            "private_attestation": {
                "schema": "DISCOVERY_PRIVATE_SUBJECT_ATTESTATION_V1",
                "consumer_commitment_sha256": "not-a-digest",
                "subject_commitment_sha256": "2" * 64,
                "receipt_sha256": "3" * 64,
                "verifier_class": "PRIVATE_OWNER_REGISTRY",
                "status": "EXACT_PRIVATE_SUBJECT_ATTESTED",
            },
        }
        failures = validator._validate_candidate_lifecycle(
            candidate,
            filename="synthetic-private.json",
        )
        self.assertIn(
            "private consumer raw ref forbidden: synthetic-private.json:1",
            failures,
        )
        self.assertIn(
            "private consumer consumer commitment invalid: synthetic-private.json:1",
            failures,
        )

    def test_private_consumer_distinctness_uses_consumer_commitment(self):
        candidate = load_candidate("RUNNER_WIP_EXECUTION_INTEGRITY_V1.json")
        attestation = {
            "schema": "DISCOVERY_PRIVATE_SUBJECT_ATTESTATION_V1",
            "consumer_commitment_sha256": "1" * 64,
            "subject_commitment_sha256": "2" * 64,
            "receipt_sha256": "3" * 64,
            "verifier_class": "PRIVATE_OWNER_REGISTRY",
            "status": "EXACT_PRIVATE_SUBJECT_ATTESTED",
        }
        candidate["consumers"] = [
            {
                "repo": "PRIVATE_OPAQUE_ALPHA",
                "role": "private consumer one",
                "ref": None,
                "visibility": "PRIVATE_OPAQUE",
                "private_attestation": copy.deepcopy(attestation),
            },
            {
                "repo": "PRIVATE_OPAQUE_BETA",
                "role": "private consumer two",
                "ref": None,
                "visibility": "PRIVATE_OPAQUE",
                "private_attestation": copy.deepcopy(attestation),
            },
        ]
        failures = validator._validate_candidate_lifecycle(
            candidate,
            filename="synthetic-private.json",
        )
        self.assertIn(
            "active candidate consumers not distinct: synthetic-private.json",
            failures,
        )

    def test_proven_reusable_rejects_opaque_private_consumer_for_now(self):
        candidate = proven_candidate()
        candidate["consumers"][1] = {
            "repo": "PRIVATE_OPAQUE_ALPHA",
            "role": "private experimental consumer",
            "ref": None,
            "visibility": "PRIVATE_OPAQUE",
            "private_attestation": {
                "schema": "DISCOVERY_PRIVATE_SUBJECT_ATTESTATION_V1",
                "consumer_commitment_sha256": "1" * 64,
                "subject_commitment_sha256": "2" * 64,
                "receipt_sha256": "3" * 64,
                "verifier_class": "INDEPENDENT_PRIVATE_REVIEWER",
                "status": "EXACT_PRIVATE_SUBJECT_ATTESTED",
            },
        }
        failures = validator._validate_candidate_lifecycle(
            candidate,
            filename="synthetic-private.json",
        )
        self.assertIn(
            "proven candidate cannot rely on opaque private consumer: synthetic-private.json",
            failures,
        )

    def test_experimenting_may_carry_pass_with_limits_and_objections(self):
        candidate = load_candidate("RUNNER_WIP_EXECUTION_INTEGRITY_V1.json")
        failures = validator._validate_candidate_lifecycle(
            candidate,
            filename="synthetic.json",
        )
        self.assertEqual([], failures)

    def test_proven_reusable_requires_clean_pass_and_no_objections(self):
        candidate = proven_candidate()
        self.assertEqual(
            [],
            validator._validate_candidate_lifecycle(
                candidate,
                filename="synthetic.json",
            ),
        )
        candidate["hostile_review"] = {
            "status": "PASS_WITH_LIMITS",
            "critical_objections": ["coupling remains"],
        }
        failures = validator._validate_candidate_lifecycle(
            candidate,
            filename="synthetic.json",
        )
        self.assertIn(
            "proven candidate hostile review not clean PASS: synthetic.json",
            failures,
        )
        self.assertIn(
            "proven candidate has critical objections: synthetic.json",
            failures,
        )

    def test_proven_reusable_requires_two_evidence_records(self):
        candidate = proven_candidate()
        candidate["promotion_evidence"] = candidate["promotion_evidence"][:1]
        failures = validator._validate_candidate_lifecycle(
            candidate,
            filename="synthetic.json",
        )
        self.assertIn(
            "proven candidate lacks independent evidence: synthetic.json",
            failures,
        )

    def test_schema_exact_subject_pattern_accepts_branch_ref_and_rejects_whitespace(self):
        schema = json.loads(
            (ROOT / "schemas" / "discovery_candidate_v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        active_item = schema["allOf"][0]["then"]["properties"]["consumers"]["items"][
            "allOf"
        ][0]
        pattern = active_item["else"]["properties"]["ref"]["pattern"]
        compiled = re.compile(pattern)
        self.assertIsNotNone(compiled.fullmatch("main@" + "a" * 40))
        self.assertIsNotNone(
            compiled.fullmatch("science/demography-v1@" + "b" * 40)
        )
        self.assertIsNone(compiled.fullmatch("bad ref@" + "c" * 40))

    def test_schema_has_active_and_proven_gates(self):
        schema = json.loads(
            (ROOT / "schemas" / "discovery_candidate_v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        gates = schema.get("allOf", [])
        self.assertEqual(2, len(gates))
        active = gates[0]["then"]["properties"]
        self.assertEqual(1, active["promotion_evidence"]["minItems"])
        proven = gates[1]["then"]["properties"]
        self.assertEqual(2, proven["promotion_evidence"]["minItems"])
        self.assertIn("not", proven["consumers"])
        self.assertEqual(
            "PASS",
            proven["hostile_review"]["properties"]["status"]["const"],
        )
        self.assertEqual(
            0,
            proven["hostile_review"]["properties"]["critical_objections"]["maxItems"],
        )


if __name__ == "__main__":
    unittest.main()
