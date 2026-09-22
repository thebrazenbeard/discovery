# Discovery Architecture Observatory V1

Status: **RESEARCH ARCHITECTURE / HYPOTHESIS / NO RUNTIME AUTHORITY**

Parent exact subject:

`vera/discovery-federated-cohesion-falsifier-round-v1-20260922@0ead7c2e8752d447f6cc55cdbb921529317f9e0c`

## Purpose

Discovery should become the portfolio's **architecture observatory and reuse laboratory**.

Its job is not to operate other repositories. Its job is to observe the portfolio, reconstruct relationships, nominate falsifiable architecture hypotheses, run bounded reuse experiments, and surface change-impact evidence that individual repositories cannot see alone.

The governing separation is:

`portfolio insight != project authority`

Discovery may become important for understanding the estate. It must remain unnecessary for any project's local build, execution, recovery, semantic interpretation, or authority.

## Hard invariants

1. **Delete-Discovery invariant.** If Discovery disappears, no observed repository loses the ability to build, run, recover, or retain its own meaning.
2. **Observation is not authority.** A relationship, similarity, dependency, or stale-state finding does not authorize a project change.
3. **Confidence is not evidence class.** A high semantic-similarity score cannot substitute for exact provenance, executable behavior, or a real consumer experiment.
4. **No self-corroboration.** Discovery-generated summaries, embeddings, candidate records, or graph edges may not be cited as independent evidence for the claims that created them.
5. **Fail-closed currentness.** When a bound repository/ref moves, claims depending on that subject become stale until refreshed or explicitly historical.
6. **Negative controls remain first-class.** Similarity may justify investigation; meaningful semantic isolation may justify permanent duplication.
7. **No automatic promotion.** Automated detectors may nominate candidates. They may not move a candidate to EXPERIMENTING or PROVEN_REUSABLE.
8. **No hidden mandatory runtime.** Shared mechanisms must not require live Discovery availability for consumers to operate.
9. **Privacy boundaries survive observability.** Private repositories may participate only through governed private analysis or approved opaque evidence; public outputs must not leak private identities or implementation detail.
10. **Reuse must pay rent.** Interoperability alone is insufficient. A promoted shared mechanism must remove duplicated non-domain work, prevent a known failure class, or materially reduce maintenance/qualification burden.

## Operating loop

### 1. Observe

Produce exact, time-bound repository observations:

- repository visibility and lifecycle;
- exact default head and tree;
- languages and package/build manifests;
- dependency/SBOM surface where available;
- exported APIs, CLIs and schemas;
- workflows and qualification surfaces;
- branch/topology/provenance evidence;
- exact file/blob fingerprints;
- ownership/authority metadata when explicitly sourced.

The observation plane is descriptive. It must distinguish provider facts from Discovery inference.

### 2. Detect

Run a detector ladder from strongest literal evidence to weakest inferential evidence.

**D0 — exact Git identity**

Blob/tree/commit equality, exact ancestry, exact manifest identity.

Useful for copied snapshots, provenance reconstruction and exact stale-state detection.

**D1 — normalized lexical fingerprints**

Whitespace/comment-insensitive or identifier-normalized matching.

Useful for detecting mechanically edited copies that exact blobs miss.

**D2 — syntax/AST structure**

Language-aware structural matching using parsers such as Tree-sitter.

Useful for identifying structurally similar implementations after renaming or formatting changes.

**D3 — dependency/interface/workflow shape**

Imports, dependency graph, public API/CLI/schema shape, workflow structure, effect/currentness boundaries.

Useful for finding independently implemented instances of the same mechanical role.

**D4 — behavioral evidence**

Tests, receipts, traces, failure/retry semantics and reproducible input/output behavior.

Useful when source structure differs but an operational invariant may be shared.

**D5 — semantic/LLM nomination**

Embedding or model-assisted similarity and architecture hypotheses.

Useful for broad recall only. These results may nominate a HYPOTHESIS but never establish equivalence, provenance, reuse value, or promotion.

Semantic clone research shows why this ceiling is necessary: detectors that perform strongly on benchmark distributions can degrade under distribution shift and may rely on lexical or structural shortcuts rather than robust semantic equivalence.

### 3. Falsify

Every nominated candidate gets an opposition case before implementation.

Required attacks include:

- accidental centralization;
- false semantic equivalence;
- intentional evolutionary isolation mistaken for waste;
- privacy leakage;
- stale-source dependence;
- adapter tax;
- blast-radius increase;
- rollback failure;
- qualification burden;
- existence of a simpler local solution.

The strongest alternative explanation should be recorded beside the candidate, not buried in review prose.

### 4. Experiment

Only organic or independently useful integration targets qualify.

Measure at minimum:

- pre-existing duplicated non-domain LOC or operational steps;
- shared implementation added;
- adapter/verifier code added;
- tests/qualification added;
- dependency edges introduced;
- failure modes prevented;
- rollback/fallback cost;
- change propagation after at least one relevant upstream change;
- whether each consumer remains locally operable without Discovery.

A successful compatibility demo with no maintenance reduction remains compatibility evidence, not reuse value.

### 5. Impact radar

When an observed subject moves, Discovery should identify dependent observations and suspected relatives.

Potential outputs:

- `STALE_EVIDENCE`
- `POSSIBLE_SIBLING_FIX_REQUIRED`
- `PROVENANCE_CHANGED`
- `DEPENDENCY_SURFACE_CHANGED`
- `REQUALIFICATION_REQUIRED`
- `CANDIDATE_ECONOMICS_CHANGED`

Impact signals are investigative prompts. They are not automatic patch or merge authority.

## Evidence graph

