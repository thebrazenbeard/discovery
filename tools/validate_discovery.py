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

PR21_PRIOR_CENSUS_BINDING = {
    "repository": "thebrazenbeard/discovery",
    "commit": "34b9d49ff4be7eedd6104cbfa5501549e468eccd",
    "path": "portfolio/PORTFOLIO_CENSUS_V1.json",
    "blob": "34cd2ab55d46f5a1ecc2c894f3e8cfdb8afa41df",
    "observed_date": "2026-09-19",
    "public_names_sha256": "290a9a832b1c6a51dc0288de6892591fdbf5fd904d875782005d2b2d44197d34",
}
PR21_PRIOR_PUBLIC_REPOSITORIES = frozenset({
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
})
OPAQUE_PRIVATE_COHORT_ID = "private-cohort"
PRIVATE_ATTESTATION_REF = re.compile(r"^private-attestation:sha256:[0-9a-f]{64}$")
PUBLIC_GRAPH_REPO_REF = re.compile(
    r"^thebrazenbeard/([^:]+):(.+)$"
)


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


def _public_names_sha256(names) -> str:
    normalized = sorted(names)
    payload = "".join(f"{name}\n" for name in normalized).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _validate_census_contract(
    census: dict,
    graph: dict,
    public_intake: dict,
) -> list[str]:
    errors: list[str] = []
    counts = census.get("counts", {})
    public_repos = census.get("public_repositories")
    if not isinstance(public_repos, list) or any(
        not _nonempty_string(item) for item in public_repos
    ):
        return ["census public_repositories invalid"]

    if len(public_repos) != len(set(public_repos)):
        errors.append("census public_repositories contains duplicates")

    public_count = counts.get("public")
    private_count = counts.get("private")
    total_count = counts.get("total")
    if public_count != len(public_repos):
        errors.append("census public count does not match public repository list")
    if (
        type(public_count) is not int
        or type(private_count) is not int
        or type(total_count) is not int
        or total_count != public_count + private_count
    ):
        errors.append("census total/public/private arithmetic mismatch")

    digests = census.get("inventory_digests", {})
    expected_public_digest = _public_names_sha256(public_repos)
    if digests.get("public_names_sha256") != expected_public_digest:
        errors.append("census public_names_sha256 does not recompute")

    validation = census.get("inventory_digest_validation", {})
    if validation.get("public_names_sha256") != "SOURCE_RECOMPUTED_FROM_PUBLIC_REPOSITORIES":
        errors.append("census public digest validation class mismatch")
    if (
        validation.get("private_names_sha256")
        != "EXTERNAL_LIVE_INVENTORY_OBSERVATION_NOT_SOURCE_RECOMPUTABLE"
    ):
        errors.append("census private digest evidence ceiling mismatch")
    if (
        validation.get("all_names_sha256")
        != "EXTERNAL_LIVE_INVENTORY_OBSERVATION_NOT_SOURCE_RECOMPUTABLE"
    ):
        errors.append("census all-names digest evidence ceiling mismatch")

    observed_date = census.get("observed_date")
    binding = graph.get("inventory_binding", {})
    if binding.get("observed_date") != observed_date:
        errors.append("graph observed_date does not match census")
    if binding.get("total_count") != total_count:
        errors.append("graph total_count does not match census")
    if binding.get("all_names_sha256") != digests.get("all_names_sha256"):
        errors.append("graph all_names digest does not match census external observation")

    current_cut = public_intake.get("current_public_cut", {})
    if public_intake.get("observed_date") != observed_date:
        errors.append("public intake observed_date does not match census")
    if current_cut.get("observed_date") != observed_date:
        errors.append("public intake current-cut observed_date does not match census")
    if current_cut.get("public_count") != public_count:
        errors.append("public intake current public count does not match census")
    if current_cut.get("public_names_sha256") != expected_public_digest:
        errors.append("public intake current public digest does not match census")

    prior_cut = public_intake.get("prior_public_cut", {})
    prior_public = set(prior_cut.get("public_repositories", []))
    if prior_public != set(PR21_PRIOR_PUBLIC_REPOSITORIES):
        errors.append("public intake prior public set diverges from immutable prior census")
    if prior_cut.get("observed_date") != PR21_PRIOR_CENSUS_BINDING["observed_date"]:
        errors.append("public intake prior observed_date mismatch")
    if prior_cut.get("public_count") != len(PR21_PRIOR_PUBLIC_REPOSITORIES):
        errors.append("public intake prior public count mismatch")
    if _public_names_sha256(prior_public) != PR21_PRIOR_CENSUS_BINDING["public_names_sha256"]:
        errors.append("public intake prior public digest recomputation mismatch")
    source_binding = prior_cut.get("source_binding")
    if source_binding != {
        key: value
        for key, value in PR21_PRIOR_CENSUS_BINDING.items()
        if key != "observed_date"
    }:
        errors.append("public intake prior census immutable source binding mismatch")

    return errors


