from __future__ import annotations

import json
import re
from pathlib import Path

ALLOWED_STATUS = {
    "OBSERVED", "HYPOTHESIS", "EXPERIMENTING", "PROVEN_REUSABLE",
    "PROJECT_SPECIFIC", "REJECTED", "SUPERSEDED",
}
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def _nonempty(value) -> bool:
    return type(value) is str and bool(value.strip())


def validate_candidate(candidate: dict) -> list[str]:
    failures: list[str] = []
    if type(candidate) is not dict:
        return ["candidate_not_object"]
    if candidate.get("schema_version") != "DISCOVERY_CANDIDATE_V1":
        failures.append("schema_version_invalid")
    status = candidate.get("status")
    if status not in ALLOWED_STATUS:
        failures.append("status_invalid")

    consumers = candidate.get("consumers")
    if not isinstance(consumers, list) or len(consumers) < 2:
        failures.append("consumers_missing")
        consumers = []

    hostile = candidate.get("hostile_review")
    if not isinstance(hostile, dict):
        failures.append("hostile_review_missing")
        hostile = {}

    evidence = candidate.get("promotion_evidence")
    if not isinstance(evidence, list):
        failures.append("promotion_evidence_invalid")
        evidence = []

    if status == "PROVEN_REUSABLE":
        repos: list[str] = []
        for index, consumer in enumerate(consumers):
            if not isinstance(consumer, dict):
                failures.append(f"proven_consumer_invalid:{index}")
                continue
            repo = consumer.get("repo")
            ref = consumer.get("ref")
            if not _nonempty(repo) or repo.upper().startswith("TBD"):
                failures.append(f"proven_consumer_not_real:{index}")
            else:
                repos.append(repo)
            if type(ref) is not str or not HEX40.fullmatch(ref):
                failures.append(f"proven_consumer_ref_not_exact:{index}")
        if len(set(repos)) < 2:
            failures.append("proven_consumers_not_materially_distinct")
        if len(evidence) < 2 or any(not _nonempty(item) for item in evidence):
            failures.append("proven_promotion_evidence_insufficient")
        if hostile.get("status") not in {"PASS", "PASS_WITH_LIMITS"}:
            failures.append("proven_hostile_review_not_passed")
        objections = hostile.get("critical_objections")
        if not isinstance(objections, list) or objections:
            failures.append("proven_unresolved_critical_objections")

    return failures


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    candidates = sorted((root / "candidates").glob("*.json"))
    failures: list[str] = []
    for path in candidates:
        data = json.loads(path.read_text(encoding="utf-8"))
        for failure in validate_candidate(data):
            failures.append(f"{path.name}:{failure}")
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print(f"validated {len(candidates)} discovery candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
