from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CURRENTNESS_BASELINE = (
    ROOT / "portfolio" / "PUBLIC_CURRENTNESS_BASELINE_20260924_V2.json"
)
GIT_OID = re.compile(r"^[0-9a-f]{40}$")
SELF_CURRENTNESS_SUBJECT = "discovery"


class PublicCurrentnessError(ValueError):
    pass


def _nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PublicCurrentnessError(f"{label} must be a non-empty string")
    return value.strip()


def _git_oid(value: Any, label: str) -> str:
    value = _nonempty(value, label)
    if not GIT_OID.fullmatch(value):
        raise PublicCurrentnessError(f"{label} must be a lowercase 40-hex Git object id")
    return value


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PublicCurrentnessError(f"{path} must contain a JSON object")
    return payload


def load_currentness_baseline(
    *,
    baseline_path: Path = CURRENTNESS_BASELINE,
) -> dict[str, Any]:
    baseline = _load(baseline_path)
    if baseline.get("schema") != "DISCOVERY_PUBLIC_CURRENTNESS_BASELINE_V2":
        raise PublicCurrentnessError("unexpected public currentness baseline schema")
    repositories = baseline.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        raise PublicCurrentnessError(
            "public currentness baseline repositories must be a non-empty list"
        )
    if baseline.get("repository_count") != len(repositories):
        raise PublicCurrentnessError(
            "public currentness baseline repository_count mismatch"
        )
    return baseline


def load_expected_public_subjects(
    *,
    baseline_path: Path = CURRENTNESS_BASELINE,
) -> dict[str, dict[str, Any]]:
    baseline = load_currentness_baseline(baseline_path=baseline_path)
    repositories = baseline["repositories"]
    subjects: dict[str, dict[str, Any]] = {}
    for value in repositories:
        if not isinstance(value, dict):
            raise PublicCurrentnessError(
                "public currentness baseline repository entry must be an object"
            )
        name = _nonempty(value.get("name"), "baseline repository name")
        if name in subjects:
            raise PublicCurrentnessError(
                f"duplicate public subject in baseline: {name}"
            )
        default_branch = _nonempty(
            value.get("default_branch"),
            f"{name} expected default_branch",
        )
        head = _git_oid(value.get("head"), f"{name} expected head")
        tree = _git_oid(value.get("tree_sha"), f"{name} expected tree")
        archived = value.get("archived")
        if type(archived) is not bool:
            raise PublicCurrentnessError(
                f"{name} expected archived must be boolean"
            )
        subjects[name] = {
            "name": name,
            "default_branch": default_branch,
            "head": head,
            "tree_sha": tree,
            "archived": archived,
        }
    return subjects


