> **License:** Source-visible, **not open source**. The original code and documents are proprietary. Private noncommercial evaluation and research are permitted under [LICENSE](LICENSE); redistribution, commercial use, and hosted services require separate written permission. See [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Third-party materials retain their own licenses.

# Discovery — portfolio capability and integration research toolkit

Discovery is a set of Python utilities, evidence contracts, and review protocols for understanding a portfolio of software repositories. It helps maintainers take repeatable snapshots, detect changes, investigate possible duplication, and evaluate whether a capability should remain independent or become shared infrastructure.

**Implemented today:** source-side portfolio snapshots and comparisons, public-currentness checks against pinned historical evidence, overlap/reconciliation validators, candidate records, and bounded effect-envelope observation. **Not implemented:** a general-purpose repository crawler service, an automatic refactoring engine, an authorization service, or deployment of discovered capabilities to a host.

The working method is **discover → classify → experiment → verify → hand off**. A shared abstraction must earn promotion through independent consumers, demonstrable simplification, semantic ownership, rollbackability, and hostile review. A source match, validated receipt, or passing unit test is evidence for a narrow claim—not permission to merge, deploy, or act.

## Available tools

| Tool or artifact | What it actually does | Important limit |
| --- | --- | --- |
| [`build_portfolio_snapshot.py`](tools/build_portfolio_snapshot.py) | Builds a public-safe snapshot from authorized local JSON inventory or an authenticated GitHub owner inventory | Reads inventory; does not classify correctness or grant rights. Private-set commitments require a caller-held key |
| [`compare_portfolio_snapshots.py`](tools/compare_portfolio_snapshots.py) | Compares two snapshot files and reports public subject, membership, and private-set drift | Relative currentness only, not cause or architectural authority |
| [`check_public_currentness.py`](tools/check_public_currentness.py) | Checks the checked-in, historically pinned public observatory against live GitHub state | The checked-in public cut is not the entire present-day portfolio |
| [`trace_public_impact.py`](tools/trace_public_impact.py) | Finds dependent repository artifacts referencing outdated exact-source IDs | Affected-file lead list, not automated repair |
| [`refresh_public_blob_evidence.py`](tools/refresh_public_blob_evidence.py) | Reproduces or explicitly regenerates pinned public Git blob evidence (`--check` / `--write`) | `--write` mutates evidence artifacts; use only with a reviewed currentness plan |
| [`effect_observer.py`](tools/effect_observer.py) | Validates and summarizes producer-selected effect-envelope records | Cannot independently prove a host effect occurred or identify an authorized actor |
| [Candidate protocol](docs/DISCOVERY_PROTOCOL_V1.md) and [classification](docs/CLASSIFIER_PROTOCOL_V1.md) | Define evidence-qualified promotion states and falsification questions | Research/review contracts; not an executable consolidation engine |

The historical [implementation planner](tools/plan_vera_vcp_implementation.py) consumes a specific Vera/Vera Control Plane registry. It is an **optional project-specific integration experiment**, not a requirement or capability available for arbitrary hosts.

## Quick start: work with an inventory you are authorized to inspect

Python 3.12 is used by the repository's validation workflow. The tools are stand-alone scripts and do not require installing a published package. In a checkout:

1. Provide a JSON list of repository records at `inventory.json`. A synthetic public-only example has this shape (the object IDs below are illustrative, not real Git references):

   ```json
   [
     {
       "name": "sample-library",
       "visibility": "public",
       "archived": false,
       "default_branch": "main",
       "head_sha": "1111111111111111111111111111111111111111",
       "tree_sha": "2222222222222222222222222222222222222222"
     }
   ]
   ```

2. Build and compare snapshots:

   ```bash
   python3 tools/build_portfolio_snapshot.py \
     --owner sample-organization --input-json inventory.json \
     --observed-at 2026-01-01T00:00:00Z --output snapshot-a.json
   python3 tools/compare_portfolio_snapshots.py snapshot-a.json snapshot-a.json
   ```

   Comparing a snapshot to itself is a **format demonstration**, not proof that a repository is current. For useful drift checks, acquire a second independently observed inventory at a later time.

3. Run local validation:

   ```bash
   python3 tools/validate_discovery.py
   python3 tools/validate_reconciliation.py
   python3 -m unittest discover -s tests -q
   ```

The snapshot builder also supports authorized live GitHub inventory acquisition using a caller-supplied token from `GITHUB_TOKEN` (or `--token-env`). Do not put tokens in tracked files, command arguments, or public receipts. If private repository records are present, the builder requires a separately supplied private-census HMAC key through `DISCOVERY_PRIVATE_CENSUS_KEY_HEX` (or `--private-key-env`). It does not publish private names in the public snapshot; **a digest or HMAC commitment is not a privacy review**.

See the [snapshot pipeline](docs/PORTFOLIO_SNAPSHOT_PIPELINE_V1.md) and [currentness/reconciliation contract](docs/CURRENTNESS_AND_RECONCILIATION_V1.md) for input rules and claim ceilings.

## Candidate decisions and evidence

The research lifecycle is `OBSERVED → HYPOTHESIS → EXPERIMENTING → PROVEN_REUSABLE`. A candidate may also become `PROJECT_SPECIFIC`, `REJECTED`, or `SUPERSEDED`. `PROVEN_REUSABLE` means only that the examined reuse claim survived the stated test; a separate owner must authorize code changes, installation, runtime access, and effects.

The repository contains checked-in experimental evidence for overlapping source trees, registry handoffs, transport/evidence interfaces, and competing integration designs. These are historical observations tied to **exact source commits**, not endorsements of a current portfolio architecture. In particular:

- [September 2026 public/private portfolio census](portfolio/PORTFOLIO_CENSUS_V2.json) is a dated 71-repository observation, **not** a live or authoritative current total.
- [V1 public observatory](docs/DISCOVERY_ARCHITECTURE_OBSERVATORY_V1.md), [blob reproducibility](docs/PUBLIC_BLOB_REPRODUCIBILITY_V1.md), and [relationship graph](portfolio/PUBLIC_RELATIONSHIP_GRAPH_V1.json) are bound to their older public cut. Their 23-source/253-pair measurements must not be generalized to the current estate.
- [Public intake](docs/PUBLIC_SUBJECT_INTAKE_20260921_V1.md) and [research experiments](experiments/) retain historical provenance and negative controls. A byte-identical blob does not alone establish lineage, intended ownership, or permission to consolidate.
- [Implementation-engine protocol](docs/DISCOVERY_VERA_VCP_IMPLEMENTATION_ENGINE_V1.md) illustrates a specific consuming ecosystem; future adopters can apply the principles without inheriting that ecosystem's identities or authority.

## Security and deployment boundaries

- **Read-only by default:** Inventory, comparison, and validation do not confer write authority. The explicit blob-evidence `--write` path is separate and requires review.
- **No host authorization service:** Tools neither authenticate providers nor bind immutable subject identities, consent, or effect permissions. A consuming host must enforce those controls independently.
- **No independent effect attestation:** The envelope observer reads records selected by a producer. Its report does not prove external execution, consent, or custody.
- **No exhaustive privacy guarantee:** Public-safe snapshots suppress private *names*, but repository metadata, timing, hashes, and other artifacts may still disclose information. Check your disclosure and license obligations before publishing.
- **Historical source-execution hazard:** A concealed VS Code `folderOpen` launcher and disguised font-path loader were removed from this source tree. [`test_editor_startup_source_guard.py`](tests/test_editor_startup_source_guard.py) checks the current source for regressions. This is **not** forensic evidence that an earlier checkout or any workstation was uncompromised.

Use [`discovery-validation.yml`](.github/workflows/discovery-validation.yml) for source-level regression checks. The [public-currentness workflow](.github/workflows/discovery-public-currentness.yml) is a monitoring check bound to its declared historical evidence; it does not auto-refresh artifacts or authorize merges/deployment.

## Status and licensing

Discovery is an **experimental, source-executed governance/research toolkit**. It is useful for bounded inventory evidence and candidate-review workflows. It is not a turnkey SaaS inventory service, distributed runtime, or universally proven consolidation framework. Public visibility does not grant open-source redistribution rights; consult [LICENSE](LICENSE) before reusing code or research artifacts outside the permitted evaluation scope.
