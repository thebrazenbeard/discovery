# VeraMesh ↔ Vera Synology handoff experiment V1

Status: **FAIL_CURRENT_NATIVE_CROSS_REPO_BINDING_MISSING**

This experiment executes the next falsifier in `VERAMESH_SYNOLOGY_HANDOFF_V1`:

> Can the smallest neutral handoff bind exact VeraMesh producer source identity to the intended Vera Synology package payload while Synology validates the handoff without importing VeraPort transport authority?

## Exact subjects

VeraMesh:
`PR #12 @ 9bffc57930587bf74a12657bbeaa913474ab5574`

Vera Synology:
`PR #3 @ 553e3a637833c5469f6b99fbc4d597755a0c9a5e`

Both PR heads remain unchanged at the 2026-09-22 experiment cut.

## What Synology already proves

The current Synology package line is strong about **local** source/artifact identity.

`SOURCE_MANIFEST.json` binds packaged paths to:

- byte count;
- path;
- SHA-256;
- source mode;
- regular-file type.

`verify_spk.py` checks package members against that manifest for byte identity, mode identity, path-set identity, deterministic archive structure, and a closed package metadata profile.

For `payload/bin/veramesh_edge.py`, the committed manifest records:

- 12,303 bytes;
- mode `0755`;
- SHA-256 `1374d263213fceb125a4052b4e306e5200d61621087b313ef119182dd8df8dca`;
- Git blob `3d61fdd322a3f225e8c609a2a622b757d8315403` at the bound Synology head.

## What the native package identity path does not prove

The inspected package identity/verification sources do **not** bind:

- `thebrazenbeard/vera-mesh`;
- VeraMesh exact producer head `9bffc579...`;
- VeraMesh route/current-session state;
- any VeraMesh live effect.

That is good for authority separation, but it means the current Synology verifier cannot establish the proposed end-to-end provenance statement:

`exact VeraMesh source contract -> this exact Synology package payload`.

Discovery can write an external record containing both refs. That would prove only that Discovery observed and paired them; it would not make the Synology package natively attest the producer relationship.

## Result

`FAIL_CURRENT_NATIVE_CROSS_REPO_BINDING_MISSING`

This does **not** reject VeraMesh or Vera Synology. It rejects the stronger claim that the proposed cross-repo handoff is already natively verifiable.

> **HOSTILE REVIEWER:** Why not just add the VeraMesh commit to Discovery's record and call the handoff complete?

Because that would turn Discovery into a shadow release/provenance authority. A package consumer could not independently recover or validate the producer binding from its own governed source/package contract.

## Candidate consequence

`VERAMESH_SYNOLOGY_HANDOFF_V1` remains **HYPOTHESIS**, narrowed to a missing-contract question.

A future experiment would need a source-controlled, non-authoritative producer-provenance field or receipt consumed by the package validation path while still preserving all of these distinctions:

`source != build != install != route != read/write/process effect`.

Discovery does not have authority from this experiment to add that field to either source repository, install a package, or change runtime/provider state.
