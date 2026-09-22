from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURE = ROOT / "architecture" / "DISCOVERY_ARCHITECTURE_OBSERVATORY_V1.json"

EXPECTED_PLANES = {
    "OBSERVE",
    "DETECT",
    "FALSIFY",
    "EXPERIMENT",
    "IMPACT_RADAR",
}
EXPECTED_DETECTORS = {
    "D0_EXACT_GIT_IDENTITY",
    "D1_NORMALIZED_LEXICAL",
    "D2_AST_STRUCTURE",
    "D3_INTERFACE_DEPENDENCY_WORKFLOW",
    "D4_BEHAVIORAL",
    "D5_SEMANTIC_LLM_NOMINATION",
}
REQUIRED_INVARIANTS = {
    "DELETE_DISCOVERY_DOES_NOT_BREAK_PROJECT_LOCAL_OPERATION",
    "OBSERVATION_IS_NOT_AUTHORITY",
    "CONFIDENCE_IS_NOT_EVIDENCE_CLASS",
    "NO_SELF_CORROBORATION",
    "FAIL_CLOSED_CURRENTNESS",
    "NEGATIVE_CONTROLS_ARE_FIRST_CLASS",
    "NO_AUTOMATIC_PROMOTION",
    "NO_MANDATORY_DISCOVERY_RUNTIME",
    "PRIVACY_BOUNDARIES_SURVIVE_OBSERVABILITY",
    "REUSE_MUST_PAY_RENT",
}
REQUIRED_BUILD_PREFIX = [
    "SNAPSHOT_ENGINE",
    "CURRENTNESS_INVALIDATION_ENGINE",
    "DETECTOR_PLUGIN_CONTRACT",
]
REQUIRED_ECONOMICS = {
    "PREEXISTING_DUPLICATED_NON_DOMAIN_WORK",
    "SHARED_IMPLEMENTATION_ADDED",
    "ADAPTER_OR_VERIFIER_COST",
    "TEST_AND_QUALIFICATION_COST",
    "DEPENDENCY_EDGES_INTRODUCED",
    "FAILURE_CLASS_PREVENTED",
    "ROLLBACK_FALLBACK_COST",
    "CHANGE_PROPAGATION_COST",
    "LOCAL_OPERABILITY_WITHOUT_DISCOVERY",
}


