# Public intake second pass V1

Status: **SOURCE-BOUND / CLASSIFICATION REFRESH**

This pass resolves four entries left open by the complete public-subject intake.

## VeraMesh

Exact subject: `PR #12 @ 9bffc57930587bf74a12657bbeaa913474ab5574`.

The source exposes concrete reusable-looking mechanics around authenticated route/session currentness, bounded failover, mutation ambiguity, durable idempotency, and explicit source/runtime/effect separation.

The important boundary is that VeraMesh owns transport/application-session semantics. Its MCP profile explicitly refuses to treat source creation, server runtime, plugin registration, route currentness, and live effects as interchangeable states.

## Vera Synology

Exact subject: `PR #3 @ 553e3a637833c5469f6b99fbc4d597755a0c9a5e`.

The package source exposes a different mechanical surface: deterministic SPK verification, source-manifest byte/mode cross-binding, fail-closed legacy-state migration, and installed-version versus current-source separation.

This supports a **complementary boundary**, not a merge:

`VeraMesh transport/session source -> package/source handoff -> Synology build/install/runtime currentness`

Neither side should infer the other's authority.

## Voss

Exact public head: `main@54478372002bb24c6df733092a32abbdd1fa8d3c`.

The public repository currently contains only the README role statement that Voss is a forensic auditor/reviewer. That is insufficient to infer a reusable audit protocol, receipt schema, exact-head review contract, or implementation.

Disposition: `INSUFFICIENT_PUBLIC_SOURCE_NO_CANDIDATE`.

## ABIL industrial handoff search

ABIL remains the public industrial-chain anchor.

Discovery searched the other 22 repositories in the bound public census for:

- `brownfield PLC industrial`
- `historian fieldbus`
- `OPC Modbus`
- `machine telemetry sensor`

No second public industrial handoff subject was returned on the current default-branch search cut.

This is a negative result, not proof of absence. Branch-only, unindexed, differently worded, private, or future subjects may still exist.

Disposition: `HOLD_PUBLIC_INDUSTRIAL_HANDOFF_CANDIDATE`.

> **HOSTILE REVIEWER:** Search-term absence is weak evidence. Do not turn it into “ABIL is unique” or into permission to bind a generic telemetry system as an industrial producer.

Accepted. The only justified conclusion is that Discovery lacks a defensible **public** second industrial subject on this cut.
