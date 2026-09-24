import importlib.util
import json
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
WATCH_TOOL = ROOT / "tools" / "check_public_currentness.py"
IMPACT_TOOL = ROOT / "tools" / "trace_public_impact.py"

watch_spec = importlib.util.spec_from_file_location("check_public_currentness", WATCH_TOOL)
watch = importlib.util.module_from_spec(watch_spec)
assert watch_spec.loader is not None
watch_spec.loader.exec_module(watch)

impact_spec = importlib.util.spec_from_file_location("trace_public_impact", IMPACT_TOOL)
impact = importlib.util.module_from_spec(impact_spec)
assert impact_spec.loader is not None
impact_spec.loader.exec_module(impact)


def subject(name, head, tree, branch="main", archived=False):
    return {
        "name": name,
        "default_branch": branch,
        "head": head,
        "tree_sha": tree,
        "archived": archived,
    }


class PublicImpactRadarTests(unittest.TestCase):
    def test_moved_head_traces_exact_evidence_references(self):
        old_head = "a" * 40
        new_head = "c" * 40
        expected = {"alpha": subject("alpha", old_head, "b" * 40)}
        observed = {"alpha": subject("alpha", new_head, "d" * 40)}
        currentness = watch.compare_public_subjects(expected, observed)

        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "docs").mkdir()
            (root / "experiments").mkdir()
            (root / "docs" / "claim.md").write_text(
                f"Exact subject: alpha:main@{old_head}\n",
                encoding="utf-8",
            )
            (root / "experiments" / "other.json").write_text(
                json.dumps({"unrelated": "x"}),
                encoding="utf-8",
            )

            result = impact.trace_exact_head_references(currentness, root=root)

        self.assertEqual("STALE_PUBLIC_SUBJECTS_TRACED", result["status"])
        self.assertEqual(1, result["subjects_with_exact_references"])
        item = result["subjects"][0]
        self.assertEqual("alpha", item["name"])
        self.assertEqual("MOVED", item["change_kind"])
        self.assertEqual("EXACT_REFERENCES_FOUND", item["reference_state"])
        self.assertEqual("BLOCK", item["impact_gate"])
        self.assertEqual("BLOCKING_CURRENTNESS_IMPACT", result["gate_status"])
        self.assertEqual("docs/claim.md", item["exact_old_head_references"][0]["path"])
        self.assertEqual([1], item["exact_old_head_references"][0]["lines"])
        self.assertEqual("BLOCK", item["impact_gate"])
        self.assertEqual("BLOCKING_CURRENTNESS_IMPACT", result["gate_status"])

    def test_absence_is_reported_as_gap_not_proof_of_no_dependency(self):
        expected = {"alpha": subject("alpha", "a" * 40, "b" * 40)}
        observed = {"alpha": subject("alpha", "c" * 40, "d" * 40)}
        currentness = watch.compare_public_subjects(expected, observed)

        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "claim.md").write_text("no exact ref here\n", encoding="utf-8")
            result = impact.trace_exact_head_references(currentness, root=root)

        self.assertEqual(1, result["subjects_without_exact_references"])
        self.assertEqual(
            "NO_EXACT_REFERENCE_FOUND",
            result["subjects"][0]["reference_state"],
        )
        self.assertIn(
            "does not prove that no dependency exists",
            result["negative_evidence_rule"],
        )
        self.assertEqual("NONBLOCKING_EXACT_HEAD_DRIFT", result["gate_status"])

    def test_removed_subject_traces_old_head(self):
        old_head = "e" * 40
        expected = {"alpha": subject("alpha", old_head, "f" * 40)}
        currentness = watch.compare_public_subjects(expected, {})

        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "portfolio").mkdir()
            (root / "portfolio" / "graph.json").write_text(
                json.dumps({"source": f"alpha:main@{old_head}"}),
                encoding="utf-8",
            )
            result = impact.trace_exact_head_references(currentness, root=root)

        item = result["subjects"][0]
        self.assertEqual("REMOVED", item["change_kind"])
        self.assertEqual(old_head, item["expected_head"])
        self.assertIsNone(item["observed_head"])
        self.assertEqual("EXACT_REFERENCES_FOUND", item["reference_state"])

    def test_added_subject_is_classification_frontier_not_stale_reference(self):
        observed = {"beta": subject("beta", "1" * 40, "2" * 40)}
        currentness = watch.compare_public_subjects({}, observed)

        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            result = impact.trace_exact_head_references(currentness, root=root)

        self.assertEqual([], result["subjects"])
        self.assertEqual(
            "UNCLASSIFIED_NEW_PUBLIC_SUBJECT",
            result["new_subjects"][0]["disposition"],
        )
        self.assertEqual("BLOCKING_CURRENTNESS_IMPACT", result["gate_status"])

    def test_baseline_self_reference_only_is_observe_only(self):
        old_head = "7" * 40
        new_head = "8" * 40
        expected = {"alpha": subject("alpha", old_head, "9" * 40)}
        observed = {"alpha": subject("alpha", new_head, "0" * 40)}
        currentness = watch.compare_public_subjects(expected, observed)

        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            baseline = root / "portfolio" / "PUBLIC_CURRENTNESS_BASELINE_20260924_V2.json"
            baseline.parent.mkdir()
            baseline.write_text(
                json.dumps({"repository": f"alpha@{old_head}"}),
                encoding="utf-8",
            )
            result = impact.trace_exact_head_references(currentness, root=root)

        item = result["subjects"][0]
        self.assertEqual("OBSERVE_ONLY", item["impact_gate"])
        self.assertEqual([], item["blocking_exact_old_head_references"])
        self.assertEqual("NONBLOCKING_EXACT_HEAD_DRIFT", result["gate_status"])

    def test_default_branch_drift_blocks_even_without_old_head_reference(self):
        expected = {"alpha": subject("alpha", "a" * 40, "b" * 40)}
        observed = {
            "alpha": subject(
                "alpha",
                "a" * 40,
                "b" * 40,
                branch="stable",
            )
        }
        currentness = watch.compare_public_subjects(expected, observed)

        with tempfile.TemporaryDirectory() as tmp:
            result = impact.trace_exact_head_references(
                currentness,
                root=pathlib.Path(tmp),
            )

        item = result["subjects"][0]
        self.assertEqual("BLOCK", item["impact_gate"])
        self.assertIn("default_branch", item["change_fields"])
        self.assertEqual("BLOCKING_CURRENTNESS_IMPACT", result["gate_status"])

    def test_current_report_has_no_stale_subjects(self):
        expected = {"alpha": subject("alpha", "a" * 40, "b" * 40)}
        currentness = watch.compare_public_subjects(expected, expected)

        with tempfile.TemporaryDirectory() as tmp:
            result = impact.trace_exact_head_references(
                currentness,
                root=pathlib.Path(tmp),
            )

        self.assertEqual("NO_STALE_PUBLIC_SUBJECTS", result["status"])
        self.assertEqual(0, result["stale_subject_count"])
        self.assertEqual("CURRENT", result["gate_status"])


if __name__ == "__main__":
    unittest.main()
