"""The 81-repo observation is internally checked, never promoted by validation."""

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
    "validate_public_identity_probe", ROOT / "tools" / "validate_public_identity_probe.py"
)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


def digest(subjects):
    data = json.dumps(subjects, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"
    return hashlib.sha256(data.encode()).hexdigest()


def good():
    subjects = [
        {"name": "Alpha", "id": 1, "branch": "main", "head": "a" * 40,
         "tree": "b" * 40, "archived": False},
        {"name": "beta", "id": 2, "branch": "main", "head": "c" * 40,
         "tree": "d" * 40, "archived": True},
    ]
    return {
        "schema": "DISCOVERY_READ_ONLY_PUBLIC_IDENTITY_PROBE_20261028",
        "owner": "thebrazenbeard",
        "source": "GitHub public REST inventory B0/B1 plus Git shallow commit/tree and ls-remote B1",
        "started_at_utc": "2026-10-28T21:12:45+00:00",
        "ended_at_utc": "2026-10-28T21:12:57+00:00",
        "B0_count": 2, "B1_count": 2, "bound_exact_subjects": 2,
        "archived": 1, "repo_set_stable": True, "head_drift": [], "errors": [],
        "not_admitted": True, "admission_state": "UNREVIEWED_NOT_ADMITTED",
        "identity_digest_sha256": digest(subjects),
        "names_digest_sha256": hashlib.sha256(b"Alpha\nbeta\n").hexdigest(),
        "subjects": subjects,
        "admission_guards": {"authorized_independent_signer": "MISSING"},
    }


class PublicIdentityReceiptTests(unittest.TestCase):
    def test_valid_receipt_is_structure_only(self):
        result = validator.validate_probe(good())
        self.assertEqual("LOCAL_IDENTITY_STRUCTURE_PASS_ONLY", result["status"])
        self.assertEqual("NOT_ATTESTED", result["independent_b0_b1_replay"])
        self.assertEqual("NOT_ADMITTED", result["admission"])

    def test_tampered_head_fails_digest(self):
        value = good()
        value["subjects"][0]["head"] = "e" * 40
        with self.assertRaisesRegex(validator.ProbeError, "identity digest"):
            validator.validate_probe(value)

    def test_sorted_names_and_case_insensitive_uniqueness_required(self):
        value = good()
        value["subjects"] = list(reversed(value["subjects"]))
        with self.assertRaisesRegex(validator.ProbeError, "sorted"):
            validator.validate_probe(value)
        value = good()
        value["subjects"][1]["name"] = "alpha"
        with self.assertRaisesRegex(validator.ProbeError, "unique"):
            validator.validate_probe(value)

    def test_duplicate_numeric_id_and_bool_count_fail(self):
        value = good()
        value["subjects"][1]["id"] = 1
        with self.assertRaisesRegex(validator.ProbeError, "ids unique"):
            validator.validate_probe(value)
        value = good()
        value["B0_count"] = True
        with self.assertRaisesRegex(validator.ProbeError, "B0_count"):
            validator.validate_probe(value)

    def test_unstable_or_unqualified_still_refuses(self):
        for change in ({"repo_set_stable": False}, {"errors": ["network"]},
                       {"head_drift": ["Alpha"]}, {"not_admitted": False},
                       {"admission_state": "ADMITTED"}):
            value = good()
            value.update(change)
            with self.subTest(change=change), self.assertRaises(validator.ProbeError):
                validator.validate_probe(value)

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "duplicate.json"
            target.write_text('{"owner":"thebrazenbeard","owner":"other"}')
            with self.assertRaisesRegex(validator.ProbeError, "duplicate JSON key"):
                validator.load_probe(target)

    def test_real_local_81_repository_receipt_is_only_structural(self):
        captured = ROOT.parent / "DISCOVERY_PUBLIC_IDENTITY_PROBE_20261028.json"
        if not captured.exists():
            self.skipTest("external historical observation not bundled in repository")
        outcome = validator.validate_probe(validator.load_probe(captured))
        self.assertEqual(81, outcome["subjects"])
        self.assertEqual("NOT_ADMITTED", outcome["admission"])


if __name__ == "__main__":
    unittest.main()
