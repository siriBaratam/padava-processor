from typing import Protocol, List
from models.accountant_models import RefineryStatus


class RefineryToolInterface(Protocol):
    def get_refinery_status(self) -> List[RefineryStatus]: ...


class MockRefineryTool:
    def __init__(self, refineries=None):
        self._refineries = refineries or [
            {"refinery": "Refinery-1", "supported_crude": ["Brent"], "daily_capacity": 200_000.0, "current_inventory": 1_000_000.0, "status": "operational"},
            {"refinery": "Refinery-2", "supported_crude": ["Dubai"], "daily_capacity": 150_000.0, "current_inventory": 200_000.0, "status": "reduced"},
        ]

    def get_refinery_status(self):
        return [RefineryStatus(**r) for r in self._refineries]
