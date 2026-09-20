from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments" / "hc_transcendence" / "HC_FRONTIER_TREE_V1.json"
TARGET = ROOT / "experiments" / "hc_transcendence" / "TRANSCENDENCE_FRONTIER_TREE_V1.json"
OVERLAY = ROOT / "experiments" / "hc_transcendence" / "HC_TRANSCENDENCE_OVERLAY_V1.json"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _files(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = snapshot.get("files")
    if not isinstance(rows, list):
        raise ValueError("snapshot files must be an array")
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("snapshot file row must be an object")
        path = row.get("path")
        mode = row.get("mode")
        sha = row.get("sha")
        size = row.get("size")
        if not isinstance(path, str) or not path or path.startswith("/") or ".." in Path(path).parts:
            raise ValueError(f"invalid snapshot path: {path!r}")
        if path in out:
            raise ValueError(f"duplicate snapshot path: {path}")
        if mode not in {"100644", "100755", "120000"}:
            raise ValueError(f"unsupported blob mode for {path}: {mode!r}")
        if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
            raise ValueError(f"invalid Git blob SHA for {path}")
        if type(size) is not int or size < 0:
            raise ValueError(f"invalid blob size for {path}")
        out[path] = {"path": path, "mode": mode, "sha": sha, "size": size}
    return out


def _git_object_sha(kind: str, payload: bytes) -> str:
    header = f"{kind} {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def git_tree_sha(files: dict[str, dict[str, Any]]) -> str:
    root: dict[str, Any] = {}
    for path, row in files.items():
        parts = path.split("/")
        node = root
        for part in parts[:-1]:
            existing = node.get(part)
            if existing is None:
                existing = {}
                node[part] = existing
            if not isinstance(existing, dict) or "_blob" in existing:
                raise ValueError(f"path collision while constructing tree: {path}")
            node = existing
        leaf = parts[-1]
        if leaf in node:
            raise ValueError(f"path collision while constructing tree: {path}")
        node[leaf] = {"_blob": row}

    def hash_node(node: dict[str, Any]) -> str:
        entries: list[tuple[bytes, bytes]] = []
        for name, child in node.items():
            name_bytes = name.encode("utf-8")
            if isinstance(child, dict) and "_blob" in child:
                row = child["_blob"]
                mode = row["mode"]
                sha = row["sha"]
                sort_key = name_bytes + b"\0"
            else:
                mode = "40000"
                sha = hash_node(child)
                sort_key = name_bytes + b"/"
            entry = (
                f"{mode} ".encode("ascii")
                + name_bytes
                + b"\0"
                + bytes.fromhex(sha)
            )
            entries.append((sort_key, entry))
        payload = b"".join(entry for _, entry in sorted(entries, key=lambda item: item[0]))
        return _git_object_sha("tree", payload)

    return hash_node(root)


def reconstruct() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    base = load_json(BASE)
    target = load_json(TARGET)
    overlay = load_json(OVERLAY)

    if base.get("schema") != "DISCOVERY_GIT_TREE_SNAPSHOT_V1":
        raise ValueError("base snapshot schema mismatch")
    if target.get("schema") != "DISCOVERY_GIT_TREE_SNAPSHOT_V1":
        raise ValueError("target snapshot schema mismatch")
    if overlay.get("schema") != "DISCOVERY_EXACT_BASE_OVERLAY_V1":
        raise ValueError("overlay schema mismatch")

    base_files = _files(base)
    target_files = _files(target)

    if git_tree_sha(base_files) != base["tree"]:
        raise ValueError("base snapshot does not reconstruct its bound Git tree")
    if git_tree_sha(target_files) != target["tree"]:
        raise ValueError("target snapshot does not reconstruct its bound Git tree")
    if overlay["base"]["commit"] != base["commit"] or overlay["base"]["tree"] != base["tree"]:
        raise ValueError("overlay base binding mismatch")
    if overlay["target"]["commit"] != target["commit"] or overlay["target"]["tree"] != target["tree"]:
        raise ValueError("overlay target binding mismatch")

    reconstructed = {path: dict(row) for path, row in base_files.items()}

    for row in overlay["deletes"]:
        path = row["path"]
        current = reconstructed.get(path)
        if current is None:
            raise ValueError(f"delete path absent from base: {path}")
        for field in ("mode", "sha", "size"):
            if current[field] != row[field]:
                raise ValueError(f"delete preimage mismatch for {path}: {field}")
        del reconstructed[path]

    for row in overlay["overwrites"]:
        path = row["path"]
        current = reconstructed.get(path)
        if current is None:
            raise ValueError(f"overwrite path absent from base: {path}")
        if current["mode"] != row["base_mode"] or current["sha"] != row["base_sha"]:
            raise ValueError(f"overwrite preimage mismatch: {path}")
        target_row = target_files.get(path)
        if target_row is None:
            raise ValueError(f"overwrite path absent from target: {path}")
        if (
            target_row["mode"] != row["target_mode"]
            or target_row["sha"] != row["target_sha"]
            or target_row["size"] != row["target_size"]
        ):
            raise ValueError(f"overwrite target mismatch: {path}")
        reconstructed[path] = dict(target_row)

    for row in overlay["adds"]:
        path = row["path"]
        if path in reconstructed:
            raise ValueError(f"add path already exists after overlay: {path}")
        target_row = target_files.get(path)
        if target_row != row:
            raise ValueError(f"add target mismatch: {path}")
        reconstructed[path] = dict(row)

    if reconstructed != target_files:
        missing = sorted(set(target_files) - set(reconstructed))
        extra = sorted(set(reconstructed) - set(target_files))
        changed = sorted(
            path
            for path in set(reconstructed) & set(target_files)
            if reconstructed[path] != target_files[path]
        )
        raise ValueError(
            f"overlay reconstruction mismatch missing={missing} extra={extra} changed={changed}"
        )

    reconstructed_tree = git_tree_sha(reconstructed)
    if reconstructed_tree != target["tree"]:
        raise ValueError(
            f"reconstructed tree mismatch: {reconstructed_tree} != {target['tree']}"
        )

    return reconstructed, overlay


def validate() -> dict[str, Any]:
    reconstructed, overlay = reconstruct()
    metrics = overlay["metrics"]
    if metrics["target_files"] != len(reconstructed):
        raise ValueError("target file metric mismatch")
    if metrics["identical_same_path_files"] + metrics["overwrite_files"] + metrics["add_files"] != metrics["target_files"]:
        raise ValueError("target partition metric mismatch")
    if metrics["overlay_payload_files"] != metrics["overwrite_files"] + metrics["add_files"]:
        raise ValueError("overlay payload file metric mismatch")
    if metrics["overlay_payload_bytes"] != metrics["overwrite_bytes"] + metrics["add_bytes"]:
        raise ValueError("overlay payload byte metric mismatch")
    return {
        "status": "EXACT_TREE_RECONSTRUCTION_PASS",
        "base_tree": overlay["base"]["tree"],
        "target_tree": overlay["target"]["tree"],
        "target_files": metrics["target_files"],
        "shared_files": metrics["identical_same_path_files"],
        "overlay_payload_files": metrics["overlay_payload_files"],
        "overlay_payload_bytes": metrics["overlay_payload_bytes"],
        "delete_files": metrics["delete_files"],
    }


def main() -> int:
    print(json.dumps(validate(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
