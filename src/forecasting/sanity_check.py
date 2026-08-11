"""
sanity_check.py
Phase 3, Step 8 — Sanity-checks the forecasting pipeline's output:
accuracy distribution, category-level MAPE breakdown, and any
products with suspiciously high error worth investigating further.

Run:
    python src/forecasting/sanity_check.py
"""

import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_generation"))
from db import engine


def load_accuracy_with_category():
    """Joins forecast accuracy with product category for breakdown analysis."""
    query = """
        SELECT
            a.product_id,
            p.category,
            a.mean_mape,
            a.std_mape,
            a.min_mape,
            a.max_mape,
            a.n_folds
        FROM forecast_accuracy_summary a
        JOIN products p ON a.product_id = p.product_id
        ORDER BY a.mean_mape
    """
    return pd.read_sql(query, engine)


def print_overall_summary(df):
    print("=" * 60)
    print("OVERALL FORECAST ACCURACY")
    print("=" * 60)
    print(f"Products evaluated:  {len(df)}")
    print(f"Mean MAPE:           {df['mean_mape'].mean():.2f}%")
    print(f"Median MAPE:         {df['mean_mape'].median():.2f}%")
    print(f"Std dev:             {df['mean_mape'].std():.2f}%")
    print(f"Range:               {df['mean_mape'].min():.2f}% - {df['mean_mape'].max():.2f}%")
    print(f"Avg folds/product:   {df['n_folds'].mean():.1f}")


def print_category_breakdown(df):
    print("\n" + "=" * 60)
    print("ACCURACY BY CATEGORY")
    print("=" * 60)
    category_summary = df.groupby("category")["mean_mape"].agg(
        ["mean", "median", "std", "count"]
    ).round(2)
    category_summary.columns = ["Mean MAPE", "Median MAPE", "Std Dev", "# Products"]
    print(category_summary.to_string())


def print_full_table(df):
    print("\n" + "=" * 60)
    print("ALL PRODUCTS (sorted best to worst)")
    print("=" * 60)
    print(df[["product_id", "category", "mean_mape", "n_folds"]].to_string(index=False))


def flag_outliers(df, threshold=50.0):
    print("\n" + "=" * 60)
    print(f"PRODUCTS WITH MAPE > {threshold}% (worth investigating)")
    print("=" * 60)
    outliers = df[df["mean_mape"] > threshold]
    if len(outliers) == 0:
        print(f"None — all products are under {threshold}% MAPE ✅")
    else:
        print(outliers[["product_id", "category", "mean_mape", "n_folds"]].to_string(index=False))
        print(f"\n⚠️  {len(outliers)} product(s) flagged. Consider checking:")
        print("   - Low baseline demand (percentage errors get exaggerated on small numbers)")
        print("   - Overlap with a Phase 1 disruption window")
        print("   - Insufficient history (low n_folds)")


def flag_low_fold_count(df, min_folds=3):
    print("\n" + "=" * 60)
    print(f"PRODUCTS WITH FEWER THAN {min_folds} CV FOLDS (less reliable estimate)")
    print("=" * 60)
    low_folds = df[df["n_folds"] < min_folds]
    if len(low_folds) == 0:
        print("None — every product has enough folds for a stable estimate ✅")
    else:
        print(low_folds[["product_id", "n_folds"]].to_string(index=False))


def check_forecast_table_shape():
    print("\n" + "=" * 60)
    print("FORECAST TABLE SHAPE CHECK")
    print("=" * 60)
    forecasts = pd.read_sql("SELECT * FROM demand_forecasts", engine)
    products = pd.read_sql("SELECT DISTINCT product_id FROM products", engine)

    n_products_forecasted = forecasts["product_id"].nunique()
    n_products_total = len(products)
    rows_per_product = forecasts.groupby("product_id").size()

    print(f"Products with forecasts:  {n_products_forecasted}/{n_products_total}")
    print(f"Forecast horizon (days):  {rows_per_product.mode()[0]} (most common)")

    if n_products_forecasted < n_products_total:
        missing = set(products["product_id"]) - set(forecasts["product_id"])
        print(f"⚠️  Missing forecasts for: {sorted(missing)}")
    else:
        print("✅ Every product has a forecast")

    # negative forecast values are physically implausible for demand
    negative_forecasts = forecasts[forecasts["yhat"] < 0]
    if len(negative_forecasts) > 0:
        print(f"⚠️  {len(negative_forecasts)} forecasted rows have negative yhat — "
              f"Prophet doesn't enforce non-negativity by default")
    else:
        print("✅ No negative forecast values")


def main():
    df = load_accuracy_with_category()

    print_overall_summary(df)
    print_category_breakdown(df)
    flag_outliers(df)
    flag_low_fold_count(df)
    check_forecast_table_shape()
    print_full_table(df)


if __name__ == "__main__":
    main()