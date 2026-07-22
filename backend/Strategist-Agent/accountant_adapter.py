"""Adapter from Accountant output to Strategist input.

This module keeps Accountant-to-Strategist mapping inside the Strategist
Agent folder, so the platform ``main.py`` can remain a simple pipeline caller.
"""

from __future__ import annotations

import importlib.util
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


DAILY_NATIONAL_DEMAND_BPD = 5_200_000
CURRENT_SPR_RESERVE_BARRELS = 5_000_000
MINIMUM_SAFETY_RESERVE_BARRELS = 1_500_000

LOCAL_MODULE_NAMES = (
    "runner",
    "config",
    "graph",
    "redis_store",
    "schemas",
    "services",
    "state",
    "calculations",
    "redis_client",
)


@contextmanager
def _load_local_runner() -> Iterator[Any]:
    """Load this Strategist Agent's runner without cross-agent import collisions."""

    agent_dir = Path(__file__).resolve().parent
    runner_path = agent_dir / "runner.py"
    original_sys_path = list(sys.path)
    previous_modules = {
        module_name: sys.modules.get(module_name)
        for module_name in LOCAL_MODULE_NAMES
    }

    try:
        sys.path = [str(agent_dir), *[path for path in sys.path if path != str(agent_dir)]]
        for module_name in LOCAL_MODULE_NAMES:
            sys.modules.pop(module_name, None)

        spec = importlib.util.spec_from_file_location(
            "strategist_agent_runner",
            runner_path,
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load Strategist runner from {runner_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        yield module
    finally:
        for module_name in LOCAL_MODULE_NAMES:
            sys.modules.pop(module_name, None)
            previous_module = previous_modules[module_name]
            if previous_module is not None:
                sys.modules[module_name] = previous_module
        sys.path = original_sys_path


def build_strategist_payload(
    accountant_report: dict[str, Any],
    index: int = 0,
) -> dict[str, Any]:
    business = accountant_report["business_summary"]
    risk = accountant_report["risk_analysis"]
    strategist_input = accountant_report["strategist_input"]

    supply_loss_percent = business["supply_loss_percent"]
    net_daily_shortfall_bpd = DAILY_NATIONAL_DEMAND_BPD * supply_loss_percent / 100
    estimated_disruption_days = max(1, int(round(business["expected_recovery_days"])))
    import_delay_days = max(
        0,
        int(round(strategist_input["suppliers"]["average_lead_time"])),
    )

    return {
        "scenario_id": f"scenario-{index + 1}",
        "risk_level": risk["overall_risk_level"],
        "net_daily_shortfall_bpd": net_daily_shortfall_bpd,
        "estimated_disruption_days": estimated_disruption_days,
        "current_spr_reserve_barrels": CURRENT_SPR_RESERVE_BARRELS,
        "minimum_safety_reserve_barrels": MINIMUM_SAFETY_RESERVE_BARRELS,
        "daily_national_demand_bpd": DAILY_NATIONAL_DEMAND_BPD,
        "import_delay_days": import_delay_days,
    }


def run_from_accountant_output(
    scout_output: Any,
    accountant_output: dict[str, Any] | list[dict[str, Any]],
) -> Any:
    with _load_local_runner() as runner:
        store = runner.DemoStrategistStore()

        if isinstance(accountant_output, list):
            return [
                runner.run_strategist(
                    build_strategist_payload(report, index),
                    store=store,
                )
                for index, report in enumerate(accountant_output)
            ]

        return runner.run_strategist(
            build_strategist_payload(accountant_output),
            store=store,
        )
