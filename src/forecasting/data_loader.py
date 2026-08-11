"""
data_loader.py
Pulls per-product demand history from the database in the format
each forecasting library expects.
"""

import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_generation"))
from db import engine


def get_all_product_ids():
    df = pd.read_sql("SELECT DISTINCT product_id FROM products ORDER BY product_id", engine)
    return df["product_id"].tolist()


def get_demand_for_product(product_id):
    """
    Returns a DataFrame with columns ['ds', 'y'] — Prophet's required
    naming convention (ds = date, y = value). Reused for SARIMA too,
    just accessed via .y instead.
    """
    query = """
        SELECT date, units_sold
        FROM demand_history
        WHERE product_id = ?
        ORDER BY date
    """
    df = pd.read_sql(query, engine, params=(product_id,))
    df = df.rename(columns={"date": "ds", "units_sold": "y"})
    df["ds"] = pd.to_datetime(df["ds"])
    return df


if __name__ == "__main__":
    product_ids = get_all_product_ids()
    print(f"Found {len(product_ids)} products")
    sample = get_demand_for_product(product_ids[0])
    print(f"\nSample demand for {product_ids[0]}:")
    print(sample.head())
    print(f"Date range: {sample['ds'].min()} to {sample['ds'].max()}")
    print(f"Total rows: {len(sample)}")