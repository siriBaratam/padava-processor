"""
=========================================================
Inventory Analyzer
=========================================================

Analyzes refinery inventory after shipment disruptions.
"""

import pandas as pd


class InventoryAnalyzer:

    def __init__(self, inventory_df):

        self.inventory = inventory_df

    # -------------------------------------------------
    # Find Affected Inventory
    # -------------------------------------------------

    def find_inventory(self, shipment_result):

        refinery_ids = shipment_result["refinery_ids"]

        inventory = self.inventory[

            self.inventory["refinery_id"]

            .isin(refinery_ids)

        ].copy()

        return inventory

    # -------------------------------------------------
    # Inventory Health Score
    # -------------------------------------------------

    def calculate_health_score(self, row):

        utilization = (

            row["current_stock_bbl"]

            /

            row["tank_capacity_bbl"]

        ) * 100

        if utilization >= 80:

            return 100

        elif utilization >= 60:

            return 80

        elif utilization >= 40:

            return 60

        elif utilization >= 20:

            return 40

        return 20

    # -------------------------------------------------
    # Inventory Status
    # -------------------------------------------------

    def inventory_status(self, days):

        if days >= 20:

            return "HEALTHY"

        elif days >= 10:

            return "WARNING"

        elif days >= 5:

            return "LOW"

        return "CRITICAL"

    # -------------------------------------------------
    # Inventory Gap
    # -------------------------------------------------

    def calculate_gap(

        self,

        inventory,

        shipment_result

    ):

        eta = shipment_result["average_eta"]

        inventory["inventory_gap_days"] = (

            eta

            -

            inventory["days_remaining"]

        )

        inventory["inventory_gap_days"] = (

            inventory["inventory_gap_days"]

            .clip(lower=0)

        )

        return inventory

    # -------------------------------------------------
    # Calculate Metrics
    # -------------------------------------------------

    def metrics(self, inventory):

        if inventory.empty:

            return {

                "average_days_remaining":0,

                "average_gap":0,

                "critical_refineries":0

            }

        critical = (

            inventory["days_remaining"]

            < 5

        ).sum()

        return {

            "average_days_remaining":

                round(

                    inventory["days_remaining"]

                    .mean(),

                    2

                ),

            "average_gap":

                round(

                    inventory["inventory_gap_days"]

                    .mean(),

                    2

                ),

            "critical_refineries":

                int(critical)

        }

    # -------------------------------------------------
    # Inventory Risk
    # -------------------------------------------------

    def inventory_risk(self, gap):

        if gap >= 10:

            return {

                "score":90,

                "level":"CRITICAL"

            }

        elif gap >= 7:

            return {

                "score":70,

                "level":"HIGH"

            }

        elif gap >= 3:

            return {

                "score":40,

                "level":"MEDIUM"

            }

        return {

            "score":10,

            "level":"LOW"

        }

    # -------------------------------------------------
    # Main Analysis
    # -------------------------------------------------

    def analyze(

        self,

        shipment_result

    ):

        inventory = self.find_inventory(

            shipment_result

        )

        inventory = self.calculate_gap(

            inventory,

            shipment_result

        )

        inventory["health_score"] = inventory.apply(

            self.calculate_health_score,

            axis=1

        )

        inventory["inventory_status"] = inventory[

            "days_remaining"

        ].apply(

            self.inventory_status

        )

        metrics = self.metrics(

            inventory

        )

        risk = self.inventory_risk(

            metrics["average_gap"]

        )
        return {

    "affected_refinery_ids":
        inventory["refinery_id"].unique().tolist(),

    "average_days_remaining":
        metrics["average_days_remaining"],

    "inventory_gap_days":
        metrics["average_gap"],

    "critical_refineries":
        metrics["critical_refineries"],

    "inventory_risk":
        risk
        }