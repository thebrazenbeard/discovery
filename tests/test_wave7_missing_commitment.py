import copy
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("snapshot_compare", ROOT / "tools" / "compare_portfolio_snapshots.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class CommitmentComparisonTests(unittest.TestCase):
    def test_missing_hmac_with_matching_key_does_not_verify_private_currentness(self):
        prior = {
            "schema": module.SCHEMA,
            "observed_at": "2026-10-10",
            "public_repositories": [],
            "private_inventory_commitment": {"key_id":"same-key", "hmac_sha256":None, "count":1},
            "all_inventory_commitment": {"key_id":"same-key", "hmac_sha256":None, "count":1},
            "counts":{"total":1,"public":0,"private":1},
        }
        result=module.compare_snapshots(prior, copy.deepcopy(prior))
        self.assertNotEqual(result["private_set_state"], "UNCHANGED")
        self.assertNotEqual(result["all_set_state"], "UNCHANGED")
        self.assertNotEqual(result["currentness"], "CURRENT_RELATIVE_TO_NEW_SNAPSHOT")
