"""Pydantic schemas for the Allocator Agent V2.

All data models live here. No business logic, no Redis I/O, no LangGraph.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ──────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────


class PriorityLevel(int, Enum):
    """National priority levels for fuel allocation.

    Level 1 sectors are satisfied before Level 2, Level 2 before Level 3.
    Within a level, any shortfall is distributed proportionally among
    that level's sectors.
    """

    LEVEL_1 = 1  # Defense, Healthcare, Emergency Services, Power Generation
    LEVEL_2 = 2  # Agriculture, Food Supply, Public Transport
    LEVEL_3 = 3  # Commercial, Industrial Non-Essential, Private Consumption


class SatisfactionStatus(str, Enum):
    """Whether a sector's demand was fully, partially, or not at all satisfied."""

    FULL = "FULL"
    PARTIAL = "PARTIAL"
    NONE = "NONE"


class AllocationStatus(str, Enum):
    """Overall national allocation status.

    Informs downstream agents and dashboards at a glance.
    """

    FULL_ALLOCATION = "FULL_ALLOCATION"
    RATIONED_ALLOCATION = "RATIONED_ALLOCATION"
    CRITICAL_ONLY_ALLOCATION = "CRITICAL_ONLY_ALLOCATION"
    NO_ALLOCATION = "NO_ALLOCATION"


# ──────────────────────────────────────────────
# Sector-to-Priority Registry
# ──────────────────────────────────────────────

# Deterministic policy table encoding the government's priority framework.
# This is the single source of truth for which sector belongs to which
# priority level. Maps sector_id -> PriorityLevel.
#
# Only sectors listed here are recognised by the allocation engine.
# Unrecognised sector IDs default to LEVEL_3.
SECTOR_PRIORITY_MAP: dict[str, PriorityLevel] = {
    "DEFENSE": PriorityLevel.LEVEL_1,
    "HEALTHCARE": PriorityLevel.LEVEL_1,
    "EMERGENCY_SERVICES": PriorityLevel.LEVEL_1,
    "POWER_GENERATION": PriorityLevel.LEVEL_1,
    "AGRICULTURE": PriorityLevel.LEVEL_2,
    "FOOD_SUPPLY": PriorityLevel.LEVEL_2,
    "PUBLIC_TRANSPORT": PriorityLevel.LEVEL_2,
    "COMMERCIAL": PriorityLevel.LEVEL_3,
    "INDUSTRIAL_NON_ESSENTIAL": PriorityLevel.LEVEL_3,
    "PRIVATE_CONSUMPTION": PriorityLevel.LEVEL_3,
}

# Human-readable names for each recognised sector.
# Used to populate SectorAllocation.sector_name during output construction.
SECTOR_NAME_MAP: dict[str, str] = {
    "DEFENSE": "Defense Services",
    "HEALTHCARE": "Healthcare",
    "EMERGENCY_SERVICES": "Emergency Services",
    "POWER_GENERATION": "Power Generation",
    "AGRICULTURE": "Agriculture",
    "FOOD_SUPPLY": "Food Supply Chain",
    "PUBLIC_TRANSPORT": "Public Transport",
    "COMMERCIAL": "Commercial",
    "INDUSTRIAL_NON_ESSENTIAL": "Industrial Non-Essential",
    "PRIVATE_CONSUMPTION": "Private Consumption",
}


# ──────────────────────────────────────────────
# Input Models
# ──────────────────────────────────────────────


class StateSectorDemand(BaseModel):
    """A single state's daily fuel demand for a single sector.

    This is the atomic demand record. National sector totals are derived
    by aggregating these records across all states.  There is no separate
    national-sector dataset — doing so would create a synchronisation risk
    between two sources of truth.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    state_code: str = Field(
        min_length=1,
        description="ISO-like state code, e.g. MH",
    )
    state_name: str = Field(
        min_length=1,
        description="Full state name, e.g. Maharashtra",
    )
    sector_id: str = Field(
        min_length=1,
        description="Sector identifier, e.g. HEALTHCARE",
    )
    daily_demand_bpd: float = Field(
        gt=0,
        description="Daily fuel demand for this state-sector pair in barrels per day",
    )

    @field_validator("state_code", mode="before")
    @classmethod
    def normalize_state_code(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @field_validator("sector_id", mode="before")
    @classmethod
    def normalize_sector_id(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().upper()
        return value


class AllocatorInput(BaseModel):
    """Input to the Allocator Agent.

    The approved release volume (``recommended_spr_release_bpd``) is never
    passed here — it is always read from the Strategist output in Redis.
    National sector demands are never passed here — they are derived by
    aggregating ``state_sector_demands``.

    Only the scenario identifier and the state-sector demand records are
    required.  Everything else is loaded or derived inside the pipeline.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    scenario_id: str = Field(min_length=1)
    state_sector_demands: list[StateSectorDemand] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_state_sector_pairs(self) -> AllocatorInput:
        seen: set[tuple[str, str]] = set()
        for record in self.state_sector_demands:
            pair = (record.state_code, record.sector_id)
            if pair in seen:
                raise ValueError(
                    f"Duplicate (state_code, sector_id) pair: {pair}"
                )
            seen.add(pair)
        return self


