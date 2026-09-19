# Portfolio Cluster Map V1

Status: **OBSERVED CLUSTERING / HYPOTHESES ONLY**

Discovery now treats the full accessible portfolio as the search space. At the 2026-09-19 cut, that is 57 repositories: 12 public and 45 private.

Because this repository is public, private repository names and private mechanism details are deliberately omitted. Their presence still affects counts, overlap analysis, and candidate generation.

## 1. Execution integrity

Public anchors: `project-runner`, `wip`, `driftguard`.

Questions:

- Is there one reusable mechanical core for exact work identity, CAS/fencing, leases, idempotency, effect reconciliation, verification, and crash recovery?
- Which parts are orchestration semantics versus generic integrity mechanics?
- Does a shared mechanism reduce total state-machine complexity, or merely move it into adapters?

Strong current hypothesis: Project Runner can own generic durable execution while WIP contributes recovery/effect-state semantics. This remains an experiment, not a declaration.

## 2. Evidence, provenance, and custody

Public anchors: `roots`, `testament`, `on-theo`.

Private participants include systems concerned with evidence storage, semantic provenance, historical retrieval, industrial evidence, and currentness.

Question: can custody mechanics be shared while each domain retains its own standards for what evidence *means*?

The failure condition is a common record format silently becoming a common ontology or truth authority.

## 3. Coordination and transport

The strongest participants are private at this cut, so this public map records the family without publishing their names.

Question: can message envelopes, routing, delivery receipts, dead-letter handling, and device transport share a neutral protocol without making the transport layer an authority system?

A candidate abstraction must first prove itself in a real cross-project flow.

## 4. Cognitive-base overlap

Public anchors: `hc-brain`, `transcendence`.

The prior portfolio audit observed substantial same-path byte identity between these systems. Discovery must remeasure against exact experiment heads rather than carrying an old count as current truth.

The central experiment is exact reconstruction:

`pinned base + explicit overlay -> identical target tree`

If that fails, deduplication is not justified.

Private related repositories are included as additional overlap subjects or negative controls.

## 5. Experiment mechanics

Public anchors: `world-zero`, `mosaic`.

Private participants include independent cognitive/model experiments and training/qualification systems.

Potentially reusable mechanics include:

- preregistration;
- deterministic run manifests;
- exact subject hashes;
- seeded experiment configuration;
- negative controls;
- holdouts;
- immutable receipts;
- statistical summary plumbing.

Scientific hypotheses, evaluators, and validity criteria remain owned by their projects.

## 6. Vera runtime and control

Public anchor: `driftguard`.

Most members of this cluster are private. The cluster includes runtime, control-plane, persistence/currentness, hardware/device, and model-routing concerns.

Discovery should aggressively look for shared *mechanics* here while treating Vera identity, current self-state, consent, relationship semantics, and release authority as project-specific boundaries.

## 7. Industrial diagnostic chain

This cluster is private at the current public surface.

Working architectural question:

Can trustworthy machine evidence/replay feed brownfield reconstruction, which then feeds a human delivery/commercial layer, without each layer rebuilding the acquisition stack?

The expected separation is:

`evidence + replay -> reconstruction/shadow model -> human service/deployment`

No actuation or production authority follows from architectural reuse.

## 8. Domain negative controls

Public anchors: `on-theo`, `testament`.

A good shared substrate should work underneath specialized domains without flattening their evidence classes, canon rules, scientific questions, privacy models, or authorship.

Negative controls are first-class Discovery evidence. A project that **should not** fit an abstraction can be more informative than a project that does.

## 9. Next experiment queue

After the three seeded candidates, the strongest next families to instantiate are:

1. execution-integrity common mechanics;
2. neutral coordination envelope tested by a real cross-project flow;
3. experiment-harness mechanics across two scientifically independent consumers;
4. runtime/control setting propagation with a deliberately non-authoritative feature;
5. industrial evidence/replay handoff into reconstruction.

Each must be converted into a bounded candidate with exact refs and explicit rejection criteria before implementation begins.

## Hostile review of this map

> **HOSTILE REVIEWER:** Clustering 57 repositories can create the illusion of objectivity while still embedding the classifier's assumptions. Counts and digests prove inventory coverage, not that the chosen families are correct. Discovery must permit repositories to belong to multiple clusters, permit new clusters to emerge, and record failed classifications rather than forcing everything into the initial taxonomy.

Accepted. The family map is explicitly non-exclusive and revisable.
