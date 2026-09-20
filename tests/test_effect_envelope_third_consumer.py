from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "effect_attempt_envelope_v0.schema.json"
CANDIDATE = ROOT / "candidates" / "RUNNER_WIP_EXECUTION_INTEGRITY_V1.json"
EXPERIMENT = ROOT / "experiments" / "RUNNER_WIP_EFFECT_INTEGRITY_V1.md"


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def test_third_consumer_did_not_mutate_v0_envelope_schema():
    raw = SCHEMA.read_bytes()
    assert git_blob_sha1(raw) == "b5d85ba31a33ad7192fd4a08934628a72e593312"


def test_candidate_has_three_distinct_exact_public_consumers():
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    consumers = candidate["consumers"]
    assert len(consumers) == 3
    assert len({row["repo"] for row in consumers}) == 3
    driftguard = next(
        row for row in consumers if row["repo"] == "thebrazenbeard/driftguard"
    )
    assert driftguard["ref"] == (
        "work/discovery-effect-envelope-consumer-v1-20260920"
        "@976f50ca391560d16ebcdcfe478df28b1cd1efca"
    )
    assert candidate["status"] == "EXPERIMENTING"


def test_experiment_preserves_acknowledged_not_verified_boundary():
    text = EXPERIMENT.read_text(encoding="utf-8")
    assert "accepted reload acknowledgement → `POST_EFFECT_UNVERIFIED`" in text
    assert "no DriftGuard adapter path to `POST_EFFECT_VERIFIED`" in text
    assert "THREE_CONSUMER_INTEROPERABILITY_SUPPORTED" in text


def test_v0_schema_already_contains_required_driftguard_phases():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    phases = set(schema["properties"]["normalized_phase"]["enum"])
    assert "PRE_EFFECT" in phases
    assert "POST_EFFECT_UNVERIFIED" in phases
    assert "POST_EFFECT_VERIFIED" in phases
    assert schema["additionalProperties"] is False
