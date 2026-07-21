"""Deterministic allocation calculations for the Allocator Agent V2.

Implements the Hierarchical Priority Distribution algorithm:

    1. Extract available supply from the Strategist output.
    2. Single-pass group of StateSectorDemand records by PriorityLevel.
    3. Strict L1 → L2 → L3 waterfall allocation.
    4. Build sector / level / state output structures.
    5. Generate a deterministic reasoning string.

Rounding is reconciled at every distribution boundary — no barrels are
lost or created due to floating-point drift.

``generate_distribution_plan`` is the only public business API.
All helpers are ``_``-prefixed implementation details.
``round_bpd`` is a public pure utility (not business logic).

No Redis, LangGraph, or LLM logic belongs in this module.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from schemas import (
    AllocationStatus,
    AllocatorOutput,
    DeliveryPrioritySchedule,
    LevelAllocationSummary,
    PriorityLevel,
    SatisfactionStatus,
    SectorAllocation,
    SECTOR_NAME_MAP,
    SECTOR_PRIORITY_MAP,
    StateAllocation,
    StateSectorDemand,
)
from strategist_contract import StrategistOutput


# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

BPD_QUANT: Decimal = Decimal("0.01")
"""Smallest meaningful barrel-per-day unit.  All allocation amounts are
rounded to this precision."""

BPD_STEP: float = 0.01
"""Float equivalent of *BPD_QUANT*, used for iterative reconciliation."""

_URGENCY_MAP: dict[PriorityLevel, str] = {
    PriorityLevel.LEVEL_1: "IMMEDIATE",
    PriorityLevel.LEVEL_2: "NEXT_72H",
    PriorityLevel.LEVEL_3: "SCHEDULED",
}
"""Delivery urgency label for each priority level."""


# ──────────────────────────────────────────────
# Public Utility
# ──────────────────────────────────────────────


def round_bpd(value: float) -> float:
    """Deterministic rounding to **BPD_QUANT** (0.01) precision.

    Parameters
    ----------
    value : float
        Any numeric value representing a barrel-per-day quantity.

    Returns
    -------
    float
        The value rounded to two decimal places using ``ROUND_HALF_UP``.
    """
    return float(Decimal(str(value)).quantize(BPD_QUANT, rounding=ROUND_HALF_UP))


# ──────────────────────────────────────────────
# Public Business API (single entry point)
# ──────────────────────────────────────────────


def generate_distribution_plan(
    strategist_output: StrategistOutput,
    state_sector_demands: list[StateSectorDemand],
) -> AllocatorOutput:
    """Generate a complete national distribution plan.

    This is the **sole public API** of ``calculations.py``.  It
    orchestrates every private helper below and returns a fully
    populated ``AllocatorOutput``.

    Parameters
    ----------
    strategist_output : StrategistOutput
        The approved Strategist decision loaded from Redis.  Only
        ``recommended_spr_release_bpd`` and ``scenario_id`` are used.
    state_sector_demands : list[StateSectorDemand]
        The atomic demand records from every state and sector.

    Returns
    -------
    AllocatorOutput
        Complete hierarchical allocation result.
    """
    # Step 1 — available daily supply
    available_bpd = _calculate_available_supply(strategist_output)

    # Step 2 — single-pass grouping + national aggregation
    grouped, national_demands = _group_demands_by_priority(
        state_sector_demands,
        SECTOR_PRIORITY_MAP,
    )

    # Step 3 — strict L1 → L2 → L3 waterfall
    sector_amounts, _remaining_fuel = _allocate_by_priority_levels(
        grouped,
        available_bpd,
    )

    # Step 4 — build enriched sector objects
    sector_allocations = _build_sector_allocations(
        sector_amounts,
        national_demands,
        SECTOR_PRIORITY_MAP,
        SECTOR_NAME_MAP,
    )

    # Step 5 — per-level aggregate summaries
    level_summaries = _build_level_summaries(sector_allocations)

    # Step 6 — per-state distribution (with per-sector rounding)
    state_allocations = _compute_state_distribution(
        sector_allocations,
        state_sector_demands,
        national_demands,
    )

    # Step 7 — ranked delivery schedule
    delivery_schedule = _build_delivery_priority_schedule(sector_allocations)

    # Step 8 — national summary statistics
    total_national_demand = round_bpd(sum(national_demands.values()))
    total_allocated = round_bpd(sum(s.allocated_bpd for s in sector_allocations))
    total_unmet = round_bpd(max(total_national_demand - total_allocated, 0))
    national_ratio: float = (
        (total_unmet / total_national_demand) * 100
        if total_national_demand > 0
        else 0.0
    )
    status = _evaluate_allocation_status(available_bpd, total_unmet, level_summaries)

    output = AllocatorOutput(
        scenario_id=strategist_output.scenario_id,
        total_available_bpd=round_bpd(available_bpd),
        total_national_demand_bpd=total_national_demand,
        total_allocated_bpd=total_allocated,
        total_unmet_bpd=total_unmet,
        national_rationing_percent=round(national_ratio, 2),
        allocation_status=status,
        level_summaries=level_summaries,
        sector_allocations=sector_allocations,
        state_allocations=state_allocations,
        delivery_priority_schedule=delivery_schedule,
        allocation_reasoning="Pending allocation reasoning.",  # filled in Step 9
    )

    # Step 9 — purely descriptive reasoning (no calculations)
    output.allocation_reasoning = _build_allocation_reasoning(output)

    return output


# ──────────────────────────────────────────────
# Private Helpers (business-logic internals)
# ──────────────────────────────────────────────


def _calculate_available_supply(strategist_output: StrategistOutput) -> float:
    """Return the approved daily release from the Strategist output.

    The Strategist is the single source of truth for the release volume.
    This value is never duplicated in the Allocator input.

    Parameters
    ----------
    strategist_output : StrategistOutput
        The Strategist decision loaded from Redis.

    Returns
    -------
    float
        ``recommended_spr_release_bpd``, rounded.
    """
    return round_bpd(strategist_output.recommended_spr_release_bpd)


def _group_demands_by_priority(
    state_sector_demands: list[StateSectorDemand],
    sector_priority_map: dict[str, PriorityLevel],
) -> tuple[dict[PriorityLevel, dict[str, float]], dict[str, float]]:
    """Single-pass grouping and aggregation of demand records.

    For each ``StateSectorDemand`` record:

    * its sector's ``PriorityLevel`` is looked up
    * the demand is accumulated into ``grouped[level][sector_id]``
    * the demand is also accumulated into ``national[sector_id]``

    This avoids an intermediate separate aggregation step.

    Parameters
    ----------
    state_sector_demands : list[StateSectorDemand]
        Atomic demand records.
    sector_priority_map : dict[str, PriorityLevel]
        Sector-to-priority lookup table (``SECTOR_PRIORITY_MAP``).

    Returns
    -------
    tuple[dict[PriorityLevel, dict[str, float]], dict[str, float]]
        ``(grouped, national_demands)`` where *grouped* organises
        sector demands by priority level and *national_demands* is the
        flat total per sector.
    """
    national: dict[str, float] = {}
    grouped: dict[PriorityLevel, dict[str, float]] = {}

    for record in state_sector_demands:
        level = sector_priority_map.get(record.sector_id, PriorityLevel.LEVEL_3)

        # Accumulate into the level group
        level_bucket = grouped.setdefault(level, {})
        level_bucket[record.sector_id] = round_bpd(
            level_bucket.get(record.sector_id, 0.0) + record.daily_demand_bpd,
        )

        # Accumulate into national totals
        national[record.sector_id] = round_bpd(
            national.get(record.sector_id, 0.0) + record.daily_demand_bpd,
        )

    return grouped, national


def _allocate_proportionally(
    demands: dict[str, float],
    available_bpd: float,
) -> dict[str, float]:
    """Distribute *available_bpd* among sectors by their demand share.

    Parameters
    ----------
    demands : dict[str, float]
        Sector-id → demand within a single priority level.
    available_bpd : float
        Fuel available for this proportion.

    Returns
    -------
    dict[str, float]
        Sector-id → allocated amount, with rounding reconciled so that
        ``sum(result) == round_bpd(available_bpd)``.
    """
    total_demand = sum(demands.values())
    if total_demand <= 0:
        return {sector: 0.0 for sector in demands}

    raw_shares: dict[str, float] = {
        sector: available_bpd * (demand / total_demand)
        for sector, demand in demands.items()
    }
    rounded = {sector: round_bpd(amount) for sector, amount in raw_shares.items()}
    return _reconcile_rounded_sum(raw_shares, rounded, round_bpd(available_bpd))


def _reconcile_rounded_sum(
    raw: dict[str, float],
    rounded: dict[str, float],
    target: float,
) -> dict[str, float]:
    """Adjust rounded values so their sum exactly equals *target*.

    Uses a largest-remainder approach with **cyclic modulo traversal**:
    the rounding error is distributed in 0.01-BPD steps to sectors with
    the largest rounding losses (or gains when reducing).  The loop
    cycles through sectors via ``i % len(sectors)`` until ``delta`` is
    fully reconciled, guaranteeing correctness even when the number of
    required 0.01-steps exceeds the number of sectors.

    Parameters
    ----------
    raw : dict[str, float]
        The un-rounded raw allocation amounts.
    rounded : dict[str, float]
        The per-sector rounded amounts.
    target : float
        The desired total (must have been passed through ``round_bpd``).

    Returns
    -------
    dict[str, float]
        Adjusted allocations whose sum equals *target*.
    """
    current_total = round_bpd(sum(rounded.values()))
    delta = round_bpd(target - current_total)

    if abs(delta) < BPD_STEP:
        return dict(rounded)

    result = dict(rounded)
    step = BPD_STEP if delta > 0 else -BPD_STEP

    # Sort by rounding loss (largest loss first)
    sectors = sorted(
        result.keys(),
        key=lambda s: (raw.get(s, 0.0) - result[s], s),
        reverse=(delta > 0),
    )

    num_sectors = len(sectors)
    if num_sectors == 0:
        return result

    i = 0
    # Safety limit: at most 1 000 × num_sectors iterations.
    max_iterations = num_sectors * 1000

    while abs(delta) >= BPD_STEP and i < max_iterations:
        sector = sectors[i % num_sectors]
        proposed = round_bpd(result[sector] + step)
        if proposed >= 0:
            result[sector] = proposed
            delta = round_bpd(delta - step)
        i += 1

    return result


def _allocate_level(
    level_demands: dict[str, float],
    available_bpd: float,
) -> tuple[dict[str, float], float]:
    """Allocate fuel to a single priority level.

    If supply is sufficient the level is fully satisfied; any remainder
    is returned.  Otherwise the available fuel is split proportionally
    among the level's sectors and zero remainder is returned.

    Parameters
    ----------
    level_demands : dict[str, float]
        Sector-id → demand for this level.
    available_bpd : float
        Fuel currently available.

    Returns
    -------
    tuple[dict[str, float], float]
        ``(sector_allocations, remaining_fuel)``.
    """
    level_total = sum(level_demands.values())

    if available_bpd >= level_total:
        # Fully satisfy every sector in this level.
        return {
            sector: round_bpd(demand)
            for sector, demand in level_demands.items()
        }, round_bpd(available_bpd - level_total)

    # Partial — proportional split.
    return _allocate_proportionally(level_demands, available_bpd), 0.0


def _allocate_by_priority_levels(
    grouped_demands: dict[PriorityLevel, dict[str, float]],
    available_bpd: float,
) -> tuple[dict[str, float], float]:
    """Strict L1 → L2 → L3 waterfall allocation.

    Parameters
    ----------
    grouped_demands : dict[PriorityLevel, dict[str, float]]
        Sector demands already grouped by priority level (from
        ``_group_demands_by_priority``).
    available_bpd : float
        Total daily fuel to allocate.

    Returns
    -------
    tuple[dict[str, float], float]
        ``(all_sector_amounts, remaining_fuel)`` where
        *all_sector_amounts* maps every sector to its allocated amount
        (possibly zero) and *remaining_fuel* is what is left after
        all three levels (non-zero only when supply exceeds total demand).
    """
    remaining = available_bpd
    all_sector_amounts: dict[str, float] = {}

    for level in (PriorityLevel.LEVEL_1, PriorityLevel.LEVEL_2, PriorityLevel.LEVEL_3):
        level_demands = grouped_demands.get(level, {})
        if not level_demands:
            continue

        if remaining <= 0:
            # No fuel left — every sector in this and subsequent levels
            # receives zero.
            for sector_id in level_demands:
                all_sector_amounts[sector_id] = 0.0
            continue

        level_allocations, remaining = _allocate_level(level_demands, remaining)
        all_sector_amounts.update(level_allocations)

    return all_sector_amounts, remaining


def _build_sector_allocations(
    sector_amounts: dict[str, float],
    national_demands: dict[str, float],
    sector_priority_map: dict[str, PriorityLevel],
    sector_name_map: dict[str, str],
) -> list[SectorAllocation]:
    """Convert raw allocation amounts into ``SectorAllocation`` objects.

    Parameters
    ----------
    sector_amounts : dict[str, float]
        Sector-id → allocated amount (from the waterfall).
    national_demands : dict[str, float]
        Sector-id → total national demand.
    sector_priority_map : dict[str, PriorityLevel]
        Sector-to-priority lookup table.
    sector_name_map : dict[str, str]
        Sector-id → human-readable name.

    Returns
    -------
    list[SectorAllocation]
        One entry per sector present in *national_demands*.
    """
    allocations: list[SectorAllocation] = []

    for sector_id, demand in national_demands.items():
        allocated = sector_amounts.get(sector_id, 0.0)
        unmet = max(demand - allocated, 0.0)
        ratio: float = (unmet / demand) * 100 if demand > 0 else 0.0

        if demand <= 0 and allocated <= 0:
            status = SatisfactionStatus.FULL
        elif unmet <= 0:
            status = SatisfactionStatus.FULL
        elif allocated <= 0:
            status = SatisfactionStatus.NONE
        else:
            status = SatisfactionStatus.PARTIAL

        allocations.append(
            SectorAllocation(
                sector_id=sector_id,
                sector_name=sector_name_map.get(sector_id, sector_id),
                priority_level=sector_priority_map.get(
                    sector_id, PriorityLevel.LEVEL_3,
                ),
                daily_demand_bpd=round_bpd(demand),
                allocated_bpd=round_bpd(allocated),
                unmet_demand_bpd=round_bpd(unmet),
                rationing_percent=round(ratio, 2),
                satisfaction_status=status,
            ),
        )

    return allocations


def _build_level_summaries(
    sector_allocations: list[SectorAllocation],
) -> list[LevelAllocationSummary]:
    """Group ``SectorAllocation`` objects by priority level.

    Parameters
    ----------
    sector_allocations : list[SectorAllocation]
        Per-sector results from ``_build_sector_allocations``.

    Returns
    -------
    list[LevelAllocationSummary]
        One summary per populated level, ordered L1 → L2 → L3.
    """
    grouped: dict[PriorityLevel, list[SectorAllocation]] = {}
    for sa in sector_allocations:
        grouped.setdefault(sa.priority_level, []).append(sa)

    summaries: list[LevelAllocationSummary] = []
    for level in (PriorityLevel.LEVEL_1, PriorityLevel.LEVEL_2, PriorityLevel.LEVEL_3):
        sectors = grouped.get(level, [])
        if not sectors:
            continue

        total_demand = round_bpd(sum(s.daily_demand_bpd for s in sectors))
        total_allocated = round_bpd(sum(s.allocated_bpd for s in sectors))
        total_unmet = round_bpd(max(total_demand - total_allocated, 0))
        fully_satisfied = all(
            s.satisfaction_status == SatisfactionStatus.FULL
            for s in sectors
        )

        summaries.append(
            LevelAllocationSummary(
                priority_level=level,
                total_demand_bpd=total_demand,
                total_allocated_bpd=total_allocated,
                total_unmet_bpd=total_unmet,
                is_fully_satisfied=fully_satisfied,
                sectors=list(sectors),
            ),
        )

    return summaries


def _compute_state_distribution(
    sector_allocations: list[SectorAllocation],
    state_sector_demands: list[StateSectorDemand],
    national_sector_demands: dict[str, float],
) -> list[StateAllocation]:
    """Distribute sector allocations to states proportionally.

    For each sector, every state that demands that sector receives a
    share proportional to its demand.  **Rounding is reconciled per
    sector** so that ``sum(state_allocations_for_sector)`` always
    equals the sector's national allocation exactly.

    Parameters
    ----------
    sector_allocations : list[SectorAllocation]
        National-level sector allocation results.
    state_sector_demands : list[StateSectorDemand]
        Original demand records (used for state shares).
    national_sector_demands : dict[str, float]
        Aggregated national demand totals per sector.

    Returns
    -------
    list[StateAllocation]
        One entry per state, each containing a per-sector breakdown.
    """
    # ── Build lookup: sector_id -> {state_code -> demand} ──
    demand_by_sector: dict[str, dict[str, float]] = {}
    state_names: dict[str, str] = {}
    for record in state_sector_demands:
        demand_by_sector.setdefault(record.sector_id, {})
        demand_by_sector[record.sector_id][record.state_code] = record.daily_demand_bpd
        state_names[record.state_code] = record.state_name

    # ── Build: state_code -> {sector_id -> allocated_bpd} ──
    state_sector_alloc: dict[str, dict[str, float]] = {}

    for sa in sector_allocations:
        sector_id = sa.sector_id
        sector_national_alloc = sa.allocated_bpd
        sector_national_demand = national_sector_demands.get(sector_id, 0.0)
        state_demands = demand_by_sector.get(sector_id, {})

        if sector_national_demand <= 0:
            # No demand — every state gets zero for this sector.
            for state_code in state_demands:
                state_sector_alloc.setdefault(state_code, {})[sector_id] = 0.0
            continue

        # Raw proportional shares
        raw_shares: dict[str, float] = {}
        for state_code, state_demand in state_demands.items():
            share = sector_national_alloc * (state_demand / sector_national_demand)
            raw_shares[state_code] = share

        # Round and reconcile per sector
        rounded = {sc: round_bpd(v) for sc, v in raw_shares.items()}
        reconciled = _reconcile_rounded_sum(
            raw_shares,
            rounded,
            round_bpd(sector_national_alloc),
        )

        for state_code, amount in reconciled.items():
            state_sector_alloc.setdefault(state_code, {})[sector_id] = amount

    # ── Build StateAllocation objects ──
    # Build a reversed lookup: sector_id -> sector allocation metadata
    sector_meta: dict[str, SectorAllocation] = {
        sa.sector_id: sa for sa in sector_allocations
    }

    state_allocations: list[StateAllocation] = []
    for state_code in sorted(state_sector_alloc):
        sector_amounts = state_sector_alloc[state_code]
        state_name = state_names.get(state_code, state_code)

        per_sector: list[SectorAllocation] = []
        total_state_demand = 0.0
        total_state_allocated = 0.0

        for sector_id, allocated_amount in sorted(sector_amounts.items()):
            meta = sector_meta.get(sector_id)
            if meta is None:
                continue

            state_demand_for_sector = demand_by_sector.get(sector_id, {}).get(
                state_code, 0.0,
            )
            unmet_state = max(state_demand_for_sector - allocated_amount, 0.0)
            ratio_s: float = (
                (unmet_state / state_demand_for_sector) * 100
                if state_demand_for_sector > 0
                else 0.0
            )

            if state_demand_for_sector <= 0 and allocated_amount <= 0:
                sat_status = SatisfactionStatus.FULL
            elif unmet_state <= 0:
                sat_status = SatisfactionStatus.FULL
            elif allocated_amount <= 0:
                sat_status = SatisfactionStatus.NONE
            else:
                sat_status = SatisfactionStatus.PARTIAL

            per_sector.append(
                SectorAllocation(
                    sector_id=meta.sector_id,
                    sector_name=meta.sector_name,
                    priority_level=meta.priority_level,
                    daily_demand_bpd=round_bpd(state_demand_for_sector),
                    allocated_bpd=round_bpd(allocated_amount),
                    unmet_demand_bpd=round_bpd(unmet_state),
                    rationing_percent=round(ratio_s, 2),
                    satisfaction_status=sat_status,
                ),
            )

            total_state_demand += state_demand_for_sector
            total_state_allocated += allocated_amount

        total_state_unmet = max(total_state_demand - total_state_allocated, 0.0)
        state_ratio: float = (
            (total_state_unmet / total_state_demand) * 100
            if total_state_demand > 0
            else 0.0
        )

        state_allocations.append(
            StateAllocation(
                state_code=state_code,
                state_name=state_name,
                sector_allocations=per_sector,
                total_allocated_bpd=round_bpd(total_state_allocated),
                total_demand_bpd=round_bpd(total_state_demand),
                total_unmet_bpd=round_bpd(total_state_unmet),
                rationing_percent=round(state_ratio, 2),
            ),
        )

    return state_allocations


def _build_delivery_priority_schedule(
    sector_allocations: list[SectorAllocation],
) -> list[DeliveryPrioritySchedule]:
    """Create a ranked delivery schedule for downstream agents.

    Sectors are ordered by priority level (L1 → L2 → L3) and within
    each level by descending allocation amount.

    Parameters
    ----------
    sector_allocations : list[SectorAllocation]
        Per-sector results from ``_build_sector_allocations``.

    Returns
    -------
    list[DeliveryPrioritySchedule]
        Ranked delivery entries.
    """
    schedule: list[DeliveryPrioritySchedule] = []
    rank = 1

    for level in (PriorityLevel.LEVEL_1, PriorityLevel.LEVEL_2, PriorityLevel.LEVEL_3):
        level_sectors = sorted(
            [sa for sa in sector_allocations if sa.priority_level == level],
            key=lambda s: s.allocated_bpd,
            reverse=True,
        )

        for sa in level_sectors:
            schedule.append(
                DeliveryPrioritySchedule(
                    priority_rank=rank,
                    priority_level=level,
                    sector_id=sa.sector_id,
                    sector_name=sa.sector_name,
                    allocated_bpd=sa.allocated_bpd,
                    delivery_urgency=_URGENCY_MAP[level],
                    rationale=(
                        f"Priority Level {level.value} — {sa.sector_name}: "
                        f"{sa.allocated_bpd:,.2f} bpd allocated"
                    ),
                ),
            )
            rank += 1

    return schedule


def _evaluate_allocation_status(
    total_available_bpd: float,
    total_unmet_bpd: float,
    level_summaries: list[LevelAllocationSummary],
) -> AllocationStatus:
    """Determine the overall national allocation status.

    Parameters
    ----------
    total_available_bpd : float
        Daily supply available for allocation.
    total_unmet_bpd : float
        National unmet demand after allocation.
    level_summaries : list[LevelAllocationSummary]
        Per-level aggregate summaries.

    Returns
    -------
    AllocationStatus
        One of ``NO_ALLOCATION``, ``FULL_ALLOCATION``,
        ``CRITICAL_ONLY_ALLOCATION``, or ``RATIONED_ALLOCATION``.
    """
    if total_available_bpd <= 0:
        return AllocationStatus.NO_ALLOCATION

    if total_unmet_bpd <= 0:
        return AllocationStatus.FULL_ALLOCATION

    # CRITICAL_ONLY only applies when at least one lower-priority level
    # actually exists (has demand) AND all existing lower levels received
    # zero allocation.  If no lower level exists the allocation is simply
    # rationed within Level 1.
    l2 = next(
        (ls for ls in level_summaries if ls.priority_level == PriorityLevel.LEVEL_2),
        None,
    )
    l3 = next(
        (ls for ls in level_summaries if ls.priority_level == PriorityLevel.LEVEL_3),
        None,
    )

    l2_exists = l2 is not None
    l3_exists = l3 is not None

    if l2_exists or l3_exists:
        l2_starved = not l2_exists or l2.total_allocated_bpd <= 0
        l3_starved = not l3_exists or l3.total_allocated_bpd <= 0
        if l2_starved and l3_starved:
            return AllocationStatus.CRITICAL_ONLY_ALLOCATION

    return AllocationStatus.RATIONED_ALLOCATION


def _build_allocation_reasoning(output: AllocatorOutput) -> str:
    """Generate a deterministic explanation of the allocation decision.

    This function **must not perform any business calculations**.  It
    reads pre-computed fields from the completed ``AllocatorOutput``
    and formats them into a human-readable string.

    Parameters
    ----------
    output : AllocatorOutput
        The fully built allocation result.

    Returns
    -------
    str
        Deterministic reasoning string.
    """
    if output.allocation_status == AllocationStatus.FULL_ALLOCATION:
        return (
            f"All national demand of {output.total_national_demand_bpd:,.2f} bpd "
            f"is covered by the Strategist's approved release of "
            f"{output.total_available_bpd:,.2f} bpd. No rationing is required."
        )

    if output.allocation_status == AllocationStatus.NO_ALLOCATION:
        return (
            f"No SPR release is available for allocation. All sectors receive zero "
            f"fuel. National demand of {output.total_national_demand_bpd:,.2f} bpd "
            f"is entirely unmet."
        )

    if output.allocation_status == AllocationStatus.CRITICAL_ONLY_ALLOCATION:
        return (
            f"Only Level 1 sectors received fuel. Level 2 and Level 3 sectors "
            f"receive zero allocation. Of {output.total_national_demand_bpd:,.2f} "
            f"bpd total demand, {output.total_allocated_bpd:,.2f} bpd was allocated "
            f"({output.national_rationing_percent:.2f}% unmet)."
        )

    # RATIONED_ALLOCATION — build level-by-level description
    l1 = next(
        (ls for ls in output.level_summaries if ls.priority_level == PriorityLevel.LEVEL_1),
        None,
    )
    l2 = next(
        (ls for ls in output.level_summaries if ls.priority_level == PriorityLevel.LEVEL_2),
        None,
    )
    l3 = next(
        (ls for ls in output.level_summaries if ls.priority_level == PriorityLevel.LEVEL_3),
        None,
    )

    parts: list[str] = ["Allocation was rationed across priority levels."]

    if l1 is not None:
        parts.append(
            f"Level 1: {l1.total_allocated_bpd:,.2f}/{l1.total_demand_bpd:,.2f} bpd.",
        )
    if l2 is not None:
        satisfied = "fully satisfied" if l2.is_fully_satisfied else "rationed"
        parts.append(
            f"Level 2: {l2.total_allocated_bpd:,.2f}/{l2.total_demand_bpd:,.2f} bpd "
            f"({satisfied}).",
        )
    if l3 is not None:
        satisfied = "fully satisfied" if l3.is_fully_satisfied else "rationed"
        parts.append(
            f"Level 3: {l3.total_allocated_bpd:,.2f}/{l3.total_demand_bpd:,.2f} bpd "
            f"({satisfied}).",
        )

    parts.append(
        f"National unmet: {output.total_unmet_bpd:,.2f} bpd "
        f"({output.national_rationing_percent:.2f}%).",
    )

    return " ".join(parts)
