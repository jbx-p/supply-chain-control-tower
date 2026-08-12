\# Disruption Simulation Approach — Phase 6



\## Overview

A `simpy` discrete-event Monte Carlo simulation that stress-tests Phase 5's inventory policies under an ongoing reorder regime with randomized supplier disruptions and demand shocks — resolving Phase 5's documented limitation (a single-order LP that couldn't prevent pre-arrival stockout) by allowing continuous reordering across a 180-day simulated horizon.



\## Simulation design

Each product runs as two concurrent `simpy` processes:

\- \*\*Demand/inventory process\*\*: ticks forward one simulated day at a time, consumes randomized daily demand (with a chance of a demand spike), and checks whether inventory has dropped to the reorder point

\- \*\*Supplier delivery process\*\*: triggered whenever a reorder fires; waits a risk-adjusted lead time, with a chance of an additional stochastic disruption delay, then adds stock back to inventory



Two policies were compared, each with its own reorder point and order quantity derived from Phase 5's actual data:

\- \*\*Optimized\*\*: reorder point = expected demand during risk-adjusted lead time + a safety buffer scaled by demand variability and supplier risk score

\- \*\*Naive\*\*: reorder point = expected demand during the un-adjusted (nominal) lead time only, no safety buffer



Both policies were run for 30 Monte Carlo trials each, across all 40 products (2,400 total simulations), with independent random seeds per trial.



\## A bug found and fixed: both policies must face the same reality

An early version of the simulation applied the risk-adjustment to the \*actual simulated lead time\* differently per policy — the optimized policy's simulated deliveries were made to run slower (risk-adjusted) while the naive policy's ran faster (un-adjusted), even though both were meant to represent the same real supplier. This gave the naive policy an artificially easier physical world to operate in, and produced a misleading result where naive appeared to outperform optimized.



The fix: risk-adjusted lead time is now applied identically to \*\*both\*\* policies' actual simulated deliveries, since a supplier's real behavior doesn't change based on which policy is planning around it. Only the \*planning\* parameters (reorder point, order quantity) differ between policies — which is the only thing that should differ. After the fix, the result direction flipped to what theory predicted, and held up under a targeted follow-up check (see below) — strong evidence the bug, not the underlying approach, was producing the earlier misleading numbers.



\## Results



\*\*Overall (2,400 trials, both policies):\*\*



| Policy | Mean service level | p10 service level (worst-case tail) | Mean stockout units | Mean orders placed |

|---|---|---|---|---|

| Naive | 91.97% | 83.21% | 1,454.8 | 28.4 |

| Optimized | 92.24% | 82.96% | 1,421.3 | 28.3 |



The average improvement is real but modest (+0.27 percentage points mean service level), and the worst-case tail is essentially a wash between the two policies at this trial count — worth stating plainly rather than overselling the aggregate number.



\*\*The more informative result is the product-level pattern.\*\* Correlating each product's supplier risk score against its service-level improvement (optimized vs. naive) across all 40 products gives \*\*r = 0.46\*\* — a real, moderate-to-strong positive relationship. The products with the largest improvement (P015, P038, P009, P013, P005, P026 — improvements of 1.0–2.7 percentage points) are concentrated almost entirely among suppliers scored 35.8+ risk by Phase 4, while most near-zero or slightly negative improvements cluster among suppliers scored below 20.



\*\*This is the central finding of the phase:\*\* the risk-adjusted safety stock policy doesn't help uniformly — it helps disproportionately for exactly the suppliers Phase 4 identified as risky, and does little to nothing (as expected) for low-risk suppliers where the extra buffer isn't needed. That's the intended behavior of a risk-adjusted policy working correctly, demonstrated empirically rather than assumed.



\## Why the aggregate improvement is modest despite the strong correlation

With most suppliers in this dataset scored low-risk (median risk score well under 20, per Phase 4), most products don't have much room for the risk-adjusted policy to add value — the naive policy is already close to sufficient for them. The benefit concentrates in a minority of genuinely high-risk-supplier products, which is diluted out in a simple average across all 40. A cost-benefit framing that weights by supplier risk (rather than a flat per-product average) would likely show a clearer picture — a natural next analysis, not built here.



\## Output

Two tables written to the database:

\- `simulation\_trial\_results` — every individual trial's service level, stockout units, orders placed, and disruption events hit (2,400 rows)

\- `simulation\_policy\_comparison` — per-product mean and p10 service level for each policy, with the improvement delta



\## Debugging notes worth keeping

This phase's central lesson mirrors Phase 5's: \*\*a comparison is only as trustworthy as the fairness of what's being compared.\*\* The lead-time leak bug (both policies should face identical physical reality, differing only in what they planned for) produced a directionally wrong result that looked plausible on first read — it was only caught by noticing the result contradicted the reasoning behind the whole project (a risk-adjusted policy performing worse than one that ignores risk doesn't make sense on its face), not by an error message or a crash. That's a useful debugging habit worth naming explicitly: results that "work" but contradict your own design reasoning deserve the same scrutiny as an outright error.

