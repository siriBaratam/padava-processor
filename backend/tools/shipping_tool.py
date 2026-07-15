from typing import Protocol, List
from models.accountant_models import IncomingShip


class ShippingToolInterface(Protocol):
    def get_incoming_ships(self) -> List[IncomingShip]: ...


class MockShippingTool:
    def __init__(self, ships=None):
        self._ships = ships or [
            {"name": "Vessel-A", "supplier": "Supplier-X", "eta": "2026-07-20", "cargo_quantity": 2_000_000.0, "delay": False, "status": "on-time"},
            {"name": "Vessel-B", "supplier": "Supplier-Y", "eta": "2026-07-25", "cargo_quantity": 1_500_000.0, "delay": True, "status": "delayed"},
        ]

    def get_incoming_ships(self):
        result = []
        for s in self._ships:
            result.append(IncomingShip(**s))
        return result
