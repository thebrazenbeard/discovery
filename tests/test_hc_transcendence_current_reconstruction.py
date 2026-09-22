import copy
import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "validate_hc_transcendence_current_reconstruction.py"

spec = importlib.util.spec_from_file_location("hc_transcendence_reconstruction", TOOL)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


class HCTranscendenceCurrentReconstructionTests(unittest.TestCase):
    def setUp(self):
        self.manifest = validator.load(validator.MANIFEST)
        self.base = validator.load(validator.BASE_FILEMAP)

    def test_exact_current_tree_reconstruction_passes(self):
        self.assertEqual([], validator.validate_data(self.manifest, self.base))

    def test_missing_delete_breaks_exact_target_tree(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["operations"]["delete_paths"] = manifest["operations"]["delete_paths"][:-1]
        manifest["counts"]["deletes"] -= 1
        manifest["counts"]["target_files"] += 1
        errors = validator.validate_data(manifest, self.base)
        self.assertIn(
            "reconstructed tree does not match bound Transcendence tree",
            errors,
        )

    def test_override_blob_mutation_breaks_exact_target_tree(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["operations"]["overrides"][0]["to"]["sha"] = "0" * 40
        errors = validator.validate_data(manifest, self.base)
        self.assertIn(
            "reconstructed tree does not match bound Transcendence tree",
            errors,
        )

    def test_base_snapshot_mutation_breaks_bound_hc_tree(self):
        base = copy.deepcopy(self.base)
        inherited_paths = {
            entry["path"] for entry in base["entries"]
        } - set(self.manifest["operations"]["delete_paths"]) - {
            item["path"] for item in self.manifest["operations"]["overrides"]
        }
        target_path = sorted(inherited_paths)[0]
        entry = next(item for item in base["entries"] if item["path"] == target_path)
        entry["sha"] = "0" * 40
        errors = validator.validate_data(self.manifest, base)
        self.assertIn("base filemap does not reproduce bound HC tree", errors)


if __name__ == "__main__":
    unittest.main()
