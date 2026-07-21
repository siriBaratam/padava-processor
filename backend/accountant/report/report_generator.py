"""
=========================================================
Report Generator
=========================================================

Formats Accountant analysis into a clean report that is
consumed by the Strategist agent.
"""

from datetime import datetime


class ReportGenerator:

    def __init__(self):
        pass

    # -------------------------------------------------
    # Executive Summary
    # -------------------------------------------------

    def executive_summary(
        self,
        event,
        risk,
        metrics
    ):

      return {
    "headline": event["Headline"],
    "event_type": event["Event Type"],
    "classification": event["Classification"],
    "severity": event["Severity"],
    "country": event["Country"],
    "commodity": event["Commodity"],
    "corridor": event["Corridor at Risk"],
    "summary": event["Summary"]
}

    # -------------------------------------------------
    # Operational Summary
    # -------------------------------------------------

    def operational_summary(

        self,

        corridor,

        supplier,

        shipment,

        inventory,

        refinery

    ):

        return {

            "corridor":

                corridor["corridor_name"],

            "affected_suppliers":

                supplier["supplier_count"],

            "affected_tankers":
                    shipment["affected_tankers"]

               ,

            "affected_refineries":

                refinery["refinery_count"],

            "critical_refineries":

                inventory["critical_refineries"]

        }

    # -------------------------------------------------
    # Business Summary
    # -------------------------------------------------

    def business_summary(

        self,

        metrics

    ):

        return {

            "supply_loss_percent":

                metrics["supply_loss_percent"],

            "transportation_cost_increase":

                metrics[

                    "transportation_cost_increase_percent"

                ],

            "insurance_multiplier":

                metrics["insurance_multiplier"],

            "expected_recovery_days":

                metrics["expected_recovery_days"],

            "demand_coverage":

                metrics["demand_coverage_percent"]

        }

    # -------------------------------------------------
    # Generate Final Report
    # -------------------------------------------------

    def generate(self, analysis):

        report = {

            "generated_at":

                datetime.utcnow().isoformat(),

            "executive_summary":

                self.executive_summary(

                    analysis["event"],

                    analysis["enterprise_risk"],

                    analysis["business_metrics"]

                ),

            "operational_summary":

                self.operational_summary(

                    analysis["corridor_analysis"],

                    analysis["supplier_analysis"],

                    analysis["shipment_analysis"],

                    analysis["inventory_analysis"],

                    analysis["refinery_analysis"]

                ),

            "business_summary":

                self.business_summary(

                    analysis["business_metrics"]

                ),

            "risk_analysis":

                analysis["enterprise_risk"],

            "recommendations":

                analysis["enterprise_risk"][

                    "recommendations"

                ],

            # Strategist consumes these directly
            "strategist_input": {
                "event": analysis["event"],
                "corridor": analysis["corridor_analysis"],
                "suppliers": analysis["supplier_analysis"],
                "shipments": analysis["shipment_analysis"],
                "inventory": analysis["inventory_analysis"],
                "refineries": analysis["refinery_analysis"],
                "business": analysis["business_metrics"],
                "risk": analysis["enterprise_risk"]
            }

        }

        return report