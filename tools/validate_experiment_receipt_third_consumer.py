from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "experiments" / "EXPERIMENT_RECEIPT_THIRD_CONSUMER_V1.json"
EXPECTED_DISPOSITION = "THIRD_CONSUMER_FALSIFIES_PRIOR_GENERIC_RECEIPT_PATTERN_NO_EXTRACTION"


def load() -> dict:
    return json.loads(PATH.read_text(encoding="utf-8"))


def validate_result(doc: dict) -> list[str]:
    errors: list[str] = []
    if doc.get("schema") != "DISCOVERY_EXPERIMENT_RECEIPT_THIRD_CONSUMER_V1":
        errors.append("third-consumer receipt schema mismatch")

    subjects = doc.get("exact_subjects", {})
    expected_refs = {
        "world_zero": "science/demography-older-mortality-mass-normalization-v1-20260919@9be13e8e34772a90a812815b074bf21bb89e972a",
        "mosaic": "one/mosaic-p1-protocol-harness-v1-20260918@96fd911e5a6a9b2069a88ae20d0dfa4f6bbad01f",
        "driftguard": "main@9894692ff6b549e4378bcc2b8ca46813ff18bf37",
    }
    for key, ref in expected_refs.items():
        if subjects.get(key, {}).get("ref") != ref:
            errors.append(f"third-consumer exact subject drifted: {key}")

    intersection = doc.get("intersection_test", {})
    expected_intersection = {
        "exact_repository_source_subject_shared_across_all_three": False,
        "general_execution_environment_identity_shared_across_all_three": False,
        "result_or_evidence_identity_shared_across_all_three": True,
        "explicit_claim_ceiling_field_shared_across_all_three": False,
        "meaningful_common_executable_validation_beyond_digest_or_identity_plumbing": False,
        "demonstrated_code_deleted_or_replaced_by_common_layer": 0,
    }
    if intersection != expected_intersection:
        errors.append("third-consumer intersection result drifted")

    result = doc.get("result", {})
    if result.get("third_materially_independent_receipt_system_found") is not True:
        errors.append("third consumer must remain acknowledged")
    if result.get("prior_four_part_pattern_survives_three_way") is not False:
        errors.append("prior generic receipt pattern falsely promoted")
    if result.get("shared_executable_harness_candidate_created") is not False:
        errors.append("shared harness candidate falsely created")
    if result.get("generic_receipt_candidate_created") is not False:
        errors.append("generic receipt candidate falsely created")
    if result.get("disposition") != EXPECTED_DISPOSITION:
        errors.append("third-consumer disposition drifted")

    return errors


def validate() -> list[str]:
    return validate_result(load())


if __name__ == "__main__":
    problems = validate()
    if problems:
        for problem in problems:
            print(problem)
        raise SystemExit(1)
    print("Experiment receipt third-consumer validation PASS")
