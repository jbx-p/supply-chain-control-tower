"""
optimizer.py
Solves a single-order inventory optimization LP for one product:
how much to order right now to minimize total cost (holding +
stockout + ordering) over the forecast horizon, given a risk-adjusted
lead time and a safety stock requirement.
"""

import pulp
import numpy as np

from cost_model import (
    daily_holding_cost, stockout_cost_per_unit, order_cost_per_unit,
    risk_adjusted_lead_time, safety_stock_buffer,
)


def optimize_product(product_input):
    """
    product_input: dict from data_loader.build_product_input()
    Returns a dict with the recommended order quantity and cost breakdown.
    """
    unit_cost = product_input["unit_cost"]
    unit_price = product_input["unit_price"]
    on_hand = product_input["on_hand"]
    demand = product_input["demand"]
    demand_upper = product_input["demand_upper"]
    risk_score = product_input["supplier_risk_score"]

    horizon = len(demand)
    lead_time = risk_adjusted_lead_time(product_input["base_lead_time"], risk_score)
    lead_time_days = min(int(round(lead_time)), horizon)  # cap at horizon length

    demand_before_arrival = float(np.sum(demand[:lead_time_days]))
    demand_after_arrival = float(np.sum(demand[lead_time_days:]))

    safety_stock = safety_stock_buffer(demand_upper, demand, risk_score)

    h_cost = daily_holding_cost(unit_cost)
    s_cost = stockout_cost_per_unit(unit_cost, unit_price)
    o_cost = order_cost_per_unit(unit_cost)

    # --- Build the LP ---
    prob = pulp.LpProblem(f"inventory_opt_{product_input['product_id']}", pulp.LpMinimize)

    Q = pulp.LpVariable("order_quantity", lowBound=0)
    stockout_before = pulp.LpVariable("stockout_before_arrival", lowBound=0)
    stockout_after = pulp.LpVariable("stockout_after_arrival", lowBound=0)
    ending_inventory = pulp.LpVariable("ending_inventory", lowBound=0)

    inv_before_arrival = on_hand - demand_before_arrival + stockout_before
    inv_after_arrival = inv_before_arrival + Q

    # ending_inventory reflects demand consumed after arrival, net of any further stockout
    prob += ending_inventory == inv_after_arrival - demand_after_arrival + stockout_after
    prob += stockout_before >= demand_before_arrival - on_hand
    prob += stockout_after >= demand_after_arrival - inv_after_arrival

    # service-level constraint: end the horizon with at least the safety stock buffer
    prob += ending_inventory >= safety_stock

    # objective: minimize holding + stockout + ordering cost
    avg_inventory = (inv_before_arrival + ending_inventory) / 2
    total_holding_cost = h_cost * avg_inventory * horizon
    total_stockout_cost = s_cost * (stockout_before + stockout_after)
    total_order_cost = o_cost * Q

    prob += total_holding_cost + total_stockout_cost + total_order_cost

    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    return {
        "product_id": product_input["product_id"],
        "status": pulp.LpStatus[prob.status],
        "order_quantity": round(Q.varValue, 1) if Q.varValue is not None else None,
        "risk_adjusted_lead_time_days": round(lead_time, 1),
        "safety_stock_target": round(safety_stock, 1),
        "stockout_units_before_arrival": round(stockout_before.varValue, 1),
        "stockout_units_after_arrival": round(stockout_after.varValue, 1),
        "ending_inventory": round(ending_inventory.varValue, 1),
        "total_cost": round(pulp.value(prob.objective), 2),
    }


if __name__ == "__main__":
    from data_loader import get_optimization_inputs, build_product_input

    products, inventory, forecast = get_optimization_inputs()
    product_id = products["product_id"].iloc[0]
    product_input = build_product_input(product_id, products, inventory, forecast)

    result = optimize_product(product_input)
    print(f"Optimization result for {product_id}:\n")
    for k, v in result.items():
        print(f"  {k}: {v}")