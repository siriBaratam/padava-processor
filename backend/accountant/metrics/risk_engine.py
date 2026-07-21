"""
=========================================================
Risk Engine
=========================================================

Combines all analyzer outputs into a single enterprise
risk assessment.
"""

from ..config import RISK_WEIGHTS

class RiskEngine:

    def __init__(self):
        self.weights = RISK_WEIGHTS

    # -------------------------------------------------
    # Weighted Risk Score
    # -------------------------------------------------

    def overall_score(
        self,
        corridor_result,
        supplier_result,
        shipment_result,
        inventory_result,
        refinery_result
    ):

        score = (

            corridor_result["risk_score"] *
            self.weights["corridor"]

            +

            supplier_result["supplier_risk"]["score"] *
            self.weights["supplier"]

            +

            shipment_result["shipment_risk"]["score"] *
            self.weights["shipment"]

            +

            inventory_result["inventory_risk"]["score"] *
            self.weights["inventory"]

            +

            refinery_result["capacity_risk"]["score"] *
            self.weights["refinery"]

        )/100

        return round(score, 2)

    # -------------------------------------------------
    # Risk Level
    # -------------------------------------------------

    def risk_level(self, score):

        if score >= 85:
            return "CRITICAL"

        elif score >= 70:
            return "HIGH"

        elif score >= 40:
            return "MEDIUM"

        return "LOW"

    # -------------------------------------------------
    # Risk Color
    # -------------------------------------------------

    def risk_color(self, level):

        colors = {

            "LOW": "GREEN",

            "MEDIUM": "YELLOW",

            "HIGH": "ORANGE",

            "CRITICAL": "RED"

        }

        return colors[level]

    # -------------------------------------------------
    # Main Contributors
    # -------------------------------------------------

    def contributors(

        self,

        corridor_result,

        supplier_result,

        shipment_result,

        inventory_result,

        refinery_result

    ):

        risks = {

            "Corridor":
                corridor_result["risk_score"],

            "Supplier":
                supplier_result["supplier_risk"]["score"],

            "Shipment":
                shipment_result["shipment_risk"]["score"],

            "Inventory":
                inventory_result["inventory_risk"]["score"],

            "Refinery":
                refinery_result["capacity_risk"]["score"]

        }

        risks = dict(

            sorted(

                risks.items(),

                key=lambda x: x[1],

                reverse=True

            )

        )

        return risks

    # -------------------------------------------------
    # Recommendations
    # -------------------------------------------------

    def recommendations(

        self,

        level

    ):

        if level == "CRITICAL":

            return [

                "Activate alternate shipping routes",

                "Use strategic crude reserves",

                "Prioritize critical refinery operations",

                "Increase inventory replenishment",

                "Escalate to executive response team"

            ]

        elif level == "HIGH":

            return [

                "Monitor supplier performance",

                "Increase safety stock",

                "Review logistics schedules",

                "Prepare alternate procurement"

            ]

        elif level == "MEDIUM":

            return [

                "Continue monitoring",

                "Review inventory weekly"

            ]

        return [

            "Normal operations"

        ]

    # -------------------------------------------------
    # Main Analysis
    # -------------------------------------------------

    def analyze(

        self,

        corridor_result,

        supplier_result,

        shipment_result,

        inventory_result,

        refinery_result

    ):

        score = self.overall_score(

            corridor_result,

            supplier_result,

            shipment_result,

            inventory_result,

            refinery_result

        )

        level = self.risk_level(score)

        return {

            "overall_risk_score":

                score,

            "overall_risk_level":

                level,

            "risk_color":

                self.risk_color(level),

            "risk_contributors":

                self.contributors(

                    corridor_result,

                    supplier_result,

                    shipment_result,

                    inventory_result,

                    refinery_result

                ),

            "recommendations":

                self.recommendations(level)

        }