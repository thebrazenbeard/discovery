from __future__ import annotations

import copy
from pathlib import Path

import pytest

from tools.effect_observer import load_contract, observe_latest, validate_envelope


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "effect_attempt_envelope_v0.schema.json"
OBSERVER = ROOT / "tools" / "effect_observer.py"


def envelope(
    source_system: str,
    operation_id: str,
    phase: str,
    retry: str,
) -> dict:
    return {
        "schema_version": "DISCOVERY_EFFECT_ATTEMPT_V0",
        "source_system": source_system,
        "source_operation_id": operation_id,
        "source_state": "NATIVE_STATE_OPAQUE_TO_OBSERVER",
        "source_ref": "exact-source@0123456789abcdef0123456789abcdef01234567",
        "source_payload_sha256": "a" * 64,
        "action_class": "EXAMPLE_EFFECT",
        "target": {
            "kind": "example-target",
            "locator": f"example://{operation_id}",
            "expected_precondition": "generation=1",
        },
        "normalized_phase": phase,
        "retry_disposition": retry,
        "receipts": [
            {"kind": "native_receipt", "value": f"receipt-{operation_id}"}
        ],
    }


def contract():
    return load_contract(SCHEMA)


def test_one_observer_handles_three_current_producer_classes_without_branching():
    rows = [
        envelope("project-runner", "runner-op", "POST_EFFECT_VERIFIED", "DO_NOT_RETRY"),
        envelope("wip", "wip-op", "RECONCILED", "DO_NOT_RETRY"),
        envelope(
            "driftguard",
            "drift-op",
            "POST_EFFECT_UNVERIFIED",
            "DOMAIN_DECIDES",
        ),
    ]
    report = observe_latest(rows, contract=contract())
    assert report["total_latest_operations"] == 3
    assert report["phase_counts"]["POST_EFFECT_VERIFIED"] == 1
    assert report["phase_counts"]["RECONCILED"] == 1
    assert report["phase_counts"]["POST_EFFECT_UNVERIFIED"] == 1
    assert report["unresolved"] == ["driftguard:drift-op"]


def test_unknown_future_source_uses_same_path_without_registration():
    row = envelope(
        "future-system-with-no-discovery-code-change",
        "future-op",
        "OUTCOME_UNKNOWN",
        "INSPECT_BEFORE_RETRY",
    )
    report = observe_latest([row], contract=contract())
    assert report["inspection_required"] == [
        "future-system-with-no-discovery-code-change:future-op"
    ]
    assert report["phase_counts"]["OUTCOME_UNKNOWN"] == 1


def test_source_state_is_opaque_and_never_interpreted():
    row = envelope("arbitrary-source", "op", "PRE_EFFECT", "DOMAIN_DECIDES")
    row["source_state"] = "SOME_DOMAIN_STATE_DISCOVERY_HAS_NEVER_SEEN"
    validate_envelope(row, contract=contract())
    report = observe_latest([row], contract=contract())
    assert report["unresolved"] == ["arbitrary-source:op"]


def test_duplicate_latest_envelope_for_same_native_operation_fails_closed():
    row = envelope("source", "op", "PRE_EFFECT", "DOMAIN_DECIDES")
    with pytest.raises(ValueError, match="exactly one producer-selected latest"):
        observe_latest([row, copy.deepcopy(row)], contract=contract())


def test_invalid_normalized_phase_fails_against_schema_derived_contract():
    row = envelope("source", "op", "PRE_EFFECT", "DOMAIN_DECIDES")
    row["normalized_phase"] = "SOURCE_SPECIFIC_MAGIC"
    with pytest.raises(ValueError, match="outside the bound V0 contract"):
        validate_envelope(row, contract=contract())


def test_observer_implementation_contains_no_current_producer_names():
    source = OBSERVER.read_text(encoding="utf-8").lower()
    assert "project-runner" not in source
    assert "driftguard" not in source
    assert '"wip"' not in source
    assert "'wip'" not in source


def test_report_is_observational_not_authoritative():
    report = observe_latest(
        [envelope("source", "op", "POST_EFFECT_VERIFIED", "DO_NOT_RETRY")],
        contract=contract(),
    )
    assert report["authority_ceiling"] == (
        "OBSERVATIONAL_REPORT_ONLY_PRODUCERS_RETAIN_NATIVE_AUTHORITY"
    )
