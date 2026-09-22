#!/usr/bin/env python3
"""Fail-closed structural validator for the public federated-cohesion research packet."""

from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "research" / "FEDERATED_PORTFOLIO_COHESION_20260922_V1.json"
EXACT_REF = re.compile(r"^.+@[0-9a-f]{40}$")
EXPECTED_CLAIM = (
    "PUBLIC_SAFE_RESEARCH_HYPOTHESIS_ONLY_NO_CANDIDATE_PROMOTION_NO_RUNTIME_AUTHORITY"
)


def load_packet() -> dict[str, Any]:
    return json.loads(PACKET.read_text(encoding="utf-8"))


def validate_packet(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if data.get("schema_version") != "DISCOVERY_FEDERATED_COHESION_RESEARCH_V1":
        errors.append("unexpected schema_version")
    if data.get("status") != "PUBLIC_SAFE_HYPOTHESIS_PACKET":
        errors.append("status must remain PUBLIC_SAFE_HYPOTHESIS_PACKET")
    if data.get("claim_ceiling") != EXPECTED_CLAIM:
        errors.append("claim ceiling widened or changed")

    inventory = data.get("inventory_binding") or {}
    total = inventory.get("total_repositories")
    public = inventory.get("public_repositories")
    private = inventory.get("private_repositories")
    if not all(isinstance(v, int) and v >= 0 for v in (total, public, private)):
        errors.append("inventory counts must be non-negative integers")
    elif total != public + private:
        errors.append("inventory arithmetic mismatch")
    if inventory.get("privacy_rule") != (
        "PUBLIC_REPOSITORIES_MAY_BE_NAMED_PRIVATE_REPOSITORIES_REMAIN_OPAQUE"
    ):
        errors.append("privacy rule missing or changed")
    if not EXACT_REF.fullmatch(str(inventory.get("discovery_live_base", ""))):
        errors.append("discovery_live_base must be an exact ref")

    subjects = data.get("public_subjects")
    if not isinstance(subjects, list) or not subjects:
        errors.append("public_subjects must be a non-empty list")
        subjects = []
    seen_repos: set[str] = set()
    for subject in subjects:
        repo = subject.get("repo")
        if not isinstance(repo, str) or not repo:
            errors.append("public subject missing repo")
            continue
        if repo in seen_repos:
            errors.append(f"duplicate public subject: {repo}")
        seen_repos.add(repo)
        if not EXACT_REF.fullmatch(str(subject.get("exact_ref", ""))):
            errors.append(f"{repo}: exact_ref is not immutable")
        if not subject.get("evidence"):
            errors.append(f"{repo}: evidence list is empty")
        if not subject.get("observed_mechanics"):
            errors.append(f"{repo}: observed_mechanics is empty")
        if not subject.get("preserved_boundary"):
            errors.append(f"{repo}: preserved_boundary is empty")

    observations = data.get("cross_system_observations")
    if not isinstance(observations, list) or not observations:
        errors.append("cross_system_observations must be non-empty")
        observations = []
    for observation in observations:
        if observation.get("state") != "OBSERVED":
            errors.append(
                f"{observation.get('id', '<unknown>')}: research observation escaped OBSERVED"
            )
        if not observation.get("support"):
            errors.append(f"{observation.get('id', '<unknown>')}: support is empty")

    hypothesis = data.get("architecture_hypothesis") or {}
    if hypothesis.get("state") != "HYPOTHESIS":
        errors.append("architecture_hypothesis must remain HYPOTHESIS")
    if hypothesis.get("promotion_ceiling") != "HYPOTHESIS_ONLY":
        errors.append("architecture_hypothesis promotion ceiling widened")
    if hypothesis.get("mandatory_global_runtime") != "NOT_JUSTIFIED":
        errors.append("mandatory global runtime cannot be asserted by this research packet")
    if not hypothesis.get("fallback_rule"):
        errors.append("federated hypothesis requires an explicit fallback rule")

    private_boundary = data.get("private_portfolio_boundary") or {}
    if private_boundary.get("named_private_repositories") != []:
        errors.append("private repository names must remain absent from the public packet")
    if private_boundary.get("private_count") != private:
        errors.append("private cohort count must match inventory binding")
    if private_boundary.get("allowed_use") != "AGGREGATE_OR_OPAQUE_PARTICIPATION_ONLY":
        errors.append("private cohort use widened beyond aggregate/opaque participation")

    hostile = data.get("hostile_review") or {}
    if hostile.get("status") != "PASS_WITH_BLOCKING_OBJECTIONS":
        errors.append("hostile review must retain blocking objections")
    objections = hostile.get("objections")
    if not isinstance(objections, list) or not objections:
        errors.append("hostile review objections are required")
    else:
        for objection in objections:
            if not objection.get("challenge") or not objection.get("required_falsifier"):
                errors.append("every hostile objection requires challenge and falsifier")

    experiments = data.get("next_experiments")
    if not isinstance(experiments, list) or len(experiments) < 2:
        errors.append("at least two next falsifiers are required")
    else:
        for experiment in experiments:
            if not all(experiment.get(k) for k in ("id", "question", "success", "failure")):
                errors.append("each next experiment requires id/question/success/failure")

    return errors


def main() -> int:
    errors = validate_packet(load_packet())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Federated cohesion research packet: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