Discovery's graph should contain claims with provenance, not free-floating conclusions.

Every nontrivial edge should carry:

- exact source subjects;
- observation date;
- evidence class;
- relation type;
- derivation method;
- current/stale/historical state;
- falsifiers;
- claim ceiling;
- whether the edge is observed or inferred.

Inferred edges should be invalidated when their source observations move.

The graph should be reconstructible from source observations plus deterministic transforms wherever practical. LLM output may annotate or nominate, but should not become the only provenance for a mechanical claim.

## Why this is not Backstage, CodeQL, or a clone detector

Existing systems provide useful pieces:

- Backstage demonstrates the value of a portfolio catalog while explicitly separating catalog metadata from ultimate source-of-truth authority.
- GitHub dependency-graph/SBOM facilities provide machine-readable dependency evidence.
- CodeQL demonstrates code-as-data analysis and custom structural querying.
- Tree-sitter provides language-aware syntax trees and structural query patterns.
- repository knowledge-graph research demonstrates large-scale provenance and sustainability analysis.

Discovery's distinctive job is to combine those evidence classes with **falsification, negative controls, reuse economics, exact currentness and protected authority boundaries**.

It should consume mature tools where useful rather than reinventing parsers, dependency resolvers or code-query engines.

## Hostile review

> **HOSTILE REVIEWER:** This is a central brain disguised as an observatory. Once every cross-project decision depends on its graph, Discovery becomes the portfolio's de facto authority.

Accepted. The delete-Discovery invariant is mandatory. Discovery may produce better information, but projects retain their own source, tests, runbooks, recovery state and decision authority. No consumer may need live Discovery availability for normal operation.

> **HOSTILE REVIEWER:** Semantic and AST similarity will flood the graph with plausible-looking nonsense.

Accepted. Similarity detectors produce candidate signals, not architectural facts. D2-D5 outputs require exact source bindings and independent corroboration. D5 can never exceed HYPOTHESIS by itself.

> **HOSTILE REVIEWER:** A continuously refreshed graph will become stale faster than you can qualify it, creating false confidence with timestamps attached.

Accepted. Staleness is a state, not an embarrassment. Head movement invalidates dependent current claims. Historical observations remain evidence but cannot silently masquerade as current truth.

> **HOSTILE REVIEWER:** Measuring LOC deleted is gameable. A shared abstraction can delete lines while increasing conceptual and operational complexity.

Accepted. Reuse economics must count adapter code, tests, dependencies, qualification work, operational burden, rollback cost and blast radius. LOC is one input, never the verdict.

> **HOSTILE REVIEWER:** Negative controls can become an excuse to preserve every duplicate forever.

Accepted. Deliberate isolation must also pay rent. When two consumers repeatedly make the same maintenance change, suffer the same bug, or maintain equivalent non-domain machinery, the burden shifts toward an extraction experiment.

> **HOSTILE REVIEWER:** Discovery can become a self-referential evidence machine: its own summaries create edges, those edges justify candidates, and those candidates become evidence for the summaries.

Accepted. No self-corroboration. Derived Discovery artifacts must trace to external exact subjects or independently governed evidence. Discovery-generated inference cannot count as an independent witness to itself.

> **HOSTILE REVIEWER:** The observatory may cost more to maintain than the duplication it is trying to understand.

Accepted as a kill criterion. Automation should be added only where it repeatedly removes manual census/reconciliation work or detects issues that would otherwise be missed. Detectors without demonstrated portfolio value should be removable plugins, not permanent architecture.

## Initial build order

1. **Snapshot engine** — turn repository inventory into exact, timestamped observations without changing projects.
2. **Currentness/invalidation engine** — mechanically mark dependent evidence stale when exact subjects move.
3. **Detector plugin contract** — support D0-D5 without allowing weaker detectors to overclaim.
4. **Evidence graph projection** — derive queryable edges from exact observations and detector receipts.
5. **Impact radar** — surface changed subjects and possible sibling/dependent effects.
6. **Experiment accounting** — compare before/after maintenance economics across real consumers.
7. **Only then:** optional UI/search surfaces.

Do not begin with a universal schema for project-native state. Begin with observation receipts and detector boundaries.

## First implementation target

The first implementation should be a **read-only snapshot/currentness pipeline**, because Discovery currently validates snapshots more strongly than it produces them.

A snapshot record should bind:

- repository;
- visibility class;
- observed ref;
- exact commit;
- exact tree where available;
- observation timestamp;
- acquisition method;
- public/private publication policy;
- optional dependency/interface fingerprints;
- status.

Changing the exact subject must invalidate derived current claims without deleting historical evidence.

That closes a real existing gap without inventing another shared runtime.

## Research anchors

- Backstage Software Catalog and system model: https://backstage.io/docs/features/software-catalog/
- Backstage catalog graph guidance: https://backstage.io/docs/features/software-catalog/creating-the-catalog-graph/
- GitHub dependency graph/SBOM APIs: https://docs.github.com/en/rest/dependency-graph
- GitHub CodeQL code-as-data analysis: https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-code-scanning
- Tree-sitter structural queries: https://tree-sitter.github.io/tree-sitter/using-parsers/queries/
- SemRepo research-software knowledge graph: https://arxiv.org/abs/2605.13310
- Semantic clone generalization study: https://arxiv.org/abs/2606.25272

## Claim ceiling

`ARCHITECTURE_OBSERVATORY_HYPOTHESIS / READ_ONLY_DISCOVERY_FIRST / NO_RUNTIME_AUTHORITY / NO_AUTOMATIC_PROMOTION / NO_MERGE_OR_DEPLOY_AUTHORITY`
