# Allocator Agent V2

## Overview

The Allocator Agent is the distribution engine of the **SPR Command Platform**. It sits downstream of the Strategist Agent and converts the approved SPR release decision into a concrete, actionable fuel distribution plan for every state and sector in India.

```
Strategist → Allocator → Dealmaker
```

The Allocator's job is **not** to divide fuel equally. It implements a hierarchical priority framework that ensures critical national services (defence, healthcare, emergency services, power generation) continue functioning during severe shortages. Only when a priority level is fully satisfied does remaining fuel cascade to the next level.

This optimisation is required because even with SPR release, supply rarely meets total demand during a disruption. The Allocator must make transparent, principled rationing decisions that are explainable to policymakers and traceable to deterministic rules.

---

## Agent Workflow

```
              Strategist Output
                      │
                      ▼
              Validate Input
                      │
                      ▼
          Load Strategist Decision
                      │
                      ▼
           Load State Demand Records
                      │
                      ▼
           Priority Classification
                      │
                      ▼
             Supply Allocation
                      │
                      ▼
             State Distribution
                      │
                      ▼
           Delivery Scheduling
                      │
                      ▼
              Redis Storage
                      │
                      ▼
         Publish Completion Event
```

The pipeline executes as a LangGraph workflow. Each step is a discrete node; conditional edges route errors to `END` with a descriptive message if any node fails.

---

## Responsibilities

| Responsibility | Description |
|---|---|
| **Priority-Based Allocation** | Fuel is never divided equally. Higher-priority sectors receive fuel before lower-priority ones. |
| **Sector Protection** | Level 1 sectors (Defence, Healthcare, Emergency Services, Power Generation) are satisfied first and fully before any fuel reaches Level 2 or Level 3. |
| **State Distribution** | Each sector's national allocation is distributed across states proportionally to each state's demand share for that sector. |
| **Demand Satisfaction** | Every state-sector pair is evaluated for full, partial, or zero satisfaction based on how much of its demand was met. |
| **Rationing Decisions** | When supply is insufficient within a priority level, fuel is distributed proportionally among that level's sectors. |
| **Delivery Planning** | A ranked delivery priority schedule is generated so downstream agents (Navigator, Dealmaker) can sequence fuel logistics. |

---

## Priority Model

### Level 1 — Critical National Security

Sectors that must be sustained at all costs. These are fully satisfied before any other sector receives fuel.

| Sector | Identifier |
|---|---|
| Defence Services | `DEFENSE` |
| Healthcare | `HEALTHCARE` |
| Emergency Services | `EMERGENCY_SERVICES` |
| Power Generation | `POWER_GENERATION` |

### Level 2 — Essential Economic & Social Functions

Sectors that sustain the population and economy. They receive fuel only after Level 1 is fully satisfied.

| Sector | Identifier |
|---|---|
| Agriculture | `AGRICULTURE` |
| Food Supply Chain | `FOOD_SUPPLY` |
| Public Transport | `PUBLIC_TRANSPORT` |

### Level 3 — Non-Essential & Commercial

Sectors with lowest priority. They receive fuel only when Levels 1 and 2 are both fully satisfied.

| Sector | Identifier |
|---|---|
| Commercial | `COMMERCIAL` |
| Industrial Non-Essential | `INDUSTRIAL_NON_ESSENTIAL` |
| Private Consumption | `PRIVATE_CONSUMPTION` |

### Fallback

Any unrecognised sector identifier defaults to **Level 3**.

---

## Architecture

```
app/allocator/
├── config.py          Environment variables and default settings
├── schemas.py         Pydantic input/output models, enums, and sector registry
├── state.py           LangGraph TypedDict state definition
├── calculations.py    Deterministic allocation engine (pure functions)
├── services.py        Orchestration layer and store protocol
├── redis_store.py     Redis persistence and Pub/Sub event publishing
├── graph.py           LangGraph workflow definition
└── runner.py          CLI entry point and programmatic API
```

### `schemas.py`

All data models and the sector-priority registry. Key types:

| Model | Purpose |
|---|---|
| `PriorityLevel` | Enum: `LEVEL_1`, `LEVEL_2`, `LEVEL_3` |
| `AllocationStatus` | Enum: `FULL_ALLOCATION`, `RATIONED_ALLOCATION`, `CRITICAL_ONLY_ALLOCATION`, `NO_ALLOCATION` |
| `SatisfactionStatus` | Enum: `FULL`, `PARTIAL`, `NONE` |
| `StateSectorDemand` | Atomic demand record for a single state-sector pair |
| `AllocatorInput` | Validated input (scenario ID + demand records) |
| `SectorAllocation` | Per-sector allocation result |
| `LevelAllocationSummary` | Aggregate per-priority-level summary |
| `StateAllocation` | Per-state breakdown with sector-level detail |
| `DeliveryPrioritySchedule` | Ranked delivery entry for logistics planning |
| `LogisticsContext` | Placeholder for future Navigator integration |
| `AllocatorOutput` | Complete hierarchical allocation result |
| `SECTOR_PRIORITY_MAP` | Deterministic sector-to-priority lookup table |
| `SECTOR_NAME_MAP` | Human-readable sector name registry |

