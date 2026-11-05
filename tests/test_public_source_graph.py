"""Public contract tests for source-derived graph edges and non-edges."""

import importlib.util
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "build_public_dependency_graph", ROOT / "tools" / "build_public_dependency_graph.py"
)
graph = importlib.util.module_from_spec(spec)
spec.loader.exec_module(graph)
OWNER = "example-owner"


def source(path, content):
    return {"path": path, "content": content, "blob_sha": graph._git_blob_oid(content)}


def subject(name, *files, visibility="public"):
    return {
        "repository": f"{OWNER}/{name}",
        "visibility": visibility,
        "commit": "a" * 40,
        "files": list(files),
    }


def corpus(*subjects):
    return {"schema": graph.SCHEMA, "owner": OWNER, "subjects": list(subjects)}


class PublicSourceGraphTests(unittest.TestCase):
    def test_python_manifest_and_import_produce_distinct_source_edges(self):
        a = subject(
            "alpha",
            source("pyproject.toml", '[project]\nname="alpha"\ndependencies=["beta-lib>=1"]\n'),
            source("alpha/cli.py", "from beta_lib.api import execute\n"),
        )
        b = subject(
            "beta",
            source("pyproject.toml", '[project]\nname="beta-lib"\n[tool.setuptools]\npackages=["beta_lib"]\n'),
            source("beta_lib/__init__.py", ""),
        )
        result = graph.build_graph(corpus(a, b))
        self.assertEqual(2, result["counts"]["edges"])
        self.assertEqual(
            {"PYPROJECT_DECLARATION", "PYTHON_SOURCE_IMPORT"},
            {e["relation"] for e in result["edges"]},
        )
        self.assertTrue(all(e["runtime_connection"] == "NOT_VERIFIED" for e in result["edges"]))
        self.assertEqual([], result["static_reference_cycles"])

    def test_npm_manifest_cycle_detected_but_not_called_runtime(self):
        a = subject("a", source("package.json", '{"name":"@a/a","dependencies":{"@a/b":"^1"}}'))
        b = subject("b", source("package.json", '{"name":"@a/b","dependencies":{"@a/a":"^1"}}'))
        result = graph.build_graph(corpus(a, b))
        self.assertEqual([[f"{OWNER}/a", f"{OWNER}/b"]], result["static_reference_cycles"])
        self.assertEqual(2, len(result["edges"]))
        self.assertEqual("SOURCE_DERIVED_NOT_RUNTIME_VERIFIED", result["status"])

    def test_duplicate_public_providers_suppress_false_cross_repo_import(self):
        portal = subject(
            "portal", source("pyproject.toml", '[project]\nname="project-runner"\n[tool.setuptools]\npackages=["portal","runner"]\n'),
            source("portal/cli.py", "from runner.tasks import run\n"),
        )
        runner = subject("project-runner", source("pyproject.toml", '[project]\nname="project-runner"\n[tool.setuptools]\npackages=["runner"]\n'))
        result = graph.build_graph(corpus(portal, runner))
        self.assertEqual([], result["edges"])
        self.assertEqual({"PYTHON_DISTRIBUTION", "PYTHON_MODULE"}, {x["kind"] for x in result["provider_conflicts"]})
        self.assertEqual(1, result["counts"]["ambiguous_provider"])

    def test_textual_mentions_are_not_manifest_or_import_evidence(self):
        a = subject("a", source("README.md", "Run beta-api through the network. Not an installed edge."))
        b = subject("b", source("pyproject.toml", '[project]\nname="beta-api"\n'))
        result = graph.build_graph(corpus(a, b))
        self.assertEqual([], result["edges"])
        self.assertEqual(0, result["counts"]["external_or_unmapped"])

    def test_declared_source_pin_is_historical_reference_only(self):
        pin = json.dumps({"schema": graph.PIN_SCHEMA, "repository": f"{OWNER}/core", "commit": "b" * 40, "tree": "c" * 40,
                          "private_overlay_inputs": ["DO_NOT_DISCLOSE_PRIVATE_PATH"]})
        bus = subject("bus", source(graph.PIN_PATH, pin))
        core = subject("core")
        result = graph.build_graph(corpus(bus, core))
        self.assertEqual(1, len(result["edges"]))
        edge = result["edges"][0]
        self.assertEqual("DECLARED_HISTORICAL_SOURCE_PIN", edge["relation"])
        self.assertEqual("DIFFERS_FROM_SUPPLIED_SUBJECT", edge["pinned_head_relation"])
        self.assertNotIn("DO_NOT_DISCLOSE_PRIVATE_PATH", json.dumps(result))

    def test_unmapped_import_and_dependency_do_not_create_repositories(self):
        a = subject("a", source("requirements.txt", "requests>=2\n"), source("a/main.py", "import json\n"))
        result = graph.build_graph(corpus(a))
        self.assertEqual(1, len(result["nodes"]))
        self.assertEqual([], result["edges"])
        self.assertEqual(2, result["counts"]["external_or_unmapped"])

    def test_private_records_are_rejected_before_output(self):
        with self.assertRaisesRegex(graph.GraphInputError, "private"):
            graph.build_graph(corpus(subject("private-subject", visibility="private")))

    def test_forged_blob_is_rejected(self):
        a = subject("a", source("package.json", '{"name":"alpha"}'))
        a["files"][0]["blob_sha"] = "0" * 40
        with self.assertRaisesRegex(graph.GraphInputError, "digest mismatch"):
            graph.build_graph(corpus(a))

    def test_source_path_traversal_is_rejected(self):
        with self.assertRaisesRegex(graph.GraphInputError, "traversal"):
            graph.build_graph(corpus(subject("a", source("../private.txt", "x"))))

    def test_malformed_public_identity_is_rejected(self):
        a = subject("a")
        a["commit"] = "not-a-commit"
        with self.assertRaises(graph.GraphInputError):
            graph.build_graph(corpus(a))

    def test_direct_url_and_local_npm_aliases_create_no_false_edges(self):
        a = subject("a", source("package.json", '{"name":"a","dependencies":{"beta":"npm:other@1","other":"file:../beta"}}'))
        b = subject("b", source("package.json", '{"name":"beta"}'))
        result = graph.build_graph(corpus(a, b))
        self.assertEqual([], result["edges"])

    def test_same_name_python_vs_npm_is_not_a_dependency(self):
        a = subject("python-app", source("pyproject.toml", '[project]\nname="python-app"\ndependencies=["shared-name>=1"]\n'))
        b = subject("npm-app", source("package.json", '{"name":"shared-name"}'))
        result = graph.build_graph(corpus(a, b))
        self.assertEqual([], result["edges"])
        self.assertEqual([], result["provider_conflicts"])

    def test_malformed_optional_dependencies_rejected(self):
        a = subject("a", source("pyproject.toml", '[project]\nname="a"\noptional-dependencies=["not-a-table"]\n'))
        with self.assertRaises(graph.GraphInputError):
            graph.build_graph(corpus(a))

    def test_duplicate_json_keys_fail_closed_before_manifest_parsing(self):
        a = subject("a", source("package.json", '{"name":"a","name":"b"}'))
        with self.assertRaisesRegex(graph.GraphInputError, "duplicate JSON"):
            graph.build_graph(corpus(a))

    def test_duplicate_visibility_keys_fail_closed_at_cli_parser(self):
        with self.assertRaisesRegex(graph.GraphInputError, "duplicate JSON"):
            graph._strict_json('{"visibility":"private","visibility":"public"}')

    def test_deterministic_order_independent_of_corpus_subject_order(self):
        a = subject("a", source("package.json", '{"name":"a","dependencies":{"b":"^1"}}'))
        b = subject("b", source("package.json", '{"name":"b"}'))
        self.assertEqual(graph.build_graph(corpus(a, b)), graph.build_graph(corpus(b, a)))

    def test_rejects_duplicate_casefold_repositories(self):
        with self.assertRaisesRegex(graph.GraphInputError, "duplicate"):
            graph.build_graph(corpus(subject("Alpha"), subject("alpha")))

    def test_source_hash_is_byte_sensitive(self):
        content = "héllo\n"
        self.assertNotEqual(graph._git_blob_oid(content), graph._git_blob_oid("hello\n"))

    def test_tracked_public_slice_preserves_narrow_claim_ceiling(self):
        observed = json.loads(
            (ROOT / "portfolio" / "PUBLIC_SOURCE_GRAPH_20261105_SLICE_V1.json").read_text(encoding="utf-8")
        )
        self.assertEqual(graph.GRAPH_SCHEMA, observed["schema"])
        self.assertEqual("SOURCE_DERIVED_NOT_RUNTIME_VERIFIED", observed["status"])
        self.assertEqual(4, observed["counts"]["public_nodes"])
        self.assertEqual(1, observed["counts"]["edges"])
        self.assertEqual(
            {"PYTHON_DISTRIBUTION", "PYTHON_MODULE"},
            {x["kind"] for x in observed["provider_conflicts"]},
        )
        self.assertTrue(all(x["runtime_connection"] == "NOT_VERIFIED" for x in observed["edges"]))


if __name__ == "__main__":
    unittest.main()
