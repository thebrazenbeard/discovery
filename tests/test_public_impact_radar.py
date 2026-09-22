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
        self.assertEqual("docs/claim.md", item["exact_old_head_references"][0]["path"])
        self.assertEqual([1], item["exact_old_head_references"][0]["lines"])

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


if __name__ == "__main__":
    unittest.main()
