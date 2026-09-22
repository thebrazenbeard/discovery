from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SA_PATH = ROOT / "experiments" / "semantic_provenance_interchange_v1" / "SEMANTIC_ATLAS_CASE.json"
UNV_PATH = ROOT / "experiments" / "semantic_provenance_interchange_v1" / "UNVTRSLR_CASE.json"
SPM_PATH = ROOT / "experiments" / "semantic_provenance_interchange_v1" / "SPM_CONSUMER_TEST.json"
RESULT_PATH = ROOT / "experiments" / "SEMANTIC_PROVENANCE_INTERCHANGE_EXPERIMENT_V1.json"

SHA40 = re.compile(r"^[0-9a-f]{40}$")
EXACT_MAIN = re.compile(r"^main@[0-9a-f]{40}$")

RECORD_KEYS = {
    "schema_version",
    "record_id",
    "record_mode",
    "project_subject",
    "proposition",
    "source_bindings",
    "evidence_bindings",
    "interpretation_state",
    "currentness",
    "claim_ceiling",
    "native_extension_refs",
}

EXPECTED_SA = {
    "record_id": "SA_SEMANTIC_INTERFACE_FIDELITY_CURRENT_METHOD",
    "record_mode": "OBSERVED_CURRENT_RECORD",
    "repo": "thebrazenbeard/semanticatlas",
    "exact_ref": "main@5669a727b870a490ecee748b2cd712a2fc4a54c5",
    "proposition_id": "PROP-b1cfd327-7276-4c12-9532-cff244332845",
    "proposition_status": "CURRENT_METHOD_PENDING_SCHEMA_MAPPING",
    "interpretation_status": "DECIDED_PENDING_CANONICAL_SCHEMA_MAPPING",
    "claim_label": "DECIDED_PENDING_CANONICAL_SCHEMA_MAPPING",
    "source_bindings": {
        (
            "research/staging/semantic_population_v0.2/candidate_propositions_v0.2_semantic_interface_fidelity_addendum.jsonl",
            "a963b50e88445e550f01d0b4049efc6a13baddce",
        ),
        (
            "research/staging/semantic_population_v0.2/vera_adjudication_decisions_v0.2_semantic_interface_fidelity_addendum.jsonl",
            "7dc560a38c765e696de2ad86a0bde4444f84bb2f",
        ),
        (
            "research/staging/semantic_population_v0.2/candidate_evidence_spans_v0.2_r8_exact_contract_recovery_addendum.jsonl",
            "ef8a7643d7afb9952087b6f9eb71b257edcf553f",
        ),
    },
    "evidence_ids": {
        "EV-8996501b-749a-4c9a-890d-b66d1c543522",
        "EV-a28828eb-dd66-4ec2-aba2-c73c5e4e6d75",
        "EV-9dd6bf0a-7033-4557-82c6-bf5c265d21cd",
    },
}

EXPECTED_UNV = {
    "record_id": "UNVTRSLR_C047_OPERATIONAL_SEMANTIC_SEPARATION",
    "record_mode": "SPECIFIED_CONTROL_CASE",
    "repo": "thebrazenbeard/unvtrslr",
    "exact_ref": "main@903d79c6e47bb9f73bd7700edd35315777e9f5d1",
    "proposition_id": "C047",
    "proposition_status": "DESIGN_REQUIREMENT",
    "interpretation_status": "OPERATIONAL_RELATION_VERIFIED_SEMANTIC_NAMING_UNRESOLVED",
    "claim_label": "R2_SEMANTIC_CLAIM_CONTROLS_SPECIFIED / HARNESS_NOT_BUILT",
    "source_bindings": {
        ("research/CLAIMS_AND_EVIDENCE.md", "1ea0034acd74a28f6a08eb11ce0391c4d4082de5"),
        ("docs/R2_SEMANTIC_CLAIM_CONTROLS.md", "325a536bba0e00bdaf081582f416a179844504a2"),
        ("specs/R1R2_EVALUATION_CONTRACT_V1.yaml", "f0bbfcc55566800d71719442d8e362f827373789"),
    },
}

