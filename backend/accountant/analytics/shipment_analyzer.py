"""
=========================================================
Shipment Analyzer
=========================================================

Analyzes tanker movements affected by corridor disruptions.
"""

import pandas as pd


class ShipmentAnalyzer:

    def __init__(self, tankers_df):

        self.tankers = tankers_df

    # -------------------------------------------------
    # Find Affected Tankers
    # -------------------------------------------------

    def find_tankers(self, supplier_result):

        suppliers = supplier_result["affected_suppliers"]

        tankers = self.tankers[

            self.tankers["supplier_company"]

            .isin(suppliers)

        ].copy()

        return tankers

    # -------------------------------------------------
    # Calculate Updated ETA
    # -------------------------------------------------

    def calculate_eta(
        self,
        tankers,
        corridor_result
    ):

        reroute_delay = corridor_result["reroute_delay"]

        tankers["updated_eta"] = (

            tankers["eta_days"]

            +

            tankers["delay_days"]

            +

            reroute_delay

        )

        return tankers

    # -------------------------------------------------
    # Cargo Metrics
    # -------------------------------------------------

    def cargo_metrics(
        self,
        tankers
    ):

        if tankers.empty:

            return {

                "cargo_delayed": 0,

                "average_delay": 0,

                "average_eta": 0

            }

        return {

            "cargo_delayed":

                tankers["cargo_barrels"].sum(),

            "average_delay":

                round(

                    tankers["delay_days"].mean(),

                    2

                ),

            "average_eta":

                round(

                    tankers["updated_eta"].mean(),

                    2

                )

        }

    # -------------------------------------------------
    # Shipment Risk
    # -------------------------------------------------

    def shipment_risk(
        self,
        average_delay
    ):

        if average_delay >= 10:

            return {

                "score":90,

                "level":"CRITICAL"

            }

        elif average_delay >= 7:

            return {

                "score":70,

                "level":"HIGH"

            }

        elif average_delay >= 4:

            return {

                "score":40,

                "level":"MEDIUM"

            }

        return {

            "score":15,

            "level":"LOW"

        }

    # -------------------------------------------------
    # Shipment Status Summary
    # -------------------------------------------------

    def shipment_status(
        self,
        tankers
    ):

        if tankers.empty:

            return {}

        return (

            tankers["shipment_status"]

            .value_counts()

            .to_dict()

        )

    # -------------------------------------------------
    # Main Analysis
    # -------------------------------------------------

    def analyze(

        self,

        supplier_result,

        corridor_result

    ):

        tankers = self.find_tankers(

            supplier_result

        )

        tankers = self.calculate_eta(

            tankers,

            corridor_result

        )

        metrics = self.cargo_metrics(

            tankers

        )

        risk = self.shipment_risk(

            metrics["average_delay"]

        )

        return {
            "affected_tankers":
        len(tankers),

    "refinery_ids":
        tankers["refinery_id"].unique().tolist(),

    "cargo_delayed":
        metrics["cargo_delayed"],

    "average_delay":
        metrics["average_delay"],

    "average_eta":
        metrics["average_eta"],

    "shipment_status":
        self.shipment_status(tankers),

    "shipment_risk":
        risk
           
        }