"""
compare_policies.py
Runs both the LP-optimized policy and the naive baseline across all
products, and reports the cost difference — the actual "so what" of
this phase.
"""

import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_generation"))
from db import engine

from data_loader import get_optimization_inputs, build_product_input
from optimizer import optimize_product
from naive_baseline import evaluate_naive_policy


def compare_all_products():
    products, inventory, forecast = get_optimization_inputs()
    product_ids = products["product_id"].unique()

    comparisons = []
    for product_id in product_ids:
        product_input = build_product_input(product_id, products, inventory, forecast)
        optimized = optimize_product(product_input)
        naive = evaluate_naive_policy(product_input)

        comparisons.append({
            "product_id": product_id,
            "optimized_cost": optimized["total_cost"],
            "naive_cost": naive["naive_total_cost"],
            "savings": naive["naive_total_cost"] - optimized["total_cost"],
            "savings_pct": (
                (naive["naive_total_cost"] - optimized["total_cost"]) / naive["naive_total_cost"] * 100
                if naive["naive_total_cost"] > 0 else 0
            ),
        })

    comparison_df = pd.DataFrame(comparisons)
    comparison_df.to_sql("optimization_vs_naive_comparison", engine, if_exists="replace", index=False)

    total_optimized = comparison_df["optimized_cost"].sum()
    total_naive = comparison_df["naive_cost"].sum()
    total_savings = total_naive - total_optimized
    savings_pct = (total_savings / total_naive * 100) if total_naive > 0 else 0

    print(f"Naive policy total cost:      ${total_naive:,.2f}")
    print(f"Optimized policy total cost:  ${total_optimized:,.2f}")
    print(f"Total savings:                ${total_savings:,.2f} ({savings_pct:.1f}%)")

    print(f"\nTop 5 products by savings:")
    print(comparison_df.sort_values("savings", ascending=False).head(5).to_string(index=False))

    return comparison_df


if __name__ == "__main__":
    compare_all_products()