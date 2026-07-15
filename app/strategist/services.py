"""Business services for the Strategist Agent."""

from __future__ import annotations

from typing import Any, Protocol

from app.strategist.calculations import build_strategy_reasoning
from app.strategist.schemas import (
    CoverageStatus,
    ReserveState,
    SPRReleaseMetrics,
    StrategistInput,
    StrategistOutput,
)


class StrategistStore(Protocol):
    def load_current_reserve_state(self, scenario_id: str) -> dict[str, Any] | None:
        ...

    def save_state(self, scenario_id: str, state: dict[str, Any]) -> str:
        ...

    def save_output(self, output: StrategistOutput) -> str:
        ...

    def publish_completed(self, scenario_id: str, output_key: str) -> dict[str, Any]:
        ...


def load_reserve_state(input_data: StrategistInput, store: StrategistStore | None) -> ReserveState:
    reserve_payload = store.load_current_reserve_state(input_data.scenario_id) if store else None

    if not reserve_payload:
        return ReserveState(
            current_spr_reserve_barrels=input_data.current_spr_reserve_barrels,
            minimum_safety_reserve_barrels=input_data.minimum_safety_reserve_barrels,
        )

    return ReserveState(
        current_spr_reserve_barrels=reserve_payload.get(
            "current_spr_reserve_barrels",
            input_data.current_spr_reserve_barrels,
        ),
        minimum_safety_reserve_barrels=reserve_payload.get(
            "minimum_safety_reserve_barrels",
            input_data.minimum_safety_reserve_barrels,
        ),
    )


def build_final_output(
    input_data: StrategistInput,
    reserve_state: ReserveState,
    usable_reserve_barrels: float,
    release_metrics: SPRReleaseMetrics,
    coverage_status: CoverageStatus,
) -> StrategistOutput:
    reasoning = build_strategy_reasoning(
        input_data=input_data,
        reserve_state=reserve_state,
        usable_reserve_barrels=usable_reserve_barrels,
        release_metrics=release_metrics,
        coverage_status=coverage_status,
    )

    return StrategistOutput(
        scenario_id=input_data.scenario_id,
        recommended_spr_release_bpd=release_metrics.recommended_spr_release_bpd,
        release_duration_days=release_metrics.release_duration_days,
        total_release_barrels=release_metrics.total_release_barrels,
        remaining_spr_barrels=release_metrics.remaining_spr_barrels,
        reserve_utilization_percent=release_metrics.reserve_utilization_percent,
        uncovered_shortfall_bpd=release_metrics.uncovered_shortfall_bpd,
        coverage_status=coverage_status,
        strategy_reasoning=reasoning,
    )
