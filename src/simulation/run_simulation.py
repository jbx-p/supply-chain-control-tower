"""
run_simulation.py
Monte Carlo runner: simulates every product under BOTH the optimized
and naive reorder policies, many trials each, and compares service
level and stockout exposure across the trial distribution.

Run:
    python src/simulation/run_simulation.py
"""

import sys
import os
import random
import simpy
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_generation"))
from db import engine

from inventory_sim import InventorySimulation
from policy_loader import get_all_policy_params


N_TRIALS = 30       # Monte Carlo trials per product per policy
SIM_DAYS = 180       # simulate 6 months of ongoing operation
INITIAL_INVENTORY_DAYS = 15  # start with ~15 days of demand on hand


def run_trial(policy_row, policy_type, trial_seed):
    random.seed(trial_seed)
    env = simpy.Environment()
    # Both policies face the SAME real supplier — risk_score reflects
    # actual physical delivery behavior, not what a policy assumed
    # about it. Only the planning parameters (reorder point, order
    # quantity) should differ between policies.
    risk_score = policy_row["risk_score"]

    if policy_type == "optimized":
        reorder_point = policy_row["optimized_reorder_point"]
        order_qty = policy_row["optimized_order_qty"]
    else:
        reorder_point = policy_row["naive_reorder_point"]
        order_qty = policy_row["naive_order_qty"]
	



    initial_inventory = policy_row["daily_demand_mean"] * INITIAL_INVENTORY_DAYS

    sim = InventorySimulation(
        env, product_id=policy_row["product_id"],
        initial_inventory=initial_inventory,
        daily_demand_mean=policy_row["daily_demand_mean"],
        daily_demand_std=policy_row["daily_demand_std"],
        reorder_point=reorder_point,
        order_quantity=order_qty,
        base_lead_time=policy_row["base_lead_time"],
        risk_score=risk_score,
        sim_days=SIM_DAYS,
    )
    env.run(until=SIM_DAYS)

    return {
        "product_id": policy_row["product_id"],
        "policy": policy_type,
        "trial": trial_seed,
        "service_level": sim.service_level,
        "total_stockout_units": sim.total_stockout_units,
        "orders_placed": sim.orders_placed,
        "disruption_events": sim.disruption_events,
    }


def run_all_simulations():
    policy_params = get_all_policy_params()
    all_results = []

    print(f"Running {N_TRIALS} trials x 2 policies x {len(policy_params)} products "
          f"= {N_TRIALS * 2 * len(policy_params)} total simulations...\n")

    for i, (_, policy_row) in enumerate(policy_params.iterrows(), 1):
        for policy_type in ["optimized", "naive"]:
            for trial in range(N_TRIALS):
                # unique, reproducible seed per (product, policy, trial)
                seed = hash((policy_row["product_id"], policy_type, trial)) % (2**31)
                result = run_trial(policy_row, policy_type, seed)
                all_results.append(result)

        if i % 10 == 0 or i == len(policy_params):
            print(f"  [{i}/{len(policy_params)}] products simulated")

    results_df = pd.DataFrame(all_results)
    results_df.to_sql("simulation_trial_results", engine, if_exists="replace", index=False)

    print(f"\n✅ {len(results_df)} total trials saved to database.")
    return results_df


if __name__ == "__main__":
    run_all_simulations()