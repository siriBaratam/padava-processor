import unittest

from app.strategist.calculations import (
    calculate_usable_reserve,
    determine_release_duration_days,
    evaluate_coverage_status,
    generate_release_metrics,
)
from app.strategist.schemas import CoverageStatus, ReserveState, StrategistInput


def sample_input(**overrides):
    payload = {
        "scenario_id": "scenario-001",
        "risk_level": "HIGH",
        "net_daily_shortfall_bpd": 100_000,
        "estimated_disruption_days": 10,
        "current_spr_reserve_barrels": 2_000_000,
        "minimum_safety_reserve_barrels": 500_000,
        "daily_national_demand_bpd": 5_000_000,
        "import_delay_days": 4,
    }
    payload.update(overrides)
    return StrategistInput.model_validate(payload)


class StrategistCalculationTests(unittest.TestCase):
    def test_import_delay_zero_uses_estimated_disruption_days(self):
        input_data = sample_input(import_delay_days=0, estimated_disruption_days=12)

        self.assertEqual(determine_release_duration_days(input_data), 12)

    def test_generates_full_coverage_when_reserve_can_cover_shortfall(self):
        input_data = sample_input()
        reserve_state = ReserveState(
            current_spr_reserve_barrels=2_000_000,
            minimum_safety_reserve_barrels=500_000,
        )
        usable_reserve = calculate_usable_reserve(reserve_state)
        metrics = generate_release_metrics(input_data, reserve_state, usable_reserve)

        self.assertEqual(metrics.release_duration_days, 4)
        self.assertEqual(metrics.recommended_spr_release_bpd, 100_000)
        self.assertEqual(metrics.total_release_barrels, 400_000)
        self.assertEqual(metrics.uncovered_shortfall_bpd, 0)
        self.assertEqual(evaluate_coverage_status(input_data, metrics), CoverageStatus.FULL_COVERAGE)

    def test_generates_partial_coverage_when_usable_reserve_is_limited(self):
        input_data = sample_input(
            net_daily_shortfall_bpd=100_000,
            estimated_disruption_days=2,
            import_delay_days=2,
            current_spr_reserve_barrels=100_000,
            minimum_safety_reserve_barrels=50_000,
        )
        reserve_state = ReserveState(
            current_spr_reserve_barrels=100_000,
            minimum_safety_reserve_barrels=50_000,
        )
        usable_reserve = calculate_usable_reserve(reserve_state)
        metrics = generate_release_metrics(input_data, reserve_state, usable_reserve)

        self.assertEqual(metrics.recommended_spr_release_bpd, 25_000)
        self.assertEqual(metrics.total_release_barrels, 50_000)
        self.assertEqual(metrics.uncovered_shortfall_bpd, 75_000)
        self.assertEqual(metrics.remaining_spr_barrels, 50_000)
        self.assertEqual(evaluate_coverage_status(input_data, metrics), CoverageStatus.PARTIAL_COVERAGE)

    def test_generates_no_coverage_when_no_usable_reserve_exists(self):
        input_data = sample_input(
            current_spr_reserve_barrels=500_000,
            minimum_safety_reserve_barrels=500_000,
        )
        reserve_state = ReserveState(
            current_spr_reserve_barrels=500_000,
            minimum_safety_reserve_barrels=500_000,
        )
        metrics = generate_release_metrics(input_data, reserve_state, calculate_usable_reserve(reserve_state))

        self.assertEqual(metrics.recommended_spr_release_bpd, 0)
        self.assertEqual(metrics.uncovered_shortfall_bpd, 100_000)
        self.assertEqual(evaluate_coverage_status(input_data, metrics), CoverageStatus.NO_COVERAGE)


if __name__ == "__main__":
    unittest.main()
