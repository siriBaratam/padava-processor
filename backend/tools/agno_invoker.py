from typing import Any
from tools.consumption_tool import MockConsumptionTool
from tools.stock_tool import MockStockTool
from tools.shipping_tool import MockShippingTool
from tools.refinery_tool import MockRefineryTool


class AgnoToolInvoker:
    """Simple invoker that represents Agno tool-calling mechanism.
    It maps logical tool names to concrete tool instances. In production the
    invoker would call remote tools via Agno; here it delegates to tool
    implementations in `tools/`.
    """

    def __init__(self, consumption=None, stock=None, shipping=None, refinery=None):
        self._consumption = consumption or MockConsumptionTool()
        self._stock = stock or MockStockTool()
        self._shipping = shipping or MockShippingTool()
        self._refinery = refinery or MockRefineryTool()

    def call_tool(self, tool_name: str, method: str, *args, **kwargs) -> Any:
        if tool_name == "consumption":
            if method == "get_consumption":
                return self._consumption.get_consumption()
        if tool_name == "stock":
            if method == "get_current_stock":
                return self._stock.get_current_stock()
        if tool_name == "shipping":
            if method == "get_incoming_ships":
                return self._shipping.get_incoming_ships()
        if tool_name == "refinery":
            if method == "get_refinery_status":
                return self._refinery.get_refinery_status()
        raise NotImplementedError(f"Tool {tool_name}.{method} not implemented in invoker")
