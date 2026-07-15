"""CLI and programmatic runner for the Allocator Agent V2.

Supports three execution modes (same pattern as the Strategist runner):

1. **Sample / demo** — no arguments; uses ``SAMPLE_SCENARIO`` and
   a ``DemoAllocatorStore`` with ``SAMPLE_STRATEGIST_OUTPUT``.
2. **JSON file** — pass a file path as the first CLI argument.
3. **stdin** — pipe JSON input via standard input.

The runner is intentionally thin: it parses input, invokes the
LangGraph workflow, and prints the result.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, TextIO

from app.allocator.config import get_settings
from app.allocator.graph import build_allocator_graph
from app.allocator.redis_store import AllocatorRedisStore
from app.allocator.schemas import AllocatorOutput


SAMPLE_SCENARIO: dict[str, Any] = {
    "scenario_id": "demo-scenario-001",
    "state_sector_demands": [
        {
            "state_code": "MH",
            "state_name": "Maharashtra",
            "sector_id": "HEALTHCARE",
            "daily_demand_bpd": 120_000,
        },
        {
            "state_code": "MH",
            "state_name": "Maharashtra",
            "sector_id": "DEFENSE",
            "daily_demand_bpd": 80_000,
        },
        {
            "state_code": "MH",
            "state_name": "Maharashtra",
            "sector_id": "AGRICULTURE",
            "daily_demand_bpd": 90_000,
        },
        {
            "state_code": "GJ",
            "state_name": "Gujarat",
            "sector_id": "HEALTHCARE",
            "daily_demand_bpd": 90_000,
        },
        {
            "state_code": "GJ",
            "state_name": "Gujarat",
            "sector_id": "DEFENSE",
            "daily_demand_bpd": 60_000,
        },
        {
            "state_code": "GJ",
            "state_name": "Gujarat",
            "sector_id": "PUBLIC_TRANSPORT",
            "daily_demand_bpd": 50_000,
        },
        {
            "state_code": "TN",
            "state_name": "Tamil Nadu",
            "sector_id": "HEALTHCARE",
            "daily_demand_bpd": 100_000,
        },
        {
            "state_code": "TN",
            "state_name": "Tamil Nadu",
            "sector_id": "POWER_GENERATION",
            "daily_demand_bpd": 70_000,
        },
        {
            "state_code": "TN",
            "state_name": "Tamil Nadu",
            "sector_id": "COMMERCIAL",
            "daily_demand_bpd": 60_000,
        },
        {
            "state_code": "UP",
            "state_name": "Uttar Pradesh",
            "sector_id": "HEALTHCARE",
            "daily_demand_bpd": 110_000,
        },
        {
            "state_code": "UP",
            "state_name": "Uttar Pradesh",
            "sector_id": "AGRICULTURE",
            "daily_demand_bpd": 140_000,
        },
        {
            "state_code": "UP",
            "state_name": "Uttar Pradesh",
            "sector_id": "PRIVATE_CONSUMPTION",
            "daily_demand_bpd": 80_000,
        },
    ],
}

SAMPLE_STRATEGIST_OUTPUT: dict[str, Any] = {
    "scenario_id": "demo-scenario-001",
    "recommended_spr_release_bpd": 250_000,
    "release_duration_days": 7,
    "total_release_barrels": 1_750_000,
    "remaining_spr_barrels": 3_250_000,
    "reserve_utilization_percent": 35,
    "uncovered_shortfall_bpd": 0,
    "coverage_status": "FULL_COVERAGE",
    "strategy_reasoning": "Demo Strategist output for Allocator V2 runner.",
}


class DemoAllocatorStore:
    """In-memory store used only for no-argument demo runs.

    Provides a fixed ``StrategistOutput`` and keeps saved data in
    local dicts for inspection.  Implements the ``AllocatorStore``
    protocol.
    """

    def __init__(self, strategist_output: dict[str, Any]) -> None:
        self.strategist_output = strategist_output
        self.saved: dict[str, Any] = {}
        self.events: list[dict[str, Any]] = []

    # ── Read ───────────────────────────────────────────────────

    def load_strategist_output(self, scenario_id: str) -> dict[str, Any] | None:
        if self.strategist_output["scenario_id"] != scenario_id:
            return None
        return self.strategist_output

    def load_state_sector_demands(
        self, scenario_id: str,
    ) -> list[dict[str, Any]] | None:
        return None  # Demands come from the input in sample mode.

    # ── Write ──────────────────────────────────────────────────

    def save_state(self, scenario_id: str, state: dict[str, Any]) -> str:
        key = f"spr:scenario:{scenario_id}:allocator_state"
        self.saved[key] = state
        return key

    def save_output(self, output: AllocatorOutput) -> str:
        key = f"spr:scenario:{output.scenario_id}:allocator_output"
        self.saved[key] = output.model_dump(mode="json")
        return key

    def publish_completed(
        self, scenario_id: str, output_key: str,
    ) -> dict[str, Any]:
        event = {
            "event": "allocator.completed",
            "scenario_id": scenario_id,
            "next_agent": "dealmaker",
            "redis_key": output_key,
        }
        self.events.append(event)
        return event


# ──────────────────────────────────────────────
# Programmatic entry point
# ──────────────────────────────────────────────


def run_allocator(
    payload: dict[str, Any],
    store: Any | None = None,
) -> AllocatorOutput:
    """Execute the Allocator pipeline for a given input payload.

    Parameters
    ----------
    payload : dict[str, Any]
        Raw input JSON matching the ``AllocatorInput`` schema.
    store : Any | None, optional
        A store implementing the ``AllocatorStore`` protocol.  Falls
        back to a production ``AllocatorRedisStore`` when ``None``.

    Returns
    -------
    AllocatorOutput
        The completed allocation result.

    Raises
    ------
    RuntimeError
        If any errors were recorded during graph execution.
    """
    effective_store = store or AllocatorRedisStore(get_settings())
    graph = build_allocator_graph(effective_store)

    final_state = graph.invoke({"raw_input": payload, "errors": []})
    errors = final_state.get("errors", [])
    if errors:
        raise RuntimeError("; ".join(errors))

    return final_state["final_output"]


# ──────────────────────────────────────────────
# CLI helpers
# ──────────────────────────────────────────────


def _load_payload_from_cli(
    argv: list[str] | None = None,
    stdin: TextIO | None = None,
) -> tuple[dict[str, Any], bool]:
    """Read the Allocator input from CLI arguments, stdin, or defaults.

    Returns
    -------
    tuple[dict[str, Any], bool]
        ``(payload, using_sample)`` where *using_sample* is ``True``
        when the sample scenario was used (so the caller can set up a
        ``DemoAllocatorStore``).
    """
    args = sys.argv[1:] if argv is None else argv
    input_stream = sys.stdin if stdin is None else stdin

    # Sample mode
    if "--sample" in args:
        print("Loading sample scenario...")
        return dict(SAMPLE_SCENARIO), True

    # File mode
    if args:
        print("Reading input from file...")
        return json.loads(Path(args[0]).read_text(encoding="utf-8")), False

    # Stdin mode
    stdin_payload = _read_stdin_if_available(input_stream)
    if stdin_payload is not None:
        print("Reading input from stdin...")
        return json.loads(stdin_payload), False

    # Default to sample if no input is provided
    print("Loading sample scenario...")
    return dict(SAMPLE_SCENARIO), True


def _read_stdin_if_available(stdin: TextIO) -> str | None:
    """Return stdin content if piped, ``None`` if interactive or empty."""
    try:
        if stdin.isatty():
            return None
    except (AttributeError, OSError):
        return None

    content = stdin.read()
    return content if content.strip() else None


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────


def main() -> None:
    """CLI entry point for the Allocator Agent."""
    payload, using_sample = _load_payload_from_cli()

    # In sample mode, provide an in-memory store with the demo
    # Strategist output.  In file/stdin mode, external Redis is used.
    store = DemoAllocatorStore(SAMPLE_STRATEGIST_OUTPUT) if using_sample else None

    output = run_allocator(payload, store=store)
    print("Allocator execution completed.")
    print(output.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
