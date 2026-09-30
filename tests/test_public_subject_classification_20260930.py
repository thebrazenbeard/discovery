from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLASSIFICATION = ROOT / "portfolio" / "PUBLIC_SUBJECT_CLASSIFICATION_20260930_V1.json"


def test_all_four_new_public_subjects_are_exact_head_classified():
    data = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
    records = {row["id"]: row for row in data["subjects"]}
    assert set(records) == {
        "semiotics", "thebrazenbeard", "workbridgecommander", "workbridge"
    }
    assert records["semiotics"]["exact_head"] == "37117a2097f7f2aa35968fc9db24eacf7240826e"
    assert records["thebrazenbeard"]["exact_head"] == "83ea2e083ccbf83ad5215ca53a9d5a00d16bb0d0"
    assert records["workbridgecommander"]["exact_head"] == "c2b95be79ca011a539c20bfee60fcbc46cfea177"
    assert records["workbridge"]["exact_head"] == "7caab29eb5667897a0a03d0ce67d733380b01685"


def test_classification_does_not_alias_workbridge_surfaces_or_grant_effects():
    data = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
    records = {row["id"]: row for row in data["subjects"]}
    assert records["workbridgecommander"]["family_id"] == "coordination"
    assert records["workbridge"]["family_id"] == "workstation-runtime"
    assert data["authority_ceiling"] == "DESCRIPTIVE_SOURCE_CLASSIFICATION_ONLY"
    boundaries = data["cross_subject_boundaries"]
    assert "not aliased" in boundaries["WorkBridgeMCP"]
    assert "independent currentness" in boundaries["workbridge"]


def test_profile_is_presentation_not_currentness_authority():
    data = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
    profile = next(row for row in data["subjects"] if row["id"] == "thebrazenbeard")
    assert profile["family_id"] == "portfolio-presentation"
    assert "do not use profile prose as project currentness or authority" in profile["current_frontier"]
