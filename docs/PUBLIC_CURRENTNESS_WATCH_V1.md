# Public Currentness Watch V1

Status: **READ-ONLY AUTOMATED PUBLIC CURRENTNESS CHECK**

Parent exact subject:

`vera/discovery-tree-binding-repair-v1-20260922@d0e6db24055b0f4b210b3df192b19c495c875852`

## What this closes

Discovery previously had exact public repository evidence but no self-running mechanism that checked whether those subjects were still current.

`tools/check_public_currentness.py` now compares the live public GitHub portfolio with the exact public subjects already owned by:

- `portfolio/PORTFOLIO_CENSUS_V1.json` for public repository membership; and
- `experiments/public_blob_index_v1/SHARD_*.json` for default branch, commit, tree and archive state.

It does not create a second baseline registry.

## Automation

`.github/workflows/discovery-public-currentness.yml` runs:

- on relevant pull requests;
- manually through workflow dispatch; and
- every six hours after the workflow reaches the default branch.

The job is read-only. It uses the GitHub-provided token with `contents: read` and performs no repository writes.

A current result exits zero.

Public repository addition/removal or default-branch/head/tree/archive movement exits nonzero and prints an exact machine-readable drift report.

The workflow does **not** automatically refresh Discovery evidence. A red currentness watch is intentionally a review trigger, not permission to rewrite the baseline.

When stale public subjects are detected, `tools/trace_public_impact.py` searches Discovery's bounded evidence surface for exact references to the stale commit SHA. The workflow prints a second machine-readable impact report listing the affected files and line numbers.

This is exact-reference tracing, not semantic dependency inference. A missing exact SHA reference is reported as an evidence gap and never treated as proof that no dependency exists.

## Private boundary

This watch does not inspect private repositories.

Its output always carries:

`private_currentness = NOT_OBSERVED`

Private currentness remains a separate governed problem. Public automation is not allowed to imply whole-portfolio currentness.

## Hostile review

> **HOSTILE REVIEWER:** A green scheduled check can become security theater if it compares live GitHub against another hand-maintained duplicate baseline.

The watch uses the public blob-index shards that already own the exact subjects for byte-overlap research. No second head/tree registry is introduced.

> **HOSTILE REVIEWER:** If the workflow automatically updates stale refs, it can erase the very drift it is meant to expose.

It does not write. Drift fails closed. Refresh remains an explicit reviewed source change.

> **HOSTILE REVIEWER:** GitHub Actions may not actually be able to inspect the other public repositories with the built-in token.

Correct. Local/unit behavior is insufficient evidence. The pull-request workflow must execute successfully against live GitHub before this capability is considered operational.

> **HOSTILE REVIEWER:** Watching every six hours is pointless if nobody responds to red status.

Correct. This feature proves detection only. It does not prove response latency, ownership, or automatic reconciliation. Those remain separate operational questions.

> **HOSTILE REVIEWER:** Public currentness is not portfolio currentness while 35 repositories remain private.

Correct. The claim ceiling says exactly that. No public result may be promoted into a whole-portfolio currentness claim.

> **HOSTILE REVIEWER:** A repository can remain at the same Git head while an external dependency, release, deployment or runtime has changed.

Correct. This watch proves only repository-source currentness for the bound public subjects. Runtime/effect/qualification currentness remains project-owned evidence.

## Claim ceiling

`AUTOMATED_PUBLIC_SOURCE_CURRENTNESS_ONLY / EXACT_REPOSITORY_SET_DEFAULT_BRANCH_HEAD_TREE_ARCHIVE / PRIVATE_NOT_OBSERVED / NO_AUTOMATIC_REFRESH / NO_RUNTIME_OR_PROJECT_AUTHORITY`
