from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class DisruptionReport(BaseModel):
    raw: Dict[str, Any]
    event: str
    severity: Optional[str] = None
    expected_delay_days: Optional[int] = None
    confidence: Optional[float] = None


class Consumption(BaseModel):
    daily_consumption: float


class Stock(BaseModel):
    strategic_reserve: float
    commercial_stock: float
    total_stock: float


class IncomingShip(BaseModel):
    name: Optional[str]
    supplier: Optional[str]
    eta: Optional[str]
    cargo_quantity: Optional[float]
    delay: Optional[bool]
    status: Optional[str]


class RefineryStatus(BaseModel):
    refinery: str
    supported_crude: Optional[List[str]] = []
    daily_capacity: Optional[float] = 0.0
    current_inventory: Optional[float] = 0.0
    status: Optional[str] = "unknown"
