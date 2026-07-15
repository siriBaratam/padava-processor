# SPR Command Platform - Agent Prototypes

This repository currently implements the Strategist and Allocator Agent prototypes.

Pipeline context:

```text
Scout -> Accountant -> Strategist -> Allocator -> Dealmaker -> Navigator -> Translator
```

Prototype data flow:

```text
Accountant → Strategist → Redis → Allocator → Redis → Dealmaker
```

The Strategist Agent consumes the Accountant Agent's net daily shortfall and decides how much oil to release from the Strategic Petroleum Reserve.

The Allocator Agent consumes the Strategist output and distributes available oil supply across Indian states.

Neither prototype performs procurement, maritime routing, or dashboard translation.

## Structure

```text
app/
  shared/
    redis_client.py
  strategist/
    config.py
    schemas.py
    state.py
    calculations.py
    services.py
    redis_store.py
    graph.py
    runner.py
  allocator/
    config.py
    schemas.py
    state.py
    calculations.py
    services.py
    redis_store.py
    graph.py
    runner.py
tests/
```

## Redis Keys

Strategist output:

```text
spr:scenario:{scenario_id}:strategist_output
```

Strategist state:

```text
spr:scenario:{scenario_id}:strategist_state
```

Allocator state demand profiles:

```text
spr:scenario:{scenario_id}:state_demand_profiles
```

Allocator output:

```text
spr:scenario:{scenario_id}:allocator_output
```

Allocator state:

```text
spr:scenario:{scenario_id}:allocator_state
```

Completion event channels:

```text
strategist.completed
allocator.completed
```

The Strategist Agent publishes `strategist.completed` after writing its scenario output to Redis.

The Allocator Agent publishes `allocator.completed` after writing state-wise allocation output to Redis.

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run with JSON from stdin:

```bash
python -m app.strategist.runner < sample_payload.json
```

Run with a JSON file:

```bash
python -m app.strategist.runner sample_payload.json
```

Run the built-in sample scenario:

```bash
python -m app.strategist.runner
```

Run the Allocator built-in sample scenario:

```bash
python -m app.allocator.runner
```

Run Allocator with JSON from stdin:

```bash
python -m app.allocator.runner < allocator_payload.json
```

Run Allocator with a JSON file:

```bash
python -m app.allocator.runner allocator_payload.json
```

## Test

```bash
python -m unittest discover -s tests
```
