from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

app = FastAPI(
    title="Atlas Commercial Bank API",
    description="Financial data API for Atlas Commercial Bank",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"message": "Welcome to Atlas Commercial Bank API"}

# ── Employees ──────────────────────────────────────────

@app.get("/employees")
def get_employees(
    department: str = None,
    country: str = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = "SELECT * FROM employees WHERE 1=1"
    if department:
        query += f" AND department = '{department}'"
    if country:
        query += f" AND country = '{country}'"
    query += f" LIMIT {limit}"
    result = db.execute(text(query))
    return result.mappings().all()

@app.get("/employees/summary")
def get_employee_summary(db: Session = Depends(get_db)):
    query = """
        SELECT 
            department,
            COUNT(*) as headcount,
            ROUND(AVG(salary)::numeric, 2) as avg_salary,
            ROUND(AVG(total_compensation)::numeric, 2) as avg_total_comp,
            ROUND(SUM(salary)::numeric, 2) as total_salary_cost
        FROM employees
        GROUP BY department
        ORDER BY headcount DESC
    """
    result = db.execute(text(query))
    return result.mappings().all()

@app.get("/employees/by-country")
def get_employees_by_country(db: Session = Depends(get_db)):
    query = """
        SELECT 
            country,
            COUNT(*) as headcount,
            ROUND(AVG(salary)::numeric, 2) as avg_salary
        FROM employees
        GROUP BY country
        ORDER BY headcount DESC
    """
    result = db.execute(text(query))
    return result.mappings().all()

# ── P&L Actual ─────────────────────────────────────────

@app.get("/pnl/actual")
def get_pnl_actual(
    country: str = None,
    department: str = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = "SELECT * FROM pnl_actual WHERE 1=1"
    if country:
        query += f" AND country = '{country}'"
    if department:
        query += f" AND department = '{department}'"
    query += f" ORDER BY month DESC LIMIT {limit}"
    result = db.execute(text(query))
    return result.mappings().all()

@app.get("/pnl/actual/summary")
def get_pnl_actual_summary(db: Session = Depends(get_db)):
    query = """
        SELECT
            country,
            department,
            ROUND(SUM(revenue)::numeric, 2) as total_revenue,
            ROUND(SUM(operating_expenses)::numeric, 2) as total_expenses,
            ROUND(SUM(net_profit_after_tax)::numeric, 2) as total_net_profit
        FROM pnl_actual
        GROUP BY country, department
        ORDER BY total_net_profit DESC
    """
    result = db.execute(text(query))
    return result.mappings().all()

@app.get("/pnl/actual/by-country")
def get_pnl_by_country(db: Session = Depends(get_db)):
    query = """
        SELECT
            country,
            ROUND(SUM(revenue)::numeric, 2) as total_revenue,
            ROUND(SUM(operating_expenses)::numeric, 2) as total_expenses,
            ROUND(SUM(net_profit_after_tax)::numeric, 2) as total_net_profit
        FROM pnl_actual
        GROUP BY country
        ORDER BY total_net_profit DESC
    """
    result = db.execute(text(query))
    return result.mappings().all()

# ── P&L Budget ─────────────────────────────────────────

@app.get("/pnl/budget")
def get_pnl_budget(
    country: str = None,
    department: str = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = "SELECT * FROM pnl_budget WHERE 1=1"
    if country:
        query += f" AND country = '{country}'"
    if department:
        query += f" AND department = '{department}'"
    query += f" ORDER BY month DESC LIMIT {limit}"
    result = db.execute(text(query))
    return result.mappings().all()

@app.get("/pnl/budget/summary")
def get_pnl_budget_summary(db: Session = Depends(get_db)):
    query = """
        SELECT
            country,
            department,
            ROUND(SUM(budgeted_revenue)::numeric, 2) as total_budgeted_revenue,
            ROUND(SUM(budgeted_expenses)::numeric, 2) as total_budgeted_expenses,
            ROUND(SUM(budgeted_net_profit_after_tax)::numeric, 2) as total_budgeted_profit,
            ROUND(SUM(variance_net_profit)::numeric, 2) as total_variance
        FROM pnl_budget
        GROUP BY country, department
        ORDER BY total_budgeted_profit DESC
    """
    result = db.execute(text(query))
    return result.mappings().all()

@app.get("/pnl/variance")
def get_pnl_variance(db: Session = Depends(get_db)):
    query = """
        SELECT
            country,
            ROUND(SUM(variance_revenue)::numeric, 2) as total_variance_revenue,
            ROUND(SUM(variance_expenses)::numeric, 2) as total_variance_expenses,
            ROUND(SUM(variance_net_profit)::numeric, 2) as total_variance_profit
        FROM pnl_budget
        GROUP BY country
        ORDER BY total_variance_profit DESC
    """
    result = db.execute(text(query))
    return result.mappings().all()
