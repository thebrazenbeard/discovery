import copy
import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "validate_evidence_custody_package_readiness.py"

spec = importlib.util.spec_from_file_location("validate_evidence_custody_package_readiness", TOOL)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class EvidenceCustodyPackageReadinessTests(unittest.TestCase):
    def setUp(self):
        self.doc = module.load()

    def test_repository_validation_passes(self):
        self.assertEqual([], module.validate())

    def test_private_identity_cannot_be_promoted_public(self):
        doc = copy.deepcopy(self.doc)
        doc["source_identity_published"] = True
        errors = module.validate_result(doc)
        self.assertIn("private source identity falsely published", errors)

    def test_clean_install_cannot_be_invented(self):
        doc = copy.deepcopy(self.doc)
        doc["qualification"]["clean_install_qualification"] = "PASS"
        errors = module.validate_result(doc)
        self.assertIn("clean install falsely qualified", errors)

    def test_general_installability_cannot_be_promoted(self):
        doc = copy.deepcopy(self.doc)
        doc["qualification"]["general_installability"] = "PASS"
        errors = module.validate_result(doc)
        self.assertIn("general installability falsely promoted", errors)

    def test_reuse_evaluation_remains_blocked(self):
        doc = copy.deepcopy(self.doc)
        doc["package_readiness_result"]["reusable_interchange_evaluation_allowed"] = True
        errors = module.validate_result(doc)
        self.assertIn("reuse evaluation falsely authorized", errors)

    def test_platform_ceiling_cannot_be_invented(self):
        doc = copy.deepcopy(self.doc)
        doc["qualification"]["explicit_os_platform_ceiling_present"] = True
        errors = module.validate_result(doc)
        self.assertIn("OS/platform support ceiling falsely asserted", errors)


if __name__ == "__main__":
    unittest.main()
