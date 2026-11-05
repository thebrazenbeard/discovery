"""Build a bounded source-reference graph from public, exact-blob source evidence.

This program parses source as data. It never imports the observed projects,
fetches providers, infers an installed runtime, or promotes a source reference
to an authorized communication route.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
import tomllib
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any


SCHEMA = "DISCOVERY_PUBLIC_SOURCE_CORPUS_V1"
GRAPH_SCHEMA = "DISCOVERY_PUBLIC_SOURCE_GRAPH_V1"
OID = re.compile(r"[0-9a-f]{40}\Z")
NAME = re.compile(r"[A-Za-z0-9_.-]+\Z")
DEPENDENCY_NAME = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]+\])?(?=\s|[<>=!~;]|$)")
MAX_SUBJECTS = 200
MAX_FILES = 2000
MAX_FILE_BYTES = 256 * 1024
MAX_TOTAL_BYTES = 8 * 1024 * 1024
PIN_SCHEMA = "CHAT_COMMUNICATION_BUS_CCB_BASE_CONTROL_PIN_V1"
PIN_PATH = "architecture/contracts/CCB_BASE_CONTROL_PIN_V1.json"


class GraphInputError(ValueError):
    pass


def _unique_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise GraphInputError("duplicate JSON object key forbidden")
        result[key] = value
    return result


def _strict_json(content: str) -> Any:
    return json.loads(content, object_pairs_hook=_unique_json_pairs)


def _oid(value: Any, label: str) -> str:
    if not isinstance(value, str) or not OID.fullmatch(value):
        raise GraphInputError(f"{label} requires a lowercase 40-hex Git object ID")
    return value


def _repo(value: Any, owner: str) -> str:
    if not isinstance(value, str) or value.count("/") != 1:
        raise GraphInputError("repository must be owner/name")
    actual_owner, name = value.split("/", 1)
    if actual_owner != owner or not NAME.fullmatch(name):
        raise GraphInputError("repository outside declared public owner scope")
    return value


def _path(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise GraphInputError("source path must be a relative POSIX path")
    parsed = PurePosixPath(value)
    if parsed.is_absolute() or any(part in {".", ".."} for part in value.split("/")):
        raise GraphInputError("source path traversal forbidden")
    return value


def _git_blob_oid(content: str) -> str:
    encoded = content.encode("utf-8")
    return hashlib.sha1(f"blob {len(encoded)}\0".encode() + encoded).hexdigest()


def _distribution(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _dependency_name(spec: Any) -> str | None:
    if not isinstance(spec, str) or "@" in spec or "\\" in spec:
        return None
    match = DEPENDENCY_NAME.match(spec.strip())
    return _distribution(match.group(1)) if match else None


def _provided_modules(manifest: dict[str, Any] | None) -> set[str]:
    if manifest is None:
        return set()
    setuptools = manifest.get("tool", {}).get("setuptools", {})
    packages = setuptools.get("packages", [])
    if not isinstance(packages, list):
        return set()  # Dynamic package discovery is not an attested provider list.
    return {
        p.split(".", 1)[0]
        for p in packages
        if isinstance(p, str) and all(part.isidentifier() for part in p.split("."))
    }


def _scan_subject(subject: dict[str, Any]) -> dict[str, Any]:
    files = subject["files"]
    python_distributions: set[str] = set()
    npm_packages: set[str] = set()
    modules: set[str] = set()
    dependencies: list[tuple[str, str, str, str]] = []
    imports: list[tuple[str, str, str, int]] = []
    pins: list[tuple[str, str, str, str]] = []
    ignored_imports = 0
    ignored_dependencies = 0
    for item in files:
        path, text = item["path"], item["content"]
        if path == "pyproject.toml":
            try:
                manifest = tomllib.loads(text)
            except tomllib.TOMLDecodeError as exc:
                raise GraphInputError("invalid public pyproject.toml evidence") from exc
            project = manifest.get("project", {})
            if not isinstance(project, dict):
                raise GraphInputError("pyproject project metadata must be an object")
            if isinstance(project.get("name"), str):
                python_distributions.add(_distribution(project["name"]))
            modules.update(_provided_modules(manifest))
            scopes = {"runtime": project.get("dependencies", [])}
            optional = project.get("optional-dependencies", {})
            if not isinstance(optional, dict):
                raise GraphInputError("pyproject optional-dependencies must be an object")
            scopes.update({
                f"optional:{k}": v
                for k, v in optional.items()
            })
            for scope, specs in scopes.items():
                if not isinstance(specs, list):
                    raise GraphInputError("pyproject dependency scope must be a list")
                for spec in specs:
                    name = _dependency_name(spec)
                    if name is None:
                        ignored_dependencies += 1
                    else:
                        dependencies.append((name, path, scope, "PYPROJECT_DECLARATION"))
        elif path == "package.json":
            try:
                manifest = _strict_json(text)
            except json.JSONDecodeError as exc:
                raise GraphInputError("invalid public package.json evidence") from exc
            if not isinstance(manifest, dict):
                raise GraphInputError("package.json must be an object")
            if isinstance(manifest.get("name"), str):
                npm_packages.add(manifest["name"].lower())
            for scope in ("dependencies", "devDependencies", "optionalDependencies"):
                entries = manifest.get(scope, {})
                if not isinstance(entries, dict):
                    raise GraphInputError("package.json dependency scope must be an object")
                for name, version in entries.items():
                    if not isinstance(name, str) or not isinstance(version, str):
                        raise GraphInputError("package.json dependency must be a string pair")
                    if version.startswith((
                        "file:", "link:", "workspace:", "npm:",
                        "git+", "git:", "http:", "https:"
                    )):
                        ignored_dependencies += 1
                    else:
                        dependencies.append((name.lower(), path, scope, "NPM_DECLARATION"))
        elif path == "requirements.txt":
            for spec in text.splitlines():
                spec = spec.strip()
                if not spec or spec.startswith("#"):
                    continue
                name = _dependency_name(spec)
                if name is None:
                    ignored_dependencies += 1
                else:
                    dependencies.append((name, path, "runtime", "REQUIREMENTS_DECLARATION"))
        elif path.endswith(".py"):
            parts = PurePosixPath(path).parts
            if len(parts) >= 2 and parts[-1] == "__init__.py":
                if len(parts) == 2 and parts[0].isidentifier():
                    modules.add(parts[0])
                elif len(parts) >= 3 and parts[0] == "src" and parts[1].isidentifier():
                    modules.add(parts[1])
                elif (
                    len(parts) >= 5 and parts[0] == "packages"
                    and parts[2] == "src" and parts[3].isidentifier()
                ):
                    modules.add(parts[3])
            try:
                tree = ast.parse(text, filename=path)
            except SyntaxError as exc:
                raise GraphInputError("invalid Python source evidence") from exc
            for node in ast.walk(tree):
                names: list[str] = []
                if isinstance(node, ast.Import):
                    names = [alias.name.split(".", 1)[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    names = [node.module.split(".", 1)[0]]
                for name in names:
                    if name.isidentifier():
                        imports.append((name, path, "PYTHON_SOURCE_IMPORT", node.lineno))
                    else:
                        ignored_imports += 1
        elif path == PIN_PATH:
            try:
                manifest = _strict_json(text)
            except json.JSONDecodeError as exc:
                raise GraphInputError("invalid CCB source pin JSON") from exc
            if not isinstance(manifest, dict) or manifest.get("schema") != PIN_SCHEMA:
                raise GraphInputError("unsupported CCB source pin schema")
            _oid(manifest.get("commit"), "source pin commit")
            _oid(manifest.get("tree"), "source pin tree")
            pins.append((manifest.get("repository"), manifest["commit"], manifest["tree"], path))
    return {
        "python_distributions": python_distributions,
        "npm_packages": npm_packages,
        "modules": modules,
        "dependencies": dependencies,
        "imports": imports,
        "pins": pins,
        "ignored_imports": ignored_imports,
        "ignored_dependencies": ignored_dependencies,
    }


def _cycles(nodes: list[str], edges: list[dict[str, Any]]) -> list[list[str]]:
    graph: dict[str, set[str]] = {node: set() for node in nodes}
    for edge in edges:
        graph[edge["from"]].add(edge["to"])
    index = 0
    stack: list[str] = []
    active: set[str] = set()
    indices: dict[str, int] = {}
    low: dict[str, int] = {}
    components: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = low[node] = index
        index += 1
        stack.append(node)
        active.add(node)
        for neighbor in sorted(graph[node]):
            if neighbor not in indices:
                visit(neighbor)
                low[node] = min(low[node], low[neighbor])
            elif neighbor in active:
                low[node] = min(low[node], indices[neighbor])
        if low[node] == indices[node]:
            component = []
            while True:
                member = stack.pop()
                active.remove(member)
                component.append(member)
                if member == node:
                    break
            if len(component) > 1 or node in graph[node]:
                components.append(sorted(component))

    for node in sorted(nodes):
        if node not in indices:
            visit(node)
    return sorted(components)


def build_graph(corpus: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(corpus, dict) or corpus.get("schema") != SCHEMA:
        raise GraphInputError("unsupported public source corpus schema")
    owner = corpus.get("owner")
    if not isinstance(owner, str) or not NAME.fullmatch(owner):
        raise GraphInputError("invalid public source corpus owner")
    subjects = corpus.get("subjects")
    if not isinstance(subjects, list) or len(subjects) > MAX_SUBJECTS:
        raise GraphInputError("subject count exceeds public corpus bound")
    observed: dict[str, dict[str, Any]] = {}
    total_files = total_bytes = 0
    for subject in subjects:
        if not isinstance(subject, dict):
            raise GraphInputError("public subject must be an object")
        repo = _repo(subject.get("repository"), owner)
        if repo.casefold() in {p.casefold() for p in observed}:
            raise GraphInputError("duplicate public repository identity")
        if subject.get("visibility") != "public":
            raise GraphInputError("private or unverified repository records forbidden")
        ref = _oid(subject.get("commit"), "subject commit")
        files = subject.get("files")
        if not isinstance(files, list):
            raise GraphInputError("public subject files must be a list")
        seen_paths: set[str] = set()
        for item in files:
            if not isinstance(item, dict):
                raise GraphInputError("public source file must be an object")
            path = _path(item.get("path"))
            if path.casefold() in seen_paths:
                raise GraphInputError("duplicate public source path")
            seen_paths.add(path.casefold())
            content = item.get("content")
            if not isinstance(content, str):
                raise GraphInputError("public source content must be UTF-8 text")
            size = len(content.encode("utf-8"))
            total_files += 1
            total_bytes += size
            if size > MAX_FILE_BYTES or total_files > MAX_FILES or total_bytes > MAX_TOTAL_BYTES:
                raise GraphInputError("public source corpus size bound exceeded")
            if _oid(item.get("blob_sha"), "source blob") != _git_blob_oid(content):
                raise GraphInputError("public source Git blob digest mismatch")
        observed[repo] = {"commit": ref, "files": files, "scan": _scan_subject({"files": files})}

    provider_python_dist: dict[str, set[str]] = defaultdict(set)
    provider_npm: dict[str, set[str]] = defaultdict(set)
    provider_mod: dict[str, set[str]] = defaultdict(set)
    for repo, item in observed.items():
        for value in item["scan"]["python_distributions"]:
            provider_python_dist[value].add(repo)
        for value in item["scan"]["npm_packages"]:
            provider_npm[value].add(repo)
        for value in item["scan"]["modules"]:
            provider_mod[value].add(repo)

    edges: list[dict[str, Any]] = []
    unresolved = {"external_or_unmapped": 0, "ambiguous_provider": 0}
    for source, item in observed.items():
        source_blobs = {f["path"]: f["blob_sha"] for f in item["files"]}
        scan = item["scan"]

        def add(target: str, relation: str, path: str, symbol: str, **detail: Any) -> None:
            if target == source:
                return
            edges.append({
                "from": source,
                "to": target,
                "relation": relation,
                "source_commit": item["commit"],
                "evidence": {"path": path, "blob_sha": source_blobs[path], "symbol": symbol},
                "source_evidence_class": "GIT_BLOB_BYTES_VERIFIED_LOCAL_INPUT",
                "runtime_connection": "NOT_VERIFIED",
                **detail,
            })

        for name, path, scope, relation in scan["dependencies"]:
            providers = provider_npm if relation == "NPM_DECLARATION" else provider_python_dist
            candidates = providers.get(name, set())
            if len(candidates) == 1:
                add(next(iter(candidates)), relation, path, name, dependency_scope=scope)
            elif len(candidates) > 1:
                unresolved["ambiguous_provider"] += 1
            else:
                unresolved["external_or_unmapped"] += 1
        for module, path, relation, line in scan["imports"]:
            candidates = provider_mod.get(module, set())
            if len(candidates) == 1:
                add(next(iter(candidates)), relation, path, module, line=line)
            elif len(candidates) > 1:
                unresolved["ambiguous_provider"] += 1
            else:
                unresolved["external_or_unmapped"] += 1
        for target, commit, tree, path in scan["pins"]:
            if not isinstance(target, str) or target not in observed:
                unresolved["external_or_unmapped"] += 1
                continue
            add(
                target, "DECLARED_HISTORICAL_SOURCE_PIN", path, "source-pin",
                pinned_commit=commit, pinned_tree=tree,
                pinned_head_relation=(
                    "MATCHES_SUPPLIED_SUBJECT"
                    if observed[target]["commit"] == commit
                    else "DIFFERS_FROM_SUPPLIED_SUBJECT"
                ),
            )

    unique = {json.dumps(edge, sort_keys=True): edge for edge in edges}
    edges = sorted(
        unique.values(),
        key=lambda e: (
            e["from"], e["to"], e["relation"],
            e["evidence"]["path"], e["evidence"]["symbol"],
        ),
    )
    conflicts = sorted(
        [
            {"kind": kind, "name": name, "public_providers": sorted(providers)}
            for kind, source in (
                ("PYTHON_DISTRIBUTION", provider_python_dist),
                ("NPM_PACKAGE", provider_npm),
                ("PYTHON_MODULE", provider_mod),
            )
            for name, providers in source.items() if len(providers) > 1
        ],
        key=lambda x: (x["kind"], x["name"]),
    )
    return {
        "schema": GRAPH_SCHEMA,
        "status": "SOURCE_DERIVED_NOT_RUNTIME_VERIFIED",
        "owner": owner,
        "nodes": [
            {"repository": repo, "commit": item["commit"],
             "scanned_file_count": len(item["files"])}
            for repo, item in sorted(observed.items())
        ],
        "edges": edges,
        "provider_conflicts": conflicts,
        "static_reference_cycles": _cycles(list(observed), edges),
        "counts": {
            "public_nodes": len(observed), "source_files": total_files,
            "verified_source_bytes": total_bytes, "edges": len(edges),
            **unresolved,
        },
        "claim_ceiling": (
            "SUPPLIED_PUBLIC_BLOB_BYTES_ONLY_NO_PROVIDER_AUTHENTICATION_"
            "NO_RUNTIME_OR_EFFECT_AUTHORITY"
        ),
        "negative_evidence_rule": (
            "Missing edges mean only no supported declaration in supplied "
            "files, not absence of a real dependency or channel."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a source-only public repository dependency and reference graph."
    )
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = build_graph(_strict_json(args.corpus.read_text(encoding="utf-8")))
    except (GraphInputError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
