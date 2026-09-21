from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any, Iterable


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class EffectEnvelopeContract:
    required_fields: frozenset[str]
    allowed_fields: frozenset[str]
    phases: frozenset[str]
    retry_dispositions: frozenset[str]
    target_required: frozenset[str]
    target_allowed: frozenset[str]
    receipt_required: frozenset[str]
    receipt_allowed: frozenset[str]

    @classmethod
    def from_schema(cls, schema: dict[str, Any]) -> "EffectEnvelopeContract":
        props = schema["properties"]
        target = props["target"]
        receipt = props["receipts"]["items"]
        return cls(
            required_fields=frozenset(schema["required"]),
            allowed_fields=frozenset(props),
            phases=frozenset(props["normalized_phase"]["enum"]),
            retry_dispositions=frozenset(props["retry_disposition"]["enum"]),
            target_required=frozenset(target["required"]),
            target_allowed=frozenset(target["properties"]),
            receipt_required=frozenset(receipt["required"]),
            receipt_allowed=frozenset(receipt["properties"]),
        )


def load_contract(path: str | Path) -> EffectEnvelopeContract:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("effect-envelope schema must be a JSON object")
    return EffectEnvelopeContract.from_schema(value)


def _require_exact_fields(
    value: dict[str, Any],
    *,
    required: frozenset[str],
    allowed: frozenset[str],
    label: str,
) -> None:
    keys = set(value)
    missing = required - keys
    extra = keys - allowed
    if missing:
        raise ValueError(f"{label} missing required fields: {sorted(missing)}")
    if extra:
        raise ValueError(f"{label} has unexpected fields: {sorted(extra)}")


def _nonempty_string(value: Any, label: str) -> str:
    if type(value) is not str or not value:
        raise ValueError(f"{label} must be a non-empty exact string")
    return value


def validate_envelope(
    envelope: dict[str, Any],
    *,
    contract: EffectEnvelopeContract,
) -> None:
    if type(envelope) is not dict:
        raise ValueError("effect envelope must be a JSON object")
    _require_exact_fields(
        envelope,
        required=contract.required_fields,
        allowed=contract.allowed_fields,
        label="effect envelope",
    )
    if envelope.get("schema_version") != "DISCOVERY_EFFECT_ATTEMPT_V0":
        raise ValueError("unsupported effect-envelope schema version")

    for field in (
        "source_system",
        "source_operation_id",
        "source_state",
        "source_ref",
        "action_class",
    ):
        _nonempty_string(envelope.get(field), field)

    payload_digest = envelope.get("source_payload_sha256")
    if payload_digest is not None and (
        type(payload_digest) is not str or _SHA256.fullmatch(payload_digest) is None
    ):
        raise ValueError("source_payload_sha256 must be null or lowercase SHA-256")

    phase = envelope.get("normalized_phase")
    if phase not in contract.phases:
        raise ValueError("normalized_phase is outside the bound V0 contract")
    retry = envelope.get("retry_disposition")
    if retry not in contract.retry_dispositions:
        raise ValueError("retry_disposition is outside the bound V0 contract")

    target = envelope.get("target")
    if type(target) is not dict:
        raise ValueError("target must be an object")
    _require_exact_fields(
        target,
        required=contract.target_required,
        allowed=contract.target_allowed,
        label="target",
    )
    _nonempty_string(target.get("kind"), "target.kind")
    _nonempty_string(target.get("locator"), "target.locator")
    expected = target.get("expected_precondition")
    if expected is not None and type(expected) is not str:
        raise ValueError("target.expected_precondition must be string or null")

    receipts = envelope.get("receipts")
    if type(receipts) is not list:
        raise ValueError("receipts must be an array")
    for index, receipt in enumerate(receipts):
        if type(receipt) is not dict:
            raise ValueError(f"receipt {index} must be an object")
        _require_exact_fields(
            receipt,
            required=contract.receipt_required,
            allowed=contract.receipt_allowed,
            label=f"receipt {index}",
        )
        _nonempty_string(receipt.get("kind"), f"receipt {index}.kind")
        _nonempty_string(receipt.get("value"), f"receipt {index}.value")


def _operation_key(envelope: dict[str, Any]) -> str:
    return f"{envelope['source_system']}:{envelope['source_operation_id']}"


def observe_latest(
    envelopes: Iterable[dict[str, Any]],
    *,
    contract: EffectEnvelopeContract,
) -> dict[str, Any]:
    """Summarize one latest native envelope per source-native operation.

    Latest-event selection is intentionally producer-owned. This observer does
    not know or infer source-native ordering, authority, retry, or completion
    semantics beyond the normalized fields already supplied by each producer.
    """
    rows = list(envelopes)
    seen: set[str] = set()
    phase_counts = {phase: 0 for phase in sorted(contract.phases)}
    retry_counts = {
        disposition: 0 for disposition in sorted(contract.retry_dispositions)
    }
    inspection_required: list[str] = []
    unresolved: list[str] = []
    verified: list[str] = []
    reconciled: list[str] = []

    for envelope in rows:
        validate_envelope(envelope, contract=contract)
        key = _operation_key(envelope)
        if key in seen:
            raise ValueError(
                "observer requires exactly one producer-selected latest envelope "
                f"per source-native operation: duplicate {key}"
            )
        seen.add(key)

        phase = envelope["normalized_phase"]
        retry = envelope["retry_disposition"]
        phase_counts[phase] += 1
        retry_counts[retry] += 1

        if retry == "INSPECT_BEFORE_RETRY":
            inspection_required.append(key)
        if phase in {"PRE_EFFECT", "POST_EFFECT_UNVERIFIED", "OUTCOME_UNKNOWN"}:
            unresolved.append(key)
        if phase == "POST_EFFECT_VERIFIED":
            verified.append(key)
        if phase == "RECONCILED":
            reconciled.append(key)

    return {
        "schema": "DISCOVERY_EFFECT_OBSERVER_REPORT_V1",
        "total_latest_operations": len(rows),
        "phase_counts": phase_counts,
        "retry_counts": retry_counts,
        "inspection_required": sorted(inspection_required),
        "unresolved": sorted(unresolved),
        "verified": sorted(verified),
        "reconciled": sorted(reconciled),
        "authority_ceiling": (
            "OBSERVATIONAL_REPORT_ONLY_PRODUCERS_RETAIN_NATIVE_AUTHORITY"
        ),
    }


def _load_envelope(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Observe producer-selected latest Discovery effect envelopes."
    )
    parser.add_argument(
        "--schema",
        default="schemas/effect_attempt_envelope_v0.schema.json",
        type=Path,
    )
    parser.add_argument("envelopes", nargs="+", type=Path)
    args = parser.parse_args(argv)

    contract = load_contract(args.schema)
    report = observe_latest(
        (_load_envelope(path) for path in args.envelopes),
        contract=contract,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
