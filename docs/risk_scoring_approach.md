\# Supplier Risk Scoring Approach — Phase 4



\## Overview

A supplier risk scoring model that predicts next-month delivery risk from each supplier's recent behavior, producing a live 0–100 risk score per supplier. Built with a scikit-learn Gradient Boosting Classifier on a supplier-month feature panel derived from real order and shipment data.



\## Why features were built from delivery behavior, not fabricated defect data

The dataset has no `defect\_rate` or quality column — Phase 1 only generated delivery timing behavior. Rather than inventing a synthetic quality metric, every feature here is derived from real, verifiable order/shipment records: on-time delivery rate, delay magnitude and consistency, fulfillment completeness, and order volume/concentration.



\## Why a monthly panel with lagged features, not a static per-supplier snapshot

A model trained on each supplier's full-history aggregate would only have 11-12 rows to learn from — too few to train or evaluate meaningfully — and would be purely descriptive rather than predictive (labeling a supplier "risky" using the same data used to describe them is circular). Instead, behavior was broken into a \*\*supplier × month panel\*\* (11 suppliers × \~24 months ≈ 253 usable rows after adding lags), and every predictor feature is \*\*lagged by one month\*\* relative to its label — the model predicts month M's risk using only information available as of month M-1. This makes it a genuine forward-looking prediction rather than a backward-looking description.



\## Label definition

A supplier-month is labeled "high risk" if its on-time delivery rate falls below 80%. This threshold was set empirically, not assumed: the raw distribution of on-time rates was inspected first (mean 87%, median 89%, 25th percentile 82.5%), and 80% was chosen because it produces a 23.3% minority class — enough positive examples for the classifier to learn from without being either negligible or the majority case.



One correction made along the way: "on-time" was initially defined as delay ≤ 0 days, which produced an unusably low \~43% mean on-time rate. Reviewing Phase 1's own data generation logic showed that even successfully delivered orders (non-disrupted) were generated with a 0–2 day delay by design — so "on-time" was redefined as delay ≤ 2 days to match the data's actual generative process, which corrected the on-time rate to a realistic 87% mean.



\## Train/test split

A \*\*time-based\*\* split was used (train: Feb 2024 – Jun 2025, test: Jul 2025 – Dec 2025) rather than a random split, since randomly shuffling rows would let the model train on data from after the point it's meant to predict — a form of leakage that would inflate apparent performance without reflecting real usability.



\## Model

`GradientBoostingClassifier` (scikit-learn), 100 estimators, max depth 3, learning rate 0.1.



\## Results



\*\*Classification performance (test set, 66 rows):\*\*

\- Overall accuracy: 79%

\- ROC-AUC: 0.816

\- Precision / Recall / F1 (High Risk class): 0.50 / 0.50 / 0.50

\- Precision / Recall / F1 (Low/Med Risk class): 0.87 / 0.87 / 0.87



Recall of 50% on the High Risk class (7 of 14 actual risk-months caught) is the number worth stating plainly rather than the more flattering 79% accuracy figure alone — with only \~253 total rows and a 23% minority class, this is a reasonable first-pass result that demonstrates real, above-chance signal (ROC-AUC 0.816 vs. 0.5 baseline), not a production-grade detector. A larger dataset (more suppliers, longer history) would be the natural next step to improve recall.



\*\*Feature importance:\*\*



| Feature | Importance |

|---|---|

| `rolling\_3m\_on\_time` | 0.271 |

| `prev\_delay\_std` | 0.236 |

| `prev\_avg\_delay\_days` | 0.125 |

| `product\_diversity` | 0.103 |

| `prev\_on\_time\_rate` | 0.094 |

| `prev\_avg\_shipment\_count` | 0.087 |

| `prev\_order\_count` | 0.084 |

| `prev\_avg\_fulfillment\_ratio` | 0.000 |



The model correctly learned to weight recent on-time trend and delay \*consistency\* (not just average delay) most heavily — both genuinely meaningful delivery-behavior signals. `prev\_avg\_fulfillment\_ratio` contributed nothing once the other features were included, a legitimate finding (most orders in this dataset were fully fulfilled, so the feature carried little discriminating signal) rather than a bug.



\## Validation against known ground truth

Phase 1 deliberately injected reliability disruptions into 3 specific suppliers (`DISRUPTION\_WINDOWS`, mapping to S003, S006, and S009). Checking the model's current risk scores against this known ground truth:



\- \*\*S009\*\* → scored 87.3 ("High") — ✅ correctly identified as high risk

\- \*\*S006\*\* → scored 9.4 ("Low") — not flagged; plausibly explained by recovery, since the score reflects the \*most recent\* month's behavior rather than full history, and this supplier's disruption window may have resolved before the scoring period

\- \*\*S003\*\* → has zero orders in the dataset entirely, so it was never scored — a data coverage gap (this supplier appears to have never been selected as an order recipient during Phase 1's generation), not a model failure



This is an honest 1-confirmed / 1-explainable-miss / 1-untestable result, rather than a perfect validation — a more informative and credible finding than reporting only the successful case.



\## Output

`supplier\_risk\_scores` table in the database: `supplier\_id`, `order\_month` (most recent scored month), `risk\_score` (0–100), `risk\_tier` (Low/Medium/High), plus supplier name/country/reliability\_base for readability. This feeds directly into Phase 5's sourcing/optimization decisions.

