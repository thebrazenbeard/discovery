"""Integrity checks for the descriptive (non-authorizing) V2 owner census."""
import hashlib
import json
from pathlib import Path

CENSUS = Path(__file__).resolve().parents[1] / "portfolio" / "PORTFOLIO_CENSUS_V2.json"


def test_portfolio_census_v2_membership_and_privacy():
    data = json.loads(CENSUS.read_text(encoding="utf-8"))
    counts = data["counts"]
    names = data["public_repositories"]
    archived = data["archived_repositories_public"]
    assert data["schema"] == "DISCOVERY_PORTFOLIO_CENSUS_V2"
    assert len(names) == len(set(names)) == counts["public"]
    assert names == sorted(names)
    assert set(archived).issubset(set(names))
    assert len(archived) == counts["archived_public"]
    assert counts["total"] == counts["public"] + counts["private"]
    assert counts["archived"] == counts["archived_public"] + counts["archived_private"]
    assert counts["active"] == counts["active_public"] + counts["active_private"]
    assert counts["total"] == counts["active"] + counts["archived"]
    digest = hashlib.sha256(("".join(n + "\n" for n in names)).encode("utf-8")).hexdigest()
    assert data["inventory_digests"]["public_names_sha256"] == digest
    assert "private_repositories" not in data
