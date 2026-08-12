# Global Supply Chain Control Tower

An AI-powered supply chain control tower: demand sensing, supplier risk scoring,
inventory/network optimization, disruption simulation, and GenAI-generated
executive briefings — built end-to-end in Python.

## Status
🚧 In progress — Phase 6 (disruption simulation) complete.

## Progress
- ✅ Phase 0 — Environment & Foundation Setup
- ✅ Phase 1 — Data Architecture & Synthetic Dataset Generation
- ✅ Phase 2 — Automated Data Quality & Validation Pipeline
- ✅ Phase 3 — Demand Sensing & Forecasting Engine (Prophet + SARIMA, mean MAPE 13.34%)
- ✅ Phase 4 — Supplier Risk Scoring Model (GBM classifier, 0–100 risk scores)
- ✅ Phase 5 — Network & Inventory Optimization Engine (PuLP LP, risk-adjusted safety stock)
- ✅ Phase 6 — Disruption Simulation Engine (simpy Monte Carlo, risk-correlation r=0.46)
- ⬜ Phase 7 — GenAI Executive Briefing Generator
- ⬜ Phase 8 — Streamlit Interactive Control Tower App
- ⬜ Phase 9 — Tableau Public Executive Dashboard
- ⬜ Phase 10 — Testing, Documentation & Portfolio Packaging

## Regenerating and validating the data
```powershell
python src/data_generation/generate_data.py
python src/validation/run_validation.py
```

## Running the forecasting pipeline
```powershell
python src/forecasting/run_forecasting.py
python src/forecasting/sanity_check.py
```

## Running the risk scoring pipeline
```powershell
python src/risk_scoring/train_model.py
python src/risk_scoring/score_suppliers.py
```