"""Negative controls for consuming public-safe portfolio observations.

These tests verify that the *reader* refuses internally inconsistent evidence;
they do not authenticate a producer or make a public snapshot authoritative.
"""

import copy
import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_script("build_portfolio_snapshot")
comparator = load_script("compare_portfolio_snapshots")

PUBLIC = {
    "name": "example-public",
    "visibility": "public",
    "default_branch": "main",
    "head_sha": "a" * 40,
    "tree_sha": "b" * 40,
    "archived": False,
}
PRIVATE = {"name": "opaque-private", "visibility": "private", "archived": False}


def valid_snapshot():
    return builder.build_public_snapshot(
        [PUBLIC, PRIVATE],
        owner="example-owner",
        observed_at="2026-11-05T12:00:00Z",
        acquisition_method="SYNTHETIC_TEST",
        private_key=b"K" * 32,
    )


class ComparisonIntegrityTests(unittest.TestCase):
    def assert_rejected_identical_forgery(self, change):
        snapshot = valid_snapshot()
        change(snapshot)
        with self.assertRaises(comparator.ComparisonError):
            comparator.compare_snapshots(snapshot, copy.deepcopy(snapshot))

    def test_valid_snapshot_remains_comparable(self):
        snapshot = valid_snapshot()
        result = comparator.compare_snapshots(snapshot, copy.deepcopy(snapshot))
        self.assertEqual("CURRENT_RELATIVE_TO_NEW_SNAPSHOT", result["currentness"])

    def test_unkeyed_public_only_snapshot_is_structurally_accepted_but_unverifiable(self):
        public_only = builder.build_public_snapshot(
            [PUBLIC],
            owner="example-owner",
            observed_at="2026-11-05T12:00:00Z",
            acquisition_method="SYNTHETIC_TEST",
            private_key=None,
        )
        result = comparator.compare_snapshots(public_only, copy.deepcopy(public_only))
        self.assertEqual("STALE", result["currentness"])
        self.assertEqual("KEY_CHANGED_OR_UNCOMPARABLE", result["all_set_state"])

    def test_rejects_forged_public_name_digest(self):
        self.assert_rejected_identical_forgery(
            lambda s: s["public_name_digest"].update(sha256="0" * 64)
        )

    def test_rejects_malformed_public_git_object_id(self):
        self.assert_rejected_identical_forgery(
            lambda s: s["public_repositories"][0].update(exact_commit="garbage")
        )

    def test_rejects_nonboolean_archive_flag(self):
        self.assert_rejected_identical_forgery(
            lambda s: s["public_repositories"][0].update(archived="false")
        )

    def test_rejects_forged_counts(self):
        self.assert_rejected_identical_forgery(
            lambda s: s["counts"].update(public=17, total=18)
        )

    def test_rejects_missing_keyed_commitment_digest(self):
        self.assert_rejected_identical_forgery(
            lambda s: s["private_inventory_commitment"].update(hmac_sha256=None)
        )

    def test_rejects_mismatched_private_commitment_count(self):
        self.assert_rejected_identical_forgery(
            lambda s: s["private_inventory_commitment"].update(count=0)
        )

    def test_rejects_casefold_colliding_public_names(self):
        self.assert_rejected_identical_forgery(
            lambda s: (
                s["public_repositories"].append(
                    dict(s["public_repositories"][0], name="EXAMPLE-PUBLIC")
                ),
                s["counts"].update(public=2, total=3),
                s["public_name_digest"].update(
                    sha256=builder.public_name_digest(["example-public", "EXAMPLE-PUBLIC"])
                ),
            )
        )

    def test_rejects_unrelated_owner_context(self):
        original = valid_snapshot()
        different = copy.deepcopy(original)
        different["source"]["owner"] = "different-owner"
        with self.assertRaises(comparator.ComparisonError):
            comparator.compare_snapshots(original, different)

    def test_rejects_reversed_observation_time(self):
        original = valid_snapshot()
        older = copy.deepcopy(original)
        older["observed_at"] = "2026-11-04T12:00:00Z"
        with self.assertRaises(comparator.ComparisonError):
            comparator.compare_snapshots(original, older)


if __name__ == "__main__":
    unittest.main()
