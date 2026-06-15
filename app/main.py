from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.agents.query_agent import query_agent
from app.agents.anomaly_agent import anomaly_agent
from app.agents.report_agent import report_agent
from app.agents.rag_agent import rag_agent, save_report_to_rag
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Atlas Commercial Bank API",
    description="Financial data API for Atlas Commercial Bank",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
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

# ── Financials (Dimensional Model) ──────────────────────

@app.get("/financials/summary")
def get_financials_summary(
    scenario: str = "Actual",
    db: Session = Depends(get_db)
):
    """P&L summary by entity (country) - revenue, expenses, net profit in USD"""
    query = """
        SELECT
            e.country,
            e.currency,
            ROUND(SUM(CASE WHEN a.account_type = 'Revenue' THEN f.amount_usd ELSE 0 END)::numeric, 2) as total_revenue,
            ROUND(SUM(CASE WHEN a.account_type = 'Expense' THEN f.amount_usd ELSE 0 END)::numeric, 2) as total_expenses,
            ROUND(SUM(CASE WHEN a.account_type = 'Revenue' THEN f.amount_usd ELSE -f.amount_usd END)::numeric, 2) as net_profit
        FROM fact_financials f
        JOIN dim_entity e ON f.entity_id = e.entity_id
        JOIN dim_account a ON f.account_id = a.account_id
        JOIN dim_scenario s ON f.scenario_id = s.scenario_id
        WHERE s.scenario_name = :scenario
        GROUP BY e.country, e.currency
        ORDER BY net_profit DESC
    """
    result = db.execute(text(query), {"scenario": scenario})
    return result.mappings().all()

@app.get("/financials/by-department")
def get_financials_by_department(
    country: str,
    scenario: str = "Actual",
    db: Session = Depends(get_db)
):
    """P&L breakdown by department for a given country"""
    query = """
        SELECT
            d.department_name,
            ROUND(SUM(CASE WHEN a.account_type = 'Revenue' THEN f.amount_usd ELSE 0 END)::numeric, 2) as total_revenue,
            ROUND(SUM(CASE WHEN a.account_type = 'Expense' THEN f.amount_usd ELSE 0 END)::numeric, 2) as total_expenses,
            ROUND(SUM(CASE WHEN a.account_type = 'Revenue' THEN f.amount_usd ELSE -f.amount_usd END)::numeric, 2) as net_profit
        FROM fact_financials f
        JOIN dim_entity e ON f.entity_id = e.entity_id
        JOIN dim_department d ON f.department_id = d.department_id
        JOIN dim_account a ON f.account_id = a.account_id
        JOIN dim_scenario s ON f.scenario_id = s.scenario_id
        WHERE e.country = :country AND s.scenario_name = :scenario
        GROUP BY d.department_name
        ORDER BY net_profit DESC
    """
    result = db.execute(text(query), {"country": country, "scenario": scenario})
    return result.mappings().all()

@app.get("/financials/by-account")
def get_financials_by_account(
    country: str,
    department: str,
    scenario: str = "Actual",
    db: Session = Depends(get_db)
):
    """P&L breakdown by account for a given country + department"""
    query = """
        SELECT
            a.account_code,
            a.account_name,
            a.account_group,
            a.account_category,
            a.account_type,
            ROUND(SUM(f.amount_usd)::numeric, 2) as total_amount_usd
        FROM fact_financials f
        JOIN dim_entity e ON f.entity_id = e.entity_id
        JOIN dim_department d ON f.department_id = d.department_id
        JOIN dim_account a ON f.account_id = a.account_id
        JOIN dim_scenario s ON f.scenario_id = s.scenario_id
        WHERE e.country = :country AND d.department_name = :department AND s.scenario_name = :scenario
        GROUP BY a.account_code, a.account_name, a.account_group, a.account_category, a.account_type
        ORDER BY a.account_code
    """
    result = db.execute(text(query), {"country": country, "department": department, "scenario": scenario})
    return result.mappings().all()

