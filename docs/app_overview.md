\# Streamlit App Overview — Phase 8



\## Purpose

A 6-page interactive Streamlit app that ties together every prior phase's output into one non-technical-friendly interface — the first version of this project that can be demoed live rather than described.



\## Pages



\*\*Home\*\* — Top-line KPI summary (mean forecast MAPE, high-risk supplier count, total optimized inventory cost, average simulated service level), pulling live from the database rather than hardcoded values.



\*\*Demand Forecast Explorer\*\* — Category and product filters, a chart overlaying actual demand history with the forecast and its uncertainty interval, plus a sortable accuracy table across all 40 products (Phase 3).



\*\*Supplier Risk Scoring\*\* — Tier counts (High/Medium/Low) and a color-coded horizontal bar chart of all 12 suppliers' risk scores, plus the full detail table (Phase 4).



\*\*Inventory Optimization\*\* — Cost comparison (optimized vs. naive baseline) and an interactive \*\*what-if risk-tolerance slider\*\*: selecting a product and adjusting the slider live-recalculates the safety stock buffer using the same formula from Phase 5's cost model, letting a user explore sensitivity without touching code (Phase 5).



\*\*Disruption Simulation\*\* — A box plot comparing service-level distributions across 2,400 Monte Carlo trials for both policies, and a scatter plot (with trendline) of supplier risk score vs. service-level improvement — the visual form of the r=0.46 correlation finding from Phase 6.



\*\*Executive Briefing\*\* — Displays the most recent GenAI-generated briefing (Phase 7), with a "Generate New Briefing" button that calls the live OpenRouter/Claude API on demand and refreshes the page with fresh output.



\## Technical notes

\- All data access goes through a shared, cached (`@st.cache\_data`, 5-minute TTL) module (`db\_utils.py`) — necessary because Streamlit re-runs the entire script on every user interaction, so uncached queries would hit the database on every click.

\- Charts use Plotly (`plotly.express` / `plotly.graph\_objects`) rather than Streamlit's built-in charting, for interactivity (hover tooltips, zoom) and finer visual control (tier-based color coding, uncertainty bands).

\- The Inventory Optimization page's what-if slider reuses the actual `safety\_stock\_buffer()` function from Phase 5's `cost\_model.py` directly — the interactive result is a genuine recalculation, not a separate approximation.



\## Running it

```powershell

streamlit run src/app/Home.py

```

Opens automatically at `localhost:8501`.



\## Deployment (not done in this phase, but supported)

The app is structured to deploy as-is to \*\*Streamlit Community Cloud\*\* (free tier, connects directly to a GitHub repo) without any code changes — a natural next step for a shareable live link, though not required for the project to be considered complete.