EXPECTED_SPM_MAPPING = {
    "referential_integrity": ["record_id", "proposition.native_id", "project_subject"],
    "semantic_scope_fidelity": ["proposition.text", "claim_ceiling"],
    "contradiction_and_ambiguity_preservation": [
        "interpretation_state.unresolved",
        "interpretation_state.surviving_alternatives",
    ],
    "provenance_sensitivity": ["source_bindings", "evidence_bindings"],
    "correction_state_transition": ["currentness.supersedes"],
    "temporal_currentness_sensitivity": ["currentness.state", "currentness.observed_date"],
}

FORBIDDEN_SPM_SHARED_PREFIXES = (
    "proposition.native_status",
    "interpretation_state.native_status",
    "native_extension_refs",
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_common(record: dict, *, label: str) -> list[str]:
    errors: list[str] = []
    if set(record) != RECORD_KEYS:
        errors.append(f"{label} interchange top-level keys drifted")
    if record.get("schema_version") != "SEMANTIC_EVIDENCE_INTERCHANGE_V1":
        errors.append(f"{label} schema version mismatch")
    if record.get("record_mode") not in {"OBSERVED_CURRENT_RECORD", "SPECIFIED_CONTROL_CASE"}:
        errors.append(f"{label} record mode invalid")

    subject = record.get("project_subject", {})
    if not isinstance(subject.get("repo"), str) or not subject["repo"].startswith("thebrazenbeard/"):
        errors.append(f"{label} repo binding invalid")
    if not isinstance(subject.get("exact_ref"), str) or not EXACT_MAIN.fullmatch(subject["exact_ref"]):
        errors.append(f"{label} exact ref invalid")

    proposition = record.get("proposition", {})
    for field in ("native_id", "text", "native_type", "native_status"):
        if not isinstance(proposition.get(field), str) or not proposition[field].strip():
            errors.append(f"{label} proposition field invalid: {field}")

    bindings = record.get("source_bindings")
    if not isinstance(bindings, list) or not bindings:
        errors.append(f"{label} source bindings missing")
        bindings = []
    for binding in bindings:
        if not isinstance(binding, dict):
            errors.append(f"{label} source binding invalid")
            continue
        if not isinstance(binding.get("path"), str) or not binding["path"]:
            errors.append(f"{label} source path invalid")
        if not isinstance(binding.get("blob_sha"), str) or not SHA40.fullmatch(binding["blob_sha"]):
            errors.append(f"{label} source blob invalid")
        ids = binding.get("native_record_ids")
        if not isinstance(ids, list) or any(not isinstance(value, str) or not value for value in ids):
            errors.append(f"{label} native record ids invalid")

    evidence = record.get("evidence_bindings")
    if not isinstance(evidence, list):
        errors.append(f"{label} evidence bindings invalid")
        evidence = []
    for item in evidence:
        if not isinstance(item, dict):
            errors.append(f"{label} evidence binding invalid")
            continue
        for field in ("native_id", "evidence_class", "custody_status", "source_path"):
            if not isinstance(item.get(field), str) or not item[field]:
                errors.append(f"{label} evidence field invalid: {field}")
        if not isinstance(item.get("source_blob_sha"), str) or not SHA40.fullmatch(item["source_blob_sha"]):
            errors.append(f"{label} evidence source blob invalid")

    interpretation = record.get("interpretation_state", {})
    if not isinstance(interpretation.get("native_status"), str) or not interpretation["native_status"]:
        errors.append(f"{label} interpretation native status invalid")
    if type(interpretation.get("unresolved")) is not bool:
        errors.append(f"{label} unresolved flag invalid")
    alternatives = interpretation.get("surviving_alternatives")
    if not isinstance(alternatives, list) or any(not isinstance(value, str) or not value for value in alternatives):
        errors.append(f"{label} alternatives invalid")

    currentness = record.get("currentness", {})
    if currentness.get("state") not in {"CURRENT", "HISTORICAL", "UNRESOLVED"}:
        errors.append(f"{label} currentness state invalid")
    if not isinstance(currentness.get("observed_date"), str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", currentness["observed_date"]):
        errors.append(f"{label} observed date invalid")
    if not isinstance(currentness.get("supersedes"), list):
        errors.append(f"{label} supersedes invalid")

    ceiling = record.get("claim_ceiling", {})
    for field in ("native_label", "text"):
        if not isinstance(ceiling.get(field), str) or not ceiling[field].strip():
            errors.append(f"{label} claim ceiling invalid: {field}")

    extensions = record.get("native_extension_refs")
    if not isinstance(extensions, list):
        errors.append(f"{label} native extension refs invalid")
        extensions = []
    for item in extensions:
        if not isinstance(item, dict):
            errors.append(f"{label} native extension ref invalid")
            continue
        if not isinstance(item.get("path"), str) or not item["path"]:
            errors.append(f"{label} extension path invalid")
        if not isinstance(item.get("blob_sha"), str) or not SHA40.fullmatch(item["blob_sha"]):
            errors.append(f"{label} extension blob invalid")
        if not isinstance(item.get("purpose"), str) or not item["purpose"]:
            errors.append(f"{label} extension purpose invalid")

    return errors


def _binding_pairs(record: dict) -> set[tuple[str, str]]:
    return {
        (item["path"], item["blob_sha"])
        for item in record.get("source_bindings", [])
        if isinstance(item, dict) and "path" in item and "blob_sha" in item
    }


def validate_semantic_atlas(record: dict) -> list[str]:
    errors = _validate_common(record, label="Semantic Atlas")
    expected = EXPECTED_SA
    if record.get("record_id") != expected["record_id"]:
        errors.append("Semantic Atlas record id mismatch")
    if record.get("record_mode") != expected["record_mode"]:
        errors.append("Semantic Atlas must remain an observed current record")
    subject = record.get("project_subject", {})
    if subject.get("repo") != expected["repo"] or subject.get("exact_ref") != expected["exact_ref"]:
        errors.append("Semantic Atlas exact subject binding mismatch")
    proposition = record.get("proposition", {})
    if proposition.get("native_id") != expected["proposition_id"]:
        errors.append("Semantic Atlas proposition id mismatch")
    if proposition.get("native_status") != expected["proposition_status"]:
        errors.append("Semantic Atlas proposition status mismatch")
    if record.get("interpretation_state", {}).get("native_status") != expected["interpretation_status"]:
        errors.append("Semantic Atlas adjudication status mismatch")
    if record.get("interpretation_state", {}).get("unresolved") is not False:
        errors.append("Semantic Atlas current method must remain adjudicated, not unresolved")
    if record.get("claim_ceiling", {}).get("native_label") != expected["claim_label"]:
        errors.append("Semantic Atlas claim ceiling label mismatch")
    if _binding_pairs(record) != expected["source_bindings"]:
        errors.append("Semantic Atlas exact source bindings mismatch")
    evidence_ids = {item.get("native_id") for item in record.get("evidence_bindings", []) if isinstance(item, dict)}
    if evidence_ids != expected["evidence_ids"]:
        errors.append("Semantic Atlas evidence id set mismatch")
    return errors


def validate_unvtrslr(record: dict) -> list[str]:
    errors = _validate_common(record, label="UNVTRSLR")
    expected = EXPECTED_UNV
    if record.get("record_id") != expected["record_id"]:
        errors.append("UNVTRSLR record id mismatch")
    if record.get("record_mode") != expected["record_mode"]:
        errors.append("UNVTRSLR must remain a specified control case")
    subject = record.get("project_subject", {})
    if subject.get("repo") != expected["repo"] or subject.get("exact_ref") != expected["exact_ref"]:
        errors.append("UNVTRSLR exact subject binding mismatch")
    proposition = record.get("proposition", {})
    if proposition.get("native_id") != expected["proposition_id"]:
        errors.append("UNVTRSLR proposition id mismatch")
    if proposition.get("native_status") != expected["proposition_status"]:
        errors.append("UNVTRSLR C047 must remain DESIGN_REQUIREMENT")
    if record.get("evidence_bindings") != []:
        errors.append("UNVTRSLR design-control case must not fabricate empirical evidence bindings")
    state = record.get("interpretation_state", {})
    if state.get("native_status") != expected["interpretation_status"]:
        errors.append("UNVTRSLR semantic naming state mismatch")
    if state.get("unresolved") is not True:
        errors.append("UNVTRSLR stronger semantic naming must remain unresolved in this control case")
    if record.get("claim_ceiling", {}).get("native_label") != expected["claim_label"]:
        errors.append("UNVTRSLR claim ceiling label mismatch")
    if _binding_pairs(record) != expected["source_bindings"]:
        errors.append("UNVTRSLR exact source bindings mismatch")
    return errors


def validate_spm_consumer(spm: dict, records: list[dict]) -> list[str]:
    errors: list[str] = []
    if spm.get("schema_version") != "SEMANTIC_PROVENANCE_INTERCHANGE_SPM_CONSUMER_V1":
        errors.append("SPM consumer schema mismatch")
    subject = spm.get("project_subject", {})
    if subject != {
        "repo": "thebrazenbeard/spm",
        "exact_ref": "main@0ab6e6cd32a48a0afa22c8c27ec6bae67220d7e8",
        "source_path": "docs/03-evaluation-and-falsification.md",
        "source_blob_sha": "73e7915486baf2d1449d73122d0232eff297313f",
    }:
        errors.append("SPM exact source binding mismatch")
    if spm.get("consumer_mode") != "EVALUATION_METADATA_ONLY":
        errors.append("SPM consumer mode must remain metadata-only")
    record_ids = [record.get("record_id") for record in records]
    if spm.get("records") != record_ids:
        errors.append("SPM consumer record list mismatch")
    mapping = spm.get("dimension_mapping")
    if mapping != EXPECTED_SPM_MAPPING:
        errors.append("SPM dimension mapping drifted")
    if isinstance(mapping, dict):
        for paths in mapping.values():
            for field_path in paths:
                if field_path.startswith(FORBIDDEN_SPM_SHARED_PREFIXES):
                    errors.append(f"SPM mapping imports project-native semantics: {field_path}")
    if spm.get("claim_ceiling") != "STRUCTURAL_THIRD_CONSUMER_COMPATIBILITY_ONLY_NOT_SPM_MODEL_QUALIFICATION":
        errors.append("SPM consumer claim ceiling mismatch")
    return errors


def validate_result(result: dict, records: list[dict]) -> list[str]:
    errors: list[str] = []
    expected = {
        "record_count": 2,
        "shared_top_level_field_count": len(RECORD_KEYS),
        "spm_mapped_dimension_count": len(EXPECTED_SPM_MAPPING),
        "project_native_status_fields_consumed_by_spm": 0,
        "result": "PASS_WITH_LIMITS",
        "candidate_disposition": "HYPOTHESIS_RETAINED_PENDING_INDEPENDENT_REVIEW_AND_IMPLEMENTATION_ECONOMICS",
    }
    if result.get("schema") != "DISCOVERY_SEMANTIC_PROVENANCE_INTERCHANGE_EXPERIMENT_V1":
        errors.append("semantic provenance experiment schema mismatch")
    if result.get("summary") != expected:
        errors.append("semantic provenance experiment summary mismatch")
    if result.get("records") != [record.get("record_id") for record in records]:
        errors.append("semantic provenance experiment record list mismatch")
    return errors


def validate() -> list[str]:
    sa = load(SA_PATH)
    unv = load(UNV_PATH)
    spm = load(SPM_PATH)
    result = load(RESULT_PATH)
    records = [sa, unv]

    errors: list[str] = []
    errors.extend(validate_semantic_atlas(sa))
    errors.extend(validate_unvtrslr(unv))
    errors.extend(validate_spm_consumer(spm, records))
    errors.extend(validate_result(result, records))
    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        for problem in problems:
            print(problem)
        raise SystemExit(1)
    print("Semantic provenance interchange validation PASS")
