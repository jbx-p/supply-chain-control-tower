\# Network \& Inventory Optimization Approach — Phase 5



\## Overview

A per-product linear program (PuLP) that decides how much to order right now, minimizing total cost (holding + stockout + ordering) subject to a risk-adjusted safety stock requirement, using Phase 3's demand forecasts and Phase 4's supplier risk scores as direct inputs.



\## LP formulation

For each product, given a forecast horizon of demand `d\[1..H]`, current on-hand inventory `I0`, and a risk-adjusted lead time `L`:



\- \*\*Decision variable:\*\* `Q` — order quantity placed today

\- \*\*Auxiliary variables:\*\* `stockout\_before` (unmet demand before the order arrives), `stockout\_after` (unmet demand after arrival), `ending\_inventory`

\- \*\*Objective:\*\* minimize `holding\_cost × avg\_inventory × H + stockout\_cost × (stockout\_before + stockout\_after) + order\_cost × Q`

\- \*\*Constraints:\*\*

&#x20; - `stockout\_before ≥ demand\_before\_arrival − I0`

&#x20; - `ending\_inventory = I0 − demand\_before\_arrival + stockout\_before + Q − demand\_after\_arrival + stockout\_after`

&#x20; - `ending\_inventory ≥ safety\_stock\_target` (service-level floor)



\## How Phase 3 and Phase 4 feed into this model

\- \*\*Lead time is inflated by supplier risk score:\*\* `lead\_time\_adjusted = base\_lead\_time × (1 + risk\_score/100 × 0.5)`. A supplier scored 87/100 risk sees its 20-day lead time treated as 28.7 days — the optimizer plans for the supplier being slower and less certain, not just its nominal contracted lead time.

\- \*\*Safety stock is derived from the forecast's own uncertainty interval\*\* (`yhat\_upper − yhat`), scaled further by risk score. This ties the size of the safety buffer directly to how uncertain the demand forecast is for that specific product, and how risky its supplier is — rather than a flat, arbitrary percentage.



\## Cost assumptions

\- Holding cost: 20% annual carrying cost, standard industry rule of thumb

\- Stockout cost: lost margin (unit price − unit cost) per unfulfilled unit — deliberately conservative, not full retail price

\- Order cost: 2% of unit cost per unit ordered



\## Naive baseline

A simple reorder policy: order enough to cover demand for the remainder of the horizon after lead time, plus a flat 10% margin — no risk-adjustment, no cost-minimized safety stock target, no consideration of \*which\* supplier is riskier.



\*\*An earlier version of the naive baseline assumed instant order arrival (no lead-time modeling at all).\*\* This was caught and corrected during development — it made the comparison meaningless, since it let the naive policy avoid pre-arrival stockout entirely while the optimized policy correctly accounted for it. The corrected naive baseline uses the same lead-time exposure, just without risk-adjustment or cost optimization, making the comparison fair.



\## Results and a key structural finding



\*\*Cost comparison (60-day horizon, after fixing the naive baseline):\*\*

\- Naive policy total cost: $6,262,377.62

\- Optimized policy total cost: $7,218,002.98

\- Difference: optimized costs \~15.3% more



\*\*This is not a failure of the optimization — it's an honest, quantifiable finding about a structural limitation of the single-order model.\*\* Breaking stockout into its two components (`stockout\_before\_arrival` vs. `stockout\_after\_arrival`) reveals:

\- \*\*`stockout\_after\_arrival` is 0 for every product.\*\* Once the order arrives, the optimizer manages inventory with zero stockout for the remainder of the horizon, in every single case — full success on the part of the problem the model can actually control.

\- \*\*`stockout\_before\_arrival` accounts for essentially all stockout in the model\*\*, and scales directly with each product's lead time. This is mathematically unavoidable in a single-order model: if starting inventory is low and lead time is long (some risk-adjusted lead times exceed 45 days), that much demand physically cannot be met before the first order can possibly arrive — no amount of optimization changes that, because the model only allows one order per horizon.

\- Since both the naive and optimized policies share the same starting inventory and lead time, this pre-arrival gap is a \*\*shared cost baked equally into both comparisons\*\* — it doesn't invalidate the cost comparison, it explains why the "savings" number alone is an incomplete/misleading measure of the optimizer's value.

\- The real, interpretable finding: \*\*the optimizer's \~15% cost premium is the quantifiable price of a risk-adjusted safety buffer\*\* that the naive 10%-flat-margin policy simply doesn't provide — a legitimate cost-vs-resilience tradeoff, not wasted spend.



\## Known limitation and natural next step

The single-order-per-horizon structure is a real modeling simplification, stated as an assumption from the outset (Step 1). It cannot prevent stockout that occurs before the first order arrives when starting inventory is low relative to lead time. \*\*A natural extension\*\* — not built in this phase, but a clear direction for future work — would be a multi-period/rolling-reorder LP that allows periodic ordering throughout the horizon rather than a single decision, which would eliminate the pre-arrival stockout gap entirely and let the safety-stock/risk-adjustment logic operate across the full horizon rather than just after the first arrival.



\## Output

Two tables written to the database:

\- `inventory\_optimization\_results` — per-product optimized order quantity, cost breakdown, and stockout components

\- `optimization\_vs\_naive\_comparison` — cost and stockout comparison against the (corrected) naive baseline



\## Debugging notes worth keeping

Two real issues were found and fixed during this phase, both worth being able to discuss:

1\. \*\*An unfair naive baseline\*\* (assumed instant delivery) initially made the optimized policy look dramatically worse than it was — caught by noticing the cost gap was implausibly large (-2142%) and tracing it to the baseline ignoring lead time entirely.

2\. \*\*A forecast-horizon/lead-time mismatch\*\*: the initial 30-day forecast horizon was shorter than several suppliers' risk-adjusted lead times, forcing the entire horizon into "before arrival" for those products. Fixed by extending Phase 3's forecast horizon to 60 days so lead times fit within the planning window.

