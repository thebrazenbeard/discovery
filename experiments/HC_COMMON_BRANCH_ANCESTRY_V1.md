# HC common-branch ancestry V1

Status: **EXHAUSTIVE OVER ALL 34 NON-MAIN THREE-WAY COMMON LIVE BRANCHES**

The prior exhaustive content scan established that all 34 non-`main` branch names common to `hc-brain`, `transcendence`, and `god-brain` have identical blob path/SHA snapshots.

This pass inspected the Git commit objects behind all 34 branch heads.

## Result

Every branch shows the same pattern — **34/34**:

- the three repositories point to the **same Git tree SHA**;
- HC's branch head is an **earlier, parented commit**;
- Transcendence's counterpart is a **later, parentless root commit** with message `Initialize <branch>`;
- God Brain's counterpart is a **still later, parentless root commit** with the same initialization-message pattern.

No exception was found.

Bounded result:

`ALL_34_NON_MAIN_COMMON_BRANCHES_SHOW_EARLIER_PARENTED_HC_COMMIT_AND_LATER_PARENTLESS_IDENTICAL_TREE_INITIALIZATIONS_IN_TRANSCENDENCE_AND_GOD_BRAIN`

## What this establishes

This is strong historical source-side evidence for HC across those copied branch snapshots. The Transcendence and God Brain branch histories were not preserved as the same commit DAG; identical HC tree snapshots were re-rooted into repository-local commits later.

## What remains unresolved

Chronology alone does **not** prove God Brain copied from Transcendence rather than directly from HC or from another reconstruction source. It also does not make HC authoritative over later project semantics, nor does it decide consolidation direction.

`main` is excluded because it is the active divergence surface found by the exhaustive content scan.

> **HOSTILE REVIEWER:** The pattern proves source-side chronology for the observed snapshots, but a migration/export process could have sourced the trees from an intermediate artifact rather than directly from the HC repository.

Correct. The claim is deliberately limited to historical source-side evidence: HC contains the same trees earlier in parented history; the later repositories initialize those trees as new roots. Direct transfer path remains unresolved.
