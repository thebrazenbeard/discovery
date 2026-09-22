import copy
import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "validate_experiment_receipt_third_consumer.py"

spec = importlib.util.spec_from_file_location("validate_experiment_receipt_third_consumer", TOOL)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class ExperimentReceiptThirdConsumerTests(unittest.TestCase):
    def setUp(self):
        self.doc = module.load()

    def test_repository_validation_passes(self):
        self.assertEqual([], module.validate())

    def test_cannot_promote_four_part_pattern(self):
        doc = copy.deepcopy(self.doc)
        doc["result"]["prior_four_part_pattern_survives_three_way"] = True
        errors = module.validate_result(doc)
        self.assertIn("prior generic receipt pattern falsely promoted", errors)

    def test_cannot_create_generic_candidate_from_failed_intersection(self):
        doc = copy.deepcopy(self.doc)
        doc["result"]["generic_receipt_candidate_created"] = True
        errors = module.validate_result(doc)
        self.assertIn("generic receipt candidate falsely created", errors)

    def test_code_deletion_must_remain_zero(self):
        doc = copy.deepcopy(self.doc)
        doc["intersection_test"]["demonstrated_code_deleted_or_replaced_by_common_layer"] = 1
        errors = module.validate_result(doc)
        self.assertIn("third-consumer intersection result drifted", errors)

    def test_exact_subject_mutation_fails(self):
        doc = copy.deepcopy(self.doc)
        doc["exact_subjects"]["driftguard"]["ref"] = "main@" + "0" * 40
        errors = module.validate_result(doc)
        self.assertIn("third-consumer exact subject drifted: driftguard", errors)


if __name__ == "__main__":
    unittest.main()
