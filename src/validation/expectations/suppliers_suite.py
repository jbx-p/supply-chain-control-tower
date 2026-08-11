import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from gx_setup import get_context


def build_suppliers_suite():
    context, datasource = get_context()
    asset = datasource.add_table_asset(name="suppliers", table_name="suppliers")
    batch_request = asset.build_batch_request()

    suite_name = "suppliers_suite"
    context.add_or_update_expectation_suite(suite_name)
    validator = context.get_validator(
        batch_request=batch_request, expectation_suite_name=suite_name
    )

    validator.expect_column_values_to_not_be_null("supplier_id")
    validator.expect_column_values_to_be_unique("supplier_id")
    validator.expect_column_values_to_not_be_null("name")
    validator.expect_column_values_to_not_be_null("country")
    validator.expect_column_values_to_be_between(
        "reliability_base", min_value=0, max_value=1
    )

    validator.save_expectation_suite(discard_failed_expectations=False)
    return suite_name


if __name__ == "__main__":
    build_suppliers_suite()