@app.get("/financials/monthly")
def get_financials_monthly(
    country: str,
    department: str,
    account_code: str = None,
    scenario: str = "Actual",
    db: Session = Depends(get_db)
):
    """Monthly trend for a country + department (optionally filtered by account)"""
    query = """
        SELECT
            p.period_date,
            a.account_name,
            ROUND(SUM(f.amount_usd)::numeric, 2) as amount_usd,
            ROUND(SUM(f.amount_local)::numeric, 2) as amount_local,
            e.currency
        FROM fact_financials f
        JOIN dim_entity e ON f.entity_id = e.entity_id
        JOIN dim_department d ON f.department_id = d.department_id
        JOIN dim_account a ON f.account_id = a.account_id
        JOIN dim_scenario s ON f.scenario_id = s.scenario_id
        JOIN dim_period p ON f.period_id = p.period_id
        WHERE e.country = :country AND d.department_name = :department AND s.scenario_name = :scenario
    """
    params = {"country": country, "department": department, "scenario": scenario}
    if account_code:
        query += " AND a.account_code = :account_code"
        params["account_code"] = account_code
    query += " GROUP BY p.period_date, a.account_name, e.currency ORDER BY p.period_date ASC"

    result = db.execute(text(query), params)
    return result.mappings().all()

@app.get("/financials/variance")
def get_financials_variance(
    db: Session = Depends(get_db)
):
    """Budget vs Actual variance by country (for overlapping periods - 2025+)"""
    query = """
        WITH budget AS (
            SELECT e.country,
                   ROUND(SUM(CASE WHEN a.account_type = 'Revenue' THEN f.amount_usd ELSE -f.amount_usd END)::numeric, 2) as budget_profit,
                   ROUND(SUM(CASE WHEN a.account_type = 'Revenue' THEN f.amount_usd ELSE 0 END)::numeric, 2) as budget_revenue
            FROM fact_financials f
            JOIN dim_entity e ON f.entity_id = e.entity_id
            JOIN dim_account a ON f.account_id = a.account_id
            JOIN dim_scenario s ON f.scenario_id = s.scenario_id
            WHERE s.scenario_name = 'Budget'
            GROUP BY e.country
        ),
        forecast AS (
            SELECT e.country,
                   ROUND(SUM(CASE WHEN a.account_type = 'Revenue' THEN f.amount_usd ELSE -f.amount_usd END)::numeric, 2) as forecast_profit,
                   ROUND(SUM(CASE WHEN a.account_type = 'Revenue' THEN f.amount_usd ELSE 0 END)::numeric, 2) as forecast_revenue
            FROM fact_financials f
            JOIN dim_entity e ON f.entity_id = e.entity_id
            JOIN dim_account a ON f.account_id = a.account_id
            JOIN dim_scenario s ON f.scenario_id = s.scenario_id
            WHERE s.scenario_name = 'Forecast'
            GROUP BY e.country
        )
        SELECT
            b.country,
            b.budget_revenue,
            f.forecast_revenue,
            b.budget_profit,
            f.forecast_profit,
            ROUND((f.forecast_revenue - b.budget_revenue)::numeric, 2) as variance_revenue,
            ROUND((f.forecast_profit - b.budget_profit)::numeric, 2) as variance_profit
        FROM budget b
        JOIN forecast f ON b.country = f.country
        ORDER BY variance_profit DESC
    """
    result = db.execute(text(query))
    return result.mappings().all()
@app.get("/employees/comp-by-country")
def get_comp_by_country(
    department: str,
    db: Session = Depends(get_db)
):
    """Compensation breakdown by country for a given department"""
    query = """
        SELECT
            country,
            COUNT(*) as headcount,
            ROUND(AVG(salary)::numeric, 2) as avg_salary,
            ROUND(AVG(ic)::numeric, 2) as avg_ic,
            ROUND(AVG(rsu)::numeric, 2) as avg_rsu,
            ROUND(AVG(total_compensation)::numeric, 2) as avg_total_comp
        FROM employees
        WHERE department = :department
        GROUP BY country
        ORDER BY avg_total_comp DESC
    """
    result = db.execute(text(query), {"department": department})
    return result.mappings().all()

