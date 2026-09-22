from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

from check_public_currentness import (
    GitHubPublicInventoryClient,
    PublicCurrentnessError,
    load_expected_public_subjects,
)


ROOT = Path(__file__).resolve().parents[1]
SHARD_PATHS = (
    ROOT / "experiments" / "public_blob_index_v1" / "SHARD_A.json",
    ROOT / "experiments" / "public_blob_index_v1" / "SHARD_B.json",
)
SCAN_PATH = ROOT / "experiments" / "PUBLIC_BLOB_OVERLAP_SCAN_V1.json"
HC_FAMILY = {"bt2", "god-brain", "hc-brain", "transcendence"}


class BlobEvidenceError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise BlobEvidenceError(f"{path} must contain a JSON object")
    return payload


def _render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2) + "\n"


def _git_blob_sha1_text(text: str) -> str:
    payload = text.encode("utf-8")
    header = b"blob " + str(len(payload)).encode("ascii") + b"\0"
    return hashlib.sha1(header + payload).hexdigest()


def _prepare_subject(subject: dict[str, Any]) -> dict[str, Any]:
    blobs = subject.get("blobs")
    if not isinstance(blobs, list):
        raise BlobEvidenceError(f"{subject.get('name')} blob list missing")
    by_path: dict[str, dict[str, Any]] = {}
    by_sha: dict[str, int] = {}
    total = 0
    for blob in blobs:
        if not isinstance(blob, dict):
            raise BlobEvidenceError("blob entry must be an object")
        path = blob.get("path")
        sha = blob.get("sha")
        size = blob.get("size")
        if not isinstance(path, str) or not path:
            raise BlobEvidenceError("blob path must be a non-empty string")
        if not isinstance(sha, str) or len(sha) != 40:
            raise BlobEvidenceError(f"blob sha invalid: {path}")
        if type(size) is not int or size < 0:
            raise BlobEvidenceError(f"blob size invalid: {path}")
        if path in by_path:
            raise BlobEvidenceError(f"duplicate blob path: {path}")
        by_path[path] = blob
        total += size
        by_sha.setdefault(sha, size)
    return {
        "by_path": by_path,
        "by_sha": by_sha,
        "total": total,
        "files": len(blobs),
    }


