"""Frozen V1 safety and unqualified V2 public-cut proposals."""

from __future__ import annotations

import copy
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location(
    "refresh_public_blob_evidence_v2_guard", TOOLS / "refresh_public_blob_evidence.py"
)
reproducer = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(reproducer)


def _subject(name: str, head: str) -> dict:
    return {
        "name": name,
        "default_branch": "main",
        "head": head,
        "tree_sha": "d" * 40,
        "archived": False,
        "blobs": [],
    }


class PublicCutProposalV2Tests(unittest.TestCase):
    def test_new_cut_is_unreviewed_and_absences_are_not_deletions(self):
        previous = {
            "changed": _subject("changed", "a" * 40),
            "absent": _subject("absent", "b" * 40),
        }
        observed = {
            "changed": _subject("changed", "c" * 40),
            "added": _subject("added", "e" * 40),
        }
        proposal = reproducer.build_public_cut_proposal_v2(
            previous, observed, observed_date="2026-10-28", owner="thebrazenbeard"
        )
        self.assertEqual("DISCOVERY_PUBLIC_CUT_PROPOSAL_V2", proposal["schema"])
        self.assertEqual("UNREVIEWED_NOT_ADMITTED", proposal["disposition"])
        self.assertEqual("NOT_ATTESTED", proposal["snapshot_stability"])
        self.assertEqual(["added"], proposal["added_names"])
        self.assertEqual(["absent"], proposal["absent_from_public_inventory"])
        self.assertEqual(["changed"], proposal["changed_source_names"])
        self.assertEqual("UNRESOLVED", proposal["transitions"]["added"]["review_disposition"])
        self.assertEqual("UNRESOLVED", proposal["transitions"]["absent"]["review_disposition"])
        self.assertNotIn("deleted", json.dumps(proposal).lower())

    def test_proposal_refuses_noncanonical_date_and_invalid_head(self):
        previous = {"prior": _subject("prior", "a" * 40)}
        with self.assertRaisesRegex(reproducer.BlobEvidenceError, "YYYY-MM-DD"):
            reproducer.build_public_cut_proposal_v2(
                previous, previous, observed_date="2026-1-2", owner="thebrazenbeard"
            )
        invalid = {"prior": _subject("prior", "x" * 40)}
        with self.assertRaisesRegex(reproducer.BlobEvidenceError, "Git SHA"):
            reproducer.build_public_cut_proposal_v2(
                previous, invalid, observed_date="2026-10-28", owner="thebrazenbeard"
            )

    def test_legacy_set_change_write_is_refused_before_live_collection(self):
        with patch.object(reproducer, "collect_live_subjects") as collect, patch.object(
            reproducer, "_write_rendered"
        ) as writer:
            outcome = reproducer.main([
                "--write", "--accept-set-change", "--observed-date", "2026-10-28"
            ])
        self.assertEqual(2, outcome)
        collect.assert_not_called()
        writer.assert_not_called()

    def test_write_refuses_modified_v1_even_without_set_change(self):
        previous = reproducer.subjects_from_committed_shards()
        observed = copy.deepcopy(previous)
        observed["semanticatlas"]["head"] = "a" * 40
        with patch.object(reproducer, "collect_live_subjects", return_value=observed), patch.object(
            reproducer, "_write_rendered"
        ) as writer:
            outcome = reproducer.main([
                "--write", "--observed-date", "2026-10-28"
            ])
        self.assertEqual(2, outcome)
        writer.assert_not_called()

    def test_proposal_file_is_create_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidate.json"
            path.write_text("prior", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                reproducer.write_new_public_cut_proposal_v2(path, {"schema": "probe"})
            self.assertEqual("prior", path.read_text(encoding="utf-8"))

    def test_proposal_does_not_follow_dangling_final_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.json"
            alias = Path(tmp) / "alias.json"
            alias.symlink_to(target)
            with self.assertRaisesRegex(reproducer.BlobEvidenceError, "symlink"):
                reproducer.write_new_public_cut_proposal_v2(
                    alias, {"schema": "forbidden-symlink-write"}
                )
            self.assertTrue(alias.is_symlink())
            self.assertFalse(target.exists())

    def test_low_level_writer_refuses_frozen_v1(self):
        path = reproducer.SHARD_PATHS[0]
        before = path.read_bytes()
        with self.assertRaisesRegex(reproducer.BlobEvidenceError, "frozen V1"):
            reproducer._write_rendered({path: "bad historical replacement"})
        self.assertEqual(before, path.read_bytes())

    def test_v2_inventory_observes_live_discovery_self_head(self):
        prior = reproducer.subjects_from_committed_shards()
        actual = {
            name: {key: value for key, value in subject.items() if key != "blobs"}
            for name, subject in prior.items()
        }
        actual["discovery"]["head"] = (
            "f" * 40 if prior["discovery"]["head"] != "f" * 40 else "e" * 40
        )
        with patch.object(
            reproducer.GitHubPublicInventoryClient, "inventory", return_value=actual
        ) as inventory:
            observed = reproducer.collect_public_cut_observed_inventory(
                "thebrazenbeard", token=None
            )
        inventory.assert_called_once_with("thebrazenbeard")
        self.assertEqual(actual["discovery"]["head"], observed["discovery"]["head"])
        proposal = reproducer.build_public_cut_proposal_v2(
            prior, observed, observed_date="2026-10-28", owner="thebrazenbeard"
        )
        self.assertIn("discovery", proposal["changed_source_names"])
        self.assertEqual(
            actual["discovery"]["head"],
            proposal["transitions"]["discovery"]["observed"]["head"],
        )

    def test_proposal_cli_preserves_v1_bytes_and_never_admits_membership(self):
        historical_before = {
            path: path.read_bytes()
            for path in (*reproducer.SHARD_PATHS, reproducer.SCAN_PATH)
        }
        observed = reproducer.subjects_from_committed_shards()
        observed["added"] = _subject("added", "a" * 40)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "public_cut_candidate_v2.json"
            with patch.object(reproducer, "collect_public_cut_observed_inventory", return_value=observed):
                code = reproducer.main([
                    "--proposal", "--proposal-path", str(path),
                    "--observed-date", "2026-10-28",
                ])
            self.assertEqual(0, code)
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual("UNREVIEWED_NOT_ADMITTED", payload["disposition"])
            self.assertEqual("thebrazenbeard", payload["owner"])
            self.assertEqual(["added"], payload["added_names"])
            with patch.object(reproducer, "collect_public_cut_observed_inventory", return_value=observed):
                self.assertEqual(2, reproducer.main([
                    "--proposal", "--proposal-path", str(path),
                    "--observed-date", "2026-10-28",
                ]))
        self.assertEqual(
            historical_before,
            {path: path.read_bytes() for path in historical_before},
        )

    def test_proposal_rejects_cross_owner_before_collection(self):
        with patch.object(reproducer, "collect_public_cut_observed_inventory") as collect:
            code = reproducer.main([
                "--proposal", "--owner", "someone-else",
                "--observed-date", "2026-10-28",
                "--proposal-path", "/tmp/uncreated-cross-owner-probe.json",
            ])
        self.assertEqual(2, code)
        collect.assert_not_called()
        with self.assertRaisesRegex(reproducer.BlobEvidenceError, "owner"):
            reproducer.build_public_cut_proposal_v2(
                {}, {}, observed_date="2026-10-28", owner="someone-else"
            )

    def test_cli_help_declares_v1_write_is_non_mutating(self):
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit) as outcome:
            reproducer.main(["--help"])
        self.assertEqual(0, outcome.exception.code)
        help_text = " ".join(output.getvalue().split())
        self.assertIn("legacy frozen V1 compare-only compatibility; never writes", help_text)
        self.assertIn("create unreviewed V2 public identity proposal", help_text)


if __name__ == "__main__":
    unittest.main()
