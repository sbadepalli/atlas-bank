import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

engine = create_engine(DATABASE_URL)

def load_data():
    print("Loading employee data...")
    employees = pd.read_csv("data/employees.csv")
    employees.to_sql("employees", engine, if_exists="replace", index=False)
    print(f"✅ Loaded {len(employees)} employees")

    print("Loading P&L actual data...")
    pnl_actual = pd.read_csv("data/pnl_actual.csv")
    pnl_actual.to_sql("pnl_actual", engine, if_exists="replace", index=False)
    print(f"✅ Loaded {len(pnl_actual)} P&L actual rows")

    print("Loading P&L budget data...")
    pnl_budget = pd.read_csv("data/pnl_budget.csv")
    pnl_budget.to_sql("pnl_budget", engine, if_exists="replace", index=False)
    print(f"✅ Loaded {len(pnl_budget)} P&L budget rows")

    print("✅ All data loaded successfully!")

if __name__ == "__main__":
    load_data()
