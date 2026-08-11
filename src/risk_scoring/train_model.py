"""
train_model.py
Trains a scikit-learn classifier on the supplier-month panel to
predict next-month risk, using a TIME-BASED train/test split (not
random) since shuffling would leak future information into training.
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix

from feature_engineering import build_monthly_panel, add_lagged_features


FEATURE_COLS = [
    "prev_on_time_rate", "prev_avg_delay_days", "prev_delay_std",
    "prev_order_count", "prev_avg_fulfillment_ratio", "prev_avg_shipment_count",
    "rolling_3m_on_time", "product_diversity",
]
TARGET_COL = "is_risk_month"


def time_based_split(panel, test_fraction=0.25):
    """
    Splits by calendar month, not randomly — every supplier's most
    recent months go into the test set. This respects the fact that
    you'd never train on the future to predict the past.
    """
    panel = panel.sort_values("order_month")
    unique_months = panel["order_month"].unique()
    split_idx = int(len(unique_months) * (1 - test_fraction))
    train_months = unique_months[:split_idx]
    test_months = unique_months[split_idx:]

    train = panel[panel["order_month"].isin(train_months)]
    test = panel[panel["order_month"].isin(test_months)]
    return train, test


def train_and_evaluate():
    panel = build_monthly_panel()
    panel = add_lagged_features(panel)

    train, test = time_based_split(panel)
    print(f"Train: {len(train)} rows ({train['order_month'].min()} to {train['order_month'].max()})")
    print(f"Test:  {len(test)} rows ({test['order_month'].min()} to {test['order_month'].max()})")

    X_train, y_train = train[FEATURE_COLS], train[TARGET_COL]
    X_test, y_test = test[FEATURE_COLS], test[TARGET_COL]

    model = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.1,
        random_state=42,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred, target_names=["Low/Med Risk", "High Risk"]))

    print("--- Confusion Matrix ---")
    print(confusion_matrix(y_test, y_pred))

    if y_test.nunique() > 1:  # ROC-AUC undefined if test set has only one class
        auc = roc_auc_score(y_test, y_proba)
        print(f"\nROC-AUC: {auc:.3f}")

    print("\n--- Feature Importance ---")
    importance = pd.Series(model.feature_importances_, index=FEATURE_COLS).sort_values(ascending=False)
    print(importance)

    joblib.dump(model, "supplier_risk_model.joblib")
    print("\n✅ Model saved to supplier_risk_model.joblib")

    return model, importance


if __name__ == "__main__":
    train_and_evaluate()