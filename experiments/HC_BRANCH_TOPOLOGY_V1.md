# HC branch-topology scan V1

Status: **LIVE REF SNAPSHOT / PROVENANCE SIGNAL / NO LINEAGE DIRECTION**

Discovery compared every live `refs/heads/*` name and exact head SHA across the four public HC-family repositories.

## Results

- `hc-brain`: **43** live branches
- `god-brain`: **88**
- `transcendence`: **42**
- `bt2`: **52**

Pairwise same-name branch overlap:

- HC ↔ God Brain: **42** common branch names; **0** equal commit heads.
- HC ↔ Transcendence: **35** common branch names; **0** equal commit heads.
- God Brain ↔ Transcendence: **35** common branch names; **0** equal commit heads.
- bt2 ↔ HC: **1** common name (`main`); **0** equal heads.
- bt2 ↔ God Brain: **1** common name (`main`); **0** equal heads.
- bt2 ↔ Transcendence: **1** common name (`main`); **0** equal heads.

HC, God Brain, and Transcendence share a **35-branch common namespace**. None of those same-named branches has one identical commit head across all three.

## Interpretation

This strengthens the HC-family picture but changes its shape.

The main-head blob scan already showed strong byte identity. The live branch topology now shows that HC/God Brain/Transcendence retained a large common branch vocabulary while their actual commit heads diverged repository-locally. bt2 does not retain that branch namespace despite sharing substantial HC bytes.

Bounded result:

`HC_GODBRAIN_TRANSCENDENCE_SHARE_LARGE_BRANCH_NAMESPACE_WITH_DIVERGED_HEADS_BT2_DOES_NOT`

> **HOSTILE REVIEWER:** Same branch names can be bulk-created or copied without proving ancestry; different commit SHAs can still have identical trees after metadata/parent changes.

Accepted. This scan is a provenance signal, not an ancestry proof. The next valid test is tree-level comparison on stratified same-named branch heads, followed by commit-parent ancestry only where tree evidence warrants it.
