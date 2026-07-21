"""LangGraph workflow for the Strategist Agent."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from calculations import (
    calculate_usable_reserve,
    evaluate_coverage_status,
    generate_release_metrics,
)
from schemas import StrategistInput
from services import StrategistStore, build_final_output, load_reserve_state
from state import StrategistState


def _errors(state: StrategistState) -> list[str]:
    return list(state.get("errors", []))


def _error_update(state: StrategistState, message: str) -> StrategistState:
    errors = _errors(state)
    errors.append(message)
    return {"errors": errors}


def _route_on_errors(state: StrategistState) -> str:
    return "error" if state.get("errors") else "ok"


def build_strategist_graph(store: StrategistStore | None = None) -> Any:
    """Build and compile the Strategist Agent workflow."""
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:
        raise ImportError(
            "LangGraph is required to build the Strategist workflow. "
            "Install dependencies with: pip install -r requirements.txt"
        ) from exc

    def validate_input(state: StrategistState) -> StrategistState:
        try:
            raw_input = state.get("raw_input", {})
            return {
                "validated_input": StrategistInput.model_validate(raw_input),
                "errors": _errors(state),
            }
        except ValidationError as exc:
            return _error_update(state, exc.json())

    def load_current_reserve_state(state: StrategistState) -> StrategistState:
        try:
            input_data = state["validated_input"]
            return {"reserve_state": load_reserve_state(input_data, store)}
        except Exception as exc:
            return _error_update(state, f"Failed to load reserve state: {exc}")

    def calculate_available_reserve(state: StrategistState) -> StrategistState:
        try:
            return {"usable_reserve_barrels": calculate_usable_reserve(state["reserve_state"])}
        except Exception as exc:
            return _error_update(state, f"Failed to calculate usable reserve: {exc}")

    def generate_spr_release_plan(state: StrategistState) -> StrategistState:
        try:
            return {
                "release_metrics": generate_release_metrics(
                    input_data=state["validated_input"],
                    reserve_state=state["reserve_state"],
                    usable_reserve_barrels=state["usable_reserve_barrels"],
                )
            }
        except Exception as exc:
            return _error_update(state, f"Failed to generate SPR release plan: {exc}")

    def evaluate_coverage(state: StrategistState) -> StrategistState:
        try:
            return {
                "coverage_status": evaluate_coverage_status(
                    input_data=state["validated_input"],
                    release_metrics=state["release_metrics"],
                )
            }
        except Exception as exc:
            return _error_update(state, f"Failed to evaluate coverage status: {exc}")

    def generate_decision_summary(state: StrategistState) -> StrategistState:
        try:
            final_output = build_final_output(
                input_data=state["validated_input"],
                reserve_state=state["reserve_state"],
                usable_reserve_barrels=state["usable_reserve_barrels"],
                release_metrics=state["release_metrics"],
                coverage_status=state["coverage_status"],
            )
            return {
                "strategy_reasoning": final_output.strategy_reasoning,
                "final_output": final_output,
            }
        except Exception as exc:
            return _error_update(state, f"Failed to generate decision summary: {exc}")

    def save_output_to_redis(state: StrategistState) -> StrategistState:
        if store is None:
            return _error_update(state, "No Redis store configured for Strategist Agent")

        try:
            output = state["final_output"]
            output_key = store.save_output(output)
            state_snapshot = dict(state)
            state_snapshot["redis_output_key"] = output_key
            state_key = store.save_state(output.scenario_id, state_snapshot)
            return {
                "redis_output_key": output_key,
                "redis_state_key": state_key,
            }
        except Exception as exc:
            return _error_update(state, f"Failed to save Strategist output to Redis: {exc}")

    def publish_completion_event(state: StrategistState) -> StrategistState:
        if store is None:
            return _error_update(state, "No Redis store configured for Strategist Agent")

        try:
            output = state["final_output"]
            event_payload = store.publish_completed(output.scenario_id, state["redis_output_key"])
            return {"event_payload": event_payload}
        except Exception as exc:
            return _error_update(state, f"Failed to publish Strategist completion event: {exc}")

    workflow = StateGraph(StrategistState)

    workflow.add_node("validate_input", validate_input)
    workflow.add_node("load_current_reserve_state", load_current_reserve_state)
    workflow.add_node("calculate_available_reserve", calculate_available_reserve)
    workflow.add_node("generate_spr_release_plan", generate_spr_release_plan)
    workflow.add_node("evaluate_coverage_status", evaluate_coverage)
    workflow.add_node("generate_decision_summary", generate_decision_summary)
    workflow.add_node("save_output_to_redis", save_output_to_redis)
    workflow.add_node("publish_completion_event", publish_completion_event)

    workflow.add_edge(START, "validate_input")
    workflow.add_conditional_edges(
        "validate_input",
        _route_on_errors,
        {"ok": "load_current_reserve_state", "error": END},
    )
    workflow.add_conditional_edges(
        "load_current_reserve_state",
        _route_on_errors,
        {"ok": "calculate_available_reserve", "error": END},
    )
    workflow.add_conditional_edges(
        "calculate_available_reserve",
        _route_on_errors,
        {"ok": "generate_spr_release_plan", "error": END},
    )
    workflow.add_conditional_edges(
        "generate_spr_release_plan",
        _route_on_errors,
        {"ok": "evaluate_coverage_status", "error": END},
    )
    workflow.add_conditional_edges(
        "evaluate_coverage_status",
        _route_on_errors,
        {"ok": "generate_decision_summary", "error": END},
    )
    workflow.add_conditional_edges(
        "generate_decision_summary",
        _route_on_errors,
        {"ok": "save_output_to_redis", "error": END},
    )
    workflow.add_conditional_edges(
        "save_output_to_redis",
        _route_on_errors,
        {"ok": "publish_completion_event", "error": END},
    )
    workflow.add_edge("publish_completion_event", END)

    return workflow.compile()
