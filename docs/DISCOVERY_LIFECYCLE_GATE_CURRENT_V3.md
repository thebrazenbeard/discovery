# Discovery Lifecycle Gate — Current Source V3

Status: SOURCE CANDIDATE / CURRENT-BASE QUALIFICATION REQUIRED

This successor binds lifecycle promotion checks directly into Discovery's current structural validator rather than maintaining a second parallel validator.

## Exact subject syntax

Active candidates (`EXPERIMENTING` or `PROVEN_REUSABLE`) must bind each consumer to an exact subject using either:

- bare 40-hex commit SHA; or
- `refname@40hex`.

The second form matches current Discovery experiments such as `main@<sha>` and experiment-branch `<branch>@<sha>` while preserving exact immutable commit identity.

Placeholder repositories and null/non-exact refs fail closed for active candidates.

## Lifecycle evidence

`EXPERIMENTING` requires:
- at least two distinct real consumers;
- exact consumer subjects;
- nonempty promotion evidence;
- a hostile review that has actually run.

`PASS_WITH_LIMITS` plus explicit objections is permitted at this stage because the current Runner↔WIP experiment is intentionally `PARTIAL_SUPPORT_NARROWED`, not proven reuse.

`PROVEN_REUSABLE` additionally requires:
- at least two evidence records;
- hostile status exactly `PASS`;
- zero critical objections.

Schema conditionals mirror those machine rules.

## Boundary

These gates validate lifecycle bookkeeping. They do not prove any shared architecture correct and do not make Discovery a central portfolio authority.
