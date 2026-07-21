"""
=========================================================
Supplier Analyzer
=========================================================

Analyzes suppliers affected by a corridor disruption.
"""

import pandas as pd


class SupplierAnalyzer:

    def __init__(self, suppliers_df):

        self.suppliers = suppliers_df

    # -------------------------------------------------
    # Find Suppliers
    # -------------------------------------------------

    def find_suppliers(self, corridor_name):

        df = self.suppliers[

            self.suppliers["primary_corridor"]
            .str.contains(
                corridor_name,
                case=False,
                na=False
            )

        ].copy()

        return df

    # -------------------------------------------------
    # Calculate Supplier Metrics
    # -------------------------------------------------

    def calculate_metrics(self, suppliers):

        if suppliers.empty:

            return {

                "supplier_count": 0,

                "monthly_supply_barrels": 0,

                "average_reliability": 0,

                "average_lead_time": 0

            }

        return {

            "supplier_count":

                len(suppliers),

            "monthly_supply_barrels":

                suppliers[
                    "monthly_supply_barrels"
                ].sum(),

            "average_reliability":

                round(

                    suppliers[
                        "reliability_score"
                    ].mean(),

                    2

                ),

            "average_lead_time":

                round(

                    suppliers[
                        "average_lead_time_days"
                    ].mean(),

                    2

                )

        }

    # -------------------------------------------------
    # Find Alternate Suppliers
    # -------------------------------------------------

    def alternate_suppliers(
        self,
        suppliers
    ):

        alternatives = []

        if "alternate_supplier" not in suppliers.columns:

            return alternatives

        for supplier in suppliers["alternate_supplier"]:

            if pd.notna(supplier):

                alternatives.append(supplier)

        return sorted(list(set(alternatives)))

    # -------------------------------------------------
    # Supplier Risk
    # -------------------------------------------------

    def supplier_risk(
        self,
        reliability
    ):

        if reliability >= 95:

            return {

                "score": 10,

                "level": "LOW"

            }

        elif reliability >= 90:

            return {

                "score": 30,

                "level": "MEDIUM"

            }

        elif reliability >= 80:

            return {

                "score": 60,

                "level": "HIGH"

            }

        else:

            return {

                "score": 90,

                "level": "CRITICAL"

            }

    # -------------------------------------------------
    # Main Analysis
    # -------------------------------------------------

    def analyze(
        self,
        corridor_result
    ):

        corridor_name = corridor_result[

            "corridor_name"

        ]

        suppliers = self.find_suppliers(

            corridor_name

        )

        metrics = self.calculate_metrics(

            suppliers

        )

        risk = self.supplier_risk(

            metrics[
                "average_reliability"
            ]

        )

        return {

            "affected_suppliers":

                suppliers[
                    "supplier_company"
                ].tolist(),

            "supplier_countries":

                suppliers[
                    "supplier_country"
                ].tolist(),

            "alternate_suppliers":

                self.alternate_suppliers(
                    suppliers
                ),

            "monthly_supply_barrels":

                metrics[
                    "monthly_supply_barrels"
                ],

            "supplier_count":

                metrics[
                    "supplier_count"
                ],

            "average_reliability":

                metrics[
                    "average_reliability"
                ],

            "average_lead_time":

                metrics[
                    "average_lead_time"
                ],

            "supplier_risk":

                risk

        }