import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from gx_setup import get_context, get_or_add_table_asset


def build_inventory_suite():
    context, datasource = get_context()
    asset = get_or_add_table_asset(datasource, "inventory_snapshots")
    batch_request = asset.build_batch_request()

    suite_name = "inventory_suite"
    context.add_or_update_expectation_suite(suite_name)
    validator = context.get_validator(
        batch_request=batch_request, expectation_suite_name=suite_name
    )

    validator.expect_column_values_to_not_be_null("snapshot_date")
    validator.expect_column_values_to_not_be_null("product_id")
    validator.expect_column_values_to_not_be_null("quantity_on_hand")

    # Hard invariant: stock can never go negative
    validator.expect_column_values_to_be_between(
        "quantity_on_hand", min_value=0, max_value=None
    )

    # No duplicate (snapshot_date, product_id) pairs — one snapshot per
    # product per day
    validator.expect_compound_columns_to_be_unique(["snapshot_date", "product_id"])

    # Soft expectation: matches the generation window from Phase 1
    validator.expect_column_values_to_be_between(
    "snapshot_date", min_value="2024-01-01 00:00:00", max_value="2025-12-31 23:59:59")

    validator.save_expectation_suite(discard_failed_expectations=False)
    return suite_name


if __name__ == "__main__":
    build_inventory_suite()