# ──────────────────────────────────────────────
# Output Models
# ──────────────────────────────────────────────


class SectorAllocation(BaseModel):
    """Allocation result for a single sector at the national level."""

    sector_id: str = Field(min_length=1)
    sector_name: str = Field(min_length=1)
    priority_level: PriorityLevel
    daily_demand_bpd: float = Field(ge=0)
    allocated_bpd: float = Field(ge=0)
    unmet_demand_bpd: float = Field(ge=0)
    rationing_percent: float = Field(ge=0, le=100)
    satisfaction_status: SatisfactionStatus


class LevelAllocationSummary(BaseModel):
    """Aggregated allocation summary for a single priority level.

    Provides a dashboard-level view of how a priority level fared.
    """

    priority_level: PriorityLevel
    total_demand_bpd: float = Field(ge=0)
    total_allocated_bpd: float = Field(ge=0)
    total_unmet_bpd: float = Field(ge=0)
    is_fully_satisfied: bool
    sectors: list[SectorAllocation]


class StateAllocation(BaseModel):
    """Allocation result for a single state, broken down by sector.

    Kept in the output for dashboard-level geographic reporting.
    """

    state_code: str = Field(min_length=1)
    state_name: str = Field(min_length=1)
    sector_allocations: list[SectorAllocation]
    total_allocated_bpd: float = Field(ge=0)
    total_demand_bpd: float = Field(ge=0)
    total_unmet_bpd: float = Field(ge=0)
    rationing_percent: float = Field(ge=0, le=100)


class DeliveryPrioritySchedule(BaseModel):
    """A ranked delivery priority entry for logistics planning.

    Used by downstream agents (Navigator, Dealmaker) to sequence fuel
    deliveries.
    """

    priority_rank: int = Field(ge=1)
    priority_level: PriorityLevel
    sector_id: str = Field(min_length=1)
    sector_name: str = Field(min_length=1)
    allocated_bpd: float = Field(ge=0)
    delivery_urgency: str = Field(min_length=1)
    rationale: str = Field(min_length=1)


class LogisticsContext(BaseModel):
    """Placeholder for future Navigator agent logistics constraints.

    Currently emits a no-op note.  When the Navigator agent is implemented,
    this will carry pipeline / rail / tanker capacity constraints that the
    Allocator will use to validate or adjust state distribution.

    This model is already wired into ``AllocatorOutput`` so that adding
    real constraints later requires no schema changes — only populating
    the fields.
    """

    logistics_note: str = Field(
        default=(
            "Logistics constraints are not yet enforced. "
            "The Navigator agent integration is required for "
            "pipeline, rail, and tanker capacity validation."
        ),
        min_length=1,
    )


class AllocatorOutput(BaseModel):
    """Complete output of the Allocator Agent.

    Contains the hierarchical allocation result: priority level summaries,
    per-sector allocations, per-state allocations, a delivery priority
    schedule, a placeholder for future logistics constraints, and a
    deterministic reasoning string.
    """

    scenario_id: str = Field(min_length=1)

    # ── Strategic summary ──────────────────────────────────────
    total_available_bpd: float = Field(
        ge=0,
        description="From Strategist's recommended_spr_release_bpd",
    )
    total_national_demand_bpd: float = Field(ge=0)
    total_allocated_bpd: float = Field(ge=0)
    total_unmet_bpd: float = Field(ge=0)
    national_rationing_percent: float = Field(ge=0, le=100)
    allocation_status: AllocationStatus

    # ── Hierarchical outputs ───────────────────────────────────
    level_summaries: list[LevelAllocationSummary]
    sector_allocations: list[SectorAllocation]
    state_allocations: list[StateAllocation]
    delivery_priority_schedule: list[DeliveryPrioritySchedule]

    # ── Future integration point ───────────────────────────────
    logistics_context: LogisticsContext = Field(
        default_factory=LogisticsContext,
        description="Placeholder for future Navigator logistics constraints",
    )

    # ── Deterministic reasoning ────────────────────────────────
    allocation_reasoning: str = Field(min_length=1)
