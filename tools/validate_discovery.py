from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / "portfolio" / "PORTFOLIO_CENSUS_V1.json"
GRAPH = ROOT / "portfolio" / "PUBLIC_RELATIONSHIP_GRAPH_V1.json"
CANDIDATES = ROOT / "candidates"

VALID_RELATIONS = {
    "OVERLAPPING_MECHANIC",
    "DUPLICATED_IMPLEMENTATION",
    "COMPLEMENTARY_BOUNDARY",
    "POTENTIAL_BASE_OVERLAY",
    "PROVIDER_CONSUMER",
    "MUST_REMAIN_SEPARATE",
    "NEGATIVE_CONTROL",
    "HISTORICAL_REFERENCE",
    "NEEDS_MORE_EVIDENCE",
}
VALID_STATES = {
    "OBSERVED",
    "HYPOTHESIS",
    "EXPERIMENTING",
    "SUPPORTED",
    "REJECTED",
    "SUPERSEDED",
}
CANDIDATE_STATES = {
    "OBSERVED",
    "HYPOTHESIS",
    "EXPERIMENTING",
    "PROVEN_REUSABLE",
    "PROJECT_SPECIFIC",
    "REJECTED",
    "SUPERSEDED",
}
EXACT_SUBJECT_REF = re.compile(
    r"^(?:[0-9a-f]{40}|[^@\s]+@[0-9a-f]{40})$"
)
PLACEHOLDER_REPO_PREFIXES = ("TBD", "UNKNOWN", "PLACEHOLDER")


def _nonempty_string(value) -> bool:
    return type(value) is str and bool(value.strip())


