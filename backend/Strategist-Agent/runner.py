"""CLI and programmatic runner for the Strategist Agent."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, TextIO

from app.strategist.config import get_settings
from app.strategist.graph import build_strategist_graph
from app.strategist.redis_store import StrategistRedisStore
from app.strategist.schemas import StrategistOutput


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


def run_strategist(payload: dict[str, Any]) -> StrategistOutput:
    settings = get_settings()
    store = StrategistRedisStore(settings)
    graph = build_strategist_graph(store)

    final_state = graph.invoke({"raw_input": payload, "errors": []})
    errors = final_state.get("errors", [])
    if errors:
        raise RuntimeError("; ".join(errors))

    return final_state["final_output"]


def _load_payload_from_cli(
    argv: list[str] | None = None,
    stdin: TextIO | None = None,
) -> dict[str, Any]:
    """Load input from --sample, file, stdin, or default sample."""

    args = sys.argv[1:] if argv is None else argv
    input_stream = sys.stdin if stdin is None else stdin

    # Handle sample mode
    if "--sample" in args:
        print("Loading sample scenario...")
        return dict(SAMPLE_SCENARIO)

    # Handle JSON file input
    if args:
        print("Reading input from file...")
        return json.loads(Path(args[0]).read_text(encoding="utf-8"))

    # Handle stdin
    stdin_payload = _read_stdin_if_available(input_stream)
    if stdin_payload is not None:
        print("Reading input from stdin...")
        return json.loads(stdin_payload)

    # Default to sample
    print("Loading sample scenario...")
    return dict(SAMPLE_SCENARIO)

def _read_stdin_if_available(stdin: TextIO) -> str | None:
    try:
        if stdin.isatty():
            return None
    except (AttributeError, OSError):
        return None

    content = stdin.read()
    return content if content.strip() else None


def main() -> None:
    payload = _load_payload_from_cli()
    output = run_strategist(payload)
    print("Strategist execution completed.")
    print(output.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
