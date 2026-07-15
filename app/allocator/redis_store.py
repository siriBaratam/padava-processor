"""Redis storage and event publishing for the Allocator Agent V2.

Provides production Redis persistence for the Allocator pipeline.
The implementation mirrors the ``StrategistRedisStore`` pattern exactly.

Backward compatibility
----------------------
All V1 methods (``load_state_demand_profiles``, the original key
generators) are preserved so existing callers and tests continue to
work.  New V2 methods are additive.
"""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

from pydantic import BaseModel

from app.allocator.config import AllocatorSettings
from app.allocator.schemas import AllocatorOutput
from app.shared.redis_client import get_redis_client


# Default key template for the V2 state-sector demand dataset.
# This will move into ``AllocatorSettings`` when the config module
# is updated; it lives here for now so that ``config.py`` does not
# need to be touched.
_STATE_SECTOR_DEMANDS_KEY_TEMPLATE: str = (
    "spr:scenario:{scenario_id}:state_sector_demands"
)


def to_jsonable(value: Any) -> Any:
    """Recursively convert a Python value into a JSON-serialisable form.

    Handles ``BaseModel`` instances (via ``model_dump(mode="json")``),
    ``Enum`` members (via ``.value``), and standard containers (dict,
    list, tuple).  Everything else is returned unchanged.
    """
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


class AllocatorRedisStore:
    """Production Redis persistence for the Allocator Agent.

    Parameters
    ----------
    settings : AllocatorSettings
        Configuration including Redis URL, key templates, TTL, and
        the completion Pub/Sub channel name.
    """

    def __init__(self, settings: AllocatorSettings) -> None:
        self.settings = settings
        self.client = get_redis_client(settings.redis_url)

    # ── Key generation ─────────────────────────────────────────

    def strategist_output_key(self, scenario_id: str) -> str:
        """Return the Redis key for a scenario's Strategist output."""
        return self.settings.strategist_output_key_template.format(
            scenario_id=scenario_id,
        )

    def allocator_output_key(self, scenario_id: str) -> str:
        """Return the Redis key for a scenario's Allocator output."""
        return self.settings.allocator_output_key_template.format(
            scenario_id=scenario_id,
        )

    def allocator_state_key(self, scenario_id: str) -> str:
        """Return the Redis key for a scenario's Allocator state snapshot."""
        return self.settings.allocator_state_key_template.format(
            scenario_id=scenario_id,
        )

    def state_demand_profiles_key(self, scenario_id: str) -> str:
        """Return the Redis key for V1 state-demand profiles (deprecated)."""
        return self.settings.state_demand_profiles_key_template.format(
            scenario_id=scenario_id,
        )

    def state_sector_demands_key(self, scenario_id: str) -> str:
        """Return the Redis key for V2 state-sector demand records."""
        return _STATE_SECTOR_DEMANDS_KEY_TEMPLATE.format(
            scenario_id=scenario_id,
        )

    # ── Read helpers ───────────────────────────────────────────

    def load_strategist_output(self, scenario_id: str) -> dict[str, Any] | None:
        """Fetch the Strategist output for *scenario_id*.

        Returns a raw dict (or ``None`` if missing) ready for
        ``StrategistOutput.model_validate()``.
        """
        return self._load_json_object(self.strategist_output_key(scenario_id))

    def load_state_demand_profiles(  # noqa: D102  # V1 backward compat
        self, scenario_id: str,
    ) -> list[dict[str, Any]] | None:
        """V1 — load state-demand profiles (deprecated)."""
        raw = self.client.get(self.state_demand_profiles_key(scenario_id))
        if not raw:
            return None

        payload = json.loads(raw)
        if not isinstance(payload, list):
            raise ValueError(
                f"State demand profiles at "
                f"'{self.state_demand_profiles_key(scenario_id)}' "
                f"must be a JSON list.",
            )
        return payload

    def load_state_sector_demands(  # noqa: D102
        self, scenario_id: str,
    ) -> list[dict[str, Any]] | None:
        """V2 — load state-sector demand records from Redis.

        Returns a list of raw dicts (or ``None``) ready for
        ``StateSectorDemand.model_validate()``.
        """
        raw = self.client.get(self.state_sector_demands_key(scenario_id))
        if not raw:
            return None

        payload = json.loads(raw)
        if not isinstance(payload, list):
            raise ValueError(
                f"State-sector demands at "
                f"'{self.state_sector_demands_key(scenario_id)}' "
                f"must be a JSON list.",
            )
        return payload

    # ── Write helpers ──────────────────────────────────────────

    def save_state(self, scenario_id: str, state: dict[str, Any]) -> str:
        """Snapshot the current Allocator graph state to Redis.

        Parameters
        ----------
        scenario_id : str
            Scenario identifier.
        state : dict[str, Any]
            The complete LangGraph state dict.

        Returns
        -------
        str
            The Redis key under which the state was saved.
        """
        key = self.allocator_state_key(scenario_id)
        payload = json.dumps(to_jsonable(state), sort_keys=True)
        self._set(key, payload)
        return key

    def save_output(self, output: AllocatorOutput) -> str:
        """Persist the final Allocator output to Redis.

        Parameters
        ----------
        output : AllocatorOutput
            The completed allocation result.

        Returns
        -------
        str
            The Redis key under which the output was saved.
        """
        key = self.allocator_output_key(output.scenario_id)
        self._set(key, output.model_dump_json())
        return key

    # ── Event publishing ───────────────────────────────────────

    def publish_completed(
        self, scenario_id: str, output_key: str,
    ) -> dict[str, Any]:
        """Publish an ``allocator.completed`` event to Redis Pub/Sub.

        Downstream agents (Dealmaker, Navigator) subscribe to this
        channel to be notified when allocation is finished.

        Parameters
        ----------
        scenario_id : str
            The completed scenario.
        output_key : str
            The Redis key where the output was saved.

        Returns
        -------
        dict[str, Any]
            The event payload for logging or inspection.
        """
        payload = {
            "event": self.settings.completion_channel,
            "scenario_id": scenario_id,
            "next_agent": "dealmaker",
            "redis_key": output_key,
        }
        self.client.publish(
            self.settings.completion_channel,
            json.dumps(payload, sort_keys=True),
        )
        return payload

    # ── Internal helpers ───────────────────────────────────────

    def _load_json_object(self, key: str) -> dict[str, Any] | None:
        """Deserialise a JSON-object value from *key*.

        Parameters
        ----------
        key : str
            Redis key.

        Returns
        -------
        dict[str, Any] | None
            The parsed object, or ``None`` if the key is missing.

        Raises
        ------
        ValueError
            If the value exists but is not a JSON object.
        """
        raw = self.client.get(key)
        if not raw:
            return None

        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError(
                f"Redis key '{key}' must contain a JSON object, "
                f"got {type(payload).__name__}.",
            )
        return payload

    def _set(self, key: str, payload: str) -> None:
        """Write *payload* to *key*, optionally with a TTL.

        Parameters
        ----------
        key : str
            Redis key.
        payload : str
            Serialised JSON string.
        """
        if self.settings.redis_ttl_seconds:
            self.client.setex(key, self.settings.redis_ttl_seconds, payload)
        else:
            self.client.set(key, payload)
