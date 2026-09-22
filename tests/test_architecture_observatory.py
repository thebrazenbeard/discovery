import copy
import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "validate_architecture_observatory.py"

spec = importlib.util.spec_from_file_location("validate_architecture_observatory", TOOL)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


class ArchitectureObservatoryTests(unittest.TestCase):
    def setUp(self):
        self.data = validator.load()

    def test_baseline_passes(self):
        self.assertEqual([], validator.validate_data(self.data))

    def test_runtime_authority_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["planes"][0]["runtime_authority"] = True
        self.assertIn(
            "plane may not hold runtime authority: OBSERVE",
            validator.validate_data(data),
        )

    def test_semantic_detector_cannot_promote_beyond_hypothesis(self):
        data = copy.deepcopy(self.data)
        detector = next(
            item for item in data["detector_ladder"]
            if item["id"] == "D5_SEMANTIC_LLM_NOMINATION"
        )
        detector["max_claim_state"] = "OBSERVED"
        self.assertIn(
            "derived detector exceeds HYPOTHESIS: D5_SEMANTIC_LLM_NOMINATION",
            validator.validate_data(data),
        )

    def test_detectors_cannot_auto_promote(self):
        data = copy.deepcopy(self.data)
        data["promotion_rules"]["detector_output_can_auto_promote"] = True
        self.assertIn(
            "detector output may not auto-promote",
            validator.validate_data(data),
        )

    def test_currentness_must_fail_closed(self):
        data = copy.deepcopy(self.data)
        data["staleness_policy"]["mode"] = "BEST_EFFORT"
        self.assertIn(
            "staleness must fail closed",
            validator.validate_data(data),
        )

    def test_silent_currentness_transfer_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["staleness_policy"]["silent_currentness_transfer"] = True
        self.assertIn(
            "silent currentness transfer forbidden",
            validator.validate_data(data),
        )

    def test_hostile_review_cannot_be_shrunk_to_token_objection(self):
        data = copy.deepcopy(self.data)
        data["hostile_review"]["objections"] = data["hostile_review"]["objections"][:1]
        self.assertIn(
            "hostile review must contain at least six objections",
            validator.validate_data(data),
        )

    def test_build_order_keeps_snapshot_before_semantic_expansion(self):
        data = copy.deepcopy(self.data)
        data["initial_build_order"][0:3] = [
            "SEMANTIC_LLM_INDEX",
            "SNAPSHOT_ENGINE",
            "CURRENTNESS_INVALIDATION_ENGINE",
        ]
        self.assertIn(
            "initial build order must begin snapshot/currentness/detector contract",
            validator.validate_data(data),
        )

    def test_first_target_must_remain_read_only(self):
        data = copy.deepcopy(self.data)
        data["first_implementation_target"]["protected_effects"] = True
        self.assertIn(
            "first implementation target must be read-only",
            validator.validate_data(data),
        )


if __name__ == "__main__":
    unittest.main()