def load(path: Path = ARCHITECTURE) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_data(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["architecture must be an object"]

    if data.get("schema") != "DISCOVERY_ARCHITECTURE_OBSERVATORY_V1":
        errors.append("architecture schema mismatch")
    if data.get("status") != "RESEARCH_ARCHITECTURE_HYPOTHESIS_NO_RUNTIME_AUTHORITY":
        errors.append("architecture status exceeds research ceiling")
    if data.get("role") != "PORTFOLIO_ARCHITECTURE_OBSERVATORY_AND_REUSE_LABORATORY":
        errors.append("architecture role mismatch")

    invariants = data.get("hard_invariants")
    if not isinstance(invariants, list) or set(invariants) != REQUIRED_INVARIANTS:
        errors.append("hard invariants mismatch")

    planes = data.get("planes")
    plane_ids: set[str] = set()
    if not isinstance(planes, list):
        errors.append("planes must be a list")
    else:
        for index, plane in enumerate(planes):
            if not isinstance(plane, dict):
                errors.append(f"plane invalid: {index}")
                continue
            plane_id = plane.get("id")
            if not isinstance(plane_id, str):
                errors.append(f"plane id invalid: {index}")
                continue
            if plane_id in plane_ids:
                errors.append(f"duplicate plane id: {plane_id}")
            plane_ids.add(plane_id)
            if plane.get("runtime_authority") is not False:
                errors.append(f"plane may not hold runtime authority: {plane_id}")
            purpose = plane.get("purpose")
            if not isinstance(purpose, str) or not purpose.strip():
                errors.append(f"plane purpose missing: {plane_id}")
        if plane_ids != EXPECTED_PLANES:
            errors.append("plane set mismatch")

    detectors = data.get("detector_ladder")
    detector_ids: set[str] = set()
    if not isinstance(detectors, list):
        errors.append("detector ladder must be a list")
    else:
        for index, detector in enumerate(detectors):
            if not isinstance(detector, dict):
                errors.append(f"detector invalid: {index}")
                continue
            detector_id = detector.get("id")
            if not isinstance(detector_id, str):
                errors.append(f"detector id invalid: {index}")
                continue
            if detector_id in detector_ids:
                errors.append(f"duplicate detector id: {detector_id}")
            detector_ids.add(detector_id)
            if detector.get("max_claim_state") not in {"OBSERVED", "HYPOTHESIS"}:
                errors.append(f"detector claim ceiling invalid: {detector_id}")
            if detector_id != "D0_EXACT_GIT_IDENTITY" and detector.get("max_claim_state") != "HYPOTHESIS":
                errors.append(f"derived detector exceeds HYPOTHESIS: {detector_id}")
            for field in ("evidence_class", "required_corroboration", "limitations"):
                value = detector.get(field)
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"detector {field} missing: {detector_id}")
        if detector_ids != EXPECTED_DETECTORS:
            errors.append("detector set mismatch")

    rules = data.get("promotion_rules")
    if not isinstance(rules, dict):
        errors.append("promotion rules missing")
    else:
        if rules.get("detector_output_can_auto_promote") is not False:
            errors.append("detector output may not auto-promote")
        if rules.get("interoperability_alone_is_reuse_value") is not False:
            errors.append("interoperability alone may not count as reuse value")
        for field in ("experimenting_requires", "proven_reusable_requires"):
            value = rules.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"promotion rule missing: {field}")

    staleness = data.get("staleness_policy")
    if not isinstance(staleness, dict):
        errors.append("staleness policy missing")
    else:
        if staleness.get("mode") != "FAIL_CLOSED":
            errors.append("staleness must fail closed")
        if staleness.get("subject_movement_effect") != "DEPENDENT_CURRENT_CLAIMS_BECOME_STALE":
            errors.append("subject movement must invalidate dependent current claims")
        if staleness.get("historical_evidence_preserved") is not True:
            errors.append("historical evidence must be preserved")
        if staleness.get("silent_currentness_transfer") is not False:
            errors.append("silent currentness transfer forbidden")

    economics = data.get("economics_required")
    if not isinstance(economics, list) or set(economics) != REQUIRED_ECONOMICS:
        errors.append("reuse economics requirements mismatch")

    hostile = data.get("hostile_review")
    objections = hostile.get("objections") if isinstance(hostile, dict) else None
    if not isinstance(objections, list) or len(objections) < 6:
        errors.append("hostile review must contain at least six objections")
    else:
        seen: set[str] = set()
        for index, objection in enumerate(objections):
            if not isinstance(objection, dict):
                errors.append(f"hostile objection invalid: {index}")
                continue
            objection_id = objection.get("id")
            if not isinstance(objection_id, str) or not objection_id:
                errors.append(f"hostile objection id invalid: {index}")
                continue
            if objection_id in seen:
                errors.append(f"duplicate hostile objection: {objection_id}")
            seen.add(objection_id)
            if objection.get("severity") not in {"MEDIUM", "HIGH", "CRITICAL"}:
                errors.append(f"hostile objection severity invalid: {objection_id}")
            for field in ("challenge", "guard"):
                value = objection.get(field)
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"hostile objection {field} missing: {objection_id}")

    build_order = data.get("initial_build_order")
    if not isinstance(build_order, list) or build_order[:3] != REQUIRED_BUILD_PREFIX:
        errors.append("initial build order must begin snapshot/currentness/detector contract")

    target = data.get("first_implementation_target")
    if not isinstance(target, dict):
        errors.append("first implementation target missing")
    else:
        if target.get("id") != "READ_ONLY_SNAPSHOT_CURRENTNESS_PIPELINE":
            errors.append("first implementation target mismatch")
        if target.get("protected_effects") is not False:
            errors.append("first implementation target must be read-only")

    claim = data.get("claim_ceiling")
    if not isinstance(claim, str) or "NO_RUNTIME_AUTHORITY" not in claim or "NO_AUTOMATIC_PROMOTION" not in claim:
        errors.append("claim ceiling missing authority guards")

    return errors


def validate(path: Path = ARCHITECTURE) -> list[str]:
    return validate_data(load(path))


if __name__ == "__main__":
    problems = validate()
    if problems:
        for problem in problems:
            print(problem)
        raise SystemExit(1)
    print("Discovery architecture observatory validation PASS")
