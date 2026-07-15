"""Configuration for the Strategist Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class StrategistSettings:
    redis_url: str = "redis://localhost:6379/0"
    strategist_output_key_template: str = "spr:scenario:{scenario_id}:strategist_output"
    strategist_state_key_template: str = "spr:scenario:{scenario_id}:strategist_state"
    reserve_state_key: str = "spr:reserve:current"
    completion_channel: str = "strategist.completed"
    redis_ttl_seconds: int | None = None


def get_settings() -> StrategistSettings:
    ttl_raw = os.getenv("STRATEGIST_REDIS_TTL_SECONDS", "").strip()
    ttl = int(ttl_raw) if ttl_raw else None

    return StrategistSettings(
        redis_url=os.getenv("REDIS_URL", StrategistSettings.redis_url),
        reserve_state_key=os.getenv("SPR_RESERVE_STATE_KEY", StrategistSettings.reserve_state_key),
        completion_channel=os.getenv(
            "STRATEGIST_COMPLETION_CHANNEL",
            StrategistSettings.completion_channel,
        ),
        redis_ttl_seconds=ttl,
    )
