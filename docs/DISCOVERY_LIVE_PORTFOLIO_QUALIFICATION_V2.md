# Live portfolio qualification V2

This is a hostile qualification, not a claim that every repository is runtime-consumed.

Passes: all 59 accessible repositories are classified exactly once; Native Project control ownership is limited to Vera Control Plane / Vera / Chat Communication Bus; both Supabase projects are healthy and mapped; current Vera routing comes from live Bus topology; Build Team 2.0 and bt2 are distinct; Vera R9A0 remains predecessor evidence; empty stubs are not promoted.

Blockers: private hosted Actions still fail before runner assignment on Vera/VCP; live github-bus-ingest matches Bus PR #325 rather than Bus main; WorkBridgeMCP's usable implementation is not yet main/installed; self/hc-brain/bt2 canonical template claims remain unresolved.

Gaps: Redworm historical authoring is unresolved; the complete fresh-chat -> source -> Bus -> provider -> recovery path is not yet end-to-end qualified.

## Non-HC byte-overlap hostile review

The refreshed exact-byte scan found two non-HC overlaps. WorkBridgeMCP and VeraMesh share 10 blobs covering about 94% of the smaller repository's bytes, but every shared blob is a generic GitHub Actions workflow template under `.github/workflows/`. DriftGuard and VeraMesh share one additional generic Conda workflow template. Under Roots provenance rules this is reuse/boilerplate evidence, not origin, derivation, succession, or canonicality evidence. The scan remains marked `PATTERN_CHANGED_REVIEW_REQUIRED`; the review result is `NO_NEW_LINEAGE_ESTABLISHED`.
