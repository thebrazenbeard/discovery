import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / "portfolio" / "PORTFOLIO_CENSUS_20260924_V2.json"
BASELINE = ROOT / "portfolio" / "PUBLIC_CURRENTNESS_BASELINE_20260924_V2.json"


def _digest(names):
    payload = "".join(f"{name}\n" for name in sorted(names)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_census_v2_public_membership_and_arithmetic():
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    assert census["schema"] == "DISCOVERY_PORTFOLIO_CENSUS_V2"
    counts = census["counts"]
    assert counts["total"] == counts["public"] + counts["private"]
    assert counts["archived"] == (
        counts["public_archived"] + counts["private_archived"]
    )
    assert counts["total"] == 66
    assert counts["public"] == 48
    assert counts["private"] == 18
    assert len(census["public_repositories"]) == counts["public"]
    assert len(set(census["public_repositories"])) == counts["public"]
    assert _digest(census["public_repositories"]) == census["public_names_sha256"]


def test_census_v2_does_not_publish_unkeyed_private_name_digest():
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    private = census["private_inventory"]
    assert private["count"] == census["counts"]["private"]
    assert private["public_commitment_scheme"] == "COUNT_ONLY_PUBLIC_V1"
    assert private["exact_membership_publicly_committed"] is False
    serialized = json.dumps(private, sort_keys=True)
    assert "private_names_sha256" not in serialized
    assert "hmac_sha256" not in serialized


def test_predecessor_whole_public_evidence_is_explicitly_stale():
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    effect = census["currentness_effect"]
    assert effect["prior_public_graph_current"] is False
    assert effect["prior_public_intake_current"] is False
    assert effect["prior_public_blob_overlap_scan_current"] is False
    assert effect["prior_architecture_observatory_current"] is False


def test_census_v2_and_exact_currentness_baseline_membership_match():
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    baseline_names = sorted(item["name"] for item in baseline["repositories"])
    assert baseline["repository_count"] == census["counts"]["public"]
    assert baseline_names == sorted(census["public_repositories"])
