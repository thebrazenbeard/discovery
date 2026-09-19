# Discovery Classifier Protocol V1

Status: **SOURCE CANDIDATE / PUBLIC-SAFE**

## Purpose

Discovery must not convert one architect's first taxonomy into portfolio truth.

This protocol defines a falsifiable, multi-label relationship graph used to generate architecture hypotheses from observed repository evidence.

## Rules

1. **Census before classification.** Every accessible repository is in the search space even when no public node is emitted.
2. **No forced fit.** A repository may be `UNCLASSIFIED`.
3. **Multi-label by default.** A repository may participate in multiple candidate families.
4. **Competing edges are legal.** The same pair may simultaneously carry, for example, `OVERLAPPING_MECHANIC` and `MUST_REMAIN_SEPARATE` claims when they refer to different scopes.
5. **Relationships are scoped.** An edge must say what mechanic/semantic surface it concerns.
6. **Evidence state is explicit.** `OBSERVED`, `HYPOTHESIS`, `EXPERIMENTING`, `SUPPORTED`, `REJECTED`, or `SUPERSEDED`.
7. **No numeric confidence laundering.** Discovery does not convert subjective confidence scores into architectural authority.
8. **Exact refs for strong claims.** `SUPPORTED` and implementation-affecting claims require immutable source subjects or reproducible evidence locators.
9. **Negative evidence counts.** Failed integrations, irreducible adapters, semantic collisions, and useful isolation are first-class evidence.
10. **Privacy before completeness display.** Private repositories are still analyzed, but this public repository may represent them only through approved opaque/aggregate surfaces.

## Relationship vocabulary

- `OVERLAPPING_MECHANIC` — similar mechanical invariant appears in both subjects.
- `DUPLICATED_IMPLEMENTATION` — implementation duplication is directly measured.
- `COMPLEMENTARY_BOUNDARY` — systems appear intentionally composable while retaining separate semantics.
- `POTENTIAL_BASE_OVERLAY` — one system may be reconstructible as pinned base plus explicit overlay.
- `PROVIDER_CONSUMER` — one subject may provide a reusable mechanic to another.
- `MUST_REMAIN_SEPARATE` — shared implementation or ontology would collapse a material semantic/scientific/authority boundary.
- `NEGATIVE_CONTROL` — a subject is intentionally used to test that an abstraction does not overreach.
- `HISTORICAL_REFERENCE` — useful comparison/provenance source, not presumed current architecture.
- `NEEDS_MORE_EVIDENCE` — observed similarity is insufficient to classify more strongly.

These labels describe scoped relationships. They are not global verdicts on repositories.

## Candidate generation

A relationship becomes a Discovery candidate only when:

- at least two real subjects are identified;
- the shared scope is narrow enough to state precisely;
- preserved boundaries are explicit;
- at least one falsifiable experiment can be named;
- rejection conditions are written before implementation;
- private information can be handled without publication leakage.

Candidate generation is allowed from `OBSERVED` and `HYPOTHESIS` edges. Promotion is governed separately by the Discovery Protocol.

## Classification falsification

A classification must be revised or rejected when:

- exact remeasurement contradicts the claimed overlap;
- an integration requires semantic translation that is larger than the shared mechanic;
- the abstraction moves rather than removes complexity;
- an allegedly generic component imports project-specific authority;
- a negative-control project cannot consume the mechanic without semantic damage;
- newer exact evidence supersedes the source cut.

## Self-critique

Discovery's own classifier is itself a hypothesis. If it becomes harder to understand than the portfolio relationships it describes, that is evidence against the classifier.
