# Discovery Canonicalization Candidate V1

Status: **DRAFT / NO MERGE AUTHORITY**

Current `main` is only the repository's initial commit. The active project is a reviewed stack.

Proposed future canonical subject is the exact current PR #17 lineage:

`#1 -> #8 -> #9 -> #10 -> #11 -> #12 -> #13 -> #14 -> #15 -> #16 -> #17`

The branch containing this file starts from PR #17 exact head `250644f34bc7f0e16dc078487905ecfb8e537f02`.

PRs #2, #3, and #7 are historical lifecycle branches superseded by PR #8's current-base composition.

PR #18 diverged from an older PR #17 head `28810a2e63edb40af25f977fb0595c6a88458a75`. Current PR #17 already integrates the real failure-path evidence; PR #18's result artifact remains stale and still lists `REAL_FAILURE_PATH_INTEROP` as not established. Preserve #18 as failed/divergent provenance rather than treating it as a merge dependency.

Exact hosted evidence on PR #17 head:
- Discovery validation run 35520628840: SUCCESS.
- Discovery composed lifecycle validation run 35520628866: SUCCESS.

The machine-readable graph and proposed dispositions are in `architecture/REPOSITORY_RECONCILIATION_V1.json`.

No PR is closed or merged by this artifact. Privacy issue #6 remains active. Fresh exact-head review is required if this branch moves.
