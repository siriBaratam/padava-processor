"""
=========================================================
ACCOUNTANT AGENT
=========================================================

Entry point for the Accountant Agent.

Pipeline

Scout
   ↓
Accountant
   ↓
Strategist
"""

from .data_loader import DataLoader
from .analytics.analytics_engine import AnalyticsEngine
from .report.report_generator import ReportGenerator


class Accountant:

    def __init__(self):

        # --------------------------------------------
        # Load datasets
        # --------------------------------------------

        loader = DataLoader()

        loader.load_all()

        # Dataset references

        self.refineries = loader.get_dataset("refineries")

        self.inventory = loader.get_dataset("inventory")

        self.tankers = loader.get_dataset("tankers")

        self.suppliers = loader.get_dataset("suppliers")

        self.corridors = loader.get_dataset("corridors")

        # --------------------------------------------
        # Initialize Engine
        # --------------------------------------------

        self.engine = AnalyticsEngine(

            corridors_df=self.corridors,

            suppliers_df=self.suppliers,

            tankers_df=self.tankers,

            inventory_df=self.inventory,

            refineries_df=self.refineries

        )

        self.report_generator = ReportGenerator()

    # -------------------------------------------------
    # Analyze One Event
    # -------------------------------------------------

    def analyze(self, scout_event):

        analysis = self.engine.analyze(

            scout_event

        )

        report = self.report_generator.generate(

            analysis

        )

        return report

    # -------------------------------------------------
    # Analyze Multiple Events
    # -------------------------------------------------

    def analyze_batch(self, scout_events):

        reports = []

        for event in scout_events:

            reports.append(

                self.analyze(event)

            )

        return reports


# =====================================================
# Example
# =====================================================

if __name__ == "__main__":

    accountant = Accountant()

    scout_event = {

        "event": "Missile Attack",

        "corridor": "Strait of Hormuz"

    }

    report = accountant.analyze(

        scout_event

    )

    from pprint import pprint

    pprint(report)

if __name__ == "__main__":
    accountant = Accountant()

    scout_event = {
        "event": "Missile Attack",
        "corridor": "Strait of Hormuz"
    }

    report = accountant.analyze(scout_event)

    from pprint import pprint
    pprint(report)


    