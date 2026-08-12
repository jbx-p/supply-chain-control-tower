"""
export_for_tableau.py
Exports curated CSV files for the Tableau Public dashboard — flat,
denormalized tables Tableau can connect to directly, since Tableau
Public doesn't support a shareable live connection to a local SQLite
database.

Run:
    python src/app/export_for_tableau.py
"""

import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_generation"))
from db import engine


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "tableau_data")


def export_demand_summary():
    """Product-level forecast trend + accuracy, denormalized with category."""
    query = """
        SELECT
            f.product_id, p.category,
            f.ds as forecast_date, f.yhat, f.yhat_lower, f.yhat_upper,
            a.mean_mape
        FROM demand_forecasts f
        JOIN products p ON f.product_id = p.product_id
        JOIN forecast_accuracy_summary a ON f.product_id = a.product_id
    """
    df = pd.read_sql(query, engine, parse_dates=["forecast_date"])
    df.to_csv(os.path.join(OUTPUT_DIR, "demand_summary.csv"), index=False)
    return len(df)


def export_supplier_risk():
    df = pd.read_sql("SELECT * FROM supplier_risk_scores", engine)
    df.to_csv(os.path.join(OUTPUT_DIR, "supplier_risk.csv"), index=False)
    return len(df)


def export_optimization_comparison():
    query = """
        SELECT c.*, p.category
        FROM optimization_vs_naive_comparison c
        JOIN products p ON c.product_id = p.product_id
    """
    df = pd.read_sql(query, engine)
    df.to_csv(os.path.join(OUTPUT_DIR, "optimization_comparison.csv"), index=False)
    return len(df)


def export_simulation_results():
    query = """
        SELECT sc.*, p.category, r.risk_score
        FROM simulation_policy_comparison sc
        JOIN products p ON sc.product_id = p.product_id
        JOIN product_suppliers ps ON p.product_id = ps.product_id AND ps.is_primary = 1
        JOIN supplier_risk_scores r ON ps.supplier_id = r.supplier_id
    """
    df = pd.read_sql(query, engine)
    df.to_csv(os.path.join(OUTPUT_DIR, "simulation_results.csv"), index=False)
    return len(df)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    counts = {
        "demand_summary.csv": export_demand_summary(),
        "supplier_risk.csv": export_supplier_risk(),
        "optimization_comparison.csv": export_optimization_comparison(),
        "simulation_results.csv": export_simulation_results(),
    }

    print("Exported files:")
    for filename, count in counts.items():
        print(f"  {filename}: {count} rows")
    print(f"\n✅ Saved to {OUTPUT_DIR}")