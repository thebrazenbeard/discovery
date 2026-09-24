import copy
import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "check_public_currentness.py"

spec = importlib.util.spec_from_file_location("check_public_currentness", TOOL)
watch = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(watch)


def subject(
    name: str,
    *,
    branch: str = "main",
    head: str = "a" * 40,
    tree: str = "b" * 40,
    archived: bool = False,
):
    return {
        "name": name,
        "default_branch": branch,
        "head": head,
        "tree_sha": tree,
        "archived": archived,
    }


class PublicCurrentnessComparisonTests(unittest.TestCase):
    def test_identical_subjects_are_current(self):
        expected = {"alpha": subject("alpha")}
        observed = copy.deepcopy(expected)
        report = watch.compare_public_subjects(expected, observed)
        self.assertEqual("CURRENT", report["status"])
        self.assertEqual([], report["invalidation_reasons"])
        self.assertEqual("NOT_OBSERVED", report["private_currentness"])

    def test_repository_set_change_is_stale(self):
        expected = {"alpha": subject("alpha")}
        observed = {
            "alpha": subject("alpha"),
            "beta": subject("beta", head="c" * 40, tree="d" * 40),
        }
        report = watch.compare_public_subjects(expected, observed)
        self.assertEqual("STALE", report["status"])
        self.assertEqual(["beta"], report["added"])
        self.assertIn(
            "PUBLIC_REPOSITORY_SET_CHANGED",
            report["invalidation_reasons"],
        )

    def test_head_or_tree_movement_is_stale(self):
        expected = {"alpha": subject("alpha")}
        observed = {
            "alpha": subject("alpha", head="c" * 40, tree="d" * 40),
        }
        report = watch.compare_public_subjects(expected, observed)
        self.assertEqual("STALE", report["status"])
        changes = report["moved"][0]["changes"]
        self.assertIn("head", changes)
        self.assertIn("tree_sha", changes)

    def test_discovery_self_head_movement_is_separate_ci_concern(self):
        expected = {"discovery": subject("discovery")}
        observed = {
            "discovery": subject("discovery", head="c" * 40, tree="d" * 40),
        }
        report = watch.compare_public_subjects(expected, observed)
        self.assertEqual("CURRENT", report["status"])
        self.assertEqual([], report["moved"])
        self.assertEqual(
            "HEAD_TREE_SEPARATE_CI_CONCERN",
            report["self_subject_currentness"]["status"],
        )

    def test_default_branch_change_is_stale(self):
        expected = {"alpha": subject("alpha")}
        observed = {"alpha": subject("alpha", branch="stable")}
        report = watch.compare_public_subjects(expected, observed)
        self.assertEqual("STALE", report["status"])
        self.assertIn(
            "default_branch",
            report["moved"][0]["changes"],
        )

    def test_archive_state_change_is_stale(self):
        expected = {"alpha": subject("alpha")}
        observed = {"alpha": subject("alpha", archived=True)}
        report = watch.compare_public_subjects(expected, observed)
        self.assertEqual("STALE", report["status"])
        self.assertIn("archived", report["moved"][0]["changes"])


class PublicCurrentnessBaselineTests(unittest.TestCase):
    def test_repository_baseline_loads_exact_current_public_set(self):
        subjects = watch.load_expected_public_subjects()
        self.assertEqual(48, len(subjects))
        self.assertIn("discovery", subjects)
        self.assertIn("world-zero", subjects)
        self.assertIn("WorkBridgeMCP", subjects)
        self.assertEqual("collab", subjects["masamune"]["default_branch"])
        for name, item in subjects.items():
            if name != "masamune":
                self.assertEqual("main", item["default_branch"])
            self.assertFalse(item["archived"])
            self.assertNotEqual(item["head"], item["tree_sha"])

    def test_currentness_baseline_keeps_blob_overlap_stale(self):
        baseline = watch.load_currentness_baseline()
        self.assertEqual(
            "STALE_PREDECESSOR_24_SUBJECT_SET",
            baseline["blob_evidence_status"],
        )
        self.assertEqual(
            "NO_48_SUBJECT_BLOB_OVERLAP_CLAIM",
            baseline["blob_evidence_claim_ceiling"],
        )


class FakeGitHubPublicInventoryClient(watch.GitHubPublicInventoryClient):
    def __init__(self, payloads):
        super().__init__(None, api_base="https://example.invalid")
        self.payloads = payloads
        self.calls = []

    def _get_json(self, path):
        self.calls.append(path)
        try:
            return self.payloads[path]
        except KeyError as exc:
            raise AssertionError(f"unexpected GitHub path: {path}") from exc


class PublicCurrentnessClientTests(unittest.TestCase):
    def test_public_inventory_needs_no_private_endpoint(self):
        list_path = (
            "/users/thebrazenbeard/repos?type=owner&sort=full_name"
            "&direction=asc&per_page=100&page=1"
        )
        branch_path = "/repos/thebrazenbeard/alpha/branches/main"
        client = FakeGitHubPublicInventoryClient(
            {
                list_path: [
                    {
                        "name": "alpha",
                        "private": False,
                        "default_branch": "main",
                        "archived": False,
                        "owner": {"login": "thebrazenbeard"},
                    }
                ],
                branch_path: {
                    "commit": {
                        "sha": "a" * 40,
                        "commit": {
                            "tree": {"sha": "b" * 40},
                        },
                    }
                },
            }
        )

        inventory = client.inventory("thebrazenbeard")

        self.assertEqual({"alpha"}, set(inventory))
        self.assertEqual("a" * 40, inventory["alpha"]["head"])
        self.assertEqual("b" * 40, inventory["alpha"]["tree_sha"])
        self.assertTrue(
            all("/user/repos" not in call for call in client.calls),
            client.calls,
        )

    def test_private_records_from_public_endpoint_are_ignored(self):
        list_path = (
            "/users/thebrazenbeard/repos?type=owner&sort=full_name"
            "&direction=asc&per_page=100&page=1"
        )
        client = FakeGitHubPublicInventoryClient(
            {
                list_path: [
                    {
                        "name": "private-leak",
                        "private": True,
                        "default_branch": "main",
                        "archived": False,
                        "owner": {"login": "thebrazenbeard"},
                    }
                ],
            }
        )
        self.assertEqual({}, client.inventory("thebrazenbeard"))


if __name__ == "__main__":
    unittest.main()
