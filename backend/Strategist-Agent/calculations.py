"""Deterministic SPR release calculations.

No Redis, LangGraph, or LLM logic belongs in this module.
"""

from __future__ import annotations

from app.strategist.schemas import CoverageStatus, ReserveState, SPRReleaseMetrics, StrategistInput


def round_barrels(value: float) -> float:
    return round(value, 2)


def calculate_usable_reserve(reserve_state: ReserveState) -> float:
    return round_barrels(
        max(
            reserve_state.current_spr_reserve_barrels
            - reserve_state.minimum_safety_reserve_barrels,
            0,
        )
    )


def determine_release_duration_days(input_data: StrategistInput) -> int:
    if input_data.import_delay_days == 0:
        return input_data.estimated_disruption_days

    return min(input_data.estimated_disruption_days, input_data.import_delay_days)


def generate_release_metrics(
    input_data: StrategistInput,
    reserve_state: ReserveState,
    usable_reserve_barrels: float,
) -> SPRReleaseMetrics:
    release_duration_days = determine_release_duration_days(input_data)

    required_release_barrels = input_data.net_daily_shortfall_bpd * release_duration_days
    total_release_barrels = min(required_release_barrels, usable_reserve_barrels)

    recommended_spr_release_bpd = (
        total_release_barrels / release_duration_days if release_duration_days > 0 else 0
    )
    remaining_spr_barrels = reserve_state.current_spr_reserve_barrels - total_release_barrels
    reserve_utilization_percent = (
        (total_release_barrels / reserve_state.current_spr_reserve_barrels) * 100
        if reserve_state.current_spr_reserve_barrels > 0
        else 0
    )
    uncovered_shortfall_bpd = max(
        input_data.net_daily_shortfall_bpd - recommended_spr_release_bpd,
        0,
    )

    return SPRReleaseMetrics(
        recommended_spr_release_bpd=round_barrels(recommended_spr_release_bpd),
        release_duration_days=release_duration_days,
        total_release_barrels=round_barrels(total_release_barrels),
        remaining_spr_barrels=round_barrels(remaining_spr_barrels),
        reserve_utilization_percent=round(reserve_utilization_percent, 2),
        uncovered_shortfall_bpd=round_barrels(uncovered_shortfall_bpd),
    )


def evaluate_coverage_status(
    input_data: StrategistInput,
    release_metrics: SPRReleaseMetrics,
) -> CoverageStatus:
    if input_data.net_daily_shortfall_bpd == 0:
        return CoverageStatus.FULL_COVERAGE

    if release_metrics.recommended_spr_release_bpd <= 0:
        return CoverageStatus.NO_COVERAGE

    if release_metrics.uncovered_shortfall_bpd <= 0:
        return CoverageStatus.FULL_COVERAGE

    return CoverageStatus.PARTIAL_COVERAGE


def build_strategy_reasoning(
    input_data: StrategistInput,
    reserve_state: ReserveState,
    usable_reserve_barrels: float,
    release_metrics: SPRReleaseMetrics,
    coverage_status: CoverageStatus,
) -> str:
    if input_data.net_daily_shortfall_bpd == 0:
        return (
            "No SPR release is recommended because the Accountant Agent reported no net daily "
            "shortfall. The reserve remains intact while monitoring continues."
        )

    return (
        f"Risk level is {input_data.risk_level.value}. The usable SPR reserve is "
        f"{usable_reserve_barrels:,.2f} barrels after preserving the minimum safety reserve of "
        f"{reserve_state.minimum_safety_reserve_barrels:,.2f} barrels. The release duration is "
        f"{release_metrics.release_duration_days} days based on the disruption and import delay "
        f"window. The recommended release is {release_metrics.recommended_spr_release_bpd:,.2f} "
        f"bpd, leaving {release_metrics.uncovered_shortfall_bpd:,.2f} bpd uncovered. Coverage "
        f"status is {coverage_status.value}."
    )
