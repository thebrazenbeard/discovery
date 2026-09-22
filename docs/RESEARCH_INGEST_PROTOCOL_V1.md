# Discovery Research Ingest Protocol V1

Status: SOURCE CANDIDATE / PUBLIC-SAFE
Scope: repeatable portfolio research ingestion
Authority ceiling: observation and hypothesis generation only

## Purpose

Discovery needs a durable research layer between raw repository inspection and architectural candidate generation.

A research ingest records what was actually observed at an exact source subject, what mechanical or semantic signals were found, what remains uncertain, and which candidate families the observation may inform. Ingest does not promote a shared abstraction and does not make Discovery authoritative over the source project.

## Required discipline

Each public research observation must bind:

- a repository name;
- an immutable 40-hex source ref;
- the exact source locator inspected;
- an observation state;
- a concise source-grounded summary;
- candidate-family inputs, including newly emerging families when the existing taxonomy does not fit;
- preserved boundaries;
- unresolved uncertainty;
- an explicit promotion ceiling.

A current research cut must also bind the exact portfolio census by observation date, repository count, and all-name digest.

## Evidence states

Research ingest uses only:

- `OBSERVED` — directly supported by the inspected source;
- `HYPOTHESIS` — a falsifiable interpretation generated from one or more observations.

Ingest may not emit `EXPERIMENTING`, `SUPPORTED`, or `PROVEN_REUSABLE`. Those states require the separate Discovery candidate/experiment lifecycle.

## Currentness

An observation is current only for its exact source ref.

Later movement of a repository does not erase the observation, but it prevents the observation from being represented as a fresh statement about the new head until re-ingested.

Inventory drift invalidates a research cut's claim to portfolio completeness. Refresh the census and cut together.

## Privacy

This public repository may name public repositories.

Private repository identities and private technical details must not be emitted by the public ingest. Private participation is represented only through approved aggregate or opaque mechanisms already governed by Discovery.

The public census may publish private counts and digests, but not raw private repository names.

## Discrepancies

Conflicting source roles, duplicated identity claims, stale documentation, or disagreement between installed project contracts and repository contents are evidence.

Do not silently reconcile them.

Record the discrepancy, bind both sides when available, and keep the conclusion at `OBSERVED` or `HYPOTHESIS` until exact evidence resolves it.

## Candidate-family generation

A research observation may point at an existing family or propose an emergent family. This is routing metadata, not architectural truth.

A family becomes a candidate only under `docs/CLASSIFIER_PROTOCOL_V1.md` and `docs/DISCOVERY_PROTOCOL_V1.md`.

## Negative evidence

Absence, incompatibility, semantic collision, sparse documentation, and useful independence are first-class findings.

A research cut is successful when it makes uncertainty and non-reuse legible, not when it maximizes the number of abstractions.

## Validation target

`research/PUBLIC_REPOSITORY_RESEARCH_CUT_20260921_V1.json` is the first populated cut under this protocol.

`tools/validate_research_ingest.py` enforces:

1. exact census binding;
2. exact equality between public census membership and research observations;
3. unique repositories;
4. immutable source refs;
5. public-only source subjects;
6. non-empty summaries, boundaries, and uncertainty arrays;
7. `OBSERVED`/`HYPOTHESIS` state ceiling;
8. `OBSERVED_ONLY` or `HYPOTHESIS_ONLY` promotion ceiling.
