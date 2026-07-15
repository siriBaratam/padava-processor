import json
from pathlib import Path
from agents.accountant_agent import AccountantAgent, AccountantAgnoWrapper
from tools.agno_invoker import AgnoToolInvoker
from tools.consumption_tool import MockConsumptionTool

BASE = Path(__file__).resolve().parent
SCOUT_STATE = BASE.parent / "Scout-agent" / "scout_output.json"


def load_latest_scout_entry() -> dict:
    if not SCOUT_STATE.exists():
        raise FileNotFoundError(f"Scout output file not found: {SCOUT_STATE}")
    data = json.loads(SCOUT_STATE.read_text(encoding="utf-8"))
    entries = data.get("entries") or []
    if not entries:
        raise ValueError("No entries found in scout_output.json")
    # choose most recent entry (last)
    return entries[-1]


def main():
    report = load_latest_scout_entry()

    # instantiate real tool implementations (or mocks if runtime provides none)
    invoker = AgnoToolInvoker()
    acct = AccountantAgent(consumption_tool=None, stock_tool=None, shipping_tool=None, refinery_tool=None)
    wrapper = AccountantAgnoWrapper(acct, invoker)

    result = wrapper.run(report)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
