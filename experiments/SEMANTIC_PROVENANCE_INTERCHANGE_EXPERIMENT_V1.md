# Semantic provenance interchange experiment V1

Status: **PASS_WITH_LIMITS / CANDIDATE REMAINS HYPOTHESIS**

This experiment executes the next falsifier named by `SEMANTIC_PROVENANCE_INTERCHANGE_V1`.

It does not try to define a universal semantic ontology. The shared envelope carries only:

- exact proposition identity and text;
- exact project/source provenance;
- evidence bindings when evidence actually exists;
- unresolved/surviving-alternative state;
- currentness and supersession;
- a claim ceiling;
- exact pointers back to project-native extensions.

## Semantic Atlas case

Exact subject: `semanticatlas/main@5669a727b870a490ecee748b2cd712a2fc4a54c5`.

The case uses the current staged `SEMANTIC_INTERFACE_FIDELITY` method:

- proposition `PROP-b1cfd327-7276-4c12-9532-cff244332845`;
- current-method status `CURRENT_METHOD_PENDING_SCHEMA_MAPPING`;
- adjudication `VADJ-f895b498-bcab-4c12-b989-51fd32575561`;
- three exact historical evidence IDs;
- explicit evidence-custody limitation retained from the source;
- project-native definitions and node semantics remain external exact refs.

The interchange does not reinterpret Semantic Atlas node IDs or promote research staging into canonical state.

## UNVTRSLR case

Exact subject: `unvtrslr/main@903d79c6e47bb9f73bd7700edd35315777e9f5d1`.

The case uses C047:

> Operational relation verification and semantic naming are non-monotonic, separable claims.

Its native status is `DESIGN_REQUIREMENT`.

Crucially, this record has **zero empirical evidence bindings**. R2 semantic claim controls are specified but the harness is not built. The interchange therefore records it as `SPECIFIED_CONTROL_CASE`, not an observed result.

That is a useful falsifier: a shared provenance envelope that turned C047 into “evidence” would already have failed.

## SPM third-consumer test

Exact subject: `spm/main@0ab6e6cd32a48a0afa22c8c27ec6bae67220d7e8`.

SPM's evaluation document names six dimensions that can consume the shared envelope structurally:

- referential integrity;
- semantic scope fidelity;
- contradiction / ambiguity preservation;
- provenance sensitivity;
- correction-state transition;
- temporal/currentness sensitivity.

The adapter is forbidden from consuming Semantic Atlas native status/ontology semantics or UNVTRSLR substrate/evaluator semantics as cross-project meaning.

Result:

`STRUCTURAL_THIRD_CONSUMER_COMPATIBILITY_ONLY_NOT_SPM_MODEL_QUALIFICATION`

No SPM model or prototype was evaluated.

> **HOSTILE REVIEWER:** Two hand-selected cases can prove that a schema is capable of carrying two examples, not that a reusable abstraction has positive maintenance economics. Exact project-native refs may simply move complexity out of the shared record and into consumers.

Accepted. That is why the candidate remains **HYPOTHESIS**. The next useful falsifier is an implementation/economics test: add another materially different claim-control case per producer, measure adapter complexity and duplicated plumbing removed, and require an independent hostile review before any lifecycle promotion.

## Bounded result

The first real two-producer mapping did **not** require a shared ontology, did **not** collapse a design requirement into empirical evidence, and can be consumed structurally by an independent third project without reading native semantic statuses as shared truth.

That is enough to continue testing the mechanic. It is not enough to call it reusable infrastructure.