### `state.py`

A `TypedDict` for LangGraph state. Carries the raw input, validated input, loaded Strategist output, the final allocation result, Redis keys, and error accumulator across all graph nodes.

### `calculations.py`

The deterministic allocation engine. Implements the **Hierarchical Priority Distribution** algorithm as pure functions with no side effects. Key functions:

| Function | Purpose |
|---|---|
| `round_bpd()` | Deterministic rounding to 0.01 BPD using `Decimal` with `ROUND_HALF_UP` |
| `generate_distribution_plan()` | **Sole public API** — orchestrates the full allocation pipeline |
| `_calculate_available_supply()` | Extracts `recommended_spr_release_bpd` from Strategist output |
| `_group_demands_by_priority()` | Single-pass classification of demands by priority level |
| `_allocate_proportionally()` | Proportional distribution within a partially satisfied level |
| `_reconcile_rounded_sum()` | Cyclic modulo rounding — guarantees `sum(values) == target` exactly |
| `_allocate_by_priority_levels()` | Strict L1 → L2 → L3 waterfall allocation |
| `_compute_state_distribution()` | Per-sector proportional state distribution with rounding reconciliation |
| `_build_delivery_priority_schedule()` | Ranked delivery schedule ordered by priority |
| `_evaluate_allocation_status()` | Determines overall status from allocation results |
| `_build_allocation_reasoning()` | Read-only descriptive reasoning from the completed output |

Rounding is reconciled at every boundary — no barrels are lost or created due to floating-point drift.

### `services.py`

Defines the `AllocatorStore` protocol (5 methods: load Strategist output, load demands, save state, save output, publish event). Provides:

- `load_strategist_output()` — loads and validates the Strategist decision from the store
- `load_state_sector_demands()` — loads demand records from input or store
- `execute_allocation()` — orchestrates: load → calculate → return output

Business logic is strictly delegated to `calculations.py`.

### `redis_store.py`

Production Redis persistence. Handles:

- Key generation for all Allocator and Strategist data
- Reading Strategist output and demand datasets
- Writing `AllocatorOutput` and graph state snapshots
- Publishing `allocator.completed` events via Redis Pub/Sub
- Backward-compatible V1 methods preserved
- `to_jsonable()` helper for recursive JSON serialisation of Pydantic models and enums

### `graph.py`

LangGraph workflow with 7 nodes and conditional error routing at every transition:

```
START → validate_input
     → load_strategist_decision
     → load_state_sector_demands
     → execute_allocation
     → prepare_logistics_context      (placeholder for Navigator integration)
     → save_output_to_redis
     → publish_completion_event
     → END
```

### `runner.py`

CLI entry point with three execution modes and an in-memory demo store:

1. **Sample mode** — `python -m app.allocator.runner` (built-in scenario with 4 states, 12 demand records, demo Strategist output)
2. **File mode** — `python -m app.allocator.runner input.json`
3. **Stdin mode** — `python -m app.allocator.runner < input.json`

The `DemoAllocatorStore` provides an in-memory store with a hardcoded Strategist output so the sample mode works without Redis.

### `config.py`

Frozen dataclass with environment variable overrides for Redis URL, key templates, TTL, and completion channel name.

---

## Input Example

```json
{
  "scenario_id": "IND_CRISIS_001",
  "state_sector_demands": [
    {
      "state_code": "AP",
      "state_name": "Andhra Pradesh",
      "sector_id": "POWER_GENERATION",
      "daily_demand_bpd": 50000
    },
    {
      "state_code": "AP",
      "state_name": "Andhra Pradesh",
      "sector_id": "AGRICULTURE",
      "daily_demand_bpd": 75000
    },
    {
      "state_code": "MH",
      "state_name": "Maharashtra",
      "sector_id": "HEALTHCARE",
      "daily_demand_bpd": 120000
    },
    {
      "state_code": "MH",
      "state_name": "Maharashtra",
      "sector_id": "DEFENSE",
      "daily_demand_bpd": 80000
    },
    {
      "state_code": "GJ",
      "state_name": "Gujarat",
      "sector_id": "DEFENSE",
      "daily_demand_bpd": 60000
    },
    {
      "state_code": "TN",
      "state_name": "Tamil Nadu",
      "sector_id": "COMMERCIAL",
      "daily_demand_bpd": 60000
    }
  ]
}
```

