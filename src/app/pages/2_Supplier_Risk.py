"""
2_Supplier_Risk.py
Supplier risk score overview with tier-based visual coding.
"""

import sys
import os
import streamlit as st
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db_utils import load_table

st.set_page_config(page_title="Supplier Risk", layout="wide")
st.title("⚠️ Supplier Risk Scoring")

risk = load_table("supplier_risk_scores").sort_values("risk_score", ascending=False)

col1, col2, col3 = st.columns(3)
col1.metric("High Risk Suppliers", (risk["risk_tier"] == "High").sum())
col2.metric("Medium Risk Suppliers", (risk["risk_tier"] == "Medium").sum())
col3.metric("Low Risk Suppliers", (risk["risk_tier"] == "Low").sum())

st.divider()

fig = px.bar(
    risk, x="risk_score", y="supplier_id", orientation="h",
    color="risk_tier",
    color_discrete_map={"High": "#d62728", "Medium": "#ff7f0e", "Low": "#2ca02c"},
    hover_data=["name", "country"],
    title="Supplier Risk Scores (0-100)",
)
fig.update_layout(height=500, yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Full Supplier Risk Table")
st.dataframe(
    risk[["supplier_id", "name", "country", "risk_score", "risk_tier", "reliability_base"]],
    use_container_width=True, hide_index=True,
)