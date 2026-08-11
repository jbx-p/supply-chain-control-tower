"""
cross_validation.py
Rolling-origin cross-validation for per-SKU demand forecasts, with
MAPE (Mean Absolute Percentage Error) as the primary accuracy metric.
"""

import numpy as np
import pandas as pd

from prophet_forecaster import fit_prophet_model, forecast_future


def calculate_mape(actual, predicted):
    """
    MAPE: average absolute percentage error. Excludes zero-actual
    days from the denominator to avoid division by zero — those days
    are still worth reviewing separately if frequent.
    """
    actual = np.array(actual)
    predicted = np.array(predicted)
    mask = actual != 0
    if mask.sum() == 0:
        return np.nan
    return float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100)


def rolling_origin_cv(demand_df, initial_train_days=365, horizon_days=30,
                       step_days=30, min_folds=3):
    """
    demand_df: full ['ds', 'y'] history for one product, sorted by date.

    Splits the series into multiple train/test folds by walking the
    cutoff date forward `step_days` at a time. For each fold: train
    on everything up to the cutoff, forecast `horizon_days` ahead,
    compare against actuals, record MAPE.

    Returns a DataFrame of per-fold results and a summary dict.
    """
    demand_df = demand_df.sort_values("ds").reset_index(drop=True)
    total_days = len(demand_df)

    results = []
    cutoff_idx = initial_train_days

    while cutoff_idx + horizon_days <= total_days:
        train = demand_df.iloc[:cutoff_idx]
        test = demand_df.iloc[cutoff_idx: cutoff_idx + horizon_days]

        model = fit_prophet_model(train)
        forecast = forecast_future(model, periods=horizon_days)

        # align forecast to the test window only
        forecast_window = forecast[forecast["ds"].isin(test["ds"])]
        merged = test.merge(forecast_window[["ds", "yhat"]], on="ds", how="inner")

        mape = calculate_mape(merged["y"], merged["yhat"])

        results.append({
            "cutoff_date": train["ds"].max(),
            "test_start": test["ds"].min(),
            "test_end": test["ds"].max(),
            "mape": mape,
        })

        cutoff_idx += step_days

    results_df = pd.DataFrame(results)

    if len(results_df) < min_folds:
        print(f"  ⚠️  Only {len(results_df)} fold(s) — increase history or reduce step_days for a more reliable estimate")

    summary = {
        "n_folds": len(results_df),
        "mean_mape": results_df["mape"].mean() if len(results_df) else np.nan,
        "std_mape": results_df["mape"].std() if len(results_df) else np.nan,
        "min_mape": results_df["mape"].min() if len(results_df) else np.nan,
        "max_mape": results_df["mape"].max() if len(results_df) else np.nan,
    }

    return results_df, summary


if __name__ == "__main__":
    from data_loader import get_all_product_ids, get_demand_for_product

    product_id = get_all_product_ids()[0]
    demand_df = get_demand_for_product(product_id)

    print(f"Running rolling-origin CV for {product_id}...\n")
    results_df, summary = rolling_origin_cv(demand_df)

    print(results_df)
    print(f"\nMean MAPE: {summary['mean_mape']:.2f}%")
    print(f"MAPE range: {summary['min_mape']:.2f}% - {summary['max_mape']:.2f}%")
    print(f"Folds: {summary['n_folds']}")