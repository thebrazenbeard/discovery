# Public Tree Binding Repair V1

Status: **LIVE-SOURCE REPAIR / EXACT PUBLIC HEADS UNCHANGED / TREE BINDINGS CORRECTED**

Parent exact subject:

`vera/discovery-snapshot-currentness-pipeline-v1-20260922@feca4acfb1b459644f4edb00da39d536c6f59b8d`

## What the real snapshot exercise found

The 2026-09-22 live GitHub inventory still reports:

- 58 repositories total;
- 23 public;
- 35 private;
- the same 23 public repository names as Discovery's 2026-09-21 live-intake cut.

All 23 public default-head commit SHAs also still match the heads recorded in the prior public blob-index shards.

That initially looks like a clean currentness result.

It is not.

The prior shards stored a field named `tree_sha` for every public repository, but every stored `tree_sha` was equal to that repository's commit `head`.

Fresh GitHub branch/commit reads show the actual Git tree object IDs are different.

So the prior artifact had a semantic binding defect:

`FIELD_SHAPE_VALID / FIELD_MEANING_FALSE`

The validator required 40 lowercase hex characters, but never proved that the value represented a Git tree rather than a copied commit SHA.

## Scope of damage

The public blob-overlap calculations are driven by the explicit blob path/SHA lists, not by `tree_sha`.

Therefore this finding does **not** by itself invalidate the published pairwise blob-overlap counts.

It does invalidate any claim that the old `tree_sha` field was exact tree evidence.

## Repair

This branch:

- replaces all 23 bad `tree_sha` values with the actual current Git tree OIDs observed from the unchanged exact public heads;
- adds a validator guard rejecting `tree_sha == head`;
- adds a hostile regression that recreates the old false-green and requires rejection;
- records the live source bindings in `experiments/PUBLIC_TREE_BINDING_REPAIR_V1.json`.

The current public heads did not move between the prior scan and this repair, so the corrected tree bindings apply to the same exact commit subjects.

## Hostile review

> **HOSTILE REVIEWER:** Rejecting `tree_sha == head` does not prove the replacement tree SHA is correct. It only catches this exact failure shape.

Correct. The guard is a regression barrier, not a complete source-verification proof. Exact tree acquisition still depends on the read-only GitHub branch/commit observation. Future snapshot receipts should record acquisition provenance explicitly.

> **HOSTILE REVIEWER:** If the overlap math never used `tree_sha`, this is cosmetic.

Rejected. A field named `tree_sha` is an evidence claim. Downstream provenance, snapshot comparison, or ancestry logic could reasonably consume it. A semantically false exact-identity field is a high-value defect even if one current calculation happened not to use it.

> **HOSTILE REVIEWER:** You are repairing historical artifacts with a later observation. How do you know the trees were the same on September 21?

Because all 23 exact commit heads are unchanged from the prior artifact. A Git commit object binds its tree object. The live Git tree read therefore resolves the tree of the exact same commit object that the prior scan recorded. This is source repair, not transfer from a different commit.

> **HOSTILE REVIEWER:** The new snapshot builder could still suffer another shape-valid/meaning-false bug elsewhere.

Accepted. This incident generalizes into a Discovery rule: identifiers must be validated against their source relation, not merely their syntax. A later detector-contract phase should distinguish `SHAPE_VALIDATED` from `SOURCE_RELATION_VALIDATED` evidence.

> **HOSTILE REVIEWER:** You found this manually, not because the new snapshot comparator caught it. That weakens the claim that the snapshot pipeline is already earning its maintenance cost.

Correct. The first real exercise exposed a defect in the surrounding evidence model, but it does not yet prove the pipeline reduces ongoing maintenance. The economics gate remains open.

## Project OS lesson candidate

This incident is a good candidate for a reusable engineering lesson:

`TYPE_SHAPED_IDENTIFIER != SOURCE_BOUND_IDENTITY`

A Git-looking SHA only proves syntax. If a field claims commit/tree/blob identity, verification should bind it to the corresponding Git object relationship.

That lesson should only be promoted to reusable Project OS knowledge after the Project OS control plane is deliberately bootstrapped and the finding is reviewed under its own lifecycle. This branch does not bootstrap Project OS implicitly.

## Claim ceiling

`23_PUBLIC_HEADS_UNCHANGED / TREE_BINDING_SEMANTIC_DEFECT_REPAIRED / BLOB_OVERLAP_COUNTS_NOT_REQUALIFIED_BY_THIS_FINDING / SNAPSHOT_PIPELINE_ECONOMICS_STILL_UNPROVEN / NO_RUNTIME_OR_PROJECT_AUTHORITY`
