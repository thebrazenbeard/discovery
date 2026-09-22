# HC common-branch exhaustive scan V1

Status: **EXHAUSTIVE OVER CURRENT THREE-WAY COMMON LIVE BRANCH NAMES**

Discovery exhaustively compared blob path/SHA sets for every live branch name currently shared by:

- `hc-brain`
- `god-brain`
- `transcendence`

There are **35** such branch names. For each branch, all three repository pairs were compared, giving **105 pairwise comparisons**.

## Result

- exact blob path/SHA set matches: **102 / 105**
- divergent comparisons: **3 / 105**
- non-`main` common branches: **34**
- non-`main` pairwise comparisons: **102**
- exact non-`main` matches: **102 / 102**

So every one of the **34 non-main common branch names** carries an identical blob path/SHA snapshot across all three repositories at the observed live heads.

The only divergent branch is `main`, producing the expected three pairwise failures:

1. HC ↔ God Brain: 300 common paths, 299 identical blobs, one changed path — `README.md`.
2. HC ↔ Transcendence: 263 common paths, 255 identical, 8 changed, plus 37 HC-only paths.
3. God Brain ↔ Transcendence: the same 263/255/8 shape with 37 God-Brain-only paths.

Bounded result:

`ALL_34_NON_MAIN_THREE_WAY_COMMON_BRANCHES_HAVE_IDENTICAL_BLOB_PATH_SHA_SETS_MAIN_IS_ONLY_LIVE_COMMON_BRANCH_CONTENT_DIVERGENCE`

## Interpretation

This is substantially stronger than the earlier branch-name signal.

The three repositories have distinct commit heads for those branches, but the file/blob snapshots behind every non-main common branch are identical. That is consistent with repository-local commit/history identity around copied or reconstructed content snapshots.

It still does **not** prove which repository was original, the direction or timing of copying, identical commit ancestry, or that the repositories should be consolidated.

bt2 remains a different pattern: it shares substantial HC bytes on `main` but does not preserve the inherited branch namespace.

> **HOSTILE REVIEWER:** Blob equality does not show identical commit DAGs. A migration tool could recreate identical snapshots with unrelated parentage.

Correct. The next ancestry test must inspect commit parents/history for selected or all common branches. This result establishes content-snapshot identity, not Git-history identity.
