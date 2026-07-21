"""
=========================================================
Analytics Engine
=========================================================

Executes all analyzers and produces the complete
Accountant output.
"""
from .corridor_analyzer import CorridorAnalyzer
from .supplier_analyzer import SupplierAnalyzer
from .shipment_analyzer import ShipmentAnalyzer
from .inventory_analyzer import InventoryAnalyzer
from .refinery_analyzer import RefineryAnalyzer

from ..metrics.business_metrics import BusinessMetrics
from ..metrics.risk_engine import RiskEngine


class AnalyticsEngine:

    def __init__(

        self,

        corridors_df,

        suppliers_df,

        tankers_df,

        inventory_df,

        refineries_df

    ):

        self.corridor_analyzer = CorridorAnalyzer(corridors_df)

        self.supplier_analyzer = SupplierAnalyzer(suppliers_df)

        self.shipment_analyzer = ShipmentAnalyzer(tankers_df)

        self.inventory_analyzer = InventoryAnalyzer(inventory_df)

        self.refinery_analyzer = RefineryAnalyzer(refineries_df)

        self.business_metrics = BusinessMetrics()

        self.risk_engine = RiskEngine()

    # -------------------------------------------------
    # Execute Complete Pipeline
    # -------------------------------------------------

    def analyze(

        self,

        scout_event

    ):

        # --------------------------------------------
        # Step 1
        # Corridor
        # --------------------------------------------

        corridor_result = self.corridor_analyzer.analyze(

            scout_event["Corridor at Risk"]

        )

        # --------------------------------------------
        # Step 2
        # Suppliers
        # --------------------------------------------

        supplier_result = self.supplier_analyzer.analyze(

            corridor_result

        )

        # --------------------------------------------
        # Step 3
        # Shipments
        # --------------------------------------------

        shipment_result = self.shipment_analyzer.analyze(

            supplier_result,

            corridor_result

        )

        # --------------------------------------------
        # Step 4
        # Inventory
        # --------------------------------------------

        inventory_result = self.inventory_analyzer.analyze(

            shipment_result

        )

        # --------------------------------------------
        # Step 5
        # Refineries
        # --------------------------------------------

        refinery_result = self.refinery_analyzer.analyze(

            inventory_result

        )

        # --------------------------------------------
        # Step 6
        # Business Metrics
        # --------------------------------------------

        business_result = self.business_metrics.calculate(

            corridor_result,

            supplier_result,

            shipment_result,

            inventory_result,

            refinery_result

        )

        # --------------------------------------------
        # Step 7
        # Enterprise Risk
        # --------------------------------------------

        risk_result = self.risk_engine.analyze(

            corridor_result,

            supplier_result,

            shipment_result,

            inventory_result,

            refinery_result

        )

        # --------------------------------------------
        # Final Output
        # --------------------------------------------

        return {

            "event": scout_event,

            "corridor_analysis": corridor_result,

            "supplier_analysis": supplier_result,

            "shipment_analysis": shipment_result,

            "inventory_analysis": inventory_result,

            "refinery_analysis": refinery_result,

            "business_metrics": business_result,

            "enterprise_risk": risk_result

        }

    # -------------------------------------------------
    # Execute Multiple Events
    # -------------------------------------------------

    def analyze_batch(

        self,

        scout_events

    ):

        results = []

        for event in scout_events:

            results.append(

                self.analyze(event)

            )

        return results