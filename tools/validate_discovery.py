from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / "portfolio" / "PORTFOLIO_CENSUS_V1.json"
GRAPH = ROOT / "portfolio" / "PUBLIC_RELATIONSHIP_GRAPH_V1.json"
PUBLIC_INTAKE = ROOT / "portfolio" / "PUBLIC_SUBJECT_INTAKE_20260921_V1.json"
PUBLIC_BLOB_SHARDS = (
    ROOT / "experiments" / "public_blob_index_v1" / "SHARD_A.json",
    ROOT / "experiments" / "public_blob_index_v1" / "SHARD_B.json",
)
PUBLIC_BLOB_SCAN = ROOT / "experiments" / "PUBLIC_BLOB_OVERLAP_SCAN_V1.json"
TREE_BINDING_REPAIR = ROOT / "experiments" / "PUBLIC_TREE_BINDING_REPAIR_V1.json"
HC_ANCESTRY = ROOT / "experiments" / "HC_COMMON_BRANCH_ANCESTRY_V1.json"
HC_ANCESTRY_SHARDS = tuple(
    ROOT / "experiments" / "hc_common_branch_ancestry_v1" / f"SHARD_{index:02d}.json"
    for index in range(1, 8)
)
CANDIDATES = ROOT / "candidates"

VALID_RELATIONS = {
    "OVERLAPPING_MECHANIC",
    "DUPLICATED_IMPLEMENTATION",
    "COMPLEMENTARY_BOUNDARY",
    "POTENTIAL_BASE_OVERLAY",
    "PROVIDER_CONSUMER",
    "MUST_REMAIN_SEPARATE",
    "NEGATIVE_CONTROL",
    "HISTORICAL_REFERENCE",
    "NEEDS_MORE_EVIDENCE",
}
VALID_STATES = {
    "OBSERVED",
    "HYPOTHESIS",
    "EXPERIMENTING",
    "SUPPORTED",
    "REJECTED",
    "SUPERSEDED",
}
CANDIDATE_STATES = {
    "OBSERVED",
    "HYPOTHESIS",
    "EXPERIMENTING",
    "PROVEN_REUSABLE",
    "PROJECT_SPECIFIC",
    "REJECTED",
    "SUPERSEDED",
}
EXACT_SUBJECT_REF = re.compile(
    r"^(?:[0-9a-f]{40}|[^@\s]+@[0-9a-f]{40})$"
)
PLACEHOLDER_REPO_PREFIXES = ("TBD", "UNKNOWN", "PLACEHOLDER")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
PRIVATE_OPAQUE_REPO = re.compile(r"^PRIVATE_OPAQUE_[0-9a-f]{16}$")
PRIVATE_ATTESTATION_REF = re.compile(r"^private-attestation:sha256:[0-9a-f]{64}$")
PUBLIC_SOURCE_REF = re.compile(
    r"^thebrazenbeard/([^:]+):.+@[0-9a-f]{40}$"
)
PUBLIC_NAME_DIGEST_ALGORITHM = (
    "SHA-256 over lexicographically sorted repository names, UTF-8, "
    "one name per line with trailing newline"
)
PRIOR_PUBLIC_CUT_BINDING = {
    "repository": "thebrazenbeard/discovery",
    "commit": "34b9d49ff4be7eedd6104cbfa5501549e468eccd",
    "path": "portfolio/PORTFOLIO_CENSUS_V1.json",
    "blob_sha": "34cd2ab55d46f5a1ecc2c894f3e8cfdb8afa41df",
    "schema": "DISCOVERY_PORTFOLIO_CENSUS_V1",
}
PRIOR_PUBLIC_OBSERVED_DATE = "2026-09-19"
PRIOR_PUBLIC_NAMES_SHA256 = (
    "290a9a832b1c6a51dc0288de6892591fdbf5fd904d875782005d2b2d44197d34"
)
PRIOR_PUBLIC_REPOSITORIES = (
    "discovery",
    "driftguard",
    "hc-brain",
    "mosaic",
    "on-theo",
    "project-runner",
    "rezon",
    "roots",
    "testament",
    "transcendence",
    "wip",
    "world-zero",
)
OPAQUE_PRIVATE_NODE_ID = "private-cohort"
PRIVATE_ATTESTATION_FIELDS = {
    "schema",
    "commitment_scheme",
    "consumer_commitment_sha256",
    "subject_commitment_sha256",
    "receipt_sha256",
    "verifier_class",
    "status",
}
PRIVATE_VERIFIER_CLASSES = {
    "PRIVATE_OWNER_REGISTRY",
    "INDEPENDENT_PRIVATE_REVIEWER",
}