| Field | Type | Constraints | Description |
|---|---|---|---|
| `scenario_id` | `string` | min 1 char | Must match the Strategist scenario |
| `state_sector_demands` | `array` | min 1 item | Atomic demand records, one per state-sector pair |
| `state_sector_demands[].state_code` | `string` | min 1 char | Normalised to uppercase (e.g. `MH`, `GJ`) |
| `state_sector_demands[].state_name` | `string` | min 1 char | Full state name |
| `state_sector_demands[].sector_id` | `string` | min 1 char | Normalised to uppercase; must match a known sector or default to LEVEL_3 |
| `state_sector_demands[].daily_demand_bpd` | `float` | > 0 | Daily fuel requirement for this state-sector pair |

Note: The approved release volume (`recommended_spr_release_bpd`) is **not** included in the input. It is always loaded from the Strategist output stored in Redis, ensuring the Strategist remains the single source of truth.

---

## Output Example

```json
{
  "scenario_id": "IND_CRISIS_001",
  "total_available_bpd": 250000.0,
  "total_national_demand_bpd": 445000.0,
  "total_allocated_bpd": 250000.0,
  "total_unmet_bpd": 195000.0,
  "national_rationing_percent": 43.82,
  "allocation_status": "RATIONED_ALLOCATION",
  "level_summaries": [
    {
      "priority_level": 1,
      "total_demand_bpd": 310000.0,
      "total_allocated_bpd": 250000.0,
      "total_unmet_bpd": 60000.0,
      "is_fully_satisfied": false,
      "sectors": [
        {
          "sector_id": "HEALTHCARE",
          "sector_name": "Healthcare",
          "priority_level": 1,
          "daily_demand_bpd": 120000.0,
          "allocated_bpd": 96774.19,
          "unmet_demand_bpd": 23225.81,
          "rationing_percent": 19.35,
          "satisfaction_status": "PARTIAL"
        }
      ]
    }
  ],
  "sector_allocations": [
    {
      "sector_id": "HEALTHCARE",
      "sector_name": "Healthcare",
      "priority_level": 1,
      "daily_demand_bpd": 120000.0,
      "allocated_bpd": 96774.19,
      "unmet_demand_bpd": 23225.81,
      "rationing_percent": 19.35,
      "satisfaction_status": "PARTIAL"
    }
  ],
  "state_allocations": [
    {
      "state_code": "MH",
      "state_name": "Maharashtra",
      "sector_allocations": [
        {
          "sector_id": "HEALTHCARE",
          "sector_name": "Healthcare",
          "priority_level": 1,
          "daily_demand_bpd": 120000.0,
          "allocated_bpd": 96774.19,
          "unmet_demand_bpd": 23225.81,
          "rationing_percent": 19.35,
          "satisfaction_status": "PARTIAL"
        }
      ],
      "total_allocated_bpd": 96774.19,
      "total_demand_bpd": 120000.0,
      "total_unmet_bpd": 23225.81,
      "rationing_percent": 19.35
    }
  ],
  "delivery_priority_schedule": [
    {
      "priority_rank": 1,
      "priority_level": 1,
      "sector_id": "HEALTHCARE",
      "sector_name": "Healthcare",
      "allocated_bpd": 96774.19,
      "delivery_urgency": "IMMEDIATE",
      "rationale": "Priority Level 1 — Healthcare: 96,774.19 bpd allocated"
    }
  ],
  "logistics_context": {
    "logistics_note": "Logistics constraints are not yet enforced. The Navigator agent integration is required for pipeline, rail, and tanker capacity validation."
  },
  "allocation_reasoning": "Allocation was rationed across priority levels. Level 1: 250,000.00/310,000.00 bpd. Level 2: 0.00/75,000.00 bpd (rationed). Level 3: 0.00/60,000.00 bpd (rationed). National unmet: 195,000.00 bpd (43.82%)."
}
```

