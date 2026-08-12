"""
4_Disruption_Simulation.py
Monte Carlo simulation results — policy comparison and the
risk-score-vs-improvement relationship found in Phase 6.
"""

import sys
import os
import streamlit as st
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db_utils import load_table, load_query

st.set_page_config(page_title="Disruption Simulation", layout="wide")
st.title("🎲 Disruption Simulation")

trials = load_table("simulation_trial_results")
policy_comparison = load_table("simulation_policy_comparison")

col1, col2 = st.columns(2)
with col1:
    fig = px.box(trials, x="policy", y="service_level", color="policy",
                 title="Service Level Distribution Across Trials",
                 color_discrete_map={"optimized": "#2ca02c", "naive": "#d62728"})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    risk_scores = load_query("""
        SELECT ps.product_id, r.risk_score
        FROM product_suppliers ps
        JOIN supplier_risk_scores r ON ps.supplier_id = r.supplier_id
        WHERE ps.is_primary = 1
    """)
    merged = policy_comparison.merge(risk_scores, on="product_id")
    fig2 = px.scatter(merged, x="risk_score", y="service_level_improvement",
                       trendline="ols",
                       title=f"Risk Score vs. Service Level Improvement "
                             f"(r = {merged['risk_score'].corr(merged['service_level_improvement']):.2f})",
                       hover_data=["product_id"])
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.subheader("Per-Product Policy Comparison")
st.dataframe(
    policy_comparison.sort_values("service_level_improvement", ascending=False),
    use_container_width=True, hide_index=True,
)