# Discovery Lifecycle Validation V1

Status: SOURCE CONTRACT

Discovery candidates are architecture hypotheses, not authority records. Candidate status must therefore fail closed against self-promotion.

The validator enforces:

- at least two distinct consumer repositories;
- exact 40-hex consumer subjects before a candidate becomes active;
- no placeholder/TBD consumers in EXPERIMENTING or PROVEN_REUSABLE states;
- nonempty promotion evidence for active candidates;
- a hostile review before EXPERIMENTING;
- at least two integration-evidence entries and a clean hostile PASS before PROVEN_REUSABLE;
- no unresolved critical objections on PROVEN_REUSABLE;
- duplicate candidate IDs fail closed.

This is deliberately narrower than a universal architecture validator. It does not decide whether a shared substrate should exist. It only prevents the repository from asserting lifecycle promotion without the evidence required by Discovery Protocol V1.
