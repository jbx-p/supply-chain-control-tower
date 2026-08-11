"""
run_risk_scoring.py
Runs the full Phase 4 pipeline: train the model, then score all
current suppliers.

Run:
    python src/risk_scoring/run_risk_scoring.py
"""

from train_model import train_and_evaluate
from score_suppliers import score_all_suppliers


def main():
    print("Step 1/2: Training and evaluating model...\n")
    train_and_evaluate()

    print("\n" + "=" * 60)
    print("Step 2/2: Scoring current suppliers...\n")
    score_all_suppliers()


if __name__ == "__main__":
    main()