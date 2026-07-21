"""Adapter for calling Allocator from the main pipeline."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


def _load_allocator_runner():
    agent_dir = Path(__file__).resolve().parent
    if str(agent_dir) in sys.path:
        sys.path.remove(str(agent_dir))
    sys.path.insert(0, str(agent_dir))

    for module_name in (
        "runner",
        "config",
        "graph",
        "redis_store",
        "schemas",
        "services",
        "state",
        "calculations",
        "strategist_contract",
        "redis_client",
    ):
        sys.modules.pop(module_name, None)

    spec = importlib.util.spec_from_file_location(
        "allocator_agent_runner",
        agent_dir / "runner.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_ALLOCATOR_RUNNER = _load_allocator_runner()
DemoAllocatorStore = _ALLOCATOR_RUNNER.DemoAllocatorStore
SAMPLE_SCENARIO = _ALLOCATOR_RUNNER.SAMPLE_SCENARIO
run_allocator_payload = _ALLOCATOR_RUNNER.run_allocator


def run_from_pipeline_outputs(
    scout_output: Any,
    accountant_output: Any,
    strategist_output: Any,
) -> Any:
    if isinstance(strategist_output, list):
        reports = accountant_output if isinstance(accountant_output, list) else [accountant_output]
        return [
            _run_one(report, output)
            for report, output in zip(reports, strategist_output)
        ]

    return _run_one(accountant_output, strategist_output)


def _run_one(accountant_report: Any, strategist_output: Any) -> Any:
    strategist_payload = _to_dict(strategist_output)
    scenario_id = strategist_payload["scenario_id"]
    payload = {
        "scenario_id": scenario_id,
        "state_sector_demands": _state_sector_demands(accountant_report),
    }
    store = DemoAllocatorStore(strategist_payload)
    return run_allocator_payload(payload, store=store)


def _state_sector_demands(accountant_report: Any) -> list[dict[str, Any]]:
    if isinstance(accountant_report, dict):
        if accountant_report.get("state_sector_demands"):
            return accountant_report["state_sector_demands"]

        strategist_input = accountant_report.get("strategist_input", {})
        if strategist_input.get("state_sector_demands"):
            return strategist_input["state_sector_demands"]

    return list(SAMPLE_SCENARIO["state_sector_demands"])


def _to_dict(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")

    if isinstance(value, dict):
        return value

    raise TypeError("strategist_output must be a dict or Pydantic model")
