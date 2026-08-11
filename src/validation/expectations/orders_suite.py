import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from gx_setup import get_context


def build_orders_suite():
    context, datasource = get_context()
    asset = datasource.add_table_asset(name="orders", table_name="orders")
    batch_request = asset.build_batch_request()

    suite_name = "orders_suite"
    context.add_or_update_expectation_suite(suite_name)
    validator = context.get_validator(
        batch_request=batch_request, expectation_suite_name=suite_name
    )

    validator.expect_column_values_to_not_be_null("order_id")
    validator.expect_column_values_to_be_unique("order_id")
    validator.expect_column_values_to_not_be_null("product_id")
    validator.expect_column_values_to_not_be_null("supplier_id")
    validator.expect_column_values_to_not_be_null("order_date")
    validator.expect_column_values_to_not_be_null("expected_delivery_date")

    # quantity ordered must be positive
    validator.expect_column_values_to_be_between(
        "quantity_ordered", min_value=1, max_value=None
    )

    # expected delivery must come after the order was placed
    validator.expect_column_pair_values_A_to_be_greater_than_B(
        column_A="expected_delivery_date", column_B="order_date", or_equal=True
    )

    # actual delivery must also come after the order was placed
    validator.expect_column_pair_values_A_to_be_greater_than_B(
        column_A="actual_delivery_date", column_B="order_date", or_equal=True
    )

    validator.save_expectation_suite(discard_failed_expectations=False)
    return suite_name


if __name__ == "__main__":
    build_orders_suite()