# Public Blob Evidence Reproducibility V1

Status: **READ-ONLY LIVE REPRODUCIBILITY GATE + FROZEN HISTORICAL V1**

Parent exact subject:

`vera/discovery-public-impact-radar-v1-20260922@a56c99c666ed0b9cff7b95a34acbe7ccfe2f5f74`

## Problem

Discovery could validate the public blob-index shards and overlap scan, but there was no producer capable of reconstructing those artifacts from GitHub.

That meant exact byte-overlap evidence still depended on manually manufactured JSON.

## Reproducer

`tools/refresh_public_blob_evidence.py`:

1. reads the live public owner inventory;
2. binds each current public repository to its default branch, exact commit, exact Git tree and archive state;
3. reads the exact recursive Git tree for each bound tree object;
4. rejects truncated tree responses;
5. normalizes every blob as path / Git blob SHA / size;
6. reconstructs the existing two public blob-index shards;
7. recomputes every one of the 253 pairwise overlap records;
8. recomputes the public overlap summary;
9. recomputes the Git blob IDs that bind the overlap scan to its source shards.

`--check` requires the reconstructed canonical artifacts to match the committed files byte-for-byte.

`--write --observed-date YYYY-MM-DD` is a historical compatibility switch: it now verifies byte identity and exits without writing when unchanged, or refuses if any frozen V1 byte differs. `--write --accept-set-change` is refused before live collection. Neither replaces V1.

`--proposal --observed-date YYYY-MM-DD --proposal-path /absolute/new/candidate.json` creates an **unreviewed, non-admitted** V2 public-cut candidate at a previously nonexistent local path outside the historical `experiments/` tree. It uses actual GitHub public inventory identities, including Discovery's current self HEAD/tree rather than V1's self-exempt frozen substitute. This identity-only observation does **not** verify snapshot stability, blob equivalence, public-membership transition reasons, or runtime effects. Absent-from-public-inventory is not evidence of deletion. Creation is exclusive and will not overwrite existing files; path checks are not claimed to be race-proof against concurrent directory/symlink mutation.

## Repository-set changes fail closed

The reproducer deliberately refuses to add or remove repositories from the shards.

A changed public repository set requires census/intake classification first. Blob refresh must not silently decide that a newly visible repository belongs in Discovery's current architecture surface.

## Hosted gate

When the public currentness watcher reports the current public subjects unchanged, GitHub Actions also executes:

```bash
python tools/refresh_public_blob_evidence.py --check
```

Therefore a green hosted result now means two separate things:

1. the exact public repository subjects still match the bound public baseline; and
2. the committed public blob evidence is reproducible from those live Git objects.

## Hostile review

> **HOSTILE REVIEWER:** A validator that recomputes metrics from committed blob lists still proves nothing about whether those blob lists came from GitHub.

Correct. This reproducer acquires the exact recursive Git tree from GitHub and rebuilds the blob lists before comparing canonical bytes.

> **HOSTILE REVIEWER:** GitHub's recursive tree API can truncate large trees and hand you incomplete evidence.

Correct. Any `truncated: true` response is a hard failure. Discovery must use a different complete acquisition strategy before claiming evidence for that repository.

> **HOSTILE REVIEWER:** A generator can quietly absorb a newly public repository and change the architecture story without review.

Rejected by design. Repository-set drift is a hard stop. Census/intake classification owns that transition.

> **HOSTILE REVIEWER:** “Byte-for-byte” can fail because of irrelevant JSON formatting even when the evidence is equivalent.

Correct, and that is intentional for `--check`. The canonical artifact includes its serialization and source-shard blob identities. Equivalent-but-different bytes are a changed artifact and require explicit review.

> **HOSTILE REVIEWER:** Your `--write` mode is dangerous if somebody treats generation as approval.

The historical V1 `--write` path is now verification/no-op or refusal, and the changed-set override cannot write. A separately created V2 proposal is explicitly unreviewed, with no candidate promotion, architecture decision, merge authority, or semantic equivalence.

> **HOSTILE REVIEWER:** A green blob reproducer still tells you only exact byte identity. It will miss renamed, refactored, or independently implemented equivalent mechanisms.

Correct. This is D0 exact-mechanical evidence only. AST, interface, behavioral and semantic detectors remain separate weaker evidence classes with lower claim ceilings.

## Claim ceiling

`LIVE_GITHUB_PUBLIC_BLOB_EVIDENCE_REPRODUCIBILITY / D0_EXACT_MECHANICAL_ONLY / PUBLIC_SET_CHANGES_FAIL_CLOSED / NO_AUTOMATIC_WRITE / NO_SEMANTIC_EQUIVALENCE / NO_PROJECT_AUTHORITY`
