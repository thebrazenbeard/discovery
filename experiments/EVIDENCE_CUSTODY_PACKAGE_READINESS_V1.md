# Evidence custody package readiness V1

Status: **FIRST TASK NOT CLOSED / SOURCE REPAIR PRESENT / PLATFORM CONTRACT BLOCKED**

Discovery's `EVIDENCE_CUSTODY_INTERCHANGE_V1` explicitly required one thing before reuse could be judged:

> make the candidate custody implementation a truthful, installable package.

An authenticated private-source review now provides enough evidence to test that gate without publishing the private implementation identity or exact ref.

## Current private main

The private implementation is real and substantial, but its current main package metadata is not a truthful reusable distribution. The source package contains stale unrelated package/build/CLI metadata alongside the actual custody package.

That means the candidate cannot be promoted merely because its storage/custody code exists.

## Active package repair

A private source repair exists and is materially correct at source scope. It:

- gives the package a truthful custody-package identity;
- removes inherited runtime dependencies not used by the source;
- narrows wheel, CLI, and type-check targets to the actual package;
- defines a narrow public API;
- states explicitly that custody mechanics do not decide downstream truth, authority, privacy, currentness, or acceptance;
- defines package CI for clean install, compile, tests, lint, typing, build, import/CLI smoke, and diff-check.

A later private consolidation subject carries the same package blobs unchanged.

So:

`TRUTHFUL_PACKAGE_METADATA = PASS_AT_SOURCE_SCOPE`

## Installability gate

General installability is **not established**.

Independent source execution on declared-compatible Python collected 103 tests on Windows:

- 47 passed;
- 56 failed.

The failures were dominated by two portability classes:

1. a frozen benchmark receipt is byte-sensitive to checkout line endings;
2. export/import custody paths intentionally require a POSIX no-follow filesystem primitive unavailable on Windows.

The second behavior is fail-closed and therefore not a custody-security failure. The defect is the support contract: the package currently declares Python 3.11+ without an OS/platform ceiling while major custody paths are intentionally unsupported on Windows.

Hosted package CI also does not close the gap. Current private package workflow runs fail before executable steps are exposed, so they are:

`PRE_STEP_NO_EXECUTION`

not package test failures, but also not qualification passes.

## Result

`FIRST_TASK_NOT_CLOSED_SOURCE_REPAIR_PRESENT_PLATFORM_CONTRACT_BLOCKED`

The candidate remains **HYPOTHESIS**.

Discovery should not look for a reusable first consumer until package readiness is truthful. The private owner lane can close the gate by either:

- declaring and qualifying a narrow supported POSIX platform/filesystem contract, plus making frozen artifacts checkout-stable; or
- implementing and qualifying equivalent safe Windows custody semantics.

After that, clean install/test/lint/type/build/import/CLI qualification must execute on the exact repaired subject.

> **HOSTILE REVIEWER:** A package can be semantically neutral and still be operationally dishonest if its declared support surface is broader than what its core custody paths can execute.

That is the present blocker.

No private repository identity or exact ref is published here. No release, installation, deployment, global evidence store, or downstream truth/authority transfer follows.
