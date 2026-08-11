"""
feature_engineering.py
Builds a supplier x month panel of performance features from orders
and shipments, then adds lagged features so the model predicts next
month's risk from prior behavior (not from the same month it's
labeling — that would be circular).
"""

import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_generation"))
from db import engine


def load_raw_order_data():
    query = """
        SELECT
            o.order_id, o.supplier_id, o.product_id,
            o.order_date, o.expected_delivery_date, o.actual_delivery_date,
            o.quantity_ordered
        FROM orders o
    """
    df = pd.read_sql(query, engine, parse_dates=["order_date", "expected_delivery_date", "actual_delivery_date"])
    return df


def load_shipment_fulfillment():
    query = """
        SELECT o.order_id, o.supplier_id, o.quantity_ordered,
               SUM(sh.quantity_shipped) as total_shipped,
               COUNT(sh.shipment_id) as shipment_count
        FROM orders o
        JOIN shipments sh ON o.order_id = sh.order_id
        GROUP BY o.order_id
    """
    return pd.read_sql(query, engine)


def build_monthly_panel():
    orders = load_raw_order_data()
    fulfillment = load_shipment_fulfillment()

    orders["delay_days"] = (orders["actual_delivery_date"] - orders["expected_delivery_date"]).dt.days
    orders["on_time"] = orders["delay_days"] <= 2
    orders["order_month"] = orders["order_date"].dt.to_period("M")

    orders = orders.merge(
        fulfillment[["order_id", "total_shipped", "shipment_count"]],
        on="order_id", how="left"
    )
    orders["fulfillment_ratio"] = orders["total_shipped"] / orders["quantity_ordered"]

    panel = orders.groupby(["supplier_id", "order_month"]).agg(
        on_time_rate=("on_time", "mean"),
        avg_delay_days=("delay_days", "mean"),
        delay_std=("delay_days", "std"),
        order_count=("order_id", "count"),
        avg_fulfillment_ratio=("fulfillment_ratio", "mean"),
        avg_shipment_count=("shipment_count", "mean"),
    ).reset_index()

    diversity = pd.read_sql("""
        SELECT supplier_id, COUNT(DISTINCT product_id) as product_diversity
        FROM product_suppliers
        GROUP BY supplier_id
    """, engine)
    panel = panel.merge(diversity, on="supplier_id", how="left")

    panel["delay_std"] = panel["delay_std"].fillna(0)
    panel = panel.sort_values(["supplier_id", "order_month"]).reset_index(drop=True)

    return panel


def add_lagged_features(panel):
    """
    Shifts each supplier's features forward by one month, so the row
    for month M contains month M-1's behavior as predictors, and
    month M's own on_time_rate as the label.
    """
    panel = panel.sort_values(["supplier_id", "order_month"]).copy()

    feature_cols = [
        "on_time_rate", "avg_delay_days", "delay_std",
        "order_count", "avg_fulfillment_ratio", "avg_shipment_count",
    ]

    for col in feature_cols:
        panel[f"prev_{col}"] = panel.groupby("supplier_id")[col].shift(1)

    panel["rolling_3m_on_time"] = (
        panel.groupby("supplier_id")["on_time_rate"]
        .shift(1)
        .rolling(3, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    panel["is_risk_month"] = (panel["on_time_rate"] < 0.80).astype(int)

    panel = panel.dropna(subset=[f"prev_{c}" for c in feature_cols])

    return panel


if __name__ == "__main__":
    panel = build_monthly_panel()
    print(f"Built panel: {len(panel)} supplier-month rows across {panel['supplier_id'].nunique()} suppliers")

    panel_with_lags = add_lagged_features(panel)
    print(f"After adding lags: {len(panel_with_lags)} rows (first month per supplier dropped)")
    print(f"Risk month rate: {panel_with_lags['is_risk_month'].mean():.1%}")
    print("\nSample row:")
    print(panel_with_lags.iloc[0])