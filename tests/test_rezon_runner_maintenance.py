import copy
import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "validate_rezon_runner_maintenance.py"

spec = importlib.util.spec_from_file_location("validate_rezon_runner_maintenance", TOOL)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class RezonRunnerMaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.doc = module.load()

    def test_repository_validation_passes(self):
        self.assertEqual([], module.validate())

    def test_cannot_keep_producer_agnostic_claim(self):
        doc = copy.deepcopy(self.doc)
        doc["result"]["producer_agnostic_boundary_demonstrated"] = True
        errors = module.validate_result(doc)
        self.assertIn("producer-agnostic boundary falsely promoted", errors)

    def test_cannot_promote_maintenance_savings(self):
        doc = copy.deepcopy(self.doc)
        doc["result"]["net_maintenance_savings_demonstrated"] = True
        errors = module.validate_result(doc)
        self.assertIn("maintenance savings falsely promoted", errors)

    def test_cannot_promote_second_consumer(self):
        doc = copy.deepcopy(self.doc)
        doc["result"]["organic_second_consumer_demonstrated"] = True
        errors = module.validate_result(doc)
        self.assertIn("second consumer falsely promoted", errors)

    def test_cannot_convert_structural_hardening_into_epistemic_authority(self):
        doc = copy.deepcopy(self.doc)
        doc["result"]["epistemic_authority_transfered"] = True
        errors = module.validate_result(doc)
        self.assertIn("epistemic authority falsely transferred", errors)

    def test_current_successor_binding_is_exact(self):
        doc = copy.deepcopy(self.doc)
        doc["exact_subjects"]["runner_current"]["ref"] = "PR31@" + "0" * 40
        errors = module.validate_result(doc)
        self.assertIn("current Runner successor binding drifted", errors)


if __name__ == "__main__":
    unittest.main()
