import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DATABASE_URL)

TABLES = [
    "dim_entity",
    "dim_department",
    "dim_account",
    "dim_scenario",
    "dim_period",
    "dim_fx_rate",
    "fact_financials"
]

def load_data():
    for table in TABLES:
        print(f"Loading {table}...")
        df = pd.read_csv(f"data/{table}.csv")
        df.to_sql(table, engine, if_exists="replace", index=False)
        print(f"✅ Loaded {len(df)} rows into {table}")

    print("✅ All dimensional data loaded successfully!")

if __name__ == "__main__":
    load_data()
