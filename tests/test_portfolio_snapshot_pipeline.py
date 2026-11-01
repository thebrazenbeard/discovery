import copy
import importlib.util
import json
import pathlib
import unittest
import urllib.request
from unittest import mock


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

    def test_case_colliding_repository_names_fail(self):
        collision = copy.deepcopy(PUBLIC_A)
        collision["name"] = "ALPHA"
        with self.assertRaisesRegex(builder.SnapshotError, "case-insensitive"):
            snapshot([PUBLIC_A, collision])

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


class GitHubInventoryAdmissionTests(unittest.TestCase):
    def test_bearer_is_never_forwarded_on_cross_origin_redirect(self):
        request = urllib.request.Request(
            "https://api.github.com/user/repos",
            headers={"Authorization": "Bearer synthetic-token"},
        )
        unsafe_redirect = urllib.request.HTTPRedirectHandler().redirect_request(
            request, None, 302, "moved", {}, "https://attacker.invalid/collect"
        )
        self.assertEqual("Bearer synthetic-token", unsafe_redirect.get_header("Authorization"))

        class SyntheticOpener:
            def open(self, request, timeout):
                class Response:
                    def __enter__(self):
                        return self

                    def __exit__(self, *_):
                        return False

                    def read(self):
                        return b"[]"

                return Response()

        def admit_only_redirect_denial(*handlers):
            self.assertTrue(any(
                handler.redirect_request(
                    request, None, 302, "moved", {}, "https://attacker.invalid/collect"
                ) is None
                for handler in handlers
                if isinstance(handler, urllib.request.HTTPRedirectHandler)
            ))
            return SyntheticOpener()

        with mock.patch.object(
            builder.urllib.request, "build_opener", side_effect=admit_only_redirect_denial
        ), mock.patch.object(
            builder.urllib.request, "urlopen", side_effect=AssertionError("unsafe urlopen")
        ):
            self.assertEqual([], builder.GitHubInventoryClient("synthetic-token")._get_json("/user/repos"))

    def test_owned_inventory_paginates_beyond_first_hundred(self):
        class Client(builder.GitHubInventoryClient):
            def _get_json(self, path):
                page = int(path.rsplit("page=", 1)[-1])
                if page == 1:
                    return [
                        {"name": f"repo-{i:03d}", "owner": {"login": "thebrazenbeard"}}
                        for i in range(100)
                    ]
                if page == 2:
                    return [
                        {"name": f"repo-{i:03d}", "owner": {"login": "thebrazenbeard"}}
                        for i in range(100, 112)
                    ]
                raise AssertionError("unexpected third page")

        observed = Client("synthetic-token").list_owned_repositories("thebrazenbeard")
        self.assertEqual(112, len(observed))
        self.assertEqual("repo-111", observed[-1]["name"])

    def test_malformed_owner_record_fails_instead_of_shortening_inventory(self):
        class Client(builder.GitHubInventoryClient):
            def _get_json(self, path):
                return [
                    {"name": "valid", "owner": {"login": "thebrazenbeard"}},
                    {"name": "malformed", "owner": None},
                ]

        with self.assertRaisesRegex(builder.SnapshotError, "owner"):
            Client("synthetic-token").list_owned_repositories("thebrazenbeard")

    def test_whitespace_owner_fails_instead_of_silently_skipping(self):
        class Client(builder.GitHubInventoryClient):
            def _get_json(self, path):
                return [{"name": "ambiguous", "owner": {"login": " thebrazenbeard "}}]

        with self.assertRaisesRegex(builder.SnapshotError, "owner"):
            Client("synthetic-token").list_owned_repositories("thebrazenbeard")

    def test_private_visibility_mismatch_fails_before_public_projection(self):
        class Client(builder.GitHubInventoryClient):
            def list_owned_repositories(self, owner):
                return [{
                    "name": "synthetic-private-record",
                    "private": False,
                    "visibility": "private",
                    "archived": False,
                    "default_branch": "main",
                }]

            def public_exact_subject(self, owner, repo):
                return {"name": repo["name"], "visibility": "public"}

        with self.assertRaisesRegex(builder.SnapshotError, "visibility"):
            Client("synthetic-token").inventory("thebrazenbeard")

    def test_public_exact_subject_rejects_private_metadata_directly(self):
        class Client(builder.GitHubInventoryClient):
            def _get_json(self, path):
                raise AssertionError("private record must not reach branch fetch")

        with self.assertRaisesRegex(builder.SnapshotError, "visibility"):
            Client("synthetic-token").public_exact_subject("thebrazenbeard", {
                "name": "synthetic-private-record",
                "private": True,
                "visibility": "private",
                "archived": False,
                "default_branch": "main",
            })

    def test_non_boolean_archive_flag_fails_closed(self):
        class Client(builder.GitHubInventoryClient):
            def list_owned_repositories(self, owner):
                return [{
                    "name": "private-repo",
                    "private": True,
                    "visibility": "private",
                    "archived": "false",
                    "default_branch": "main",
                }]

        with self.assertRaisesRegex(builder.SnapshotError, "archived"):
            Client("synthetic-token").inventory("thebrazenbeard")

    def test_missing_archive_flag_fails_closed(self):
        class Client(builder.GitHubInventoryClient):
            def list_owned_repositories(self, owner):
                return [{
                    "name": "private-repo",
                    "private": True,
                    "visibility": "private",
                    "default_branch": "main",
                }]

        with self.assertRaisesRegex(builder.SnapshotError, "archived"):
            Client("synthetic-token").inventory("thebrazenbeard")


if __name__ == "__main__":
    unittest.main()
