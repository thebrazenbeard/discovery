from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "experiments" / "VERAMESH_SYNOLOGY_HANDOFF_EXPERIMENT_V1.json"

EXPECTED_VM_REF = "PR12@9bffc57930587bf74a12657bbeaa913474ab5574"
EXPECTED_VS_REF = "PR3@553e3a637833c5469f6b99fbc4d597755a0c9a5e"
EXPECTED_MANIFEST_BLOB = "1ff985635f4b04b648e7a164d0fa16b2a6823660"
EXPECTED_VERIFIER_BLOB = "63ae207a3482a9dbc53b157576809b298fbd6066"
EXPECTED_PAYLOAD_BLOB = "3d61fdd322a3f225e8c609a2a622b757d8315403"
EXPECTED_PAYLOAD_SHA256 = "1374d263213fceb125a4052b4e306e5200d61621087b313ef119182dd8df8dca"
EXPECTED_MANIFEST_FIELDS = ["bytes", "path", "sha256", "source_mode", "type"]
EXPECTED_DISPOSITION = "FAIL_CURRENT_NATIVE_CROSS_REPO_BINDING_MISSING"


def load():
    return json.loads(RESULT_PATH.read_text(encoding="utf-8"))


def validate_result(doc: dict) -> list[str]:
    errors: list[str] = []
    if doc.get("schema") != "DISCOVERY_VERAMESH_SYNOLOGY_HANDOFF_EXPERIMENT_V1":
        errors.append("handoff experiment schema mismatch")

    subjects = doc.get("exact_subjects", {})
    vm = subjects.get("vera_mesh", {})
    vs = subjects.get("vera_synology", {})
    if vm.get("exact_ref") != EXPECTED_VM_REF:
        errors.append("VeraMesh exact subject drifted")
    if vs.get("exact_ref") != EXPECTED_VS_REF:
        errors.append("Vera Synology exact subject drifted")

    package_sources = {
        item.get("path"): item.get("blob")
        for item in vs.get("package_sources", [])
        if isinstance(item, dict)
    }
    if package_sources.get("SOURCE_MANIFEST.json") != EXPECTED_MANIFEST_BLOB:
        errors.append("Synology source manifest blob drifted")
    if package_sources.get("tools/verify_spk.py") != EXPECTED_VERIFIER_BLOB:
        errors.append("Synology verifier blob drifted")
    if package_sources.get("payload/bin/veramesh_edge.py") != EXPECTED_PAYLOAD_BLOB:
        errors.append("Synology payload edge blob drifted")

    handoff = doc.get("proposed_minimal_handoff_record", {})
    if handoff.get("producer_exact_ref") != EXPECTED_VM_REF.removeprefix("PR12@"):
        errors.append("proposed producer exact ref drifted")
    if handoff.get("consumer_exact_ref") != EXPECTED_VS_REF.removeprefix("PR3@"):
        errors.append("proposed consumer exact ref drifted")
    if handoff.get("consumer_source_manifest_blob") != EXPECTED_MANIFEST_BLOB:
        errors.append("proposed manifest binding drifted")
    if handoff.get("payload_git_blob") != EXPECTED_PAYLOAD_BLOB:
        errors.append("proposed payload Git binding drifted")
    if handoff.get("payload_sha256_from_source_manifest") != EXPECTED_PAYLOAD_SHA256:
        errors.append("proposed payload SHA-256 binding drifted")
    if handoff.get("source_state") != "SOURCE_IMPLEMENTATION_CANDIDATE":
        errors.append("source state overclaimed")
    for field, expected in {
        "build_state": "NOT_EXECUTED_BY_DISCOVERY",
        "install_state": "NOT_OBSERVED_BY_DISCOVERY",
        "route_state": "NOT_INFERRED",
        "live_effect_state": "NOT_INFERRED",
    }.items():
        if handoff.get(field) != expected:
            errors.append(f"handoff state overclaim: {field}")

    native = doc.get("native_validation_observation", {})
    if native.get("synology_source_manifest_entry_fields") != EXPECTED_MANIFEST_FIELDS:
        errors.append("Synology manifest schema observation drifted")
    if native.get("current_native_cross_repo_binding_present") is not False:
        errors.append("native cross-repo binding falsely promoted")
    forbidden_proofs = {
        "VeraMesh producer repository identity",
        "VeraMesh producer exact commit/ref",
        "VeraMesh route/current-session state",
        "VeraMesh live effect state",
    }
    if set(native.get("synology_verifier_does_not_bind", [])) != forbidden_proofs:
        errors.append("native verifier claim ceiling drifted")

    result = doc.get("result", {})
    if result.get("local_synology_source_to_package_crossbind") != "SUPPORTED_BY_SOURCE":
        errors.append("local Synology crossbind result drifted")
    if result.get("exact_veramesh_producer_to_synology_package_binding") != "NOT_ESTABLISHED":
        errors.append("producer/package binding falsely established")
    if result.get("discovery_side_record_is_native_synology_validation") is not False:
        errors.append("Discovery record falsely promoted to native validation")
    if result.get("end_to_end_handoff_verifiable_by_current_synology_native_verifier") is not False:
        errors.append("end-to-end native handoff falsely promoted")
    if result.get("disposition") != EXPECTED_DISPOSITION:
        errors.append("handoff disposition drifted")

    return errors


def validate() -> list[str]:
    return validate_result(load())


if __name__ == "__main__":
    problems = validate()
    if problems:
        for problem in problems:
            print(problem)
        raise SystemExit(1)
    print("VeraMesh Synology handoff experiment validation PASS")
