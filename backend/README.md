Accountant Agent (M2) for Agno-based multi-agent system

Structure

- agents/accountant_agent.py - main agent class
- tools/* - tool interfaces and mock implementations
- services/calculations.py - deterministic calculation functions
- models/accountant_models.py - Pydantic models

Usage

Inject concrete tool implementations into `AccountantAgent` and call `assess(report_json)`.

The agent returns a structured JSON following the agreed schema for the Strategist Agent.
