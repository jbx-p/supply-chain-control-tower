"""
policy_loader.py
Derives reorder-point policy parameters (reorder_point, order_quantity)
for both the OPTIMIZED policy (using Phase 5's risk-adjusted safety
stock) and the NAIVE policy (flat margin, no risk-adjustment) — so
the simulation tests the same two policies Phase 5 compared, just
under an ongoing, stochastic reorder regime instead of a single
deterministic order.
"""

import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_generation"))
from db import engine

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "optimization"))
from data_loader import get_optimization_inputs, build_product_input


def compute_policy_params(product_input):
    demand = product_input["demand"]
    daily_demand_mean = float(demand.mean())
    daily_demand_std = float(demand.std())
    lead_time = product_input["base_lead_time"]
    risk_score = product_input["supplier_risk_score"]

    risk_adjusted_lead_time = lead_time * (1 + (risk_score / 100) * 0.5)

    # OPTIMIZED policy: reorder point covers expected demand during
    # lead time PLUS the Phase 5-style safety buffer (scaled by risk)
    expected_demand_during_lead_time = daily_demand_mean * risk_adjusted_lead_time
    safety_buffer = daily_demand_std * (risk_adjusted_lead_time ** 0.5) * (1 + risk_score / 100)
    optimized_reorder_point = expected_demand_during_lead_time + safety_buffer
    optimized_order_qty = daily_demand_mean * risk_adjusted_lead_time * 1.5  # covers ~1.5 lead times of demand

    # NAIVE policy: reorder point covers only expected demand during
    # the UN-adjusted lead time, no safety buffer at all
    naive_reorder_point = daily_demand_mean * lead_time
    naive_order_qty = daily_demand_mean * lead_time * 1.5

    return {
        "product_id": product_input["product_id"],
        "daily_demand_mean": daily_demand_mean,
        "daily_demand_std": daily_demand_std,
        "base_lead_time": lead_time,
        "risk_score": risk_score,
        "optimized_reorder_point": round(optimized_reorder_point, 1),
        "optimized_order_qty": round(optimized_order_qty, 1),
        "naive_reorder_point": round(naive_reorder_point, 1),
        "naive_order_qty": round(naive_order_qty, 1),
    }


def get_all_policy_params():
    products, inventory, forecast = get_optimization_inputs()
    results = []
    for product_id in products["product_id"].unique():
        product_input = build_product_input(product_id, products, inventory, forecast)
        results.append(compute_policy_params(product_input))
    return pd.DataFrame(results)


if __name__ == "__main__":
    df = get_all_policy_params()
    print(df.head(10).to_string(index=False))