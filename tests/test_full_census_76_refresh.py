from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / "portfolio" / "PORTFOLIO_CENSUS_V1.json"
INTAKE = ROOT / "portfolio" / "PUBLIC_SUBJECT_INTAKE_20260921_V1.json"
GRAPH = ROOT / "portfolio" / "PUBLIC_RELATIONSHIP_GRAPH_V1.json"
SHARDS = (
    ROOT / "experiments" / "public_blob_index_v1" / "SHARD_A.json",
    ROOT / "experiments" / "public_blob_index_v1" / "SHARD_B.json",
)


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _subjects():
    out = {}
    for path in SHARDS:
        out.update(_load(path)["repositories"])
    return out


def test_20260930_cut_is_76_total_57_public_19_private():
    census = _load(CENSUS)
    assert census["observed_date"] == "2026-09-30"
    assert census["counts"] == {"total": 76, "public": 57, "private": 19}
    assert len(census["public_repositories"]) == 57
    assert census["inventory_digests"]["public_names_sha256"] == (
        "112028b82ae5eaca484908612721cea05df4bbb6b4861262dcbc587c98292d64"
    )


def test_generated_subject_set_matches_census_and_intake_exact_refs():
    census = _load(CENSUS)
    intake = _load(INTAKE)
    subjects = _subjects()
    assert set(subjects) == set(census["public_repositories"])
    prior = set(intake["prior_public_cut"]["public_repositories"])
    assert len(intake["subjects"]) == 45
    assert {
        row["repo"].split("/", 1)[1] for row in intake["subjects"]
    } == set(census["public_repositories"]) - prior
    for row in intake["subjects"]:
        name = row["repo"].split("/", 1)[1]
        subject = subjects[name]
        assert row["ref"] == f'{subject["default_branch"]}@{subject["head"]}'


def test_graph_covers_every_public_subject_and_private_membership_is_opaque():
    census = _load(CENSUS)
    graph = _load(GRAPH)
    public_nodes = {
        node["id"]
        for node in graph["nodes"]
        if node.get("kind") == "REPOSITORY" and node.get("privacy") == "PUBLIC"
    }
    assert public_nodes == set(census["public_repositories"])
    private = [node for node in graph["nodes"] if node.get("privacy") == "PRIVATE_OPAQUE"]
    assert private == [{
        "id": "private-cohort",
        "kind": "OPAQUE_PRIVATE_COHORT",
        "privacy": "PRIVATE_OPAQUE",
        "labels": ["19_PRIVATE_REPOSITORIES"],
        "notes": [
            "Node intentionally hides private repository identities; count bound to the 2026-09-30 census."
        ],
    }]


def test_new_discovery_members_have_bounded_descriptive_roles():
    intake = _load(INTAKE)
    rows = {row["repo"].split("/", 1)[1]: row for row in intake["subjects"]}
    assert rows["thebrazenbeard"]["primary_families"] == ["PORTFOLIO_PRESENTATION"]
    assert rows["workbridge"]["primary_families"] == [
        "WORKSTATION_RUNTIME",
        "DERIVED_IMPLEMENTATION_LINEAGE",
    ]
