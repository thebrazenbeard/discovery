from __future__ import annotations

import json
from pathlib import Path
import unittest

from tools.validate_hc_transcendence_upgrade import RESULT, validate_upgrade


class HCTranscendenceUpgradeTests(unittest.TestCase):
    def test_real_hc_base_upgrade_has_low_overlay_churn(self):
        result = validate_upgrade()
        self.assertEqual(result["status"], "BASE_UPGRADE_SIMULATION_PASS")
        self.assertEqual(result["overlay_instruction_changes"], 8)
        self.assertEqual(result["newly_required_deletions"], 2)
        self.assertEqual(result["payload_bytes_before"], 286362)
        self.assertEqual(result["payload_bytes_after"], 286362)

    def test_first_upgrade_does_not_touch_shared_inherited_target_bytes(self):
        result = validate_upgrade()
        self.assertEqual(result["shared_target_paths_touched"], 0)

    def test_upgrade_result_preserves_claim_ceiling(self):
        data = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(data["interpretation"]["result"], "LOW_CHURN_FIRST_UPGRADE")
        self.assertIn(
            "does not test conflict behavior",
            data["interpretation"]["limitation"],
        )
        self.assertTrue(
            data["claim_ceiling"].endswith("NOT_DEPENDENCY_ADOPTION")
        )

    def test_new_hc_motor_control_is_excluded_not_inherited(self):
        data = json.loads(RESULT.read_text(encoding="utf-8"))
        changed = {
            row["path"]: row
            for row in data["changed_overlay_instructions"]
        }
        self.assertIsNone(
            changed["runtime/cognitive_core/motor_control.py"]["old_instruction"]
        )
        self.assertTrue(
            changed["runtime/cognitive_core/motor_control.py"]["new_instruction"].startswith(
                "DELETE:"
            )
        )
        self.assertIsNone(
            changed["runtime/cognitive_core/test_motor_control.py"]["old_instruction"]
        )


if __name__ == "__main__":
    unittest.main()
