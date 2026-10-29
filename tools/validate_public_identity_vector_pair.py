"""Fail-closed *structural* comparison of two complete GitHub public identity cuts.

This tool cannot authenticate collectors, determine whether two observations
were independently acquired, validate a profile's provenance, or admit a
Discovery baseline. In particular it cannot repair a historical one-vector
receipt by inferring the missing second vector from a count or a digest.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any


SCHEMA = "DISCOVERY_PUBLIC_IDENTITY_VECTOR_V1"
ANCHOR_SCHEMAS = {
    "DISCOVERY_READ_ONLY_PUBLIC_IDENTITY_PROBE_20261028",
    "DISCOVERY_PUBLIC_IDENTITY_ANCHOR_V1",
}
OWNER = "thebrazenbeard"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
NAME = re.compile(r"[A-Za-z0-9_.-]+\Z")


class VectorError(ValueError):
    """A source-level full-vector comparison could not be established."""


def _require(ok: bool, reason: str) -> None:
    if not ok:
        raise VectorError(reason)


def _unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    values = {}
    for key, value in pairs:
        _require(key not in values, f"duplicate JSON key: {key}")
        values[key] = value
    return values


def load_vector(path: Path) -> dict[str, Any]:
    content = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_keys)
    _require(isinstance(content, dict), "vector must be a JSON object")
    return content


def _utc(value: Any, name: str) -> datetime:
    _require(isinstance(value, str) and bool(value), f"{name} UTC time missing")
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise VectorError(f"{name} invalid UTC time") from exc
    _require(timestamp.tzinfo is not None and timestamp.utcoffset().total_seconds() == 0,
             f"{name} must be UTC")
    return timestamp.astimezone(timezone.utc)


def _subjects(raw: Any) -> list[tuple[int, str, str, str, str, bool]]:
    _require(isinstance(raw, list) and bool(raw), "complete subjects vector required")
    subjects = []
    names = []
    ids = []
    for index, item in enumerate(raw):
        _require(isinstance(item, dict), f"subject[{index}] must be an object")
        repo_id, name = item.get("id"), item.get("name")
        _require(type(repo_id) is int and repo_id > 0, f"subject[{index}] id invalid")
        _require(isinstance(name, str) and NAME.fullmatch(name) is not None,
                 f"subject[{index}] name invalid")
        branch = item.get("branch")
        _require(isinstance(branch, str) and bool(branch) and branch.strip() == branch
                 and not any(ord(c) < 32 for c in branch),
                 f"subject[{index}] branch invalid")
        for field in ("head", "tree"):
            _require(isinstance(item.get(field), str)
                     and HEX40.fullmatch(item[field]) is not None,
                     f"subject[{index}] {field} invalid")
        _require(type(item.get("archived")) is bool,
                 f"subject[{index}] archived invalid")
        ids.append(repo_id)
        names.append(name)
        subjects.append((repo_id, name, branch, item["head"], item["tree"], item["archived"]))
    _require(names == sorted(names), "subject names not sorted")
    _require(len({name.casefold() for name in names}) == len(names),
             "case-insensitive duplicate repository name")
    _require(len(set(ids)) == len(ids), "duplicate GitHub repository id")
    return subjects


def _checked(raw: Any, label: str) -> tuple[list[tuple[int, str, str, str, str, bool]], datetime, datetime]:
    _require(isinstance(raw, dict), f"{label} object required")
    _require(raw.get("schema") == SCHEMA, f"{label} schema mismatch")
    _require(raw.get("owner") == OWNER, f"{label} owner mismatch")
    _require(isinstance(raw.get("observation_id"), str) and bool(raw["observation_id"].strip()),
             f"{label} observation_id missing")
    profile = raw.get("source_profile_sha256")
    _require(isinstance(profile, str) and HEX64.fullmatch(profile) is not None,
             f"{label} source profile digest invalid")
    _require(raw.get("errors") == [], f"{label} collection errors must be empty")
    started, ended = _utc(raw.get("started_at_utc"), f"{label} started_at"), _utc(
        raw.get("ended_at_utc"), f"{label} ended_at")
    _require(started <= ended, f"{label} observation reversed")
    return _subjects(raw.get("subjects")), started, ended


def _checked_anchor(raw: Any) -> list[tuple[int, str, str, str, str, bool]]:
    """Bind to a *supplied* self-consistent reference; never authenticate it."""
    _require(isinstance(raw, dict) and raw.get("schema") in ANCHOR_SCHEMAS,
             "anchor schema invalid")
    _require(raw.get("owner") == OWNER, "anchor owner mismatch")
    _require(raw.get("not_admitted") is True, "anchor must be explicitly non-admitted")
    values = _subjects(raw.get("subjects"))
    for key in ("bound_exact_subjects", "B0_count", "B1_count"):
        _require(type(raw.get(key)) is int and raw[key] == len(values),
                 f"anchor {key} does not bind complete subject count")
    _require(type(raw.get("archived")) is int and raw["archived"] == sum(v[5] for v in values),
             "anchor archived count mismatch")
    digest = sha256((json.dumps(raw["subjects"], sort_keys=True, ensure_ascii=False,
                                separators=(",", ":")) + "\n").encode()).hexdigest()
    _require(raw.get("identity_digest_sha256") == digest,
             "anchor supplied identity digest inconsistent")
    return values


def compare_pair(
    b0: dict[str, Any], b1: dict[str, Any], *, anchor: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Prove local pair equality (and optional anchor equality), never admission."""
    subjects0, _, end0 = _checked(b0, "B0")
    subjects1, start1, _ = _checked(b1, "B1")
    _require(b0["observation_id"] != b1["observation_id"],
             "B0 and B1 observation IDs must differ")
    _require(end0 <= start1, "B0 and B1 observation intervals overlap or are reversed")
    _require(b0["source_profile_sha256"] == b1["source_profile_sha256"],
             "B0 and B1 source profile digests differ")
    _require(subjects0 == subjects1, "B0/B1 exact identity membership/head/tree/archive drift")
    if anchor is not None:
        anchored = _checked_anchor(anchor)
        _require(subjects0 == anchored, "B0/B1 pair differs from supplied anchor")
    digest = sha256((json.dumps(subjects0, separators=(",", ":")) + "\n").encode()).hexdigest()
    return {
        "status": (
            "PAIR_MATCHES_SUPPLIED_ANCHOR_ONLY" if anchor is not None
            else "PAIR_EQUIVALENCE_ONLY"
        ),
        "owner": OWNER,
        "subjects": len(subjects0),
        "archived": sum(item[5] for item in subjects0),
        "pair_digest_sha256": digest,
        "reference_membership_binding": (
            "SUPPLIED_ANCHOR_SELF_CONSISTENT_NOT_AUTHENTICATED" if anchor is not None
            else "NOT_ATTESTED"
        ),
        "source_profile_authenticity": "NOT_ATTESTED",
        "independent_collection": "NOT_ATTESTED",
        "independent_signer": "NOT_ATTESTED",
        "historical_transition_dispositions": "NOT_ATTESTED",
        "admission": "NOT_ADMITTED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("b0", type=Path)
    parser.add_argument("b1", type=Path)
    parser.add_argument("--anchor", type=Path,
                        help="optional externally supplied complete identity reference (not trust)")
    args = parser.parse_args(argv)
    try:
        supplied_anchor = load_vector(args.anchor) if args.anchor is not None else None
        print(json.dumps(compare_pair(load_vector(args.b0), load_vector(args.b1),
                                      anchor=supplied_anchor), indent=2))
        return 0
    except (VectorError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "EXACT_VECTOR_PAIR_REJECTED", "admission": "NOT_ADMITTED",
                          "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
