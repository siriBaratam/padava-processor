# Strategist Agent

## Overview

The Strategist Agent is a core decision engine within the **SPR Command Platform** (Strategic Petroleum Reserve Command Platform). It sits at the centre of the multi-agent pipeline, consuming validated shortage and risk data from upstream agents (Scout, Accountant) and producing deterministic SPR release recommendations that are consumed by the downstream Allocator Agent.

```
Scout → Accountant → Strategist → Allocator → Dealmaker → Navigator → Translator
```

The Strategist is responsible for deciding **how much** of India's Strategic Petroleum Reserve should be released during a crude oil supply disruption, **for how long**, and whether the proposed release adequately covers the national shortfall.

---

## Agent Workflow

```
                    Input
                      │
                      ▼
             Validate Input
                      │
                      ▼
            Load Reserve State
                      │
                      ▼
         Calculate Available Reserve
                      │
                      ▼
          Generate SPR Release Plan
                      │
                      ▼
            Evaluate Coverage
                      │
                      ▼
              Save Output
                      │
                      ▼
        Publish Completion Event
```

Each step is a discrete node in the LangGraph workflow. Conditional error handling routes the graph to `END` with a descriptive error if any node fails.

---

## Responsibilities

| Responsibility | Description |
|---|---|
| **Risk Evaluation** | Accepts risk level (LOW / MEDIUM / HIGH / CRITICAL) from upstream agents and factors it into reserve release strategy. |
| **SPR Release Calculation** | Computes the recommended daily release (`recommended_spr_release_bpd`) based on the net shortfall, usable reserve, and disruption timeline. |
| **Reserve Protection** | Ensures the minimum safety reserve is preserved. Only the excess above the safety threshold is considered usable. |
| **Coverage Assessment** | Evaluates whether the recommended release fully covers, partially covers, or fails to cover the national shortfall. |
| **Decision Reasoning** | Generates deterministic, human-readable reasoning that explains the release strategy. No LLM involvement in numerical computation. |

---

## Architecture

```
app/strategist/
├── config.py          Environment variables and default settings
├── schemas.py         Pydantic input/output models and validation
├── state.py           LangGraph TypedDict state definition
├── calculations.py    Deterministic business logic (no side effects)
├── services.py        Orchestration layer and store protocol
├── redis_store.py     Redis persistence and Pub/Sub event publishing
├── graph.py           LangGraph workflow definition
└── runner.py          CLI entry point and programmatic API
```

### `schemas.py`

Pydantic models for all data entering and leaving the agent. Includes:

- `StrategistInput` — validated input from upstream agents
- `StrategistOutput` — the final release decision consumed by the Allocator
- `ReserveState` — current SPR reserve and minimum safety threshold
- `SPRReleaseMetrics` — intermediate calculation results
- `RiskLevel` — enum: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- `CoverageStatus` — enum: `FULL_COVERAGE`, `PARTIAL_COVERAGE`, `NO_COVERAGE`

Validation rules ensure internal consistency (e.g. safety reserve cannot exceed current reserve, shortfall cannot exceed national demand).

### `state.py`

A `TypedDict` that defines the shape of data flowing through the LangGraph. Carries raw input, validated input, intermediate calculations, the final output, Redis keys, and error state across all graph nodes.

### `calculations.py`

The deterministic core of the agent. All numerical logic is implemented here as pure functions with no side effects. Key functions:

| Function | Purpose |
|---|---|
| `calculate_usable_reserve()` | Excess above safety threshold |
| `determine_release_duration_days()` | Min of disruption days and import delay |
| `generate_release_metrics()` | Full SPR release plan |
| `evaluate_coverage_status()` | Full / Partial / No coverage |
| `build_strategy_reasoning()` | Deterministic explanation string |

No Redis, LangGraph, or LLM imports are permitted in this module.

### `services.py`

Orchestration layer that connects the calculation layer to the outside world. Defines the `StrategistStore` protocol (abstracting Redis behind an interface) and provides:

- `load_reserve_state()` — loads optional external reserve state, falls back to input defaults
- `build_final_output()` — assembles all components into the final `StrategistOutput`

### `redis_store.py`

Implements the `StrategistStore` protocol for production Redis usage. Handles:

- Serialisation of Pydantic models and enums to JSON
- Writing output and state snapshots to Redis
- Publishing completion events via Redis Pub/Sub
- Optional TTL-based key expiration

### `graph.py`

Defines the LangGraph `StateGraph` workflow. Each node is a single-purpose Python function. The graph uses conditional edges to route errors to `END` after any node failure.

### `runner.py`

CLI entry point and programmatic API. Three execution modes:

1. **Sample mode** — `python -m app.strategist.runner` (built-in demo scenario)
2. **File mode** — `python -m app.strategist.runner input.json`
3. **Stdin mode** — `python -m app.strategist.runner < input.json`

### `config.py`

Frozen dataclass for all configurable settings. Supports environment variable overrides for Redis URL, key templates, TTL, and completion channel names.

---

## Input Contract

```json
{
  "scenario_id": "IND_CRISIS_001",
  "risk_level": "HIGH",
  "net_daily_shortfall_bpd": 250000,
  "estimated_disruption_days": 30,
  "current_spr_reserve_barrels": 5000000,
  "minimum_safety_reserve_barrels": 1000000,
  "daily_national_demand_bpd": 5000000,
  "import_delay_days": 15
}
```

