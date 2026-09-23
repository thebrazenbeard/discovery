import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "plan_vera_vcp_implementation.py"

spec = importlib.util.spec_from_file_location("plan_vera_vcp_implementation", TOOL)
planner = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(planner)


def registry(sources=None, unbound=None):
    return {
        "repository_sources": sources or [],
        "unbound_repositories": unbound or [],
    }


def subject(repo, action="ADD_VERA_SOURCE", vcp="NOT_CONTROL_PLANE"):
    return {
        "repository": repo,
        "exact_public_head": "a" * 40,
        "current_vera_registry_state": "ABSENT",
        "implementation_action": action,
        "vera_runtime_role": "TEST_ROLE",
        "activation_mode": "MECHANISM_RESEARCH_ONLY",
        "authority_ceiling": "test only",
        "availability_implies_activation": False,
        "vcp_disposition": vcp,
    }


def implementation_map(*subjects):
    return {
        "schema": "DISCOVERY_VERA_VCP_IMPLEMENTATION_MAP_V1",
        "subjects": list(subjects),
    }


class VeraVcpImplementationPlannerTests(unittest.TestCase):
    def test_active_candidate_satisfies_before_parallel_edit(self):
        repo = "thebrazenbeard/example"
        desired = implementation_map(subject(repo))
        candidate = registry(
            sources=[
                {
                    "repository": repo,
                    "runtime_role": "TEST_ROLE",
                    "activation_mode": "MECHANISM_RESEARCH_ONLY",
                    "authority_ceiling": "test only",
                    "privacy_class": "GOVERNED",
                    "availability_implies_activation": False,
                }
            ]
        )
        result = planner.plan(desired, registry(), candidate)
        self.assertEqual(
            "SATISFIED_BY_ACTIVE_CANDIDATE",
            result["actions"][0]["disposition"],
        )
        self.assertEqual(0, result["source_actions_required"])

    def test_active_candidate_role_difference_does_not_trigger_parallel_rewrite(self):
        repo = "thebrazenbeard/example"
        desired = implementation_map(subject(repo))
        candidate = registry(
            sources=[
                {
                    "repository": repo,
                    "runtime_role": "DIFFERENT_BOUNDED_ROLE",
                    "activation_mode": "EVIDENCE_ONLY",
                    "authority_ceiling": "candidate lane classification",
                    "availability_implies_activation": False,
                }
            ]
        )
        result = planner.plan(desired, registry(), candidate)
        action = result["actions"][0]
        self.assertEqual(
            "SATISFIED_BY_ACTIVE_CANDIDATE",
            action["disposition"],
        )
        self.assertEqual(0, result["source_actions_required"])
        self.assertEqual(
            "DIFFERENT_BOUNDED_ROLE",
            action["classification_difference"]["existing_runtime_role"],
        )

    def test_candidate_unbound_promotes_on_candidate_lane(self):
        repo = "thebrazenbeard/example"
        desired = implementation_map(subject(repo))
        candidate = registry(
            unbound=[
                {
                    "repository": repo,
                    "activation_mode": "NO_AUTO_BIND",
                    "reason": "not yet classified",
                    "availability_implies_activation": False,
                }
            ]
        )
        result = planner.plan(desired, registry(), candidate)
        self.assertEqual(
            "PROMOTE_FROM_ACTIVE_CANDIDATE_UNBOUND_TO_SOURCE",
            result["actions"][0]["disposition"],
        )
        self.assertEqual("ACTIVE_CANDIDATE", result["actions"][0]["preferred_target"])

    def test_missing_repo_generates_add_action(self):
        repo = "thebrazenbeard/example"
        result = planner.plan(implementation_map(subject(repo)), registry())
        self.assertEqual(
            "ADD_MISSING_VERA_SOURCE_ENTRY",
            result["actions"][0]["disposition"],
        )
        self.assertEqual(1, result["source_actions_required"])

    def test_vcp_candidate_is_review_frontier_not_control_promotion(self):
        repo = "thebrazenbeard/example"
        result = planner.plan(
            implementation_map(subject(repo, vcp="CONTROL_EXECUTION_SUPPORT_CANDIDATE")),
            registry(),
        )
        self.assertEqual(1, len(result["vcp_frontier"]))
        self.assertEqual(
            "CONTROL_INTEGRATION_REVIEW_REQUIRED",
            result["vcp_frontier"][0]["state"],
        )

    def test_repository_cannot_be_bound_and_unbound(self):
        repo = "thebrazenbeard/example"
        broken = registry(
            sources=[{"repository": repo}],
            unbound=[{"repository": repo}],
        )
        with self.assertRaisesRegex(
            planner.ImplementationPlanError,
            "appears bound and unbound",
        ):
            planner.plan(implementation_map(subject(repo)), broken)


if __name__ == "__main__":
    unittest.main()
