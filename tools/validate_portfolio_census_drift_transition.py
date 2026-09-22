from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "experiments" / "PORTFOLIO_CENSUS_DRIFT_TRANSITION_V1.json"

OLD_BLOB = "34cd2ab55d46f5a1ecc2c894f3e8cfdb8afa41df"
CURRENT_BLOB = "1b46d74176f8d67f3c1bd53bfcf2f369b89e9d8d"
PUBLIC_CONSUMER = "PR23@b763c707abacc7dfe30dc451b2b42354a30e3621"
CURRENT_ESTATE = "PR29@48c2074ce4f679c724036e14c5b6910e145c2492"
EXPECTED_DISPOSITION = "PARTIAL_FALSIFIER_STALE_REJECTION_PASS_REFRESH_UNRESOLVED"


def load() -> dict:
    return json.loads(PATH.read_text(encoding="utf-8"))


def validate_result(doc: dict) -> list[str]:
    errors: list[str] = []
    if doc.get("schema") != "DISCOVERY_PORTFOLIO_CENSUS_DRIFT_TRANSITION_V1":
        errors.append("census drift transition schema mismatch")

    old = doc.get("old_provider", {})
    current = doc.get("current_provider", {})
    if old.get("census_blob") != OLD_BLOB or old.get("total") != 57:
        errors.append("old census binding drifted")
    if current.get("census_blob") != CURRENT_BLOB or current.get("total") != 58:
        errors.append("current census binding drifted")
    if current.get("public") != 23 or current.get("private") != 35:
        errors.append("current visibility split drifted")
    if current.get("all_names_digest_evidence_class") != "EXTERNALLY_SUPPLIED_NOT_SOURCE_VALIDATED":
        errors.append("current all-name digest evidence ceiling drifted")

    consumer = doc.get("public_consumer", {})
    if consumer.get("original_consumer_ref") != PUBLIC_CONSUMER:
        errors.append("public consumer exact subject drifted")
    if consumer.get("bound_old_census_blob") != OLD_BLOB:
        errors.append("public consumer old blob binding drifted")
    if consumer.get("current_estate_ref") != CURRENT_ESTATE:
        errors.append("public consumer current estate subject drifted")
    if consumer.get("current_estate_disposition") != "PR23 = BLOCKED_STALE_EXTERNAL_CURRENTNESS":
        errors.append("stale public consumer disposition drifted")
    if consumer.get("refreshed_to_current_discovery_census") is not False:
        errors.append("public consumer refresh falsely promoted")
    if consumer.get("deterministic_stale_rejection", {}).get("result") != "PASS":
        errors.append("public stale rejection result drifted")

    opaque = doc.get("opaque_consumer", {})
    if opaque.get("current_refresh_status") != "NOT_PUBLICLY_VERIFIABLE":
        errors.append("opaque consumer refresh falsely promoted")
    if opaque.get("new_public_safe_attestation_observed") is not False:
        errors.append("opaque consumer new attestation falsely asserted")

    falsifier = doc.get("falsifier", {})
    if falsifier.get("public_consumer_stale_rejection") != "PASS":
        errors.append("public stale-rejection falsifier drifted")
    for field in ("public_consumer_refresh", "synchronized_two_consumer_refresh"):
        if falsifier.get(field) != "NOT_DEMONSTRATED":
            errors.append(f"{field} falsely promoted")
    for field in ("opaque_consumer_stale_rejection", "opaque_consumer_refresh"):
        if falsifier.get(field) != "NOT_PUBLICLY_VERIFIABLE":
            errors.append(f"{field} exceeds public attestation ceiling")
    if falsifier.get("authority_boundary_preserved") is not True:
        errors.append("authority boundary incorrectly discarded")

    result = doc.get("result", {})
    if result.get("disposition") != EXPECTED_DISPOSITION:
        errors.append("transition disposition drifted")
    if result.get("candidate_status") != "EXPERIMENTING":
        errors.append("candidate status must remain EXPERIMENTING")
    if result.get("proven_reusable") is not False:
        errors.append("candidate falsely promoted to reusable")
    return errors


def validate() -> list[str]:
    return validate_result(load())


if __name__ == "__main__":
    problems = validate()
    if problems:
        for problem in problems:
            print(problem)
        raise SystemExit(1)
    print("Portfolio census drift transition validation PASS")
