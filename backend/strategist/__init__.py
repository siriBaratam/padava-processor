"""Bridge module for calling the Strategist-Agent folder from main.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


def _load_accountant_adapter():
    agent_dir = Path(__file__).resolve().parents[1] / "Strategist-Agent"
    if str(agent_dir) not in sys.path:
        sys.path.insert(0, str(agent_dir))

    spec = importlib.util.spec_from_file_location(
        "strategist_agent_accountant_adapter",
        agent_dir / "accountant_adapter.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_strategist(scout_output: Any, accountant_output: Any) -> Any:
    adapter = _load_accountant_adapter()
    return adapter.run_from_accountant_output(scout_output, accountant_output)
