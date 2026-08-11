"""
generate_data.py
Phase 1 — Data Architecture & Synthetic Dataset Generation

Generates a realistic, internally-consistent synthetic supply chain dataset
(products, suppliers, demand history, orders, shipments, inventory
snapshots) and loads it into SQLite via SQLAlchemy.

Run:
    python src/data_generation/generate_data.py
"""

from faker import Faker
import pandas as pd
import numpy as np
from db import engine

fake = Faker()
np.random.seed(42)
Faker.seed(42)

START_DATE = "2024-01-01"
END_DATE = "2025-12-31"

# Disruption windows: (supplier_id will be assigned after suppliers are
# generated) — defined here as indices into the supplier list, plus the
# date range and severity multiplier applied to that supplier's delay.
DISRUPTION_WINDOWS = [
    {"supplier_index": 2, "start": "2024-06-01", "end": "2024-07-15", "severity": 3.0},
    {"supplier_index": 5, "start": "2025-01-10", "end": "2025-02-20", "severity": 2.5},
    {"supplier_index": 8, "start": "2025-08-01", "end": "2025-09-30", "severity": 4.0},
]


# ---------------------------------------------------------------------
# STEP 4a — Products and suppliers
# ---------------------------------------------------------------------
def generate_products(n=40):
    categories = ["electronics", "apparel", "staples"]
    rows = []
    for i in range(n):
        category = np.random.choice(categories, p=[0.4, 0.35, 0.25])
        unit_cost = round(np.random.uniform(5, 200), 2)
        rows.append({
            "product_id": f"P{i+1:03d}",
            "category": category,
            "unit_cost": unit_cost,
            "lead_time_days_base": int(np.random.randint(7, 45)),
        })
    df = pd.DataFrame(rows)
    df["unit_price"] = (df["unit_cost"] * np.random.uniform(1.3, 2.0, len(df))).round(2)
    return df


