import great_expectations as gx
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_generation"))
from db import DB_PATH  # reuse the same absolute path from Phase 1's db.py

context = gx.get_context()

datasource_name = "control_tower_sqlite"
connection_string = f"sqlite:///{DB_PATH}"

if datasource_name not in [ds["name"] for ds in context.list_datasources()]:
    datasource = context.sources.add_sql(
        name=datasource_name, connection_string=connection_string
    )
else:
    datasource = context.get_datasource(datasource_name)

def get_context():
    return context, datasource