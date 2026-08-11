"""
db.py
Shared SQLAlchemy engine for the Supply Chain Control Tower project.
"""

from sqlalchemy import create_engine
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_DIR = PROJECT_ROOT / "data" / "processed"
DB_PATH = DB_DIR / "control_tower.db"

DB_DIR.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}")

if __name__ == "__main__":
    print("Project root:", PROJECT_ROOT)
    print("DB path:", DB_PATH)
    print("DB folder exists:", DB_DIR.exists())
    print("DB file exists:", DB_PATH.exists())
    try:
        with engine.connect() as conn:
            print("✅ Connection succeeded")
    except Exception as e:
        print("❌ Connection failed:", e)