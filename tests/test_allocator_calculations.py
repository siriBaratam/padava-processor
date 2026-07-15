"""Tests for the Allocator Agent V2 — deterministic calculation layer.

Test matrix
----------
* Full allocation          — supply >= total demand               → FULL_ALLOCATION
* Zero allocation          — supply = 0                          → NO_ALLOCATION
* Critical-only            — L1 satisfied, L2/L3 exist + get 0    → CRITICAL_ONLY
* Rationed (L1 only)       — supply < L1, no L2/L3 sectors       → RATIONED
* Rationed (cross-level)   — L1 full, L2 partial, L3 = 0         → RATIONED
* Supply > total demand    — surplus fuel                         → FULL_ALLOCATION
* Supply = total demand    — exact match                          → FULL_ALLOCATION
* Unknown sector IDs       — default to LEVEL_3                   → LEVEL_3
* Deterministic rounding   — round_bpd precision                  → 0.01 resolution
* Rounding reconciliation  — sum(proportional) == available        → exact
* State reconciliation     — sum(state) == national per sector     → exact
* Reconciliation cycles    — delta > num_sectors × 0.01           → modulo cycling works
* Delivery schedule        — L1 ranked before L2 before L3        → correct order
* Reasoning output         — descriptive, no recalculations       → read-only
"""

import unittest

from app.allocator.calculations import (
    _reconcile_rounded_sum,
    generate_distribution_plan,
    round_bpd,
)
from app.allocator.schemas import (
    AllocationStatus,
    PriorityLevel,
    SatisfactionStatus,
    StateSectorDemand,
)
from app.strategist.schemas import StrategistOutput


# ──────────────────────────────────────────────
# Test helpers
# ──────────────────────────────────────────────


def strategist_output(**overrides: object) -> StrategistOutput:
    """Build a ``StrategistOutput`` with overridable defaults."""
    payload: dict[str, object] = {
        "scenario_id": "scenario-001",
        "recommended_spr_release_bpd": 500_000,
        "release_duration_days": 5,
        "total_release_barrels": 2_500_000,
        "remaining_spr_barrels": 5_000_000,
        "reserve_utilization_percent": 33.33,
        "uncovered_shortfall_bpd": 0,
        "coverage_status": "FULL_COVERAGE",
        "strategy_reasoning": "Test strategist output for Allocator V2.",
    }
    payload.update(overrides)
    return StrategistOutput.model_validate(payload)


def demand(
    state_code: str,
    state_name: str,
    sector_id: str,
    daily_demand_bpd: float,
) -> StateSectorDemand:
    """Shorthand for constructing a ``StateSectorDemand`` record."""
    return StateSectorDemand(
        state_code=state_code,
        state_name=state_name,
        sector_id=sector_id,
        daily_demand_bpd=daily_demand_bpd,
    )


def assert_national_balance(tc: unittest.TestCase, output: object) -> None:
    """Verify that national totals are internally consistent."""
    total_allocated = round_bpd(
        sum(s.allocated_bpd for s in output.sector_allocations),
    )
    total_unmet = round_bpd(
        sum(s.unmet_demand_bpd for s in output.sector_allocations),
    )
    tc.assertEqual(
        round_bpd(total_allocated + total_unmet),
        output.total_national_demand_bpd,
    )
    # National allocated matches sum across states.
    state_total = round_bpd(
        sum(s.total_allocated_bpd for s in output.state_allocations),
    )
    tc.assertEqual(state_total, output.total_allocated_bpd)


def assert_state_sector_integrity(tc: unittest.TestCase, output: object) -> None:
    """For every sector, verify sum(state_alloc) == national_alloc."""
    # Build a map: sector_id -> sum of state allocations
    state_sums: dict[str, float] = {}
    for st in output.state_allocations:
        for sa in st.sector_allocations:
            state_sums[sa.sector_id] = round_bpd(
                state_sums.get(sa.sector_id, 0.0) + sa.allocated_bpd,
            )
    for sa in output.sector_allocations:
        tc.assertEqual(
            state_sums.get(sa.sector_id, 0.0),
            sa.allocated_bpd,
            f"State sum for sector {sa.sector_id} ({sa.sector_name}) "
            f"does not match national allocation "
            f"({state_sums.get(sa.sector_id, 0.0)} vs {sa.allocated_bpd})",
        )


# ──────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────


