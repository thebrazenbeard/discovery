import copy
import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "validate_discovery.py"

spec = importlib.util.spec_from_file_location("validate_discovery_currentness", TOOL)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


class DiscoveryCurrentnessIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.census = validator.load(validator.CENSUS)
        self.graph = validator.load(validator.GRAPH)
        self.intake = validator.load(validator.PUBLIC_INTAKE)

    def currentness_errors(self, census=None, graph=None, intake=None):
        return validator._validate_census_currentness_bindings(
            census or self.census,
            graph or self.graph,
            intake or self.intake,
        )

    def privacy_errors(self, census=None, graph=None):
        return validator._validate_opaque_graph_privacy(
            census or self.census,
            graph or self.graph,
        )

    def test_currentness_baseline_passes(self):
        self.assertEqual([], self.currentness_errors())
        self.assertEqual([], self.privacy_errors())

    def test_public_count_must_equal_public_list(self):
        census = copy.deepcopy(self.census)
        census["counts"]["public"] -= 1
        self.assertIn(
            "census public count does not match published public list",
            self.currentness_errors(census=census),
        )

    def test_total_must_equal_public_plus_private(self):
        census = copy.deepcopy(self.census)
        census["counts"]["total"] -= 1
        self.assertIn(
            "census total must equal public plus private",
            self.currentness_errors(census=census),
        )

    def test_public_digest_is_recomputed(self):
        census = copy.deepcopy(self.census)
        census["inventory_digests"]["public_names_sha256"] = "0" * 64
        self.assertIn(
            "census public names digest mismatch",
            self.currentness_errors(census=census),
        )

    def test_graph_and_intake_dates_are_bound_to_census(self):
        graph = copy.deepcopy(self.graph)
        graph["inventory_binding"]["observed_date"] = "2099-01-01"
        self.assertIn(
            "graph observed_date does not match census",
            self.currentness_errors(graph=graph),
        )

        intake = copy.deepcopy(self.intake)
        intake["current_public_cut"]["observed_date"] = "2099-01-01"
        self.assertIn(
            "public subject intake current cut date mismatch",
            self.currentness_errors(intake=intake),
        )

    def test_current_public_count_and_digest_are_bound(self):
        intake = copy.deepcopy(self.intake)
        intake["current_public_cut"]["public_count"] -= 1
        self.assertIn(
            "public subject intake current count mismatch",
            self.currentness_errors(intake=intake),
        )

        intake = copy.deepcopy(self.intake)
        intake["current_public_cut"]["public_names_sha256"] = "0" * 64
        self.assertIn(
            "public subject intake current public digest mismatch",
            self.currentness_errors(intake=intake),
        )

    def test_prior_cut_cannot_self_authenticate_by_mutating_list_and_count(self):
        intake = copy.deepcopy(self.intake)
        intake["prior_public_cut"]["public_repositories"] = intake[
            "prior_public_cut"
        ]["public_repositories"][:-1]
        intake["prior_public_cut"]["public_count"] -= 1
        intake["prior_public_cut"]["public_names_sha256"] = validator._canonical_name_digest(
            intake["prior_public_cut"]["public_repositories"]
        )
        errors = self.currentness_errors(intake=intake)
        self.assertIn(
            "public subject intake prior count not bound to historical census",
            errors,
        )
        self.assertIn(
            "public subject intake prior digest identity mismatch",
            errors,
        )
        self.assertIn(
            "public subject intake prior list diverges from historical census",
            errors,
        )

    def test_prior_cut_source_binding_is_exact(self):
        intake = copy.deepcopy(self.intake)
        intake["prior_public_cut"]["source_binding"]["blob_sha"] = "0" * 40
        self.assertIn(
            "public subject intake prior source binding mismatch",
            self.currentness_errors(intake=intake),
        )

    def test_opaque_private_node_identity_is_fixed(self):
        graph = copy.deepcopy(self.graph)
        node = next(
            item for item in graph["nodes"]
            if item.get("privacy") == "PRIVATE_OPAQUE"
        )
        node["id"] = "hidden-repository"
        self.assertIn(
            "opaque private cohort id invalid",
            self.privacy_errors(graph=graph),
        )

    def test_opaque_private_node_cannot_smuggle_identifier_in_label(self):
        graph = copy.deepcopy(self.graph)
        node = next(
            item for item in graph["nodes"]
            if item.get("privacy") == "PRIVATE_OPAQUE"
        )
        node["labels"] = ["35_PRIVATE_REPOSITORIES", "hidden-repository"]
        self.assertIn(
            "opaque private cohort label must contain aggregate count only",
            self.privacy_errors(graph=graph),
        )

    def test_opaque_private_edge_rejects_nonpublic_direct_repo_ref(self):
        graph = copy.deepcopy(self.graph)
        edge = next(
            item for item in graph["edges"]
            if "private-cohort" in {item.get("from"), item.get("to")}
        )
        edge["source_refs"] = [
            "thebrazenbeard/hidden-repository:main@" + "a" * 40
        ]
        self.assertIn(
            f"opaque private edge has unsafe source ref: {edge.get('edge_id')}",
            self.privacy_errors(graph=graph),
        )


if __name__ == "__main__":
    unittest.main()
