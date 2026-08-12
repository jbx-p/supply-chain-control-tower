"""
3_Inventory_Optimization.py
Shows optimized vs. naive ordering recommendations, with an
interactive risk-tolerance slider that live-recalculates the safety
stock target — the "what-if" element of this page.
"""

import sys
import os
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db_utils import load_table

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "optimization"))
from cost_model import safety_stock_buffer
from data_loader import get_optimization_inputs, build_product_input

st.set_page_config(page_title="Inventory Optimization", layout="wide")
st.title("📦 Inventory Optimization")

results = load_table("inventory_optimization_results")
comparison = load_table("optimization_vs_naive_comparison")

col1, col2, col3 = st.columns(3)
col1.metric("Optimized Total Cost", f"${comparison['optimized_cost'].sum():,.0f}")
col2.metric("Naive Baseline Cost", f"${comparison['naive_cost'].sum():,.0f}")
col3.metric("Cost Difference", f"${comparison['savings'].sum() * -1:,.0f}",
            help="Positive means the optimized policy costs more — the price of risk-adjusted resilience")

st.divider()

st.subheader("What-If: Adjust Risk Tolerance")
st.caption("See how a different risk sensitivity would change the recommended safety stock for one product.")

products, inventory, forecast = get_optimization_inputs()
selected_product = st.selectbox("Product", sorted(products["product_id"].unique()))
risk_multiplier = st.slider("Risk sensitivity multiplier", 0.5, 3.0, 1.0, 0.1,
                             help="1.0 = current model default. Higher = more conservative (larger safety buffer).")

product_input = build_product_input(selected_product, products, inventory, forecast)
adjusted_safety_stock = safety_stock_buffer(
    product_input["demand_upper"], product_input["demand"], product_input["supplier_risk_score"]
) * risk_multiplier

col1, col2 = st.columns(2)
col1.metric("Adjusted Safety Stock Target", f"{adjusted_safety_stock:,.0f} units")
current_row = results[results["product_id"] == selected_product]
if len(current_row):
    col2.metric("Current Model's Safety Stock Target", f"{current_row['safety_stock_target'].iloc[0]:,.0f} units")

st.divider()
st.subheader("Full Optimization Results — All Products")
st.dataframe(
    results[["product_id", "order_quantity", "risk_adjusted_lead_time_days",
             "safety_stock_target", "total_cost", "status"]].sort_values("total_cost", ascending=False),
    use_container_width=True, hide_index=True,
)