class RoundingTests(unittest.TestCase):
    """``round_bpd`` utility precision tests."""

    def test_rounds_to_two_decimal_places(self) -> None:
        self.assertEqual(round_bpd(100.005), 100.01)
        self.assertEqual(round_bpd(100.004), 100.0)
        self.assertEqual(round_bpd(0.0), 0.0)
        self.assertEqual(round_bpd(1.999), 2.0)
        self.assertEqual(round_bpd(1.001), 1.0)


class FullAllocationTests(unittest.TestCase):
    """Supply >= total demand."""

    def test_full_allocation_when_supply_exceeds_demand(self) -> None:
        """Supply > national demand → everything satisfied, status FULL."""
        output = generate_distribution_plan(
            strategist_output(recommended_spr_release_bpd=500_000),
            [
                demand("MH", "Maharashtra", "HEALTHCARE", 100_000),
                demand("MH", "Maharashtra", "DEFENSE", 80_000),
                demand("GJ", "Gujarat", "AGRICULTURE", 90_000),
                demand("TN", "Tamil Nadu", "COMMERCIAL", 60_000),
            ],
        )

        self.assertEqual(output.allocation_status, AllocationStatus.FULL_ALLOCATION)
        self.assertEqual(output.total_available_bpd, 500_000)
        self.assertEqual(output.total_national_demand_bpd, 330_000)
        self.assertEqual(output.total_allocated_bpd, 330_000)
        self.assertEqual(output.total_unmet_bpd, 0)
        self.assertEqual(output.national_rationing_percent, 0.0)
        assert_national_balance(self, output)
        assert_state_sector_integrity(self, output)

    def test_full_allocation_when_supply_equals_demand(self) -> None:
        """Supply == demand → exact match, FULL."""
        output = generate_distribution_plan(
            strategist_output(recommended_spr_release_bpd=250_000),
            [
                demand("MH", "Maharashtra", "DEFENSE", 100_000),
                demand("GJ", "Gujarat", "HEALTHCARE", 80_000),
                demand("TN", "Tamil Nadu", "AGRICULTURE", 70_000),
            ],
        )

        self.assertEqual(output.allocation_status, AllocationStatus.FULL_ALLOCATION)
        self.assertEqual(output.total_allocated_bpd, 250_000)
        self.assertEqual(output.total_unmet_bpd, 0)


class ZeroAllocationTests(unittest.TestCase):
    """No fuel available."""

    def test_no_allocation_when_supply_is_zero(self) -> None:
        output = generate_distribution_plan(
            strategist_output(recommended_spr_release_bpd=0),
            [
                demand("MH", "Maharashtra", "HEALTHCARE", 100_000),
                demand("GJ", "Gujarat", "DEFENSE", 80_000),
            ],
        )

        self.assertEqual(output.allocation_status, AllocationStatus.NO_ALLOCATION)
        self.assertEqual(output.total_available_bpd, 0)
        self.assertEqual(output.total_allocated_bpd, 0)
        self.assertEqual(output.total_unmet_bpd, 180_000)
        assert_national_balance(self, output)


class CriticalOnlyAllocationTests(unittest.TestCase):
    """L1 satisfied, L2/L3 exist and get zero."""

    def test_critical_only_when_supply_equals_L1_demand(self) -> None:
        """Supply exactly covers L1; L2 sectors exist but get nothing."""
        output = generate_distribution_plan(
            strategist_output(recommended_spr_release_bpd=200_000),
            [
                # L1 sectors
                demand("MH", "Maharashtra", "HEALTHCARE", 120_000),
                demand("GJ", "Gujarat", "DEFENSE", 80_000),
                # L2 sector
                demand("TN", "Tamil Nadu", "AGRICULTURE", 100_000),
            ],
        )

        self.assertEqual(
            output.allocation_status,
            AllocationStatus.CRITICAL_ONLY_ALLOCATION,
        )
        self.assertEqual(output.total_available_bpd, 200_000)
        self.assertEqual(output.total_national_demand_bpd, 300_000)
        self.assertEqual(output.total_allocated_bpd, 200_000)
        self.assertEqual(output.total_unmet_bpd, 100_000)

        # All L1 sectors fully satisfied
        for sa in output.sector_allocations:
            if sa.priority_level == PriorityLevel.LEVEL_1:
                self.assertEqual(
                    sa.satisfaction_status, SatisfactionStatus.FULL,
                    f"{sa.sector_id} should be FULL",
                )
            else:
                self.assertEqual(
                    sa.satisfaction_status, SatisfactionStatus.NONE,
                    f"{sa.sector_id} should be NONE",
                )


