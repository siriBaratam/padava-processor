import json
import re
from .accountant import Accountant

_accountant = Accountant()

def run_accountant(scout_output):

    if isinstance(scout_output, str):

        match = re.search(r"\[\s*{.*}\s*\]", scout_output, re.DOTALL)

        if not match:
            raise ValueError("Scout output does not contain a valid JSON array.")

        scout_output = json.loads(match.group(0))

    if isinstance(scout_output, list):
        return _accountant.analyze_batch(scout_output)

    return _accountant.analyze(scout_output)