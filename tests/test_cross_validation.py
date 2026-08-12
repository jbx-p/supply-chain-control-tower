"""
test_cross_validation.py
Unit tests for the MAPE calculation logic (Phase 3).
"""

import sys
import os
import numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src", "forecasting"))

from cross_validation import calculate_mape


def test_mape_perfect_forecast_is_zero():
    actual = [100, 200, 300]
    predicted = [100, 200, 300]
    assert calculate_mape(actual, predicted) == 0


def test_mape_known_case():
    actual = [100]
    predicted = [110]
    assert abs(calculate_mape(actual, predicted) - 10.0) < 0.01


def test_mape_ignores_zero_actual_days():
    actual = [0, 100]
    predicted = [50, 110]
    result = calculate_mape(actual, predicted)
    assert abs(result - 10.0) < 0.01