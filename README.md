# Global Supply Chain Control Tower

An end-to-end, AI-powered supply chain control tower: demand forecasting, supplier risk
scoring, inventory optimization, disruption simulation, and GenAI-generated executive
briefings — built entirely in Python, with both an interactive Streamlit app and a
published Tableau dashboard.

📊 **[Live Tableau Dashboard](https://public.tableau.com/app/profile/joel.bumba1631/viz/SupplyChainControlTower/Dashboard1)**

## The problem
Supply chain teams often find out a supplier is unreliable after a shipment is already
late. This project builds a system that forecasts demand, quantifies supplier risk from
real delivery behavior, and translates both into concrete, cost-justified inventory
decisions — before problems happen, not after.

## What it does
1. **Generates realistic synthetic data** — 40 products, 12 suppliers, 2 years of daily
   demand with category-specific seasonality and deliberately injected supplier disruptions
2. **Validates data quality automatically** — 7 `great_expectations` suites + referential
   integrity checks, one command to verify the whole dataset
3. **Forecasts demand per-SKU** — Prophet + SARIMA benchmark, validated with rolling-origin
   cross-validation (13.34% mean MAPE across 40 products)
4. **Scores supplier risk** — a Gradient Boosting classifier predicting next-month risk
   from real delivery behavior (79% accuracy, 0.816 ROC-AUC)
5. **Optimizes inventory decisions** — a PuLP linear program balancing holding, stockout,
   and ordering costs, with risk-adjusted safety stock
6. **Stress-tests the policy** — a `simpy` Monte Carlo simulation (2,400 trials) confirming
   the optimized policy's benefit concentrates exactly where Phase 4's risk scores predict
   it should (r=0.46 correlation)
7. **Generates executive briefings** — an LLM (via OpenRouter/Claude) synthesizes results
   from every phase into a grounded, plain-language weekly summary
8. **Presents everything two ways** — a 6-page interactive Streamlit app, and a published
   Tableau Public dashboard

## Key results
| Metric | Result |
|---|---|
| Forecast accuracy | 13.34% mean MAPE across 40 products |
| Risk model accuracy | 79% accuracy, 0.816 ROC-AUC |
| Optimized vs. naive cost | +15.3% (the quantified cost of risk-adjusted resilience) |
| Simulated resilience benefit | r=0.46 correlation between supplier risk and service-level improvement |

## Architecture
[Insert a simple diagram here — see Step 3]

## Tech stack
Python · pandas/numpy · SQLAlchemy/SQLite · great_expectations · Prophet · statsmodels ·
scikit-learn · PuLP · simpy · Anthropic Claude (via OpenRouter) · Streamlit · Tableau

## Project structure

## Running it

**Set up:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Generate and validate data:**
```powershell
python src/data_generation/generate_data.py
python src/validation/run_validation.py
```

**Run the full pipeline:**
```powershell
python src/forecasting/run_forecasting.py
python src/risk_scoring/train_model.py
python src/risk_scoring/score_suppliers.py
python src/optimization/run_optimization.py
python src/simulation/run_simulation.py
python src/genai/generate_briefing.py
```

**Launch the interactive app:**
```powershell
streamlit run src/app/Home.py
```

**Run tests:**
```powershell
pytest tests/ -v
```

## Methodology write-ups
Every phase has a detailed methodology doc under `docs/`, including honest discussion of
real bugs found and fixed along the way (an unfair naive baseline, a forecast-horizon/
lead-time mismatch, a lead-time leak between simulated policies, a risk-tier color bug) —
these are linked from each phase's section above, or browse `docs/` directly.

## Author
Joel Bumba — [LinkedIn](your-link) · [GitHub](https://github.com/jbx-p)