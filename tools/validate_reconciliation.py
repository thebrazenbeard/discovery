from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RECONCILIATION = ROOT / "architecture" / "REPOSITORY_RECONCILIATION_V1.json"

SHA1 = re.compile(r"^[0-9a-f]{40}$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

TOP_LEVEL_FIELDS = {
    "schema",
    "status",
    "generated_date",
    "current_main",
    "proposed_candidate",
    "ancestry",
    "exact_evidence",
    "proposed_pr_dispositions",
    "canonicalization_effect_if_authorized_later",
    "unresolved",
}
EXPECTED_STACK = [1, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
EXPECTED_HISTORICAL = {
    2: "SUPERSEDED_BY_8",
    3: "SUPERSEDED_BY_8",
    7: "SUPERSEDED_BY_8",
    18: "FAILED_PRESERVED_EVIDENCE_SUPERSEDED_BY_17_CURRENT",
}
EXPECTED_DISPOSITIONS = {
    "1": "CURRENT_STACK_DEPENDENCY",
    "2": "SUPERSEDED_BY_8",
    "3": "SUPERSEDED_BY_8",
    "7": "SUPERSEDED_BY_8",
    "8": "CURRENT_STACK_DEPENDENCY",
    "9": "CURRENT_STACK_DEPENDENCY",
    "10": "CURRENT_STACK_DEPENDENCY",
    "11": "CURRENT_STACK_DEPENDENCY",
    "12": "CURRENT_STACK_DEPENDENCY",
    "13": "CURRENT_STACK_DEPENDENCY",
    "14": "CURRENT_STACK_DEPENDENCY",
    "15": "CURRENT_STACK_DEPENDENCY",
    "16": "CURRENT_STACK_DEPENDENCY",
    "17": "CURRENT_SOURCE_LINEAGE_TERMINAL",
    "18": "FAILED_PRESERVED_EVIDENCE_SUPERSEDED_BY_17_CURRENT",
    "19": "CURRENT_CANONICALIZATION_WRAPPER",
}
EXPECTED_UNRESOLVED = {
    "Privacy issue #6 remains active and must not be erased by canonicalization.",
    "No protected merge/closure effect is authorized.",
}
HEAD_BINDING_RULE = (
    "A committed manifest cannot truthfully self-bind its own eventual commit SHA; "
    "bind review/currentness to the live PR ref and external exact-head evidence."
)
STACK_MEANING = (
    "SOURCE_LINEAGE_INHERITED_BY_CANONICALIZATION_WRAPPER_NOT_CURRENT_WRAPPER_IDENTITY"
)


def load(path: Path = RECONCILIATION) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _exact_keys(
    value: Any,
    expected: set[str],
    label: str,
    errors: list[str],
) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return False
    actual = set(value)
    if actual != expected:
        errors.append(
            f"{label} fields mismatch: expected={sorted(expected)} actual={sorted(actual)}"
        )
        return False
    return True


def _sha1(value: Any, label: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not SHA1.fullmatch(value):
        errors.append(f"{label} must be lowercase 40-hex")
        return False
    return True


def _nonempty(value: Any, label: str, errors: list[str]) -> bool:
    if type(value) is not str or not value.strip():
        errors.append(f"{label} must be a non-empty exact string")
        return False
    return True


def validate_reconciliation_data(data: Any) -> list[str]:
    errors: list[str] = []
    if not _exact_keys(data, TOP_LEVEL_FIELDS, "reconciliation", errors):
        return errors

    if data.get("schema") != "DISCOVERY_REPOSITORY_RECONCILIATION_V1":
        errors.append("reconciliation schema mismatch")
    if data.get("status") != "DRAFT_CANONICALIZATION_CANDIDATE_NO_MERGE_AUTHORITY":
        errors.append("reconciliation status mismatch")
    generated = data.get("generated_date")
    if not isinstance(generated, str) or not DATE.fullmatch(generated):
        errors.append("generated_date must be YYYY-MM-DD")

    current_main = data.get("current_main")
    if _exact_keys(current_main, {"sha", "meaning"}, "current_main", errors):
        _sha1(current_main.get("sha"), "current_main.sha", errors)
        _nonempty(current_main.get("meaning"), "current_main.meaning", errors)

    candidate = data.get("proposed_candidate")
    candidate_fields = {
        "pr",
        "sha_at_branch_creation",
        "branch",
        "base_main_sha",
        "qualified_pre_manifest_head",
        "current_exact_head",
        "head_binding_rule",
        "source_lineage_terminal_pr",
    }
    if _exact_keys(candidate, candidate_fields, "proposed_candidate", errors):
        if candidate.get("pr") != 19:
            errors.append("canonicalization wrapper PR must be 19")
        if (
            candidate.get("branch")
            != "bt2/discovery-canonical-main-candidate-v1-20260920"
        ):
            errors.append("canonicalization branch mismatch")
        _sha1(
            candidate.get("sha_at_branch_creation"),
            "proposed_candidate.sha_at_branch_creation",
            errors,
        )
        _sha1(
            candidate.get("qualified_pre_manifest_head"),
            "proposed_candidate.qualified_pre_manifest_head",
            errors,
        )
        _sha1(
            candidate.get("base_main_sha"),
            "proposed_candidate.base_main_sha",
            errors,
        )
        if isinstance(current_main, dict) and (
            candidate.get("base_main_sha") != current_main.get("sha")
        ):
            errors.append("canonicalization base_main_sha must equal current_main.sha")
        if candidate.get("current_exact_head") != "EXTERNAL_GIT_READ_REQUIRED":
            errors.append("committed manifest must not self-assert current exact head")
        if candidate.get("head_binding_rule") != HEAD_BINDING_RULE:
            errors.append("canonicalization head binding rule mismatch")
        if candidate.get("source_lineage_terminal_pr") != 17:
            errors.append("source lineage terminal PR must be 17")

    ancestry = data.get("ancestry")
    ancestry_fields = {
        "current_stack",
        "current_stack_meaning",
        "superseded_or_historical",
    }
    if _exact_keys(ancestry, ancestry_fields, "ancestry", errors):
        if ancestry.get("current_stack") != EXPECTED_STACK:
            errors.append("source lineage stack mismatch")
        if ancestry.get("current_stack_meaning") != STACK_MEANING:
            errors.append("source lineage meaning mismatch")
        historical = ancestry.get("superseded_or_historical")
        if not isinstance(historical, list):
            errors.append("superseded_or_historical must be a list")
        else:
            seen: dict[int, str] = {}
            for index, item in enumerate(historical):
                if not _exact_keys(
                    item,
                    {"pr", "classification", "reason"},
                    f"superseded_or_historical[{index}]",
                    errors,
                ):
                    continue
                pr = item.get("pr")
                classification = item.get("classification")
                reason = item.get("reason")
                if type(pr) is not int or isinstance(pr, bool):
                    errors.append(f"historical PR invalid at index {index}")
                    continue
                if pr in seen:
                    errors.append(f"historical PR duplicated: {pr}")
                seen[pr] = classification
                _nonempty(reason, f"historical reason PR {pr}", errors)
            if seen != EXPECTED_HISTORICAL:
                errors.append("historical PR classification map mismatch")

    exact_evidence = data.get("exact_evidence")
    expected_evidence_fields = {
        "main_to_pr17",
        "pr8_to_pr17",
        "pr1_to_pr17",
        "pr18_to_pr17",
        "hosted_ci",
        "local_bt2_execution",
    }
    if _exact_keys(
        exact_evidence,
        expected_evidence_fields,
        "exact_evidence",
        errors,
    ):
        for label in ("main_to_pr17", "pr8_to_pr17", "pr1_to_pr17"):
            item = exact_evidence.get(label)
            if _exact_keys(
                item,
                {"status", "ahead_by", "behind_by"},
                f"exact_evidence.{label}",
                errors,
            ):
                if item.get("status") != "ahead":
                    errors.append(f"{label} status must be ahead")
                for count_field in ("ahead_by", "behind_by"):
                    count = item.get(count_field)
                    if type(count) is not int or isinstance(count, bool) or count < 0:
                        errors.append(f"{label}.{count_field} must be non-negative int")
        diverged = exact_evidence.get("pr18_to_pr17")
        if _exact_keys(
            diverged,
            {
                "status",
                "merge_base",
                "pr17_ahead_by",
                "pr17_behind_by",
            },
            "exact_evidence.pr18_to_pr17",
            errors,
        ):
            if diverged.get("status") != "diverged":
                errors.append("pr18_to_pr17 status must be diverged")
            _sha1(diverged.get("merge_base"), "pr18_to_pr17.merge_base", errors)
            for count_field in ("pr17_ahead_by", "pr17_behind_by"):
                count = diverged.get(count_field)
                if type(count) is not int or isinstance(count, bool) or count < 0:
                    errors.append(
                        f"pr18_to_pr17.{count_field} must be non-negative int"
                    )

        hosted = exact_evidence.get("hosted_ci")
        if not isinstance(hosted, list) or not hosted:
            errors.append("hosted_ci must be a non-empty list")
        else:
            for index, item in enumerate(hosted):
                if not _exact_keys(
                    item,
                    {"run_id", "name", "conclusion", "subject"},
                    f"hosted_ci[{index}]",
                    errors,
                ):
                    continue
                run_id = item.get("run_id")
                if type(run_id) is not int or isinstance(run_id, bool) or run_id <= 0:
                    errors.append(f"hosted_ci[{index}].run_id must be positive int")
                _nonempty(item.get("name"), f"hosted_ci[{index}].name", errors)
                if item.get("conclusion") != "success":
                    errors.append(f"hosted_ci[{index}] conclusion must be success")
                _sha1(item.get("subject"), f"hosted_ci[{index}].subject", errors)

        local = exact_evidence.get("local_bt2_execution")
        local_fields = {
            "subject",
            "validate_discovery",
            "unit_tests",
            "compileall",
            "diff_check_against_main",
            "initial_defect_repaired",
        }
        if _exact_keys(local, local_fields, "local_bt2_execution", errors):
            _sha1(local.get("subject"), "local_bt2_execution.subject", errors)
            for field in (
                "validate_discovery",
                "unit_tests",
                "compileall",
                "diff_check_against_main",
                "initial_defect_repaired",
            ):
                _nonempty(local.get(field), f"local_bt2_execution.{field}", errors)

    dispositions = data.get("proposed_pr_dispositions")
    if dispositions != EXPECTED_DISPOSITIONS:
        errors.append("proposed PR dispositions mismatch")

    effects = data.get("canonicalization_effect_if_authorized_later")
    if not isinstance(effects, list) or len(effects) != 3 or any(
        not _nonempty(item, "canonicalization effect", errors) for item in effects
    ):
        errors.append("canonicalization effects must contain exactly three statements")

    unresolved = data.get("unresolved")
    if (
        not isinstance(unresolved, list)
        or len(unresolved) != len(EXPECTED_UNRESOLVED)
        or set(unresolved) != EXPECTED_UNRESOLVED
    ):
        errors.append("unresolved privacy/authority holds mismatch")

    return errors


def validate_reconciliation(path: Path = RECONCILIATION) -> list[str]:
    return validate_reconciliation_data(load(path))


if __name__ == "__main__":
    problems = validate_reconciliation()
    if problems:
        for problem in problems:
            print(problem)
        raise SystemExit(1)
    print("Discovery reconciliation validation PASS")
