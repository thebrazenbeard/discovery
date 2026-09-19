from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SHA40 = re.compile(r"^[0-9a-f]{40}$")
CANDIDATE_ID = re.compile(r"^[A-Z0-9][A-Z0-9_-]+$")
STATUSES = {
    "OBSERVED",
    "HYPOTHESIS",
    "EXPERIMENTING",
    "PROVEN_REUSABLE",
    "PROJECT_SPECIFIC",
    "REJECTED",
    "SUPERSEDED",
}
PLACEHOLDER_PREFIXES = ("TBD", "UNKNOWN", "PLACEHOLDER")


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_candidate(candidate: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    if candidate.get("schema_version") != "DISCOVERY_CANDIDATE_V1":
        failures.append("SCHEMA_VERSION_INVALID")

    candidate_id = candidate.get("candidate_id")
    if not isinstance(candidate_id, str) or not CANDIDATE_ID.fullmatch(candidate_id):
        failures.append("CANDIDATE_ID_INVALID")

    status = candidate.get("status")
    if status not in STATUSES:
        failures.append("STATUS_INVALID")

    for field in ("title", "claim"):
        if not _nonempty_string(candidate.get(field)):
            failures.append(f"{field.upper()}_INVALID")

    consumers = candidate.get("consumers")
    if not isinstance(consumers, list) or len(consumers) < 2:
        failures.append("CONSUMERS_INSUFFICIENT")
        consumers = []

    repos: list[str] = []
    for index, consumer in enumerate(consumers):
        if not isinstance(consumer, dict):
            failures.append(f"CONSUMER_INVALID:{index}")
            continue
        repo = consumer.get("repo")
        role = consumer.get("role")
        if not _nonempty_string(repo):
            failures.append(f"CONSUMER_REPO_INVALID:{index}")
        else:
            repos.append(repo.strip())
        if not _nonempty_string(role):
            failures.append(f"CONSUMER_ROLE_INVALID:{index}")

    if len(set(repos)) != len(repos):
        failures.append("CONSUMER_REPOSITORIES_NOT_DISTINCT")

    for field in ("preserved_boundaries", "rejection_conditions"):
        value = candidate.get(field)
        if (
            not isinstance(value, list)
            or not value
            or any(not _nonempty_string(item) for item in value)
        ):
            failures.append(f"{field.upper()}_INVALID")

    promotion_evidence = candidate.get("promotion_evidence")
    if not isinstance(promotion_evidence, list) or any(
        not _nonempty_string(item) for item in promotion_evidence
    ):
        failures.append("PROMOTION_EVIDENCE_INVALID")
        promotion_evidence = []

    hostile = candidate.get("hostile_review")
    if not isinstance(hostile, dict):
        failures.append("HOSTILE_REVIEW_INVALID")
        hostile = {}
    hostile_status = hostile.get("status")
    if hostile_status not in {"NOT_RUN", "FAIL", "PASS_WITH_LIMITS", "PASS"}:
        failures.append("HOSTILE_REVIEW_STATUS_INVALID")
    objections = hostile.get("critical_objections")
    if not isinstance(objections, list) or any(
        not _nonempty_string(item) for item in objections
    ):
        failures.append("HOSTILE_REVIEW_OBJECTIONS_INVALID")
        objections = []

    if status in {"EXPERIMENTING", "PROVEN_REUSABLE"}:
        for index, consumer in enumerate(consumers):
            if not isinstance(consumer, dict):
                continue
            repo = consumer.get("repo")
            ref = consumer.get("ref")
            if (
                not _nonempty_string(repo)
                or repo.strip().upper().startswith(PLACEHOLDER_PREFIXES)
            ):
                failures.append(f"ACTIVE_CONSUMER_PLACEHOLDER:{index}")
            if not isinstance(ref, str) or not SHA40.fullmatch(ref):
                failures.append(f"ACTIVE_CONSUMER_REF_NOT_EXACT:{index}")
        if not promotion_evidence:
            failures.append("ACTIVE_PROMOTION_EVIDENCE_REQUIRED")
        if hostile_status == "NOT_RUN":
            failures.append("ACTIVE_HOSTILE_REVIEW_REQUIRED")

    if status == "PROVEN_REUSABLE":
        if len(set(repos)) < 2:
            failures.append("PROVEN_TWO_REAL_CONSUMERS_REQUIRED")
        if len(promotion_evidence) < 2:
            failures.append("PROVEN_INDEPENDENT_INTEGRATION_EVIDENCE_REQUIRED")
        if hostile_status != "PASS":
            failures.append("PROVEN_HOSTILE_PASS_REQUIRED")
        if objections:
            failures.append("PROVEN_UNRESOLVED_CRITICAL_OBJECTIONS")

    return failures


def validate_directory(directory: Path) -> dict[str, list[str]]:
    results: dict[str, list[str]] = {}
    seen_ids: set[str] = set()
    for path in sorted(directory.glob("*.json")):
        try:
            candidate = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            results[str(path)] = ["JSON_INVALID"]
            continue
        if not isinstance(candidate, dict):
            results[str(path)] = ["CANDIDATE_NOT_OBJECT"]
            continue
        failures = validate_candidate(candidate)
        candidate_id = candidate.get("candidate_id")
        if isinstance(candidate_id, str):
            if candidate_id in seen_ids:
                failures.append("CANDIDATE_ID_DUPLICATE")
            seen_ids.add(candidate_id)
        results[str(path)] = failures
    if not results:
        results[str(directory)] = ["NO_CANDIDATES_FOUND"]
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    results = validate_directory(args.directory)
    failures = {path: items for path, items in results.items() if items}
    print(json.dumps(results, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
