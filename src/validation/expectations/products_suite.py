import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from gx_setup import get_context, get_or_add_table_asset

def build_products_suite():
    context, datasource = get_context()
    asset = get_or_add_table_asset(datasource, "products")
    batch_request = asset.build_batch_request()

    suite_name = "products_suite"
    context.add_or_update_expectation_suite(suite_name)
    validator = context.get_validator(
        batch_request=batch_request, expectation_suite_name=suite_name
    )

    validator.expect_column_values_to_not_be_null("product_id")
    validator.expect_column_values_to_be_unique("product_id")
    validator.expect_column_values_to_be_in_set(
        "category", ["electronics", "apparel", "staples"]
    )
    validator.expect_column_values_to_be_between("unit_cost", min_value=0, max_value=10000)
    validator.expect_column_values_to_be_between("unit_price", min_value=0, max_value=20000)
    validator.expect_column_values_to_be_between(
        "lead_time_days_base", min_value=1, max_value=180
    )

    validator.save_expectation_suite(discard_failed_expectations=False)
    return suite_name

if __name__ == "__main__":
    build_products_suite()