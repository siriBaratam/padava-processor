"""
=========================================================
Refinery Analyzer
=========================================================

Analyzes refineries affected by inventory shortages.
"""

import pandas as pd


class RefineryAnalyzer:

    def __init__(self, refinery_df):

        self.refineries = refinery_df

    # -------------------------------------------------
    # Find Refineries
    # -------------------------------------------------

    def find_refineries(self, inventory_result):

        refinery_ids = inventory_result["affected_refinery_ids"]

        refineries = self.refineries[

            self.refineries["refinery_id"]

            .isin(refinery_ids)

        ].copy()

        return refineries

    # -------------------------------------------------
    # Capacity Metrics
    # -------------------------------------------------

    def capacity_metrics(self, refineries):

        if refineries.empty:

            return {

                "affected_capacity":0,

                "average_capacity":0,

                "refinery_count":0

            }

        return {

            "affected_capacity":

                round(

                    refineries["capacity_mmpta"]

                    .sum(),

                    2

                ),

            "average_capacity":

                round(

                    refineries["capacity_mmpta"]

                    .mean(),

                    2

                ),

            "refinery_count":

                len(refineries)

        }

    # -------------------------------------------------
    # State Distribution
    # -------------------------------------------------

    def state_distribution(self, refineries):

        if refineries.empty:

            return {}

        return (

            refineries["state"]

            .value_counts()

            .to_dict()

        )

    # -------------------------------------------------
    # Company Distribution
    # -------------------------------------------------

    def company_distribution(self, refineries):

        if refineries.empty:

            return {}

        return (

            refineries["company"]

            .value_counts()

            .to_dict()

        )

    # -------------------------------------------------
    # Connected Ports
    # -------------------------------------------------

    def connected_ports(self, refineries):

        if refineries.empty:

            return []

        return sorted(

            refineries["connected_port"]

            .dropna()

            .unique()

            .tolist()

        )

    # -------------------------------------------------
    # Capacity Risk
    # -------------------------------------------------

    def capacity_risk(self, capacity):

        if capacity >= 60:

            return {

                "score":95,

                "level":"CRITICAL"

            }

        elif capacity >= 40:

            return {

                "score":75,

                "level":"HIGH"

            }

        elif capacity >= 20:

            return {

                "score":45,

                "level":"MEDIUM"

            }

        return {

            "score":20,

            "level":"LOW"

        }

    # -------------------------------------------------
    # Main Analysis
    # -------------------------------------------------

    def analyze(self, inventory_result):

        refineries = self.find_refineries(

            inventory_result

        )

        metrics = self.capacity_metrics(

            refineries

        )

        risk = self.capacity_risk(

            metrics["affected_capacity"]

        )
        return {

    "affected_capacity_mmpta":
        metrics["affected_capacity"],

    "average_capacity_mmpta":
        metrics["average_capacity"],

    "refinery_count":
        metrics["refinery_count"],

    "connected_ports":
        self.connected_ports(refineries),

    "capacity_risk":
        risk

}