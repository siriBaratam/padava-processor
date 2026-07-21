"""Minimal Strategist output contract consumed by the Allocator Agent.

This keeps the standalone ``Allocator-agent`` folder runnable without
importing from the sibling ``Strategist-Agent`` directory, whose hyphenated
name is not a valid Python package name.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class CoverageStatus(str, Enum):
    FULL_COVERAGE = "FULL_COVERAGE"
    PARTIAL_COVERAGE = "PARTIAL_COVERAGE"
    NO_COVERAGE = "NO_COVERAGE"


class StrategistOutput(BaseModel):
    scenario_id: str
    recommended_spr_release_bpd: float = Field(ge=0)
    release_duration_days: int = Field(ge=1)
    total_release_barrels: float = Field(ge=0)
    remaining_spr_barrels: float = Field(ge=0)
    reserve_utilization_percent: float = Field(ge=0, le=100)
    uncovered_shortfall_bpd: float = Field(ge=0)
    coverage_status: CoverageStatus
    strategy_reasoning: str = Field(min_length=1)
