"""
referential_checks.py
Cross-table (foreign key) integrity checks that GX's single-table
expectations can't perform natively. Runs plain SQL LEFT JOIN queries
and reports any "orphan" rows — child records whose referenced parent
doesn't exist.
"""

import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_generation"))
from db import engine


# Each entry: (check_name, SQL query that returns orphan rows if any exist)
REFERENTIAL_CHECKS = {
    "product_suppliers.product_id -> products": """
        SELECT ps.product_id, ps.supplier_id
        FROM product_suppliers ps
        LEFT JOIN products p ON ps.product_id = p.product_id
        WHERE p.product_id IS NULL
    """,
    "product_suppliers.supplier_id -> suppliers": """
        SELECT ps.product_id, ps.supplier_id
        FROM product_suppliers ps
        LEFT JOIN suppliers s ON ps.supplier_id = s.supplier_id
        WHERE s.supplier_id IS NULL
    """,
    "orders.product_id -> products": """
        SELECT o.order_id, o.product_id
        FROM orders o
        LEFT JOIN products p ON o.product_id = p.product_id
        WHERE p.product_id IS NULL
    """,
    "orders.supplier_id -> suppliers": """
        SELECT o.order_id, o.supplier_id
        FROM orders o
        LEFT JOIN suppliers s ON o.supplier_id = s.supplier_id
        WHERE s.supplier_id IS NULL
    """,
    "shipments.order_id -> orders": """
        SELECT sh.shipment_id, sh.order_id
        FROM shipments sh
        LEFT JOIN orders o ON sh.order_id = o.order_id
        WHERE o.order_id IS NULL
    """,
    "demand_history.product_id -> products": """
        SELECT DISTINCT dh.product_id
        FROM demand_history dh
        LEFT JOIN products p ON dh.product_id = p.product_id
        WHERE p.product_id IS NULL
    """,
    "inventory_snapshots.product_id -> products": """
        SELECT DISTINCT inv.product_id
        FROM inventory_snapshots inv
        LEFT JOIN products p ON inv.product_id = p.product_id
        WHERE p.product_id IS NULL
    """,
}


def check_referential_integrity(verbose=True):
    """
    Runs every referential check and returns a dict of
    {check_name: orphan_row_count}. A healthy dataset returns 0 for
    every check.
    """
    results = {}

    for check_name, query in REFERENTIAL_CHECKS.items():
        orphan_rows = pd.read_sql(query, engine)
        count = len(orphan_rows)
        results[check_name] = count

        if verbose:
            status = "✅ PASS" if count == 0 else f"❌ FAIL ({count} orphan rows)"
            print(f"{status}  {check_name}")
            if count > 0:
                # show a few examples to make debugging fast
                print(orphan_rows.head(5).to_string(index=False))
                print()

    return results


if __name__ == "__main__":
    print("Running referential integrity checks...\n")
    results = check_referential_integrity()

    total_failures = sum(1 for v in results.values() if v > 0)
    print(f"\n{len(results) - total_failures}/{len(results)} checks passed")

    if total_failures > 0:
        print("❌ Referential integrity issues found — see details above")
    else:
        print("✅ All referential integrity checks passed")