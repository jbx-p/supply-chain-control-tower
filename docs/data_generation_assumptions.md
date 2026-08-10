# Data Generation Assumptions

This document outlines the parameters used to generate the synthetic supply chain dataset for the Global Supply Chain Control Tower project.

### 1. Time Range
- **Start Date:** January 1, 2024
- **End Date:** December 31, 2025
- **Duration:** 24 months of historical data. This covers 2 full seasonal cycles to support downstream forecasting modules.

### 2. Supply Chain Scale
- **Products:** 40 unique SKUs distributed across 5 categories (Electronics, Clothing, Food, Furniture, Tools).
- **Suppliers:** 5 unique suppliers (`SUP-001` to `SUP-005`).
- **Warehouses:** 4 distribution nodes (`WH-001` to `WH-004`).
- **Orders & Shipments:** 100 purchase orders and 80 randomly assigned shipments (some orders may not be shipped yet or are delayed).

### 3. Seasonality & Demand Patterns
Demand is generated with a base trend, a seasonal component, and random noise to emulate real-world volatility:
- **Electronics:** Exhibit an 80% demand spike during November and December (Q4 holiday shopping).
- **Clothing:** Exhibit a 50% demand spike during March, April, September, and October (spring and fall seasons).
- **Staples / Other Categories:** Remain relatively stable with baseline demand plus random noise.

### 4. Data Consistency
- Database integrity is maintained via foreign key relationships. 
- `orders` and `shipments` are linked directly to valid `product_id`s and `supplier_id`s.
- `inventory_snapshots` are derived from initial stock levels, daily demand depletion, and replenishment upon shipment arrival, ensuring internal consistency across the dataset.

### 5. Supplier Reliability & Future Disruptions
- Each supplier is assigned a base reliability score between 80% and 99%.
- The generator currently supports injecting "disruption windows" (e.g., a specific supplier failing to deliver on time for a 6-week period). This ground truth is planned to be used in Phase 4 to validate the risk detection algorithms.