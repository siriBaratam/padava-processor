"""
=========================================================
Corridor Analyzer
=========================================================

Analyzes the affected corridor based on Scout output.

Responsibilities
----------------
1. Locate corridor
2. Determine corridor risk
3. Find alternate route
4. Calculate reroute delay
5. Determine insurance multiplier
6. Return structured corridor object
"""

from ..config import CORRIDOR_RISK_SCORE, DEFAULTS

class CorridorAnalyzer:

    def __init__(self, corridor_df):

        self.corridors = corridor_df

    # -------------------------------------------------
    # Find Corridor
    # -------------------------------------------------

    def find_corridor(self, corridor_name):

        result = self.corridors[
            self.corridors["corridor_name"]
            .str.lower()
            ==
            corridor_name.lower()
        ]

        if result.empty:
            return {
        "corridor_name": corridor_name,
        "risk_level": "Low",
        "risk_score": 0,
        "normal_transit_days": 0,
        "reroute_delay": 0,
        "alternate_route": "N/A",
        "insurance_premium_factor": 1.0,
        "strategic_score": 0,
        "major_export_regions": "N/A",
        "affected_ports": "N/A",
        "affected_refineries": "N/A",
        "recommended_action": "Continue monitoring",
        "reroute_fuel_cost_percent": 0,
        "reroute_co2_percent": 0,
        "expected_recovery_days": 0,
        "block_probability": 0
        }

        return result.iloc[0]

    # -------------------------------------------------
    # Convert Risk Level -> Score
    # -------------------------------------------------

    def calculate_risk_score(
        self,
        risk_level
    ):

        return CORRIDOR_RISK_SCORE.get(

            risk_level,

            0

        )

    # -------------------------------------------------
    # Analyze Corridor
    # -------------------------------------------------

    def analyze(
        self,
        corridor_name,
    ):
          if corridor_name.lower() == "unknown":
              return {
            "corridor_name": "Unknown",
            "risk_level": "Low",
            "risk_score": 0,
            "normal_transit_days": 0,
            "reroute_delay": 0,
            "alternate_route": "N/A",
            "insurance_premium_factor": 1.0,
            "strategic_score": 0,
            "major_export_regions": "N/A",
            "affected_ports": "N/A",
            "affected_refineries": "N/A",
            "recommended_action": "Continue monitoring",
            "reroute_fuel_cost_percent": 0,
            "reroute_co2_percent": 0,
            "expected_recovery_days": 0,
            "block_probability": 0
        }
          corridor = self.find_corridor(
            corridor_name
        )
          return {

            "corridor_name":
                corridor["corridor_name"],

            "risk_level":
                corridor["risk_level"],

            "risk_score":
                self.calculate_risk_score(
                    corridor["risk_level"]
                ),

            "normal_transit_days":
                corridor["normal_transit_days"],

            "reroute_delay":
                corridor["reroute_delay"],

            "alternate_route":
                corridor["alternate_route"],

            "insurance_premium_factor":
                corridor["insurance_premium_factor"],

            "strategic_score":
                corridor["strategic_importance_score"],

            "major_export_regions":
                corridor["major_exporting_regions"],

            "affected_ports":
                corridor["affected_indian_ports"],

            "affected_refineries":
                corridor["affected_refineries"],

            "recommended_action":
                corridor["recommended_action"],
            "reroute_fuel_cost_percent":
            corridor["reroute_fuel_cost_percent"],
            "reroute_co2_percent":
            corridor["reroute_co2_percent"],
            "expected_recovery_days":
            corridor["expected_recovery_days"],
            "block_probability":
            corridor["block_probability"],

        }

    # -------------------------------------------------
    # Print
    # -------------------------------------------------

    def display(
        self,
        corridor_info
    ):

        print("\n========== Corridor Analysis ==========\n")

        for key, value in corridor_info.items():

            print(f"{key:25}: {value}")

        print()