"""
run_forecasting.py
Runs the full per-SKU forecasting pipeline: for every product, fit
Prophet, run rolling-origin CV, fit the SARIMA benchmark, and save
results to the database for downstream phases (optimization, app).
"""

import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_generation"))
from db import engine

from data_loader import get_all_product_ids, get_demand_for_product
from prophet_forecaster import fit_prophet_model, forecast_future
from sarima_forecaster import fit_sarima_model, forecast_sarima
from cross_validation import rolling_origin_cv


def run_full_pipeline(forecast_horizon=30):
    product_ids = get_all_product_ids()
    print(f"Running forecasting pipeline for {len(product_ids)} products...\n")

    all_forecasts = []
    all_cv_results = []
    accuracy_summary = []

    for i, product_id in enumerate(product_ids, 1):
        print(f"[{i}/{len(product_ids)}] {product_id}")
        demand_df = get_demand_for_product(product_id)

        # 1. Rolling-origin CV (accuracy validation)
        cv_results_df, cv_summary = rolling_origin_cv(demand_df, horizon_days=forecast_horizon)
        cv_results_df["product_id"] = product_id
        all_cv_results.append(cv_results_df)
        accuracy_summary.append({"product_id": product_id, **cv_summary})
        print(f"    Mean MAPE: {cv_summary['mean_mape']:.2f}%  ({cv_summary['n_folds']} folds)")

        # 2. Final production forecast (train on ALL available history)
        final_model = fit_prophet_model(demand_df)
        forecast = forecast_future(final_model, periods=forecast_horizon)
        forecast_future_only = forecast[forecast["ds"] > demand_df["ds"].max()].copy()
        forecast_future_only["product_id"] = product_id
        all_forecasts.append(
            forecast_future_only[["product_id", "ds", "yhat", "yhat_lower", "yhat_upper"]]
        )

        # 3. SARIMA benchmark (for comparison, not used downstream directly)
        try:
            sarima_fitted = fit_sarima_model(demand_df)
            sarima_forecast = forecast_sarima(sarima_fitted, periods=forecast_horizon)
            sarima_mape = None  # optional: extend with its own CV if you want a like-for-like comparison
        except Exception as e:
            print(f"    ⚠️  SARIMA fit failed for {product_id}: {e}")

    forecasts_df = pd.concat(all_forecasts, ignore_index=True)
    cv_results_df = pd.concat(all_cv_results, ignore_index=True)
    accuracy_df = pd.DataFrame(accuracy_summary)

    print("\nSaving results to database...")
    forecasts_df.to_sql("demand_forecasts", engine, if_exists="replace", index=False)
    cv_results_df.to_sql("forecast_cv_results", engine, if_exists="replace", index=False)
    accuracy_df.to_sql("forecast_accuracy_summary", engine, if_exists="replace", index=False)

    print(f"\n✅ Pipeline complete.")
    print(f"   Forecasts: {len(forecasts_df)} rows across {len(product_ids)} products")
    print(f"   Overall mean MAPE: {accuracy_df['mean_mape'].mean():.2f}%")
    print(f"   Best product: {accuracy_df.loc[accuracy_df['mean_mape'].idxmin(), 'product_id']} "
          f"({accuracy_df['mean_mape'].min():.2f}% MAPE)")
    print(f"   Worst product: {accuracy_df.loc[accuracy_df['mean_mape'].idxmax(), 'product_id']} "
          f"({accuracy_df['mean_mape'].max():.2f}% MAPE)")

    return forecasts_df, cv_results_df, accuracy_df


if __name__ == "__main__":
    run_full_pipeline()