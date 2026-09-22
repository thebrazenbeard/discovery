from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "DISCOVERY_PORTFOLIO_SNAPSHOT_V1"
STATUS = "OBSERVED_READ_ONLY_NOT_ARCHITECTURAL_AUTHORITY"
PUBLIC_DIGEST_SCHEME = "SHA256_SORTED_UTF8_NAMES_V1"
PRIVATE_COMMITMENT_SCHEME = "HMAC_SHA256_PRIVATE_KEY_CANONICAL_V1"
PRIVATE_DOMAIN = b"DISCOVERY_PRIVATE_REPOSITORY_SET_V1\x00"
ALL_DOMAIN = b"DISCOVERY_ALL_REPOSITORY_SET_V1\x00"
KEY_ID_DOMAIN = b"DISCOVERY_PRIVATE_CENSUS_KEY_ID_V1\x00"
GIT_OID = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


class SnapshotError(ValueError):
    pass


def canonical_name_bytes(names: list[str]) -> bytes:
    return "".join(f"{name}\n" for name in sorted(names)).encode("utf-8")


def public_name_digest(names: list[str]) -> str:
    return hashlib.sha256(canonical_name_bytes(names)).hexdigest()


def _commitment(key: bytes, domain: bytes, names: list[str]) -> str:
    return hmac.new(key, domain + canonical_name_bytes(names), hashlib.sha256).hexdigest()


def _key_id(key: bytes) -> str:
    return hashlib.sha256(KEY_ID_DOMAIN + key).hexdigest()[:16]


def parse_private_key_hex(value: str | None) -> bytes | None:
    if value is None or not value.strip():
        return None
    raw = value.strip()
    try:
        key = bytes.fromhex(raw)
    except ValueError as exc:
        raise SnapshotError("private census key must be hexadecimal") from exc
    if len(key) < 16:
        raise SnapshotError("private census key must contain at least 128 bits")
    return key


def _nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SnapshotError(f"{label} must be a non-empty string")
    return value.strip()


def _git_oid(value: Any, label: str) -> str:
    value = _nonempty(value, label)
    if not GIT_OID.fullmatch(value):
        raise SnapshotError(f"{label} must be a lowercase 40- or 64-hex Git object id")
    return value


def normalize_repository_record(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise SnapshotError("repository record must be an object")

    name = _nonempty(record.get("name"), "repository name")
    visibility = record.get("visibility")
    if visibility not in {"public", "private"}:
        raise SnapshotError(f"repository {name} visibility must be public or private")

    archived = record.get("archived", False)
    if type(archived) is not bool:
        raise SnapshotError(f"repository {name} archived must be boolean")

    normalized: dict[str, Any] = {
        "name": name,
        "visibility": visibility,
        "archived": archived,
    }

    default_branch = record.get("default_branch")
    if visibility == "public":
        normalized["default_branch"] = _nonempty(
            default_branch, f"repository {name} default_branch"
        )
        normalized["head_sha"] = _git_oid(
            record.get("head_sha"), f"repository {name} head_sha"
        )
        normalized["tree_sha"] = _git_oid(
            record.get("tree_sha"), f"repository {name} tree_sha"
        )
    elif default_branch is not None:
        normalized["default_branch"] = _nonempty(
            default_branch, f"repository {name} default_branch"
        )

    return normalized


def build_public_snapshot(
    records: list[dict[str, Any]],
    *,
    owner: str,
    observed_at: str,
    acquisition_method: str,
    private_key: bytes | None,
) -> dict[str, Any]:
    owner = _nonempty(owner, "owner")
    observed_at = _nonempty(observed_at, "observed_at")
    acquisition_method = _nonempty(acquisition_method, "acquisition_method")

    normalized = [normalize_repository_record(record) for record in records]
    names = [record["name"] for record in normalized]
    if len(names) != len(set(names)):
        raise SnapshotError("repository names must be unique")

    public_records = sorted(
        (record for record in normalized if record["visibility"] == "public"),
        key=lambda item: item["name"],
    )
    private_records = sorted(
        (record for record in normalized if record["visibility"] == "private"),
        key=lambda item: item["name"],
    )

    private_names = [record["name"] for record in private_records]
    public_names = [record["name"] for record in public_records]
    all_names = public_names + private_names

    if private_records and private_key is None:
        raise SnapshotError(
            "private census key required when private repositories are present"
        )

    key_id = _key_id(private_key) if private_key is not None else None
    private_commitment = (
        _commitment(private_key, PRIVATE_DOMAIN, private_names)
        if private_key is not None
        else None
    )
    all_commitment = (
        _commitment(private_key, ALL_DOMAIN, all_names)
        if private_key is not None
        else None
    )

    public_subjects = [
        {
            "name": record["name"],
            "default_branch": record["default_branch"],
            "exact_commit": record["head_sha"],
            "exact_tree": record["tree_sha"],
            "archived": record["archived"],
        }
        for record in public_records
    ]

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "observed_at": observed_at,
        "source": {
            "kind": "GITHUB_ACCESSIBLE_REPOSITORY_INVENTORY",
            "owner": owner,
            "acquisition_method": acquisition_method,
        },
        "counts": {
            "total": len(normalized),
            "public": len(public_records),
            "private": len(private_records),
        },
        "public_repositories": public_subjects,
        "public_name_digest": {
            "scheme": PUBLIC_DIGEST_SCHEME,
            "sha256": public_name_digest(public_names),
            "publicly_recomputable": True,
        },
        "private_inventory_commitment": {
            "scheme": PRIVATE_COMMITMENT_SCHEME if private_records else "NONE",
            "key_id": key_id,
            "hmac_sha256": private_commitment,
            "count": len(private_records),
            "publicly_recomputable": False,
        },
        "all_inventory_commitment": {
            "scheme": PRIVATE_COMMITMENT_SCHEME if private_key is not None else "NONE",
            "key_id": key_id,
            "hmac_sha256": all_commitment,
            "count": len(normalized),
            "publicly_recomputable": False,
        },
        "privacy_rule": (
            "Private repository names are never emitted. Private and all-repository "
            "set currentness uses a keyed domain-separated HMAC commitment so the "
            "public artifact is not a deterministic dictionary oracle over private names."
        ),
        "currentness_rule": (
            "Any public repository set/head/tree movement, private-set commitment "
            "movement under the same key_id, all-set commitment movement under the "
            "same key_id, or count movement invalidates claims bound to the prior snapshot."
        ),
        "claim_ceiling": (
            "READ_ONLY_PORTFOLIO_OBSERVATION_NO_PROJECT_AUTHORITY_"
            "NO_RUNTIME_DEPENDENCY_NO_PRIVATE_NAME_PUBLICATION"
        ),
    }


