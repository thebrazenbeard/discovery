# Discovery baseline V2 hostile qualification — append-only research log

## Frozen question and confirmatory plan

Question: Does the public 81-repository Discovery observation provide sufficient independent evidence to admit a new baseline without rewriting the historical V1 census or defeating the two-observer admission gate?

Hypotheses (falsifiable):

- H1: A structurally valid public observation does not satisfy B0/B1 independence and signer requirements. Falsifier: an authenticated, independently sourced B0/B1 vector and authorized signer are recorded, bound to one observed inventory and live report.
- H2: The current validator rejects incomplete, stale, or logically inconsistent admission records. Falsifier: a targeted malformed fixture that exits successfully.
- H3: GitHub public repository listing is a temporally sampled observation, not proof that historical 97/93 records were wrong. Falsifier: a trusted immutable source proving historical inventory and current complete population are the same sampled set.

Methods: C1 inspect repository HEAD, schemas, tests, current receipt and provenance; C2 run native receipt validators and adversarial fixtures; C3 check GitHub REST paging/visibility official docs, match versioned API behavior; C4 independent evidence review by parent (review only, do not self-admit). Exploratory probes will be labeled E-series.

Stopping rules: conclude only at verified admit/not-admit boundary, or explicit inability to inspect required independent evidence. Preserve V1 unchanged. No production writes or baseline admission as part of this lane.

## Evidence log (append-only)

- E001: Local detached worktree created from `thebrazenbeard/discovery` commit `762742908bf80028185903cb774700a42988d67a` for isolated review; pre-existing untracked receipt artifacts in `discovery_v2_qualification` left untouched. `git worktree add --detach ... HEAD` exit 0.
- E002: `DISCOVERY_PUBLIC_IDENTITY_PROBE_20261028.json`: `jq` observed `B0_count=81`, `B1_count=81`, `bound_exact_subjects=81`, `archived=3`, one `subjects` vector of length 81, no `B0_subjects` or `B1_subjects`; `admission_state=UNREVIEWED_NOT_ADMITTED`, `not_admitted=true`; exit 0. This fails the independent full B0/B1 replay precondition, not necessarily the validity of GitHub inventory.
- E003: GitHub authoritative REST documentation via web search 2026-10-28: `https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repositories-for-a-user`, `https://docs.github.com/en/rest/branches/branches?apiVersion=2022-11-28#get-a-branch`, `https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api?apiVersion=2022-11-28`. Public owner repository endpoint can be unauthenticated, lists public repos; REST paging max 100, Link header carries next; branch gives commit SHA and nested tree. Version parameter matches repository's `2022-11-28` header. These claims do not guarantee complete archived/moved/private set completeness.
- E004: Confirmatory C2 red stage: `python -m unittest discover -s tests -p 'test_public_identity_full_vector_pair.py' -v`, exit 1 because `tools/validate_public_identity_vector_pair.py` did not exist (missing capability, not behavioral failure). Added first targeted source-only pair comparator and fixtures.
- E005: Confirmatory C2 green stage: same focused command exit 0 `Ran 7 tests ... OK`; all seven hostile cases (missing full B1, changed tree/id, repeated observation IDs, time overlap, profile mismatch, collection error, duplicate JSON keys/names, bool ID/empty branch) rejected. Source-only match returns `NOT_ADMITTED`.
- E006: Regression C2: `python -m unittest discover -s tests -p 'test_*.py'` exit 0 `Ran 189 tests in 1.584s / OK`. V1 freeze tests still pass. No external deployment or GitHub branch write attempted.

## Provisional verdict

H1 supported by E002 and schema controls E004/E005; `NOT_ADMITTED`. H2 partial: new paired-vector structural check passes hostile local fixtures, but cannot independently authenticate provider/collectors/signers. H3 remains a limitation under source API and sampling (E003): prior historical counts must remain preserved as observations from different dates/visibility scopes, not retroactively overwritten. C4 independent external review pending; confirmatory source-only work cannot become admitted solely by author review.

## Hostile reviewer follow-up (plan unchanged)

- E007: Independent reviewer correctly observed that two byte-identical *truncated* vectors satisfy pair equality, so `EXACT_VECTOR_PAIR_MATCH_SOURCE_ONLY` implied unjustified completeness. Reproduced with two one-subject arrays; a new targeted test initially failed, red output `FAIL... 'PAIR_EQUIVALENCE_ONLY' != 'EXACT_VECTOR_PAIR_MATCH_SOURCE_ONLY'`, exit 1. This is a new exploratory challenge/repair, not a retroactive confirmatory success.
- E008: Changed unanchored result to `PAIR_EQUIVALENCE_ONLY` and added optional `--anchor` membership reference, requiring its count/archive/digest self-consistency plus exact equality with both B0/B1 tuples. Supplied reference remains untrusted and not admitted. Focused command exit 0 `Ran 9 tests ... OK`, including equal-truncated-pair downgrade and externally anchored truncation rejection.
- E009: Real captured `../DISCOVERY_PUBLIC_IDENTITY_PROBE_20261028.json` supplied to `_checked_anchor` returns `81`, exit 0. This proves only the file is structurally self-consistent; it is not a second observation or authenticated provenance.
