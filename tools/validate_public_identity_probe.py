"""Validate a public inventory receipt's *internal consistency*, not its admission.

The 2026-10-28 observer retained one subject vector, two counts and summary
stability flags. It did not retain independent full B0/B1 subject vectors or
an independent signer's source/policy/profile binding. Those missing facts
cannot be reconstructed from a hash or self-reported boolean.
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


SCHEMA = "DISCOVERY_READ_ONLY_PUBLIC_IDENTITY_PROBE_20261028"
OWNER = "thebrazenbeard"
OID = re.compile(r"[0-9a-f]{40}\Z")
NAME = re.compile(r"[A-Za-z0-9_.-]+\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")


class ProbeError(ValueError):
    """A receipt failed a fail-closed structural requirement."""


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise ProbeError(label)


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in pairs:
        if name in result:
            raise ProbeError(f"duplicate JSON key: {name}")
        result[name] = value
    return result


def load_probe(path: Path) -> dict[str, Any]:
    result = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicate_keys)
    _require(isinstance(result, dict), "receipt must be a JSON object")
    return result


def _timestamp(raw: Any, field: str) -> datetime:
    _require(isinstance(raw, str) and bool(raw), f"{field} must be a timestamp")
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProbeError(f"{field} invalid timestamp") from exc
    _require(parsed.tzinfo is not None and parsed.utcoffset().total_seconds() == 0,
             f"{field} must use UTC")
    return parsed.astimezone(timezone.utc)


def _digest(value: Any) -> str:
    encoded = (json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode()
    return sha256(encoded).hexdigest()


def validate_probe(receipt: dict[str, Any]) -> dict[str, Any]:
    """Return only the bounded structural result, *never* an admission token."""
    _require(isinstance(receipt, dict), "receipt must be an object")
    _require(receipt.get("schema") == SCHEMA, "unexpected observation schema")
    _require(receipt.get("owner") == OWNER, "owner mismatch")
    _require(receipt.get("not_admitted") is True, "not_admitted must be true")
    _require(receipt.get("admission_state") == "UNREVIEWED_NOT_ADMITTED",
             "admission state must remain unreviewed")
    _require(receipt.get("repo_set_stable") is True, "snapshot reports unstable membership")
    _require(receipt.get("head_drift") == [], "head drift must be empty")
    _require(receipt.get("errors") == [], "collection errors must be empty")

    started = _timestamp(receipt.get("started_at_utc"), "started_at_utc")
    ended = _timestamp(receipt.get("ended_at_utc"), "ended_at_utc")
    _require(started <= ended, "observation end precedes start")

    subjects = receipt.get("subjects")
    _require(isinstance(subjects, list) and len(subjects) > 0, "subjects must be nonempty")
    names: list[str] = []
    ids: list[int] = []
    archived = 0
    for index, subject in enumerate(subjects):
        _require(isinstance(subject, dict), f"subjects[{index}] must be object")
        name = subject.get("name")
        _require(isinstance(name, str) and NAME.fullmatch(name) is not None,
                 f"subjects[{index}] name invalid")
        names.append(name)
        repo_id = subject.get("id")
        _require(type(repo_id) is int and repo_id > 0, f"subjects[{index}] id invalid")
        ids.append(repo_id)
        branch = subject.get("branch")
        _require(isinstance(branch, str) and branch.strip() == branch and bool(branch),
                 f"subjects[{index}] branch invalid")
        for field in ("head", "tree"):
            value = subject.get(field)
            _require(isinstance(value, str) and OID.fullmatch(value) is not None,
                     f"subjects[{index}] {field} invalid")
        _require(type(subject.get("archived")) is bool,
                 f"subjects[{index}] archived invalid")
        archived += int(subject["archived"])

    _require(names == sorted(names), "subject names must be sorted")
    _require(len(set(map(str.casefold, names))) == len(names), "subject names must be unique")
    _require(len(set(ids)) == len(ids), "repository ids unique requirement violated")
    for field in ("B0_count", "B1_count", "bound_exact_subjects"):
        _require(type(receipt.get(field)) is int and receipt[field] == len(subjects),
                 f"{field} must match subjects count")
    _require(type(receipt.get("archived")) is int and receipt["archived"] == archived,
             "archived count mismatch")
    _require(receipt.get("identity_digest_sha256") == _digest(subjects),
             "identity digest mismatch")
    names_hash = sha256("".join(f"{name}\n" for name in names).encode()).hexdigest()
    _require(receipt.get("names_digest_sha256") == names_hash,
             "names digest mismatch")
    for field in ("identity_digest_sha256", "names_digest_sha256"):
        _require(isinstance(receipt[field], str) and DIGEST.fullmatch(receipt[field]) is not None,
                 f"{field} invalid SHA256")

    return {
        "status": "LOCAL_IDENTITY_STRUCTURE_PASS_ONLY",
        "owner": OWNER,
        "subjects": len(subjects),
        "archived": archived,
        "identity_digest_sha256": receipt["identity_digest_sha256"],
        "independent_b0_b1_replay": "NOT_ATTESTED",
        "independent_source_policy_profile_binding": "NOT_ATTESTED",
        "redirect_transition_dispositions": "NOT_ATTESTED",
        "admission": "NOT_ADMITTED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path, help="read-only local JSON observation")
    args = parser.parse_args(argv)
    try:
        report = validate_probe(load_probe(args.receipt))
    except (ProbeError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "STRUCTURE_REJECTED", "admission": "NOT_ADMITTED",
                          "error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