def _canonical_name_digest(names: list[str] | tuple[str, ...]) -> str:
    payload = "".join(f"{name}\n" for name in sorted(names)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _public_safe_opaque_source_ref(value, public_repos: set[str]) -> bool:
    if not isinstance(value, str):
        return False
    if PRIVATE_ATTESTATION_REF.fullmatch(value):
        return True
    match = PUBLIC_SOURCE_REF.fullmatch(value)
    return bool(match and match.group(1) in public_repos)


def _validate_census_currentness_bindings(
    census: dict,
    graph: dict,
    public_intake: dict,
) -> list[str]:
    errors: list[str] = []
    public_list = census.get("public_repositories")
    if not isinstance(public_list, list) or any(
        not _nonempty_string(item) for item in public_list
    ):
        return ["census public repository list invalid"]
    if len(set(public_list)) != len(public_list):
        errors.append("census public repository list contains duplicates")

    counts = census.get("counts", {})
    total = counts.get("total")
    public_count = counts.get("public")
    private_count = counts.get("private")
    if public_count != len(public_list):
        errors.append("census public count does not match published public list")
    if not all(type(value) is int and value >= 0 for value in (total, public_count, private_count)):
        errors.append("census counts must be nonnegative integers")
    elif total != public_count + private_count:
        errors.append("census total must equal public plus private")

    digests = census.get("inventory_digests", {})
    if digests.get("algorithm") != PUBLIC_NAME_DIGEST_ALGORITHM:
        errors.append("census inventory digest algorithm mismatch")
    recomputed_public = _canonical_name_digest(public_list)
    if digests.get("public_names_sha256") != recomputed_public:
        errors.append("census public names digest mismatch")
    for field in ("private_names_sha256", "all_names_sha256"):
        value = digests.get(field)
        if not isinstance(value, str) or not SHA256.fullmatch(value):
            errors.append(f"census {field} malformed")

    digest_validation = census.get("inventory_digest_validation", {})
    if digest_validation != {
        "public_names_sha256": "SOURCE_RECOMPUTED",
        "private_names_sha256": "EXTERNALLY_SUPPLIED_NOT_SOURCE_VALIDATED",
        "all_names_sha256": "EXTERNALLY_SUPPLIED_NOT_SOURCE_VALIDATED",
    }:
        errors.append("census inventory digest validation ceiling mismatch")

    observed_date = census.get("observed_date")
    binding = graph.get("inventory_binding", {})
    if binding.get("observed_date") != observed_date:
        errors.append("graph observed_date does not match census")
    if public_intake.get("observed_date") != observed_date:
        errors.append("public subject intake observed_date does not match census")

    current_cut = public_intake.get("current_public_cut", {})
    if current_cut.get("observed_date") != observed_date:
        errors.append("public subject intake current cut date mismatch")
    if current_cut.get("public_count") != public_count:
        errors.append("public subject intake current count mismatch")
    if current_cut.get("public_names_sha256") != recomputed_public:
        errors.append("public subject intake current public digest mismatch")

    prior_cut = public_intake.get("prior_public_cut", {})
    prior_list = prior_cut.get("public_repositories")
    expected_prior = list(PRIOR_PUBLIC_REPOSITORIES)
    if prior_cut.get("source_binding") != PRIOR_PUBLIC_CUT_BINDING:
        errors.append("public subject intake prior source binding mismatch")
    if prior_cut.get("observed_date") != PRIOR_PUBLIC_OBSERVED_DATE:
        errors.append("public subject intake prior observed_date mismatch")
    if prior_cut.get("public_count") != len(PRIOR_PUBLIC_REPOSITORIES):
        errors.append("public subject intake prior count not bound to historical census")
    if prior_cut.get("public_names_sha256") != PRIOR_PUBLIC_NAMES_SHA256:
        errors.append("public subject intake prior digest identity mismatch")
    if prior_list != expected_prior:
        errors.append("public subject intake prior list diverges from historical census")
    if isinstance(prior_list, list):
        if _canonical_name_digest(prior_list) != PRIOR_PUBLIC_NAMES_SHA256:
            errors.append("public subject intake prior list digest mismatch")

    return errors


def _validate_opaque_graph_privacy(census: dict, graph: dict) -> list[str]:
    errors: list[str] = []
    public_repos = set(census.get("public_repositories", []))
    private_count = census.get("counts", {}).get("private")
    observed_date = census.get("observed_date")
    nodes = graph.get("nodes", [])
    opaque_nodes = [
        node for node in nodes
        if isinstance(node, dict) and node.get("privacy") == "PRIVATE_OPAQUE"
    ]
    if len(opaque_nodes) != 1:
        errors.append("public graph must contain exactly one opaque private cohort node")
        return errors

    node = opaque_nodes[0]
    if node.get("id") != OPAQUE_PRIVATE_NODE_ID:
        errors.append("opaque private cohort id invalid")
    if node.get("kind") != "OPAQUE_PRIVATE_COHORT":
        errors.append("opaque private cohort kind invalid")
    if node.get("labels") != [f"{private_count}_PRIVATE_REPOSITORIES"]:
        errors.append("opaque private cohort label must contain aggregate count only")
    expected_note = (
        "Node intentionally hides private repository identities; count bound to the "
        f"{observed_date} census."
    )
    if node.get("notes") != [expected_note]:
        errors.append("opaque private cohort notes must match public-safe template")

    for other in nodes:
        if not isinstance(other, dict):
            continue
        if other.get("privacy") == "PRIVATE":
            errors.append(f"raw private node forbidden in public graph: {other.get('id')}")
        if other.get("privacy") == "PRIVATE_OPAQUE" and other.get("id") != OPAQUE_PRIVATE_NODE_ID:
            errors.append("unexpected opaque private node identifier")
        if other.get("kind") == "OPAQUE_PRIVATE_COHORT" and other.get("privacy") != "PRIVATE_OPAQUE":
            errors.append("opaque private cohort kind requires PRIVATE_OPAQUE privacy")

    for edge in graph.get("edges", []):
        if not isinstance(edge, dict):
            continue
        if OPAQUE_PRIVATE_NODE_ID not in {edge.get("from"), edge.get("to")}:
            continue
        refs = edge.get("source_refs")
        if not isinstance(refs, list) or not refs:
            errors.append(f"opaque private edge source refs invalid: {edge.get('edge_id')}")
            continue
        for ref in refs:
            if not _public_safe_opaque_source_ref(ref, public_repos):
                errors.append(
                    f"opaque private edge has unsafe source ref: {edge.get('edge_id')}"
                )

    return errors


def _validate_private_attestation(
    value,
    *,
    filename: str,
    index: int,
) -> tuple[list[str], str | None]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return (
            [f"private consumer attestation invalid: {filename}:{index}"],
            None,
        )
    if set(value) != PRIVATE_ATTESTATION_FIELDS:
        errors.append(
            f"private consumer attestation fields mismatch: {filename}:{index}"
        )
    if value.get("schema") != "DISCOVERY_PRIVATE_SUBJECT_ATTESTATION_V1":
        errors.append(
            f"private consumer attestation schema mismatch: {filename}:{index}"
        )
    if value.get("commitment_scheme") != "SHA256_PRIVATE_NONCE_CANONICAL_V1":
        errors.append(
            f"private consumer commitment scheme invalid: {filename}:{index}"
        )
    consumer_commitment = value.get("consumer_commitment_sha256")
    subject_commitment = value.get("subject_commitment_sha256")
    receipt = value.get("receipt_sha256")
    for label, digest in (
        ("consumer", consumer_commitment),
        ("subject", subject_commitment),
        ("receipt", receipt),
    ):
        if not isinstance(digest, str) or not SHA256.fullmatch(digest):
            errors.append(
                f"private consumer {label} commitment invalid: {filename}:{index}"
            )
    digest_values = [consumer_commitment, subject_commitment, receipt]
    if all(isinstance(item, str) and SHA256.fullmatch(item) for item in digest_values):
        if len(set(digest_values)) != 3:
            errors.append(
                f"private consumer commitments must be domain-separated: {filename}:{index}"
            )
    if value.get("verifier_class") not in PRIVATE_VERIFIER_CLASSES:
        errors.append(
            f"private consumer verifier class invalid: {filename}:{index}"
        )
    if value.get("status") != "EXACT_PRIVATE_SUBJECT_ATTESTED":
        errors.append(
            f"private consumer attestation status invalid: {filename}:{index}"
        )
    return errors, consumer_commitment if not errors else None


def _nonempty_string(value) -> bool:
    return type(value) is str and bool(value.strip())


def _validate_candidate_lifecycle(candidate: dict, *, filename: str) -> list[str]:
    errors: list[str] = []
    status = candidate.get("status")
    if status not in CANDIDATE_STATES:
        return [f"candidate unsupported status: {filename}"]

    consumers = candidate.get("consumers")
    if not isinstance(consumers, list) or len(consumers) < 2:
        return [f"candidate needs at least two consumers: {filename}"]

    consumer_keys: list[str] = []
    private_consumer_count = 0
    active = status in {"EXPERIMENTING", "PROVEN_REUSABLE"}
    for index, consumer in enumerate(consumers):
        if not isinstance(consumer, dict):
            errors.append(f"candidate consumer invalid: {filename}:{index}")
            continue
        repo = consumer.get("repo")
        role = consumer.get("role")
        ref = consumer.get("ref")
        visibility = consumer.get("visibility", "PUBLIC")
        if not _nonempty_string(repo):
            errors.append(f"candidate consumer repo invalid: {filename}:{index}")
        if not _nonempty_string(role):
            errors.append(f"candidate consumer role invalid: {filename}:{index}")
        if visibility not in {"PUBLIC", "PRIVATE_OPAQUE"}:
            errors.append(
                f"candidate consumer visibility invalid: {filename}:{index}"
            )
            continue

        if visibility == "PRIVATE_OPAQUE":
            private_consumer_count += 1
            if (
                not isinstance(repo, str)
                or not PRIVATE_OPAQUE_REPO.fullmatch(repo)
            ):
                errors.append(
                    f"private consumer public handle invalid: {filename}:{index}"
                )
            if ref is not None:
                errors.append(
                    f"private consumer raw ref forbidden: {filename}:{index}"
                )
            attestation = consumer.get("private_attestation")
            if active:
                attestation_errors, commitment = _validate_private_attestation(
                    attestation,
                    filename=filename,
                    index=index,
                )
                errors.extend(attestation_errors)
                if commitment is not None:
                    expected_handle = f"PRIVATE_OPAQUE_{commitment[:16]}"
                    if repo != expected_handle:
                        errors.append(
                            f"private consumer handle commitment mismatch: {filename}:{index}"
                        )
                    consumer_keys.append(f"private:{commitment}")
            elif attestation is not None:
                attestation_errors, commitment = _validate_private_attestation(
                    attestation,
                    filename=filename,
                    index=index,
                )
                errors.extend(attestation_errors)
                if commitment is not None:
                    expected_handle = f"PRIVATE_OPAQUE_{commitment[:16]}"
                    if repo != expected_handle:
                        errors.append(
                            f"private consumer handle commitment mismatch: {filename}:{index}"
                        )
                    consumer_keys.append(f"private:{commitment}")
            elif _nonempty_string(repo):
                consumer_keys.append(f"private-hypothesis:{repo.strip()}")
        else:
            if "private_attestation" in consumer:
                errors.append(
                    f"public consumer may not carry private attestation: {filename}:{index}"
                )
            if _nonempty_string(repo):
                consumer_keys.append(f"public:{repo.strip()}")
            if active:
                if (
                    not _nonempty_string(repo)
                    or repo.strip().upper().startswith(PLACEHOLDER_REPO_PREFIXES)
                ):
                    errors.append(
                        f"active candidate consumer is placeholder: {filename}:{index}"
                    )
                if not isinstance(ref, str) or not EXACT_SUBJECT_REF.fullmatch(ref):
                    errors.append(
                        f"active candidate consumer ref not exact: {filename}:{index}"
                    )

    if active and len(set(consumer_keys)) < 2:
        errors.append(f"active candidate consumers not distinct: {filename}")

    promotion_evidence = candidate.get("promotion_evidence")
    if not isinstance(promotion_evidence, list) or any(
        not _nonempty_string(item) for item in promotion_evidence
    ):
        errors.append(f"candidate promotion evidence invalid: {filename}")
        promotion_evidence = []

    hostile = candidate.get("hostile_review")
    if not isinstance(hostile, dict):
        errors.append(f"candidate hostile review invalid: {filename}")
        hostile = {}
    hostile_status = hostile.get("status")
    objections = hostile.get("critical_objections")
    if hostile_status not in {"NOT_RUN", "FAIL", "PASS_WITH_LIMITS", "PASS"}:
        errors.append(f"candidate hostile review status invalid: {filename}")
    if not isinstance(objections, list) or any(
        not _nonempty_string(item) for item in objections
    ):
        errors.append(f"candidate hostile objections invalid: {filename}")
        objections = []

    if active:
        if not promotion_evidence:
            errors.append(f"active candidate lacks promotion evidence: {filename}")
        if hostile_status == "NOT_RUN":
            errors.append(f"active candidate lacks hostile review: {filename}")

    if status == "PROVEN_REUSABLE":
        if private_consumer_count:
            errors.append(
                f"proven candidate cannot rely on opaque private consumer: {filename}"
            )
        if len(promotion_evidence) < 2:
            errors.append(f"proven candidate lacks independent evidence: {filename}")
        if hostile_status != "PASS":
            errors.append(f"proven candidate hostile review not clean PASS: {filename}")
        if objections:
            errors.append(f"proven candidate has critical objections: {filename}")

    return errors


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    header = b"blob " + str(len(payload)).encode("ascii") + b"\0"
    return hashlib.sha1(header + payload).hexdigest()


def _validate_public_blob_scan(census: dict) -> list[str]:
    errors: list[str] = []
    public_repos = set(census.get("public_repositories", []))
    indexed: dict[str, dict] = {}

    for path in PUBLIC_BLOB_SHARDS:
        shard = load(path)
        if shard.get("schema") != "DISCOVERY_PUBLIC_BLOB_INDEX_SHARD_V1":
            errors.append(f"unexpected public blob shard schema: {path.name}")
            continue
        repositories = shard.get("repositories")
        if not isinstance(repositories, dict):
            errors.append(f"public blob shard repositories invalid: {path.name}")
            continue
        for repo_name, subject in repositories.items():
            if repo_name in indexed:
                errors.append(f"public blob repo duplicated across shards: {repo_name}")
                continue
            if repo_name not in public_repos:
                errors.append(f"public blob repo not in census: {repo_name}")
            if not isinstance(subject, dict):
                errors.append(f"public blob subject invalid: {repo_name}")
                continue
            head = subject.get("head")
            tree_sha = subject.get("tree_sha")
            blobs = subject.get("blobs")
            if not isinstance(head, str) or not re.fullmatch(r"[0-9a-f]{40}", head):
                errors.append(f"public blob head invalid: {repo_name}")
            if not isinstance(tree_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", tree_sha):
                errors.append(f"public blob tree sha invalid: {repo_name}")
            elif isinstance(head, str) and tree_sha == head:
                errors.append(
                    f"public blob tree sha incorrectly aliases commit sha: {repo_name}"
                )
            if not isinstance(blobs, list):
                errors.append(f"public blob list invalid: {repo_name}")
                continue
            seen_paths: set[str] = set()
            for index, blob in enumerate(blobs):
                if not isinstance(blob, dict):
                    errors.append(f"public blob entry invalid: {repo_name}:{index}")
                    continue
                blob_path = blob.get("path")
                blob_sha = blob.get("sha")
                size = blob.get("size")
                if not _nonempty_string(blob_path):
                    errors.append(f"public blob path invalid: {repo_name}:{index}")
                elif blob_path in seen_paths:
                    errors.append(f"public blob path duplicated: {repo_name}:{blob_path}")
                else:
                    seen_paths.add(blob_path)
                if not isinstance(blob_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", blob_sha):
                    errors.append(f"public blob sha invalid: {repo_name}:{index}")
                if type(size) is not int or size < 0:
                    errors.append(f"public blob size invalid: {repo_name}:{index}")
            indexed[repo_name] = subject

    if set(indexed) != public_repos:
        errors.append("public blob shards must exactly cover current public census")

    prepared: dict[str, dict] = {}
    for repo_name, subject in indexed.items():
        blobs = subject.get("blobs", [])
        by_path = {blob["path"]: blob for blob in blobs if isinstance(blob, dict) and "path" in blob}
        by_sha: dict[str, int] = {}
        total = 0
        for blob in blobs:
            if not isinstance(blob, dict):
                continue
            size = blob.get("size")
            sha = blob.get("sha")
            if type(size) is int:
                total += size
            if isinstance(sha, str) and sha not in by_sha and type(size) is int:
                by_sha[sha] = size
        prepared[repo_name] = {
            "by_path": by_path,
            "by_sha": by_sha,
            "total": total,
            "files": len(blobs),
        }

    scan = load(PUBLIC_BLOB_SCAN)
    if scan.get("schema") != "DISCOVERY_PUBLIC_BLOB_OVERLAP_SCAN_V1":
        errors.append("unexpected public blob overlap scan schema")
        return errors

    expected_source_shards = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "blob": _git_blob_sha1(path),
        }
        for path in PUBLIC_BLOB_SHARDS
    ]
    if scan.get("source_shards") != expected_source_shards:
        errors.append("public blob scan source shard bindings mismatch")

    repair = load(TREE_BINDING_REPAIR)
    if repair.get("schema") != "DISCOVERY_PUBLIC_TREE_BINDING_REPAIR_V1":
        errors.append("unexpected public tree binding repair schema")
    repair_live = repair.get("live_inventory", {})
    census_counts = census.get("counts", {})
    if repair_live != {
        "total": census_counts.get("total"),
        "public": census_counts.get("public"),
        "private": census_counts.get("private"),
        "public_set_changed": False,
    }:
        errors.append("public tree binding repair inventory mismatch")
    repair_data = repair.get("repair", {})
    repair_bindings = repair_data.get("bindings")
    expected_repair_bindings = {
        repo_name: {
            "head": subject.get("head"),
            "tree": subject.get("tree_sha"),
        }
        for repo_name, subject in indexed.items()
    }
    if repair_bindings != expected_repair_bindings:
        errors.append("public tree binding repair bindings mismatch")
    if repair_data.get("repaired_repository_count") != len(public_repos):
        errors.append("public tree binding repair repository count mismatch")
    if repair_data.get("public_default_heads_changed_since_prior_scan") is not False:
        errors.append("public tree binding repair head-movement claim mismatch")

    expected_pair_count = len(public_repos) * (len(public_repos) - 1) // 2
    if scan.get("repository_count") != len(public_repos):
        errors.append("public blob scan repository count mismatch")
    if scan.get("pair_count") != expected_pair_count:
        errors.append("public blob scan pair count mismatch")

    scan_repositories = scan.get("repositories")
    if not isinstance(scan_repositories, dict) or set(scan_repositories) != public_repos:
        errors.append("public blob scan repository set mismatch")
    else:
        for repo_name in public_repos:
            scan_subject = scan_repositories[repo_name]
            indexed_subject = indexed.get(repo_name, {})
            prep = prepared.get(repo_name, {})
            if scan_subject.get("head") != indexed_subject.get("head"):
                errors.append(f"public blob scan head mismatch: {repo_name}")
            if scan_subject.get("tree_sha") != indexed_subject.get("tree_sha"):
                errors.append(f"public blob scan tree mismatch: {repo_name}")
            if scan_subject.get("files") != prep.get("files"):
                errors.append(f"public blob scan file count mismatch: {repo_name}")
            if scan_subject.get("total_blob_bytes") != prep.get("total"):
                errors.append(f"public blob scan byte count mismatch: {repo_name}")

    expected_pairs: dict[frozenset[str], dict] = {}
    names = sorted(public_repos)
    for index, a in enumerate(names):
        for b in names[index + 1:]:
            pa = prepared[a]
            pb = prepared[b]
            common = identical = changed = same_bytes = 0
            for blob_path, left in pa["by_path"].items():
                right = pb["by_path"].get(blob_path)
                if right is None:
                    continue
                common += 1
                if left.get("sha") == right.get("sha"):
                    identical += 1
                    same_bytes += left.get("size", 0)
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
            expected_pairs[frozenset((a, b))] = {
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
                "a_head": indexed[a].get("head"),
                "b_head": indexed[b].get("head"),
                "a_name": a,
                "b_name": b,
            }

    observed_pairs = scan.get("pairs")
    if not isinstance(observed_pairs, list):
        errors.append("public blob scan pairs invalid")
        observed_pairs = []
    seen_pairs: set[frozenset[str]] = set()
    for record in observed_pairs:
        if not isinstance(record, dict):
            errors.append("public blob scan pair record invalid")
            continue
        a = record.get("a")
        b = record.get("b")
        key = frozenset((a, b)) if isinstance(a, str) and isinstance(b, str) else frozenset()
        if len(key) != 2 or key not in expected_pairs:
            errors.append(f"public blob scan unexpected pair: {a!r}<->{b!r}")
            continue
        if key in seen_pairs:
            errors.append(f"public blob scan duplicate pair: {a}<->{b}")
            continue
        seen_pairs.add(key)
        expected = expected_pairs[key]

        # Pair orientation in the stored scan determines which side owns a_* fields.
        if a != expected["a_name"]:
            expected = {
                **expected,
                "a_files": expected["b_files"],
                "b_files": expected["a_files"],
                "a_bytes": expected["b_bytes"],
                "b_bytes": expected["a_bytes"],
                "a_only_paths": expected["b_only_paths"],
                "b_only_paths": expected["a_only_paths"],
                "a_head": expected["b_head"],
                "b_head": expected["a_head"],
            }

        integer_fields = (
            "a_files", "b_files", "a_bytes", "b_bytes", "common_paths",
            "identical_same_path_blobs", "changed_same_path_blobs",
            "identical_same_path_bytes", "shared_blob_sha_count",
            "shared_blob_sha_bytes_unique", "a_only_paths", "b_only_paths",
        )
        for field in integer_fields:
            if record.get(field) != expected[field]:
                errors.append(f"public blob scan metric mismatch: {a}<->{b}:{field}")
        for field in (
            "identical_same_path_share_of_smaller_bytes",
            "shared_blob_sha_share_of_smaller_bytes",
        ):
            value = record.get(field)
            if not isinstance(value, (int, float)) or not math.isclose(
                float(value), float(expected[field]), rel_tol=1e-12, abs_tol=1e-15
            ):
                errors.append(f"public blob scan ratio mismatch: {a}<->{b}:{field}")
        if record.get("a_head") != expected["a_head"] or record.get("b_head") != expected["b_head"]:
            errors.append(f"public blob scan pair head mismatch: {a}<->{b}")

    if seen_pairs != set(expected_pairs):
        errors.append("public blob scan does not contain every public repository pair")

    hc_family = {"bt2", "god-brain", "hc-brain", "transcendence"}
    identity_pairs = [
        record for record in observed_pairs
        if isinstance(record, dict) and record.get("shared_blob_sha_count", 0) > 0
    ]
    if len(identity_pairs) != 6:
        errors.append("public blob scan expected exactly six byte-identity pairs")
    for record in identity_pairs:
        if {record.get("a"), record.get("b")} - hc_family:
            errors.append("public blob scan byte identity escaped HC family")
    non_hc = [
        record for record in observed_pairs
        if isinstance(record, dict)
        and not ({record.get("a"), record.get("b")} <= hc_family)
    ]
    if any(record.get("shared_blob_sha_count", 0) != 0 for record in non_hc):
        errors.append("public blob scan non-HC shared blob found")

    summary = scan.get("summary", {})
    if summary.get("total_pairs") != expected_pair_count:
        errors.append("public blob scan summary pair count mismatch")
    if summary.get("non_hc_pair_count") != expected_pair_count - 6:
        errors.append("public blob scan summary non-HC pair count mismatch")
    if summary.get("all_byte_identity_pairs_are_inside_hc_family") is not True:
        errors.append("public blob scan summary HC isolation flag missing")

    return errors



def _validate_hc_ancestry_contract(artifact: dict, shards: list[dict]) -> list[str]:
    errors: list[str] = []
    if artifact.get("schema") != "DISCOVERY_HC_COMMON_BRANCH_ANCESTRY_V1":
        errors.append("unexpected HC ancestry schema")

    branch_subjects: dict[str, dict] = {}
    for index, shard in enumerate(shards, start=1):
        if shard.get("schema") != "DISCOVERY_HC_COMMON_BRANCH_ANCESTRY_SHARD_V1":
            errors.append(f"unexpected HC ancestry shard schema: {index:02d}")
            continue
        if shard.get("shard") != f"{index:02d}":
            errors.append(f"HC ancestry shard id mismatch: {index:02d}")
        branches = shard.get("branches")
        if not isinstance(branches, dict):
            errors.append(f"HC ancestry shard branches invalid: {index:02d}")
            continue
        for branch_name, subjects in branches.items():
            if branch_name == "main":
                errors.append("HC ancestry shards must exclude main")
            if branch_name in branch_subjects:
                errors.append(f"HC ancestry branch duplicated across shards: {branch_name}")
            branch_subjects[branch_name] = subjects

    if len(branch_subjects) != 34:
        errors.append("HC ancestry shards must contain exactly 34 non-main branches")

    expected_records: dict[str, dict] = {}
    required_subjects = {"hc-brain", "transcendence", "god-brain"}
    for branch_name, subjects in branch_subjects.items():
        if not isinstance(subjects, dict) or set(subjects) != required_subjects:
            errors.append(f"HC ancestry subjects invalid: {branch_name}")
            continue
        h = subjects["hc-brain"]
        t = subjects["transcendence"]
        g = subjects["god-brain"]
        for label, subject in (("hc", h), ("transcendence", t), ("god_brain", g)):
            for field in ("sha", "tree_sha"):
                value = subject.get(field)
                if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value):
                    errors.append(f"HC ancestry {label} {field} invalid: {branch_name}")
            parents = subject.get("parents")
            if not isinstance(parents, list) or any(
                not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value)
                for value in parents
            ):
                errors.append(f"HC ancestry {label} parents invalid: {branch_name}")
            if not _nonempty_string(subject.get("message")):
                errors.append(f"HC ancestry {label} message invalid: {branch_name}")
            if not _nonempty_string(subject.get("author_date")):
                errors.append(f"HC ancestry {label} author_date invalid: {branch_name}")

        expected_records[branch_name] = {
            "branch": branch_name,
            "hc": {
                "head": h.get("sha"),
                "tree_sha": h.get("tree_sha"),
                "parents": h.get("parents"),
                "message": h.get("message"),
                "author_date": h.get("author_date"),
            },
            "transcendence": {
                "head": t.get("sha"),
                "tree_sha": t.get("tree_sha"),
                "parents": t.get("parents"),
                "message": t.get("message"),
                "author_date": t.get("author_date"),
            },
            "god_brain": {
                "head": g.get("sha"),
                "tree_sha": g.get("tree_sha"),
                "parents": g.get("parents"),
                "message": g.get("message"),
                "author_date": g.get("author_date"),
            },
            "same_tree_sha": (
                h.get("tree_sha") == t.get("tree_sha") == g.get("tree_sha")
            ),
            "hc_parented": bool(h.get("parents")),
            "transcendence_parentless": t.get("parents") == [],
            "god_brain_parentless": g.get("parents") == [],
            "hc_earlier_than_transcendence": (
                isinstance(h.get("author_date"), str)
                and isinstance(t.get("author_date"), str)
                and h["author_date"] < t["author_date"]
            ),
            "transcendence_earlier_than_god_brain": (
                isinstance(t.get("author_date"), str)
                and isinstance(g.get("author_date"), str)
                and t["author_date"] < g["author_date"]
            ),
            "transcendence_initialize_message": (
                t.get("message") == f"Initialize {branch_name}"
            ),
            "god_brain_initialize_message": (
                g.get("message") == f"Initialize {branch_name}"
            ),
        }

    records = artifact.get("records")
    if not isinstance(records, list):
        errors.append("HC ancestry records must be a list")
        records = []
    observed_records: dict[str, dict] = {}
    for record in records:
        if not isinstance(record, dict) or not _nonempty_string(record.get("branch")):
            errors.append("HC ancestry record invalid")
            continue
        branch_name = record["branch"]
        if branch_name in observed_records:
            errors.append(f"HC ancestry record duplicated: {branch_name}")
        observed_records[branch_name] = record

    if set(observed_records) != set(expected_records):
        errors.append("HC ancestry records must exactly cover shard branch population")
    for branch_name, expected in expected_records.items():
        if observed_records.get(branch_name) != expected:
            errors.append(f"HC ancestry record does not recompute: {branch_name}")

    expected_pattern = [
        record
        for record in expected_records.values()
        if all(
            record[field] is True
            for field in (
                "same_tree_sha",
                "hc_parented",
                "transcendence_parentless",
                "god_brain_parentless",
                "hc_earlier_than_transcendence",
                "transcendence_earlier_than_god_brain",
                "transcendence_initialize_message",
                "god_brain_initialize_message",
            )
        )
    ]
    results = artifact.get("results", {})
    expected_count = len(expected_records)
    expected_summary = {
        "branch_count": expected_count,
        "same_tree_sha_count": sum(r["same_tree_sha"] for r in expected_records.values()),
        "hc_parented_count": sum(r["hc_parented"] for r in expected_records.values()),
        "transcendence_parentless_count": sum(
            r["transcendence_parentless"] for r in expected_records.values()
        ),
        "god_brain_parentless_count": sum(
            r["god_brain_parentless"] for r in expected_records.values()
        ),
        "hc_earlier_than_transcendence_count": sum(
            r["hc_earlier_than_transcendence"] for r in expected_records.values()
        ),
        "transcendence_earlier_than_god_brain_count": sum(
            r["transcendence_earlier_than_god_brain"] for r in expected_records.values()
        ),
        "transcendence_initialize_message_count": sum(
            r["transcendence_initialize_message"] for r in expected_records.values()
        ),
        "god_brain_initialize_message_count": sum(
            r["god_brain_initialize_message"] for r in expected_records.values()
        ),
        "all_branches_match_pattern": len(expected_pattern) == expected_count == 34,
        "bounded_result": (
            "ALL_34_NON_MAIN_COMMON_BRANCHES_SHOW_EARLIER_PARENTED_HC_COMMIT_"
            "AND_LATER_PARENTLESS_IDENTICAL_TREE_INITIALIZATIONS_IN_TRANSCENDENCE_"
            "AND_GOD_BRAIN"
        ),
    }
    if results != expected_summary:
        errors.append("HC ancestry summary does not recompute")

    return errors


