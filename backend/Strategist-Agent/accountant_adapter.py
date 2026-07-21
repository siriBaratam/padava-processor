"""Adapter from Accountant output to Strategist input.

This module keeps Accountant-to-Strategist mapping inside the Strategist
Agent folder, so the platform ``main.py`` can remain a simple pipeline caller.
"""

from __future__ import annotations

from typing import Any

from runner import DemoStrategistStore, run_strategist as run_strategist_payload


DAILY_NATIONAL_DEMAND_BPD = 5_200_000
CURRENT_SPR_RESERVE_BARRELS = 5_000_000
MINIMUM_SAFETY_RESERVE_BARRELS = 1_500_000


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
    store = DemoStrategistStore()

    if isinstance(accountant_output, list):
        return [
            run_strategist_payload(
                build_strategist_payload(report, index),
                store=store,
            )
            for index, report in enumerate(accountant_output)
        ]

    return run_strategist_payload(
        build_strategist_payload(accountant_output),
        store=store,
    )
