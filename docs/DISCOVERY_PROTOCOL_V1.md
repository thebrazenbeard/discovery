# Discovery Protocol V1

Status: INITIAL SOURCE CANDIDATE
Scope: portfolio architecture discovery
Non-goal: creation of a mandatory portfolio operating system

## 1. Purpose

Discovery is an experimental layer for deciding whether repeated mechanisms across independently evolved repositories should be:

- reused as-is;
- generalized into a narrow shared substrate;
- retained independently because the duplication is semantically important;
- rejected as a bad abstraction;
- reconstructed as a base + overlay relationship.

Discovery records evidence about architecture. It does not become the authority of the projects it observes.

## 2. Preservation rule

A source project's semantics, authority model, scientific hypothesis, privacy boundary, runtime state, and qualification state remain owned by that project.

Discovery may record that two projects implement similar mechanics. It may not infer that they therefore mean the same thing.

## 2.1 Private consumer attestations

Discovery is public while much of the portfolio is private. Exactness must not force publication of private repository identities or refs.

For an active `EXPERIMENTING` candidate, a private consumer may therefore appear as `visibility=PRIVATE_OPAQUE` with:

- a public-safe handle derived from the first 16 hex characters of the consumer commitment rather than a human-selected label;
- no raw repository ref;
- an explicit `SHA256_PRIVATE_NONCE_CANONICAL_V1` commitment scheme using private high-entropy nonce material;
- a 256-bit consumer commitment;
- a 256-bit exact-subject commitment;
- a 256-bit private verification-receipt digest;
- an attestation class and exact attested status.

The public validator can prove the attestation's shape, distinctness, and commitment continuity. It cannot independently inspect the hidden repository merely because a digest exists. Therefore opaque private consumers are sufficient to participate in an experiment, but **not sufficient for `PROVEN_REUSABLE` promotion** in V1. A later independently verifiable privacy-preserving mechanism must earn that stronger claim.

This rule preserves both requirements: private projects remain private, and Discovery does not weaken exact-subject discipline into undocumented trust.

## 3. Candidate lifecycle

### OBSERVED
A repeated pattern or duplication has been measured.

Required evidence:
- exact repositories and refs;
- what is identical/similar/different;
- uncertainty and missing evidence.

### HYPOTHESIS
A bounded claim proposes that sharing or deduplication could reduce complexity without semantic leakage.

Required:
- proposed boundary;
- expected consumers;
- predicted benefit;
- predicted failure modes;
- explicit rejection criteria.

### EXPERIMENTING
At least one real integration/reconstruction experiment exists.

Required:
- exact experiment subject;
- reproducible procedure;
- before/after comparison;
- failure isolation;
- rollback/fallback;
- hostile-review result.

### PROVEN_REUSABLE
A narrow mechanism has independently demonstrated value in at least two materially independent consumers.

Required:
- >= 2 real consumers;
- exact successful integrations;
- measured reduction in duplicated implementation or operational burden;
- no authority/semantic promotion;
- bounded blast radius;
- fallback remains viable;
- hostile reviewer cannot identify an unresolved critical reason to keep implementations independent.

This state says only that the mechanism is reusable. It does not authorize adoption elsewhere.

### PROJECT_SPECIFIC
Similarity exists, but sharing would erase meaningful semantic/scientific/authority isolation.

### REJECTED
The proposed abstraction failed its experiment or introduced more coupling than value.

### SUPERSEDED
A later candidate or design replaces the hypothesis.

## 4. Mandatory hostile review

Every promotion beyond HYPOTHESIS must include a hostile review whose job is to defeat the proposal.

The hostile reviewer must attack at least:

1. hidden semantic coupling;
2. authority leakage;
3. new single points of failure;
4. false equivalence between similar concepts;
5. migration/reconstruction risk;
6. rollback fidelity;
7. operational burden;
8. whether duplicated code is actually useful experimental isolation.

A candidate cannot pass by answering objections rhetorically. It needs evidence.

## 5. Consumer-driven extraction

Discovery forbids speculative universalization.

A generalized component should normally be extracted only after two real consumers need substantially the same mechanical invariant.

Examples of mechanics that may be candidates:
- exact subject identity;
- CAS/fencing;
- idempotency/effect reconciliation;
- immutable receipts;
- source snapshots/custody;
- neutral message envelopes;
- base + overlay reconstruction.

Examples that should remain project-owned unless extraordinary evidence says otherwise:
- epistemic admission;
- cognition semantics;
- scientific hypotheses/evaluators;
- relationship/identity semantics;
- industrial diagnostic meaning;
- project-specific authority.

## 6. Success metric

The goal is not fewer repositories.

The goal is:

**less duplicated machinery + clearer ownership + preserved independence + smaller blast radius.**

If a consolidation reduces repository count but increases semantic ambiguity or coupling, Discovery should call it a failure.
