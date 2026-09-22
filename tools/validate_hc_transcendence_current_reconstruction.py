from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "experiments" / "HC_TRANSCENDENCE_CURRENT_TREE_RECONSTRUCTION_V1.json"
BASE_FILEMAP = (
    ROOT
    / "experiments"
    / "hc_transcendence_current_reconstruction_v1"
    / "HC_BASE_FILEMAP.json"
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _tree_sha(entries: list[dict]) -> str:
    root = {"dirs": {}, "files": {}}

    for entry in entries:
        path = entry["path"]
        parts = path.split("/")
        node = root
        for part in parts[:-1]:
            node = node["dirs"].setdefault(part, {"dirs": {}, "files": {}})
        node["files"][parts[-1]] = {
            "mode": entry["mode"],
            "sha": entry["sha"],
            "type": entry.get("type", "blob"),
        }

    def calculate(node: dict) -> str:
        children = []
        for name, item in node["files"].items():
            children.append(
                {
                    "name": name,
                    "sort_key": name.encode("utf-8"),
                    "mode": item["mode"].lstrip("0") or "0",
                    "sha": item["sha"],
                }
            )
        for name, child in node["dirs"].items():
            children.append(
                {
                    "name": name,
                    "sort_key": (name + "/").encode("utf-8"),
                    "mode": "40000",
                    "sha": calculate(child),
                }
            )
        children.sort(key=lambda item: item["sort_key"])

        payload = bytearray()
        for item in children:
            payload.extend(item["mode"].encode("ascii"))
            payload.extend(b" ")
            payload.extend(item["name"].encode("utf-8"))
            payload.extend(b"\x00")
            payload.extend(bytes.fromhex(item["sha"]))

        header = f"tree {len(payload)}\0".encode("ascii")
        return hashlib.sha1(header + payload).hexdigest()

    return calculate(root)


def validate_data(manifest: dict, base_snapshot: dict) -> list[str]:
    errors: list[str] = []

    if manifest.get("schema") != "DISCOVERY_HC_TRANSCENDENCE_CURRENT_TREE_RECONSTRUCTION_V1":
        errors.append("unexpected reconstruction manifest schema")
    if base_snapshot.get("schema") != "DISCOVERY_GIT_FILEMAP_SNAPSHOT_V1":
        errors.append("unexpected base filemap schema")

    base = manifest.get("base", {})
    target = manifest.get("target", {})
    counts = manifest.get("counts", {})
    operations = manifest.get("operations", {})
    expected = manifest.get("expected_result", {})
    entries = base_snapshot.get("entries")

    if not isinstance(entries, list):
        return errors + ["base filemap entries invalid"]

    if base_snapshot.get("repository") != base.get("repository"):
        errors.append("base repository binding mismatch")
    if base_snapshot.get("commit") != base.get("ref", "").split("@")[-1]:
        errors.append("base commit binding mismatch")
    if base_snapshot.get("tree_sha") != base.get("tree_sha"):
        errors.append("base tree binding mismatch")
    if base_snapshot.get("entry_count") != len(entries):
        errors.append("base filemap entry count mismatch")

    try:
        computed_base_tree = _tree_sha(entries)
    except (KeyError, TypeError, ValueError) as exc:
        return errors + [f"base tree computation failed: {exc}"]

    if computed_base_tree != base_snapshot.get("tree_sha"):
        errors.append("base filemap does not reproduce bound HC tree")
    if computed_base_tree != base.get("tree_sha"):
        errors.append("computed base tree does not match manifest base")

    by_path = {}
    for entry in entries:
        path = entry.get("path")
        if not isinstance(path, str) or not path:
            errors.append("base filemap path invalid")
            continue
        if path in by_path:
            errors.append(f"duplicate base path: {path}")
            continue
        by_path[path] = copy.deepcopy(entry)

    delete_paths = operations.get("delete_paths")
    overrides = operations.get("overrides")
    additions = operations.get("additions")
    if not isinstance(delete_paths, list):
        errors.append("delete_paths invalid")
        delete_paths = []
    if not isinstance(overrides, list):
        errors.append("overrides invalid")
        overrides = []
    if not isinstance(additions, list):
        errors.append("additions invalid")
        additions = []

    if len(delete_paths) != len(set(delete_paths)):
        errors.append("duplicate delete path")
    for path in delete_paths:
        if path not in by_path:
            errors.append(f"delete path absent from base: {path}")
            continue
        del by_path[path]

    seen_override_paths = set()
    for operation in overrides:
        path = operation.get("path")
        if path in seen_override_paths:
            errors.append(f"duplicate override path: {path}")
            continue
        seen_override_paths.add(path)
        current = by_path.get(path)
        if current is None:
            errors.append(f"override path absent after deletes: {path}")
            continue
        expected_from = operation.get("from", {})
        current_identity = {
            "mode": current.get("mode"),
            "type": current.get("type"),
            "sha": current.get("sha"),
        }
        if current_identity != expected_from:
            errors.append(f"override source identity mismatch: {path}")
            continue
        replacement = operation.get("to", {})
        if not all(isinstance(replacement.get(key), str) and replacement.get(key) for key in ("mode", "type", "sha")):
            errors.append(f"override target identity invalid: {path}")
            continue
        by_path[path] = {"path": path, **replacement}

    seen_add_paths = set()
    for addition in additions:
        path = addition.get("path")
        if path in seen_add_paths:
            errors.append(f"duplicate addition path: {path}")
            continue
        seen_add_paths.add(path)
        if path in by_path:
            errors.append(f"addition path already exists: {path}")
            continue
        if not all(isinstance(addition.get(key), str) and addition.get(key) for key in ("path", "mode", "type", "sha")):
            errors.append(f"addition identity invalid: {path}")
            continue
        by_path[path] = copy.deepcopy(addition)

    if counts.get("base_files") != len(entries):
        errors.append("base file count mismatch")
    if counts.get("deletes") != len(delete_paths):
        errors.append("delete count mismatch")
    if counts.get("overrides") != len(overrides):
        errors.append("override count mismatch")
    if counts.get("additions") != len(additions):
        errors.append("addition count mismatch")
    if counts.get("target_files") != len(by_path):
        errors.append("target file count mismatch")
    if counts.get("inherited_unchanged") != (
        len(by_path) - len(overrides) - len(additions)
    ):
        errors.append("inherited unchanged count mismatch")

    try:
        reconstructed_tree = _tree_sha(list(by_path.values()))
    except (KeyError, TypeError, ValueError) as exc:
        return errors + [f"reconstructed tree computation failed: {exc}"]

    target_tree = target.get("tree_sha")
    if reconstructed_tree != target_tree:
        errors.append("reconstructed tree does not match bound Transcendence tree")
    if reconstructed_tree != expected.get("reconstructed_tree_sha"):
        errors.append("reconstructed tree does not match expected result")
    if expected.get("exact_target_tree_match") is not True:
        errors.append("exact target tree match flag missing")

    return errors


def validate() -> list[str]:
    return validate_data(load(MANIFEST), load(BASE_FILEMAP))


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    manifest = load(MANIFEST)
    print(
        "PASS: HC -> Transcendence current-head reconstruction "
        f"{manifest['base']['tree_sha']} -> {manifest['target']['tree_sha']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
