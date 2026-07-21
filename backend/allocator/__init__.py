"""Bridge module for calling the Allocator-agent folder from main.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


def _load_pipeline_adapter():
    agent_dir = Path(__file__).resolve().parents[1] / "Allocator-agent"
    if str(agent_dir) not in sys.path:
        sys.path.insert(0, str(agent_dir))

    spec = importlib.util.spec_from_file_location(
        "allocator_agent_pipeline_adapter",
        agent_dir / "pipeline_adapter.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_allocator(
    scout_output: Any,
    accountant_output: Any,
    strategist_output: Any,
) -> Any:
    adapter = _load_pipeline_adapter()
    return adapter.run_from_pipeline_outputs(
        scout_output,
        accountant_output,
        strategist_output,
    )
