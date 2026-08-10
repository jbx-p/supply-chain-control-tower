from sqlalchemy import create_engine

DB_PATH = "data/processed/control_tower.db"
engine = create_engine(f"sqlite:///{DB_PATH}")