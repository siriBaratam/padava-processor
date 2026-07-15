"""LangGraph workflow for the Allocator Agent V2.

Workflow sequence
-----------------
1. Validate input        — parse ``AllocatorInput`` from raw JSON.
2. Load Strategist       — fetch approved ``StrategistOutput`` from store.
3. Load demands          — load ``StateSectorDemand`` records.
4. Execute allocation    — delegate to ``generate_distribution_plan``.
5. Prepare logistics     — placeholder for future Navigator integration.
6. Save output           — persist the final ``AllocatorOutput``.
7. Save state            — snapshot the graph state.
8. Publish event         — notify downstream agents.

Each node is single-purpose and wrapped in a try/except that routes
to ``END`` on error.  The pattern matches ``build_strategist_graph``
exactly.
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from app.allocator.schemas import AllocatorInput
from app.allocator.services import (
    AllocatorStore,
    execute_allocation,
    load_state_sector_demands,
    load_strategist_output,
)
from app.allocator.state import AllocatorState


def _errors(state: AllocatorState) -> list[str]:
    """Return the current error list (never ``None``)."""
    return list(state.get("errors", []))


def _error_update(state: AllocatorState, message: str) -> AllocatorState:
    """Append *message* to the error list and return a state update."""
    errors = _errors(state)
    errors.append(message)
    return {"errors": errors}


def _route_on_errors(state: AllocatorState) -> str:
    """Return ``"error"`` when the state carries errors, else ``"ok"``."""
    return "error" if state.get("errors") else "ok"


def build_allocator_graph(store: AllocatorStore | None = None) -> Any:
    """Build and compile the Allocator Agent V2 workflow.

    Parameters
    ----------
    store : AllocatorStore | None, optional
        The persistence store.  When ``None``, nodes that require
        persistence (save / publish) will report an error.

    Returns
    -------
    Any
        A compiled LangGraph ``StateGraph`` application.
    """
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:
        raise ImportError(
            "LangGraph is required to build the Allocator workflow. "
            "Install dependencies with: pip install -r requirements.txt"
        ) from exc

    # ── Node definitions ───────────────────────────────────────

    def validate_input(state: AllocatorState) -> AllocatorState:
        """Parse and validate ``raw_input`` into ``AllocatorInput``."""
        try:
            raw_input = state.get("raw_input", {})
            validated_input = AllocatorInput.model_validate(raw_input)
            return {
                "validated_input": validated_input,
                "errors": _errors(state),
            }
        except ValidationError as exc:
            return _error_update(state, exc.json())

    def load_strategist_decision(state: AllocatorState) -> AllocatorState:
        """Load the approved Strategist output from the store."""
        try:
            return {
                "strategist_output": load_strategist_output(
                    input_data=state["validated_input"],
                    store=store,
                )
            }
        except Exception as exc:
            return _error_update(
                state, f"Failed to load Strategist output: {exc}",
            )

    def load_demand_records(state: AllocatorState) -> AllocatorState:
        """Load state-sector demand records (from input or store)."""
        try:
            demands = load_state_sector_demands(
                input_data=state["validated_input"],
                store=store,
            )
            # Store in state for the execution node.
            # Note: ``state_sector_demands`` is not a declared field of
            # ``AllocatorState`` (to avoid modifying state.py).  LangGraph
            # passes dicts at runtime, so the extra key works fine.
            result: dict[str, Any] = {"state_sector_demands": demands}
            return result  # type: ignore[return-value]
        except Exception as exc:
            return _error_update(
                state, f"Failed to load state-sector demands: {exc}",
            )

    def execute_allocation_node(state: AllocatorState) -> AllocatorState:
        """Run the priority-based distribution algorithm.

        Delegates to the service layer's ``execute_allocation()``
        which in turn calls ``generate_distribution_plan()`` from
        the calculations layer.  Using the service-layer entry point
        ensures consistent orchestration semantics.
        """
        try:
            output = execute_allocation(
                input_data=state["validated_input"],
                store=store,
            )
            return {"final_output": output}
        except Exception as exc:
            return _error_update(
                state, f"Allocation execution failed: {exc}",
            )

    def prepare_logistics_context(state: AllocatorState) -> AllocatorState:
        """Prepare logistics context (placeholder — no Navigator yet).

        The ``AllocatorOutput`` already carries a ``LogisticsContext``
        with a default note explaining that constraints are not yet
        enforced.  This node exists as an extension point for the
        future Navigator agent integration.
        """
        # No-op: the default ``LogisticsContext`` in the output is
        # sufficient.  Future implementations will populate pipeline,
        # rail, and tanker capacity constraints here.
        return {"errors": _errors(state)}

    def save_output_to_redis(state: AllocatorState) -> AllocatorState:
        """Persist the final ``AllocatorOutput`` and a state snapshot."""
        if store is None:
            return _error_update(
                state, "No Redis store configured for Allocator Agent",
            )

        try:
            output = state["final_output"]
            output_key = store.save_output(output)

            # Build a serialisable copy of the state that includes the
            # output key so downstream consumers can locate the result.
            state_snapshot = dict(state)
            state_snapshot["redis_output_key"] = output_key
            state_key = store.save_state(output.scenario_id, state_snapshot)

            return {
                "redis_output_key": output_key,
                "redis_state_key": state_key,
            }
        except Exception as exc:
            return _error_update(
                state, f"Failed to save Allocator output to Redis: {exc}",
            )

    def publish_completion_event(state: AllocatorState) -> AllocatorState:
        """Publish ``allocator.completed`` to Redis Pub/Sub."""
        if store is None:
            return _error_update(
                state, "No Redis store configured for Allocator Agent",
            )

        try:
            output = state["final_output"]
            event_payload = store.publish_completed(
                output.scenario_id,
                state["redis_output_key"],
            )
            return {"event_payload": event_payload}
        except Exception as exc:
            return _error_update(
                state,
                f"Failed to publish Allocator completion event: {exc}",
            )

    # ── Workflow construction ──────────────────────────────────

    workflow = StateGraph(AllocatorState)

    workflow.add_node("validate_input", validate_input)
    workflow.add_node("load_strategist_decision", load_strategist_decision)
    workflow.add_node("load_state_sector_demands", load_demand_records)
    workflow.add_node("execute_allocation", execute_allocation_node)
    workflow.add_node("prepare_logistics_context", prepare_logistics_context)
    workflow.add_node("save_output_to_redis", save_output_to_redis)
    workflow.add_node("publish_completion_event", publish_completion_event)

    # ── Edges ──────────────────────────────────────────────────

    workflow.add_edge(START, "validate_input")

    workflow.add_conditional_edges(
        "validate_input",
        _route_on_errors,
        {"ok": "load_strategist_decision", "error": END},
    )
    workflow.add_conditional_edges(
        "load_strategist_decision",
        _route_on_errors,
        {"ok": "load_state_sector_demands", "error": END},
    )
    workflow.add_conditional_edges(
        "load_state_sector_demands",
        _route_on_errors,
        {"ok": "execute_allocation", "error": END},
    )
    workflow.add_conditional_edges(
        "execute_allocation",
        _route_on_errors,
        {"ok": "prepare_logistics_context", "error": END},
    )
    workflow.add_conditional_edges(
        "prepare_logistics_context",
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