class RationedAllocationTests(unittest.TestCase):
    """Rationing scenarios."""

    def test_rationed_when_only_L1_exists_and_supply_is_insufficient(self) -> None:
        """All demand is L1 with no L2/L3 sectors. Supply < L1 → RATIONED."""
        output = generate_distribution_plan(
            strategist_output(recommended_spr_release_bpd=150_000),
            [
                demand("MH", "Maharashtra", "HEALTHCARE", 200_000),
                demand("GJ", "Gujarat", "DEFENSE", 100_000),
            ],
        )

        self.assertEqual(
            output.allocation_status,
            AllocationStatus.RATIONED_ALLOCATION,
        )
        self.assertEqual(output.total_available_bpd, 150_000)
        self.assertEqual(output.total_allocated_bpd, 150_000)
        self.assertEqual(output.total_unmet_bpd, 150_000)

        # Proportional distribution: HEALTHCARE gets 200/300 * 150k = 100k
        # DEFENSE gets 100/300 * 150k = 50k
        for sa in output.sector_allocations:
            if sa.sector_id == "HEALTHCARE":
                self.assertAlmostEqual(sa.allocated_bpd, 100_000)
                self.assertEqual(sa.satisfaction_status, SatisfactionStatus.PARTIAL)
            elif sa.sector_id == "DEFENSE":
                self.assertAlmostEqual(sa.allocated_bpd, 50_000)
                self.assertEqual(sa.satisfaction_status, SatisfactionStatus.PARTIAL)

    def test_rationed_when_L1_full_and_L2_partial(self) -> None:
        """L1 satisfied, L2 gets proportional, L3 gets zero → RATIONED."""
        output = generate_distribution_plan(
            strategist_output(recommended_spr_release_bpd=300_000),
            [
                # L1
                demand("MH", "Maharashtra", "HEALTHCARE", 100_000),
                demand("GJ", "Gujarat", "DEFENSE", 80_000),
                # L2
                demand("TN", "Tamil Nadu", "AGRICULTURE", 200_000),
                demand("UP", "Uttar Pradesh", "FOOD_SUPPLY", 100_000),
                # L3
                demand("MH", "Maharashtra", "COMMERCIAL", 50_000),
            ],
        )

        self.assertEqual(
            output.allocation_status,
            AllocationStatus.RATIONED_ALLOCATION,
        )
        # L1 = 180k (fully satisfied), remaining = 120k for L2
        # L2 total = 300k, supply = 120k → proportional
        # AGRICULTURE gets 120k * 200/300 = 80k
        # FOOD_SUPPLY gets 120k * 100/300 = 40k
        # L3 gets 0

        l1 = [ls for ls in output.level_summaries if ls.priority_level == PriorityLevel.LEVEL_1][0]
        l2 = [ls for ls in output.level_summaries if ls.priority_level == PriorityLevel.LEVEL_2][0]
        l3_summaries = [ls for ls in output.level_summaries if ls.priority_level == PriorityLevel.LEVEL_3]

        self.assertTrue(l1.is_fully_satisfied)
        self.assertFalse(l2.is_fully_satisfied)
        # L3 sectors exist (COMMERCIAL) and get 0 allocation, so a summary exists.
        self.assertEqual(len(l3_summaries), 1)
        self.assertEqual(l3_summaries[0].total_allocated_bpd, 0)

        assert_national_balance(self, output)
        assert_state_sector_integrity(self, output)

    def test_rationed_with_supply_between_L1_and_L2(self) -> None:
        """Supply > L1 but < L1+L2 → L1 full, L2 partial, L3 0."""
        output = generate_distribution_plan(
            strategist_output(recommended_spr_release_bpd=250_000),
            [
                demand("MH", "Maharashtra", "HEALTHCARE", 100_000),
                demand("GJ", "Gujarat", "POWER_GENERATION", 80_000),
                demand("TN", "Tamil Nadu", "AGRICULTURE", 150_000),
                demand("UP", "Uttar Pradesh", "PUBLIC_TRANSPORT", 100_000),
                demand("MH", "Maharashtra", "COMMERCIAL", 50_000),
            ],
        )

        self.assertEqual(output.allocation_status, AllocationStatus.RATIONED_ALLOCATION)
        # L1 = 180k (fully), remaining = 70k for L2
        # L2 total = 250k, 70k proportional: AG gets 70*150/250=42k, PT gets 70*100/250=28k
        self.assertEqual(output.total_allocated_bpd, 250_000)
        assert_state_sector_integrity(self, output)


