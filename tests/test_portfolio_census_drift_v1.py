from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRIFT = ROOT / "portfolio" / "PORTFOLIO_CENSUS_DRIFT_20260930_V1.json"


def test_live_drift_fails_closed_without_replacing_census():
    data = json.loads(DRIFT.read_text(encoding="utf-8"))
    assert data["base_census"]["counts"] == {"total": 74, "public": 55, "private": 19}
    assert data["live_authenticated_inventory"]["counts"] == {
        "total": 76,
        "public": 57,
        "private": 19,
        "archived": 2,
        "public_archived": 0,
        "private_archived": 2,
    }
    assert data["status"] == "BASE_CENSUS_STALE_REQUIRES_FULL_DETERMINISTIC_REFRESH"
    assert data["rules"]["this_artifact_is_not_replacement_census"] is True


def test_drift_publishes_only_new_public_membership():
    data = json.loads(DRIFT.read_text(encoding="utf-8"))
    assert data["live_authenticated_inventory"]["public_additions_since_base"] == [
        "thebrazenbeard/thebrazenbeard",
        "thebrazenbeard/workbridge",
    ]
    assert data["live_authenticated_inventory"]["public_removals_since_base"] == []
    assert data["private_inventory"]["count"] == 19
    assert data["private_inventory"]["exact_membership_publicly_committed"] is False
    assert data["classification_state"] == "NEW_PUBLIC_SUBJECTS_UNCLASSIFIED_PENDING_DEDICATED_REVIEW"
    assert data["rules"]["do_not_publish_private_names"] is True
