import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "validate_discovery.py"

spec = importlib.util.spec_from_file_location("validate_discovery", TOOL)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class DiscoveryGraphTests(unittest.TestCase):
    def test_repository_validation_passes(self):
        self.assertEqual([], module.validate())

    def test_graph_allows_multiple_relationships_without_numeric_confidence(self):
        graph = module.load(module.GRAPH)
        serialized = module.GRAPH.read_text(encoding="utf-8")
        self.assertNotIn('"confidence"', serialized)
        self.assertGreaterEqual(len(graph["edges"]), 5)

    def test_private_inventory_is_opaque(self):
        graph = module.load(module.GRAPH)
        for node in graph["nodes"]:
            self.assertNotEqual("PRIVATE", node.get("privacy"))
        self.assertTrue(
            any(node.get("kind") == "OPAQUE_PRIVATE_COHORT" for node in graph["nodes"])
        )


    def test_census_public_count_mutation_fails(self):
        census = module.load(module.CENSUS)
        graph = module.load(module.GRAPH)
        intake = module.load(module.PUBLIC_INTAKE)
        census["counts"]["public"] -= 1
        errors = module._validate_census_currentness_bindings(census, graph, intake)
        self.assertIn("census public count does not match published public list", errors)

    def test_census_total_arithmetic_mutation_fails(self):
        census = module.load(module.CENSUS)
        graph = module.load(module.GRAPH)
        intake = module.load(module.PUBLIC_INTAKE)
        census["counts"]["total"] += 1
        errors = module._validate_census_currentness_bindings(census, graph, intake)
        self.assertIn("census total must equal public plus private", errors)

    def test_census_public_digest_mutation_fails(self):
        census = module.load(module.CENSUS)
        graph = module.load(module.GRAPH)
        intake = module.load(module.PUBLIC_INTAKE)
        census["inventory_digests"]["public_names_sha256"] = "0" * 64
        errors = module._validate_census_currentness_bindings(census, graph, intake)
        self.assertIn("census public names digest mismatch", errors)

    def test_census_date_join_mutation_fails(self):
        census = module.load(module.CENSUS)
        graph = module.load(module.GRAPH)
        intake = module.load(module.PUBLIC_INTAKE)
        graph["inventory_binding"]["observed_date"] = "2099-01-01"
        errors = module._validate_census_currentness_bindings(census, graph, intake)
        self.assertIn("graph observed_date does not match census", errors)

    def test_intake_current_count_mutation_fails(self):
        census = module.load(module.CENSUS)
        graph = module.load(module.GRAPH)
        intake = module.load(module.PUBLIC_INTAKE)
        intake["current_public_cut"]["public_count"] -= 1
        errors = module._validate_census_currentness_bindings(census, graph, intake)
        self.assertIn("public subject intake current count mismatch", errors)

    def test_prior_cut_cannot_self_authenticate_by_mutating_list(self):
        census = module.load(module.CENSUS)
        graph = module.load(module.GRAPH)
        intake = module.load(module.PUBLIC_INTAKE)
        intake["prior_public_cut"]["public_repositories"] = [
            name
            for name in intake["prior_public_cut"]["public_repositories"]
            if name != "world-zero"
        ]
        intake["prior_public_cut"]["public_count"] -= 1
        errors = module._validate_census_currentness_bindings(census, graph, intake)
        self.assertIn(
            "public subject intake prior list diverges from historical census",
            errors,
        )

    def test_prior_cut_source_binding_mutation_fails(self):
        census = module.load(module.CENSUS)
        graph = module.load(module.GRAPH)
        intake = module.load(module.PUBLIC_INTAKE)
        intake["prior_public_cut"]["source_binding"]["blob"] = "0" * 40
        errors = module._validate_census_currentness_bindings(census, graph, intake)
        self.assertIn(
            "public subject intake prior source binding mismatch",
            errors,
        )

    def test_opaque_private_node_identifier_is_fixed(self):
        census = module.load(module.CENSUS)
        graph = module.load(module.GRAPH)
        node = next(
            item for item in graph["nodes"]
            if item.get("kind") == "OPAQUE_PRIVATE_COHORT"
        )
        node["id"] = "raw-private-repository-name"
        errors = module._validate_opaque_graph_privacy(census, graph)
        self.assertIn("opaque private cohort id invalid", errors)

    def test_opaque_private_direct_repository_ref_fails(self):
        census = module.load(module.CENSUS)
        graph = module.load(module.GRAPH)
        edge = next(
            item for item in graph["edges"]
            if item.get("to") == "private-cohort"
        )
        edge["source_refs"].append(
            "thebrazenbeard/not-in-public-census:main@"
            + "1" * 40
        )
        errors = module._validate_opaque_graph_privacy(census, graph)
        self.assertIn(
            "opaque private edge has unsafe source ref: DISCOVERY_CENSUS_PRIVATE_OPAQUE_CONSUMER",
            errors,
        )

    def test_opaque_private_attestation_ref_shape_is_enforced(self):
        census = module.load(module.CENSUS)
        graph = module.load(module.GRAPH)
        edge = next(
            item for item in graph["edges"]
            if item.get("to") == "private-cohort"
        )
        edge["source_refs"].append("private-attestation:raw-name")
        errors = module._validate_opaque_graph_privacy(census, graph)
        self.assertIn(
            "opaque private edge has unsafe source ref: DISCOVERY_CENSUS_PRIVATE_OPAQUE_CONSUMER",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
