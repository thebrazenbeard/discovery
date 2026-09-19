# Discovery

Discovery exists to answer one question:

> **What should actually be shared across the portfolio, and what should remain independently evolved?**

Repository sprawl is not automatically a defect. Duplication can provide evolutionary isolation, fault containment, independent falsification, and freedom to challenge assumptions.

Discovery therefore does **not** begin with a universal framework. It begins with competing hypotheses and forces proposed shared infrastructure to earn promotion through real consumers, measured simplification, exact evidence, rollbackability, and hostile review.

## Core rule

**No abstraction is promoted because it looks elegant.**

A candidate shared mechanism must demonstrate that it:

1. serves at least two materially independent consumers;
2. removes more complexity than it introduces;
3. preserves each consumer's semantic ownership and authority boundaries;
4. can fail without taking unrelated projects down with it;
5. has an explicit fallback or rollback path;
6. survives a hostile review that tries to prove the abstraction should not exist.

## Candidate states

`OBSERVED` → `HYPOTHESIS` → `EXPERIMENTING` → `PROVEN_REUSABLE`

A candidate may instead become `PROJECT_SPECIFIC`, `REJECTED`, or `SUPERSEDED`.

`PROVEN_REUSABLE` is evidence of reuse suitability only. It grants no merge, deployment, installation, authority, or semantic promotion elsewhere.

See [docs/DISCOVERY_PROTOCOL_V1.md](docs/DISCOVERY_PROTOCOL_V1.md).

## Initial experiments

The first three candidates deliberately test different kinds of reuse:

- **Rezon ↔ Project Runner:** can epistemic reasoning remain independent while delegating mechanical execution?
- **HC Brain ↔ Transcendence:** can duplicated base implementation be replaced by exact base + overlay reconstruction without destroying provenance or experimental independence?
- **Project Lantern ↔ two consumers:** can evidence custody/interchange be reused without creating a global truth database?

These are hypotheses, not architectural decisions.
