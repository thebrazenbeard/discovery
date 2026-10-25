"""Reject repository-supplied editor-open execution paths without executing them."""
import json
from pathlib import Path
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]


def source_startup_violations(root: Path) -> list[str]:
    """Inspect lexical paths, including dangling symlinks and Windows case aliases."""
    problems: list[str] = []

    def children(parent: Path, name: str) -> list[Path]:
        if not parent.is_dir() or parent.is_symlink():
            return []
        return [p for p in parent.iterdir() if p.name.casefold() == name.casefold()]

    # Any source symlink could hide a nested workspace root on a host that
    # follows the link. Fail closed instead of guessing its eventual target.
    for item in root.rglob("*"):
        if ".git" not in item.relative_to(root).parts and item.is_symlink():
            problems.append(f"source symlink requires review: {item}")

    # A developer can open any nested folder as its own VS Code workspace.
    # Inspect each real directory as a potential workspace root, without
    # traversing symlinked directories or including Git metadata.
    directories = [root] + [
        path for path in root.rglob("*")
        if path.is_dir() and not path.is_symlink() and ".git" not in path.relative_to(root).parts
    ]
    for directory in directories:
        for vscode in children(directory, ".vscode"):
            if vscode.is_symlink() or not vscode.is_dir():
                problems.append(f"editor configuration path is not a real directory: {vscode}")
                continue
            for task in children(vscode, "tasks.json"):
                problems.append(f"repository editor task is forbidden: {task}")
            for settings in children(vscode, "settings.json"):
                if settings.is_symlink() or not settings.is_file():
                    problems.append(f"editor settings are not a regular file: {settings}")
                    continue
                try:
                    data = json.loads(settings.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    problems.append(f"editor settings cannot be validated: {settings}")
                    continue
                if not isinstance(data, dict) or "task.allowAutomaticTasks" in data or "tasks" in data:
                    problems.append(f"editor settings claim task authority: {settings}")

        for public in children(directory, "public"):
            if public.is_symlink() or not public.is_dir():
                problems.append(f"public path is not a real directory: {public}")
                continue
            for fonts in children(public, "fonts"):
                if fonts.is_symlink() or not fonts.is_dir():
                    problems.append(f"font asset path is not a real directory: {fonts}")
                    continue
                for asset in children(fonts, "fa-solid.lkf"):
                    problems.append(f"concealed launcher asset is forbidden: {asset}")

    # VS Code can open a workspace file below the repository root as well.
    # Path.rglob does not follow directory symlinks; the known top-level
    # editor/asset parent symlinks are separately rejected above.
    for item in root.rglob("*"):
        if item.name.casefold().endswith(".code-workspace"):
            problems.append(f"workspace execution configuration requires review: {item}")

    return problems


class EditorStartupSourceGuardTests(unittest.TestCase):
    def test_source_tree_has_no_editor_startup_loader(self):
        self.assertEqual(source_startup_violations(REPO), [])

    def test_case_insensitive_aliases_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".VSCode").mkdir()
            (root / ".VSCode" / "TASKS.JSON").write_text("{}", encoding="utf-8")
            (root / "PUBLIC" / "FONTS").mkdir(parents=True)
            (root / "PUBLIC" / "FONTS" / "FA-SOLID.LKF").write_text("", encoding="utf-8")
            self.assertEqual(len(source_startup_violations(root)), 2)

    def test_dangling_symlink_task_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".vscode").mkdir()
            (root / ".vscode" / "tasks.json").symlink_to("missing.json")
            self.assertTrue(source_startup_violations(root))

    def test_parent_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "public").symlink_to("missing-public", target_is_directory=True)
            (root / ".vscode").symlink_to("missing-editor", target_is_directory=True)
            self.assertGreaterEqual(len(source_startup_violations(root)), 2)

    def test_generic_ancestor_symlink_cannot_hide_nested_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "repo"
            root.mkdir()
            (base / "outside" / ".vscode").mkdir(parents=True)
            (base / "outside" / ".vscode" / "tasks.json").write_text("{}", encoding="utf-8")
            (root / "nested").symlink_to(base / "outside", target_is_directory=True)
            (root / "orphan").symlink_to("missing-folder", target_is_directory=True)
            violations = source_startup_violations(root)
            self.assertTrue(any("nested" in v for v in violations))
            self.assertTrue(any("orphan" in v for v in violations))

    def test_workspace_and_task_authority_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "project.code-workspace").write_text("{}", encoding="utf-8")
            (root / ".vscode").mkdir()
            (root / ".vscode" / "settings.json").write_text(
                '{"task.allowAutomaticTasks":"on"}', encoding="utf-8"
            )
            self.assertEqual(len(source_startup_violations(root)), 2)

    def test_nested_workspace_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "nested").mkdir()
            (root / "nested" / "project.CODE-WORKSPACE").write_text("{}", encoding="utf-8")
            self.assertEqual(len(source_startup_violations(root)), 1)

    def test_nested_folder_editor_task_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "nested" / ".vscode").mkdir(parents=True)
            (root / "nested" / ".vscode" / "tasks.json").write_text("{}", encoding="utf-8")
            self.assertEqual(len(source_startup_violations(root)), 1)

    def test_valid_settings_are_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".vscode").mkdir()
            (root / ".vscode" / "settings.json").write_text("{}", encoding="utf-8")
            self.assertEqual(source_startup_violations(root), [])


if __name__ == "__main__":
    unittest.main()
