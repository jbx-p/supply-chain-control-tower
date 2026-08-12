"""
test_cost_model.py
Unit tests for the cost and risk-adjustment functions (Phase 5) —
these are pure functions, ideal for fast, isolated unit testing.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src", "optimization"))

from cost_model import (
    daily_holding_cost, stockout_cost_per_unit, order_cost_per_unit,
    risk_adjusted_lead_time,
)


def test_daily_holding_cost_is_positive_and_scales_with_unit_cost():
    low = daily_holding_cost(10)
    high = daily_holding_cost(100)
    assert low > 0
    assert high > low  # more expensive items should cost more to hold


def test_stockout_cost_equals_margin():
    cost = stockout_cost_per_unit(unit_cost=50, unit_price=90)
    assert cost == 40  # lost margin, not full price


def test_order_cost_is_small_fraction_of_unit_cost():
    cost = order_cost_per_unit(unit_cost=100)
    assert 0 < cost < 100 * 0.1  # should be a small percentage, not comparable to the item cost itself


def test_risk_adjusted_lead_time_scales_correctly():
    base = 20
    no_risk = risk_adjusted_lead_time(base, risk_score=0)
    full_risk = risk_adjusted_lead_time(base, risk_score=100)

    assert no_risk == base  # zero risk should mean no adjustment
    assert full_risk == base * 1.5  # per the documented +50% at max risk
    assert no_risk < full_risk