| Field | Type | Description |
|---|---|---|
| `total_available_bpd` | `float` | Daily supply released from SPR (from Strategist) |
| `total_national_demand_bpd` | `float` | Aggregated national demand across all states and sectors |
| `total_allocated_bpd` | `float` | Total fuel allocated across all sectors |
| `total_unmet_bpd` | `float` | Demand not covered by allocation |
| `national_rationing_percent` | `float` | Percentage of demand left unmet |
| `allocation_status` | `string` | FULL / RATIONED / CRITICAL_ONLY / NO allocation |
| `level_summaries` | `array` | Per-priority-level aggregated results |
| `sector_allocations` | `array` | Per-sector national allocation details |
| `state_allocations` | `array` | Per-state allocation broken down by sector |
| `delivery_priority_schedule` | `array` | Ranked delivery entries ordered by priority |
| `logistics_context` | `object` | Placeholder for future Navigator constraints |
| `allocation_reasoning` | `string` | Deterministic, human-readable explanation |

---

## Redis Integration

### Stored Keys

```
spr:scenario:{scenario_id}:strategist_output
spr:scenario:{scenario_id}:allocator_output
spr:scenario:{scenario_id}:allocator_state
spr:scenario:{scenario_id}:state_sector_demands
```

| Key | Purpose |
|---|---|
| `strategist_output` | Read by Allocator to obtain the approved `recommended_spr_release_bpd` |
| `allocator_output` | Written with the complete `AllocatorOutput` after allocation completes |
| `allocator_state` | Written with a snapshot of the LangGraph state for observability |
| `state_sector_demands` | Optional read — demand records can be pre-loaded here alongside the input |

All V1 keys (`state_demand_profiles`) are preserved for backward compatibility.

### Event Publishing

After saving output, the agent publishes to channel:

```
allocator.completed
```

Event payload:

```json
{
  "event": "allocator.completed",
  "scenario_id": "IND_CRISIS_001",
  "next_agent": "dealmaker",
  "redis_key": "spr:scenario:IND_CRISIS_001:allocator_output"
}
```

---

## Running the Agent

### Prerequisites

```bash
pip install -r requirements.txt
```

### CLI Execution

```bash
# Run built-in sample scenario (4 states, 12 demand records, demo Strategist output)
python -m app.allocator.runner

# Run with a JSON input file
python -m app.allocator.runner input.json

# Run with piped JSON
python -m app.allocator.runner < input.json
```

The sample mode uses an in-memory demo store and does **not** require a running Redis instance.

### Programmatic API

```python
from app.allocator.runner import run_allocator

payload = {
    "scenario_id": "IND_CRISIS_001",
    "state_sector_demands": [
        {
            "state_code": "MH",
            "state_name": "Maharashtra",
            "sector_id": "HEALTHCARE",
            "daily_demand_bpd": 120000
        },
    ],
}
output = run_allocator(payload)
print(output.allocation_reasoning)
```

---

## Testing

```bash
# Run all tests (Strategist + Allocator)
python -m unittest discover -s tests

# Run Allocator-specific tests
python -m unittest tests.test_allocator_calculations
python -m unittest tests.test_allocator_graph
python -m unittest tests.test_allocator_runner
python -m unittest tests.test_redis_key_conventions
```

Calculation tests are pure unit tests with no external dependencies. Graph tests use in-memory fake stores and are skipped when LangGraph is not installed. Runner tests verify file, stdin, and sample input loading.

The test suite covers:
- Full allocation (supply ≥ demand)
- Zero allocation (no SPR release)
- Critical-only allocation (L1 only satisfied, L2/L3 exist + get 0)
- Rationed allocation (proportional within level)
- Unknown sector defaults to Level 3
- Deterministic rounding and reconciliation
- State distribution rounding integrity
- Modulo cycling for rounding deltas exceeding sector count
- Delivery priority ordering
- Reasoning for all four allocation statuses
- Graph execution, persistence, and event publishing

---

## Design Principles

| Principle | Implementation |
|---|---|
| **Deterministic Allocation Engine** | All calculations use `Decimal` with `ROUND_HALF_UP`. No randomness. No LLM involvement in numerical decisions. |
| **Priority-First Distribution** | Strict L1 → L2 → L3 waterfall. Higher-priority sectors are always satisfied before lower-priority ones. |
| **Rounding Integrity** | Every distribution boundary (sector and state level) reconciles rounding so `sum(values) == target` exactly. No barrels are lost or created. |
| **Pydantic Contracts** | Every input, output, and intermediate structure is validated by strongly typed Pydantic models. |
| **LangGraph Orchestration** | The pipeline runs as a directed graph with single-purpose nodes and conditional error routing. |
| **Redis Event Communication** | Completion events are published via Redis Pub/Sub, enabling loose coupling with downstream agents (Dealmaker, Navigator). |
| **Protocol Abstraction** | The store interface is defined as a Python Protocol, allowing in-memory stores for testing and Redis stores for production. |
| **Backward Compatibility** | All V1 Redis methods and key templates are preserved. The V2 architecture is fully additive. |
