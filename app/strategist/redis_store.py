"""Redis storage and event publishing for the Strategist Agent."""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

from pydantic import BaseModel

from app.shared.redis_client import get_redis_client
from app.strategist.config import StrategistSettings
from app.strategist.schemas import StrategistOutput


def to_jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}

    if isinstance(value, list):
        return [to_jsonable(item) for item in value]

    if isinstance(value, tuple):
        return [to_jsonable(item) for item in value]

    return value


class StrategistRedisStore:
    def __init__(self, settings: StrategistSettings):
        self.settings = settings
        self.client = get_redis_client(settings.redis_url)

    def strategist_output_key(self, scenario_id: str) -> str:
        return self.settings.strategist_output_key_template.format(scenario_id=scenario_id)

    def strategist_state_key(self, scenario_id: str) -> str:
        return self.settings.strategist_state_key_template.format(scenario_id=scenario_id)

    def load_current_reserve_state(self, scenario_id: str) -> dict[str, Any] | None:
        raw = self.client.get(self.settings.reserve_state_key)
        if not raw:
            return None

        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError(f"Reserve state at {self.settings.reserve_state_key} must be a JSON object")

        return payload

    def save_state(self, scenario_id: str, state: dict[str, Any]) -> str:
        key = self.strategist_state_key(scenario_id)
        payload = json.dumps(to_jsonable(state), sort_keys=True)
        self._set(key, payload)
        return key

    def save_output(self, output: StrategistOutput) -> str:
        key = self.strategist_output_key(output.scenario_id)
        self._set(key, output.model_dump_json())
        return key

    def publish_completed(self, scenario_id: str, output_key: str) -> dict[str, Any]:
        payload = {
            "event": self.settings.completion_channel,
            "scenario_id": scenario_id,
            "next_agent": "allocator",
            "redis_key": output_key,
        }
        self.client.publish(self.settings.completion_channel, json.dumps(payload, sort_keys=True))
        return payload

    def _set(self, key: str, payload: str) -> None:
        if self.settings.redis_ttl_seconds:
            self.client.setex(key, self.settings.redis_ttl_seconds, payload)
        else:
            self.client.set(key, payload)
