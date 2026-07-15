"""LangGraph state type for the Allocator Agent V2."""

from __future__ import annotations

from typing import Any, TypedDict

from app.allocator.schemas import AllocatorInput, AllocatorOutput
from app.strategist.schemas import StrategistOutput


class AllocatorState(TypedDict, total=False):
    raw_input: dict[str, Any]
    validated_input: AllocatorInput
    strategist_output: StrategistOutput
    final_output: AllocatorOutput
    redis_output_key: str
    redis_state_key: str
    event_payload: dict[str, Any]
    errors: list[str]
