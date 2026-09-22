import copy
import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "validate_veramesh_synology_handoff.py"

spec = importlib.util.spec_from_file_location("validate_veramesh_synology_handoff", TOOL)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class VeraMeshSynologyHandoffTests(unittest.TestCase):
    def setUp(self):
        self.doc = module.load()

    def test_repository_validation_passes(self):
        self.assertEqual([], module.validate())

    def test_producer_ref_mutation_fails(self):
        doc = copy.deepcopy(self.doc)
        doc["proposed_minimal_handoff_record"]["producer_exact_ref"] = "0" * 40
        errors = module.validate_result(doc)
        self.assertIn("proposed producer exact ref drifted", errors)

    def test_discovery_record_cannot_be_native_validation(self):
        doc = copy.deepcopy(self.doc)
        doc["result"]["discovery_side_record_is_native_synology_validation"] = True
        errors = module.validate_result(doc)
        self.assertIn("Discovery record falsely promoted to native validation", errors)

    def test_source_presence_cannot_promote_install(self):
        doc = copy.deepcopy(self.doc)
        doc["proposed_minimal_handoff_record"]["install_state"] = "INSTALLED"
        errors = module.validate_result(doc)
        self.assertIn("handoff state overclaim: install_state", errors)

    def test_source_presence_cannot_promote_route(self):
        doc = copy.deepcopy(self.doc)
        doc["proposed_minimal_handoff_record"]["route_state"] = "CURRENT_ROUTE"
        errors = module.validate_result(doc)
        self.assertIn("handoff state overclaim: route_state", errors)

    def test_missing_native_binding_cannot_be_flipped(self):
        doc = copy.deepcopy(self.doc)
        doc["native_validation_observation"]["current_native_cross_repo_binding_present"] = True
        errors = module.validate_result(doc)
        self.assertIn("native cross-repo binding falsely promoted", errors)

    def test_failed_experiment_cannot_self_promote_to_pass(self):
        doc = copy.deepcopy(self.doc)
        doc["result"]["disposition"] = "PASS"
        errors = module.validate_result(doc)
        self.assertIn("handoff disposition drifted", errors)


if __name__ == "__main__":
    unittest.main()
