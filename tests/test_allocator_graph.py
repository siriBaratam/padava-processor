"""Tests for the Allocator Agent V2 — LangGraph workflow.

Verifies that every node executes in the correct order, state
transitions are valid, the service layer is invoked, and Redis
persistence / event publishing works end-to-end.
"""

import importlib.util
import unittest

from app.allocator.graph import build_allocator_graph

HAS_LANGGRAPH = importlib.util.find_spec("langgraph") is not None


class FakeAllocatorStore:
    """In-memory store implementing the V2 ``AllocatorStore`` protocol."""

    def __init__(self) -> None:
        self.saved: dict[str, object] = {}
        self.events: list[dict[str, object]] = []

    def load_strategist_output(self, scenario_id: str) -> dict[str, object] | None:
        return {
            "scenario_id": scenario_id,
            "recommended_spr_release_bpd": 250_000,
            "release_duration_days": 7,
            "total_release_barrels": 1_750_000,
            "remaining_spr_barrels": 3_250_000,
            "reserve_utilization_percent": 35,
            "uncovered_shortfall_bpd": 0,
            "coverage_status": "FULL_COVERAGE",
            "strategy_reasoning": "Test Strategist output for Allocator V2 graph.",
        }

    def load_state_sector_demands(
        self, scenario_id: str,
    ) -> list[dict[str, object]] | None:
        return None  # Demands come from the input payload.

    def save_state(self, scenario_id: str, state: dict[str, object]) -> str:
        key = f"spr:scenario:{scenario_id}:allocator_state"
        self.saved[key] = state
        return key

    def save_output(self, output: object) -> str:
        key = f"spr:scenario:{output.scenario_id}:allocator_output"
        self.saved[key] = output.model_dump(mode="json")
        return key

    def publish_completed(
        self, scenario_id: str, output_key: str,
    ) -> dict[str, object]:
        event: dict[str, object] = {
            "event": "allocator.completed",
            "scenario_id": scenario_id,
            "next_agent": "dealmaker",
            "redis_key": output_key,
        }
        self.events.append(event)
        return event


@unittest.skipUnless(HAS_LANGGRAPH, "langgraph is not installed")
class AllocatorGraphTests(unittest.TestCase):
    """End-to-end graph execution tests."""

    def setUp(self) -> None:
        self.store = FakeAllocatorStore()
        self.graph = build_allocator_graph(self.store)

    def _invoke(
        self,
        payload: dict[str, object] | None = None,
    ) -> dict[str, object]:
        if payload is None:
            payload = {
                "scenario_id": "scenario-001",
                "state_sector_demands": [
                    {
                        "state_code": "MH",
                        "state_name": "Maharashtra",
                        "sector_id": "HEALTHCARE",
                        "daily_demand_bpd": 120_000,
                    },
                    {
                        "state_code": "GJ",
                        "state_name": "Gujarat",
                        "sector_id": "DEFENSE",
                        "daily_demand_bpd": 80_000,
                    },
                ],
            }
        return self.graph.invoke({"raw_input": payload, "errors": []})

    def test_graph_produces_output(self) -> None:
        """The full graph executes without errors and returns a result."""
        final_state = self._invoke()
        self.assertIn("final_output", final_state)
        output = final_state["final_output"]
        self.assertEqual(output.scenario_id, "scenario-001")

    def test_graph_allocation_metrics_are_consistent(self) -> None:
        """National totals balance correctly."""
        final_state = self._invoke()
        output = final_state["final_output"]
        self.assertGreater(output.total_national_demand_bpd, 0)
        self.assertGreaterEqual(output.total_available_bpd, 0)
        self.assertEqual(
            output.total_allocated_bpd + output.total_unmet_bpd,
            output.total_national_demand_bpd,
        )

    def test_graph_saves_output_to_store(self) -> None:
        """Output is persisted after successful execution."""
        self._invoke()
        self.assertIn(
            "spr:scenario:scenario-001:allocator_output",
            self.store.saved,
        )
        saved = self.store.saved["spr:scenario:scenario-001:allocator_output"]
        self.assertEqual(saved["scenario_id"], "scenario-001")

    def test_graph_publishes_completion_event(self) -> None:
        """A completion event is published after successful execution."""
        self._invoke()
        self.assertEqual(len(self.store.events), 1)
        event = self.store.events[0]
        self.assertEqual(event["event"], "allocator.completed")
        self.assertEqual(event["scenario_id"], "scenario-001")
        self.assertEqual(event["next_agent"], "dealmaker")

    def test_graph_errors_on_missing_strategist_output(self) -> None:
        """When no Strategist output exists, the graph routes to END."""
        empty_store = FakeAllocatorStore()
        empty_store.load_strategist_output = lambda _: None  # type: ignore[method-assign]
        graph = build_allocator_graph(empty_store)

        final_state = graph.invoke({
            "raw_input": {
                "scenario_id": "missing-scenario",
                "state_sector_demands": [
                    {
                        "state_code": "MH",
                        "state_name": "Maharashtra",
                        "sector_id": "HEALTHCARE",
                        "daily_demand_bpd": 100_000,
                    },
                ],
            },
            "errors": [],
        })

        errors = final_state.get("errors", [])
        self.assertGreater(len(errors), 0)
        self.assertNotIn("final_output", final_state)

    def test_graph_all_level_summaries_present(self) -> None:
        """Level summaries are generated for each populated priority level."""
        final_state = self._invoke()
        output = final_state["final_output"]
        self.assertGreater(len(output.level_summaries), 0)

    def test_graph_delivery_schedule_is_generated(self) -> None:
        """A delivery schedule is always present in the output."""
        final_state = self._invoke()
        output = final_state["final_output"]
        self.assertGreater(len(output.delivery_priority_schedule), 0)

    def test_graph_logistics_context_is_placeholder(self) -> None:
        """The logistics context is a no-op placeholder."""
        final_state = self._invoke()
        output = final_state["final_output"]
        self.assertIn(
            "Logistics constraints are not yet enforced",
            output.logistics_context.logistics_note,
        )


if __name__ == "__main__":
    unittest.main()
