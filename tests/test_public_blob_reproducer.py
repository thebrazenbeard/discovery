import importlib.util
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

TOOL = TOOLS / "refresh_public_blob_evidence.py"
spec = importlib.util.spec_from_file_location("refresh_public_blob_evidence", TOOL)
reproducer = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(reproducer)


class PublicBlobReproducerTests(unittest.TestCase):
    def test_committed_subjects_reproduce_canonical_artifacts_byte_for_byte(self):
        subjects = reproducer.subjects_from_committed_shards()
        rendered = reproducer.render_artifacts_from_subjects(subjects)

        expected_paths = {
            reproducer.SHARD_PATHS[0],
            reproducer.SHARD_PATHS[1],
            reproducer.SCAN_PATH,
        }
        self.assertEqual(expected_paths, set(rendered))

        for path, text in rendered.items():
            self.assertEqual(
                path.read_text(encoding="utf-8"),
                text,
                path.relative_to(ROOT).as_posix(),
            )

    def test_git_blob_identity_matches_known_empty_blob(self):
        self.assertEqual(
            "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391",
            reproducer._git_blob_sha1_text(""),
        )

    def test_repository_set_change_refuses_blind_repartition(self):
        subjects = reproducer.subjects_from_committed_shards()
        subjects["new-public-repository"] = {
            "name": "new-public-repository",
            "default_branch": "main",
            "head": "1" * 40,
            "tree_sha": "2" * 40,
            "archived": False,
            "blobs": [],
        }

        with self.assertRaisesRegex(
            reproducer.BlobEvidenceError,
            "classify census membership before blob refresh",
        ):
            reproducer.render_artifacts_from_subjects(subjects)

    def test_recursive_tree_rejects_truncation(self):
        class FakeClient(reproducer.GitHubPublicBlobClient):
            def __init__(self):
                super().__init__(None, api_base="https://example.invalid")

            def _get_json(self, path):
                return {
                    "sha": "b" * 40,
                    "truncated": True,
                    "tree": [],
                }

        client = FakeClient()
        with self.assertRaisesRegex(
            reproducer.BlobEvidenceError,
            "truncated",
        ):
            client.recursive_blobs(
                "owner",
                {
                    "name": "alpha",
                    "tree_sha": "b" * 40,
                },
            )

    def test_recursive_tree_rejects_wrong_root(self):
        class FakeClient(reproducer.GitHubPublicBlobClient):
            def __init__(self):
                super().__init__(None, api_base="https://example.invalid")

            def _get_json(self, path):
                return {
                    "sha": "c" * 40,
                    "truncated": False,
                    "tree": [],
                }

        client = FakeClient()
        with self.assertRaisesRegex(
            reproducer.BlobEvidenceError,
            "root mismatch",
        ):
            client.recursive_blobs(
                "owner",
                {
                    "name": "alpha",
                    "tree_sha": "b" * 40,
                },
            )

    def test_recursive_tree_normalizes_only_blob_entries(self):
        class FakeClient(reproducer.GitHubPublicBlobClient):
            def __init__(self):
                super().__init__(None, api_base="https://example.invalid")

            def _get_json(self, path):
                return {
                    "sha": "b" * 40,
                    "truncated": False,
                    "tree": [
                        {
                            "path": "z.txt",
                            "type": "blob",
                            "sha": "3" * 40,
                            "size": 3,
                        },
                        {
                            "path": "submodule",
                            "type": "commit",
                            "sha": "4" * 40,
                        },
                        {
                            "path": "a.txt",
                            "type": "blob",
                            "sha": "5" * 40,
                            "size": 5,
                        },
                    ],
                }

        blobs = FakeClient().recursive_blobs(
            "owner",
            {
                "name": "alpha",
                "tree_sha": "b" * 40,
            },
        )
        self.assertEqual(["a.txt", "z.txt"], [item["path"] for item in blobs])


if __name__ == "__main__":
    unittest.main()
