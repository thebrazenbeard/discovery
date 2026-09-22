# Rezon ↔ Project Runner maintenance/currentness V1

Status: **EXPERIMENTING NARROWED / CURRENT SUCCESSOR INGESTED / NO REUSE PROMOTION**

Discovery's original Rezon↔Runner experiment succeeded on Project Runner PR #26:

`4de0f6148b3d7d04ccdb4e0057435fa0d904590a`

That verifier was deliberately thin and Discovery recorded two important boundaries:

- Runner did **not** recompute Rezon's canonical producer-ID formula.
- accepted/rejected/unresolved claim data was treated as opaque mechanical payload.

Those statements are no longer current.

## Current successor

Project Runner PR #31 is now the exact hardened successor:

`8e588bd1cb72808b4a611d2a0bcbaeba6cb10b15`

Its independent hostile rereview is `PASS_WITH_CLAIM_CEILING`.

The current verifier now:

- mirrors Rezon's deterministic canonical producer-ID algorithm;
- rejects forged producer IDs even when trace and receipt agree;
- rejects duplicate execution IDs independently of optional output/producer bindings;
- requires canonical digest fields to be lowercase SHA-256 when present;
- requires snapshot/output digests for a canonical producer binding;
- rejects non-empty generic accepted/rejected claim dispositions;
- rejects `claim_disposition_complete=true`;
- remains PLAN-only and non-promotional.

It still does **not** decide Rezon truth, admission, qualification, completion, target authority, or external-effect authority.

## Maintenance delta from the original Discovery verifier

From PR #26 exact head to PR #31 exact head:

- **11 commits ahead**
- **7 changed files**
- **+445 / -16 lines**
- verifier: **314 → 387 lines** (+73 net)
- primary verifier tests: **132 → 212 lines** (+80 net)
- new failure-path test module: **105 lines**
- new boundary document: **74 lines**
- new failure fixture + binding: **58 + 41 lines**

The current hosted qualification is **234/234 PASS** at run `35546042175`.

This growth is not automatically waste. The added checks close real hostile counterexamples. But it is direct evidence that the supposedly thin boundary has ongoing producer-contract maintenance cost.

## Organic second-consumer search

Discovery searched the inspected public/default and active-PR surfaces for a second direct consumer of `rezon.run-evidence.v1`.

No second parser/consumer was identified.

Vera PR #181 references the hardened Project Runner/Rezon evidence boundary in a broader coherence contract, but it does not independently parse or verify the Rezon evidence object.

That is not a portfolio-wide absence proof. Private repositories and unindexed branch contents remain outside this negative search.

## Result

`EXPERIMENTING_NARROWED_CURRENT_SUCCESSOR_NO_REUSE_PROMOTION`

The boundary still demonstrates a useful fact:

`REZON_EPISTEMIC_AUTHORITY_RETAINED / RUNNER_STRUCTURAL_VERIFICATION_WORKS`.

But the stronger reusable-infrastructure story is weaker than before:

- the verifier is producer-contract-aware;
- maintenance coupling is measurable;
- net code deletion/savings is not demonstrated;
- no second organic consumer is demonstrated.

> **HOSTILE REVIEWER:** If every producer invariant has to be mirrored into Runner, you may be building a second Rezon validator with a different badge.

That objection is now live. Current evidence does not show semantic authority transfer, but it does show growing producer-specific contract duplication. Promotion must wait for actual maintenance economics or a second organic consumer.
