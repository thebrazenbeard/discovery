from __future__ import annotations

import json
from pathlib import Path

ALLOWED_STATUS = {
    "OBSERVED", "HYPOTHESIS", "EXPERIMENTING", "PROVEN_REUSABLE",
    "PROJECT_SPECIFIC", "REJECTED", "SUPERSEDED",
}


def validate_candidate(candidate: dict) -> list[str]:
    failures: list[str] = []
    if type(candidate) is not dict:
        return ["candidate_not_object"]
    if candidate.get("schema_version") != "DISCOVERY_CANDIDATE_V1":
        failures.append("schema_version_invalid")
    if candidate.get("status") not in ALLOWED_STATUS:
        failures.append("status_invalid")
    consumers = candidate.get("consumers")
    if not isinstance(consumers, list) or len(consumers) < 2:
        failures.append("consumers_missing")
    hostile = candidate.get("hostile_review")
    if not isinstance(hostile, dict):
        failures.append("hostile_review_missing")
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
