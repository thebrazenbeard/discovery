# Full-vector B0/B1 structural comparison — not admission

Discovery cannot use matching B0/B1 **counts** or a digest of just one vector to prove a two-observation baseline. The 2026-10-28 public 81-repository receipt contains a single subject vector, two counts, three archived subjects, and summary flags. It does **not** contain two complete B0/B1 vectors; no validator can reconstruct the second vector after the fact.

The standalone read-only comparator in `tools/validate_public_identity_vector_pair.py` accepts two externally captured files:

```sh
python tools/validate_public_identity_vector_pair.py /path/to/B0.json /path/to/B1.json
python tools/validate_public_identity_vector_pair.py /path/to/B0.json /path/to/B1.json --anchor /path/to/complete-observed-inventory.json
python -m unittest discover -s tests -p 'test_public_identity_full_vector_pair.py' -v
```

Each file must be a `DISCOVERY_PUBLIC_IDENTITY_VECTOR_V1` object for `thebrazenbeard` with `observation_id`, UTC `started_at_utc` and `ended_at_utc`, `source_profile_sha256`, an empty `errors` array, and a **complete** sorted `subjects` array. Each subject must contain unique positive integer GitHub `id`, name, branch, exact lowercase 40-hex Git commit `head` and `tree`, and boolean `archived`.

The comparator rejects duplicate JSON keys, missing/invalid subjects, mismatched repo IDs, membership, commit/tree, archive state, different source profile digests, repeated observation IDs, overlapped/reversed observation intervals, or collection errors. Matching B0/B1 inputs without a reference return **`PAIR_EQUIVALENCE_ONLY`**: even two identical one-repository arrays cannot prove they are complete.

The optional `--anchor` input binds both vectors to a separately supplied full membership reference with a self-consistent subject count, B0/B1 count, archive count, and subject digest. That binding rejects equal but truncated input vectors *relative to the supplied anchor*. The 2026-10-28 public identity probe is accepted as a reference and its 81 subject entries pass anchor structural checks. Passing with an anchor returns **`PAIR_MATCHES_SUPPLIED_ANCHOR_ONLY`**; the anchor is still untrusted input, **not** independent completeness, provenance, or admission evidence. A future canonical inventory can be passed without hard-coding the count 81 into software.

**Important limits:** Distinct strings in `observation_id` do not authenticate distinct collectors. The comparator does not validate who created either input, whether a GitHub API response was genuine, whether the declared profile digest matches a reviewed source/profile, whether the second capture was independent, whether renamed/deleted/inaccessible repositories were properly classified, or whether a qualified signer admitted a baseline. Every success therefore explicitly returns `admission: NOT_ADMITTED` and independent signer/collection `NOT_ATTESTED`.

Historical V1 blobs and prior source statements remain immutable. A new qualified baseline requires new live, independently recorded full B0/B1 inputs, signed source/policy/profile bindings, redirect and transition dispositions, independent review, and a separate authorized admission step. The old 81-repository receipt cannot be retroactively promoted.

Primary external contract checked 2026-10-28, GitHub REST API version `2022-11-28`: [List repositories for a user](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repositories-for-a-user); [Get a branch](https://docs.github.com/en/rest/branches/branches?apiVersion=2022-11-28#get-a-branch); [REST pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api?apiVersion=2022-11-28). These document API field/paging behavior, **not** proof that any particular local 81-repo receipt came from GitHub.