@app.get("/financials/variance-by-department")
def get_variance_by_department(
    country: str,
    db: Session = Depends(get_db)
):
    """Budget vs Forecast variance by department for a given country"""
    query = """
        WITH budget AS (
            SELECT d.department_name,
                   ROUND(SUM(CASE WHEN a.account_type = 'Revenue' THEN f.amount_usd ELSE 0 END)::numeric, 2) as budget_revenue,
                   ROUND(SUM(CASE WHEN a.account_type = 'Revenue' THEN f.amount_usd ELSE -f.amount_usd END)::numeric, 2) as budget_profit
            FROM fact_financials f
            JOIN dim_entity e ON f.entity_id = e.entity_id
            JOIN dim_department d ON f.department_id = d.department_id
            JOIN dim_account a ON f.account_id = a.account_id
            JOIN dim_scenario s ON f.scenario_id = s.scenario_id
            WHERE e.country = :country AND s.scenario_name = 'Budget'
            GROUP BY d.department_name
        ),
        forecast AS (
            SELECT d.department_name,
                   ROUND(SUM(CASE WHEN a.account_type = 'Revenue' THEN f.amount_usd ELSE 0 END)::numeric, 2) as forecast_revenue,
                   ROUND(SUM(CASE WHEN a.account_type = 'Revenue' THEN f.amount_usd ELSE -f.amount_usd END)::numeric, 2) as forecast_profit
            FROM fact_financials f
            JOIN dim_entity e ON f.entity_id = e.entity_id
            JOIN dim_department d ON f.department_id = d.department_id
            JOIN dim_account a ON f.account_id = a.account_id
            JOIN dim_scenario s ON f.scenario_id = s.scenario_id
            WHERE e.country = :country AND s.scenario_name = 'Forecast'
            GROUP BY d.department_name
        )
        SELECT
            b.department_name,
            b.budget_revenue, f.forecast_revenue,
            b.budget_profit, f.forecast_profit,
            ROUND((f.forecast_revenue - b.budget_revenue)::numeric, 2) as variance_revenue,
            ROUND((f.forecast_profit - b.budget_profit)::numeric, 2) as variance_profit
        FROM budget b
        JOIN forecast f ON b.department_name = f.department_name
        ORDER BY variance_profit DESC
    """
    result = db.execute(text(query), {"country": country})
    return result.mappings().all()

@app.get("/financials/variance-monthly")
def get_variance_monthly(
    country: str,
    db: Session = Depends(get_db)
):
    """Monthly Budget vs Forecast net profit trend for a given country"""
    query = """
        SELECT
            p.period_date,
            s.scenario_name,
            ROUND(SUM(CASE WHEN a.account_type = 'Revenue' THEN f.amount_usd ELSE -f.amount_usd END)::numeric, 2) as net_profit
        FROM fact_financials f
        JOIN dim_entity e ON f.entity_id = e.entity_id
        JOIN dim_account a ON f.account_id = a.account_id
        JOIN dim_scenario s ON f.scenario_id = s.scenario_id
        JOIN dim_period p ON f.period_id = p.period_id
        WHERE e.country = :country AND s.scenario_name IN ('Budget', 'Forecast')
        GROUP BY p.period_date, s.scenario_name
        ORDER BY p.period_date ASC
    """
    result = db.execute(text(query), {"country": country})
    rows = [dict(r) for r in result.mappings().all()]

    # pivot into {period_date, budget, forecast}
    pivot = {}
    for row in rows:
        pd_date = str(row["period_date"])
        if pd_date not in pivot:
            pivot[pd_date] = {"period_date": pd_date, "budget": None, "forecast": None}
        if row["scenario_name"] == "Budget":
            pivot[pd_date]["budget"] = row["net_profit"]
        else:
            pivot[pd_date]["forecast"] = row["net_profit"]

    return list(pivot.values())
@app.get("/employees/by-department-for-country")
def get_employees_by_department_for_country(
    country: str,
    db: Session = Depends(get_db)
):
    """Headcount and salary by department for a given country"""
    query = """
        SELECT
            department,
            COUNT(*) as headcount,
            ROUND(AVG(salary)::numeric, 2) as avg_salary,
            ROUND(AVG(total_compensation)::numeric, 2) as avg_total_comp
        FROM employees
        WHERE country = :country
        GROUP BY department
        ORDER BY headcount DESC
    """
    result = db.execute(text(query), {"country": country})
    return result.mappings().all()
