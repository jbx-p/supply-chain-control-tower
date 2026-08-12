\# Tableau Public Dashboard Approach — Phase 9



\## Live dashboard

📊 https://public.tableau.com/app/profile/joel.bumba1631/viz/SupplyChainControlTower/Dashboard1



\## Purpose

A single-screen, published, publicly shareable executive dashboard — complementing the Streamlit app (Phase 8) with a format some stakeholders expect by default: a traditional BI dashboard with no local setup required to view it.



\## Data pipeline

Since Tableau Public doesn't support a shareable live connection to a local SQLite database, `src/app/export\_for\_tableau.py` exports 4 curated, denormalized CSV files (`demand\_summary.csv`, `supplier\_risk.csv`, `optimization\_comparison.csv`, `simulation\_results.csv`) that Tableau connects to directly.



\## Dashboard contents

\- \*\*4 KPI cards\*\* (top row): Avg Forecast Accuracy (13.5% MAPE), High-Risk Suppliers (2), Total Optimized Inventory Cost ($7.2M), Avg. Simulated Service Level (92.2%) — matching the same top-line metrics shown on the Streamlit app's Home page, so both front-ends tell a consistent story

\- \*\*Demand Trend by Category\*\* — one line per product category, showing forecasted demand shape

\- \*\*Supplier Risk\*\* — horizontal bar chart of all 12 suppliers' risk scores, color-coded by tier (red/orange/green for High/Medium/Low)

\- \*\*Cost Comparison\*\* — optimized vs. naive policy cost, grouped by category

\- \*\*Risk vs. Resilience Improvement\*\* — scatter plot with a linear trend line, the direct visual form of Phase 6's r≈0.46 finding that risk-adjusted safety stock disproportionately benefits high-risk-supplier products



\## Design decisions

\- \*\*Risk-tier colors (red/orange/green) were manually matched\*\* to the same scheme used in the Streamlit app's Plotly charts, so the two front-ends feel like one coherent project rather than two disconnected pieces.

\- \*\*The MAPE KPI uses a FIXED-level-of-detail calculation\*\* (`{FIXED \[Product Id] : AVG(\[Mean Mape])}`) rather than a plain average, since the underlying export has each product's MAPE repeated across 60 forecast-day rows — a plain average would coincidentally give the right answer only because every product has an equal row count, which is fragile. The LOD expression computes the correct per-product average regardless of row count.

\- \*\*The risk/resilience trend line's correlation value is hardcoded in the chart title\*\* (r ≈ 0.46) rather than dynamically computed within Tableau, since that value was already calculated and verified in Phase 6's Python analysis — Tableau's trend line does compute its own R² independently (viewable via right-click → Describe Trend Line), which was used to cross-check consistency with the Python-derived figure.



\## A bug caught during development

An early version of the Supplier Risk chart had Medium and Low risk-tier colors swapped (Medium showing green, Low showing orange) — caught by comparing the chart against the known Phase 4 results before publishing, rather than assuming the color assignment was correct. Fixed via Edit Colors on the Risk Tier legend.



\## Output

Published, publicly accessible via the link above — no login or local setup required to view.

