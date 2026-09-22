import copy
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "validate_research_ingest.py"

spec = importlib.util.spec_from_file_location("validate_research_ingest", TOOL)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class ResearchIngestTests(unittest.TestCase):
    def test_repository_research_cut_passes(self):
        self.assertEqual([], module.validate())

    def test_missing_public_repo_fails_closed(self):
        census = module.load(module.CENSUS)
        cut = module.load(module.CUT)
        broken = copy.deepcopy(cut)
        broken["observations"] = broken["observations"][:-1]
        errors = module.validate_data(census, broken)
        self.assertTrue(any("membership mismatch" in error for error in errors))

    def test_promotion_above_hypothesis_is_rejected(self):
        census = module.load(module.CENSUS)
        cut = module.load(module.CUT)
        broken = copy.deepcopy(cut)
        broken["observations"][0]["evidence_state"] = "EXPERIMENTING"
        errors = module.validate_data(census, broken)
        self.assertTrue(any("exceeds ingest ceiling" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
