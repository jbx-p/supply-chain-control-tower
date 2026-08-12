"""
db_utils.py
Shared, cached database access for the Streamlit app. Streamlit's
@st.cache_data decorator avoids re-querying the database on every
user interaction (Streamlit re-runs the whole script on every widget
change, so caching is essential, not optional).
"""

import sys
import os
import streamlit as st
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_generation"))
from db import engine


@st.cache_data(ttl=300)  # cache for 5 minutes — long enough to avoid re-querying on every click
def load_table(table_name):
    return pd.read_sql(f"SELECT * FROM {table_name}", engine)


@st.cache_data(ttl=300)
def load_query(query, params=None):
    return pd.read_sql(query, engine, params=params)