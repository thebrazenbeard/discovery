#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / "portfolio" / "PORTFOLIO_CENSUS_V2.json"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ALGORITHM = (
    "SHA-256 over lexicographically sorted repository names, UTF-8, "
    "one name per line with trailing newline"
)


def digest(names: list[str]) -> str:
    raw = "".join(f"{name}\n" for name in sorted(names)).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate() -> list[str]:
    data = json.loads(CENSUS.read_text(encoding="utf-8"))
    errors: list[str] = []
    if data.get("schema") != "DISCOVERY_PORTFOLIO_CENSUS_V2":
        errors.append("unexpected census schema")
    counts = data.get("counts", {})
    public = data.get("public_repositories")
    if not isinstance(public, list) or any(not isinstance(x, str) or not x for x in public):
        return errors + ["public repository list invalid"]
    if public != sorted(public):
        errors.append("public repository list must be sorted")
    if len(public) != len(set(public)):
        errors.append("public repository list contains duplicates")
    if counts.get("public") != len(public):
        errors.append("public count does not match public repository list")
    if counts.get("total") != counts.get("public", -1) + counts.get("private", -1):
        errors.append("total count does not equal public plus private")
    if counts.get("archived") != counts.get("public_archived", -1) + counts.get("private_archived", -1):
        errors.append("archived count does not equal archive visibility split")
    digests = data.get("inventory_digests", {})
    if digests.get("algorithm") != ALGORITHM:
        errors.append("inventory digest algorithm mismatch")
    if digests.get("public_names_sha256") != digest(public):
        errors.append("public repository digest mismatch")
    for key in ("private_names_sha256", "all_names_sha256"):
        value = digests.get(key)
        if not isinstance(value, str) or not SHA256.fullmatch(value):
            errors.append(f"{key} malformed")
    binding = data.get("project_runner_binding", {})
    if binding.get("corpus_id") != "PROJECT_RUNNER_PORTFOLIO_CORPUS_V1":
        errors.append("Project Runner corpus binding missing")
    if binding.get("counts") != {k: counts.get(k) for k in ("total", "public", "private")}:
        errors.append("Project Runner count binding mismatch")
    if binding.get("private_names_sha256") != digests.get("private_names_sha256"):
        errors.append("Project Runner private digest binding mismatch")
    return errors


if __name__ == "__main__":
    failures = validate()
    if failures:
        raise SystemExit("\n".join(failures))
    print("PASS: DISCOVERY_PORTFOLIO_CENSUS_V2")
