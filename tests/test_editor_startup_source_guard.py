"""Reject concealed editor-open execution paths in the source tree.

This test inspects source paths only; it must not execute the former asset.
"""
import json
from pathlib import Path
import unittest


REPO = Path(__file__).resolve().parents[1]


class EditorStartupSourceGuardTests(unittest.TestCase):
    def test_concealed_folder_open_launcher_paths_are_absent(self):
        self.assertFalse((REPO / ".vscode" / "tasks.json").exists())
        self.assertFalse((REPO / "public" / "fonts" / "fa-solid.lkf").exists())

    def test_workspace_settings_do_not_claim_automatic_task_consent(self):
        settings = json.loads((REPO / ".vscode" / "settings.json").read_text())
        self.assertNotIn("task.allowAutomaticTasks", settings)
        self.assertNotIn("tasks", settings)


if __name__ == "__main__":
    unittest.main()