def _pair_metrics(
    a_name: str,
    b_name: str,
    prepared: dict[str, dict[str, Any]],
    subjects: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    pa = prepared[a_name]
    pb = prepared[b_name]

    common = identical = changed = same_bytes = 0
    for blob_path, left in pa["by_path"].items():
        right = pb["by_path"].get(blob_path)
        if right is None:
            continue
        common += 1
        if left["sha"] == right["sha"]:
            identical += 1
            same_bytes += left["size"]
        else:
            changed += 1

    small_sha, large_sha = (
        (pa["by_sha"], pb["by_sha"])
        if len(pa["by_sha"]) <= len(pb["by_sha"])
        else (pb["by_sha"], pa["by_sha"])
    )
    shared_sha_count = 0
    shared_sha_bytes = 0
    for sha, size in small_sha.items():
        if sha in large_sha:
            shared_sha_count += 1
            shared_sha_bytes += size

    smaller_bytes = min(pa["total"], pb["total"])
    return {
        "a": a_name,
        "b": b_name,
        "a_head": subjects[a_name]["head"],
        "b_head": subjects[b_name]["head"],
        "a_files": pa["files"],
        "b_files": pb["files"],
        "a_bytes": pa["total"],
        "b_bytes": pb["total"],
        "common_paths": common,
        "identical_same_path_blobs": identical,
        "changed_same_path_blobs": changed,
        "identical_same_path_bytes": same_bytes,
        "identical_same_path_share_of_smaller_bytes": (
            same_bytes / smaller_bytes if smaller_bytes else 0.0
        ),
        "shared_blob_sha_count": shared_sha_count,
        "shared_blob_sha_bytes_unique": shared_sha_bytes,
        "shared_blob_sha_share_of_smaller_bytes": (
            shared_sha_bytes / smaller_bytes if smaller_bytes else 0.0
        ),
        "a_only_paths": pa["files"] - common,
        "b_only_paths": pb["files"] - common,
    }


def _refresh_summary(
    summary: dict[str, Any],
    pairs: list[dict[str, Any]],
    subjects: dict[str, dict[str, Any]],
) -> None:
    positive_same_path = [
        pair for pair in pairs if pair["identical_same_path_blobs"] > 0
    ]
    positive_shared = [
        pair for pair in pairs if pair["shared_blob_sha_count"] > 0
    ]
    non_hc = [
        pair
        for pair in pairs
        if not ({pair["a"], pair["b"]} <= HC_FAMILY)
    ]
    hc_members = sorted(HC_FAMILY & set(subjects))
    hc_pair_count = len(hc_members) * (len(hc_members) - 1) // 2

    summary["total_pairs"] = len(pairs)
    summary["hc_family_members"] = hc_members
    summary["hc_family_pair_count"] = hc_pair_count
    summary["pairs_with_any_identical_same_path_blob"] = len(positive_same_path)
    summary["pairs_with_any_shared_blob_sha_any_path"] = len(positive_shared)
    summary["all_byte_identity_pairs_are_inside_hc_family"] = all(
        {pair["a"], pair["b"]} <= HC_FAMILY for pair in positive_shared
    )
    summary["non_hc_pair_count"] = len(non_hc)
    summary["max_non_hc_identical_same_path_blobs"] = max(
        (pair["identical_same_path_blobs"] for pair in non_hc),
        default=0,
    )
    summary["max_non_hc_shared_blob_sha_count"] = max(
        (pair["shared_blob_sha_count"] for pair in non_hc),
        default=0,
    )

    if not positive_shared:
        summary["bounded_result"] = "NO_PUBLIC_DEFAULT_HEAD_BYTE_IDENTITY_OBSERVED"
    elif (
        len(positive_shared) == hc_pair_count
        and summary["all_byte_identity_pairs_are_inside_hc_family"]
        and set(hc_members) == HC_FAMILY
    ):
        summary["bounded_result"] = (
            "PUBLIC_DEFAULT_HEAD_BYTE_IDENTITY_ISOLATES_ONE_FOUR_REPO_HC_FAMILY_CLUSTER"
        )
    else:
        summary["bounded_result"] = (
            "PUBLIC_DEFAULT_HEAD_BYTE_IDENTITY_PATTERN_CHANGED_REVIEW_REQUIRED"
        )


def render_artifacts_from_subjects(
    live_subjects: dict[str, dict[str, Any]],
    *,
    root: Path = ROOT,
    observed_date: str | None = None,
) -> dict[Path, str]:
    shard_paths = tuple(
        root / path.relative_to(ROOT) if root != ROOT else path
        for path in SHARD_PATHS
    )
    scan_path = root / SCAN_PATH.relative_to(ROOT) if root != ROOT else SCAN_PATH

    shard_payloads = [_load(path) for path in shard_paths]
    scan = _load(scan_path)

    template_names = {
        name
        for shard in shard_payloads
        for name in shard.get("repositories", {})
    }
    if template_names != set(live_subjects):
        missing = sorted(template_names - set(live_subjects))
        added = sorted(set(live_subjects) - template_names)
        raise BlobEvidenceError(
            "public repository set changed; classify census membership before blob refresh: "
            f"missing={missing} added={added}"
        )

    rendered: dict[Path, str] = {}
    canonical_subjects: dict[str, dict[str, Any]] = {}

    for path, shard in zip(shard_paths, shard_payloads):
        if shard.get("schema") != "DISCOVERY_PUBLIC_BLOB_INDEX_SHARD_V1":
            raise BlobEvidenceError(f"unexpected shard schema: {path.name}")
        if observed_date is not None:
            shard["observed_date"] = observed_date

        repositories = shard.get("repositories")
        if not isinstance(repositories, dict):
            raise BlobEvidenceError(f"shard repositories invalid: {path.name}")

        for name, template_subject in repositories.items():
            live = live_subjects[name]
            if not isinstance(template_subject, dict):
                raise BlobEvidenceError(f"template subject invalid: {name}")

            template_subject["head"] = live["head"]
            template_subject["tree_sha"] = live["tree_sha"]
            template_subject["blobs"] = copy.deepcopy(live["blobs"])
            template_subject["default_branch"] = live["default_branch"]
            template_subject["archived"] = live["archived"]
            canonical_subjects[name] = template_subject

        rendered[path] = _render(shard)

    source_bindings = [
        {
            "path": path.relative_to(root).as_posix(),
            "blob": _git_blob_sha1_text(rendered[path]),
        }
        for path in shard_paths
    ]

    if scan.get("schema") != "DISCOVERY_PUBLIC_BLOB_OVERLAP_SCAN_V1":
        raise BlobEvidenceError("unexpected public blob overlap scan schema")
    if observed_date is not None:
        scan["observed_date"] = observed_date
    scan["source_shards"] = source_bindings
    scan["repository_count"] = len(canonical_subjects)
    scan["pair_count"] = len(canonical_subjects) * (len(canonical_subjects) - 1) // 2

    scan_repositories = scan.get("repositories")
    if not isinstance(scan_repositories, dict) or set(scan_repositories) != set(
        canonical_subjects
    ):
        raise BlobEvidenceError("scan repository template does not match public shard set")

    prepared = {
        name: _prepare_subject(subject)
        for name, subject in canonical_subjects.items()
    }

    for name, record in scan_repositories.items():
        subject = canonical_subjects[name]
        prep = prepared[name]
        record["head"] = subject["head"]
        record["tree_sha"] = subject["tree_sha"]
        record["files"] = prep["files"]
        record["total_blob_bytes"] = prep["total"]

    existing_pairs = scan.get("pairs")
    if not isinstance(existing_pairs, list):
        raise BlobEvidenceError("scan pair template missing")

    expected_keys = {
        frozenset((a, b))
        for index, a in enumerate(sorted(canonical_subjects))
        for b in sorted(canonical_subjects)[index + 1 :]
    }
    observed_keys: set[frozenset[str]] = set()
    refreshed_pairs: list[dict[str, Any]] = []
    for record in existing_pairs:
        if not isinstance(record, dict):
            raise BlobEvidenceError("scan pair template entry invalid")
        a = record.get("a")
        b = record.get("b")
        if not isinstance(a, str) or not isinstance(b, str):
            raise BlobEvidenceError("scan pair template names invalid")
        key = frozenset((a, b))
        if key not in expected_keys or key in observed_keys:
            raise BlobEvidenceError(f"scan pair template invalid: {a}<->{b}")
        observed_keys.add(key)
        metrics = _pair_metrics(a, b, prepared, canonical_subjects)
        refreshed = copy.deepcopy(record)
        for field, value in metrics.items():
            refreshed[field] = value
        refreshed_pairs.append(refreshed)

    if observed_keys != expected_keys:
        raise BlobEvidenceError("scan pair template does not cover every public pair")
    scan["pairs"] = refreshed_pairs

    summary = scan.get("summary")
    if not isinstance(summary, dict):
        raise BlobEvidenceError("scan summary template missing")
    _refresh_summary(summary, refreshed_pairs, canonical_subjects)

    rendered[scan_path] = _render(scan)
    return rendered


def subjects_from_committed_shards(*, root: Path = ROOT) -> dict[str, dict[str, Any]]:
    subjects: dict[str, dict[str, Any]] = {}
    shard_paths = tuple(
        root / path.relative_to(ROOT) if root != ROOT else path
        for path in SHARD_PATHS
    )
    for path in shard_paths:
        shard = _load(path)
        repositories = shard.get("repositories")
        if not isinstance(repositories, dict):
            raise BlobEvidenceError(f"shard repositories invalid: {path.name}")
        for name, subject in repositories.items():
            if name in subjects:
                raise BlobEvidenceError(f"duplicate shard subject: {name}")
            if not isinstance(subject, dict):
                raise BlobEvidenceError(f"shard subject invalid: {name}")
            subjects[name] = {
                "name": name,
                "default_branch": subject["default_branch"],
                "head": subject["head"],
                "tree_sha": subject["tree_sha"],
                "archived": subject["archived"],
                "blobs": copy.deepcopy(subject["blobs"]),
            }
    return subjects


class GitHubPublicBlobClient(GitHubPublicInventoryClient):
    def recursive_blobs(
        self,
        owner: str,
        subject: dict[str, Any],
    ) -> list[dict[str, Any]]:
        name = subject["name"]
        tree_sha = subject["tree_sha"]
        payload = self._get_json(
            f"/repos/{owner}/{name}/git/trees/{tree_sha}?recursive=1"
        )
        if not isinstance(payload, dict):
            raise BlobEvidenceError(f"GitHub recursive tree response invalid for {name}")
        if payload.get("truncated") is True:
            raise BlobEvidenceError(
                f"GitHub recursive tree was truncated for {name}; refusing incomplete evidence"
            )
        returned_sha = payload.get("sha")
        if returned_sha != tree_sha:
            raise BlobEvidenceError(
                f"GitHub recursive tree root mismatch for {name}: "
                f"expected {tree_sha} observed {returned_sha}"
            )
        entries = payload.get("tree")
        if not isinstance(entries, list):
            raise BlobEvidenceError(f"GitHub recursive tree entries missing for {name}")

        blobs: list[dict[str, Any]] = []
        seen_paths: set[str] = set()
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("type") != "blob":
                continue
            path = entry.get("path")
            sha = entry.get("sha")
            size = entry.get("size")
            if not isinstance(path, str) or not path:
                raise BlobEvidenceError(f"GitHub blob path invalid for {name}")
            if path in seen_paths:
                raise BlobEvidenceError(f"GitHub blob path duplicated for {name}: {path}")
            if not isinstance(sha, str) or len(sha) != 40:
                raise BlobEvidenceError(f"GitHub blob sha invalid for {name}:{path}")
            if type(size) is not int or size < 0:
                raise BlobEvidenceError(f"GitHub blob size invalid for {name}:{path}")
            seen_paths.add(path)
            blobs.append({"path": path, "sha": sha, "size": size})
        return sorted(blobs, key=lambda item: item["path"])


def collect_live_subjects(
    owner: str,
    *,
    token: str | None,
) -> dict[str, dict[str, Any]]:
    client = GitHubPublicBlobClient(token)
    observed = client.inventory(owner)

    expected = load_expected_public_subjects()
    if set(observed) != set(expected):
        missing = sorted(set(expected) - set(observed))
        added = sorted(set(observed) - set(expected))
        raise BlobEvidenceError(
            "public repository set changed; classify census membership before blob refresh: "
            f"missing={missing} added={added}"
        )

    for name in sorted(observed):
        observed[name]["blobs"] = client.recursive_blobs(owner, observed[name])
    return observed


def _check_rendered(rendered: dict[Path, str]) -> list[str]:
    mismatches = []
    for path, text in rendered.items():
        if path.read_text(encoding="utf-8") != text:
            mismatches.append(path.relative_to(ROOT).as_posix())
    return mismatches


def _write_rendered(rendered: dict[Path, str]) -> None:
    for path, text in rendered.items():
        path.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Reproduce Discovery public blob-index shards and overlap scan from live GitHub."
        )
    )
    parser.add_argument("--owner", default="thebrazenbeard")
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    parser.add_argument("--observed-date")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    if args.check and args.observed_date is not None:
        print("--observed-date is only valid with --write", file=sys.stderr)
        return 2

    try:
        live = collect_live_subjects(
            args.owner,
            token=os.environ.get(args.token_env),
        )
        rendered = render_artifacts_from_subjects(
            live,
            observed_date=args.observed_date,
        )
    except (BlobEvidenceError, PublicCurrentnessError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.check:
        mismatches = _check_rendered(rendered)
        if mismatches:
            print(
                json.dumps(
                    {
                        "status": "STALE_OR_NONREPRODUCIBLE",
                        "mismatches": mismatches,
                    },
                    indent=2,
                )
            )
            return 1
        print(
            json.dumps(
                {
                    "status": "REPRODUCIBLE",
                    "repository_count": len(live),
                    "artifacts": [
                        path.relative_to(ROOT).as_posix()
                        for path in rendered
                    ],
                },
                indent=2,
            )
        )
        return 0

    if args.observed_date is None:
        print("--write requires --observed-date YYYY-MM-DD", file=sys.stderr)
        return 2
    _write_rendered(rendered)
    print(
        json.dumps(
            {
                "status": "WROTE_REPRODUCED_PUBLIC_BLOB_EVIDENCE",
                "observed_date": args.observed_date,
                "repository_count": len(live),
                "artifacts": [
                    path.relative_to(ROOT).as_posix()
                    for path in rendered
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
