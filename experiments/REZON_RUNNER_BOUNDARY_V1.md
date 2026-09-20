# Rezon ↔ Project Runner Mechanical Boundary Experiment V1

Status: **EXPERIMENTING / REAL MECHANICAL INTEROP / EPISTEMIC AUTHORITY RETAINED**

## Question

Can Rezon hand a bounded mechanical verification task to Project Runner without
making Runner understand or decide Rezon truth, admission, qualification,
currentness, authority, or semantic correctness?

## Exact subjects

Rezon producer:

- PR #79 / R51
- head `8289914ec500a1392b10fe1a3774dee166e73b40`
- exporter `src/rezon/interop.py`
- exporter blob `e365fd637904d4402891839ab1e187e50694e96b`

Project Runner verifier:

- PR #26
- head `4de0f6148b3d7d04ccdb4e0057435fa0d904590a`
- verifier `runner/rezon_evidence.py`
- verifier blob `d7827dec743e69fff7f981d91d7a86f6cd4a4839`

## Real producer evidence

A deterministic Rezon run was executed directly from the exact R51 source under
an already-installed Python 3.12 interpreter. No package installation was used.

The resulting export is real `rezon.run-evidence.v1`:

- effect state: `plan`;
- execution count: 1;
- evidence digest:
  `98bca73ae71697601cd7c9c10e2067cd8fef83aa58e7bad2f1fec59c18508c48`.

The local Windows writer produced CRLF bytes. GitHub persistence uses LF. The
experiment records both hashes separately instead of pretending they are the
same file representation.

Fresh producer verification:

- focused export tests: **10/10 PASS**;
- full Rezon tests: **275/275 PASS**.

This is local exact-source evidence. There is no hosted workflow attached to the
Rezon R51 final head.

## Independent Runner verification

Project Runner does not import Rezon.

It independently verifies only:

- exact schema;
- canonical body SHA-256;
- receipt/trace execution identity;
- ordered source-version binding;
- trace-failure coverage by receipt summary;
- output-digest binding;
- producer-ID binding as exported;
- task-envelope-digest binding;
- PLAN-only effect state.

It deliberately does not recompute the Rezon canonical producer-ID formula and
does not interpret accepted/rejected/unresolved claims.

A successful mechanical check returns only:

`STRUCTURALLY_VALID_NON_PROMOTIONAL`.

Hosted Runner qualification on exact head:

- workflow `35517367117`: SUCCESS;
- **222/222 PASS**;
- registry validation: **15 projects / 12 workers**;
- M6 recursive restart proof: PASS.

## Hostile semantic boundary

A regression modifies:

- accepted claim IDs;
- rejected claim IDs;
- unresolved IDs;
- `claim_disposition_complete`;

then recomputes the evidence digest.

Runner still accepts the export mechanically.

That is intentional evidence that Runner does not make Rezon epistemic
decisions.

By contrast, forged digest, source-version mismatch, concealed trace failure,
unknown schema fields, and non-PLAN effect state fail closed.

## Failed predecessor evidence

Two Runner heads failed before the final PASS:

1. the first fixture binding conflated Windows CRLF source bytes with the LF
   bytes persisted in GitHub;
2. the first provenance repair accidentally wrote literal escaped newlines into
   the Python test source.

Both failures are retained as exact provenance rather than erased.

## Result

Established:

`REAL_REZON_EXPORT + INDEPENDENT_RUNNER_MECHANICAL_VERIFICATION`

with:

`EPISTEMIC_AUTHORITY_RETAINED_BY_REZON`.

Not established:

- Rezon truth or admission;
- Rezon qualification/currentness/authority;
- Project Runner authority over Rezon;
- external-effect authorization;
- live Rezon execution through Runner;
- real failure-path interoperability;
- net maintenance savings;
- `PROVEN_REUSABLE`.

## Next falsifier

Generate a **real Rezon failure-path PLAN export** from exact source and feed it
through the same Runner verifier.

The failure must remain mechanical evidence. Runner must not convert structural
verification into admission, completion, truth, or external-effect authority.