def _validate_hc_ancestry() -> list[str]:
    return _validate_hc_ancestry_contract(
        load(HC_ANCESTRY),
        [load(path) for path in HC_ANCESTRY_SHARDS],
    )



def validate() -> list[str]:
    errors: list[str] = []
    census = load(CENSUS)
    graph = load(GRAPH)
    public_intake = load(PUBLIC_INTAKE)
    errors.extend(_validate_census_currentness_bindings(census, graph, public_intake))
    errors.extend(_validate_opaque_graph_privacy(census, graph))
    errors.extend(_validate_public_blob_scan(census))
    errors.extend(_validate_hc_ancestry())

    if graph.get("schema_version") != "DISCOVERY_RELATIONSHIP_GRAPH_V1":
        errors.append("unexpected graph schema")

    binding = graph.get("inventory_binding", {})
    if binding.get("total_count") != census.get("counts", {}).get("total"):
        errors.append("graph total_count does not match census")
    if (
        binding.get("all_names_sha256")
        != census.get("inventory_digests", {}).get("all_names_sha256")
    ):
        errors.append("graph inventory digest does not match census")

    nodes = graph.get("nodes")
    if not isinstance(nodes, list):
        return errors + ["nodes must be a list"]

    node_ids: set[str] = set()
    for node in nodes:
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            errors.append("node missing id")
            continue
        if node_id in node_ids:
            errors.append(f"duplicate node id: {node_id}")
        node_ids.add(node_id)

    edges = graph.get("edges")
    if not isinstance(edges, list):
        return errors + ["edges must be a list"]

    edge_ids: set[str] = set()
    for edge in edges:
        edge_id = edge.get("edge_id")
        if not isinstance(edge_id, str) or not edge_id:
            errors.append("edge missing edge_id")
            continue
        if edge_id in edge_ids:
            errors.append(f"duplicate edge id: {edge_id}")
        edge_ids.add(edge_id)

        if edge.get("from") not in node_ids or edge.get("to") not in node_ids:
            errors.append(f"edge has unknown endpoint: {edge_id}")
        if edge.get("relation") not in VALID_RELATIONS:
            errors.append(f"unsupported relation: {edge_id}")
        if edge.get("evidence_state") not in VALID_STATES:
            errors.append(f"unsupported evidence state: {edge_id}")
        if not edge.get("scope"):
            errors.append(f"edge missing scope: {edge_id}")
        if not edge.get("source_refs"):
            errors.append(f"edge missing source refs: {edge_id}")
        if not edge.get("falsifiers"):
            errors.append(f"edge missing falsifiers: {edge_id}")

    public_repos = set(census.get("public_repositories", []))
    public_nodes = {
        node["id"]
        for node in nodes
        if node.get("kind") == "REPOSITORY" and node.get("privacy") == "PUBLIC"
    }
    if public_nodes != public_repos:
        errors.append(
            "public graph repository nodes must exactly equal public census repositories"
        )

    if public_intake.get("schema") != "DISCOVERY_PUBLIC_SUBJECT_INTAKE_V1":
        errors.append("unexpected public subject intake schema")
    prior_cut = public_intake.get("prior_public_cut", {})
    prior_public = set(prior_cut.get("public_repositories", []))
    if not prior_public.issubset(public_repos):
        errors.append("public subject intake prior public set not contained in current census")

    intake_subjects = public_intake.get("subjects")
    intake_repos: set[str] = set()
    if not isinstance(intake_subjects, list):
        errors.append("public subject intake subjects must be a list")
        intake_subjects = []
    for index, subject in enumerate(intake_subjects):
        if not isinstance(subject, dict):
            errors.append(f"public subject intake invalid subject: {index}")
            continue
        repo = subject.get("repo")
        ref = subject.get("ref")
        families = subject.get("primary_families")
        if not isinstance(repo, str) or not repo.startswith("thebrazenbeard/"):
            errors.append(f"public subject intake invalid repo: {index}")
            continue
        repo_name = repo.split("/", 1)[1]
        intake_repos.add(repo_name)
        if repo_name not in public_repos:
            errors.append(f"public subject intake repo not in current census: {repo_name}")
        if not isinstance(ref, str) or not EXACT_SUBJECT_REF.fullmatch(ref):
            errors.append(f"public subject intake ref not exact: {repo_name}")
        if not isinstance(families, list) or not families or any(
            not _nonempty_string(item) for item in families
        ):
            errors.append(f"public subject intake families invalid: {repo_name}")
        if not _nonempty_string(subject.get("observed_role")):
            errors.append(f"public subject intake observed role missing: {repo_name}")
        if not _nonempty_string(subject.get("disposition")):
            errors.append(f"public subject intake disposition missing: {repo_name}")
        if not _nonempty_string(subject.get("next_question")):
            errors.append(f"public subject intake next question missing: {repo_name}")

    expected_new_public = public_repos - prior_public
    if intake_repos != expected_new_public:
        errors.append(
            "public subject intake must exactly cover repositories newly public "
            "relative to its bound prior cut"
        )
    anti = public_intake.get("anti_cherry_pick_result", {})
    if anti.get("subjects_expected") != len(expected_new_public):
        errors.append("public subject intake expected count mismatch")
    if anti.get("subjects_recorded") != len(intake_repos):
        errors.append("public subject intake recorded count mismatch")

    for path in CANDIDATES.glob("*.json"):
        candidate = load(path)
        if candidate.get("schema_version") != "DISCOVERY_CANDIDATE_V1":
            errors.append(f"candidate schema mismatch: {path.name}")
        if not candidate.get("rejection_conditions"):
            errors.append(f"candidate missing rejection conditions: {path.name}")
        errors.extend(
            _validate_candidate_lifecycle(candidate, filename=path.name)
        )

    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        for problem in problems:
            print(problem)
        raise SystemExit(1)
    print("Discovery validation PASS")
