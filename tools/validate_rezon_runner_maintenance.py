from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "experiments" / "REZON_RUNNER_MAINTENANCE_CURRENTNESS_V1.json"
EXPECTED_CURRENT = "PR31@8e588bd1cb72808b4a611d2a0bcbaeba6cb10b15"
EXPECTED_DISPOSITION = "EXPERIMENTING_NARROWED_CURRENT_SUCCESSOR_NO_REUSE_PROMOTION"


def load() -> dict:
    return json.loads(PATH.read_text(encoding="utf-8"))


def validate_result(doc: dict) -> list[str]:
    errors: list[str] = []
    if doc.get("schema") != "DISCOVERY_REZON_RUNNER_MAINTENANCE_CURRENTNESS_V1":
        errors.append("Rezon Runner maintenance schema mismatch")

    current = doc.get("exact_subjects", {}).get("runner_current", {})
    if current.get("ref") != EXPECTED_CURRENT:
        errors.append("current Runner successor binding drifted")
    if current.get("verifier_blob") != "d46b1c310c8cf51ae495822f5cefbec414fb6ba9":
        errors.append("current Runner verifier blob drifted")
    if current.get("hostile_review") != "PASS_WITH_CLAIM_CEILING":
        errors.append("current Runner review ceiling drifted")

    delta = doc.get("maintenance_delta", {})
    expected_delta = {
        "commits_ahead_from_original_verifier": 11,
        "changed_files": 7,
        "additions": 445,
        "deletions": 16,
        "verifier_net_line_growth": 73,
        "primary_test_net_line_growth": 80,
        "added_failure_test_lines": 105,
        "added_boundary_doc_lines": 74,
        "added_failure_fixture_lines": 58,
        "added_failure_binding_lines": 41,
    }
    if delta != expected_delta:
        errors.append("maintenance delta drifted")

    changes = doc.get("boundary_changes", {})
    stale = set(changes.get("original_discovery_claims_now_stale", []))
    if "Runner does not reimplement Rezon's canonical producer-ID formula." not in stale:
        errors.append("stale producer-ID boundary not acknowledged")
    if not any("accepted_claim_ids" in value for value in stale):
        errors.append("stale opaque claim-disposition boundary not acknowledged")

    result = doc.get("result", {})
    if result.get("mechanical_boundary_still_demonstrated") is not True:
        errors.append("mechanical boundary incorrectly discarded")
    if result.get("producer_agnostic_boundary_demonstrated") is not False:
        errors.append("producer-agnostic boundary falsely promoted")
    if result.get("epistemic_authority_transfered") is not False:
        errors.append("epistemic authority falsely transferred")
    if result.get("net_maintenance_savings_demonstrated") is not False:
        errors.append("maintenance savings falsely promoted")
    if result.get("organic_second_consumer_demonstrated") is not False:
        errors.append("second consumer falsely promoted")
    if result.get("candidate_disposition") != EXPECTED_DISPOSITION:
        errors.append("candidate disposition drifted")
    return errors


def validate() -> list[str]:
    return validate_result(load())


if __name__ == "__main__":
    problems = validate()
    if problems:
        for problem in problems:
            print(problem)
        raise SystemExit(1)
    print("Rezon Runner maintenance currentness validation PASS")
