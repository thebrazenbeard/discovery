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


if __name__ == "__main__":
    unittest.main()
