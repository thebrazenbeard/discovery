# Effect Envelope Maintenance Accounting V1

Status: **MEASURED BURDEN / ECONOMIC VALUE NOT ESTABLISHED**

This experiment now has the second independent observer required by the prior
frontier. The result is useful precisely because it does **not** support a
premature reuse promotion.

## What exists

Three independently qualified producer adapters:

- Project Runner: 177 physical lines;
- WIP: 138 physical lines;
- DriftGuard: 186 physical lines.

Producer-adapter total: **501 physical lines**.

Two independent source-agnostic observers:

- public Discovery observer: 234 physical lines;
- second private observer: 216 physical lines.

Observer total: **450 physical lines**.

Contract distribution:

- canonical V0 schema: 72 physical lines;
- one exact private vendored copy: 72 physical lines.

Core experiment surface including the private schema copy:

**1,095 physical lines / 966 nonblank lines / 95 branch lines.**

Five adapter/observer regression files add:

**804 physical lines / 707 nonblank lines.**

Total measured source + test surface:

**1,899 physical lines.**

## What was actually removed

No pre-existing source-specific parser implementation was deleted by either
observer.

Actual parser LOC removed:

**0**

Actual parser files removed:

**0**

That matters. A claim of net maintenance savings would currently be false.

## What was actually avoided

Both observers consume the same three current producer classes without
source-specific parser branches.

Measured integration points avoided:

**3 producers × 2 observers = 6 producer-specific parser integrations avoided.**

Both observer designs also accept an unknown future V0 producer without a
registration/code change.

That is genuine reuse evidence, but it is **avoided future integration surface**,
not demonstrated deletion of existing maintenance burden.

## Private second observer evidence

The second observer is represented publicly only through its privacy-safe
attestation:

- handle: `PRIVATE_OPAQUE_18f99857cf7f2beb`;
- consumer commitment:
  `18f99857cf7f2bebcbc94921c741784344d89e944bbcc8a8980a2ab7e7ba82ad`;
- subject commitment:
  `5ceed353b05144f9a754b747c9e34ff18829ac2de7aaf5b41f7493be10ecf31e`;
- receipt:
  `ed2f5146620dfd5623b1caa805976afc414e2aad34aa7ac25510cee0a50b60e8`.

Its source-level behavior check is PASS. Hosted CI is explicitly
`NOT_EXECUTED`; this accounting does not promote it to hosted qualification.

## Economic result

Current result:

`INTEROPERABILITY_AND_TWO_OBSERVER_PARSER_REUSE_DEMONSTRATED`

but:

`ECONOMIC_REUSE_VALUE_UNPROVEN`.

The experiment has introduced more than one thousand lines of core source
surface and removed zero existing parser lines. Six future parser integrations
have been avoided, which may become valuable as more consumers appear, but that
future value has not yet amortized the measured adapter/schema burden.

Therefore:

- remain `EXPERIMENTING`;
- do not promote to `PROVEN_REUSABLE`;
- do not create a mandatory shared runtime library;
- do not make Discovery a runtime dependency.

## Next meaningful falsifier

Do not add another observer merely to increase the count.

The next useful test is to find a **real existing workflow with source-specific
effect parsing** and replace that parsing with V0 while preserving all native
semantics. Only then can Discovery measure actual removed maintenance surface
against the adapter/schema burden already incurred.

If no such real consumer exists, the correct conclusion is that the envelope is
interoperable but not presently worth further centralization.
