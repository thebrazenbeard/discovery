# Portfolio census drift transition V1

Status: **PARTIAL FALSIFIER / STALE REJECTION PASS / REFRESH UNRESOLVED**

The original `PORTFOLIO_CENSUS_DRIFT_INPUT_V1` named a specific next falsifier:

> On the next repository-set change, both consumers should reject the stale digest and refresh to the same new Discovery census without changing their project-owned registry semantics.

That change has now happened.

## Provider movement

Historical Discovery census:

- exact source: `vera/discovery-shared-substrate-v1@1316094edbed17fa5918b70793c95ffddfcf92ea`
- census blob: `34cd2ab55d46f5a1ecc2c894f3e8cfdb8afa41df`
- 57 total / 12 public / 45 private
- all-name digest: `43dfda1f...`

Current Discovery census:

- exact source: `vera/discovery-live-census-public-intake-v1-20260921@56822c92c4cb3709bf742032f539206a0e398024`
- census blob: `1b46d74176f8d67f3c1bd53bfcf2f369b89e9d8d`
- 58 total / 23 public / 35 private
- public-name digest: `25fe6601...`
- all-name digest: `c854d889...`

The current public source recomputes the public-name digest. The private/all-name digests remain externally supplied commitments rather than source-recomputed values.

## Public consumer — stale rejection passes

Project Runner PR #23 is still exactly bound to the 57-repository blob:

`b763c707abacc7dfe30dc451b2b42354a30e3621`

Its verifier computes the Git blob SHA-1 of supplied census bytes and rejects any input that does not match its exact bound blob. Therefore the current 58-repository Discovery census cannot pass the old binding.

Project Runner's later canonical-baseline candidate independently reaches the same currentness conclusion:

`PR #29 @ 48c2074ce4f679c724036e14c5b6910e145c2492`

Its reconciliation machine record classifies PR #23 as:

`BLOCKED_STALE_EXTERNAL_CURRENTNESS`

and explicitly excludes the stale Discovery census experiment from the minimal current baseline.

That is real stale-input rejection.

## Public consumer — refresh does not pass

Project Runner did **not** rebind to Discovery's current 58-repository artifact.

Its own 2026-09-20 estate cut reports 58 total repositories but a 14-public / 44-private split. Discovery's later 2026-09-21 census reports 23 public / 35 private.

So:

`SAME_TOTAL_COUNT != SAME_CENSUS_CURRENTNESS`

No inspected Project Runner subject binds current Discovery blob `1b46d741...` or current all-name digest `c854d889...`.

The public half of the falsifier is therefore:

`STALE_REJECTION = PASS`

`REFRESH_TO_CURRENT_DISCOVERY_CENSUS = NOT_DEMONSTRATED`

## Opaque consumer

The existing public-safe private attestation remains exactly what V1 says it is: a commitment, not independently verifiable behavior.

No new public-safe refresh attestation was observed in the current Discovery candidate.

The public repository therefore cannot establish whether the opaque consumer:

- rejected the old 57-repository digest;
- refreshed to the 58-repository artifact;
- retained the same project-owned semantics.

Those states remain `NOT_PUBLICLY_VERIFIABLE`.

## Result

`PARTIAL_FALSIFIER_STALE_REJECTION_PASS_REFRESH_UNRESOLVED`

The candidate remains **EXPERIMENTING**.

This is meaningful progress: the mechanism did not silently accept stale bytes in the public consumer. But its stronger portability claim still fails closed because synchronized refresh across both consumers has not been demonstrated.

> **HOSTILE REVIEWER:** Detecting that your dependency is stale is not the same thing as making refresh cheap, reliable, or shared.

Correct. The next useful evidence is an actual current binding to the new Discovery artifact by an independent consumer, with no authority or runtime-registry promotion.
