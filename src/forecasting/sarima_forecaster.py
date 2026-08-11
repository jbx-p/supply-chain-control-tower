"""
sarima_forecaster.py
SARIMA benchmark model via statsmodels — a simpler, classical baseline
to compare Prophet's performance against.
"""

import warnings
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")  # SARIMA emits convergence warnings that are usually harmless


def fit_sarima_model(demand_df, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7)):
    """
    demand_df: DataFrame with columns ['ds', 'y'], indexed by date
    order: (p, d, q) — non-seasonal ARIMA terms
    seasonal_order: (P, D, Q, s) — seasonal terms, s=7 for weekly seasonality
    """
    series = demand_df.set_index("ds")["y"]
    model = SARIMAX(
        series,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    fitted = model.fit(disp=False)
    return fitted


def forecast_sarima(fitted_model, periods=30):
    forecast = fitted_model.get_forecast(steps=periods)
    forecast_df = forecast.summary_frame()
    return forecast_df


if __name__ == "__main__":
    from data_loader import get_all_product_ids, get_demand_for_product

    product_id = get_all_product_ids()[0]
    demand_df = get_demand_for_product(product_id)

    print(f"Fitting SARIMA model for {product_id}...")
    fitted = fit_sarima_model(demand_df)
    forecast_df = forecast_sarima(fitted, periods=30)

    print("\nForecast for next 5 days:")
    print(forecast_df[["mean", "mean_ci_lower", "mean_ci_upper"]].head(5))