class GitHubInventoryClient:
    def __init__(self, token: str, *, api_base: str = "https://api.github.com") -> None:
        self.token = _nonempty(token, "GitHub token")
        self.api_base = api_base.rstrip("/")

    def _get_json(self, path: str) -> Any:
        request = urllib.request.Request(
            self.api_base + path,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "discovery-read-only-snapshot-v1",
            },
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    def list_owned_repositories(self, owner: str) -> list[dict[str, Any]]:
        owner = _nonempty(owner, "owner")
        repositories: list[dict[str, Any]] = []
        page = 1
        while True:
            payload = self._get_json(
                "/user/repos?per_page=100&affiliation=owner&sort=full_name"
                f"&direction=asc&page={page}"
            )
            if not isinstance(payload, list):
                raise SnapshotError("GitHub repository listing returned non-list payload")
            if not payload:
                break
            repositories.extend(
                repo
                for repo in payload
                if isinstance(repo, dict)
                and isinstance(repo.get("owner"), dict)
                and repo["owner"].get("login") == owner
            )
            if len(payload) < 100:
                break
            page += 1
        return repositories

    def public_exact_subject(self, owner: str, repo: dict[str, Any]) -> dict[str, Any]:
        name = _nonempty(repo.get("name"), "GitHub repository name")
        default_branch = _nonempty(
            repo.get("default_branch"), f"{name} default branch"
        )
        branch_path = urllib.parse.quote(default_branch, safe="")
        branch = self._get_json(f"/repos/{owner}/{name}/branches/{branch_path}")
        if not isinstance(branch, dict) or not isinstance(branch.get("commit"), dict):
            raise SnapshotError(f"GitHub branch response invalid for {name}")
        head_sha = _git_oid(branch["commit"].get("sha"), f"{name} head sha")
        commit = self._get_json(f"/repos/{owner}/{name}/git/commits/{head_sha}")
        if not isinstance(commit, dict) or not isinstance(commit.get("tree"), dict):
            raise SnapshotError(f"GitHub commit response invalid for {name}")
        tree_sha = _git_oid(commit["tree"].get("sha"), f"{name} tree sha")
        return {
            "name": name,
            "visibility": "public",
            "default_branch": default_branch,
            "head_sha": head_sha,
            "tree_sha": tree_sha,
            "archived": bool(repo.get("archived", False)),
        }

    def inventory(self, owner: str) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for repo in self.list_owned_repositories(owner):
            private = repo.get("private")
            if type(private) is not bool:
                raise SnapshotError("GitHub repository visibility field invalid")
            name = _nonempty(repo.get("name"), "GitHub repository name")
            if private:
                records.append(
                    {
                        "name": name,
                        "visibility": "private",
                        "default_branch": repo.get("default_branch"),
                        "archived": bool(repo.get("archived", False)),
                    }
                )
            else:
                records.append(self.public_exact_subject(owner, repo))
        return records


def load_input_records(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict) and isinstance(payload.get("repositories"), list):
        records = payload["repositories"]
    else:
        raise SnapshotError("input JSON must be a repository list or contain repositories[]")
    if not all(isinstance(item, dict) for item in records):
        raise SnapshotError("input repositories must all be objects")
    return records


def _observed_at(value: str | None) -> str:
    if value is not None:
        return _nonempty(value, "observed_at")
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a public-safe, read-only Discovery portfolio snapshot."
    )
    parser.add_argument("--owner", required=True)
    parser.add_argument("--observed-at")
    parser.add_argument("--input-json", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    parser.add_argument(
        "--private-key-env",
        default="DISCOVERY_PRIVATE_CENSUS_KEY_HEX",
        help="Environment variable containing >=128-bit hex key for private-set HMAC commitments.",
    )
    args = parser.parse_args(argv)

    try:
        private_key = parse_private_key_hex(os.environ.get(args.private_key_env))
        if args.input_json is not None:
            records = load_input_records(args.input_json)
            acquisition_method = "OFFLINE_AUTHORIZED_INVENTORY_INPUT"
        else:
            token = os.environ.get(args.token_env)
            if token is None:
                raise SnapshotError(
                    f"{args.token_env} is required when --input-json is not supplied"
                )
            records = GitHubInventoryClient(token).inventory(args.owner)
            acquisition_method = "GITHUB_REST_READ_ONLY_AUTHENTICATED"

        snapshot = build_public_snapshot(
            records,
            owner=args.owner,
            observed_at=_observed_at(args.observed_at),
            acquisition_method=acquisition_method,
            private_key=private_key,
        )
    except SnapshotError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    rendered = json.dumps(snapshot, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
