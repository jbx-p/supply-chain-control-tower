"""
analyze_results.py
Aggregates Monte Carlo trial results into a policy comparison:
average and worst-case service level, stockout exposure, and how
often each policy actually got hit by a disruption event.

Run:
    python src/simulation/analyze_results.py
"""

import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_generation"))
from db import engine


def summarize_by_policy():
    trials = pd.read_sql("SELECT * FROM simulation_trial_results", engine)

    summary = trials.groupby("policy").agg(
        mean_service_level=("service_level", "mean"),
        p10_service_level=("service_level", lambda x: x.quantile(0.10)),  # worst-case tail
        mean_stockout_units=("total_stockout_units", "mean"),
        mean_orders_placed=("orders_placed", "mean"),
        mean_disruption_events=("disruption_events", "mean"),
    ).round(4)

    return trials, summary


def summarize_by_product(trials):
    per_product = trials.groupby(["product_id", "policy"]).agg(
        mean_service_level=("service_level", "mean"),
        p10_service_level=("service_level", lambda x: x.quantile(0.10)),
    ).round(4).reset_index()

    pivoted = per_product.pivot(index="product_id", columns="policy",
                                 values=["mean_service_level", "p10_service_level"])
    pivoted.columns = ["_".join(col) for col in pivoted.columns]
    pivoted = pivoted.reset_index()
    pivoted["service_level_improvement"] = (
        pivoted["mean_service_level_optimized"] - pivoted["mean_service_level_naive"]
    )
    return pivoted.sort_values("service_level_improvement", ascending=False)


def main():
    trials, summary = summarize_by_policy()

    print("=" * 60)
    print("OVERALL POLICY COMPARISON (across all products, all trials)")
    print("=" * 60)
    print(summary.to_string())

    per_product = summarize_by_product(trials)
    per_product.to_sql("simulation_policy_comparison", engine, if_exists="replace", index=False)

    print("\n" + "=" * 60)
    print("TOP 5 PRODUCTS — BIGGEST SERVICE LEVEL IMPROVEMENT (optimized vs naive)")
    print("=" * 60)
    print(per_product.head(5)[
        ["product_id", "mean_service_level_naive", "mean_service_level_optimized",
         "service_level_improvement"]
    ].to_string(index=False))

    print("\n" + "=" * 60)
    print("BOTTOM 5 PRODUCTS — smallest or negative improvement (worth investigating)")
    print("=" * 60)
    print(per_product.tail(5)[
        ["product_id", "mean_service_level_naive", "mean_service_level_optimized",
         "service_level_improvement"]
    ].to_string(index=False))


if __name__ == "__main__":
    main()