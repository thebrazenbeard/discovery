# Cognitive public-overlap refresh V1

Status: **OBSERVED / SOURCE-MEASURED / NO DEPENDENCY ADOPTION**

The 2026-09-21 public-surface refresh exposed two HC-family subjects that were not named in the prior public Discovery census: `god-brain` and `bt2`.

## Method

Discovery compared recursive Git trees by exact repository path and Git blob SHA. Same-path equal blob SHA means the bytes are identical. Byte-share calculations use `hc-brain` blob bytes as the denominator.

Exact subjects:

- `hc-brain/main@618245b54fb923c7a204892c6953ab6d1c5dac57`
- `god-brain/main@c0f6af7143aa5916bae96eb1f0ee9c9de6505cf5`
- `bt2/main@30e81cadd94fae117a7f6875523c03251c7c9f6e`

## God Brain ↔ HC

The trees each contain 300 blobs at the measured heads.

- common paths: **300**
- identical same-path blobs: **299**
- changed same-path blobs: **1**
- changed path: `README.md`
- God-Brain-only blobs: **0**
- HC-only blobs: **0**
- identical bytes: **2,181,434 / 2,191,461 HC bytes**
- identical share of HC bytes: **99.54245136%**

The bounded result is:

`NEAR_EXACT_HC_SNAPSHOT_WITH_PROJECT_SPECIFIC_README_AT_MEASURED_HEADS`

This is strong duplication evidence, not proof that God Brain should inherit a moving HC branch or surrender independent semantics.

## bt2 ↔ HC

At the measured heads:

- bt2 blobs: **517**
- HC blobs: **300**
- common paths: **188**
- identical same-path blobs: **178**
- changed same-path blobs: **10**
- bt2-only blobs: **329**
- HC-only blobs: **112**
- identical bytes: **1,011,147 / 2,191,461 HC bytes**
- identical share of HC bytes: **46.14031461%**

The bounded result is:

`SUBSTANTIAL_SHARED_HC_SUBSTRATE_WITH_MATERIAL_DIVERGENCE`

The current static measurement is not enough to call bt2 a safe HC overlay, successor, or dependency. It needs provenance and forward-maintenance testing.

## Hostile interpretation

> **HOSTILE REVIEWER:** High byte overlap can be exactly what intentional experimental isolation looks like immediately after a fork. Static duplication alone does not establish that deduplication reduces total maintenance. God Brain may need a clean fork precisely because its experiment is supposed to diverge. bt2's archive/training and qualification surfaces may make a shared base actively harmful even when many files are byte-identical.

Accepted. The next useful tests are exact reconstruction and forward-change maintenance economics, not immediate consolidation.

## Claim ceiling

This artifact establishes only byte-level overlap at the exact measured heads.

It does **not** establish dependency adoption, canonical-successor direction, merge authority, semantic ownership, runtime coupling, or `PROVEN_REUSABLE`.
