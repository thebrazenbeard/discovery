from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / "portfolio" / "PORTFOLIO_CENSUS_V1.json"
INTAKE = ROOT / "portfolio" / "PUBLIC_SUBJECT_INTAKE_20260921_V1.json"
GRAPH = ROOT / "portfolio" / "PUBLIC_RELATIONSHIP_GRAPH_V1.json"
CLASSIFICATION = ROOT / "portfolio" / "PUBLIC_SUBJECT_CLASSIFICATION_20261001_V1.json"
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


def test_20261001_cut_is_77_total_58_public_19_private():
    census = _load(CENSUS)
    assert census["observed_date"] == "2026-10-01"
    assert census["counts"] == {"total": 77, "public": 58, "private": 19}
    assert len(census["public_repositories"]) == 58
    assert census["inventory_digests"]["public_names_sha256"] == (
        "443fc84900700b79f435d88810dec8e1b250dd73fa184d509bd16375411d9fcd"
    )


def test_generated_subject_set_matches_census_and_intake_exact_refs():
    census = _load(CENSUS)
    intake = _load(INTAKE)
    subjects = _subjects()
    assert set(subjects) == set(census["public_repositories"])
    prior = set(intake["prior_public_cut"]["public_repositories"])
    assert len(intake["subjects"]) == 46
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
            "Node intentionally hides private repository identities; count bound to the 2026-10-01 census."
        ],
    }]


def test_pre_active_preserves_pro_run_repository_identity():
    data = _load(CLASSIFICATION)
    row = next(item for item in data["subjects"] if item["id"] == "pre-active")
    assert row["github_repository_id"] == 1387754784
    assert row["renamed_from"] == "thebrazenbeard/pro-run"
    assert row["exact_head"] == "0ffc95351db34afed091c3239614f57f371c04ad"
    assert row["classification"] == "RENAME_CONTINUITY_UNCLASSIFIED"


def test_executor_current_main_is_not_promoted_to_draft_candidate_role():
    data = _load(CLASSIFICATION)
    row = next(item for item in data["subjects"] if item["id"] == "executor")
    assert row["exact_main"] == "2b9b4e9456c6481b1d5fe9be0a142d01ce804d8f"
    assert row["current_main_classification"] == "BOOTSTRAP_ONLY_UNCLASSIFIED"
    assert row["draft_candidate"]["pr"] == 1
    assert row["draft_candidate"]["head"] == "f099c1af21f350d1f05a22fc13ed3658b31c6f4d"
    assert row["draft_candidate"]["ci_conclusion"] == "success"
    assert data["authority_ceiling"] == "DESCRIPTIVE_IDENTITY_AND_SOURCE_CLASSIFICATION_ONLY"
