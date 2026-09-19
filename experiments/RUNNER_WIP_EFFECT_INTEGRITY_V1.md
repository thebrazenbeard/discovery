# Runner ↔ WIP Effect Integrity Experiment V1

Status: **EXPERIMENTING / PARTIAL SUPPORT / HYPOTHESIS NARROWED**

## Exact subjects

Project Runner:
- main: `bc05812b560b4fcde3a362e72fba04c626cafac8`
- work-unit schema blob: `65fd4f1af1812c280cbec0726a55b61b6ff02e76`
- GitHub backend blob: `833915398626c091a5df1dcc96504a7a12e7325f`
- verification blob: `e4f0453404013cbfe26882ea4805ae2fb3ce25aa`
- lease implementation blob: `eeb34650b6a2f6e990917a6e6c9075c18800ccab`
- persistent-state blob: `9f74b6ac50629976d79b73628b26c34201e9b099`

WIP:
- main: `12a7c23dbe0482fd7bfe63659e54526778efef1e`
- operation-event schema blob: `66f9b5103e9ecc114feb9cb8fa6cebdc34082c2d`
- HEAD schema blob: `7f94e4ea2358926fb3f2bf248cd3cb7600e246cd`

## Question

Is there one reusable execution-integrity subsystem hiding in both projects?

Initial answer: **not at that breadth**.

The exact artifacts show two different state machines with a narrower common mechanical seam.

## What overlaps

### Target + precondition

Runner GitHub requests bind repository/ref/path plus expected head and, where relevant, expected blob SHA.

WIP operation events bind a target locator plus optional expected precondition.

This is a real common invariant:

> a consequential effect should identify its target and the state expected immediately before the effect.

### Post-effect uncertainty

Runner can end verification in `OUTCOME_UNKNOWN` when current subject state or completion authority cannot be established.

WIP has `AMBIGUOUS` and requires inspection before retry.

These are not byte-for-byte identical states, but they represent the same operational danger:

> an effect may have occurred even though completion cannot yet be safely claimed.

### Readback

Runner's GitHub backend performs explicit post-write ref/file readback and returns evidence.

WIP requires an `effect_receipt` for `VERIFIED` and `RECONCILED`, with optional readback text.

Both reject “tool call returned” as sufficient completion evidence.

## What does **not** belong in the shared layer

### Runner-only semantics

- work graph/frontier;
- collision grouping;
- recursive budgets;
- backend capability and target authority;
- lease ownership;
- monotonic fencing token;
- work completion state.

### WIP-only semantics

- workspace identity;
- checkpoint cadence;
- continuation/resume projection;
- append-only operation history;
- workspace lifecycle;
- explicit recovery instruction.

Trying to put all of these into one shared state machine would create a worse abstraction than the duplication it replaces.

## Narrowed experiment

The surviving hypothesis is a tiny **effect-attempt interchange envelope**.

It should carry only:

- source system + source-native operation ID/state;
- action class;
- target locator;
- expected precondition;
- normalized effect phase;
- effect/readback receipts;
- retry disposition;
- source payload digest/ref.

Proposed V0 schema: `schemas/effect_attempt_envelope_v0.schema.json`.

This schema is an experiment artifact, not a new dependency.

## Mapping hypothesis

WIP:
- `PREPARED` → `PRE_EFFECT`
- `ATTEMPTED` → `POST_EFFECT_UNVERIFIED`
- `VERIFIED` → `POST_EFFECT_VERIFIED`
- `FAILED` → `TERMINAL_FAILURE`
- `AMBIGUOUS` → `OUTCOME_UNKNOWN`
- `RECONCILED` → `RECONCILED`

Runner:
- exact request before backend execution → `PRE_EFFECT`
- backend success before independent verification → `POST_EFFECT_UNVERIFIED`
- `COMPLETE` → `POST_EFFECT_VERIFIED`
- deterministic backend/verification failure → `TERMINAL_FAILURE`
- `OUTCOME_UNKNOWN` → `OUTCOME_UNKNOWN`

Runner `VERIFYING` remains source-native detail attached to `POST_EFFECT_UNVERIFIED`; Runner `SUPERSEDED` is not an effect outcome and must remain outside the normalized phase.

## Rejection test

Kill this abstraction if either adapter must:

- hide source-native state;
- encode Runner lease/fence semantics;
- encode WIP workspace/checkpoint semantics;
- turn `SUPERSEDED` into an effect outcome;
- make the envelope authoritative for retry or completion;
- require either project to depend on Discovery at runtime.

## Current result

**PARTIAL SUPPORT / NARROWED.**

The original “shared execution-integrity subsystem” hypothesis was too broad.

A small effect-attempt interchange envelope remains plausible. No shared library is justified yet.

> **HOSTILE REVIEWER:** A common envelope can still become schema theater: two systems can serialize into the same shape without eliminating a single line of duplicated implementation. Promotion requires a real consumer workflow where the envelope removes translation or recovery code while preserving both native state machines.
