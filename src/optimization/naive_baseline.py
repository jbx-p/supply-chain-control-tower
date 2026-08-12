"""
naive_baseline.py
A simple reorder policy — no cost optimization, no risk adjustment —
but IS lead-time aware, so the comparison against the optimized
policy is fair. (An earlier version assumed instant delivery, which
silently hid the real cost of lead-time exposure and made the
comparison meaningless — see docs/optimization_approach.md.)
"""

import numpy as np

from cost_model import (
    daily_holding_cost, stockout_cost_per_unit, order_cost_per_unit,
)


def evaluate_naive_policy(product_input):
    on_hand = product_input["on_hand"]
    demand = product_input["demand"]
    unit_cost = product_input["unit_cost"]
    unit_price = product_input["unit_price"]
    lead_time = product_input["base_lead_time"]  # NOT risk-adjusted — that's the optimizer's edge

    horizon = len(demand)
    lead_time_days = min(int(round(lead_time)), horizon)

    demand_before_arrival = float(np.sum(demand[:lead_time_days]))
    demand_after_arrival = float(np.sum(demand[lead_time_days:]))

    # naive: order enough to cover the REST of the horizon, +10% margin,
    # with no risk-adjustment and no cost-minimized safety stock
    order_qty = max(0, demand_after_arrival * 1.10)

    stockout_before = max(0, demand_before_arrival - on_hand)
    inv_after_arrival = max(0, on_hand - demand_before_arrival) + order_qty
    ending_inventory = inv_after_arrival - demand_after_arrival
    stockout_after = max(0, -ending_inventory)
    ending_inventory = max(0, ending_inventory)

    h_cost = daily_holding_cost(unit_cost)
    s_cost = stockout_cost_per_unit(unit_cost, unit_price)
    o_cost = order_cost_per_unit(unit_cost)

    avg_inventory = (max(0, on_hand - demand_before_arrival) + ending_inventory) / 2
    total_cost = (
        (h_cost * avg_inventory * horizon)
        + (s_cost * (stockout_before + stockout_after))
        + (o_cost * order_qty)
    )

    return {
        "product_id": product_input["product_id"],
        "naive_order_quantity": round(order_qty, 1),
        "naive_total_cost": round(total_cost, 2),
    }