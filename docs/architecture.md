\# System Architecture



```mermaid

flowchart LR

&#x20;   A\[Synthetic Data Generator] --> B\[Data Validation]

&#x20;   B --> C\[Demand Forecasting]

&#x20;   B --> D\[Supplier Risk Scoring]

&#x20;   C --> E\[Inventory Optimization]

&#x20;   D --> E

&#x20;   E --> F\[Disruption Simulation]

&#x20;   C --> G\[GenAI Briefing]

&#x20;   D --> G

&#x20;   E --> G

&#x20;   F --> G

&#x20;   G --> H\[Streamlit App]

&#x20;   G --> I\[Tableau Dashboard]

```

