from __future__ import annotations

import json
from pathlib import Path
import unittest

from tools.validate_hc_transcendence_overlay import (
    BASE,
    OVERLAY,
    TARGET,
    _files,
    git_tree_sha,
    load_json,
    reconstruct,
    validate,
)


class HCTranscendenceOverlayTests(unittest.TestCase):
    def test_snapshots_recompute_exact_bound_git_trees(self):
        base = load_json(BASE)
        target = load_json(TARGET)
        self.assertEqual(
            git_tree_sha(_files(base)),
            "e4c7fcedaa77cf5d2794491a99326db67740a272",
        )
        self.assertEqual(
            git_tree_sha(_files(target)),
            "112a44d8042556b87f19b3dac05ec34a5ea2f796",
        )

    def test_overlay_reconstructs_exact_target_tree(self):
        reconstructed, overlay = reconstruct()
        self.assertEqual(len(reconstructed), 288)
        self.assertEqual(
            git_tree_sha(reconstructed),
            overlay["target"]["tree"],
        )
        self.assertEqual(
            overlay["target"]["tree"],
            "112a44d8042556b87f19b3dac05ec34a5ea2f796",
        )

    def test_current_overlap_metrics_are_exact(self):
        overlay = load_json(OVERLAY)
        metrics = overlay["metrics"]
        self.assertEqual(metrics["base_files"], 302)
        self.assertEqual(metrics["target_files"], 288)
        self.assertEqual(metrics["identical_same_path_files"], 254)
        self.assertEqual(metrics["identical_same_path_bytes"], 1706224)
        self.assertEqual(metrics["overlay_payload_files"], 34)
        self.assertEqual(metrics["overlay_payload_bytes"], 286362)
        self.assertEqual(metrics["delete_files"], 39)
        self.assertAlmostEqual(
            metrics["identical_byte_share_of_target"],
            0.8562862531403914,
        )
        self.assertAlmostEqual(
            metrics["overlay_payload_share_of_target"],
            0.14371374685960858,
        )

    def test_overlay_is_pinned_not_moving_base(self):
        overlay = load_json(OVERLAY)
        self.assertEqual(
            overlay["base"]["commit"],
            "5929da3e8904e23e484df0deac920a008ec33d52",
        )
        self.assertEqual(
            overlay["base"]["tree"],
            "e4c7fcedaa77cf5d2794491a99326db67740a272",
        )
        self.assertEqual(
            overlay["target"]["commit"],
            "be3785c83dbe89b0d4236b43eda97a277eb6baad",
        )
        self.assertEqual(
            overlay["target"]["tree"],
            "112a44d8042556b87f19b3dac05ec34a5ea2f796",
        )

    def test_deletion_manifest_blocks_silent_hc_feature_import(self):
        overlay = load_json(OVERLAY)
        deletes = {row["path"] for row in overlay["deletes"]}
        self.assertIn("runtime/cognitive_core/cognitive_loop.py", deletes)
        self.assertIn("runtime/cognitive_core/motor_control.py", deletes)
        self.assertIn("runtime/reference_kernel/governed_kernel_v2.py", deletes)
        self.assertIn("tools/validate_hc_architecture.py", deletes)

    def test_transcendence_specific_overlay_remains_distinct(self):
        overlay = load_json(OVERLAY)
        adds = {row["path"] for row in overlay["adds"]}
        self.assertIn("runtime/transcendence_core/core.py", adds)
        self.assertIn("specs/transcendence/hcsa-v0.schema.json", adds)
        self.assertIn("docs/transcendence/CONTINUITY_BOUNDARIES.md", adds)
        self.assertIn("docs/imported-hc/PROVENANCE.md", adds)

    def test_validator_reports_exact_pass_without_adoption_claim(self):
        result = validate()
        self.assertEqual(result["status"], "EXACT_TREE_RECONSTRUCTION_PASS")
        overlay = load_json(OVERLAY)
        self.assertIn("NOT_DEPENDENCY_ADOPTION", overlay["authority_ceiling"])


if __name__ == "__main__":
    unittest.main()
