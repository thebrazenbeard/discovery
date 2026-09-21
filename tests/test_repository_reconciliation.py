from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_reconciliation",
    ROOT / "tools" / "validate_reconciliation.py",
)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(validator)


def current_manifest() -> dict:
    return validator.load()


class DiscoveryRepositoryReconciliationTests(unittest.TestCase):
    def test_current_reconciliation_manifest_validates(self):
        self.assertEqual([], validator.validate_reconciliation())

    def test_committed_manifest_cannot_self_assert_current_exact_head(self):
        data = current_manifest()
        data["proposed_candidate"]["current_exact_head"] = "a" * 40
        failures = validator.validate_reconciliation_data(data)
        self.assertIn(
            "committed manifest must not self-assert current exact head",
            failures,
        )

    def test_pr19_is_wrapper_and_pr17_is_source_lineage_terminal(self):
        data = current_manifest()
        data["proposed_pr_dispositions"]["17"] = "CURRENT_CANDIDATE"
        failures = validator.validate_reconciliation_data(data)
        self.assertIn("proposed PR dispositions mismatch", failures)

        data = current_manifest()
        del data["proposed_pr_dispositions"]["19"]
        failures = validator.validate_reconciliation_data(data)
        self.assertIn("proposed PR dispositions mismatch", failures)

    def test_base_main_must_match_recorded_current_main(self):
        data = current_manifest()
        data["proposed_candidate"]["base_main_sha"] = "b" * 40
        failures = validator.validate_reconciliation_data(data)
        self.assertIn(
            "canonicalization base_main_sha must equal current_main.sha",
            failures,
        )

    def test_source_lineage_terminal_must_match_stack(self):
        data = current_manifest()
        data["proposed_candidate"]["source_lineage_terminal_pr"] = 16
        failures = validator.validate_reconciliation_data(data)
        self.assertIn("source lineage terminal PR must be 17", failures)

        data = current_manifest()
        data["ancestry"]["current_stack"] = data["ancestry"]["current_stack"][:-1]
        failures = validator.validate_reconciliation_data(data)
        self.assertIn("source lineage stack mismatch", failures)

    def test_privacy_and_merge_holds_cannot_be_removed(self):
        data = current_manifest()
        data["unresolved"] = [
            "No protected merge/closure effect is authorized.",
        ]
        failures = validator.validate_reconciliation_data(data)
        self.assertIn("unresolved privacy/authority holds mismatch", failures)

    def test_additive_authority_field_fails_closed(self):
        data = current_manifest()
        data["merge_authority"] = True
        failures = validator.validate_reconciliation_data(data)
        self.assertTrue(
            any(
                failure.startswith("reconciliation fields mismatch:")
                for failure in failures
            )
        )

    def test_historical_classification_is_closed(self):
        data = current_manifest()
        data["ancestry"]["superseded_or_historical"][0][
            "classification"
        ] = "CURRENT_CANDIDATE"
        failures = validator.validate_reconciliation_data(data)
        self.assertIn("historical PR classification map mismatch", failures)

    def test_candidate_head_binding_rule_is_exact(self):
        data = current_manifest()
        data["proposed_candidate"]["head_binding_rule"] = (
            "the manifest decides currentness"
        )
        failures = validator.validate_reconciliation_data(data)
        self.assertIn("canonicalization head binding rule mismatch", failures)

    def test_mutation_does_not_leak_between_fixtures(self):
        first = current_manifest()
        second = copy.deepcopy(first)
        second["proposed_candidate"]["pr"] = 20
        self.assertNotEqual(
            [],
            validator.validate_reconciliation_data(second),
        )
        self.assertEqual(
            [],
            validator.validate_reconciliation_data(first),
        )


if __name__ == "__main__":
    unittest.main()
