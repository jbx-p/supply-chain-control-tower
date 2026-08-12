"""
Home.py
Landing page for the Global Supply Chain Control Tower app — a
top-line KPI summary linking out to each detailed page.

Run:
    streamlit run src/app/Home.py
"""

import streamlit as st
from db_utils import load_table

st.set_page_config(page_title="Supply Chain Control Tower", layout="wide")

st.title("🌐 Global Supply Chain Control Tower")
st.markdown("AI-powered demand sensing, supplier risk scoring, inventory optimization, "
            "and disruption resilience — all in one place.")

st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    accuracy = load_table("forecast_accuracy_summary")
    st.metric("Mean Forecast Error (MAPE)", f"{accuracy['mean_mape'].mean():.1f}%")

with col2:
    risk = load_table("supplier_risk_scores")
    high_risk_count = (risk["risk_tier"] == "High").sum()
    st.metric("High-Risk Suppliers", high_risk_count, delta=None)

with col3:
    comparison = load_table("optimization_vs_naive_comparison")
    total_cost = comparison["optimized_cost"].sum()
    st.metric("Total Optimized Inventory Cost", f"${total_cost:,.0f}")

with col4:
    sim = load_table("simulation_policy_comparison")
    avg_service = sim["mean_service_level_optimized"].mean() * 100
    st.metric("Avg. Simulated Service Level", f"{avg_service:.1f}%")

st.divider()

st.markdown("""
### Navigate using the sidebar:
- **📈 Demand Forecast** — per-product demand trends and forecast accuracy
- **⚠️ Supplier Risk** — current risk scores and tiers across all suppliers
- **📦 Inventory Optimization** — recommended order quantities and cost tradeoffs
- **🎲 Disruption Simulation** — Monte Carlo resilience testing results
- **📋 Executive Briefing** — the latest AI-generated summary
""")