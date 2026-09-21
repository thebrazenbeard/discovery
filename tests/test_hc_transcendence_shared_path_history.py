from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "experiments"
    / "hc_transcendence"
    / "HC_TRANSCENDENCE_SHARED_PATH_HISTORY_V1.json"
)


class HCTranscendenceSharedPathHistoryTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_real_transition_summary_is_exact(self):
        summary = self.data["summary"]
        self.assertEqual(summary["transitions"], 10)
        self.assertEqual(summary["child_matches_current_target"], 9)
        self.assertEqual(summary["overlay_instruction_removed"], 9)
        self.assertEqual(summary["residual_override_after_child"], 1)
        self.assertEqual(summary["transient_conflict_sequences"], 1)

    def test_executed_dataflow_conflict_is_transient_in_real_history(self):
        rows = {row["id"]: row for row in self.data["transitions"]}
        initial = rows["EXECUTED_DATAFLOW_INITIAL_ADD"]
        converged = rows["EXECUTED_DATAFLOW_PREPROCESSING_CONVERGENCE"]

        self.assertTrue(initial["residual_override"])
        self.assertFalse(initial["child_matches_current_target"])
        self.assertTrue(
            initial["old_overlay_instruction"].startswith("ADD:")
        )
        self.assertTrue(
            initial["new_overlay_instruction"].startswith("OVERWRITE:")
        )

        self.assertTrue(converged["child_matches_current_target"])
        self.assertTrue(converged["instruction_removed"])
        self.assertIsNone(converged["new_overlay_instruction"])

    def test_history_result_records_selection_bias(self):
        warning = self.data["interpretation"]["bias_warning"].lower()
        self.assertIn("conditioned on paths known to be shared", warning)
        self.assertIn("cannot estimate future conflict probability", warning)

    def test_history_does_not_invent_original_import_lineage(self):
        warning = self.data["interpretation"]["provenance_warning"]
        self.assertIn("does not establish the exact original upstream HC import commit", warning)
        self.assertIn("not claims about the historical import lineage", warning)


if __name__ == "__main__":
    unittest.main()