class SupplyVsDemandTests(unittest.TestCase):
    """Edge cases around supply/demand boundaries."""

    def test_supply_greater_than_total_demand(self) -> None:
        """Surplus fuel → FULL, remaining noted."""
        output = generate_distribution_plan(
            strategist_output(recommended_spr_release_bpd=1_000_000),
            [
                demand("MH", "Maharashtra", "HEALTHCARE", 200_000),
                demand("GJ", "Gujarat", "DEFENSE", 150_000),
            ],
        )
        self.assertEqual(output.allocation_status, AllocationStatus.FULL_ALLOCATION)
        self.assertEqual(output.total_allocated_bpd, 350_000)
        self.assertEqual(output.total_unmet_bpd, 0)

    def test_unknown_sector_defaults_to_level_3(self) -> None:
        """An unrecognised sector_id → L3 default."""
        output = generate_distribution_plan(
            strategist_output(recommended_spr_release_bpd=100_000),
            [
                demand("XX", "Unknown", "UNKNOWN_SECTOR", 200_000),
            ],
        )
        for sa in output.sector_allocations:
            self.assertEqual(sa.priority_level, PriorityLevel.LEVEL_3)


class RoundingReconciliationTests(unittest.TestCase):
    """No barrels lost or created due to floating-point."""

    def test_sector_level_rounding_is_exact(self) -> None:
        """Proportional split within a level sums exactly to available."""
        output = generate_distribution_plan(
            strategist_output(recommended_spr_release_bpd=100_000),
            [
                demand("MH", "Maharashtra", "HEALTHCARE", 60_000),
                demand("GJ", "Gujarat", "DEFENSE", 30_000),
                demand("TN", "Tamil Nadu", "EMERGENCY_SERVICES", 10_000),
            ],
        )
        total = round_bpd(
            sum(s.allocated_bpd for s in output.sector_allocations),
        )
        self.assertEqual(total, output.total_available_bpd)

    def test_state_distribution_rounding_is_exact_per_sector(self) -> None:
        """For each sector, sum(state_alloc) == national_allocation."""
        output = generate_distribution_plan(
            strategist_output(recommended_spr_release_bpd=300_000),
            [
                demand("MH", "Maharashtra", "HEALTHCARE", 120_000),
                demand("GJ", "Gujarat", "HEALTHCARE", 90_000),
                demand("TN", "Tamil Nadu", "HEALTHCARE", 70_000),
                demand("UP", "Uttar Pradesh", "HEALTHCARE", 50_000),
                demand("MH", "Maharashtra", "DEFENSE", 80_000),
                demand("GJ", "Gujarat", "DEFENSE", 40_000),
            ],
        )
        assert_state_sector_integrity(self, output)


class ReconciliationCyclingTests(unittest.TestCase):
    """``_reconcile_rounded_sum`` cyclically distributes delta.

    The old implementation used a ``for sector in sectors:`` loop that
    visited each sector exactly once.  When the rounding error required
    more 0.01-BPD adjustments than there were sectors, the remaining
    delta was silently lost.

    The fix uses modulo indexing (``i % len(sectors)``) so the loop
    cycles through sectors until *all* of delta is reconciled.
    """

    def test_reconciles_when_delta_exceeds_sector_count(self) -> None:
        """2 sectors, delta = 0.03 (3 steps) → must cycle.

        Sort order when delta > 0 (reverse=True, descending):
        ``raw - rounded``: A=0.015, B=0.015 (tied). Tiebreaker by
        name in descending order → B before A.

        Adjustments: B+0.01, A+0.01, B+0.01 → A=33.33, B=66.67.
        Old code (2 iterations) would leave 0.01 unreconciled.
        """
        raw = {"A": 33.335, "B": 66.665}
        rounded = {"A": 33.32, "B": 66.65}  # sum = 99.97
        target = 100.0
        # delta = 100.0 - 99.97 = 0.03 → 3 steps, only 2 sectors

        result = _reconcile_rounded_sum(raw, rounded, target)
        total = round_bpd(sum(result.values()))
        self.assertEqual(total, target)

        # B gets the tiebreaker (reverse=True, B > A)
        self.assertAlmostEqual(result["A"], 33.33, places=2)
        self.assertAlmostEqual(result["B"], 66.67, places=2)

    def test_exact_reconciliation_without_cycling(self) -> None:
        """delta fits within sector count (no cycling needed)."""
        raw = {"A": 33.335, "B": 33.335, "C": 33.335}
        rounded = {"A": 33.33, "B": 33.33, "C": 33.33}  # sum = 99.99
        target = 100.0
        # delta = 0.01 → 1 step, 3 sectors → no cycling needed

        result = _reconcile_rounded_sum(raw, rounded, target)
        total = round_bpd(sum(result.values()))
        self.assertEqual(total, target)

    def test_negative_delta_with_cycling(self) -> None:
        """Negative delta requiring more steps than sectors."""
        raw = {"A": 33.335, "B": 66.665}
        rounded = {"A": 33.35, "B": 66.68}  # sum = 100.03
        target = 100.0
        # delta = -0.03 → 3 steps of -0.01, only 2 sectors

        result = _reconcile_rounded_sum(raw, rounded, target)
        total = round_bpd(sum(result.values()))
        self.assertEqual(total, target)

        # After 3 adjustments (B-0.01, A-0.01, B-0.01):
        # B has larger rounding gain (66.68 - 66.665 = 0.015 vs 33.35 - 33.335 = 0.015,
        # tiebreaker: sorted by name ascending → A first when delta < 0 and reverse=False)
        # Actually with delta < 0, reverse=False, so sorted by (raw-result, name) ascending.
        # A: 33.335 - 33.35 = -0.015, B: 66.665 - 66.68 = -0.015.
        # Tiebreaker by name: A first, B second.
        # So A gets -0.01 → 33.34, B gets -0.01 → 66.67, then A gets -0.01 → 33.33
        self.assertAlmostEqual(result["A"], 33.33, places=2)
        self.assertAlmostEqual(result["B"], 66.67, places=2)


