# Entity Relationship (ER) Diagram

Below is the schema designed for the Global Supply Chain Control Tower. 

**Note to viewers:** GitHub natively supports Mermaid.js and will automatically render this code block as a visual diagram.

```mermaid
erDiagram
    PRODUCTS ||--o{ ORDERS : "is ordered in"
    PRODUCTS ||--o{ PRODUCT_SUPPLIERS : "supplied by"
    SUPPLIERS ||--o{ PRODUCT_SUPPLIERS : "supplies"
    SUPPLIERS ||--o{ ORDERS : "receives order"
    ORDERS ||--o{ SHIPMENTS : "fulfilled by"
    PRODUCTS ||--o{ INVENTORY_SNAPSHOTS : "stocked in"
    WAREHOUSES ||--o{ INVENTORY_SNAPSHOTS : "holds stock"
    PRODUCTS ||--o{ DEMAND_HISTORY : "generates demand"
    SUPPLIERS ||--o{ SUPPLIER_PERFORMANCE_HISTORY : "has metrics for"
    ORDERS ||--o{ SUPPLIER_PERFORMANCE_HISTORY : "used to derive"
    SHIPMENTS ||--o{ SUPPLIER_PERFORMANCE_HISTORY : "used to derive"