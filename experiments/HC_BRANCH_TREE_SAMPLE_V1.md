# HC branch tree sample V1

Status: **STRATIFIED CONTENT SNAPSHOT / 24 OF 24 PAIRWISE BLOB-SET MATCHES**

After the live branch-topology scan found a large shared namespace but no equal commit heads, Discovery sampled eight same-named branches spanning architecture, Four, Noah, research, review, and Vera lanes.

The sample is intentionally diverse but **not random**; branch names were selected after seeing the common namespace.

Across each sampled branch, Discovery compared:

- HC ↔ God Brain
- HC ↔ Transcendence
- God Brain ↔ Transcendence

That is **24 pairwise comparisons**.

Result: **24/24 have identical repository-relative blob paths and identical Git blob SHAs, with zero changed blobs and zero missing/extra blob paths.** The commit heads are different in every case.

Sampled branches:

- `architecture-concept`
- `four/cognitive-integrity-v1`
- `four/runtime-hyperconnectome-v1`
- `noah/integration-20260909`
- `noah/reference-kernel-authority-hardening-v1`
- `research/hyperconnectome-evidence-v1`
- `review/pr4-reconciliation-v2`
- `vera/hc-architecture-hardening-v2`

Representative sizes range from 2 blobs / 1,077 bytes on `architecture-concept` to 282 blobs / 2,019,810 identical bytes on `vera/hc-architecture-hardening-v2`.

Bounded result:

`STRATIFIED_COMMON_BRANCH_SAMPLE_HAS_IDENTICAL_BLOB_PATH_SHA_SETS_ACROSS_HC_GODBRAIN_TRANSCENDENCE_DESPITE_DISTINCT_COMMIT_HEADS`

## What this supports

The three repositories preserve repository-local commit identity while carrying exact content snapshots across a broad sample of inherited branch names. That is materially stronger than branch-name overlap alone.

## What it does not support

- no original-copy direction;
- no claim that all 35 common branches are identical;
- no claim of identical commit parents/history;
- no merge/dependency direction;
- no conclusion that duplicate repositories are undesirable.

> **HOSTILE REVIEWER:** You selected branches after seeing the topology. A perfect stratified sample can still miss the branches where divergence actually happened.

Correct. The next decisive test is exhaustive blob-set comparison across all 35 three-way common branch names, or a predeclared random/complete census. This sample is evidence against “unrelated content,” not a prevalence estimate.
