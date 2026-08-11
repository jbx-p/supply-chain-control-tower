"""
score_suppliers.py
Uses the trained model to score every supplier's CURRENT risk level,
based on their most recent month of behavior — this is the live,
actionable output of the pipeline.
"""

import sys
import os
import pandas as pd
import joblib

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_generation"))
from db import engine

from feature_engineering import build_monthly_panel, add_lagged_features
from train_model import FEATURE_COLS


def get_latest_features_per_supplier():
    """
    For each supplier, takes their MOST RECENT month's features as
    the input for a live "how risky is this supplier right now"
    prediction (i.e. predicting risk for the month just ahead).
    """
    panel = build_monthly_panel()
    panel = add_lagged_features(panel)

    latest = panel.sort_values("order_month").groupby("supplier_id").tail(1)
    return latest


def risk_tier(score):
    if score >= 66:
        return "High"
    elif score >= 33:
        return "Medium"
    else:
        return "Low"


def score_all_suppliers():
    model = joblib.load("supplier_risk_model.joblib")
    latest = get_latest_features_per_supplier()

    X = latest[FEATURE_COLS]
    probabilities = model.predict_proba(X)[:, 1]  # probability of "high risk"

    results = latest[["supplier_id", "order_month"]].copy()
    results["order_month"] = results["order_month"].astype(str)
    results["risk_score"] = (probabilities * 100).round(1)
    results["risk_tier"] = results["risk_score"].apply(risk_tier)

    # bring in supplier names/countries for a readable output
    suppliers = pd.read_sql("SELECT supplier_id, name, country, reliability_base FROM suppliers", engine)
    results = results.merge(suppliers, on="supplier_id", how="left")

    results = results.sort_values("risk_score", ascending=False).reset_index(drop=True)

    results.to_sql("supplier_risk_scores", engine, if_exists="replace", index=False)

    print("Supplier Risk Scores (highest risk first):\n")
    print(results[["supplier_id", "name", "country", "risk_score", "risk_tier"]].to_string(index=False))

    return results


if __name__ == "__main__":
    score_all_suppliers()