class DeliveryScheduleTests(unittest.TestCase):
    """Delivery priority ordering."""

    def test_sectors_ordered_by_level_then_allocation(self) -> None:
        """L1 first (descending), then L2, then L3."""
        output = generate_distribution_plan(
            strategist_output(recommended_spr_release_bpd=500_000),
            [
                demand("MH", "Maharashtra", "HEALTHCARE", 100_000),
                demand("GJ", "Gujarat", "AGRICULTURE", 200_000),
                demand("TN", "Tamil Nadu", "COMMERCIAL", 50_000),
                demand("UP", "Uttar Pradesh", "DEFENSE", 80_000),
            ],
        )

        schedule = output.delivery_priority_schedule
        self.assertGreater(len(schedule), 0)

        # All L1 entries come before any L2 entry, and L2 before L3.
        max_l1_rank = max(
            (e.priority_rank for e in schedule if e.priority_level == PriorityLevel.LEVEL_1),
            default=0,
        )
        min_l2_rank = min(
            (e.priority_rank for e in schedule if e.priority_level == PriorityLevel.LEVEL_2),
            default=999,
        )
        min_l3_rank = min(
            (e.priority_rank for e in schedule if e.priority_level == PriorityLevel.LEVEL_3),
            default=999,
        )

        self.assertLess(max_l1_rank, min_l2_rank)
        # If L3 exists, its min rank should be after L2's max
        if any(e.priority_level == PriorityLevel.LEVEL_3 for e in schedule):
            max_l2_rank = max(
                e.priority_rank for e in schedule
                if e.priority_level == PriorityLevel.LEVEL_2
            )
            self.assertLess(max_l2_rank, min_l3_rank)


class ReasoningTests(unittest.TestCase):
    """``allocation_reasoning`` is generated and meaningful."""

    def test_reasoning_for_full_allocation(self) -> None:
        output = generate_distribution_plan(
            strategist_output(recommended_spr_release_bpd=200_000),
            [demand("MH", "Maharashtra", "HEALTHCARE", 100_000)],
        )
        self.assertIn("No rationing is required", output.allocation_reasoning)

    def test_reasoning_for_no_allocation(self) -> None:
        output = generate_distribution_plan(
            strategist_output(recommended_spr_release_bpd=0),
            [demand("MH", "Maharashtra", "HEALTHCARE", 100_000)],
        )
        self.assertIn("No SPR release", output.allocation_reasoning)

    def test_reasoning_for_critical_only(self) -> None:
        output = generate_distribution_plan(
            strategist_output(recommended_spr_release_bpd=100_000),
            [
                demand("MH", "Maharashtra", "HEALTHCARE", 100_000),
                demand("GJ", "Gujarat", "AGRICULTURE", 100_000),
            ],
        )
        self.assertIn("Level 1", output.allocation_reasoning)
        self.assertIn("Level 2", output.allocation_reasoning)

    def test_reasoning_for_rationed(self) -> None:
        output = generate_distribution_plan(
            strategist_output(recommended_spr_release_bpd=100_000),
            [demand("MH", "Maharashtra", "HEALTHCARE", 200_000)],
        )
        self.assertIn("rationed", output.allocation_reasoning.lower())


if __name__ == "__main__":
    unittest.main()
