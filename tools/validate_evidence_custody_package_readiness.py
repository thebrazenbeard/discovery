from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "experiments" / "EVIDENCE_CUSTODY_PACKAGE_READINESS_V1.json"
EXPECTED_DISPOSITION = "FIRST_TASK_NOT_CLOSED_SOURCE_REPAIR_PRESENT_PLATFORM_CONTRACT_BLOCKED"


def load() -> dict:
    return json.loads(PATH.read_text(encoding="utf-8"))


def validate_result(doc: dict) -> list[str]:
    errors: list[str] = []
    if doc.get("schema") != "DISCOVERY_EVIDENCE_CUSTODY_PACKAGE_READINESS_V1":
        errors.append("package readiness schema mismatch")
    if doc.get("source_visibility") != "PRIVATE_OPAQUE":
        errors.append("private source visibility drifted")
    if doc.get("source_identity_published") is not False:
        errors.append("private source identity falsely published")
    if doc.get("public_replayability") != "NOT_PUBLICLY_REPLAYABLE":
        errors.append("private source review falsely promoted to public replayability")

    current = doc.get("current_main_package_state", {})
    if current.get("truthful_package_identity") is not False:
        errors.append("current private main package identity falsely qualified")
    if current.get("reusable_distribution_ready") is not False:
        errors.append("current private main falsely marked distribution-ready")

    repair = doc.get("active_package_repair", {})
    required_true = (
        "source_metadata_truthful",
        "package_identity_narrowed_to_custody_package",
        "inherited_runtime_dependencies_removed",
        "wheel_target_narrowed_to_actual_package",
        "cli_surface_narrowed_to_actual_package",
        "mypy_target_narrowed_to_actual_package",
        "narrow_public_api_contract_present",
        "custody_vs_domain_authority_boundary_explicit",
        "package_ci_defined",
        "consolidation_carries_same_package_blobs",
    )
    for field in required_true:
        if repair.get(field) is not True:
            errors.append(f"source repair evidence drifted: {field}")
    if repair.get("merged_or_released") is not False:
        errors.append("package repair falsely promoted to merged/released")

    q = doc.get("qualification", {})
    if q.get("windows_test_collection") != 103:
        errors.append("Windows test collection count drifted")
    if q.get("windows_tests_passed") != 47 or q.get("windows_tests_failed") != 56:
        errors.append("Windows pass/fail counts drifted")
    if q.get("explicit_os_platform_ceiling_present") is not False:
        errors.append("OS/platform support ceiling falsely asserted")
    if q.get("hosted_package_ci") != "PRE_STEP_NO_EXECUTION":
        errors.append("hosted package CI evidence class drifted")
    if q.get("clean_install_qualification") != "UNRESOLVED":
        errors.append("clean install falsely qualified")
    if q.get("wheel_sdist_build_qualification") != "UNRESOLVED":
        errors.append("build qualification falsely promoted")
    if q.get("general_installability") != "NOT_ESTABLISHED":
        errors.append("general installability falsely promoted")

    result = doc.get("package_readiness_result", {})
    if result.get("disposition") != EXPECTED_DISPOSITION:
        errors.append("package readiness disposition drifted")
    if result.get("source_package_repair") != "PASS_AT_SOURCE_SCOPE":
        errors.append("source package repair result drifted")
    if result.get("cross_platform_contract") != "FAIL_CURRENT_DECLARATION":
        errors.append("platform contract result drifted")
    if result.get("installable_package_gate") != "UNRESOLVED":
        errors.append("installable package gate falsely closed")
    if result.get("reusable_interchange_evaluation_allowed") is not False:
        errors.append("reuse evaluation falsely authorized")
    return errors


def validate() -> list[str]:
    return validate_result(load())


if __name__ == "__main__":
    problems = validate()
    if problems:
        for problem in problems:
            print(problem)
        raise SystemExit(1)
    print("Evidence custody package readiness validation PASS")
