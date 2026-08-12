"""
cost_model.py
Defines the cost assumptions and the risk-adjusted lead time logic
that feed the optimizer.
"""

HOLDING_COST_RATE_ANNUAL = 0.20  # 20% of unit cost per year — standard industry rule of thumb
ORDER_COST_PER_UNIT_MULTIPLIER = 0.02  # small per-unit ordering/handling cost


def daily_holding_cost(unit_cost):
    return (unit_cost * HOLDING_COST_RATE_ANNUAL) / 365


def stockout_cost_per_unit(unit_cost, unit_price):
    """
    Cost of failing to fulfill one unit of demand: lost margin, since
    the sale doesn't happen at all. Using lost margin (not full price)
    is deliberately conservative — it doesn't double-count the cost
    already reflected in unfulfilled unit_cost.
    """
    return unit_price - unit_cost


def order_cost_per_unit(unit_cost):
    return unit_cost * ORDER_COST_PER_UNIT_MULTIPLIER


def risk_adjusted_lead_time(base_lead_time, risk_score):
    """
    Higher supplier risk -> treat lead time as longer/less certain.
    risk_score is 0-100. At risk_score=0, no adjustment. At
    risk_score=100, lead time is inflated by 50% — a deliberately
    moderate assumption, worth tuning if you had real historical
    lead-time-vs-risk data to calibrate against.
    """
    risk_multiplier = 1 + (risk_score / 100) * 0.5
    return base_lead_time * risk_multiplier


def safety_stock_buffer(demand_upper, demand_forecast, risk_score):
    """
    Extra buffer inventory, derived from the forecast's own
    uncertainty interval (yhat_upper - yhat), scaled up further for
    higher-risk suppliers. This ties Phase 3 and Phase 4's outputs
    directly into the optimization's safety margin.
    """
    forecast_uncertainty = (demand_upper - demand_forecast).clip(min=0).mean()
    risk_multiplier = 1 + (risk_score / 100)
    return forecast_uncertainty * risk_multiplier * 5  # ~5 days worth of uncertainty buffer


if __name__ == "__main__":
    print(f"Daily holding cost on a $50 item: ${daily_holding_cost(50):.4f}")
    print(f"Stockout cost per unit ($50 cost, $90 price): ${stockout_cost_per_unit(50, 90):.2f}")
    print(f"Order cost per unit on $50 item: ${order_cost_per_unit(50):.2f}")
    print(f"Risk-adjusted lead time (base 20 days, risk 87): {risk_adjusted_lead_time(20, 87):.1f} days")