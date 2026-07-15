"""Configuration for the Allocator Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AllocatorSettings:
    redis_url: str = "redis://localhost:6379/0"
    strategist_output_key_template: str = "spr:scenario:{scenario_id}:strategist_output"
    allocator_output_key_template: str = "spr:scenario:{scenario_id}:allocator_output"
    allocator_state_key_template: str = "spr:scenario:{scenario_id}:allocator_state"
    state_demand_profiles_key_template: str = "spr:scenario:{scenario_id}:state_demand_profiles"
    completion_channel: str = "allocator.completed"
    redis_ttl_seconds: int | None = None


def get_settings() -> AllocatorSettings:
    ttl_raw = os.getenv("ALLOCATOR_REDIS_TTL_SECONDS", "").strip()
    ttl = int(ttl_raw) if ttl_raw else None

    return AllocatorSettings(
        redis_url=os.getenv("REDIS_URL", AllocatorSettings.redis_url),
        completion_channel=os.getenv(
            "ALLOCATOR_COMPLETION_CHANNEL",
            AllocatorSettings.completion_channel,
        ),
        redis_ttl_seconds=ttl,
    )
