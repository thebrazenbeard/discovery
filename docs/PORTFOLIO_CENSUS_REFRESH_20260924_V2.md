# Discovery Portfolio Census Refresh — 2026-09-24

Status: live membership refresh / architecture evidence invalidation notice / no promotion authority

## Result

Live GitHub inventory for `thebrazenbeard` now contains:

- 66 repositories total;
- 48 public;
- 18 private;
- 2 archived, both private.

The predecessor V1 cut recorded 59 total / 24 public / 35 private on 2026-09-22.

This is a material portfolio topology change. Discovery must not continue treating the 24-public-repository graph, intake, overlap scan, or observatory as current whole-public-estate evidence.

## Newly public relative to the predecessor public set

The following 24 repositories are publicly nameable in the 2026-09-24 cut but were not in the prior published 24-repository set:

- RepairTracker
- bugops
- build-team-2.0
- ccb-core
- conations
- deepmemorystorage
- empathy
- freerowcochkar
- fuckup
- hephaestus
- intranel
- masamune
- meso-crct
- personification
- project-achilles
- project-lantern
- temporal
- unbound-sol
- vera
- vera-R9A0
- vera-control-plane
- vera-habitat
- vera-mono
- vera_model_training

This list is a membership delta only. It does not establish when or why visibility changed, and it does not classify any repository as reusable architecture.

## Invalidated currentness claims

The following predecessor artifacts remain useful historical evidence but are stale for claims about the **current complete public estate**:

- `portfolio/PORTFOLIO_CENSUS_V1.json`
- `portfolio/PUBLIC_SUBJECT_INTAKE_20260921_V1.json`
- `portfolio/PUBLIC_RELATIONSHIP_GRAPH_V1.json`
- public blob overlap evidence and indexes bound to the predecessor public set
- architecture-observatory claims that assume the predecessor public membership
- README counts describing 24 or fewer current public repositories

They may still support exact claims about their own frozen cuts.

## Privacy correction

Discovery already contains a hardened snapshot mechanism that uses a secret-key HMAC commitment for private repository membership.

This refresh intentionally **does not** publish a deterministic SHA-256 of sorted private repository names. No private census key was available to this execution. Therefore:

- private count is observed as 18;
- public repository membership is exact and publicly recomputable;
- exact private membership is not publicly committed by this V2 artifact;
- whole-estate exact private currentness requires a separately produced keyed snapshot.

Failing closed here is preferable to turning a public repository into a dictionary oracle for private repository names.

## Next Discovery frontier

1. Generate a fresh hardened portfolio snapshot with `tools/build_portfolio_snapshot.py` using an authorized private census key.
2. Intake/classify all 24 newly public subjects.
3. Rebuild the public relationship graph against all 48 public subjects.
4. Re-run exact public blob overlap evidence for the 48-subject set.
5. Re-run architecture-observatory validation.
6. Only then replace predecessor whole-public-estate architectural claims with the new cut.

Until those steps are complete, Discovery may use the V2 census for membership/currentness detection but must not claim that the predecessor graph or candidate-family map exhausts the present public portfolio.
