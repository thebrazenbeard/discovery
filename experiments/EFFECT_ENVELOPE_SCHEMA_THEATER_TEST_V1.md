# Effect Envelope Schema-Theater Test V1

Status: **EXPERIMENTING / SOURCE-AGNOSTIC OBSERVER**

## Question

Does the neutral effect envelope eliminate source-specific parsing in at least one
real downstream workflow, or does it merely make three systems serialize into
the same decorative shape?

## Observer contract

`tools/effect_observer.py` consumes **one producer-selected latest envelope per
source-native operation**.

That boundary is deliberate. Native systems remain responsible for:

- native event ordering;
- choosing the current/latest native event or outcome;
- target and effect authority;
- retries;
- completion;
- reconciliation;
- behavioral recovery;
- scheduling and lifecycle semantics.

The observer receives only the already-normalized V0 envelope.

It derives its accepted fields, normalized phase vocabulary, retry vocabulary,
target shape, and receipt shape from
`schemas/effect_attempt_envelope_v0.schema.json`.

It then produces only an observational report:

- counts by normalized phase;
- counts by retry disposition;
- operations explicitly marked `INSPECT_BEFORE_RETRY`;
- unresolved neutral phases;
- verified neutral phases;
- reconciled neutral phases.

## No source-specific parsing test

The implementation contains no names or code paths for the current three
producers.

Tests prove that the same function accepts:

- a Project Runner-shaped producer identity;
- a WIP-shaped producer identity;
- a DriftGuard-shaped producer identity;
- an unknown future source requiring no observer registration or code change.

`source_state` is treated as opaque provenance. The observer does not parse it.

## What this can establish

If exact producer PRs pass and this observer passes, Discovery can claim:

`DOWNSTREAM_SOURCE_SPECIFIC_PARSING_ELIMINATED_FOR_ONE_OBSERVER`.

That is stronger than shape compatibility.

## What it cannot establish

It still does not establish net portfolio maintenance savings.

The three producers each carry a small adapter, so a later measurement must
compare:

- producer adapter code/maintenance introduced;
- source-specific consumer parsing removed;
- number of future consumers that can reuse the neutral observer path;
- schema evolution burden;
- failure/recovery operational cost.

Until that measurement exists, `PROVEN_REUSABLE` remains unjustified.

## Falsifiers

Reject or narrow the envelope if:

- the observer must branch on `source_system`;
- the observer must interpret native `source_state`;
- a fourth source requires observer code changes despite emitting valid V0;
- native latest-event selection cannot remain producer-owned;
- shared validation or adapters cost more than the source-specific parsing they replace.
