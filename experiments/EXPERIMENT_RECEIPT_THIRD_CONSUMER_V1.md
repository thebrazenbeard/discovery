# Experiment receipt third-consumer falsifier V1

Status: **THIRD CONSUMER FOUND / PRIOR GENERIC PATTERN FALSIFIED / NO EXTRACTION**

The earlier World Zero ↔ Mosaic comparison rejected a shared experiment harness but left one weak residue:

`exact subject -> execution context -> result evidence -> explicit claim ceiling`

It deliberately required a third materially independent implementation before creating any reusable candidate.

DriftGuard is that third implementation.

Exact subjects remain current:

- World Zero: `science/demography-older-mortality-mass-normalization-v1-20260919@9be13e8e...`
- Mosaic: `one/mosaic-p1-protocol-harness-v1-20260918@96fd911e...`
- DriftGuard: `main@9894692...`

## World Zero

`RUN_RECEIPT_V1` explicitly binds:

- source commit/tree;
- scientific subject digests;
- calibration/holdout identity;
- solver/version/timestep/tolerance/seed;
- environment fingerprint;
- optional result digest.

Its domain-specific scientific qualification semantics remain outside the generic receipt surface.

## Mosaic

`MOSAIC_P1_PROTOCOL_HARNESS_RECEIPT_V1` returns:

- exact synthetic condition/case outcomes;
- accuracy/stale-error/correction-burden/payload metrics;
- explicit negative qualification gates;
- an explicit claim ceiling.

But the receipt object does **not** carry a general repository source commit/tree or execution-environment identity.

## DriftGuard

`DRIFTGUARD_RECOVERY_WINDOW_RECEIPT_V1` binds:

- initial recovery/state/policy digests;
- bounded turn window;
- evaluation digest trace;
- decision/reload/behavioral traces;
- durable disposition;
- receipt digest.

Its subject is a durable state/session/ledger recovery window, not a repository-source experiment identity. Its temporal claim ceiling is strongly documented, but not encoded as a generic receipt field.

## Three-way intersection

The original four-part residue does **not** survive intact:

- exact repository/source subject across all three: **no**
- general execution environment identity across all three: **no**
- result/evidence identity: **yes**
- explicit claim-ceiling field across all three: **no**
- meaningful common executable validation beyond digest/identity plumbing: **no**
- demonstrated existing code deleted/replaced by a common layer: **0**

Result:

`THIRD_CONSUMER_FALSIFIES_PRIOR_GENERIC_RECEIPT_PATTERN_NO_EXTRACTION`

> **HOSTILE REVIEWER:** You found three things called receipts and discovered they are domain records. Good. Do not rescue the abstraction by shrinking it to `id + digest + status`; that would be serialization, not architecture.

Agreed.

No shared receipt candidate is created. World Zero, Mosaic, and DriftGuard remain project-owned. A future candidate needs an organic additional consumer or a concrete adapter that measurably deletes duplicated non-domain plumbing without importing one project's validity rules into another.
