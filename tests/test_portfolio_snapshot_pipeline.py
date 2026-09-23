import copy
import importlib.util
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]

builder_spec = importlib.util.spec_from_file_location(
    "build_portfolio_snapshot",
    ROOT / "tools" / "build_portfolio_snapshot.py",
)
builder = importlib.util.module_from_spec(builder_spec)
assert builder_spec.loader is not None
builder_spec.loader.exec_module(builder)

compare_spec = importlib.util.spec_from_file_location(
    "compare_portfolio_snapshots",
    ROOT / "tools" / "compare_portfolio_snapshots.py",
)
comparer = importlib.util.module_from_spec(compare_spec)
assert compare_spec.loader is not None
compare_spec.loader.exec_module(comparer)


PUBLIC_A = {
    "name": "alpha",
    "visibility": "public",
    "default_branch": "main",
    "head_sha": "a" * 40,
    "tree_sha": "b" * 40,
    "archived": False,
}
PUBLIC_B = {
    "name": "beta",
    "visibility": "public",
    "default_branch": "main",
    "head_sha": "c" * 40,
    "tree_sha": "d" * 40,
    "archived": False,
}
PRIVATE_A = {
    "name": "private-secret-project",
    "visibility": "private",
    "default_branch": "main",
    "archived": False,
}
PRIVATE_B = {
    "name": "another-private-project",
    "visibility": "private",
    "default_branch": "main",
    "archived": False,
}
KEY = bytes.fromhex("11" * 32)
OTHER_KEY = bytes.fromhex("22" * 32)


def snapshot(records, key=KEY, observed_at="2026-09-22T14:00:00Z"):
    return builder.build_public_snapshot(
        records,
        owner="thebrazenbeard",
        observed_at=observed_at,
        acquisition_method="UNIT_TEST",
        private_key=key,
    )


class PortfolioSnapshotTests(unittest.TestCase):
    def test_public_snapshot_omits_private_names(self):
        result = snapshot([PUBLIC_A, PRIVATE_A])
        rendered = json.dumps(result)
        self.assertNotIn("private-secret-project", rendered)
        self.assertEqual(1, result["counts"]["private"])
        self.assertEqual(["alpha"], [item["name"] for item in result["public_repositories"]])

    def test_private_inventory_requires_key(self):
        with self.assertRaisesRegex(
            builder.SnapshotError,
            "private census key required",
        ):
            snapshot([PUBLIC_A, PRIVATE_A], key=None)

    def test_private_commitment_is_keyed_and_domain_separated(self):
        result = snapshot([PUBLIC_A, PRIVATE_A])
        private_digest = result["private_inventory_commitment"]["hmac_sha256"]
        all_digest = result["all_inventory_commitment"]["hmac_sha256"]
        self.assertNotEqual(private_digest, all_digest)
        self.assertEqual(
            "HMAC_SHA256_PRIVATE_KEY_CANONICAL_V1",
            result["private_inventory_commitment"]["scheme"],
        )
        self.assertFalse(result["private_inventory_commitment"]["publicly_recomputable"])

    def test_public_digest_is_recomputable(self):
        result = snapshot([PUBLIC_B, PUBLIC_A])
        expected = builder.public_name_digest(["alpha", "beta"])
        self.assertEqual(expected, result["public_name_digest"]["sha256"])
        self.assertTrue(result["public_name_digest"]["publicly_recomputable"])

    def test_duplicate_repository_names_fail(self):
        with self.assertRaisesRegex(
            builder.SnapshotError,
            "repository names must be unique",
        ):
            snapshot([PUBLIC_A, copy.deepcopy(PUBLIC_A)])

    def test_public_subject_requires_exact_commit_and_tree(self):
        broken = copy.deepcopy(PUBLIC_A)
        broken["head_sha"] = "not-a-sha"
        with self.assertRaisesRegex(builder.SnapshotError, "head_sha"):
            snapshot([broken])


class PortfolioSnapshotComparisonTests(unittest.TestCase):
    def test_identical_snapshot_is_current(self):
        old = snapshot([PUBLIC_A, PRIVATE_A])
        new = snapshot(
            [PUBLIC_A, PRIVATE_A],
            observed_at="2026-09-22T15:00:00Z",
        )
        result = comparer.compare_snapshots(old, new)
        self.assertEqual("CURRENT_RELATIVE_TO_NEW_SNAPSHOT", result["currentness"])
        self.assertEqual([], result["invalidation_reasons"])

    def test_public_head_movement_invalidates(self):
        old = snapshot([PUBLIC_A, PRIVATE_A])
        moved = copy.deepcopy(PUBLIC_A)
        moved["head_sha"] = "e" * 40
        moved["tree_sha"] = "f" * 40
        new = snapshot(
            [moved, PRIVATE_A],
            observed_at="2026-09-22T15:00:00Z",
        )
        result = comparer.compare_snapshots(old, new)
        self.assertEqual("STALE", result["currentness"])
        self.assertIn("PUBLIC_EXACT_SUBJECT_CHANGED", result["invalidation_reasons"])
        self.assertEqual("alpha", result["public_changes"]["moved"][0]["name"])

    def test_private_set_movement_invalidates_without_name_disclosure(self):
        old = snapshot([PUBLIC_A, PRIVATE_A])
        new = snapshot(
            [PUBLIC_A, PRIVATE_A, PRIVATE_B],
            observed_at="2026-09-22T15:00:00Z",
        )
        result = comparer.compare_snapshots(old, new)
        rendered = json.dumps(result)
        self.assertEqual("STALE", result["currentness"])
        self.assertEqual("CHANGED", result["private_set_state"])
        self.assertIn("PRIVATE_REPOSITORY_SET_CHANGED", result["invalidation_reasons"])
        self.assertNotIn("private-secret-project", rendered)
        self.assertNotIn("another-private-project", rendered)

    def test_key_rotation_fails_closed(self):
        old = snapshot([PUBLIC_A, PRIVATE_A], key=KEY)
        new = snapshot(
            [PUBLIC_A, PRIVATE_A],
            key=OTHER_KEY,
            observed_at="2026-09-22T15:00:00Z",
        )
        result = comparer.compare_snapshots(old, new)
        self.assertEqual("STALE", result["currentness"])
        self.assertEqual("KEY_CHANGED_OR_UNCOMPARABLE", result["private_set_state"])
        self.assertIn(
            "PRIVATE_REPOSITORY_SET_CURRENTNESS_UNVERIFIABLE",
            result["invalidation_reasons"],
        )

    def test_public_repository_addition_invalidates(self):
        old = snapshot([PUBLIC_A, PRIVATE_A])
        new = snapshot(
            [PUBLIC_A, PUBLIC_B, PRIVATE_A],
            observed_at="2026-09-22T15:00:00Z",
        )
        result = comparer.compare_snapshots(old, new)
        self.assertEqual(["beta"], result["public_changes"]["added"])
        self.assertIn("PUBLIC_REPOSITORY_SET_CHANGED", result["invalidation_reasons"])


if __name__ == "__main__":
    unittest.main()
