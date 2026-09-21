from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.validate_hc_transcendence_overlay import _files, git_tree_sha, load_json


ROOT = Path(__file__).resolve().parents[1]
OLD_BASE = ROOT / "experiments" / "hc_transcendence" / "HC_MAIN_TREE_V1.json"
NEW_BASE = ROOT / "experiments" / "hc_transcendence" / "HC_FRONTIER_TREE_V1.json"
TARGET = ROOT / "experiments" / "hc_transcendence" / "TRANSCENDENCE_FRONTIER_TREE_V1.json"
RESULT = ROOT / "experiments" / "hc_transcendence" / "HC_TRANSCENDENCE_BASE_UPGRADE_V1.json"


def _overlay(
    base: dict[str, dict[str, Any]],
    target: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    deletes: list[dict[str, Any]] = []
    overwrites: list[dict[str, Any]] = []
    adds: list[dict[str, Any]] = []
    shared: list[dict[str, Any]] = []

    for path, base_row in base.items():
        target_row = target.get(path)
        if target_row is None:
            deletes.append(base_row)
        elif (
            base_row["mode"] == target_row["mode"]
            and base_row["sha"] == target_row["sha"]
        ):
            shared.append(target_row)
        else:
            overwrites.append(
                {"path": path, "base": base_row, "target": target_row}
            )

    for path, target_row in target.items():
        if path not in base:
            adds.append(target_row)

    return {
        "deletes": deletes,
        "overwrites": overwrites,
        "adds": adds,
        "shared": shared,
    }


def _signatures(overlay: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for row in overlay["deletes"]:
        out[row["path"]] = f"DELETE:{row['mode']}:{row['sha']}"
    for row in overlay["overwrites"]:
        base = row["base"]
        target = row["target"]
        out[row["path"]] = (
            f"OVERWRITE:{base['mode']}:{base['sha']}"
            f"->{target['mode']}:{target['sha']}"
        )
    for row in overlay["adds"]:
        out[row["path"]] = f"ADD:{row['mode']}:{row['sha']}"
    return out


def validate_upgrade() -> dict[str, Any]:
    old_snapshot = load_json(OLD_BASE)
    new_snapshot = load_json(NEW_BASE)
    target_snapshot = load_json(TARGET)
    expected = load_json(RESULT)

    old_base = _files(old_snapshot)
    new_base = _files(new_snapshot)
    target = _files(target_snapshot)

    if git_tree_sha(old_base) != old_snapshot["tree"]:
        raise ValueError("old HC base snapshot tree mismatch")
    if git_tree_sha(new_base) != new_snapshot["tree"]:
        raise ValueError("new HC base snapshot tree mismatch")
    if git_tree_sha(target) != target_snapshot["tree"]:
        raise ValueError("Transcendence target snapshot tree mismatch")

    old_overlay = _overlay(old_base, target)
    new_overlay = _overlay(new_base, target)
    old_sig = _signatures(old_overlay)
    new_sig = _signatures(new_overlay)

    paths = sorted(set(old_sig) | set(new_sig))
    changes = [
        {
            "path": path,
            "old_instruction": old_sig.get(path),
            "new_instruction": new_sig.get(path),
        }
        for path in paths
        if old_sig.get(path) != new_sig.get(path)
    ]

    changed_base_paths = []
    for path in sorted(set(old_base) | set(new_base)):
        old = old_base.get(path)
        new = new_base.get(path)
        if old == new:
            continue
        target_row = target.get(path)
        changed_base_paths.append(
            {
                "path": path,
                "target_inherits_old_base": bool(old and target_row and old["mode"] == target_row["mode"] and old["sha"] == target_row["sha"]),
                "target_inherits_new_base": bool(new and target_row and new["mode"] == target_row["mode"] and new["sha"] == target_row["sha"]),
            }
        )

    def payload_bytes(overlay: dict[str, Any]) -> int:
        return sum(row["target"]["size"] for row in overlay["overwrites"]) + sum(
            row["size"] for row in overlay["adds"]
        )

    observed = {
        "old_overlay": {
            "delete_files": len(old_overlay["deletes"]),
            "overwrite_files": len(old_overlay["overwrites"]),
            "add_files": len(old_overlay["adds"]),
            "instruction_count": len(old_sig),
            "payload_files": len(old_overlay["overwrites"]) + len(old_overlay["adds"]),
            "payload_bytes": payload_bytes(old_overlay),
        },
        "new_overlay": {
            "delete_files": len(new_overlay["deletes"]),
            "overwrite_files": len(new_overlay["overwrites"]),
            "add_files": len(new_overlay["adds"]),
            "instruction_count": len(new_sig),
            "payload_files": len(new_overlay["overwrites"]) + len(new_overlay["adds"]),
            "payload_bytes": payload_bytes(new_overlay),
        },
        "churn": {
            "base_changed_paths": len(changed_base_paths),
            "overlay_instruction_changes": len(changes),
            "unchanged_current_overlay_instructions": len(new_sig) - len(changes),
            "current_overlay_instruction_churn_share": len(changes) / len(new_sig),
            "newly_required_deletions": sum(
                1
                for row in changes
                if row["old_instruction"] is None
                and (row["new_instruction"] or "").startswith("DELETE:")
            ),
            "shared_target_paths_touched_by_base_upgrade": sum(
                1
                for row in changed_base_paths
                if row["target_inherits_old_base"] or row["target_inherits_new_base"]
            ),
        },
    }

    for section in ("old_overlay", "new_overlay", "churn"):
        for key, value in observed[section].items():
            expected_value = expected[section if section != "churn" else "churn"][key]
            if value != expected_value:
                raise ValueError(
                    f"upgrade result mismatch {section}.{key}: "
                    f"{value!r} != {expected_value!r}"
                )

    if changes != expected["changed_overlay_instructions"]:
        raise ValueError("changed overlay instruction list mismatch")

    return {
        "status": "BASE_UPGRADE_SIMULATION_PASS",
        "old_base_tree": old_snapshot["tree"],
        "new_base_tree": new_snapshot["tree"],
        "target_tree": target_snapshot["tree"],
        "overlay_instruction_changes": len(changes),
        "newly_required_deletions": observed["churn"]["newly_required_deletions"],
        "payload_bytes_before": observed["old_overlay"]["payload_bytes"],
        "payload_bytes_after": observed["new_overlay"]["payload_bytes"],
        "shared_target_paths_touched": observed["churn"]["shared_target_paths_touched_by_base_upgrade"],
    }


def main() -> int:
    print(json.dumps(validate_upgrade(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
