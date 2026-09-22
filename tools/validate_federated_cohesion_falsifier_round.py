#!/usr/bin/env python3
"""Validate the source-bound federated-cohesion falsifier round."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "research" / "FEDERATED_COHESION_FALSIFIER_ROUND_20260922_V1.json"
EXACT_REF = re.compile(r"^.+@[0-9a-f]{40}$")
EXPECTED_CEILING = (
    "FOUR_EXACT_FALSIFIERS_INGESTED_HYPOTHESIS_SURVIVES_NARROWED_"
    "NO_REUSE_PROMOTION_NO_RUNTIME_AUTHORITY"
)
EXPECTED_PRS = {26, 27, 28, 29}


def load_packet() -> dict[str, Any]:
    return json.loads(PACKET.read_text(encoding="utf-8"))


def validate_packet(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if data.get("schema_version") != "DISCOVERY_FEDERATED_COHESION_FALSIFIER_ROUND_V1":
        errors.append("unexpected schema_version")
    if data.get("status") != "PUBLIC_SAFE_SOURCE_BOUND_FALSIFICATION_ROUND":
        errors.append("unexpected status")
    if data.get("claim_ceiling") != EXPECTED_CEILING:
        errors.append("claim ceiling widened or changed")

    parent = data.get("parent_subject") or {}
    if parent.get("pr") != 25:
        errors.append("parent PR must remain #25")
    if not EXACT_REF.fullmatch(str(parent.get("ref", ""))):
        errors.append("parent subject must use an exact immutable ref")
    if parent.get("prior_hypothesis") != "FEDERATED_COHESION_V1":
        errors.append("prior hypothesis binding changed")

    subjects = data.get("falsifier_subjects")
    if not isinstance(subjects, list) or len(subjects) != 4:
        errors.append("exactly four falsifier subjects are required")
        subjects = []

    seen: set[int] = set()
    for subject in subjects:
        pr = subject.get("pr")
        if pr in seen:
            errors.append(f"duplicate falsifier PR: {pr}")
        seen.add(pr)
        if not EXACT_REF.fullmatch(str(subject.get("ref", ""))):
            errors.append(f"PR #{pr}: exact immutable ref required")
        blob = str(subject.get("experiment_blob", ""))
        if not re.fullmatch(r"[0-9a-f]{40}", blob):
            errors.append(f"PR #{pr}: exact experiment blob required")
        if not subject.get("result"):
            errors.append(f"PR #{pr}: result required")
        if not subject.get("federated_implication"):
            errors.append(f"PR #{pr}: federated implication required")
    if seen != EXPECTED_PRS:
        errors.append("falsifier PR set must remain exactly {26,27,28,29}")

    reassessment = data.get("prior_experiment_reassessment")
    if not isinstance(reassessment, list) or {x.get("id") for x in reassessment} != {"FED-EXP-1", "FED-EXP-2"}:
        errors.append("both prior experiment reassessments are required")
        reassessment = []
    for item in reassessment:
        if item.get("promotion") != "NO":
            errors.append(f"{item.get('id')}: promotion must remain NO")
    exp2 = next((x for x in reassessment if x.get("id") == "FED-EXP-2"), {})
    if exp2.get("current_state") != "NAIVE_UNIVERSAL_RECEIPT_PATTERN_FALSIFIED":
        errors.append("FED-EXP-2 falsification must be preserved")

    hypothesis = data.get("narrowed_hypothesis") or {}
    if hypothesis.get("id") != "FEDERATED_COHESION_V1_NARROWED":
        errors.append("narrowed hypothesis id changed")
    if hypothesis.get("state") != "HYPOTHESIS":
        errors.append("narrowed hypothesis escaped HYPOTHESIS")
    if hypothesis.get("promotion_ceiling") != "HYPOTHESIS_ONLY":
        errors.append("narrowed hypothesis promotion ceiling widened")
    rejected = set(hypothesis.get("rejected_or_not_supported") or [])
    required_rejections = {
        "A mandatory global runtime.",
        "A universal generic receipt schema across materially different systems.",
        "Discovery-side records as substitutes for native consumer provenance.",
    }
    if not required_rejections.issubset(rejected):
        errors.append("required negative findings were removed")

    rules = {x.get("rule") for x in data.get("decision_rules") or []}
    for required in {
        "SHARE_DISTINCTIONS_BEFORE_SCHEMAS",
        "NATIVE_BINDING_BEATS_EXTERNAL_CORRELATION",
        "INTEROPERABILITY_IS_NOT_REUSE_VALUE",
        "ADAPTER_GROWTH_COUNTS_AS_COST",
        "NEGATIVE_RESULTS_ROUTE_ARCHITECTURE",
    }:
        if required not in rules:
            errors.append(f"missing decision rule: {required}")

    hostile = data.get("hostile_review") or {}
    if hostile.get("status") != "PASS_WITH_BLOCKING_OBJECTIONS":
        errors.append("hostile review blockers must remain live")
    if not hostile.get("required_next_falsifier"):
        errors.append("required next falsifier missing")
    objections = hostile.get("critical_objections")
    if not isinstance(objections, list) or len(objections) < 4:
        errors.append("hostile review must retain at least four critical objections")

    return errors


def main() -> int:
    errors = validate_packet(load_packet())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Federated cohesion falsifier round: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
