# HC-Brain → Transcendence Exact Base + Overlay Experiment V1

Status: **EXPERIMENTING / EXACT TREE RECONSTRUCTION TEST**

## Question

Can Transcendence's current source frontier be represented exactly as one pinned
HC-Brain source tree plus a relatively small, explicit Transcendence overlay
without making HC-Brain authoritative over Transcendence semantics?

## Exact subjects

HC-Brain current implementation frontier:

- PR #22
- commit `5929da3e8904e23e484df0deac920a008ec33d52`
- tree `e4c7fcedaa77cf5d2794491a99326db67740a272`

Transcendence current repair frontier:

- PR #7
- commit `be3785c83dbe89b0d4236b43eda97a277eb6baad`
- tree `112a44d8042556b87f19b3dac05ec34a5ea2f796`

## Current byte overlap

The target Transcendence tree contains 288 files and 1,992,586 blob bytes.

Of those:

- 254 files are byte-identical to the HC source at the same path;
- those shared blobs account for 1,706,224 target bytes;
- **85.628625314% of current Transcendence bytes are identical to HC**.

The exact overlay needs:

- 9 same-path overwrites;
- 25 Transcendence-only additions;
- 39 HC paths explicitly deleted;
- 34 payload files total;
- 286,362 payload bytes;
- **14.371374686% of Transcendence target bytes**.

For comparison, stable main↔main was even more duplicated: 255 of 263
Transcendence files were identical, representing 95.352510121% of target bytes.

## Why deletions are first-class

This experiment does **not** model Transcendence as "HC latest + a few new files."

The current HC frontier contains 39 files Transcendence does not contain,
including newer executable cognitive-core, motor-control, architecture-hardening,
and qualification surfaces.

Examples intentionally excluded by the overlay include:

- `runtime/cognitive_core/cognitive_loop.py`
- `runtime/cognitive_core/motor_control.py`
- `runtime/reference_kernel/governed_kernel_v2.py`
- `tools/validate_hc_architecture.py`

Therefore any reusable base must be pinned to an exact tree and must apply an
explicit deletion manifest. Moving-base inheritance is not admissible.

## Exact reconstruction proof

The experiment stores complete path/mode/blob snapshots for both exact subjects.

`tools/validate_hc_transcendence_overlay.py`:

1. reconstructs both stored Git trees from path, file mode, and blob SHA;
2. requires those reconstructed tree hashes to equal the exact GitHub tree SHAs;
3. starts from the exact HC base;
4. verifies every deletion and overwrite preimage;
5. applies all deletes, overwrites, and additions;
6. requires the resulting file map to equal the exact target map;
7. recursively rebuilds the Git tree object and requires the final SHA to equal
   Transcendence tree `112a44d8042556b87f19b3dac05ec34a5ea2f796`.

A PASS is an exact source reconstruction claim, not an approximate similarity
claim.

## Preserved ownership

Transcendence-specific BCI, capture, continuity, human-state archive, privacy,
qualification, threat-model, and phenomenal-continuity semantics remain
Transcendence-owned.

The HC subject supplies pinned source bytes only. It does not gain authority over
Transcendence requirements, roadmap, claims, BCI operation, human-subject
effects, continuity conclusions, or future divergence.

Historical provenance remains unchanged.

## Claim ceiling

A successful reconstruction can establish:

`EXACT_PINNED_BASE_PLUS_OVERLAY_RECONSTRUCTION`

and measured current duplication.

It cannot establish:

- dependency adoption;
- repository rewrite or file deletion;
- merge authority;
- moving-base compatibility;
- future upgrade economics;
- HC authority over Transcendence;
- human capture, BCI operation, migration, reconstruction, or continuity proof;
- `PROVEN_REUSABLE`.

## Next falsifier after reconstruction

If exact reconstruction passes, the next useful test is a **base-upgrade
simulation**:

take a later exact HC tree and determine whether the Transcendence overlay can be
rebased without importing excluded HC semantics or requiring large conflict
repair.

That upgrade cost—not current duplication alone—decides whether a real base
dependency would reduce maintenance.
