import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "validate_federated_cohesion_falsifier_round.py"
SPEC = importlib.util.spec_from_file_location("cohesion_falsifier_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(validator)


class FederatedCohesionFalsifierRoundTests(unittest.TestCase):
    def setUp(self):
        self.packet = validator.load_packet()

    def errors(self, mutator):
        candidate = copy.deepcopy(self.packet)
        mutator(candidate)
        return validator.validate_packet(candidate)

    def test_committed_packet_passes(self):
        self.assertEqual([], validator.validate_packet(self.packet))

    def test_generic_receipt_resurrection_fails(self):
        errors = self.errors(
            lambda d: next(
                x for x in d["prior_experiment_reassessment"] if x["id"] == "FED-EXP-2"
            ).__setitem__("current_state", "GENERIC_RECEIPT_SUPPORTED")
        )
        self.assertTrue(any("FED-EXP-2 falsification" in e for e in errors))

    def test_hypothesis_promotion_fails(self):
        errors = self.errors(
            lambda d: d["narrowed_hypothesis"].__setitem__("state", "PROVEN_REUSABLE")
        )
        self.assertTrue(any("escaped HYPOTHESIS" in e for e in errors))

    def test_discovery_side_native_provenance_claim_fails(self):
        errors = self.errors(
            lambda d: d["narrowed_hypothesis"]["rejected_or_not_supported"].remove(
                "Discovery-side records as substitutes for native consumer provenance."
            )
        )
        self.assertTrue(any("required negative findings" in e for e in errors))

    def test_falsifier_subject_drift_fails(self):
        errors = self.errors(
            lambda d: d["falsifier_subjects"][0].__setitem__("ref", "main")
        )
        self.assertTrue(any("exact immutable ref" in e for e in errors))

    def test_removing_negative_pr_fails(self):
        errors = self.errors(lambda d: d["falsifier_subjects"].pop(2))
        self.assertTrue(any("exactly four falsifier" in e for e in errors))

    def test_promotion_after_falsifier_round_fails(self):
        errors = self.errors(
            lambda d: d["prior_experiment_reassessment"][0].__setitem__("promotion", "YES")
        )
        self.assertTrue(any("promotion must remain NO" in e for e in errors))

    def test_claim_ceiling_widening_fails(self):
        errors = self.errors(
            lambda d: d.__setitem__("claim_ceiling", "PROVEN_REUSABLE")
        )
        self.assertTrue(any("claim ceiling widened" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
