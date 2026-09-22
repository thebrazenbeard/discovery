import copy
import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "validate_portfolio_census_drift_transition.py"

spec = importlib.util.spec_from_file_location("validate_portfolio_census_drift_transition", TOOL)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class PortfolioCensusDriftTransitionTests(unittest.TestCase):
    def setUp(self):
        self.doc = module.load()

    def test_repository_validation_passes(self):
        self.assertEqual([], module.validate())

    def test_public_refresh_cannot_be_invented(self):
        doc = copy.deepcopy(self.doc)
        doc["public_consumer"]["refreshed_to_current_discovery_census"] = True
        errors = module.validate_result(doc)
        self.assertIn("public consumer refresh falsely promoted", errors)

    def test_opaque_refresh_cannot_be_publicly_promoted(self):
        doc = copy.deepcopy(self.doc)
        doc["opaque_consumer"]["current_refresh_status"] = "REFRESHED"
        errors = module.validate_result(doc)
        self.assertIn("opaque consumer refresh falsely promoted", errors)

    def test_two_consumer_refresh_cannot_self_promote(self):
        doc = copy.deepcopy(self.doc)
        doc["falsifier"]["synchronized_two_consumer_refresh"] = "PASS"
        errors = module.validate_result(doc)
        self.assertIn("synchronized_two_consumer_refresh falsely promoted", errors)

    def test_candidate_cannot_become_proven_reusable(self):
        doc = copy.deepcopy(self.doc)
        doc["result"]["proven_reusable"] = True
        errors = module.validate_result(doc)
        self.assertIn("candidate falsely promoted to reusable", errors)

    def test_current_visibility_split_is_bound(self):
        doc = copy.deepcopy(self.doc)
        doc["current_provider"]["public"] = 22
        errors = module.validate_result(doc)
        self.assertIn("current visibility split drifted", errors)


if __name__ == "__main__":
    unittest.main()