def generate_suppliers(n=12):
    rows = []
    for i in range(n):
        rows.append({
            "supplier_id": f"S{i+1:03d}",
            "name": fake.company(),
            "country": fake.country(),
            "reliability_base": round(np.random.uniform(0.80, 0.99), 3),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# STEP 4b — Product-supplier mapping (many-to-many)
# ---------------------------------------------------------------------
def generate_product_suppliers(products_df, suppliers_df):
    rows = []
    supplier_ids = suppliers_df["supplier_id"].tolist()
    for product_id in products_df["product_id"]:
        n_suppliers = np.random.choice([1, 2, 3], p=[0.5, 0.35, 0.15])
        chosen = np.random.choice(supplier_ids, size=n_suppliers, replace=False)
        for i, supplier_id in enumerate(chosen):
            rows.append({
                "product_id": product_id,
                "supplier_id": supplier_id,
                "is_primary": (i == 0),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# STEP 4c — Demand history (base trend + seasonality + noise)
# ---------------------------------------------------------------------
def generate_demand(products_df, start_date=START_DATE, end_date=END_DATE):
    dates = pd.date_range(start_date, end_date, freq="D")
    records = []
    for _, product in products_df.iterrows():
        base = np.random.uniform(20, 150)
        trend = np.linspace(0, np.random.uniform(-10, 30), len(dates))
        for i, date in enumerate(dates):
            seasonal = 0.0
            if product["category"] == "electronics" and date.month in (11, 12):
                seasonal = base * 0.8
            elif product["category"] == "apparel" and date.month in (3, 4, 9, 10):
                seasonal = base * 0.5
            noise = np.random.normal(0, base * 0.15)
            units = max(0, base + trend[i] + seasonal + noise)
            records.append({
                "date": date,
                "product_id": product["product_id"],
                "units_sold": int(round(units)),
            })
    return pd.DataFrame(records)


# ---------------------------------------------------------------------
# STEP 4d — Orders and shipments, with injected disruption events
# ---------------------------------------------------------------------
def generate_orders_and_shipments(products_df, suppliers_df, product_suppliers_df,
                                   start_date=START_DATE, end_date=END_DATE):
    order_rows = []
    shipment_rows = []
    order_counter = 1
    shipment_counter = 1

    supplier_ids = suppliers_df["supplier_id"].tolist()
    disruptions = [
        {
            "supplier_id": supplier_ids[d["supplier_index"]],
            "start": pd.Timestamp(d["start"]),
            "end": pd.Timestamp(d["end"]),
            "severity": d["severity"],
        }
        for d in DISRUPTION_WINDOWS
    ]

    order_dates = pd.date_range(start_date, end_date, freq="14D")  # biweekly ordering cycle

    for _, product in products_df.iterrows():
        # who can supply this product
        suppliers_for_product = product_suppliers_df[
            product_suppliers_df["product_id"] == product["product_id"]
        ]
        primary = suppliers_for_product[suppliers_for_product["is_primary"]]
        supplier_id = primary["supplier_id"].iloc[0] if len(primary) else suppliers_for_product["supplier_id"].iloc[0]
        reliability = suppliers_df.loc[
            suppliers_df["supplier_id"] == supplier_id, "reliability_base"
        ].iloc[0]

        for order_date in order_dates:
            base_lead_time = product["lead_time_days_base"]
            expected_delivery = order_date + pd.Timedelta(days=base_lead_time)

            # check if this order falls inside a disruption window for this supplier
            severity = 1.0
            for d in disruptions:
                if d["supplier_id"] == supplier_id and d["start"] <= order_date <= d["end"]:
                    severity = d["severity"]
                    break

            # delay is small most of the time, larger (and more variable) during disruptions
            on_time_prob = reliability / severity
            if np.random.random() < on_time_prob:
                delay_days = int(np.random.uniform(0, 2))
            else:
                delay_days = int(np.random.uniform(3, 10) * severity)

            actual_delivery = expected_delivery + pd.Timedelta(days=delay_days)
            quantity_ordered = int(np.random.uniform(50, 400))

            order_id = f"O{order_counter:06d}"
            order_counter += 1
            order_rows.append({
                "order_id": order_id,
                "product_id": product["product_id"],
                "supplier_id": supplier_id,
                "order_date": order_date,
                "expected_delivery_date": expected_delivery,
                "actual_delivery_date": actual_delivery,
                "quantity_ordered": quantity_ordered,
            })

            # occasionally split into two shipments (partial fulfillment)
            if np.random.random() < 0.15:
                split_qty = int(quantity_ordered * np.random.uniform(0.3, 0.7))
                shipment_rows.append({
                    "shipment_id": f"SH{shipment_counter:06d}",
                    "order_id": order_id,
                    "ship_date": order_date + pd.Timedelta(days=1),
                    "arrival_date": actual_delivery - pd.Timedelta(days=np.random.randint(0, 3)),
                    "quantity_shipped": split_qty,
                    "status": "delivered",
                })
                shipment_counter += 1
                shipment_rows.append({
                    "shipment_id": f"SH{shipment_counter:06d}",
                    "order_id": order_id,
                    "ship_date": order_date + pd.Timedelta(days=3),
                    "arrival_date": actual_delivery,
                    "quantity_shipped": quantity_ordered - split_qty,
                    "status": "delivered",
                })
                shipment_counter += 1
            else:
                shipment_rows.append({
                    "shipment_id": f"SH{shipment_counter:06d}",
                    "order_id": order_id,
                    "ship_date": order_date + pd.Timedelta(days=1),
                    "arrival_date": actual_delivery,
                    "quantity_shipped": quantity_ordered,
                    "status": "delivered",
                })
                shipment_counter += 1

    return pd.DataFrame(order_rows), pd.DataFrame(shipment_rows)


# ---------------------------------------------------------------------
# STEP 4e — Inventory snapshots, derived from demand + shipments
# ---------------------------------------------------------------------
def generate_inventory_snapshots(products_df, demand_df, shipments_orders_df,
                                  start_date=START_DATE, end_date=END_DATE):
    """
    shipments_orders_df: shipments joined with orders (needs product_id and arrival_date)
    Simulates day-by-day stock level per product: starts with an initial
    buffer, subtracts daily demand, adds shipment arrivals.
    """
    dates = pd.date_range(start_date, end_date, freq="D")
    records = []

    demand_pivot = demand_df.pivot_table(
        index="date", columns="product_id", values="units_sold", fill_value=0
    )
    arrivals_pivot = shipments_orders_df.pivot_table(
        index="arrival_date", columns="product_id", values="quantity_shipped",
        aggfunc="sum", fill_value=0
    )

    for product_id in products_df["product_id"]:
        stock = int(np.random.uniform(500, 2000))  # starting inventory
        for date in dates:
            demand_today = int(demand_pivot.at[date, product_id]) if (
                date in demand_pivot.index and product_id in demand_pivot.columns
            ) else 0
            arrivals_today = int(arrivals_pivot.at[date, product_id]) if (
                date in arrivals_pivot.index and product_id in arrivals_pivot.columns
            ) else 0

            stock = max(0, stock - demand_today + arrivals_today)
            records.append({
                "snapshot_date": date,
                "product_id": product_id,
                "quantity_on_hand": stock,
            })

    return pd.DataFrame(records)


# ---------------------------------------------------------------------
# STEP 5 — Load everything into the database
# ---------------------------------------------------------------------
def load_to_db(tables: dict):
    for table_name, df in tables.items():
        df.to_sql(table_name, engine, if_exists="replace", index=False)
        print(f"  Loaded {table_name}: {len(df):,} rows")


# ---------------------------------------------------------------------
# STEP 6 — Sanity checks
# ---------------------------------------------------------------------
def run_sanity_checks(products_df, suppliers_df, demand_df, orders_df,
                       shipments_df, inventory_df):
    print("\nRunning sanity checks...")

    assert (demand_df["units_sold"] >= 0).all(), "Negative demand found"
    assert (inventory_df["quantity_on_hand"] >= 0).all(), "Negative inventory found"
    assert orders_df["product_id"].isin(products_df["product_id"]).all(), "Orphan product_id in orders"
    assert orders_df["supplier_id"].isin(suppliers_df["supplier_id"]).all(), "Orphan supplier_id in orders"
    assert shipments_df["order_id"].isin(orders_df["order_id"]).all(), "Orphan order_id in shipments"
    assert products_df["product_id"].is_unique, "Duplicate product_id"
    assert suppliers_df["supplier_id"].is_unique, "Duplicate supplier_id"

    print("  ✅ All sanity checks passed")


# ---------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------
def main():
    print("Generating products and suppliers...")
    products_df = generate_products()
    suppliers_df = generate_suppliers()
    product_suppliers_df = generate_product_suppliers(products_df, suppliers_df)

    print("Generating demand history...")
    demand_df = generate_demand(products_df)

    print("Generating orders and shipments (with disruption events)...")
    orders_df, shipments_df = generate_orders_and_shipments(
        products_df, suppliers_df, product_suppliers_df
    )

    print("Generating inventory snapshots...")
    shipments_orders_df = shipments_df.merge(
        orders_df[["order_id", "product_id"]], on="order_id", how="left"
    )
    inventory_df = generate_inventory_snapshots(products_df, demand_df, shipments_orders_df)

    print("\nLoading tables into SQLite...")
    load_to_db({
        "products": products_df,
        "suppliers": suppliers_df,
        "product_suppliers": product_suppliers_df,
        "demand_history": demand_df,
        "orders": orders_df,
        "shipments": shipments_df,
        "inventory_snapshots": inventory_df,
    })

    run_sanity_checks(products_df, suppliers_df, demand_df, orders_df,
                       shipments_df, inventory_df)

    print("\n✅ Data generation complete. Database written to data/processed/control_tower.db")


if __name__ == "__main__":
    main()