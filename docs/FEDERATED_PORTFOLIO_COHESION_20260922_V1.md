# Federated Portfolio Cohesion Research — 2026-09-22 V1

Status: **PUBLIC-SAFE RESEARCH / HYPOTHESIS ONLY**

Exact Discovery base:

`vera/discovery-live-census-public-intake-v1-20260921@da9fd6f507d19f8afdfff4e5a313554263e4652e`

Observed portfolio inventory at this pass:

- 58 repositories total;
- 23 public repositories;
- 35 private repositories retained as an opaque cohort in this public repository.

This packet asks a narrower question than “what common framework can run everything?”:

> **What is the smallest set of contracts that lets independently authoritative systems work together without turning one of them into a mandatory global runtime?**

The current evidence supports a **federated-cohesion hypothesis**, not a reusable-platform promotion.

## Public subjects

### Project Runner

Exact subject:

`thebrazenbeard/project-runner@bc05812b560b4fcde3a362e72fba04c626cafac8`

Its current public source separates backend capability from target authority, binds work to exact repository/ref/path subjects, requires expected-state checks for mutations, and requires post-write readback. Its work-unit schema also makes orchestration identity, inputs, collision keys, budgets, outputs and completion criteria explicit.

Bounded interpretation: Project Runner is a portfolio orchestrator. Its own contract rejects the idea that orchestration or connector capability manufactures authorization.

### WIP

Exact subject:

`thebrazenbeard/wip@12a7c23dbe0482fd7bfe63659e54526778efef1e`

WIP is a recovery/effect-integrity system. It separates work-state loss from effect ambiguity, journals consequential operations through PREPARED → ATTEMPTED → verified/failed/ambiguous outcomes, and requires inspection before retry after ambiguous execution.

Bounded interpretation: WIP can preserve and recover work, but its records do not grant authority for the external effects they describe.

### DriftGuard

Exact subject:

`thebrazenbeard/driftguard@9894692ff6b549e4378bcc2b8ca46813ff18bf37`

DriftGuard separates behavioral evidence, reload decisions, actuator outcomes, acknowledgements and later behavioral verification. It explicitly rejects hidden-state equivalence, reload-causality and provider-obedience claims that exceed the observable evidence.

Bounded interpretation: DriftGuard contributes behavioral regression/currentness evidence. It is not a general effect authority or identity oracle.

## What Discovery already falsified

Discovery has already tested a neutral effect-attempt envelope across Project Runner, WIP and DriftGuard.

That work established a useful fact: heterogeneous producers can emit one observational interchange shape while retaining native semantics.

But the same line then measured its own maintenance economics.

PR #13 recorded **zero pre-existing source-specific parser lines deleted**. PR #14 searched for a real downstream parser that the shared envelope could replace and found none. Its disposition was:

`STOP_EFFECT_ENVELOPE_CENTRALIZATION_PENDING_ORGANIC_REPLACEMENT_TARGET`

That negative result matters. Interoperability is not, by itself, evidence that a shared runtime or shared library should become mandatory.

## Working hypothesis

The portfolio should prefer **federated interoperability**:

`project-owned semantics + exact provenance + narrow shared contracts + explicit fallback`

rather than:

`one global state machine + adapters for everything`

Good sharing candidates are mechanical boundaries that can remain semantically neutral: exact-subject bindings, transport/interchange envelopes, receipts, currentness evidence classes, validation contracts and failure/retry boundaries.

Bad default centralization targets are domain truth, identity/relationship semantics, target authority, native state machines, provider effect authority, runtime currentness and project-specific qualification rules.

The following distinctions are therefore treated as candidate invariants, not stylistic preferences:

- observation ≠ authority;
- coordination ≠ authorization;
- transport ≠ semantic ownership;
- write success ≠ completion;
- decision ≠ effect;
- effect ≠ behavioral qualification;
- shared envelope ≠ shared native state machine;
- source integration ≠ runtime installation.

## Private-portfolio boundary

The 35 private repositories are intentionally not named here.

A public Discovery packet may use their count, aggregate evidence, or approved opaque attestations. It may not publish private repository identities or private mechanism details merely to make an architectural story look complete.

This means the present hypothesis is **not yet portfolio-generalized**. The public evidence is strong enough to generate falsifiable experiments, not to claim universal coverage.

## Hostile review

> **HOSTILE REVIEWER:** This can still be architecture theater. A diagram with clean layers proves nothing unless it deletes duplicated work, isolates a real failure, or reduces maintenance burden.

Accepted. No promotion follows from this packet. The next experiment must measure an organic integration, not manufacture another adapter solely to make the architecture look reusable.

> **HOSTILE REVIEWER:** You may be using the projects’ existing boundaries as circular evidence that federation is preferable.

Accepted. Federation is only the current hypothesis. A stronger shared abstraction should win if two materially independent consumers show lower total complexity, preserved semantic ownership, failure isolation and a real rollback path.

> **HOSTILE REVIEWER:** Twenty-three public repositories cannot stand in for thirty-five private ones.

Accepted. Any claim that the architecture generalizes across the private cohort requires privacy-preserving exact evidence under Discovery’s existing opaque/private mechanisms.

## Next falsifiers

**FED-EXP-1 — Organic federated handoff.** Find a real cross-project workflow that independently needs exact provenance, authority and effect evidence. A PASS requires measurable deletion of duplicated glue or prevention of a concrete failure class. If adapters add equal or greater burden, or create a mandatory central runtime, the hypothesis fails for that surface.

**FED-EXP-2 — Typed currentness receipt.** Test whether two independent projects can use one receipt shape that keeps source, package, install, route, runtime consumption, effect and qualification separate while leaving each project authoritative over its own currentness. If the receipt requires project-specific semantic interpretation, keep it local.

## Claim ceiling

`PUBLIC_SAFE_RESEARCH_HYPOTHESIS_ONLY_NO_CANDIDATE_PROMOTION_NO_RUNTIME_AUTHORITY`

This packet does not authorize merge, deployment, installation, provider mutation, runtime activation, private publication, authority transfer or repository consolidation.
