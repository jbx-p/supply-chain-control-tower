"""
check_risk_correlation.py
Correlates supplier risk score against Phase 6's simulated service-level
improvement (optimized vs naive policy) — confirms whether the
risk-adjusted safety stock policy's benefit concentrates on
higher-risk suppliers, as designed. Result: r ≈ 0.46.
"""

import sys, os
sys.path.append(os.path.join("..", "data_generation"))
from db import engine
import pandas as pd

risk_scores = pd.read_sql("""
    SELECT ps.product_id, r.risk_score
    FROM product_suppliers ps
    JOIN supplier_risk_scores r ON ps.supplier_id = r.supplier_id
    WHERE ps.is_primary = 1
""", engine)

comparison = pd.read_sql("SELECT * FROM simulation_policy_comparison", engine)

merged = comparison.merge(risk_scores, on="product_id")
print(merged[["product_id", "risk_score", "service_level_improvement"]]
      .sort_values("risk_score", ascending=False).to_string(index=False))
print()
print("Correlation between risk score and improvement:",
      merged["risk_score"].corr(merged["service_level_improvement"]))