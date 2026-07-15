"""Tests that Redis key templates follow the project naming convention.

The convention is::

    spr:scenario:{scenario_id}:{agent}_{resource}

e.g. ``spr:scenario:scenario-001:strategist_output``.

Both V1 and V2 key templates are verified.
"""

import unittest

from app.allocator.config import AllocatorSettings
from app.allocator.redis_store import _STATE_SECTOR_DEMANDS_KEY_TEMPLATE
from app.strategist.config import StrategistSettings


class RedisKeyConventionTests(unittest.TestCase):
    """Verify all Redis key templates produce the expected keys."""

    def test_scenario_key_templates_are_consistent(self) -> None:
        scenario_id = "scenario-001"
        strategist_settings = StrategistSettings()
        allocator_settings = AllocatorSettings()

        # Strategist keys (unchanged)
        self.assertEqual(
            strategist_settings.strategist_output_key_template.format(
                scenario_id=scenario_id,
            ),
            "spr:scenario:scenario-001:strategist_output",
        )
        self.assertEqual(
            strategist_settings.strategist_state_key_template.format(
                scenario_id=scenario_id,
            ),
            "spr:scenario:scenario-001:strategist_state",
        )

        # Allocator V1 keys (backward compatibility)
        self.assertEqual(
            allocator_settings.state_demand_profiles_key_template.format(
                scenario_id=scenario_id,
            ),
            "spr:scenario:scenario-001:state_demand_profiles",
        )
        self.assertEqual(
            allocator_settings.allocator_output_key_template.format(
                scenario_id=scenario_id,
            ),
            "spr:scenario:scenario-001:allocator_output",
        )
        self.assertEqual(
            allocator_settings.allocator_state_key_template.format(
                scenario_id=scenario_id,
            ),
            "spr:scenario:scenario-001:allocator_state",
        )

        # Allocator V2 key (new)
        self.assertEqual(
            _STATE_SECTOR_DEMANDS_KEY_TEMPLATE.format(scenario_id=scenario_id),
            "spr:scenario:scenario-001:state_sector_demands",
        )


if __name__ == "__main__":
    unittest.main()
