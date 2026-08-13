Most supply chain teams find out a supplier is unreliable after a shipment is already late.



I built a system that tries to catch that earlier — an AI-powered supply chain "control tower" that forecasts demand, scores supplier risk from real delivery behavior, and turns both into actual inventory decisions backed by numbers instead of gut feel.



\*\*What it does, in plain terms:\*\*

It predicts what customers will buy over the next two months, figures out which suppliers are likely to cause problems based on their actual track record (not just a gut feeling), and calculates exactly how much extra stock is worth holding to protect against that risk — then stress-tests the whole plan against 2,400 simulated disruption scenarios to see if it actually holds up.



\*\*A bug that taught me more than the feature that worked:\*\*

When I first compared my AI-optimized ordering policy against a simple baseline, the AI version looked dramatically worse — 20x more expensive. That didn't make sense, so I dug in. Turned out my baseline was quietly assuming every order arrives instantly, while the optimized model was correctly accounting for real supplier lead times. I'd built an unfair comparison without realizing it.



Once I fixed the baseline to face the same reality, the real result showed up: the smarter policy does cost more — about 15% more — but that extra cost is concentrated almost entirely on the riskiest suppliers. I confirmed this with a Monte Carlo simulation across 2,400 trials: the correlation between a supplier's risk score and how much the optimized policy actually helped was 0.46. In other words, the system pays for extra protection exactly where it's needed, and barely spends anything extra where it isn't.



That's the moment this stopped being "a model that runs" and became something I'd actually trust to make a recommendation.



\*\*The results:\*\*

📈 13.3% average forecast error across 40 products (Prophet + SARIMA, validated with rolling-origin cross-validation — not a single lucky train/test split)

⚠️ 79% accuracy, 0.82 ROC-AUC predicting which suppliers are about to become unreliable, using only real delivery history

💰 A quantified, honest tradeoff: 15% more spend for measurably better resilience — not vague reassurance, an actual number

🎲 2,400 simulated disruption scenarios confirming the strategy holds up under pressure, not just in the one scenario it was built for

🤖 An LLM-generated weekly executive briefing that turns all of the above into a plain-language summary a non-technical leader could act on in two minutes



Built end-to-end in Python — synthetic data generation, automated data quality checks, forecasting, machine learning, linear optimization, discrete-event simulation, and GenAI, tied together with both a live interactive app and a published dashboard.



📊 Live dashboard: \[https://public.tableau.com/app/profile/joel.bumba1631/viz/SupplyChainControlTower/Dashboard1]

💻 Full code + methodology write-ups: \[https://github.com/jbx-p/supply-chain-control-tower]



\#SupplyChain #DataScience #Python #MachineLearning #GenAI

