import copy
import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "validate_semantic_provenance_interchange.py"

spec = importlib.util.spec_from_file_location("validate_semantic_provenance_interchange", TOOL)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class SemanticProvenanceInterchangeTests(unittest.TestCase):
    def setUp(self):
        self.sa = module.load(module.SA_PATH)
        self.unv = module.load(module.UNV_PATH)
        self.spm = module.load(module.SPM_PATH)
        self.result = module.load(module.RESULT_PATH)

    def test_repository_validation_passes(self):
        self.assertEqual([], module.validate())

    def test_shared_envelope_keys_are_exactly_equal(self):
        self.assertEqual(set(self.sa), set(self.unv))
        self.assertEqual(module.RECORD_KEYS, set(self.sa))

    def test_semantic_atlas_exact_ref_mutation_fails(self):
        record = copy.deepcopy(self.sa)
        record["project_subject"]["exact_ref"] = "main@" + "0" * 40
        errors = module.validate_semantic_atlas(record)
        self.assertIn("Semantic Atlas exact subject binding mismatch", errors)

    def test_semantic_atlas_evidence_set_mutation_fails(self):
        record = copy.deepcopy(self.sa)
        record["evidence_bindings"].pop()
        errors = module.validate_semantic_atlas(record)
        self.assertIn("Semantic Atlas evidence id set mismatch", errors)

    def test_unvtrslr_design_requirement_cannot_be_laundered_as_observed(self):
        record = copy.deepcopy(self.unv)
        record["record_mode"] = "OBSERVED_CURRENT_RECORD"
        errors = module.validate_unvtrslr(record)
        self.assertIn("UNVTRSLR must remain a specified control case", errors)

    def test_unvtrslr_design_case_cannot_invent_empirical_evidence(self):
        record = copy.deepcopy(self.unv)
        record["evidence_bindings"] = [
            {
                "native_id": "FAKE",
                "evidence_class": "FAKE",
                "custody_status": "FAKE",
                "source_path": "fake",
                "source_blob_sha": "0" * 40,
            }
        ]
        errors = module.validate_unvtrslr(record)
        self.assertIn("UNVTRSLR design-control case must not fabricate empirical evidence bindings", errors)

    def test_spm_cannot_consume_project_native_status_as_shared_semantics(self):
        spm = copy.deepcopy(self.spm)
        spm["dimension_mapping"]["semantic_scope_fidelity"].append("proposition.native_status")
        errors = module.validate_spm_consumer(spm, [self.sa, self.unv])
        self.assertTrue(any("imports project-native semantics" in error for error in errors))

    def test_spm_source_binding_is_exact(self):
        spm = copy.deepcopy(self.spm)
        spm["project_subject"]["source_blob_sha"] = "0" * 40
        errors = module.validate_spm_consumer(spm, [self.sa, self.unv])
        self.assertIn("SPM exact source binding mismatch", errors)

    def test_result_cannot_self_promote_candidate(self):
        result = copy.deepcopy(self.result)
        result["summary"]["candidate_disposition"] = "PROVEN_REUSABLE"
        errors = module.validate_result(result, [self.sa, self.unv])
        self.assertIn("semantic provenance experiment summary mismatch", errors)


if __name__ == "__main__":
    unittest.main()
