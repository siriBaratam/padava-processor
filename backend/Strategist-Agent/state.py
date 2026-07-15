"""LangGraph state type for the Strategist Agent."""

from __future__ import annotations

from typing import Any, TypedDict

from app.strategist.schemas import CoverageStatus, ReserveState, SPRReleaseMetrics, StrategistInput, StrategistOutput


class StrategistState(TypedDict, total=False):
    raw_input: dict[str, Any]
    validated_input: StrategistInput
    reserve_state: ReserveState
    usable_reserve_barrels: float
    release_metrics: SPRReleaseMetrics
    coverage_status: CoverageStatus
    strategy_reasoning: str
    final_output: StrategistOutput
    redis_output_key: str
    redis_state_key: str
    event_payload: dict[str, Any]
    errors: list[str]
