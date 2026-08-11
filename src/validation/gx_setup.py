import great_expectations as gx
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_generation"))
from db import DB_PATH  # reuse the same absolute path from Phase 1's db.py

context = gx.get_context()

def get_or_add_table_asset(datasource, table_name):
    """
    Returns the existing asset if it's already registered on the
    datasource, otherwise creates it. Prevents "already exists" errors
    when suites are built more than once (e.g. once standalone, once
    via run_validation.py).
    """
    try:
        return datasource.get_asset(table_name)
    except LookupError:
        return datasource.add_table_asset(name=table_name, table_name=table_name)

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