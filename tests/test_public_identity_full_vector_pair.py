"""B0/B1 full-vector comparison must reject attractive summary-only evidence."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "identity_vector_pair", ROOT / "tools" / "validate_public_identity_vector_pair.py"
)
assert spec is not None and spec.loader is not None
comparison = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparison)


def vector(observation_id: str, start: str, end: str) -> dict:
    return {
        "schema": "DISCOVERY_PUBLIC_IDENTITY_VECTOR_V1",
        "owner": "thebrazenbeard",
        "observation_id": observation_id,
        "started_at_utc": start,
        "ended_at_utc": end,
        "source_profile_sha256": "a" * 64,
        "errors": [],
        "subjects": [
            {"id": 12, "name": "alpha", "branch": "main", "head": "b" * 40,
             "tree": "c" * 40, "archived": False},
            {"id": 13, "name": "beta", "branch": "main", "head": "d" * 40,
             "tree": "e" * 40, "archived": True},
        ],
    }


class IdentityVectorPairTests(unittest.TestCase):
    def setUp(self):
        self.b0 = vector("b0", "2026-10-28T20:00:00Z", "2026-10-28T20:00:05Z")
        self.b1 = vector("b1", "2026-10-28T20:00:06Z", "2026-10-28T20:00:09Z")

    def test_exact_matching_vectors_still_not_admitted(self):
        outcome = comparison.compare_pair(self.b0, self.b1)
        self.assertEqual("PAIR_EQUIVALENCE_ONLY", outcome["status"])
        self.assertEqual(2, outcome["subjects"])
        self.assertEqual("NOT_ADMITTED", outcome["admission"])
        self.assertEqual("NOT_ATTESTED", outcome["independent_signer"])
        self.assertEqual("NOT_ATTESTED", outcome["reference_membership_binding"])

    def test_equal_truncated_vectors_dont_claim_completeness(self):
        b0 = copy.deepcopy(self.b0)
        b1 = copy.deepcopy(self.b1)
        b0["subjects"] = b0["subjects"][:1]
        b1["subjects"] = b1["subjects"][:1]
        outcome = comparison.compare_pair(b0, b1)
        self.assertEqual("PAIR_EQUIVALENCE_ONLY", outcome["status"])
        self.assertEqual("NOT_ATTESTED", outcome["reference_membership_binding"])

    def test_supplied_full_anchor_rejects_equal_truncated_vectors(self):
        anchor = {
            "schema": "DISCOVERY_READ_ONLY_PUBLIC_IDENTITY_PROBE_20261028",
            "owner": "thebrazenbeard", "subjects": copy.deepcopy(self.b0["subjects"]),
            "bound_exact_subjects": 2, "B0_count": 2, "B1_count": 2,
            "archived": 1, "not_admitted": True,
        }
        anchor["identity_digest_sha256"] = hashlib.sha256(
            (json.dumps(anchor["subjects"], sort_keys=True, ensure_ascii=False,
                        separators=(",", ":")) + "\n").encode()
        ).hexdigest()
        b0, b1 = copy.deepcopy(self.b0), copy.deepcopy(self.b1)
        b0["subjects"] = b0["subjects"][:1]
        b1["subjects"] = b1["subjects"][:1]
        with self.assertRaisesRegex(comparison.VectorError, "anchor"):
            comparison.compare_pair(b0, b1, anchor=anchor)
        outcome = comparison.compare_pair(self.b0, self.b1, anchor=anchor)
        self.assertEqual("PAIR_MATCHES_SUPPLIED_ANCHOR_ONLY", outcome["status"])
        self.assertEqual("SUPPLIED_ANCHOR_SELF_CONSISTENT_NOT_AUTHENTICATED",
                         outcome["reference_membership_binding"])
        self.assertEqual("NOT_ADMITTED", outcome["admission"])

    def test_changed_tree_and_ids_are_detected(self):
        for field, value in (("tree", "f" * 40), ("id", 900)):
            b1 = copy.deepcopy(self.b1)
            b1["subjects"][0][field] = value
            with self.subTest(field=field), self.assertRaises(comparison.VectorError):
                comparison.compare_pair(self.b0, b1)

    def test_summary_counts_cannot_substitute_full_vector(self):
        b1 = copy.deepcopy(self.b1)
        b1.pop("subjects")
        b1["subject_count"] = 2
        with self.assertRaises(comparison.VectorError):
            comparison.compare_pair(self.b0, b1)

    def test_distinct_observations_and_sequential_timing_are_required(self):
        b1 = copy.deepcopy(self.b1)
        b1["observation_id"] = "b0"
        with self.assertRaises(comparison.VectorError):
            comparison.compare_pair(self.b0, b1)
        b1 = copy.deepcopy(self.b1)
        b1["started_at_utc"] = "2026-10-28T20:00:03Z"
        with self.assertRaises(comparison.VectorError):
            comparison.compare_pair(self.b0, b1)

    def test_profile_mismatch_and_collection_error_are_rejected(self):
        b1 = copy.deepcopy(self.b1)
        b1["source_profile_sha256"] = "f" * 64
        with self.assertRaises(comparison.VectorError):
            comparison.compare_pair(self.b0, b1)
        b1 = copy.deepcopy(self.b1)
        b1["errors"] = ["rate limit"]
        with self.assertRaises(comparison.VectorError):
            comparison.compare_pair(self.b0, b1)

    def test_duplicate_keys_and_duplicate_casefold_names_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "probe.json"
            p.write_text('{"owner":"thebrazenbeard","owner":"other"}', encoding="utf-8")
            with self.assertRaises(comparison.VectorError):
                comparison.load_vector(p)
        b1 = copy.deepcopy(self.b1)
        b1["subjects"][1]["name"] = "Alpha"
        with self.assertRaises(comparison.VectorError):
            comparison.compare_pair(self.b0, b1)

    def test_bool_id_and_empty_branch_rejected(self):
        for field, value in (("id", True), ("branch", "")):
            b1 = copy.deepcopy(self.b1)
            b1["subjects"][1][field] = value
            with self.subTest(field=field), self.assertRaises(comparison.VectorError):
                comparison.compare_pair(self.b0, b1)


if __name__ == "__main__":
    unittest.main()
