from typing import Protocol, Optional
from models.accountant_models import Stock


class StockToolInterface(Protocol):
    def get_current_stock(self) -> Stock: ...


class MockStockTool:
    def __init__(self, strategic: float = 30_000_000.0, commercial: float = 20_000_000.0):
        self._strategic = strategic
        self._commercial = commercial

    def get_current_stock(self) -> Stock:
        total = float(self._strategic + self._commercial)
        return Stock(strategic_reserve=float(self._strategic), commercial_stock=float(self._commercial), total_stock=total)
