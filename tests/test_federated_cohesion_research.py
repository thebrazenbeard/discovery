import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "validate_federated_cohesion_research.py"
SPEC = importlib.util.spec_from_file_location("federated_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(validator)


class FederatedCohesionResearchTests(unittest.TestCase):
    def setUp(self):
        self.packet = validator.load_packet()

    def errors(self, mutator):
        candidate = copy.deepcopy(self.packet)
        mutator(candidate)
        return validator.validate_packet(candidate)

    def test_committed_packet_passes(self):
        self.assertEqual([], validator.validate_packet(self.packet))

    def test_private_name_publication_fails(self):
        errors = self.errors(
            lambda d: d["private_portfolio_boundary"]["named_private_repositories"].append(
                "private/example"
            )
        )
        self.assertTrue(any("private repository names" in e for e in errors))

    def test_promotion_ceiling_widening_fails(self):
        errors = self.errors(
            lambda d: d["architecture_hypothesis"].__setitem__(
                "promotion_ceiling", "PROVEN_REUSABLE"
            )
        )
        self.assertTrue(any("promotion ceiling widened" in e for e in errors))

    def test_mutable_subject_ref_fails(self):
        errors = self.errors(
            lambda d: d["public_subjects"][0].__setitem__("exact_ref", "main")
        )
        self.assertTrue(any("exact_ref is not immutable" in e for e in errors))

    def test_inventory_arithmetic_drift_fails(self):
        errors = self.errors(
            lambda d: d["inventory_binding"].__setitem__("private_repositories", 34)
        )
        self.assertTrue(any("inventory arithmetic mismatch" in e for e in errors))

    def test_mandatory_global_runtime_assertion_fails(self):
        errors = self.errors(
            lambda d: d["architecture_hypothesis"].__setitem__(
                "mandatory_global_runtime", "REQUIRED"
            )
        )
        self.assertTrue(any("mandatory global runtime" in e for e in errors))

    def test_research_observation_promotion_fails(self):
        errors = self.errors(
            lambda d: d["cross_system_observations"][0].__setitem__(
                "state", "EXPERIMENTING"
            )
        )
        self.assertTrue(any("escaped OBSERVED" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
