# Portfolio Cluster Map V1

Status: **OBSERVED CLUSTERING / HYPOTHESES ONLY**

Discovery now treats the full accessible portfolio as the search space. At the 2026-09-21 cut, that is 58 repositories: 23 public and 35 private.

Because this repository is public, private repository names and private mechanism details are deliberately omitted. Their presence still affects counts, overlap analysis, and candidate generation.

## 1. Execution integrity

Public anchors: `project-runner`, `wip`, `driftguard`.

Questions:

- Is there one reusable mechanical core for exact work identity, CAS/fencing, leases, idempotency, effect reconciliation, verification, and crash recovery?
- Which parts are orchestration semantics versus generic integrity mechanics?
- Does a shared mechanism reduce total state-machine complexity, or merely move it into adapters?

Strong current hypothesis: Project Runner can own generic durable execution while WIP contributes recovery/effect-state semantics. This remains an experiment, not a declaration.

## 2. Evidence, provenance, and custody

Public anchors: `roots`, `testament`, `on-theo`, `semanticatlas`, `voss`.

Private participants include systems concerned with evidence storage, semantic provenance, historical retrieval, industrial evidence, and currentness.

Question: can custody mechanics be shared while each domain retains its own standards for what evidence *means*?

The failure condition is a common record format silently becoming a common ontology or truth authority.

## 3. Coordination and transport

Public anchor: `vera-mesh`. Private participants remain part of the family.

Question: can message envelopes, routing, delivery receipts, dead-letter handling, and device transport share a neutral protocol without making the transport layer an authority system?

A candidate abstraction must first prove itself in a real cross-project flow.

Current public hypothesis: `VERAMESH_SYNOLOGY_HANDOFF_V1` tests whether VeraMesh transport/session source can hand off source/payload identity to Vera Synology packaging while source, package, install, route, and live-effect currentness remain distinct.

## 4. Cognitive-base overlap

Public anchors: `hc-brain`, `transcendence`, `god-brain`, `bt2`.

The prior portfolio audit observed substantial same-path byte identity between these systems. Discovery must remeasure against exact experiment heads rather than carrying an old count as current truth.

The central experiment is exact reconstruction:

`pinned base + explicit overlay -> identical target tree`

That test now succeeds on the exact current main heads as well as the earlier historical subject. Current HC main tree `623f272aa9060ad9e222a5cfaea801082bb5a562` plus 37 explicit deletions and 8 same-path object overrides (0 additions) recomputes Transcendence main tree `c8d16282fa65b14962757539773a78803613bd6a` exactly. This proves current-head reconstructibility; it does not yet prove favorable forward maintenance economics.

Private related repositories are included as additional overlap subjects or negative controls.

The 2026-09-21 portfolio-wide default-head blob scan strengthens this family classification: across all 253 public-repository pairs, the only six pairs sharing any Git blob SHA are exactly the complete `bt2` / `god-brain` / `hc-brain` / `transcendence` clique. The other 247 public pairs share zero blob SHAs on that exact source cut.

This isolates a real byte-identity cluster, but does not decide lineage direction or whether deduplication is beneficial.

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

Public anchors: `driftguard`, `vera-mesh`, `vera-synology`.

Most members of this cluster are private. The cluster includes runtime, control-plane, persistence/currentness, hardware/device, and model-routing concerns.

Discovery should aggressively look for shared *mechanics* here while treating Vera identity, current self-state, consent, relationship semantics, and release authority as project-specific boundaries.

## 7. Industrial diagnostic chain

Public anchor: `abil`. Private participants remain part of the broader industrial chain.

Working architectural question:

Can trustworthy machine evidence/replay feed brownfield reconstruction, which then feeds a human delivery/commercial layer, without each layer rebuilding the acquisition stack?

The expected separation is:

`evidence + replay -> reconstruction/shadow model -> human service/deployment`

No actuation or production authority follows from architectural reuse.

Current public-cut result: ABIL is the only defensible public industrial-chain anchor found in the 2026-09-21 intake/search pass. Searches across the other 22 public repositories did not identify a second brownfield/PLC/historian/fieldbus/OPC/Modbus/machine-telemetry handoff subject. This is a hold, not proof of absence; private, branch-only, unindexed, differently worded, or future subjects may exist.

## 8. Domain negative controls

Public anchors: `on-theo`, `testament`, `Attune`.

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

> **HOSTILE REVIEWER:** Clustering 58 repositories can create the illusion of objectivity while still embedding the classifier's assumptions. Counts and digests prove inventory coverage, not that the chosen families are correct. Discovery must permit repositories to belong to multiple clusters, permit new clusters to emerge, and record failed classifications rather than forcing everything into the initial taxonomy.

Accepted. The family map is explicitly non-exclusive and revisable.


## 10. Semantic grounding and provenance

Public anchors: `semanticatlas`, `spm`, `unvtrslr`.

Question: can semantic hypothesis/provenance records, uncertainty representation, rival-hypothesis lineage, and adversarial evaluation mechanics be shared without creating a universal ontology or forcing a single model architecture?

Default posture:

`SHARE_PROVENANCE_AND_EVALUATION_MECHANICS_NOT_ONTOLOGY`

The strongest immediate falsifier is to identify one minimal record/evaluation contract independently needed by at least two projects, then prove each project's native semantic model remains strictly richer and authoritative.

## 11. 2026-09-21 public-surface refresh

Visibility changes are not architectural promotion. They do, however, permit exact public-safe source binding where Discovery previously had to stay aggregate or opaque.

Newly nameable subjects include:

- `god-brain` and `bt2` for HC-family lineage and duplication testing;
- `abil` for industrial brownfield diagnostics/reconstruction;
- `semanticatlas`, `spm`, and `unvtrslr` for semantic provenance and grounding mechanics;
- `vera-mesh` and `vera-synology` for transport/runtime/deployment separation;
- `noema` as an independently evolving predictive-cognition research subject;
- `voss` as an audit/review subject;
- `Attune` as a negative control against universalizing relationship/identity semantics.

Exact HC-family measurement at the refreshed cut:

- `god-brain/main@c0f6af7143aa5916bae96eb1f0ee9c9de6505cf5` vs `hc-brain/main@618245b54fb923c7a204892c6953ab6d1c5dac57`: 299/300 identical same-path blobs; only `README.md` differs; identical bytes are 99.54245136% of the measured HC byte surface.
- `bt2/main@30e81cadd94fae117a7f6875523c03251c7c9f6e` vs the same HC head: 178 identical same-path blobs, 10 changed same-path blobs, 329 bt2-only blobs, and 112 HC-only blobs; identical bytes are 46.14031461% of the measured HC byte surface.

These measurements establish duplication, not consolidation. The generated `HC_FAMILY_LINEAGE_V1` candidate remains a HYPOTHESIS until exact reconstruction and forward-maintenance evidence exist.


## 12. Audit/reviewer source sufficiency

Public anchor: `voss`.

At `voss/main@54478372002bb24c6df733092a32abbdd1fa8d3c`, the public surface contains only the role README identifying Voss as a forensic auditor/reviewer.

That is insufficient to classify a reusable audit protocol or generate a Discovery candidate.

Disposition:

`INSUFFICIENT_PUBLIC_SOURCE_NO_CANDIDATE`

Discovery should revisit Voss only when public source exposes a concrete review contract, receipt, exact-head binding, evidence model, or executable audit mechanic.
