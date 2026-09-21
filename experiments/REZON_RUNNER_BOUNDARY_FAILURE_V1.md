# Rezon ↔ Project Runner Failure-Path Experiment V1

Status: **EXPERIMENTING / REAL FAILURE PATH / UNCHANGED MECHANICAL VERIFIER**

The first Rezon↔Runner experiment proved that a real successful PLAN export could
be mechanically verified without transferring epistemic authority.

This successor tests the harder case: a real Rezon contract failure.

## Exact Rezon failure export

Producer:

`thebrazenbeard/rezon@8289914ec500a1392b10fe1a3774dee166e73b40`

Evidence digest:

`516146d1f01291510e5b31e645520ed5434760ff953139d6aba71ea4cc37e752`

The exact export contains:

- `effect_state=plan`;
- one execution;
- trace failure `contract_violation`;
- receipt failure `contract_violation`;
- no canonical output digest;
- no canonical producer ID;
- one unresolved invalid-contract marker.

## Unchanged Project Runner verifier

Failure-path consumer:

`thebrazenbeard/project-runner@b48e2a19fa9e26eac233d1813ee04346e96b68a7`

The production verifier remains exact Git blob:

`d7827dec743e69fff7f981d91d7a86f6cd4a4839`.

No production verifier change was required after the successful-path experiment.

Exact hosted qualification:

- workflow `35517665284`: SUCCESS;
- **228/228 tests PASS**;
- registry validation: **15 projects / 12 workers**;
- M6 recursive restart proof: PASS.

## Failure semantics remain Rezon-owned

The Runner verifier requires every trace failure to be covered by the receipt
failure summary.

It does not interpret the failure token.

A hostile regression changes both values to an unknown future Rezon failure
string, rehashes the evidence, and the unchanged verifier accepts it.

Therefore the shared contract is:

`FAILURE_COVERAGE_AND_BINDING`

not:

`SHARED_FAILURE_ONTOLOGY`.

The same applies to Rezon's unresolved markers: Runner preserves them as opaque
source evidence and exposes no completion/admission/truth field.

## Result

Established:

`REAL_SUCCESS_AND_FAILURE_PATH_MECHANICAL_INTEROP_WITH_UNCHANGED_VERIFIER`.

Not established:

- shared Rezon/Runner failure semantics;
- Rezon truth, admission, or qualification;
- Runner completion authority over Rezon;
- external-effect authorization;
- mandatory Runner dependency;
- net maintenance reduction;
- `PROVEN_REUSABLE`.

## Disposition

The core Rezon↔Runner boundary has survived both success and failure paths.

Do not keep expanding the pair merely to accumulate examples.

Pause this candidate at `EXPERIMENTING` until either:

1. a second materially independent outer consumer needs the same Rezon evidence
   contract; or
2. real duplicated verification code exists that this boundary can measurably
   remove.
