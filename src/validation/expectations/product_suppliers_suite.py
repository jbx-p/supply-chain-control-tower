import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from gx_setup import get_context, get_or_add_table_asset


def build_product_suppliers_suite():
    context, datasource = get_context()
    asset = get_or_add_table_asset(datasource, "product_suppliers")
    batch_request = asset.build_batch_request()

    suite_name = "product_suppliers_suite"
    context.add_or_update_expectation_suite(suite_name)
    validator = context.get_validator(
        batch_request=batch_request, expectation_suite_name=suite_name
    )

    validator.expect_column_values_to_not_be_null("product_id")
    validator.expect_column_values_to_not_be_null("supplier_id")
    validator.expect_column_values_to_not_be_null("is_primary")
    validator.expect_column_values_to_be_in_set("is_primary", [True, False])

    # Note: "does product_id/supplier_id actually exist in products/suppliers"
    # is a cross-table check — handled separately in Step 5's referential
    # integrity checks, not here.

    validator.save_expectation_suite(discard_failed_expectations=False)
    return suite_name


if __name__ == "__main__":
    build_product_suppliers_suite()