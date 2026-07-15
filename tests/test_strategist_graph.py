import importlib.util
import unittest

from app.strategist.graph import build_strategist_graph


HAS_LANGGRAPH = importlib.util.find_spec("langgraph") is not None


class FakeStrategistStore:
    def __init__(self):
        self.saved = {}
        self.events = []

    def load_current_reserve_state(self, scenario_id):
        return None

    def save_state(self, scenario_id, state):
        key = f"spr:scenario:{scenario_id}:strategist_state"
        self.saved[key] = state
        return key

    def save_output(self, output):
        key = f"spr:scenario:{output.scenario_id}:strategist_output"
        self.saved[key] = output.model_dump(mode="json")
        return key

    def publish_completed(self, scenario_id, output_key):
        event = {
            "event": "strategist.completed",
            "scenario_id": scenario_id,
            "next_agent": "allocator",
            "redis_key": output_key,
        }
        self.events.append(event)
        return event


@unittest.skipUnless(HAS_LANGGRAPH, "langgraph is not installed")
class StrategistGraphTests(unittest.TestCase):
    def test_graph_saves_output_and_publishes_completion_event(self):
        store = FakeStrategistStore()
        graph = build_strategist_graph(store)

        final_state = graph.invoke(
            {
                "raw_input": {
                    "scenario_id": "scenario-001",
                    "risk_level": "CRITICAL",
                    "net_daily_shortfall_bpd": 100_000,
                    "estimated_disruption_days": 10,
                    "current_spr_reserve_barrels": 2_000_000,
                    "minimum_safety_reserve_barrels": 500_000,
                    "daily_national_demand_bpd": 5_000_000,
                    "import_delay_days": 0,
                },
                "errors": [],
            }
        )

        output = final_state["final_output"]
        self.assertEqual(output.scenario_id, "scenario-001")
        self.assertEqual(output.release_duration_days, 10)
        self.assertEqual(output.uncovered_shortfall_bpd, 0)
        self.assertIn("spr:scenario:scenario-001:strategist_output", store.saved)
        self.assertEqual(store.events[0]["event"], "strategist.completed")


if __name__ == "__main__":
    unittest.main()