def _validate_graph_privacy(graph: dict, public_repos: set[str], private_count: int) -> list[str]:
    errors: list[str] = []
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return errors

    opaque_nodes = [
        node
        for node in nodes
        if isinstance(node, dict)
        and (
            node.get("kind") == "OPAQUE_PRIVATE_COHORT"
            or node.get("privacy") == "PRIVATE_OPAQUE"
        )
    ]
    if len(opaque_nodes) != 1:
        errors.append("public graph must contain exactly one opaque private cohort")
    else:
        node = opaque_nodes[0]
        expected_node = {
            "id": OPAQUE_PRIVATE_COHORT_ID,
            "kind": "OPAQUE_PRIVATE_COHORT",
            "privacy": "PRIVATE_OPAQUE",
            "labels": [f"{private_count}_PRIVATE_REPOSITORIES"],
            "notes": [
                "Node intentionally hides private repository identities; "
                f"count bound to the {graph.get('inventory_binding', {}).get('observed_date')} census."
            ],
        }
        if node != expected_node:
            errors.append("opaque private cohort shape/content mismatch")

    for node in nodes:
        if not isinstance(node, dict):
            continue
        if node.get("privacy") == "PRIVATE":
            errors.append(f"raw private node forbidden in public graph: {node.get('id')}")
        if node.get("privacy") == "PRIVATE_OPAQUE" and node.get("id") != OPAQUE_PRIVATE_COHORT_ID:
            errors.append("unexpected opaque private node identifier")

    for edge in edges:
        if not isinstance(edge, dict):
            continue
        refs = edge.get("source_refs", [])
        if not isinstance(refs, list):
            continue
        for ref in refs:
            if not isinstance(ref, str):
                errors.append("graph source_ref must be string")
                continue
            if PRIVATE_ATTESTATION_REF.fullmatch(ref):
                continue
            match = PUBLIC_GRAPH_REPO_REF.fullmatch(ref)
            if match is None:
                errors.append(f"graph source_ref unsupported public shape: {ref}")
                continue
            repo_name, subject_ref = match.groups()
            if repo_name not in public_repos:
                errors.append("graph source_ref names repository outside public census")
            if not EXACT_SUBJECT_REF.fullmatch(subject_ref):
                errors.append(f"graph source_ref not exact: {repo_name}")

    return errors



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


def validate() -> list[str]:
    errors: list[str] = []
    census = load(CENSUS)
    graph = load(GRAPH)
    public_intake = load(PUBLIC_INTAKE)
    errors.extend(_validate_public_blob_scan(census))
    errors.extend(_validate_census_contract(census, graph, public_intake))
    errors.extend(
        _validate_graph_privacy(
            graph,
            set(census.get("public_repositories", [])),
            census.get("counts", {}).get("private"),
        )
    )

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
