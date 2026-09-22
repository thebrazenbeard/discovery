from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / "portfolio" / "PORTFOLIO_CENSUS_V1.json"
CUT = ROOT / "research" / "PUBLIC_REPOSITORY_RESEARCH_CUT_20260921_V1.json"

SHA1 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
VALID_STATES = {"OBSERVED", "HYPOTHESIS"}
VALID_CEILINGS = {"OBSERVED_ONLY", "HYPOTHESIS_ONLY"}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _nonempty(value: Any) -> bool:
    return type(value) is str and bool(value.strip())


def validate_data(census: dict[str, Any], cut: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if cut.get("schema_version") != "DISCOVERY_RESEARCH_CUT_V1":
        errors.append("unexpected research-cut schema")

    binding = cut.get("inventory_binding")
    if not isinstance(binding, dict):
        return errors + ["inventory_binding must be an object"]

    counts = census.get("counts", {})
    digests = census.get("inventory_digests", {})
    expected_binding = {
        "observed_date": census.get("observed_date"),
        "total_count": counts.get("total"),
        "public_count": counts.get("public"),
        "all_names_sha256": digests.get("all_names_sha256"),
    }
    if binding != expected_binding:
        errors.append("research cut inventory binding does not exactly match census")

    digest = binding.get("all_names_sha256")
    if not isinstance(digest, str) or not SHA256.fullmatch(digest):
        errors.append("research cut all_names_sha256 invalid")

    observations = cut.get("observations")
    if not isinstance(observations, list):
        return errors + ["observations must be a list"]

    expected_public = set(census.get("public_repositories", []))
    seen: set[str] = set()

    for index, item in enumerate(observations):
        if not isinstance(item, dict):
            errors.append(f"observation invalid: {index}")
            continue

        repo = item.get("repo")
        if not _nonempty(repo):
            errors.append(f"observation repo invalid: {index}")
            continue
        if repo in seen:
            errors.append(f"duplicate observation repo: {repo}")
        seen.add(repo)

        if item.get("visibility") != "PUBLIC":
            errors.append(f"non-public observation forbidden: {repo}")

        ref = item.get("observed_ref")
        if not isinstance(ref, str) or not SHA1.fullmatch(ref):
            errors.append(f"observation ref not exact: {repo}")

        if not _nonempty(item.get("source_locator")):
            errors.append(f"source locator invalid: {repo}")

        state = item.get("evidence_state")
        if state not in VALID_STATES:
            errors.append(f"research evidence state exceeds ingest ceiling: {repo}")

        ceiling = item.get("promotion_ceiling")
        if ceiling not in VALID_CEILINGS:
            errors.append(f"promotion ceiling invalid: {repo}")
        if state == "OBSERVED" and ceiling != "OBSERVED_ONLY":
            errors.append(f"observed item must remain OBSERVED_ONLY: {repo}")

        if not _nonempty(item.get("summary")):
            errors.append(f"summary invalid: {repo}")

        for field in ("mechanic_tags", "candidate_family_inputs"):
            value = item.get(field)
            if not isinstance(value, list) or any(not _nonempty(v) for v in value):
                errors.append(f"{field} invalid: {repo}")

        for field in ("boundaries", "uncertainties"):
            value = item.get(field)
            if (
                not isinstance(value, list)
                or not value
                or any(not _nonempty(v) for v in value)
            ):
                errors.append(f"{field} invalid: {repo}")

    if seen != expected_public:
        missing = sorted(expected_public - seen)
        extra = sorted(seen - expected_public)
        errors.append(
            f"research cut public membership mismatch: missing={missing} extra={extra}"
        )

    if len(observations) != counts.get("public"):
        errors.append("research observation count does not match public census count")

    return errors


def validate() -> list[str]:
    return validate_data(load(CENSUS), load(CUT))


if __name__ == "__main__":
    problems = validate()
    if problems:
        for problem in problems:
            print(problem)
        raise SystemExit(1)
    print("Discovery research ingest validation PASS")
