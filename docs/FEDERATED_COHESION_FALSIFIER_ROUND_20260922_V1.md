# Federated Cohesion Falsifier Round — 2026-09-22 V1

Status: **PUBLIC-SAFE / SOURCE-BOUND / HYPOTHESIS NARROWING**

Parent research subject:

`Discovery PR #25 @ 7167f65ad74b3b1bb2114fa8397b8c2c1308390b`

This round does not create another broad architecture proposal. It asks whether the federated-cohesion hypothesis from PR #25 survives four newer exact-head Discovery experiments.

## Result

It survives, but in a narrower form.

The evidence no longer supports even a soft assumption that one reusable receipt, verifier, or boundary schema will span the portfolio. What survives is smaller:

> **Keep native project semantics local. Share only narrow boundary contracts and evidence-class distinctions that remain semantically neutral and earn their maintenance cost through real consumers.**

### PR #26 — semantic provenance interchange

Exact subject:

`a64e3c44c781012adf32f65338703713543d190e`

The narrow semantic/provenance envelope passed with limits. Semantic Atlas, UNVTRSLR and SPM could share structural provenance/claim-control fields without promoting one project's ontology into another.

That is positive federation evidence.

It is not reuse-economics evidence. No production/model implementation consumes it and no duplicated maintenance has yet been shown to disappear.

### PR #27 — VeraMesh → Vera Synology handoff

Exact subject:

`018028702eadd4693623d887b2228d8fa5d6e44f`

The stronger native handoff claim failed.

Vera Synology can verify its local package/source identity, but its native validation path does not establish the exact VeraMesh producer repository/head. Discovery can correlate the two exact refs externally; that correlation is not native Synology validation.

This is a useful boundary result:

`EXTERNAL_CORRELATION != NATIVE_CONSUMER_PROVENANCE`

### PR #28 — third receipt consumer

Exact subject:

`c19a73c4b563e001b09189d688b995d7b368e58b`

World Zero, Mosaic and DriftGuard falsified the prior four-part generic receipt pattern.

The only robust intersection was too weak to justify extraction. Exact repository source identity, general execution context and explicit claim-ceiling placement differ materially. Zero existing code was deleted by a common layer.

That means the useful commonality is currently closer to a **vocabulary of evidence classes** than one universal receipt schema.

### PR #29 — Rezon ↔ Project Runner maintenance currentness

Exact subject:

`033f96d171fb7eed7fba537e6044e31eb94c472a`

The mechanical/epistemic boundary still works. Project Runner can structurally verify Rezon evidence without becoming Rezon's truth or admission authority.

But the verifier is no longer credibly producer-agnostic. Hardening required mirroring Rezon producer-ID invariants and claim-disposition restrictions.

Measured successor delta from the original verifier:

- 11 commits;
- 7 changed files;
- +445 / -16 lines;
- +73 verifier lines;
- +80 primary test lines;
- +105 failure-path test lines.

That work closed real hostile findings, so the added code is not automatically waste. But it is real coupling cost, and no second organic consumer or net maintenance saving has yet been demonstrated.

## What changed from PR #25

The original federated-cohesion hypothesis proposed testing an organic cross-project handoff and a typed currentness receipt.

After these four experiments:

**FED-EXP-1** remains unresolved. We have a useful mechanical boundary, but also measurable coupling, no second organic consumer, and one failed native cross-repository provenance handoff.

**FED-EXP-2**, interpreted as one reusable generic receipt, is falsified for the current evidence set. What survives is the weaker proposition that source/build/install/route/effect/qualification are useful **distinct evidence classes** even when each project encodes them differently.

## Narrowed architecture rule

Prefer:

`local native model + exact boundary contract + explicit fallback`

Do not promote:

`one shared runtime/schema/verifier`

unless the shared mechanism independently demonstrates:

1. at least two organic consumers;
2. preserved native authority and semantics;
3. measurable deletion of duplicated non-domain glue, maintenance reduction, or prevention of a known failure class;
4. local operability when the shared component is absent;
5. exact rollback/fallback behavior.

This changes the burden of proof. Compatibility is no longer enough.

## Hostile review

> **HOSTILE REVIEWER:** You can make federation unfalsifiable by treating every failed abstraction as evidence that projects should stay separate.

Accepted as a blocking objection. A future shared abstraction must be allowed to beat federation when it demonstrates lower total complexity, real organic reuse, preserved authority boundaries and rollbackability.

> **HOSTILE REVIEWER:** “Shared evidence-class vocabulary” can quietly become a universal ontology with nicer branding.

Accepted. Labels such as source, install, effect or qualification are descriptive categories only. Their project-native meaning and admissibility criteria remain local unless separately proven reusable.

> **HOSTILE REVIEWER:** Rezon→Runner code growth does not prove reuse is economically bad.

Correct. It proves coupling cost exists. A comparative baseline is still needed before an economic conclusion can be made.

## Next valid falsifier

Do not build another adapter merely to populate Discovery.

Find one existing organic integration where a narrow boundary contract can either:

- delete duplicated non-domain code that already exists; or
- prevent a previously observed failure class;

while both participants remain independently operable.

Until that evidence exists, the narrowed hypothesis remains:

`HYPOTHESIS_ONLY`

Claim ceiling:

`FOUR_EXACT_FALSIFIERS_INGESTED_HYPOTHESIS_SURVIVES_NARROWED_NO_REUSE_PROMOTION_NO_RUNTIME_AUTHORITY`