class GitHubPublicInventoryClient:
    def __init__(
        self,
        token: str | None = None,
        *,
        api_base: str = "https://api.github.com",
    ) -> None:
        self.token = token.strip() if isinstance(token, str) and token.strip() else None
        self.api_base = api_base.rstrip("/")

    def _get_json(self, path: str) -> Any:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "discovery-public-currentness-watch-v1",
        }
        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(
            self.api_base + path,
            headers=headers,
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise PublicCurrentnessError(f"GitHub request failed for {path}: {exc}") from exc

    def list_public_owner_repositories(self, owner: str) -> list[dict[str, Any]]:
        owner = _nonempty(owner, "owner")
        repositories: list[dict[str, Any]] = []
        page = 1
        encoded_owner = urllib.parse.quote(owner, safe="")
        while True:
            payload = self._get_json(
                f"/users/{encoded_owner}/repos?type=owner&sort=full_name"
                f"&direction=asc&per_page=100&page={page}"
            )
            if not isinstance(payload, list):
                raise PublicCurrentnessError(
                    "GitHub public repository listing returned non-list payload"
                )
            for repo in payload:
                if not isinstance(repo, dict):
                    continue
                repo_owner = repo.get("owner")
                if (
                    isinstance(repo_owner, dict)
                    and repo_owner.get("login") == owner
                    and repo.get("private") is False
                ):
                    repositories.append(repo)
            if len(payload) < 100:
                break
            page += 1
        return repositories

    def exact_public_subject(
        self,
        owner: str,
        repo: dict[str, Any],
    ) -> dict[str, Any]:
        name = _nonempty(repo.get("name"), "GitHub repository name")
        default_branch = _nonempty(
            repo.get("default_branch"), f"{name} live default_branch"
        )
        archived = repo.get("archived")
        if type(archived) is not bool:
            raise PublicCurrentnessError(f"{name} live archived must be boolean")

        branch_path = urllib.parse.quote(default_branch, safe="")
        encoded_owner = urllib.parse.quote(owner, safe="")
        encoded_name = urllib.parse.quote(name, safe="")
        branch = self._get_json(
            f"/repos/{encoded_owner}/{encoded_name}/branches/{branch_path}"
        )
        if not isinstance(branch, dict):
            raise PublicCurrentnessError(f"GitHub branch response invalid for {name}")
        commit = branch.get("commit")
        if not isinstance(commit, dict):
            raise PublicCurrentnessError(f"GitHub branch commit missing for {name}")
        head = _git_oid(commit.get("sha"), f"{name} live head")

        nested_commit = commit.get("commit")
        nested_tree = (
            nested_commit.get("tree")
            if isinstance(nested_commit, dict)
            else None
        )
        tree_value = nested_tree.get("sha") if isinstance(nested_tree, dict) else None
        if tree_value is None:
            git_commit = self._get_json(
                f"/repos/{encoded_owner}/{encoded_name}/git/commits/{head}"
            )
            tree = git_commit.get("tree") if isinstance(git_commit, dict) else None
            tree_value = tree.get("sha") if isinstance(tree, dict) else None
        tree_sha = _git_oid(tree_value, f"{name} live tree")

        return {
            "name": name,
            "default_branch": default_branch,
            "head": head,
            "tree_sha": tree_sha,
            "archived": archived,
        }

    def inventory(self, owner: str) -> dict[str, dict[str, Any]]:
        subjects: dict[str, dict[str, Any]] = {}
        for repo in self.list_public_owner_repositories(owner):
            subject = self.exact_public_subject(owner, repo)
            name = subject["name"]
            if name in subjects:
                raise PublicCurrentnessError(f"duplicate live public repository: {name}")
            subjects[name] = subject
        return subjects


def compare_public_subjects(
    expected: dict[str, dict[str, Any]],
    observed: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    expected_names = set(expected)
    observed_names = set(observed)
    added = sorted(observed_names - expected_names)
    removed = sorted(expected_names - observed_names)

    moved: list[dict[str, Any]] = []
    for name in sorted(expected_names & observed_names):
        before = expected[name]
        after = observed[name]
        changes: dict[str, dict[str, Any]] = {}
        fields = (
            ("default_branch", "archived")
            if name == SELF_CURRENTNESS_SUBJECT
            else ("default_branch", "head", "tree_sha", "archived")
        )
        for field in fields:
            if before.get(field) != after.get(field):
                changes[field] = {
                    "expected": before.get(field),
                    "observed": after.get(field),
                }
        if changes:
            moved.append(
                {
                    "name": name,
                    "expected_subject": before,
                    "observed_subject": after,
                    "changes": changes,
                }
            )

    reasons: list[str] = []
    if added or removed:
        reasons.append("PUBLIC_REPOSITORY_SET_CHANGED")
    if moved:
        reasons.append("PUBLIC_EXACT_SUBJECT_CHANGED")

    return {
        "schema": "DISCOVERY_PUBLIC_CURRENTNESS_REPORT_V1",
        "status": "STALE" if reasons else "CURRENT",
        "invalidation_reasons": reasons,
        "expected_repository_count": len(expected),
        "observed_repository_count": len(observed),
        "added": added,
        "removed": removed,
        "added_subjects": [observed[name] for name in added],
        "removed_subjects": [expected[name] for name in removed],
        "moved": moved,
        "self_subject_currentness": {
            "subject": SELF_CURRENTNESS_SUBJECT,
            "status": "HEAD_TREE_SEPARATE_CI_CONCERN",
            "rule": "Discovery cannot freeze its own current main head inside a commit without self-invalidating the next commit; branch/archive remain watched here and exact source qualification remains in Discovery CI.",
        },
        "private_currentness": "NOT_OBSERVED",
        "claim_ceiling": (
            "PUBLIC_REPOSITORY_SET_DEFAULT_BRANCH_HEAD_TREE_ARCHIVE_CURRENTNESS_ONLY_"
            "NO_PRIVATE_CURRENTNESS_NO_SEMANTIC_IMPACT_NO_PROJECT_AUTHORITY"
        ),
    }


def _observed_at() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare Discovery's exact public scan subjects with live GitHub public state."
        )
    )
    parser.add_argument("--owner", default="thebrazenbeard")
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    try:
        expected = load_expected_public_subjects()
        observed = GitHubPublicInventoryClient(
            os.environ.get(args.token_env)
        ).inventory(args.owner)
        report = compare_public_subjects(expected, observed)
        baseline = load_currentness_baseline()
        report["baseline_schema"] = baseline["schema"]
        report["baseline_observed_at"] = baseline["observed_at"]
        report["blob_evidence_status"] = baseline["blob_evidence_status"]
        report["blob_evidence_claim_ceiling"] = baseline[
            "blob_evidence_claim_ceiling"
        ]
        report["observed_at"] = _observed_at()
        report["owner"] = args.owner
        report["acquisition_method"] = (
            "GITHUB_PUBLIC_REST_WITH_BEARER"
            if os.environ.get(args.token_env)
            else "GITHUB_PUBLIC_REST_ANONYMOUS"
        )
    except PublicCurrentnessError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.write_text(rendered, encoding="utf-8")

    return 0 if report["status"] == "CURRENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
