"""CLI and programmatic runner for the Strategist Agent."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, TextIO

from config import get_settings
from graph import build_strategist_graph
from redis_store import StrategistRedisStore
from schemas import StrategistOutput


SAMPLE_SCENARIO: dict[str, Any] = {
    "scenario_id": "demo-scenario-001",
    "risk_level": "HIGH",
    "net_daily_shortfall_bpd": 350_000,
    "estimated_disruption_days": 14,
    "current_spr_reserve_barrels": 5_000_000,
    "minimum_safety_reserve_barrels": 1_500_000,
    "daily_national_demand_bpd": 5_200_000,
    "import_delay_days": 7,
}


class DemoStrategistStore:
    """In-memory store used only for sample/demo Strategist runs."""

    def __init__(self) -> None:
        self.saved: dict[str, Any] = {}
        self.events: list[dict[str, Any]] = []

    def load_current_reserve_state(self, scenario_id: str) -> dict[str, Any] | None:
        return None

    def save_state(self, scenario_id: str, state: dict[str, Any]) -> str:
        key = f"spr:scenario:{scenario_id}:strategist_state"
        self.saved[key] = state
        return key

    def save_output(self, output: StrategistOutput) -> str:
        key = f"spr:scenario:{output.scenario_id}:strategist_output"
        self.saved[key] = output.model_dump(mode="json")
        return key

    def publish_completed(self, scenario_id: str, output_key: str) -> dict[str, Any]:
        event = {
            "event": "strategist.completed",
            "scenario_id": scenario_id,
            "next_agent": "allocator",
            "redis_key": output_key,
        }
        self.events.append(event)
        return event


def run_strategist(
    payload: dict[str, Any],
    store: Any | None = None,
) -> StrategistOutput:
    effective_store = store or StrategistRedisStore(get_settings())
    graph = build_strategist_graph(effective_store)

    final_state = graph.invoke({"raw_input": payload, "errors": []})
    errors = final_state.get("errors", [])
    if errors:
        raise RuntimeError("; ".join(errors))

    return final_state["final_output"]


def _load_payload_from_cli(
    argv: list[str] | None = None,
    stdin: TextIO | None = None,
) -> tuple[dict[str, Any], bool]:
    """Load input from --sample, file, stdin, or default sample."""

    args = sys.argv[1:] if argv is None else argv
    input_stream = sys.stdin if stdin is None else stdin

    # Handle sample mode
    if "--sample" in args:
        print("Loading sample scenario...")
        return dict(SAMPLE_SCENARIO), True

    # Handle JSON file input
    if args:
        print("Reading input from file...")
        return json.loads(Path(args[0]).read_text(encoding="utf-8")), False

    # Handle stdin
    stdin_payload = _read_stdin_if_available(input_stream)
    if stdin_payload is not None:
        print("Reading input from stdin...")
        return json.loads(stdin_payload), False

    # Default to sample
    print("Loading sample scenario...")
    return dict(SAMPLE_SCENARIO), True

def _read_stdin_if_available(stdin: TextIO) -> str | None:
    try:
        if stdin.isatty():
            return None
    except (AttributeError, OSError):
        return None

    content = stdin.read()
    return content if content.strip() else None


def main() -> None:
    payload, using_sample = _load_payload_from_cli()
    store = DemoStrategistStore() if using_sample else None
    output = run_strategist(payload, store=store)
    print("Strategist execution completed.")
    print(output.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
