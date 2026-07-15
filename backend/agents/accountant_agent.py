from typing import Dict, Any, List, Optional
import logging

from models.accountant_models import (
    DisruptionReport,
    Consumption,
    Stock,
    IncomingShip,
    RefineryStatus,
)
from services.calculations import (
    calculate_incoming_usable,
    calculate_survival_days,
    calculate_national_deficit,
    calculate_risk,
    calculate_refinery_shortages,
)

logger = logging.getLogger(__name__)


class AccountantAgent:
    """Accountant Agent that consumes a disruption report and tool interfaces
    to produce an oil balance assessment for the Strategist Agent.
    The class is designed for dependency injection: pass tool instances that
    implement the required methods (see tools/).
    """

    def __init__(
        self,
        consumption_tool,
        stock_tool,
        shipping_tool,
        refinery_tool,
    ) -> None:
        self.consumption_tool = consumption_tool
        self.stock_tool = stock_tool
        self.shipping_tool = shipping_tool
        self.refinery_tool = refinery_tool

    def _parse_report(self, raw: Dict[str, Any]) -> DisruptionReport:
        # Defensive parsing: tolerate missing fields and unknown shapes
        event = raw.get("event") or raw.get("title") or raw.get("headline") or "unknown"
        severity = raw.get("severity") or raw.get("impact") or "unknown"
        expected_delay_days = None
        try:
            expected_delay_days = int(raw.get("expected_delay_days") or raw.get("expected_delay") or 0)
        except Exception:
            expected_delay_days = None
        confidence = None
        try:
            confidence = float(raw.get("confidence", raw.get("confidence_score", 0.0)))
        except Exception:
            confidence = None

        return DisruptionReport(
            raw=raw,
            event=event,
            severity=severity,
            expected_delay_days=expected_delay_days,
            confidence=confidence,
        )

    def assess(self, report_json: Dict[str, Any]) -> Dict[str, Any]:
        report = self._parse_report(report_json)

        # Call tools (they may be remote/DB/APIs - agent doesn't care)
        try:
            consumption: Consumption = self.consumption_tool.get_consumption()
        except Exception as e:
            logger.exception("consumption tool failed")
            consumption = Consumption(daily_consumption=0.0)

        try:
            stock: Stock = self.stock_tool.get_current_stock()
        except Exception:
            logger.exception("stock tool failed")
            stock = Stock(strategic_reserve=0.0, commercial_stock=0.0, total_stock=0.0)

        try:
            ships: List[IncomingShip] = self.shipping_tool.get_incoming_ships()
        except Exception:
            logger.exception("shipping tool failed")
            ships = []

        try:
            refineries: List[RefineryStatus] = self.refinery_tool.get_refinery_status()
        except Exception:
            logger.exception("refinery tool failed")
            refineries = []

        # Deterministic calculations
        incoming_usable = calculate_incoming_usable(ships)
        survival_days = calculate_survival_days(stock.total_stock, incoming_usable, consumption.daily_consumption)
        national_deficit = calculate_national_deficit(stock.total_stock, incoming_usable, consumption.daily_consumption)
        refinery_assessment = calculate_refinery_shortages(refineries)
        risk_level, risk_confidence = calculate_risk(survival_days, report.severity, report.confidence)

        # Compose output following the specified schema
        output = {
            "oil_balance": {
                "current_stock": stock.total_stock,
                "incoming_supply": incoming_usable,
                "daily_consumption": consumption.daily_consumption,
                "available_supply": stock.total_stock + incoming_usable,
                "national_deficit": national_deficit,
                "survival_days": survival_days,
            },
            "refinery_assessment": [
                {"name": r["name"], "status": r["status"], "reason": r["reason"]}
                for r in refinery_assessment
            ],
            "risk_assessment": {"risk": risk_level, "confidence": risk_confidence},
            "news_context": {
                "event": report.event,
                "severity": report.severity,
                "expected_delay_days": report.expected_delay_days,
            },
            "summary": self._build_summary(report, stock, consumption, incoming_usable, survival_days, risk_level),
        }

        return output

    def _build_summary(
        self,
        report: DisruptionReport,
        stock: Stock,
        consumption: Consumption,
        incoming_usable: float,
        survival_days: float,
        risk_level: str,
    ) -> str:
        # Create a concise deterministic summary. Keep this short — for Strategist.
        parts: List[str] = []
        parts.append(f"Event: {report.event} (severity: {report.severity})")
        parts.append(f"Current total stock: {stock.total_stock:.1f}")
        parts.append(f"Daily consumption: {consumption.daily_consumption:.1f}")
        parts.append(f"Incoming usable supply (identified): {incoming_usable:.1f}")
        parts.append(f"Estimated survival days: {survival_days:.1f} ({risk_level})")
        return " | ".join(parts)


if __name__ == "__main__":
    print("AccountantAgent module. Import and inject tools in production.")


class AccountantAgnoWrapper:
    """A thin wrapper to mimic an Agno agent execution interface.
    It exposes `run(disruption_report)` which the orchestrator/Agno runtime
    can call. The wrapper uses an internal AccountantAgent instance and a
    tool invoker to perform tool calls through a single entrypoint.
    """

    def __init__(self, accountant: AccountantAgent, tool_invoker) -> None:
        self._accountant = accountant
        self._invoker = tool_invoker

    def run(self, disruption_report: dict) -> dict:
        """Execute the Accountant flow. This method is the Agno entrypoint.
        It will call tools via the provided `tool_invoker` which abstracts
        the underlying tool implementations.
        """
        # Replace direct tool attributes of accountant with proxied callables
        # that use the invoker. This keeps the accountant logic unchanged while
        # ensuring tools are invoked through the Agno tool invoker.
        class ProxyTool:
            def __init__(self, invoker, name):
                self._invoker = invoker
                self._name = name

            def __getattr__(self, item):
                # only support direct method names used by accountant
                def caller(*args, **kwargs):
                    return self._invoker.call_tool(self._name, item, *args, **kwargs)

                return caller

        # Inject proxied tools
        self._accountant.consumption_tool = ProxyTool(self._invoker, "consumption")
        self._accountant.stock_tool = ProxyTool(self._invoker, "stock")
        self._accountant.shipping_tool = ProxyTool(self._invoker, "shipping")
        self._accountant.refinery_tool = ProxyTool(self._invoker, "refinery")

        # Run assessment
        return self._accountant.assess(disruption_report)