| Field | Type | Constraints | Description |
|---|---|---|---|
| `scenario_id` | `string` | min 1 char | Unique scenario identifier |
| `risk_level` | `string` | LOW / MEDIUM / HIGH / CRITICAL | Perceived disruption severity |
| `net_daily_shortfall_bpd` | `float` | >= 0 | Uncovered daily crude requirement |
| `estimated_disruption_days` | `int` | >= 1 | Expected disruption duration |
| `current_spr_reserve_barrels` | `float` | >= 0 | Total SPR inventory |
| `minimum_safety_reserve_barrels` | `float` | >= 0, <= current | Reserve that must never be touched |
| `daily_national_demand_bpd` | `float` | > 0 | India's total daily crude consumption |
| `import_delay_days` | `int` | >= 0 | Days before replacement imports arrive |

---

## Output Contract

```json
{
  "scenario_id": "IND_CRISIS_001",
  "recommended_spr_release_bpd": 250000.0,
  "release_duration_days": 15,
  "total_release_barrels": 3750000.0,
  "remaining_spr_barrels": 1250000.0,
  "reserve_utilization_percent": 75.0,
  "uncovered_shortfall_bpd": 0.0,
  "coverage_status": "FULL_COVERAGE",
  "strategy_reasoning": "Risk level is HIGH. The usable SPR reserve is 4,000,000.00 barrels after preserving the minimum safety reserve of 1,000,000.00 barrels. The release duration is 15 days based on the disruption and import delay window. The recommended release is 250,000.00 bpd, leaving 0.00 bpd uncovered. Coverage status is FULL_COVERAGE."
}
```

| Field | Type | Description |
|---|---|---|
| `recommended_spr_release_bpd` | `float` | Daily barrels to release |
| `release_duration_days` | `int` | Number of days to sustain release |
| `total_release_barrels` | `float` | Total barrels consumed from reserve |
| `remaining_spr_barrels` | `float` | Reserve after planned release |
| `reserve_utilization_percent` | `float` | Percentage of reserve consumed |
| `uncovered_shortfall_bpd` | `float` | Shortfall remaining after SPR release |
| `coverage_status` | `string` | FULL_COVERAGE / PARTIAL_COVERAGE / NO_COVERAGE |
| `strategy_reasoning` | `string` | Deterministic explanation of the decision |

---

## Redis Integration

### Stored Keys

```
spr:scenario:{scenario_id}:strategist_output
spr:scenario:{scenario_id}:strategist_state
```

- **Output key** stores the full `StrategistOutput` as serialised JSON.
- **State key** stores a snapshot of the LangGraph state for observability and recovery.

### Event Publishing

After saving the output, the agent publishes a completion event to the channel:

```
strategist.completed
```

Event payload:

```json
{
  "event": "strategist.completed",
  "scenario_id": "IND_CRISIS_001",
  "next_agent": "allocator",
  "redis_key": "spr:scenario:IND_CRISIS_001:strategist_output"
}
```

The `next_agent` field signals to the event bus that the Allocator Agent should be triggered next.

---

## Running the Agent

### Prerequisites

```bash
pip install -r requirements.txt
```

### CLI Execution

```bash
# Run built-in sample scenario
python -m app.strategist.runner

# Run with a JSON input file
python -m app.strategist.runner input.json

# Run with piped JSON
python -m app.strategist.runner < input.json
```

### Programmatic API

```python
from app.strategist.runner import run_strategist

payload = {
    "scenario_id": "IND_CRISIS_001",
    "risk_level": "HIGH",
    # ... other fields
}
output = run_strategist(payload)
print(output.strategy_reasoning)
```

---

## Testing

```bash
# Run all tests
python -m unittest discover -s tests

# Run Strategist-specific tests only
python -m unittest tests.test_strategist_calculations
python -m unittest tests.test_strategist_graph
python -m unittest tests.test_strategist_runner
```

The calculation tests are pure unit tests with no external dependencies. Graph tests use in-memory fake stores and are skipped when LangGraph is not installed. Runner tests verify file, stdin, and sample input loading.

---

## Design Principles

| Principle | Implementation |
|---|---|
| **Deterministic Calculations** | All numerical logic is pure Python with no randomness. No LLM is used for mathematical decisions. |
| **Pydantic Validation** | Every input and output is validated at system boundaries by strongly typed Pydantic models. |
| **LangGraph Workflow** | The agent is modelled as a directed graph with conditional error handling. Each node has a single responsibility. |
| **Event-Driven Architecture** | Completion events are published via Redis Pub/Sub, enabling loose coupling with downstream agents. |
| **Redis Persistence** | Output and state are persisted to Redis for observability, recovery, and consumption by downstream agents. |
| **Protocol Abstraction** | The store interface is defined as a Python Protocol, allowing in-memory stores for testing and Redis stores for production. |
| **Separation of Concerns** | Business logic lives in `calculations.py`, persistence in `redis_store.py`, orchestration in `services.py`, models in `schemas.py`, and workflow in `graph.py`. |
