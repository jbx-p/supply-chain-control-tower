"""
prophet_forecaster.py
Wraps Prophet with sensible defaults for this project's data shape
(daily granularity, category-driven seasonality, ~2 years of history).
"""

from prophet import Prophet
import pandas as pd
import logging

# Prophet is noisy by default (cmdstanpy INFO logs) — quiet it down
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
logging.getLogger("prophet").setLevel(logging.WARNING)


def fit_prophet_model(demand_df, weekly_seasonality=True, yearly_seasonality=True):
    """
    demand_df: DataFrame with columns ['ds', 'y']
    Returns a fitted Prophet model.
    """
    model = Prophet(
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=weekly_seasonality,
        daily_seasonality=False,
        seasonality_mode="multiplicative",  # demand scales with level, matches Phase 1's generation logic
        interval_width=0.90,
    )
    model.fit(demand_df)
    return model


def forecast_future(model, periods=30, freq="D"):
    """
    Generates a forecast `periods` days beyond the training data.
    Returns the full Prophet forecast DataFrame (includes yhat,
    yhat_lower, yhat_upper, and historical fitted values).
    """
    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)
    return forecast


if __name__ == "__main__":
    from data_loader import get_all_product_ids, get_demand_for_product

    product_id = get_all_product_ids()[0]
    demand_df = get_demand_for_product(product_id)

    print(f"Fitting Prophet model for {product_id}...")
    model = fit_prophet_model(demand_df)
    forecast = forecast_future(model, periods=30)

    print("\nForecast for next 5 days:")
    print(forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(5))