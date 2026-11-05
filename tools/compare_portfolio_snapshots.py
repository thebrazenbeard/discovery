from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SCHEMA = "DISCOVERY_PORTFOLIO_SNAPSHOT_V1"
STATUS = "OBSERVED_READ_ONLY_NOT_ARCHITECTURAL_AUTHORITY"
OID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
HEX_64 = re.compile(r"[0-9a-f]{64}\Z")
KEY_ID = re.compile(r"[0-9a-f]{16}\Z")


class ComparisonError(ValueError):
    pass


def load_snapshot(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ComparisonError("snapshot must be an object")
    return payload


def _nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ComparisonError(f"{field} must be a nonempty string")
    return value


def _count(value: Any, field: str) -> int:
    if type(value) is not int or value < 0:
        raise ComparisonError(f"{field} must be a nonnegative integer")
    return value


def _digest(value: Any, field: str, pattern: re.Pattern[str] = HEX_64) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ComparisonError(f"{field} has invalid hexadecimal identity")
    return value


def _observed_time(snapshot: dict[str, Any]) -> datetime:
    raw = _nonempty(snapshot.get("observed_at"), "observed_at")
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ComparisonError("observed_at must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ComparisonError("observed_at must include a timezone")
    return parsed


def _validate_commitment(value: Any, *, field: str, count: int) -> str | None:
    if not isinstance(value, dict):
        raise ComparisonError(f"{field} must be an object")
    if set(value) != {"scheme", "key_id", "hmac_sha256", "count", "publicly_recomputable"}:
        raise ComparisonError(f"{field} has missing or unexpected fields")
    if _count(value["count"], f"{field}.count") != count:
        raise ComparisonError(f"{field}.count contradicts public counts")
    if value["publicly_recomputable"] is not False:
        raise ComparisonError(f"{field} must not claim public recomputability")
    key_id, digest = value["key_id"], value["hmac_sha256"]
    if key_id is None:
        if value["scheme"] != "NONE" or digest is not None:
            raise ComparisonError(f"{field} has an unkeyed HMAC claim")
    else:
        _digest(key_id, f"{field}.key_id", KEY_ID)
        _digest(digest, f"{field}.hmac_sha256")
        # The V1 builder labels the empty-private-set scheme NONE even if a
        # caller supplied a key and an HMAC of that empty set.
        expected_scheme = (
            "NONE"
            if field.startswith("private") and count == 0
            else "HMAC_SHA256_PRIVATE_KEY_CANONICAL_V1"
        )
        if value["scheme"] != expected_scheme:
            raise ComparisonError(f"{field}.scheme contradicts keyed commitment")
    if count and field.startswith("private") and key_id is None:
        raise ComparisonError("nonempty private set requires a keyed commitment")
    return key_id


def _validate_snapshot(snapshot: dict[str, Any]) -> datetime:
    if snapshot.get("schema") != SCHEMA or snapshot.get("status") != STATUS:
        raise ComparisonError("invalid portfolio snapshot schema or status")
    for field in ("privacy_rule", "currentness_rule", "claim_ceiling"):
        _nonempty(snapshot.get(field), field)
    source = snapshot.get("source")
    if (
        not isinstance(source, dict)
        or source.get("kind") != "GITHUB_ACCESSIBLE_REPOSITORY_INVENTORY"
    ):
        raise ComparisonError("invalid source identity")
    if set(source) != {"kind", "owner", "acquisition_method"}:
        raise ComparisonError("source has missing or unexpected fields")
    _nonempty(source["owner"], "source.owner")
    _nonempty(source["acquisition_method"], "source.acquisition_method")
    observed = _observed_time(snapshot)

    counts = snapshot.get("counts")
    if not isinstance(counts, dict) or set(counts) != {"total", "public", "private"}:
        raise ComparisonError("snapshot counts must contain total/public/private")
    total, public, private = (
        _count(counts[k], f"counts.{k}")
        for k in ("total", "public", "private")
    )
    names = _public_map(snapshot)
    if len(names) != public or total != public + private:
        raise ComparisonError("snapshot counts contradict public repository membership")
    if len({name.casefold() for name in names}) != len(names):
        raise ComparisonError("case-insensitive duplicate public repository names")
    for name, item in names.items():
        if set(item) != {
            "name", "default_branch", "exact_commit", "exact_tree", "archived"
        }:
            raise ComparisonError(f"public repository {name} has missing or unexpected fields")
        _nonempty(item["default_branch"], f"{name}.default_branch")
        _digest(item["exact_commit"], f"{name}.exact_commit", OID)
        _digest(item["exact_tree"], f"{name}.exact_tree", OID)
        if type(item["archived"]) is not bool:
            raise ComparisonError(f"{name}.archived must be boolean")

    public_digest = snapshot.get("public_name_digest")
    if not isinstance(public_digest, dict) or set(public_digest) != {
        "scheme", "sha256", "publicly_recomputable"
    }:
        raise ComparisonError("invalid public name digest metadata")
    if (
        public_digest["scheme"] != "SHA256_SORTED_UTF8_NAMES_V1"
        or public_digest["publicly_recomputable"] is not True
    ):
        raise ComparisonError("unsupported public name digest scheme")
    claimed = _digest(public_digest["sha256"], "public_name_digest.sha256")
    computed = hashlib.sha256(
        "".join(f"{name}\n" for name in sorted(names)).encode("utf-8")
    ).hexdigest()
    if claimed != computed:
        raise ComparisonError("public name digest differs from public repository membership")

    private_key = _validate_commitment(
        snapshot.get("private_inventory_commitment"),
        field="private_inventory_commitment",
        count=private,
    )
    all_key = _validate_commitment(
        snapshot.get("all_inventory_commitment"),
        field="all_inventory_commitment",
        count=total,
    )
    if private_key != all_key:
        raise ComparisonError("private and all-set commitments use different key identities")
    return observed


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

    old_time = _validate_snapshot(old)
    new_time = _validate_snapshot(new)
    if old["source"]["owner"] != new["source"]["owner"]:
        raise ComparisonError("cannot compare snapshots from different GitHub owners")
    if new_time < old_time:
        raise ComparisonError("new snapshot predates old snapshot")

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
