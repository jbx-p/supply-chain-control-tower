# Demand Forecasting Approach — Phase 3

## Overview
Per-SKU demand forecasting for all 40 products in the Global Supply Chain Control Tower, using Prophet as the primary model and a SARIMA (statsmodels) benchmark for comparison. Accuracy is validated with rolling-origin cross-validation rather than a single train/test split, and tracked via MAPE (Mean Absolute Percentage Error).

## Why Prophet as the primary model
- Handles multiple seasonality patterns (weekly + yearly) natively, without manual differencing or seasonal-order tuning
- Robust to missing data and outliers, useful given the injected supplier disruption events from Phase 1
- Configured with `seasonality_mode="multiplicative"`, matching how seasonal demand was generated in Phase 1 (`base * multiplier`, i.e. a percentage of baseline rather than a fixed additive amount)

## Why SARIMA as a benchmark, not the primary model
SARIMA (via `statsmodels.tsa.statespace.sarimax`) provides a classical baseline to sanity-check Prophet's results against — a meaningfully worse Prophet result than SARIMA would flag a configuration problem rather than an inherent forecasting limit. SARIMA requires manual (p,d,q)(P,D,Q,s) order selection and is notably slower to fit at scale (40 products), which is why it's used for comparison rather than as the production model.

## Cross-validation methodology
Standard train/test splits risk evaluating the model on a single, possibly unrepresentative period. Instead, **rolling-origin cross-validation** was used:
- Initial training window: 365 days (a full year, so yearly seasonality can be learned before evaluation)
- Forecast horizon per fold: 30 days (matches a realistic monthly operational re-forecast cadence)
- Step size: 30 days (each fold walks the cutoff forward a month, minimizing overlap between folds)
- This produced **12 folds per product** on ~2 years of history — enough to see whether accuracy is stable across different periods, including the Phase 1 disruption windows.

MAPE was chosen as the primary metric since it's scale-independent and interpretable across products with very different baseline demand levels (a 150-unit/day product and a 25-unit/day product can be compared on the same percentage scale).

## Results

**Overall (40 products, 12 CV folds each):**
- Mean MAPE: 13.34%
- Median MAPE: 12.82%
- Std dev: 3.01%
- Range: 8.67% – 21.92%
- Every product produced a stable estimate (12/12 folds); no product exceeded 50% MAPE; no negative forecast values.

**By category:**

| Category | Mean MAPE | Median MAPE | Std Dev | # Products |
|---|---|---|---|---|
| Staples | 11.72% | 11.49% | 1.91% | 11 |
| Apparel | 12.00% | 11.85% | 1.56% | 16 |
| Electronics | 16.35% | 15.26% | 2.96% | 13 |

**Why electronics forecasts harder than apparel or staples:** this is a direct, explainable consequence of how demand was generated in Phase 1. Electronics carries the sharpest, most concentrated seasonal spike (a large boost confined to November–December only). Apparel's seasonal lift is smaller and spread across four months (March–April, September–October), and staples has no seasonal component at all — just trend and noise. A model has to get both the timing and magnitude of a sharp, narrow spike exactly right to score well on it, so higher error on electronics reflects the underlying demand pattern's difficulty, not a model or pipeline flaw. This was confirmed visually in the forecast-review notebook (`notebooks/03_forecast_review.ipynb`), where the electronics sample product's chart shows a visibly sharper peak than the apparel or staples samples.

## Outputs
Three tables written to the database for downstream phases:
- `demand_forecasts` — 30-day forward forecast per product (`yhat`, `yhat_lower`, `yhat_upper`), trained on full available history. Feeds Phase 5 (inventory optimization).
- `forecast_cv_results` — per-fold MAPE results for every product, for auditability.
- `forecast_accuracy_summary` — per-product aggregate accuracy (mean/median/min/max MAPE, fold count).

## Visual review
`notebooks/03_forecast_review.ipynb` plots actual demand history against the forecast (full history and a zoomed recent-history view) for a representative (median-MAPE) product from each category, plus a boxplot of MAPE distribution by category. Used to confirm the model captures seasonal shape correctly and isn't systematically biased, beyond what the MAPE number alone shows.
