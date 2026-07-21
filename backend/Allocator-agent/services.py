"""Business services for the Allocator Agent V2.

Orchestration-only layer.  No allocation logic belongs here — it all
lives in ``app.allocator.calculations``.

Responsibilities
----------------
* Define the ``AllocatorStore`` protocol (store abstraction).
* Load and validate the Strategist approved output from the store.
* Load state-sector demand records (from input or store).
* Call ``generate_distribution_plan()`` from the calculations layer.
* Return the completed ``AllocatorOutput``.
"""

from __future__ import annotations

from typing import Any, Protocol

from calculations import generate_distribution_plan
from schemas import (
    AllocatorInput,
    AllocatorOutput,
    StateSectorDemand,
)
from strategist_contract import StrategistOutput


class AllocatorStore(Protocol):
    """Interface for the Allocator's persistence and event layer.

    Adopted by both ``AllocatorRedisStore`` (production) and
    ``DemoAllocatorStore`` (used in the CLI runner).
    """

    # ── Read ──────────────────────────────────────────────────

    def load_strategist_output(self, scenario_id: str) -> dict[str, Any] | None:
        """Load the StrategistAgent output for *scenario_id* from the store.

        Returns a raw dict (or ``None`` if not found) that the caller
        will validate into a ``StrategistOutput``.
        """

    def load_state_sector_demands(
        self, scenario_id: str,
    ) -> list[dict[str, Any]] | None:
        """Load state-sector demand records for *scenario_id*.

        Returns a list of raw dicts (or ``None``) that the caller will
        validate into ``StateSectorDemand`` objects.
        """

    # ── Write ─────────────────────────────────────────────────

    def save_state(self, scenario_id: str, state: dict[str, Any]) -> str:
        """Persist a snapshot of the allocator graph state.

        Returns the Redis key under which the state was saved.
        """

    def save_output(self, output: AllocatorOutput) -> str:
        """Persist the final allocation output.

        Returns the Redis key under which the output was saved.
        """

    def publish_completed(
        self, scenario_id: str, output_key: str,
    ) -> dict[str, Any]:
        """Publish an ``allocator.completed`` event to Redis Pub/Sub.

        Returns the event payload dict for logging or inspection.
        """


# ──────────────────────────────────────────────
# Data-loading helpers
# ──────────────────────────────────────────────


def load_strategist_output(
    input_data: AllocatorInput,
    store: AllocatorStore | None,
) -> StrategistOutput:
    """Load and validate the StrategistAgent output.

    Parameters
    ----------
    input_data : AllocatorInput
        The validated Allocator input containing the ``scenario_id``.
    store : AllocatorStore | None
        The store instance.  A ``None`` store raises immediately
        because the Strategist output must always be loaded externally.

    Returns
    -------
    StrategistOutput
        The validated Strategist decision.

    Raises
    ------
    ValueError
        If *store* is ``None``, the scenario output is missing, or the
        ``scenario_id`` values do not match.
    """
    if store is None:
        raise ValueError(
            "No store configured for loading the Strategist output. "
            "The Allocator requires an external Strategist decision.",
        )

    payload = store.load_strategist_output(input_data.scenario_id)
    if not payload:
        raise ValueError(
            f"Strategist output not found for scenario_id="
            f"'{input_data.scenario_id}'. Ensure the Strategist Agent "
            f"has been executed before the Allocator.",
        )

    strategist_output = StrategistOutput.model_validate(payload)
    if strategist_output.scenario_id != input_data.scenario_id:
        raise ValueError(
            f"Strategist output scenario_id "
            f"('{strategist_output.scenario_id}') does not match "
            f"Allocator input scenario_id "
            f"('{input_data.scenario_id}').",
        )

    return strategist_output


def load_state_sector_demands(
    input_data: AllocatorInput,
    store: AllocatorStore | None,
) -> list[StateSectorDemand]:
    """Load state-sector demand records.

    The primary data source is ``input_data.state_sector_demands``
    (provided directly as part of the Allocator input).  If that is
    unavailable (defensive fallback), the method attempts to load the
    records from the store.

    Parameters
    ----------
    input_data : AllocatorInput
        The validated Allocator input.
    store : AllocatorStore | None
        The store instance, used as fallback if the input does not
        contain demand records.

    Returns
    -------
    list[StateSectorDemand]
        Validated demand records.

    Raises
    ------
    ValueError
        If neither the input nor the store can provide demand records.
    """
    if input_data.state_sector_demands:
        return list(input_data.state_sector_demands)

    if store is None:
        raise ValueError(
            "No state-sector demand records provided in the input "
            "and no store configured to load them.",
        )

    payload = store.load_state_sector_demands(input_data.scenario_id)
    if not payload:
        raise ValueError(
            f"State-sector demand records not found for scenario_id="
            f"'{input_data.scenario_id}'.",
        )

    return [StateSectorDemand.model_validate(item) for item in payload]


# ──────────────────────────────────────────────
# Orchestration
# ──────────────────────────────────────────────


def execute_allocation(
    input_data: AllocatorInput,
    store: AllocatorStore | None = None,
) -> AllocatorOutput:
    """Execute the full allocation pipeline and return the result.

    This is the primary orchestration entry point for the service
    layer.  It:

    1. Loads the Strategist decision.
    2. Loads state-sector demand records.
    3. Delegates to ``generate_distribution_plan()`` in calculations.
    4. Returns the completed ``AllocatorOutput``.

    Parameters
    ----------
    input_data : AllocatorInput
        The validated input (scenario identifier + demand records).
    store : AllocatorStore | None, optional
        The store for external reads/writes.  Required when the
        Strategist output or demand records must be loaded from Redis.

    Returns
    -------
    AllocatorOutput
        The fully populated allocation result (including reasoning).
    """
    strategist_output = load_strategist_output(input_data, store)
    state_sector_demands = load_state_sector_demands(input_data, store)

    return generate_distribution_plan(strategist_output, state_sector_demands)
