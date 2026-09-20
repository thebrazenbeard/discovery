# Discovery Private Consumer Attestation V1

Status: SOURCE CANDIDATE / PRIVACY-PRESERVING EXPERIMENT BINDING

## Problem

Discovery is a public architecture-research repository. The current census contains 57 repositories, of which 45 are private.

The lifecycle gate correctly requires active experiments to bind real consumers to exact subjects. Publishing raw private repository names and exact refs in a public candidate would violate Discovery's own privacy rule.

The wrong repair would be to weaken exactness.

## V1 mechanism

An active private consumer is represented publicly by:

- `visibility: PRIVATE_OPAQUE`;
- an opaque handle `PRIVATE_OPAQUE_<first-16-hex-of-consumer-commitment>`, mechanically derived rather than human-named;
- `ref: null`;
- `private_attestation.schema = DISCOVERY_PRIVATE_SUBJECT_ATTESTATION_V1`;
- `commitment_scheme: SHA256_PRIVATE_NONCE_CANONICAL_V1`;
- `consumer_commitment_sha256`: commitment to stable private consumer identity;
- `subject_commitment_sha256`: commitment to the exact private source subject;
- `receipt_sha256`: digest of the private verification receipt;
- `verifier_class`: `PRIVATE_OWNER_REGISTRY` or `INDEPENDENT_PRIVATE_REVIEWER`;
- `status: EXACT_PRIVATE_SUBJECT_ATTESTED`.

The public repository does not contain the private preimages.

The commitment preimages MUST be domain-separated canonical private records containing at least 128 bits of high-entropy nonce material retained only in the private governed domain. Direct unsalted hashes such as `SHA256(repository_name)` or `SHA256(repository@ref)` are forbidden because the portfolio is small enough for dictionary attacks. Consumer, subject, and receipt commitments must be distinct digests.

## What the public validator can and cannot establish

It can establish:

- the candidate did not publish a raw private ref through the consumer object;
- digest fields have exact SHA-256 shape;
- active opaque consumers carry an attestation;
- two opaque consumer identities are distinct by consumer commitment;
- the same commitment can be tracked across candidate revisions.

It cannot establish from the public artifact alone:

- the hidden repository identity;
- that the private receipt is truthful;
- that two private repositories are operationally independent;
- that the exact hidden source really produced the claimed behavior.

Therefore V1 allows an opaque private consumer in `EXPERIMENTING`, where private evidence may be inspected in its governed domain, but rejects any `PROVEN_REUSABLE` candidate containing an opaque private consumer.

## Why PROVEN_REUSABLE fails closed

A hash commitment prevents publication leakage; it is not independent verification.

Promotion requires a later mechanism that lets Discovery establish materially independent real consumers without disclosing their identities. Candidate future mechanisms include independently signed public-safe attestations or a verifier receipt protocol, but V1 does not choose or authorize one.

## Authority boundary

The attestation proves no project authority, runtime activation, install, merge, provider state, identity transfer, or semantic equivalence. Private projects remain authoritative for their own semantics and evidence.
