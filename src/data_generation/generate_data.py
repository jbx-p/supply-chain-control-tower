from faker import Faker
import pandas as pd
import numpy as np
from db import engine
import os
import random
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta

# ==============================================================
# 1. DATABASE CONFIGURATION
# ==============================================================
db_folder = r"C:\Users\bumba\Desktop\supply_chain_data"
if not os.path.exists(db_folder):
    os.makedirs(db_folder)
db_file = os.path.join(db_folder, "supply_chain.db").replace("\\", "/")
print(f"📂 Database will be saved at: {db_file}")
engine = create_engine(f'sqlite:///{db_file}')


# ==============================================================
# 2. FUNCTION DEFINITIONS (The logic to generate relationships)
# ==============================================================
def generate_orders(products_df, suppliers_df):
    orders_data = []
    valid_product_ids = products_df['product_id'].tolist() if not products_df.empty else []
    valid_supplier_ids = suppliers_df['supplier_id'].tolist() if not suppliers_df.empty else []
    
    if not valid_product_ids or not valid_supplier_ids:
        return pd.DataFrame(columns=["order_id", "product_id", "supplier_id", "order_date", "expected_delivery_date", "actual_delivery_date", "quantity_ordered"])
    
    for i in range(1, 101): # Generate 100 orders
        order_data = {
            'order_id': f"ORD-{i:03d}",
            'product_id': random.choice(valid_product_ids),
            'supplier_id': random.choice(valid_supplier_ids),
            'order_date': datetime.now() - timedelta(days=random.randint(1, 365)),
            'expected_delivery_date': datetime.now() + timedelta(days=random.randint(5, 20)),
            'actual_delivery_date': None,
            'quantity_ordered': random.randint(10, 100)
        }
        orders_data.append(order_data)
    return pd.DataFrame(orders_data)

def generate_shipments(orders_df):
    shipments_data = []
    if orders_df.empty:
        return pd.DataFrame(columns=["shipment_id", "order_id", "ship_date", "arrival_date", "quantity_shipped", "status"])
    
    shipped_orders = orders_df.sample(n=min(80, len(orders_df)))
    for i, row in shipped_orders.iterrows():
        shipment_data = {
            'shipment_id': f"SHIP-{i+1:03d}",
            'order_id': row['order_id'],
            'ship_date': row['order_date'] + timedelta(days=random.randint(2, 5)),
            'arrival_date': row['expected_delivery_date'] - timedelta(days=random.randint(0, 3)),
            'quantity_shipped': row['quantity_ordered'],
            'status': random.choice(['In Transit', 'Delivered'])
        }
        shipments_data.append(shipment_data)
    return pd.DataFrame(shipments_data)

def generate_inventory(products_df):
    inventory_data = []
    if products_df.empty:
        return pd.DataFrame(columns=["snapshot_date", "product_id", "warehouse_id", "quantity_on_hand"])
    
    for _, product in products_df.iterrows():
        for warehouse_id in ['WH-001', 'WH-002', 'WH-003']:
            snapshot_data = {
                'snapshot_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'product_id': product['product_id'],
                'warehouse_id': warehouse_id,
                'quantity_on_hand': random.randint(0, 500)
            }
            inventory_data.append(snapshot_data)
    return pd.DataFrame(inventory_data)


# ==============================================================
# 3. DATA GENERATION LOGIC
# ==============================================================
print("🟢 Generating data...")

# --- Generate Products (Mock data for 40 products) ---
products_data = []
for i in range(1, 41):
    product_data = {
        'product_id': f"PROD-{i:03d}",
        'category': random.choice(['Electronics', 'Clothing', 'Food', 'Furniture', 'Tools']),
        'unit_cost': round(random.uniform(5.0, 500.0), 2),
        'lead_time_days': random.randint(1, 30),
        'unit_price': round(random.uniform(10.0, 800.0), 2)
    }
    products_data.append(product_data)
products_df = pd.DataFrame(products_data)

# --- Generate Suppliers (Mock data for 5 suppliers) ---
suppliers_data = []
for i in range(1, 6):
    supplier_data = {
        'supplier_id': f"SUP-{i:03d}",
        'name': f"Supplier {i}",
        'country': random.choice(['USA', 'China', 'Germany', 'India', 'Brazil']),
        'reliability_base': round(random.uniform(0.7, 1.0), 2)
    }
    suppliers_data.append(supplier_data)
suppliers_df = pd.DataFrame(suppliers_data)

# --- Generate Dependent Data ---
orders_df = generate_orders(products_df, suppliers_df)      # 1. Generate orders
shipments_df = generate_shipments(orders_df)                # 2. Generate shipments
inventory_df = generate_inventory(products_df)              # 3. Generate inventory snapshots


# ==============================================================
# 4. LOADING TO DATABASE
# ==============================================================
print("🟢 Loading to database...")

# Products
print(f"Products rows before SQL: {len(products_df)}")
products_df.to_sql("products", engine, if_exists="replace", index=False)

# Orders
print(f"Orders rows before SQL: {len(orders_df)}")
orders_df.to_sql("orders", engine, if_exists="replace", index=False)

# Shipments
print(f"Shipments rows before SQL: {len(shipments_df)}")
shipments_df.to_sql("shipments", engine, if_exists="replace", index=False)

# Inventory
print(f"Inventory rows before SQL: {len(inventory_df)}")
inventory_df.to_sql("inventory_snapshots", engine, if_exists="replace", index=False)


print("✅ Done! Data successfully loaded to the database.")



# --- Sanity Checks ---
print("Running sanity checks...")
# Check 1: No negative demand
neg_demand = pd.read_sql("SELECT * FROM demand_history WHERE units_sold < 0", engine)
assert len(neg_demand) == 0, "❌ Negative demand found!"

# Check 2: No orphan orders (orders missing a valid product)
orphan_orders = pd.read_sql("""
    SELECT o.* FROM orders o
    LEFT JOIN products p ON o.product_id = p.product_id
    WHERE p.product_id IS NULL
""", engine)
assert len(orphan_orders) == 0, "❌ Orphan orders found!"

print("✅ All sanity checks passed! No negative values and no broken foreign keys.")