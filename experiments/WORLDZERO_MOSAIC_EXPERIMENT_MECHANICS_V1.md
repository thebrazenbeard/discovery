# World Zero ↔ Mosaic Experiment Mechanics V1

Status: **PAIRWISE SHARED-HARNESS HYPOTHESIS REJECTED / PROJECT-SPECIFIC / RECEIPT PATTERN NEEDS MORE EVIDENCE**

## Exact subjects

World Zero:
- branch: `science/demography-older-mortality-mass-normalization-v1-20260919`
- head: `9be13e8e34772a90a812815b074bf21bb89e972a`
- run-receipt schema: `specs/RUN_RECEIPT_V1.schema.json`
- run-receipt blob: `88a039e32e3cbcb4e26aa9a95cc2f0d817ca1423`
- run-receipt implementation blob: `bc419e77c1b4169560435b620658cd876fb67835`
- comparison-protocol schema blob: `c0580445f322fb3b91ad0619eb30502414803d55`
- comparison implementation blob: `fe1b46abe3f31a3a326eb4bd2e04de242d16194b`

Mosaic:
- branch: `one/mosaic-p1-protocol-harness-v1-20260918`
- head: `96fd911e5a6a9b2069a88ae20d0dfa4f6bbad01f`
- P1A harness document blob: `a939a79cf9585f46dd860379ecde794f872a0e3a`
- P1 design blob: `cef955ace6529bdbb5939158fee09bc583ab5848`
- handoff runtime blob: `ab880ada80dd238751f7aec918cd0cafb5e85ce9`
- test-case blob: `09184636b877839faa191d2b068fa149405fec57`
- test blob: `ebf4851bacfbbab71b7a6ad664ef232123fd91bd`
- CI workflow blob: `8e01e7a4c16ea528adb61751e949457406cdce59`

## Initial question

Do these projects contain enough common experiment machinery to justify a shared deterministic experiment harness?

## Result

**No, not from this pair.**

They share disciplined experimental *ideas*, but the exact executable contracts solve different problems.

## World Zero owns scientific qualification semantics

The World Zero receipt binds a scientific subject far beyond a generic run ID:

- exact source commit and tree;
- manifest and dataset-set digests;
- parameter, region, scenario, and observation-map digests;
- calibration and holdout partitions;
- comparison-protocol digest;
- causal topology/implementation coverage when applicable;
- solver/version/timestep/tolerance/seed/environment identity;
- result digest.

Its comparison protocol freezes subjects, metrics, decision rules, holdouts, missing-subject behavior, and confirmatory versus exploratory status.

Those are not neutral plumbing. They are part of how World Zero prevents post-hoc scientific promotion.

## Mosaic owns continuity-experiment semantics

The current Mosaic harness is deliberately synthetic and narrow.

Its state machine is about:

- revisioned continuity events;
- RESET / MOSAIC STATE / FULL HISTORY / ORDINARY RETRIEVAL controls;
- correction/currentness/supersession and related continuity task families;
- accuracy, stale-state errors, correction burden, and payload bytes;
- explicit negative gates for actual accelerator unload, swap latency, encode/decode latency, independent repeatability, and P1 eligibility.

The tests explicitly ensure the harness cannot self-award P1 and that ordinary retrieval may match or beat Mosaic state.

Those semantics should not be forced into a generic scientific harness.

## What survives

There is a much weaker common pattern:

`exact subject -> execution context -> result evidence -> explicit claim ceiling`

That pattern may eventually justify a shared receipt/interchange mechanism.

But two implementations are not enough here. A wrapper extracted now would probably be schema theater: generic enough to contain both, but not actually deleting meaningful code.

## Decision

- Shared executable harness: **PROJECT_SPECIFIC / DO NOT EXTRACT**
- Shared evaluators or validity rules: **MUST_REMAIN_SEPARATE**
- Generic receipt pattern: **NEEDS_MORE_EVIDENCE**
- Shared code: **NONE YET**
- Next gate: compare the minimal receipt pattern against a third materially independent experiment system.

> **HOSTILE REVIEWER:** This is the correct kind of failure for Discovery. If every comparison produces a reusable component, Discovery is a consolidation engine wearing a lab coat. The remaining receipt pattern is still suspiciously generic; make it prove it removes real code in a third system before dignifying it with a shared schema.
