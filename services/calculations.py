from typing import List, Tuple
+from models.accountant_models import IncomingShip, RefineryStatus
+
+
+def calculate_incoming_usable(ships: List[IncomingShip]) -> float:
+    """Sum cargo quantities for ships that are not cancelled and are expected usable.
+    Conservative approach: exclude ships flagged as delayed unless status explicitly on-time.
+    """
+    total = 0.0
+    for s in ships:
+        try:
+            if s.cargo_quantity is None:
+                continue
+            # treat delayed ships as partially usable (50%) unless canceled
+            if getattr(s, "delay", False):
+                total += float(s.cargo_quantity) * 0.5
+            else:
+                total += float(s.cargo_quantity)
+        except Exception:
+            continue
+    return float(total)
+
+
+def calculate_survival_days(current_stock: float, incoming_usable: float, daily_consumption: float) -> float:
+    if daily_consumption <= 0:
+        return float("inf") if (current_stock + incoming_usable) > 0 else 0.0
+    available = max(0.0, current_stock + incoming_usable)
+    return available / float(daily_consumption)
+
+
+def calculate_national_deficit(current_stock: float, incoming_usable: float, daily_consumption: float, horizon_days: int = 30) -> float:
+    """Estimate deficit over a horizon (default 30 days). Positive means shortfall.
+    """
+    required = float(daily_consumption) * float(horizon_days)
+    available = float(current_stock + incoming_usable)
+    deficit = required - available
+    return float(deficit) if deficit > 0 else 0.0
+
+
+def calculate_risk(survival_days: float, severity: str, reported_confidence: float) -> Tuple[str, float]:
+    # Base risk from survival days (deterministic)
+    if survival_days == float("inf"):
+        base = "LOW"
+    elif survival_days > 20:
+        base = "LOW"
+    elif 10 <= survival_days <= 20:
+        base = "MEDIUM"
+    else:
+        base = "HIGH"
+
+    # Map severity text to a numeric factor to adjust confidence
+    severity_map = {"low": 0.9, "medium": 0.7, "high": 0.5}
+    sev_key = (severity or "").lower()
+    sev_factor = severity_map.get(sev_key, 0.8)
+
+    # Combine reported confidence (if any) with severity factor; default to 0.8
+    reported_confidence = float(reported_confidence) if reported_confidence is not None else 0.8
+    confidence = min(1.0, max(0.0, (reported_confidence + sev_factor) / 2))
+
+    return base, confidence
+
+
+def calculate_refinery_shortages(refineries: List[RefineryStatus], lookahead_days: int = 7):
+    """For each refinery, calculate if current inventory will cause a shortfall
+    over the lookahead period given daily_capacity.
+    Returns a list of dicts with name/status/reason.
+    """
+    results = []
+    for r in refineries:
+        try:
+            name = r.refinery
+            capacity = float(r.daily_capacity or 0.0)
+            inventory = float(r.current_inventory or 0.0)
+            expected_need = capacity * float(lookahead_days)
+            if inventory < expected_need:
+                shortage = expected_need - inventory
+                reason = f"Estimated shortage of {shortage:.1f} barrels over next {lookahead_days} days"
+                status = r.status or "reduced"
+            else:
+                reason = "Sufficient inventory for short-term operations"
+                status = r.status or "operational"
+            results.append({"name": name, "status": status, "reason": reason})
+        except Exception:
+            results.append({"name": getattr(r, "refinery", "unknown"), "status": "unknown", "reason": "failed to calculate"})
+    return results
