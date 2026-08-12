"""
data_aggregator.py
Pulls a curated, decision-relevant summary from every prior phase's
output tables — this is the actual input to the briefing generator,
not raw dumps of every table.
"""

import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_generation"))
from db import engine


def get_forecast_summary():
    """Top-line demand trend: which products/categories are trending up or down."""
    forecasts = pd.read_sql("SELECT * FROM demand_forecasts", engine, parse_dates=["ds"])
    products = pd.read_sql("SELECT product_id, category FROM products", engine)
    accuracy = pd.read_sql("SELECT product_id, mean_mape FROM forecast_accuracy_summary", engine)

    # trend: compare first vs last week of the forecast horizon per product
    trend_rows = []
    for product_id, group in forecasts.groupby("product_id"):
        group = group.sort_values("ds")
        first_week = group.head(7)["yhat"].mean()
        last_week = group.tail(7)["yhat"].mean()
        pct_change = ((last_week - first_week) / first_week * 100) if first_week > 0 else 0
        trend_rows.append({"product_id": product_id, "demand_trend_pct": round(pct_change, 1)})

    trend_df = pd.DataFrame(trend_rows).merge(products, on="product_id").merge(accuracy, on="product_id")

    return {
        "overall_mean_mape": round(accuracy["mean_mape"].mean(), 1),
        "top_growing": trend_df.nlargest(3, "demand_trend_pct")[["product_id", "category", "demand_trend_pct"]].to_dict("records"),
        "top_declining": trend_df.nsmallest(3, "demand_trend_pct")[["product_id", "category", "demand_trend_pct"]].to_dict("records"),
    }


def get_supplier_risk_summary():
    """Highest-risk suppliers right now, per Phase 4."""
    risk = pd.read_sql(
        "SELECT * FROM supplier_risk_scores ORDER BY risk_score DESC LIMIT 5", engine
    )
    return risk[["supplier_id", "name", "country", "risk_score", "risk_tier"]].to_dict("records")


def get_optimization_summary():
    """Cost comparison and top products by optimization impact, per Phase 5."""
    comparison = pd.read_sql("SELECT * FROM optimization_vs_naive_comparison", engine)
    total_optimized = comparison["optimized_cost"].sum()
    total_naive = comparison["naive_cost"].sum()

    return {
        "total_optimized_cost": round(total_optimized, 2),
        "total_naive_cost": round(total_naive, 2),
        "cost_delta_pct": round((total_optimized - total_naive) / total_naive * 100, 1),
    }


def get_simulation_summary():
    """Resilience findings from Phase 6's Monte Carlo simulation."""
    policy_comparison = pd.read_sql("SELECT * FROM simulation_policy_comparison", engine)
    trials = pd.read_sql("SELECT policy, service_level FROM simulation_trial_results", engine)

    summary_by_policy = trials.groupby("policy")["service_level"].mean()

    top_improved = policy_comparison.nlargest(3, "service_level_improvement")

    return {
        "naive_mean_service_level": round(summary_by_policy.get("naive", 0) * 100, 1),
        "optimized_mean_service_level": round(summary_by_policy.get("optimized", 0) * 100, 1),
        "top_resilience_gains": top_improved[
            ["product_id", "service_level_improvement"]
        ].to_dict("records"),
    }


def build_full_briefing_data():
    return {
        "forecast": get_forecast_summary(),
        "supplier_risk": get_supplier_risk_summary(),
        "optimization": get_optimization_summary(),
        "simulation": get_simulation_summary(),
    }


if __name__ == "__main__":
    import json
    data = build_full_briefing_data()
    print(json.dumps(data, indent=2, default=str))