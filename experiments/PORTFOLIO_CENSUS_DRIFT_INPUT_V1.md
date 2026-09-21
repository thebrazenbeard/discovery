# Portfolio Census Drift Input Experiment V1

Status: **EXPERIMENTING / PARTIAL SUPPORT / NO REUSE PROMOTION**

## Question

Can one exact, privacy-safe Discovery census artifact replace duplicated repository-set
enumeration/currentness bookkeeping across independent consumers without becoming a
shared runtime registry or portfolio authority?

## Provider subject

Discovery census:

- exact source: `vera/discovery-shared-substrate-v1@1316094edbed17fa5918b70793c95ffddfcf92ea`
- path: `portfolio/PORTFOLIO_CENSUS_V1.json`
- Git blob: `34cd2ab55d46f5a1ecc2c894f3e8cfdb8afa41df`
- total repositories: 57
- all-name SHA-256: `43dfda1fa3dd24dec39e2aa345d93ab192dbda777433feae384da632b3d008dd`
- hosted validation: run `35475731990` SUCCESS

## Consumer A — public

Project Runner source experiment:

- exact subject: `work/discovery-census-consumer-v1-20260920@b763c707abacc7dfe30dc451b2b42354a30e3621`
- implementation validates the exact Discovery Git blob bytes before trusting count/digest;
- exact hosted workflow run `35509678751`: SUCCESS;
- Project Runner continues to own its runtime registry and scheduling/authority semantics.

## Consumer B — private opaque

Public attestation only:

- handle: `PRIVATE_OPAQUE_f306bde2474eb046`
- consumer commitment: `f306bde2474eb04685b774c84de90b2377706df0a08b0a1c4ab9cb488cada6ef`
- subject commitment: `08855041acd5674d1b651080f1b971ae80e99e3e7125ae43b68692562e37cbf2`
- private receipt digest: `1be6377f5e125c4fca3da825824a57297dfbb16f8758fddc8bc2d17bc4ff2969`
- verifier class: `PRIVATE_OWNER_REGISTRY`
- status: `EXACT_PRIVATE_SUBJECT_ATTESTED`

The private preimage, repository identity, ref, nonce, and source path are not published here.

## Before / after

Before:
- consumers independently enumerate or remember repository-set state;
- census freshness can diverge silently between coordination surfaces.

Experiment:
- both consumers bind the same exact public-safe census artifact;
- each checks exact artifact identity/currentness before using its aggregate count/digest;
- each retains independent project semantics and can continue after obtaining verified bytes.

What is **not yet measured**:
- net maintenance reduction;
- refresh cadence cost;
- behavior under a real repository-count change after this 57-repository cut.

## Rejection / next falsifier

The next useful falsifier is an actual inventory change. On the next repository-set change,
both consumers should reject the stale digest and refresh to the same new Discovery census
without changing their project-owned registry semantics.

If either consumer instead needs Discovery-specific scheduling/authority semantics, or
requires Discovery live availability for normal operation, reject the shared mechanism.

## Claim ceiling

Current evidence supports:

`EXPERIMENTING / TWO_CONSUMER_INTEROPERABILITY_PRESENT / PRIVATE_CONSUMER_OPAQUE`

It does not support:

`PROVEN_REUSABLE / PORTFOLIO_AUTHORITY / RUNTIME_REGISTRY / REQUIRED_SHARED_SERVICE`.
