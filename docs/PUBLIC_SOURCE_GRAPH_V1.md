# Public source-reference graph V1 — executable, not a runtime map

`tools/build_public_dependency_graph.py` reads a bounded JSON corpus of **public**
Git source files, checks every file's exact Git blob SHA-1 against its UTF-8
bytes, parses declarations without executing the observed code, and emits a
deterministic graph. It never reads a workstation, calls GitHub, installs a
package, discovers private repositories, or exercises a transport.

This is a separate newer observation family. The historical
`portfolio/PUBLIC_RELATIONSHIP_GRAPH_V1.json` and its pinned 2026-09 public cut
remain unchanged and are **not** overwritten or automatically promoted.

## Input and operation

Run on an explicitly acquired, reviewable source corpus:

```sh
python3 tools/build_public_dependency_graph.py public-source-corpus.json \
  --output public-source-graph.json
```

The input format is `DISCOVERY_PUBLIC_SOURCE_CORPUS_V1`:

```json
{
  "schema": "DISCOVERY_PUBLIC_SOURCE_CORPUS_V1",
  "owner": "example-owner",
  "subjects": [
    {
      "repository": "example-owner/public-project",
      "visibility": "public",
      "commit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "files": [
        {
          "path": "pyproject.toml",
          "blob_sha": "<actual lowercase Git blob SHA-1 of the content>",
          "content": "[project]\nname='public-project'\n"
        }
      ]
    }
  ]
}
```

The placeholder `blob_sha` above is deliberately not an executable sample;
use a genuine Git object ID from authorized public Git content. A source
record missing matching bytes **fails**, rather than silently becoming a
no-evidence node. All input is data: no repository code is imported.

Recognized static evidence:

- Python `pyproject.toml` distribution names, explicit Setuptools package
  lists, runtime and optional dependencies; `requirements.txt` simple names.
- npm `package.json` package names and direct runtime, development and optional
  **registry-semver** dependencies. Explicit `npm:actual-package@range` aliases
  resolve to their named registry target, not the declaration key. GitHub,
  GitLab, Bitbucket, Git-host shorthand, URLs, local paths, workspace links,
  unknown dist-tags and unsupported selectors are skipped rather than treated
  as same-name registry providers. This limited selector recognition does not
  authenticate npm publication, resolve a lockfile, or prove an installation.
- Python `import` and absolute `from ... import` syntax in supplied `.py`
  files are inspected for provider ambiguity, but **never** produce a
  cross-repository edge by themselves. A module with a unique advertised
  provider may still resolve locally, as a namespace package, from the
  standard library, or differently in another Python environment. Those
  candidates are counted as `unverified_import_resolution` instead.
- The publicly documented CCB Base source-pin contract at
  `architecture/contracts/CCB_BASE_CONTROL_PIN_V1.json`, recognized by its
  exact schema. It produces a **historical source-pin reference**, never a
  Bus route, permission, provider or deployment claim. Other JSON documents
  do not produce edges by incidental string similarity.

Only explicitly declared **package dependencies** whose target has a unique
public provider in this corpus, or recognized typed source pins, become edges.
Duplicate distribution or module providers are reported separately and
associated edges are withheld. Import-only edges are always withheld until
independent package-resolution evidence exists. Static reference cycles are computed from
the emitted edges; they are **not** evidence of a runtime deadlock.

## 2026-11-05 public four-repository source slice

The tracked [bounded observation](../portfolio/PUBLIC_SOURCE_GRAPH_20261105_SLICE_V1.json)
was produced from the following source files acquired through the connected
GitHub source interface at the exact public commits shown below. A temporary
input corpus retained the full source bytes for local replay; it is not
checked in. All five observed Git blob IDs matched their supplied bytes.

| Public repository | Source commit | Source file(s) and Git blob SHA-1 |
| --- | --- | --- |
| `portal` | `a27db806c064248cba5cf109aa8a4866df4fb8d1` | `pyproject.toml` `753fd7ff204d968b3fbca84b9cc0d435505be3b7`; `portal/cli.py` `82b388fc4bbce4780bb9c344a30ec716785b040c` |
| `project-runner` | `44da26e02c39591118bf1fdfe7ec01bd1103fc66` | `pyproject.toml` `3b56ff1ec5257ed5964ad46abadc6e3a47c3602a` |
| `chat-communication-bus` | `eb315a5612ae99aadddb397891ffcf3a2b0433a6` | `architecture/contracts/CCB_BASE_CONTROL_PIN_V1.json` `c6d8ba72454c07dc2587156bda871acb68bd5c4c` |
| `ccb-core` | `57b5bb97b923e43da0fb677b4e4a907bab222e37` | `pyproject.toml` `38a772c5204bcadc44116284124c7f2cfb624ab5` |

The executed graph contains **four nodes, one explicit source-pin edge, two
provider collisions, and zero static reference cycles**. Portal and Project
Runner both declare the `project-runner` distribution and `runner` module;
Portal imports `runner` in source, but package ownership and installed code
are unresolved. The extractor consequently creates **no** inferred
Portal→Project Runner runtime connection. The CCB→CCB Base edge is a source
pin to an older exact commit, not evidence of an authenticated CCB channel.

This slice is deliberately not called a complete 99-public-repository graph.
New source files and new currentness-bound observations are required for
coverage. Unscanned repositories and missing edges are **UNKNOWN**, never
absent. The graph holds source declarations, not a proven network transport,
model-agnostic tool permission, process consumption or effect receipt.

An additional **unpublished eight-public-repository smoke corpus** extended
the four above with exact `main` source from:

- `vera-mono@2cf4c42525998cf298e465f294fb45c4624e1a7c` — root
  `pyproject.toml` and nested `ingest`/`rezon` package `__init__.py` source;
- `ingest@5a33541001eb93529439829b0e766e366117e944` — root
  `pyproject.toml` and `src/ingest/__init__.py`;
- `rezon@cdd36d0df2a6194dd2738fb29ee8931933bcef7b` — root
  `pyproject.toml` and `src/rezon/__init__.py`;
- `roots@e21884602b3c1955d76c5adc09025da7ef508357` — root
  `pyproject.toml`.

That independent 13-file, 108,869-byte replay also passed: eight public
nodes, the same one historical source pin, **four** ambiguous public provider
identities (`project-runner` distribution; `runner`, `ingest`, and `rezon`
modules), zero asserted runtime connections or static cycles. This is useful
negative evidence about source ownership ambiguity, not a qualified host graph.
Its raw corpus was not published. The tracked four-node artifact remains the
small independently referenced demonstration cut.

## Trust, privacy and qualification

- The input's `visibility: public` label is supplied, **not authenticated by
  this offline tool**. A real acquirer must separately verify GitHub owner,
  visibility, repository commit/tree, blob membership and currentness before
  publishing a graph. Locally matching Git blob bytes authenticate no account.
- All emitted node identities must be public. The reader rejects explicit
  private visibility, duplicate case-folded repository names, paths with
  traversal, malformed object IDs, bad blob digests and oversized input.
- It intentionally drops unmapped/external dependency names, arbitrary source
  text and private fields in source contracts from public output.
- The corpus is limited to 200 subjects, 2,000 files, 256 KiB per file and
  8 MiB total supplied source content. This is not a general Git crawler.
- Even a fully source-populated graph is **not** runtime qualification. An
  independent installed-host, authenticated permission, command-effect and
  post-execution evidence chain remains a separate requirement.

Validation: `python3 -m unittest discover -s tests -q`, the two Discovery
validators, and focused graph tests. Any future promotion or consumption by
Portal/Vera Mono must occur behind their own authority and source ownership.
