# Discovery Canonicalization Candidate V1

Status: **DRAFT / NO MERGE AUTHORITY**

Current `main` is only the repository's initial commit. The active project is a reviewed source stack plus this reconciliation wrapper.

The inherited source lineage terminates at PR #17:

`#1 -> #8 -> #9 -> #10 -> #11 -> #12 -> #13 -> #14 -> #15 -> #16 -> #17`

PR #17 is the **source-lineage terminal**, not the current canonicalization wrapper.

PR #19 is the current canonicalization wrapper candidate against `main`. Because a committed file cannot truthfully contain the SHA of the commit that contains that file, the exact current PR #19 head must be established from live Git / external review evidence. The machine manifest therefore uses `EXTERNAL_GIT_READ_REQUIRED` instead of self-asserting a current head.

The branch containing this file was created from PR #17 exact head `250644f34bc7f0e16dc078487905ecfb8e537f02`.

PRs #2, #3, and #7 are historical lifecycle branches superseded by PR #8's current-base composition.

PR #18 diverged from an older PR #17 head `28810a2e63edb40af25f977fb0595c6a88458a75`. Current PR #17 integrates the real failure-path evidence; PR #18 remains preserved failed/divergent provenance rather than a merge dependency.

Historical hosted evidence on the inherited PR #17 source head:
- Discovery validation run 35520628840: SUCCESS.
- Discovery composed lifecycle validation run 35520628866: SUCCESS.

Fresh qualification of the **current PR #19 exact head** is external evidence and must not be silently transferred from those historical runs.

The machine-readable source-lineage / wrapper distinction and proposed dispositions are in `architecture/REPOSITORY_RECONCILIATION_V1.json`, which is validated by the repository reconciliation validator.

No PR is closed or merged by this artifact. Privacy issue #6 remains active. Fresh exact-head review is required whenever PR #19 moves.
