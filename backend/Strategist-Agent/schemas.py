"""Pydantic schemas for the Strategist Agent."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CoverageStatus(str, Enum):
    FULL_COVERAGE = "FULL_COVERAGE"
    PARTIAL_COVERAGE = "PARTIAL_COVERAGE"
    NO_COVERAGE = "NO_COVERAGE"


class StrategistInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    scenario_id: str = Field(min_length=1)
    risk_level: RiskLevel
    net_daily_shortfall_bpd: float = Field(ge=0)
    estimated_disruption_days: int = Field(ge=1)
    current_spr_reserve_barrels: float = Field(ge=0)
    minimum_safety_reserve_barrels: float = Field(ge=0)
    daily_national_demand_bpd: float = Field(gt=0)
    import_delay_days: int = Field(ge=0)

    @field_validator("risk_level", mode="before")
    @classmethod
    def normalize_risk_level(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @model_validator(mode="after")
    def validate_reserve_and_shortfall(self) -> "StrategistInput":
        if self.minimum_safety_reserve_barrels > self.current_spr_reserve_barrels:
            raise ValueError("minimum_safety_reserve_barrels cannot exceed current_spr_reserve_barrels")

        if self.net_daily_shortfall_bpd > self.daily_national_demand_bpd:
            raise ValueError("net_daily_shortfall_bpd cannot exceed daily_national_demand_bpd")

        return self


class ReserveState(BaseModel):
    current_spr_reserve_barrels: float = Field(ge=0)
    minimum_safety_reserve_barrels: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_safety_reserve(self) -> "ReserveState":
        if self.minimum_safety_reserve_barrels > self.current_spr_reserve_barrels:
            raise ValueError("minimum_safety_reserve_barrels cannot exceed current_spr_reserve_barrels")
        return self


class SPRReleaseMetrics(BaseModel):
    recommended_spr_release_bpd: float = Field(ge=0)
    release_duration_days: int = Field(ge=1)
    total_release_barrels: float = Field(ge=0)
    remaining_spr_barrels: float = Field(ge=0)
    reserve_utilization_percent: float = Field(ge=0, le=100)
    uncovered_shortfall_bpd: float = Field(ge=0)


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
