"""
data_loader.py
Combines Phase 3 forecasts, Phase 4 risk scores, current inventory,
and product/supplier reference data into one input table per product
— the actual inputs the optimizer needs.
"""

import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_generation"))
from db import engine


def get_optimization_inputs():
    query = """
        SELECT
            p.product_id,
            p.category,
            p.unit_cost,
            p.unit_price,
            p.lead_time_days_base,
            ps.supplier_id,
            COALESCE(r.risk_score, 0) as supplier_risk_score
        FROM products p
        JOIN product_suppliers ps ON p.product_id = ps.product_id AND ps.is_primary = 1
        LEFT JOIN supplier_risk_scores r ON ps.supplier_id = r.supplier_id
    """
    products = pd.read_sql(query, engine)

    # current on-hand inventory: latest snapshot per product
    inventory = pd.read_sql("""
        SELECT product_id, quantity_on_hand
        FROM inventory_snapshots
        WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM inventory_snapshots)
    """, engine)

    # forecasted demand for the next 30 days
    forecast = pd.read_sql("""
        SELECT product_id, ds, yhat, yhat_lower, yhat_upper
        FROM demand_forecasts
        ORDER BY product_id, ds
    """, engine, parse_dates=["ds"])

    return products, inventory, forecast


def build_product_input(product_id, products, inventory, forecast):
    """Assembles everything needed to optimize ONE product into a dict."""
    product_row = products[products["product_id"] == product_id].iloc[0]
    inv_row = inventory[inventory["product_id"] == product_id]
    on_hand = inv_row["quantity_on_hand"].iloc[0] if len(inv_row) else 0

    product_forecast = forecast[forecast["product_id"] == product_id].sort_values("ds")

    return {
        "product_id": product_id,
        "unit_cost": product_row["unit_cost"],
        "unit_price": product_row["unit_price"],
        "base_lead_time": product_row["lead_time_days_base"],
        "supplier_risk_score": product_row["supplier_risk_score"],
        "on_hand": on_hand,
        "demand": product_forecast["yhat"].values,
        "demand_upper": product_forecast["yhat_upper"].values,
    }


if __name__ == "__main__":
    products, inventory, forecast = get_optimization_inputs()
    print(f"Products: {len(products)}, Inventory rows: {len(inventory)}, Forecast rows: {len(forecast)}")

    sample = build_product_input(products["product_id"].iloc[0], products, inventory, forecast)
    print(f"\nSample input for {sample['product_id']}:")
    for k, v in sample.items():
        if k not in ("demand", "demand_upper"):
            print(f"  {k}: {v}")
    print(f"  demand (first 5 days): {sample['demand'][:5]}")