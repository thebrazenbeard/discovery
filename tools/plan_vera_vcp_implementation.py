from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAP = ROOT / "architecture" / "DISCOVERY_VERA_VCP_IMPLEMENTATION_MAP_V1.json"


class ImplementationPlanError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ImplementationPlanError(f"{path} must contain a JSON object")
    return payload


def _registry_sets(registry: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    sources = registry.get("repository_sources")
    unbound = registry.get("unbound_repositories")
    if not isinstance(sources, list) or not isinstance(unbound, list):
        raise ImplementationPlanError("Vera registry requires repository_sources and unbound_repositories lists")

    source_map: dict[str, dict[str, Any]] = {}
    unbound_map: dict[str, dict[str, Any]] = {}
    for item in sources:
        if not isinstance(item, dict) or not isinstance(item.get("repository"), str):
            raise ImplementationPlanError("invalid repository source entry")
        repo = item["repository"]
        if repo in source_map:
            raise ImplementationPlanError(f"duplicate repository source: {repo}")
        source_map[repo] = item
    for item in unbound:
        if not isinstance(item, dict) or not isinstance(item.get("repository"), str):
            raise ImplementationPlanError("invalid unbound repository entry")
        repo = item["repository"]
        if repo in unbound_map:
            raise ImplementationPlanError(f"duplicate unbound repository: {repo}")
        if repo in source_map:
            raise ImplementationPlanError(f"repository appears bound and unbound: {repo}")
        unbound_map[repo] = item
    return source_map, unbound_map


def _desired_subjects(implementation_map: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if implementation_map.get("schema") != "DISCOVERY_VERA_VCP_IMPLEMENTATION_MAP_V1":
        raise ImplementationPlanError("unexpected implementation map schema")
    subjects = implementation_map.get("subjects")
    if not isinstance(subjects, list):
        raise ImplementationPlanError("implementation map subjects must be a list")
    result: dict[str, dict[str, Any]] = {}
    for subject in subjects:
        if not isinstance(subject, dict):
            raise ImplementationPlanError("implementation subject must be an object")
        repo = subject.get("repository")
        if not isinstance(repo, str) or not repo:
            raise ImplementationPlanError("implementation subject repository missing")
        if repo in result:
            raise ImplementationPlanError(f"duplicate implementation subject: {repo}")
        result[repo] = subject
    return result


def plan(
    implementation_map: dict[str, Any],
    current_registry: dict[str, Any],
    candidate_registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    desired = _desired_subjects(implementation_map)
    current_sources, current_unbound = _registry_sets(current_registry)
    candidate_sources: dict[str, dict[str, Any]] = {}
    candidate_unbound: dict[str, dict[str, Any]] = {}
    if candidate_registry is not None:
        candidate_sources, candidate_unbound = _registry_sets(candidate_registry)

    actions: list[dict[str, Any]] = []
    for repo, subject in sorted(desired.items()):
        desired_role = subject.get("vera_runtime_role")
        desired_mode = subject.get("activation_mode")
        desired_ceiling = subject.get("authority_ceiling")

        if repo in candidate_sources:
            existing = candidate_sources[repo]
            if (
                existing.get("runtime_role") == desired_role
                and existing.get("activation_mode") == desired_mode
                and existing.get("authority_ceiling") == desired_ceiling
                and existing.get("availability_implies_activation") is False
            ):
                disposition = "SATISFIED_BY_ACTIVE_CANDIDATE"
            else:
                disposition = "RECONCILE_ACTIVE_CANDIDATE_SOURCE_ENTRY"
            target = "ACTIVE_CANDIDATE"
        elif repo in current_sources:
            existing = current_sources[repo]
            if subject.get("implementation_action") == "KEEP_VERA_SOURCE":
                disposition = "ALREADY_SOURCE_INTEGRATED"
            elif (
                existing.get("runtime_role") == desired_role
                and existing.get("activation_mode") == desired_mode
                and existing.get("authority_ceiling") == desired_ceiling
                and existing.get("availability_implies_activation") is False
            ):
                disposition = "ALREADY_SOURCE_INTEGRATED"
            else:
                disposition = "RECONCILE_CURRENT_SOURCE_ENTRY"
            target = "CURRENT_MAIN"
        elif repo in candidate_unbound:
            disposition = "PROMOTE_FROM_ACTIVE_CANDIDATE_UNBOUND_TO_SOURCE"
            target = "ACTIVE_CANDIDATE"
        elif repo in current_unbound:
            disposition = "PROMOTE_FROM_CURRENT_UNBOUND_TO_SOURCE"
            target = "CURRENT_MAIN"
        else:
            disposition = "ADD_MISSING_VERA_SOURCE_ENTRY"
            target = "CURRENT_MAIN"

        actions.append(
            {
                "repository": repo,
                "exact_public_head": subject.get("exact_public_head"),
                "disposition": disposition,
                "preferred_target": target,
                "desired_source_entry": {
                    "repository": repo,
                    "runtime_role": desired_role,
                    "activation_mode": desired_mode,
                    "authority_ceiling": desired_ceiling,
                    "privacy_class": "PUBLIC_SAFE_SOURCE",
                    "availability_implies_activation": False,
                },
                "vcp_disposition": subject.get("vcp_disposition"),
            }
        )

    source_actions = [
        item for item in actions
        if item["disposition"] not in {"ALREADY_SOURCE_INTEGRATED", "SATISFIED_BY_ACTIVE_CANDIDATE"}
    ]
    vcp_frontier = [
        {
            "repository": item["repository"],
            "vcp_disposition": item["vcp_disposition"],
            "state": "CONTROL_INTEGRATION_REVIEW_REQUIRED",
        }
        for item in actions
        if item["vcp_disposition"] != "NOT_CONTROL_PLANE"
    ]

    return {
        "schema": "DISCOVERY_VERA_VCP_IMPLEMENTATION_PLAN_V1",
        "status": "IMPLEMENTATION_DELTA_PLANNED_NOT_INSTALLED_NOT_RUNTIME_QUALIFIED",
        "subject_count": len(actions),
        "source_actions_required": len(source_actions),
        "actions": actions,
        "vcp_frontier": vcp_frontier,
        "rules": [
            "Active candidate work is reconciled before creating parallel edits.",
            "Source registration is an implementation effect in source control only; it is not installation or runtime consumption.",
            "VCP control integration remains separately reviewed and release-bound.",
            "No implementation action may infer authority from repository visibility, token capability, or Discovery candidate status.",
        ],
        "claim_ceiling": "SOURCE_INTEGRATION_DELTA_AND_VCP_REVIEW_FRONTIER_ONLY_NO_MERGE_NO_INSTALL_NO_RUNTIME_CONSUMPTION",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan Discovery-driven Vera/VCP source implementation.")
    parser.add_argument("--implementation-map", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--vera-registry", type=Path, required=True)
    parser.add_argument("--candidate-vera-registry", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    try:
        result = plan(
            _load(args.implementation_map),
            _load(args.vera_registry),
            _load(args.candidate_vera_registry) if args.candidate_vera_registry else None,
        )
    except ImplementationPlanError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