def _validate_candidate_lifecycle(candidate: dict, *, filename: str) -> list[str]:
    errors: list[str] = []
    status = candidate.get("status")
    if status not in CANDIDATE_STATES:
        return [f"candidate unsupported status: {filename}"]

    consumers = candidate.get("consumers")
    if not isinstance(consumers, list) or len(consumers) < 2:
        return [f"candidate needs at least two consumers: {filename}"]

    repos: list[str] = []
    active = status in {"EXPERIMENTING", "PROVEN_REUSABLE"}
    for index, consumer in enumerate(consumers):
        if not isinstance(consumer, dict):
            errors.append(f"candidate consumer invalid: {filename}:{index}")
            continue
        repo = consumer.get("repo")
        role = consumer.get("role")
        ref = consumer.get("ref")
        if not _nonempty_string(repo):
            errors.append(f"candidate consumer repo invalid: {filename}:{index}")
        else:
            repos.append(repo.strip())
        if not _nonempty_string(role):
            errors.append(f"candidate consumer role invalid: {filename}:{index}")
        if active:
            if (
                not _nonempty_string(repo)
                or repo.strip().upper().startswith(PLACEHOLDER_REPO_PREFIXES)
            ):
                errors.append(
                    f"active candidate consumer is placeholder: {filename}:{index}"
                )
            if not isinstance(ref, str) or not EXACT_SUBJECT_REF.fullmatch(ref):
                errors.append(
                    f"active candidate consumer ref not exact: {filename}:{index}"
                )

    if active and len(set(repos)) < 2:
        errors.append(f"active candidate consumers not distinct: {filename}")

    promotion_evidence = candidate.get("promotion_evidence")
    if not isinstance(promotion_evidence, list) or any(
        not _nonempty_string(item) for item in promotion_evidence
    ):
        errors.append(f"candidate promotion evidence invalid: {filename}")
        promotion_evidence = []

    hostile = candidate.get("hostile_review")
    if not isinstance(hostile, dict):
        errors.append(f"candidate hostile review invalid: {filename}")
        hostile = {}
    hostile_status = hostile.get("status")
    objections = hostile.get("critical_objections")
    if hostile_status not in {"NOT_RUN", "FAIL", "PASS_WITH_LIMITS", "PASS"}:
        errors.append(f"candidate hostile review status invalid: {filename}")
    if not isinstance(objections, list) or any(
        not _nonempty_string(item) for item in objections
    ):
        errors.append(f"candidate hostile objections invalid: {filename}")
        objections = []

    if active:
        if not promotion_evidence:
            errors.append(f"active candidate lacks promotion evidence: {filename}")
        if hostile_status == "NOT_RUN":
            errors.append(f"active candidate lacks hostile review: {filename}")

    if status == "PROVEN_REUSABLE":
        if len(promotion_evidence) < 2:
            errors.append(f"proven candidate lacks independent evidence: {filename}")
        if hostile_status != "PASS":
            errors.append(f"proven candidate hostile review not clean PASS: {filename}")
        if objections:
            errors.append(f"proven candidate has critical objections: {filename}")

    return errors


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate() -> list[str]:
    errors: list[str] = []
    census = load(CENSUS)
    graph = load(GRAPH)

    if graph.get("schema_version") != "DISCOVERY_RELATIONSHIP_GRAPH_V1":
        errors.append("unexpected graph schema")

    binding = graph.get("inventory_binding", {})
    if binding.get("total_count") != census.get("counts", {}).get("total"):
        errors.append("graph total_count does not match census")
    if (
        binding.get("all_names_sha256")
        != census.get("inventory_digests", {}).get("all_names_sha256")
    ):
        errors.append("graph inventory digest does not match census")

    nodes = graph.get("nodes")
    if not isinstance(nodes, list):
        return errors + ["nodes must be a list"]

    node_ids: set[str] = set()
    for node in nodes:
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            errors.append("node missing id")
            continue
        if node_id in node_ids:
            errors.append(f"duplicate node id: {node_id}")
        node_ids.add(node_id)
        if node.get("privacy") == "PRIVATE":
            errors.append(f"raw private node forbidden in public graph: {node_id}")

    edges = graph.get("edges")
    if not isinstance(edges, list):
        return errors + ["edges must be a list"]

    edge_ids: set[str] = set()
    for edge in edges:
        edge_id = edge.get("edge_id")
        if not isinstance(edge_id, str) or not edge_id:
            errors.append("edge missing edge_id")
            continue
        if edge_id in edge_ids:
            errors.append(f"duplicate edge id: {edge_id}")
        edge_ids.add(edge_id)

        if edge.get("from") not in node_ids or edge.get("to") not in node_ids:
            errors.append(f"edge has unknown endpoint: {edge_id}")
        if edge.get("relation") not in VALID_RELATIONS:
            errors.append(f"unsupported relation: {edge_id}")
        if edge.get("evidence_state") not in VALID_STATES:
            errors.append(f"unsupported evidence state: {edge_id}")
        if not edge.get("scope"):
            errors.append(f"edge missing scope: {edge_id}")
        if not edge.get("source_refs"):
            errors.append(f"edge missing source refs: {edge_id}")
        if not edge.get("falsifiers"):
            errors.append(f"edge missing falsifiers: {edge_id}")

    public_repos = set(census.get("public_repositories", []))
    public_nodes = {
        node["id"]
        for node in nodes
        if node.get("kind") == "REPOSITORY" and node.get("privacy") == "PUBLIC"
    }
    if public_nodes != public_repos:
        errors.append(
            "public graph repository nodes must exactly equal public census repositories"
        )

    for path in CANDIDATES.glob("*.json"):
        candidate = load(path)
        if candidate.get("schema_version") != "DISCOVERY_CANDIDATE_V1":
            errors.append(f"candidate schema mismatch: {path.name}")
        if not candidate.get("rejection_conditions"):
            errors.append(f"candidate missing rejection conditions: {path.name}")
        errors.extend(
            _validate_candidate_lifecycle(candidate, filename=path.name)
        )

    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        for problem in problems:
            print(problem)
        raise SystemExit(1)
    print("Discovery validation PASS")
