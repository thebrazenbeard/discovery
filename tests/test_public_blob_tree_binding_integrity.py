import copy
import importlib.util
import json
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "validate_discovery.py"

spec = importlib.util.spec_from_file_location("validate_discovery_tree_binding", TOOL)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


class PublicBlobTreeBindingIntegrityTests(unittest.TestCase):
    def test_current_shards_do_not_alias_commit_as_tree(self):
        for path in validator.PUBLIC_BLOB_SHARDS:
            shard = validator.load(path)
            for repo_name, subject in shard["repositories"].items():
                self.assertNotEqual(
                    subject["head"],
                    subject["tree_sha"],
                    f"{repo_name} tree_sha must be the commit's tree object, not the commit SHA",
                )

    def test_validator_rejects_commit_as_tree_false_green(self):
        census = validator.load(validator.CENSUS)
        original_shards = validator.PUBLIC_BLOB_SHARDS
        first = validator.load(original_shards[0])
        mutated = copy.deepcopy(first)
        repo_name = sorted(mutated["repositories"])[0]
        mutated["repositories"][repo_name]["tree_sha"] = mutated["repositories"][repo_name]["head"]

        with tempfile.TemporaryDirectory() as tmp:
            bad_path = pathlib.Path(tmp) / "SHARD_A.json"
            bad_path.write_text(json.dumps(mutated), encoding="utf-8")
            validator.PUBLIC_BLOB_SHARDS = (bad_path, original_shards[1])
            try:
                errors = validator._validate_public_blob_scan(census)
            finally:
                validator.PUBLIC_BLOB_SHARDS = original_shards

        self.assertIn(
            f"public blob tree sha incorrectly aliases commit sha: {repo_name}",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
