from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ACCOUNTING = ROOT / "experiments" / "EFFECT_ENVELOPE_MAINTENANCE_ACCOUNTING_V1.json"


class EffectEnvelopeMaintenanceAccountingTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(ACCOUNTING.read_text(encoding="utf-8"))

    def test_core_arithmetic_is_exact(self):
        data = self.data
        self.assertEqual(data["producer_adapters"]["totals"]["physical_lines"], 501)
        self.assertEqual(data["observers"]["totals"]["physical_lines"], 450)
        self.assertEqual(data["contract"]["physical_lines"], 72)
        self.assertEqual(data["schema_distribution"]["private_copy_physical_lines"], 72)
        self.assertEqual(
            data["total_introduced_surface"]["core_physical_lines_including_private_schema_copy"],
            501 + 450 + 72 + 72,
        )
        self.assertEqual(
            data["total_introduced_surface"]["physical_lines_including_tests"],
            1095 + 804,
        )

    def test_actual_code_removal_is_zero(self):
        benefit = self.data["measured_benefit"]
        self.assertEqual(benefit["actual_preexisting_source_specific_parser_lines_deleted"], 0)
        self.assertEqual(benefit["actual_preexisting_source_specific_parser_files_deleted"], 0)
        self.assertEqual(
            benefit["classification"],
            "AVOIDED_FUTURE_INTEGRATION_SURFACE_NOT_ACTUAL_CODE_REMOVAL",
        )

    def test_avoided_integration_count_is_six(self):
        benefit = self.data["measured_benefit"]
        self.assertEqual(benefit["current_producer_specific_parser_integrations_avoided"], 6)
        self.assertEqual(
            benefit["derivation"],
            "3 qualified producer classes x 2 source-agnostic observers",
        )

    def test_private_observer_exposes_only_public_attestation(self):
        private = self.data["observers"]["private_second_observer"]
        self.assertEqual(
            set(private),
            {
                "public_attestation",
                "physical_lines",
                "nonblank_lines",
                "branch_lines",
                "source_behavior_check",
                "hosted_ci",
                "source_specific_parser_branches",
                "unknown_future_source_without_registration",
            },
        )
        self.assertEqual(
            private["public_attestation"]["opaque_handle"],
            "PRIVATE_OPAQUE_18f99857cf7f2beb",
        )
        self.assertEqual(private["hosted_ci"], "NOT_EXECUTED")

    def test_economic_result_fails_closed(self):
        result = self.data["economic_result"]
        self.assertFalse(result["positive_net_maintenance_reduction_established"])
        self.assertEqual(
            result["disposition"],
            "REMAIN_EXPERIMENTING_DO_NOT_PROMOTE_PROVEN_REUSABLE",
        )
        self.assertEqual(result["shared_runtime_library"], "NOT_JUSTIFIED")


if __name__ == "__main__":
    unittest.main()
