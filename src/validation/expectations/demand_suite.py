import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from gx_setup import get_context


def build_demand_suite():
    context, datasource = get_context()
    asset = datasource.add_table_asset(name="demand_history", table_name="demand_history")
    batch_request = asset.build_batch_request()

    suite_name = "demand_suite"
    context.add_or_update_expectation_suite(suite_name)
    validator = context.get_validator(
        batch_request=batch_request, expectation_suite_name=suite_name
    )

    validator.expect_column_values_to_not_be_null("date")
    validator.expect_column_values_to_not_be_null("product_id")
    validator.expect_column_values_to_not_be_null("units_sold")

    # Hard invariant: demand can never be negative
    validator.expect_column_values_to_be_between("units_sold", min_value=0, max_value=None)

    # Soft expectation: matches the generation window from Phase 1 —
    # update this if you regenerate with a different date range
    validator.expect_column_values_to_be_between(
        "date", min_value="2024-01-01", max_value="2025-12-31"
    )

    # No duplicate (date, product_id) pairs — each product should have
    # exactly one demand row per day
    validator.expect_compound_columns_to_be_unique(["date", "product_id"])

    validator.save_expectation_suite(discard_failed_expectations=False)
    return suite_name


if __name__ == "__main__":
    build_demand_suite()