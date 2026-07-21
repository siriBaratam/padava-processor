"""
=========================================================
Business Metrics
=========================================================

Calculates operational and business KPIs from all analyzer
outputs.
"""

class BusinessMetrics:

    def __init__(self):
        pass

    # -------------------------------------------------
    # Supply Loss (%)
    # -------------------------------------------------

    def supply_loss(
        self,
        supplier_result,
        refinery_result
    ):

        total_supply = supplier_result["monthly_supply_barrels"]

        affected_capacity = refinery_result["affected_capacity_mmpta"]

        if total_supply == 0:
            return 0

        loss = min(

            (affected_capacity * 1000000)

            /

            total_supply

            * 100,

            100

        )

        return round(loss, 2)

    # -------------------------------------------------
    # Estimated Transportation Cost Increase (%)
    # -------------------------------------------------

    def transportation_cost(
        self,
        corridor_result
    ):

        return corridor_result["reroute_fuel_cost_percent"]

    # -------------------------------------------------
    # Insurance Cost Multiplier
    # -------------------------------------------------

    def insurance_multiplier(
        self,
        corridor_result
    ):

        return corridor_result["insurance_premium_factor"]

    # -------------------------------------------------
    # Recovery Time (Days)
    # -------------------------------------------------

    def recovery_days(
        self,
        corridor_result
    ):

        return corridor_result["expected_recovery_days"]

    # -------------------------------------------------
    # Demand Coverage (%)
    # -------------------------------------------------

    def demand_coverage(
        self,
        inventory_result
    ):

        avg_days = inventory_result["average_days_remaining"]

        coverage = min(

            (avg_days / 30) * 100,

            100

        )

        return round(coverage, 2)

    # -------------------------------------------------
    # Capacity Utilization (%)
    # -------------------------------------------------

    def capacity_utilization(
        self,
        refinery_result
    ):

        capacity = refinery_result["affected_capacity_mmpta"]

        utilization = min(

            (capacity / 80) * 100,

            100

        )

        return round(utilization, 2)

    # -------------------------------------------------
    # Business Impact Score (0-100)
    # -------------------------------------------------

    def impact_score(

        self,

        corridor_result,

        supplier_result,

        shipment_result,

        inventory_result,

        refinery_result

    ):

        score = (

            corridor_result["risk_score"] * 0.25 +

            supplier_result["supplier_risk"]["score"] * 0.15 +

            shipment_result["shipment_risk"]["score"] * 0.20 +

            inventory_result["inventory_risk"]["score"] * 0.20 +

            refinery_result["capacity_risk"]["score"] * 0.20

        )

        return round(score, 2)

    # -------------------------------------------------
    # Main Function
    # -------------------------------------------------

    def calculate(

        self,

        corridor_result,

        supplier_result,

        shipment_result,

        inventory_result,

        refinery_result

    ):

        metrics = {

            "supply_loss_percent":

                self.supply_loss(

                    supplier_result,

                    refinery_result

                ),

            "transportation_cost_increase_percent":

                self.transportation_cost(

                    corridor_result

                ),

            "insurance_multiplier":

                self.insurance_multiplier(

                    corridor_result

                ),

            "expected_recovery_days":

                self.recovery_days(

                    corridor_result

                ),

            "demand_coverage_percent":

                self.demand_coverage(

                    inventory_result

                ),

            "capacity_utilization_percent":

                self.capacity_utilization(

                    refinery_result

                ),

            "business_impact_score":

                self.impact_score(

                    corridor_result,

                    supplier_result,

                    shipment_result,

                    inventory_result,

                    refinery_result

                )

        }

        return metrics