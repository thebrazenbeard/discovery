from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA = "DISCOVERY_PORTFOLIO_SNAPSHOT_V1"


class ComparisonError(ValueError):
    pass


def load_snapshot(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ComparisonError("snapshot must be an object")
    return payload


def _public_map(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    repositories = snapshot.get("public_repositories")
    if not isinstance(repositories, list):
        raise ComparisonError("public_repositories must be a list")
    result: dict[str, dict[str, Any]] = {}
    for item in repositories:
        if not isinstance(item, dict):
            raise ComparisonError("public repository item must be an object")
        name = item.get("name")
        if not isinstance(name, str) or not name:
            raise ComparisonError("public repository item missing name")
        if name in result:
            raise ComparisonError(f"duplicate public repository: {name}")
        result[name] = item
    return result


def compare_snapshots(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    if old.get("schema") != SCHEMA or new.get("schema") != SCHEMA:
        raise ComparisonError("both inputs must be DISCOVERY_PORTFOLIO_SNAPSHOT_V1")

    old_public = _public_map(old)
    new_public = _public_map(new)

    old_names = set(old_public)
    new_names = set(new_public)
    added = sorted(new_names - old_names)
    removed = sorted(old_names - new_names)

    moved: list[dict[str, Any]] = []
    for name in sorted(old_names & new_names):
        before = old_public[name]
        after = new_public[name]
        changes: dict[str, Any] = {}
        for field in ("default_branch", "exact_commit", "exact_tree", "archived"):
            if before.get(field) != after.get(field):
                changes[field] = {
                    "before": before.get(field),
                    "after": after.get(field),
                }
        if changes:
            moved.append({"name": name, "changes": changes})

    old_private = old.get("private_inventory_commitment")
    new_private = new.get("private_inventory_commitment")
    if not isinstance(old_private, dict) or not isinstance(new_private, dict):
        raise ComparisonError("private inventory commitment missing")

    old_all = old.get("all_inventory_commitment")
    new_all = new.get("all_inventory_commitment")
    if not isinstance(old_all, dict) or not isinstance(new_all, dict):
        raise ComparisonError("all inventory commitment missing")

    private_state = "UNKNOWN"
    if old_private.get("key_id") == new_private.get("key_id") and old_private.get("key_id"):
        private_state = (
            "CHANGED"
            if old_private.get("hmac_sha256") != new_private.get("hmac_sha256")
            else "UNCHANGED"
        )
    elif old_private.get("count") == 0 and new_private.get("count") == 0:
        private_state = "UNCHANGED"
    else:
        private_state = "KEY_CHANGED_OR_UNCOMPARABLE"

    all_state = "UNKNOWN"
    if old_all.get("key_id") == new_all.get("key_id") and old_all.get("key_id"):
        all_state = (
            "CHANGED"
            if old_all.get("hmac_sha256") != new_all.get("hmac_sha256")
            else "UNCHANGED"
        )
    else:
        all_state = "KEY_CHANGED_OR_UNCOMPARABLE"

    old_counts = old.get("counts")
    new_counts = new.get("counts")
    if not isinstance(old_counts, dict) or not isinstance(new_counts, dict):
        raise ComparisonError("snapshot counts missing")
    counts_changed = old_counts != new_counts

    invalidation_reasons: list[str] = []
    if added or removed:
        invalidation_reasons.append("PUBLIC_REPOSITORY_SET_CHANGED")
    if moved:
        invalidation_reasons.append("PUBLIC_EXACT_SUBJECT_CHANGED")
    if counts_changed:
        invalidation_reasons.append("PORTFOLIO_COUNTS_CHANGED")
    if private_state == "CHANGED":
        invalidation_reasons.append("PRIVATE_REPOSITORY_SET_CHANGED")
    elif private_state == "KEY_CHANGED_OR_UNCOMPARABLE":
        invalidation_reasons.append("PRIVATE_REPOSITORY_SET_CURRENTNESS_UNVERIFIABLE")
    if all_state == "CHANGED":
        invalidation_reasons.append("ALL_REPOSITORY_SET_CHANGED")
    elif all_state == "KEY_CHANGED_OR_UNCOMPARABLE":
        invalidation_reasons.append("ALL_REPOSITORY_SET_CURRENTNESS_UNVERIFIABLE")

    currentness = "STALE" if invalidation_reasons else "CURRENT_RELATIVE_TO_NEW_SNAPSHOT"

    return {
        "schema": "DISCOVERY_PORTFOLIO_SNAPSHOT_COMPARISON_V1",
        "status": "READ_ONLY_CURRENTNESS_COMPARISON",
        "old_observed_at": old.get("observed_at"),
        "new_observed_at": new.get("observed_at"),
        "currentness": currentness,
        "invalidation_reasons": invalidation_reasons,
        "public_changes": {
            "added": added,
            "removed": removed,
            "moved": moved,
        },
        "private_set_state": private_state,
        "all_set_state": all_state,
        "count_change": {
            "changed": counts_changed,
            "before": old_counts,
            "after": new_counts,
        },
        "claim_ceiling": (
            "SNAPSHOT_CURRENTNESS_ONLY_NO_CAUSALITY_NO_PROJECT_AUTHORITY_"
            "NO_AUTOMATIC_PATCH_OR_PROMOTION"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare two Discovery public-safe portfolio snapshots."
    )
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    try:
        result = compare_snapshots(load_snapshot(args.old), load_snapshot(args.new))
    except ComparisonError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
