from typing import Protocol
from models.accountant_models import Consumption


class ConsumptionToolInterface(Protocol):
    def get_consumption(self) -> Consumption: ...


class MockConsumptionTool:
    """A lightweight mock implementation. Production systems should provide
    another implementation that conforms to the same interface.
    """

    def __init__(self, daily: float = 4_000_000.0):
        # default daily consumption in barrels/day (example figure)
        self._daily = daily

    def get_consumption(self) -> Consumption:
        return Consumption(daily_consumption=float(self._daily))
