import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from gx_setup import get_context, get_or_add_table_asset


def build_shipments_suite():
    context, datasource = get_context()
    asset = get_or_add_table_asset(datasource, "shipments")
    batch_request = asset.build_batch_request()

    suite_name = "shipments_suite"
    context.add_or_update_expectation_suite(suite_name)
    validator = context.get_validator(
        batch_request=batch_request, expectation_suite_name=suite_name
    )

    validator.expect_column_values_to_not_be_null("shipment_id")
    validator.expect_column_values_to_be_unique("shipment_id")
    validator.expect_column_values_to_not_be_null("order_id")
    validator.expect_column_values_to_not_be_null("ship_date")
    validator.expect_column_values_to_not_be_null("arrival_date")

    validator.expect_column_values_to_be_between(
        "quantity_shipped", min_value=1, max_value=None
    )

    validator.expect_column_values_to_be_in_set("status", ["delivered"])

    # arrival must come after (or same day as) shipping
    validator.expect_column_pair_values_A_to_be_greater_than_B(
        column_A="arrival_date", column_B="ship_date", or_equal=True
    )

    validator.save_expectation_suite(discard_failed_expectations=False)
    return suite_name


if __name__ == "__main__":
    build_shipments_suite()