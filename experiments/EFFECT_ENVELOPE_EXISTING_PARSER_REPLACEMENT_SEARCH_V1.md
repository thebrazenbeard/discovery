# Existing Effect-Parser Replacement Search V1

Status: **NO VALID EXISTING REPLACEMENT TARGET FOUND**

The previous economic falsifier required a stronger test: stop counting hypothetical
future integrations and find a real, already-existing downstream workflow whose
source-specific effect parsing can actually be deleted.

That search did not produce a valid target.

## Admission rule

A replacement target had to satisfy all of these conditions:

1. it existed before the Discovery V0 experiment;
2. it is downstream/observational rather than native effect authority;
3. it actually parses source-specific effect/outcome state;
4. V0 can replace that parsing without erasing native semantics;
5. the removed code can be measured.

Anything that decides retry, recovery, completion, verification, provider
currentness, or another native authority domain is not eligible.

## Candidates rejected

### Project Runner recovery

Exact source:

`work/exodus-current-m6-discovery-v1-20260919@bee7e720ba923ef38ce87fca4c9c2560163a9360`

`runner/recovery.py` blob:
`b03c1ab698fe7e6352870d6132e11b9bfa689bab`

The phase branches determine recovery action, live-fence terminalization, effect
reconciliation, and bounded retry. That is Project Runner's native authority.
Replacing it with V0 would make the interchange vocabulary authoritative over
recovery.

**Rejected.**

### BT2 BugOps lifecycle

Exact main:
`30e81cadd94fae117a7f6875523c03251c7c9f6e`

The PREPARED / ATTEMPTED / VERIFIED paths in migrations 0007–0010 are the
canonical operation and bug-state implementation. They write authoritative
database state, create dispatch work, enforce closure evidence, and decide when
reconciliation is required.

V0 may describe such effects downstream. It may not replace this state machine.

**Rejected.**

### Radar operator reconciliation

Exact Bus main:
`aeab0f04fc9b4bd7c2945c9a53011c53fac809b4`

`src/radar/operator.py` blob:
`baed08db2e7c875010f72c4b6db57d6b7878f392`

Radar's GitHub/provider comparison is projection/currentness reconciliation.
It is not a parser for the effect vocabularies being normalized by V0.

**Rejected.**

### Vera provider/currentness logic

Exact Vera main:
`b7b8dcd1440a3b7147bec2cc35972f083e20f44a`

Cohesion's reconcile/audit surfaces compare evidence class, revisions, provider
receipts, projection currentness, and authority ceilings. They are already
provider-generic and semantically broader than effect outcome.

Replacing them with V0 would delete evidence semantics, not duplicate parsing.

**Rejected.**

## Literal native-vocabulary search

Portfolio code searches for the current producer vocabularies and related
effect/recovery terms did not reveal a valid downstream consumer outside native
authority or the new experimental surfaces.

The strongest matches were native implementations themselves:

- Project Runner recovery;
- BT2 operation lifecycle;
- Radar transport/projection reconciliation;
- Vera inference/provider ambiguity handling.

That is negative evidence against further centralization right now.

## Result

Actual existing parser target found: **no**

Actual removable pre-existing parser LOC identified: **0**

Current disposition:

`STOP_EFFECT_ENVELOPE_CENTRALIZATION_PENDING_ORGANIC_REPLACEMENT_TARGET`

This does not mean the envelope is useless. The preceding experiments establish
interoperability and two source-agnostic observers.

It means the portfolio currently lacks evidence that further centralization
would remove real maintenance burden.

The candidate remains `EXPERIMENTING`.

Do not promote:

- `PROVEN_REUSABLE`;
- mandatory shared runtime library;
- Discovery runtime dependency.

## Reopen condition

Reopen only when a real pre-existing downstream workflow appears that:

- branches on source-specific effect/outcome semantics;
- is not the producer's native authority path;
- can consume V0 instead;
- allows measurable deletion of the old parser;
- remains correct when Discovery itself is unavailable.
