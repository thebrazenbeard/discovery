# Portfolio Snapshot + Currentness Pipeline V1

Status: **IMPLEMENTED READ-ONLY CANDIDATE / NO PROJECT AUTHORITY**

Parent architecture:

`vera/discovery-architecture-observatory-v1-20260922@2f26e5f5b8ba3c29f0fbe3d4854ebac7b94065c6`

## Problem closed

Discovery previously validated portfolio census artifacts more strongly than it produced them.

The current public census also carries deterministic SHA-256 digests of private/all repository-name sets. Those digests are useful for change detection but are not inherently privacy-preserving because repository names can be low-entropy and guessable.

This pipeline adds a first read-only ingestion/currentness implementation without changing project runtime state.

## Builder

`tools/build_portfolio_snapshot.py`

The builder can consume either:

- a live authenticated read-only GitHub inventory; or
- an authorized offline JSON inventory.

Public repositories are emitted with:

- repository name;
- default branch;
- exact branch-head commit;
- exact Git tree;
- archived state.

Private repository names are never emitted.

Public repository-name currentness uses deterministic SHA-256 because those names are already public and the digest is intended to be independently recomputable.

Private and all-repository set currentness use:

`HMAC_SHA256_PRIVATE_KEY_CANONICAL_V1`

with separate domain prefixes.

The key is supplied at execution time through `DISCOVERY_PRIVATE_CENSUS_KEY_HEX` and is never written into the snapshot.

A stable public `key_id` permits comparison only when the same secret commitment key was used. Key rotation therefore fails closed instead of pretending two commitments are comparable.

## Comparator

`tools/compare_portfolio_snapshots.py`

The comparator identifies:

- public repository additions/removals;
- public default-branch movement;
- public exact commit/tree movement;
- archive-state movement;
- count movement;
- private-set commitment movement;
- all-set commitment movement;
- commitment-key changes that make private currentness unprovable.

Any such movement marks the old snapshot:

`STALE`

relative to the new snapshot.

Historical evidence remains valid as historical evidence. The comparator does not infer why a repository moved, whether the change is good, or whether another repository must be changed.

## Privacy correction

The existing census V1 deterministic private/all-name digests are not rewritten by this branch. They remain historical artifacts.

Future public-safe snapshots should prefer keyed commitments because Discovery's own private-consumer threat model already recognizes the weakness of unsalted hashes over a small portfolio namespace.

> **HOSTILE REVIEWER:** You're calling HMAC a privacy fix, but the secret key becomes a new critical asset.

Correct. The public repository never stores or manages the key. Loss of the key affects continuity of private-set comparison, not project operation. Key rotation is surfaced as `KEY_CHANGED_OR_UNCOMPARABLE`, which invalidates currentness rather than silently transferring trust.

> **HOSTILE REVIEWER:** A stable key identifier fingerprints the secret across snapshots.

Correct, but the identifier is a truncated SHA-256 over a domain-separated high-entropy key, not a repository name or reversible private identifier. Its sole purpose is to determine whether two HMAC commitments are comparable. If even that cross-snapshot linkage is unacceptable in a future threat model, the key-id field should be removed and private currentness treated as externally verified instead.

> **HOSTILE REVIEWER:** The live GitHub reader still sees private repository names in process memory.

Correct. Privacy here is about the public artifact, not magical blindness of the authorized acquisition process. Live inventory collection necessarily observes repository metadata available to its token. Execution therefore belongs in an authorized private environment; only the sanitized snapshot is suitable for publication.

> **HOSTILE REVIEWER:** Exact public commit/tree snapshots still do not tell you whether a project meaningfully changed.

Correct. This pipeline establishes source currentness only. Semantic or behavioral impact is a later detector/experiment concern.

> **HOSTILE REVIEWER:** A snapshot engine can become a polling dependency that projects start waiting on.

Forbidden by the parent architecture. Projects never wait for Discovery. Discovery refreshes its own observations and may declare its own claims stale.

> **HOSTILE REVIEWER:** You still have no proof that automating census refresh saves enough work to justify maintaining this code.

Correct. This implementation earns permanence only if repeated refreshes and downstream invalidation consume less maintenance than manual portfolio reconstruction or catch stale evidence that would otherwise survive. That remains an empirical gate.

## Usage

Offline authorized inventory:

```bash
export DISCOVERY_PRIVATE_CENSUS_KEY_HEX="<high-entropy-hex-key>"
python tools/build_portfolio_snapshot.py \
  --owner thebrazenbeard \
  --input-json inventory.json \
  --output snapshot.json
```

Live read-only GitHub inventory:

```bash
export GITHUB_TOKEN="<read-only-authorized-token>"
export DISCOVERY_PRIVATE_CENSUS_KEY_HEX="<high-entropy-hex-key>"
python tools/build_portfolio_snapshot.py \
  --owner thebrazenbeard \
  --output snapshot.json
```

Compare two snapshots:

```bash
python tools/compare_portfolio_snapshots.py old.json new.json
```

No credential, token, private name, or generated private preimage belongs in source control.

## Tests

`tests/test_portfolio_snapshot_pipeline.py` covers:

- no private-name publication;
- mandatory keyed commitment when private repositories exist;
- domain separation;
- deterministic public digest;
- exact public subject validation;
- duplicate-repository rejection;
- public head/tree movement invalidation;
- private-set change invalidation without identity disclosure;
- key rotation failing closed;
- public repository-set movement.

## Claim ceiling

`READ_ONLY_SNAPSHOT_AND_CURRENTNESS_PIPELINE / PUBLIC_SAFE_OUTPUT / PRIVATE_SET_KEYED_COMMITMENT / NO_PROJECT_AUTHORITY / NO_AUTOMATIC_REPAIR / NO_RUNTIME_DEPENDENCY`
