"""
1_Demand_Forecast.py
Interactive per-product demand forecast viewer.
"""

import sys
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db_utils import load_table, load_query

st.set_page_config(page_title="Demand Forecast", layout="wide")
st.title("📈 Demand Forecast Explorer")

products = load_table("products")
accuracy = load_table("forecast_accuracy_summary")

col1, col2 = st.columns([1, 3])
with col1:
    category_filter = st.selectbox("Category", ["All"] + sorted(products["category"].unique().tolist()))
    filtered_products = products if category_filter == "All" else products[products["category"] == category_filter]
    product_id = st.selectbox("Product", sorted(filtered_products["product_id"].tolist()))

    product_accuracy = accuracy[accuracy["product_id"] == product_id]
    if len(product_accuracy):
        st.metric("Forecast MAPE", f"{product_accuracy['mean_mape'].iloc[0]:.1f}%")

with col2:
    history = load_query(
        "SELECT date, units_sold FROM demand_history WHERE product_id = ? ORDER BY date",
        params=(product_id,)
    )
    forecast = load_query(
        "SELECT ds, yhat, yhat_lower, yhat_upper FROM demand_forecasts WHERE product_id = ? ORDER BY ds",
        params=(product_id,)
    )
    history["date"] = pd.to_datetime(history["date"])
    forecast["ds"] = pd.to_datetime(forecast["ds"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=history["date"].tail(180), y=history["units_sold"].tail(180),
                              name="Actual (last 180 days)", line=dict(color="steelblue")))
    fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat"],
                              name="Forecast", line=dict(color="darkorange")))
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast["ds"], forecast["ds"][::-1]]),
        y=pd.concat([forecast["yhat_upper"], forecast["yhat_lower"][::-1]]),
        fill="toself", fillcolor="rgba(255,165,0,0.2)", line=dict(color="rgba(255,255,255,0)"),
        name="Uncertainty interval", showlegend=True,
    ))
    fig.update_layout(title=f"{product_id} — Demand History & Forecast",
                       xaxis_title="Date", yaxis_title="Units Sold", height=500)
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Forecast Accuracy — All Products")
accuracy_with_category = accuracy.merge(products[["product_id", "category"]], on="product_id")
st.dataframe(
    accuracy_with_category[["product_id", "category", "mean_mape", "n_folds"]].sort_values("mean_mape"),
    use_container_width=True, hide_index=True,
)