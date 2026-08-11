"""
run_validation.py
Phase 2, Step 6 — Combined validation runner.

Runs all 7 great_expectations suites (as checkpoints) plus the
referential integrity checks, and prints one overall pass/fail report.

Run:
    python src/validation/run_validation.py
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "expectations"))

from gx_setup import get_context
from referential_checks import check_referential_integrity

from expectations.products_suite import build_products_suite
from expectations.suppliers_suite import build_suppliers_suite
from expectations.product_suppliers_suite import build_product_suppliers_suite
from expectations.demand_suite import build_demand_suite
from expectations.orders_suite import build_orders_suite
from expectations.shipments_suite import build_shipments_suite
from expectations.inventory_suite import build_inventory_suite


# table_name -> (suite_builder_function, asset_name)
SUITE_BUILDERS = {
    "products": (build_products_suite, "products"),
    "suppliers": (build_suppliers_suite, "suppliers"),
    "product_suppliers": (build_product_suppliers_suite, "product_suppliers"),
    "demand_history": (build_demand_suite, "demand_history"),
    "orders": (build_orders_suite, "orders"),
    "shipments": (build_shipments_suite, "shipments"),
    "inventory_snapshots": (build_inventory_suite, "inventory_snapshots"),
}


def run_suite_checkpoint(context, datasource, table_name, suite_builder, asset_name):
    """
    Builds the suite (Step 4 logic), then wraps it in a checkpoint and
    runs it, returning True/False for pass/fail.
    """
    suite_name = suite_builder()

    asset = datasource.get_asset(asset_name)
    batch_request = asset.build_batch_request()

    checkpoint_name = f"{table_name}_checkpoint"
    checkpoint = context.add_or_update_checkpoint(
        name=checkpoint_name,
        validations=[{
            "batch_request": batch_request,
            "expectation_suite_name": suite_name,
        }],
    )

    result = checkpoint.run()
    return result["success"]


def run_all_validations():
    context, datasource = get_context()

    print("=" * 60)
    print("SUPPLY CHAIN CONTROL TOWER — DATA VALIDATION")
    print("=" * 60)

    print("\n--- Expectation Suites (per-table checks) ---\n")
    suite_results = {}
    for table_name, (builder, asset_name) in SUITE_BUILDERS.items():
        try:
            success = run_suite_checkpoint(context, datasource, table_name, builder, asset_name)
        except Exception as e:
            print(f"❌ ERROR  {table_name}: {e}")
            success = False
        suite_results[table_name] = success
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}  {table_name}")

    print("\n--- Referential Integrity Checks (cross-table checks) ---\n")
    ref_results = check_referential_integrity(verbose=True)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    suite_pass_count = sum(suite_results.values())
    suite_total = len(suite_results)
    print(f"Expectation suites:        {suite_pass_count}/{suite_total} passed")

    ref_pass_count = sum(1 for v in ref_results.values() if v == 0)
    ref_total = len(ref_results)
    print(f"Referential integrity:     {ref_pass_count}/{ref_total} passed")

    overall_success = (suite_pass_count == suite_total) and (ref_pass_count == ref_total)

    print()
    if overall_success:
        print("✅ ALL VALIDATIONS PASSED — dataset is healthy")
    else:
        print("❌ VALIDATION FAILURES DETECTED — see details above")

    return overall_success


if __name__ == "__main__":
    success = run_all_validations()
    sys.exit(0 if success else 1)