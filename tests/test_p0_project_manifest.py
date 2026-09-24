import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "portfolio" / "P0_PROJECT_MANIFEST_V1.json"
CENSUS = ROOT / "portfolio" / "PORTFOLIO_CENSUS_20260924_V2.json"


def test_p0_manifest_is_descriptive_not_authority():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["schema"] == "PROJECT_RUNNER_P0_PROJECT_MANIFEST_V1"
    assert manifest["classification"]["project_id"] == "discovery"
    assert manifest["classification"]["priority"] == "P0"
    governance = manifest["governance"]
    assert governance["priority_is_authority"] is False
    assert governance["scheduling_requires_currentness"] is True
    assert governance["effect_requires_explicit_authority"] is True
    assert governance["merge_deploy_not_granted"] is True


def test_p0_manifest_binds_current_67_repository_census():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    assert census["counts"] == {
        "total": 67,
        "public": 49,
        "private": 18,
        "archived": 2,
        "public_archived": 0,
        "private_archived": 2,
    }
    assert (
        manifest["classification"]["source_subject"]
        == "thebrazenbeard/project-runner@381559dd07e52105b4e352a90e207a03c6793ff0:portfolio/corpus.public.json"
    )
    assert "sql-connectome" in census["public_repositories"]


def test_public_p0_manifest_does_not_reintroduce_private_set_fingerprints():
    serialized = MANIFEST.read_text(encoding="utf-8")
    assert "private_names_sha256" not in serialized
    assert "all_names_sha256" not in serialized
