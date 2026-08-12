"""
run_optimization.py
Runs the inventory optimization for every product and saves the
recommended order plan to the database.

Run:
    python src/optimization/run_optimization.py
"""

import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_generation"))
from db import engine

from data_loader import get_optimization_inputs, build_product_input
from optimizer import optimize_product


def run_all_optimizations():
    products, inventory, forecast = get_optimization_inputs()
    product_ids = products["product_id"].unique()

    print(f"Optimizing {len(product_ids)} products...\n")
    results = []

    for i, product_id in enumerate(product_ids, 1):
        product_input = build_product_input(product_id, products, inventory, forecast)
        result = optimize_product(product_input)
        results.append(result)

        status_flag = "✅" if result["status"] == "Optimal" else "⚠️"
        print(f"[{i}/{len(product_ids)}] {status_flag} {product_id}: "
              f"order {result['order_quantity']} units, cost ${result['total_cost']}")

    results_df = pd.DataFrame(results)
    results_df.to_sql("inventory_optimization_results", engine, if_exists="replace", index=False)

    n_infeasible = (results_df["status"] != "Optimal").sum()
    print(f"\n✅ Done. {len(results_df) - n_infeasible}/{len(results_df)} solved optimally.")
    if n_infeasible > 0:
        print(f"⚠️  {n_infeasible} product(s) not optimal — review before trusting their recommendation")

    print(f"\nTotal recommended order cost across all products: ${results_df['total_cost'].sum():,.2f}")

    return results_df


if __name__ == "__main__":
    run_all_optimizations()