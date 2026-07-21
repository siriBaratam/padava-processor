"""
=========================================================
Energy Supply Chain Analytics Engine
Configuration File
=========================================================

This file contains all configurable values used by the
Accountant Analytics Engine.

Changing business rules should only require editing this file.
"""

# =========================================================
# Dataset Paths
# =========================================================

DATASET_PATHS = {

    "refineries": "datasets/oil_infrastructure_dataset1.xlsx",

    "inventory": "datasets/inventory_master_dataset2_rebuilt.xlsx",

    "tankers": "datasets/tanker_master_dataset3_rebuilt.xlsx",

    "suppliers": "datasets/supplier_master_dataset4(1).xlsx",

    "corridors": "datasets/corridor_master_dataset5_updated.xlsx"
}


# =========================================================
# Corridor Risk Score Mapping
# =========================================================

CORRIDOR_RISK_SCORE = {

    "Low": 25,

    "Medium": 50,

    "High": 75,

    "Very High": 100
}


# =========================================================
# Shipment Delay Thresholds (Days)
# =========================================================

SHIPMENT_DELAY = {

    "LOW": 2,

    "MEDIUM": 5,

    "HIGH": 10
}


# =========================================================
# Inventory Health Thresholds (Days Remaining)
# =========================================================

INVENTORY_DAYS = {

    "HEALTHY": 20,

    "WARNING": 10,

    "CRITICAL": 5
}


# =========================================================
# Supplier Reliability Thresholds
# =========================================================

SUPPLIER_RELIABILITY = {

    "EXCELLENT": 95,

    "GOOD": 90,

    "AVERAGE": 80
}


# =========================================================
# Overall Risk Score Thresholds
# =========================================================

RISK_LEVELS = {

    "LOW": 30,

    "MEDIUM": 60,

    "HIGH": 80,

    "CRITICAL": 100
}


# =========================================================
# Risk Weightages
# (Must total 100%)
# =========================================================

RISK_WEIGHTS = {

    "corridor": 30,

    "supplier": 20,

    "shipment": 20,

    "inventory": 20,

    "supply_loss": 10,

    "refinery": 20
}


# =========================================================
# Business Rules
# =========================================================

BUSINESS_RULES = {

    # Inventory shortage if gap exceeds this value
    "inventory_gap_days": 5,

    # Recovery time multiplier
    "recovery_multiplier": 1.25,

    # Emergency stock multiplier
    "emergency_stock_factor": 1.20,

    # Insurance premium multiplier
    "insurance_multiplier": 1.10
}


# =========================================================
# Cost Impact Multipliers
# =========================================================

COST_FACTORS = {

    "corridor": 0.40,

    "shipment_delay": 0.20,

    "insurance": 0.20,

    "inventory_gap": 0.20
}


# =========================================================
# Default Values
# =========================================================

DEFAULTS = {

    "unknown": "Unknown",

    "no_data": 0,

    "risk_score": 0,

    "percentage": 0.0
}


# =========================================================
# Required Columns
# Used by Data Loader Validation
# =========================================================

REQUIRED_COLUMNS = {

    "refineries": [

        "refinery_id",
        "refinery_name",
        "capacity_mmpta",
        "connected_port",
        "primary_corridor"

    ],

    "inventory": [

        "inventory_id",
        "refinery_id",
        "current_stock_bbl",
        "daily_consumption_bbl",
        "days_remaining"

    ],

    "tankers": [

        "tanker_id",
        "supplier_company",
        "refinery_id",
        "cargo_barrels",
        "eta_days",
        "delay_days"

    ],

    "suppliers": [

        "supplier_company",
        "supplier_country",
        "primary_corridor",
        "monthly_supply_barrels",
        "reliability_score"

    ],

    "corridors": [

        "corridor_name",
        "risk_level",
        "reroute_delay",
        "insurance_premium_factor"

    ]
}
SUPPORTED_COMMODITIES = [
    "Crude Oil",
    "LNG",
    "Diesel",
    "Petrol",
    "ATF",
    "LPG"
]

SUPPORTED_EVENT_TYPES = [
    "Geopolitical Conflict",
    "Port Closure",
    "Pipeline Failure",
    "Sanctions",
    "Natural Disaster",
    "Shipping Delay",
    "Refinery Shutdown"
]