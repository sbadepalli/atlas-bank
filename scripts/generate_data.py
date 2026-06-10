import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import date, timedelta
import os

fake = Faker()
np.random.seed(42)
random.seed(42)

# Constants
COUNTRIES = ["USA", "UK", "Germany", "Singapore", "UAE"]
DEPARTMENTS = ["Finance", "Accounting", "Human Resources", 
               "Facilities", "Cloud Ops", "Modeling", 
               "Engineering", "Platform & Software"]

LOCATIONS = {
    "USA": "New York",
    "UK": "London",
    "Germany": "Frankfurt",
    "Singapore": "Singapore",
    "UAE": "Dubai"
}

HEADCOUNT = {
    "Engineering": 450,
    "Platform & Software": 350,
    "Finance": 250,
    "Modeling": 250,
    "Accounting": 200,
    "Cloud Ops": 200,
    "Human Resources": 150,
    "Facilities": 150
}

JOB_TITLES = {
    "Finance": ["Financial Analyst", "Senior Financial Analyst", "Finance Manager", "VP Finance", "CFO"],
    "Accounting": ["Accountant", "Senior Accountant", "Accounting Manager", "Controller", "VP Accounting"],
    "Human Resources": ["HR Coordinator", "HR Specialist", "HR Manager", "VP HR", "CHRO"],
    "Facilities": ["Facilities Coordinator", "Facilities Manager", "VP Facilities"],
    "Cloud Ops": ["Cloud Engineer", "Senior Cloud Engineer", "Cloud Architect", "VP Cloud Ops"],
    "Modeling": ["Quantitative Analyst", "Senior Quant Analyst", "Modeling Manager", "VP Modeling"],
    "Engineering": ["Software Engineer", "Senior Software Engineer", "Tech Lead", "Engineering Manager", "VP Engineering"],
    "Platform & Software": ["Platform Engineer", "Senior Platform Engineer", "Platform Architect", "VP Platform"]
}

SALARY_RANGES = {
    "Finance": (80000, 250000),
    "Accounting": (70000, 200000),
    "Human Resources": (65000, 180000),
    "Facilities": (50000, 120000),
    "Cloud Ops": (100000, 280000),
    "Modeling": (120000, 350000),
    "Engineering": (110000, 320000),
    "Platform & Software": (105000, 300000)
}

def generate_employees():
    employees = []
    emp_id = 1000
    managers = {}

    for dept, count in HEADCOUNT.items():
        dept_employees = []
        for i in range(count):
            country = random.choice(COUNTRIES)
            salary = round(random.uniform(*SALARY_RANGES[dept]), 2)
            ic = round(salary * random.uniform(0.1, 0.3), 2)
            rsu = round(salary * random.uniform(0.05, 0.25), 2)
            
            emp = {
                "employee_id": f"ATL{emp_id}",
                "full_name": fake.name(),
                "department": dept,
                "job_title": random.choice(JOB_TITLES[dept]),
                "country": country,
                "location": LOCATIONS[country],
                "salary": salary,
                "ic": ic,
                "rsu": rsu,
                "total_compensation": round(salary + ic + rsu, 2),
                "hire_date": fake.date_between(start_date=date(2015, 1, 1), end_date=date(2024, 12, 31)),
                "manager_id": None
            }
            dept_employees.append(emp)
            emp_id += 1

        # assign first employee as manager
        if dept_employees:
            managers[dept] = dept_employees[0]["employee_id"]
            for emp in dept_employees[1:]:
                emp["manager_id"] = managers[dept]

        employees.extend(dept_employees)

    return pd.DataFrame(employees)

def generate_pnl_actual():
    records = []
    start_date = date(2020, 1, 1)

    for country in COUNTRIES:
        for dept in DEPARTMENTS:
            base_revenue = random.uniform(5000000, 50000000)
            base_expenses = base_revenue * random.uniform(0.5, 0.75)

            for month in range(60):
                current_date = date(start_date.year + (start_date.month + month - 1) // 12,
                                  (start_date.month + month - 1) % 12 + 1, 1)
                
                # add growth trend and seasonality
                growth = 1 + (month * 0.002)
                seasonality = 1 + 0.1 * np.sin(2 * np.pi * month / 12)
                
                interest_income = round(base_revenue * 0.6 * growth * seasonality * random.uniform(0.95, 1.05), 2)
                fee_income = round(base_revenue * 0.4 * growth * seasonality * random.uniform(0.95, 1.05), 2)
                revenue = round(interest_income + fee_income, 2)
                operating_expenses = round(base_expenses * growth * random.uniform(0.95, 1.05), 2)
                loan_loss_provisions = round(revenue * random.uniform(0.01, 0.05), 2)
                net_income = round(revenue - operating_expenses - loan_loss_provisions, 2)
                tax = round(max(net_income * 0.25, 0), 2)
                net_profit_after_tax = round(net_income - tax, 2)

                records.append({
                    "country": country,
                    "department": dept,
                    "month": current_date,
                    "revenue": revenue,
                    "interest_income": interest_income,
                    "fee_income": fee_income,
                    "operating_expenses": operating_expenses,
                    "loan_loss_provisions": loan_loss_provisions,
                    "net_income": net_income,
                    "tax": tax,
                    "net_profit_after_tax": net_profit_after_tax
                })

    return pd.DataFrame(records)

def generate_pnl_budget():
    records = []
    start_date = date(2025, 1, 1)

    for country in COUNTRIES:
        for dept in DEPARTMENTS:
            base_revenue = random.uniform(5000000, 50000000)
            base_expenses = base_revenue * random.uniform(0.5, 0.75)

            for month in range(24):
                current_date = date(start_date.year + (start_date.month + month - 1) // 12,
                                  (start_date.month + month - 1) % 12 + 1, 1)

                growth = 1 + (month * 0.003)
                budgeted_revenue = round(base_revenue * growth * random.uniform(0.98, 1.02), 2)
                budgeted_expenses = round(base_expenses * growth * random.uniform(0.98, 1.02), 2)
                budgeted_net_income = round(budgeted_revenue - budgeted_expenses, 2)
                budgeted_tax = round(max(budgeted_net_income * 0.25, 0), 2)
                budgeted_net_profit_after_tax = round(budgeted_net_income - budgeted_tax, 2)

                # variance vs budget (simulate actuals slightly different)
                variance_revenue = round(budgeted_revenue * random.uniform(-0.05, 0.05), 2)
                variance_expenses = round(budgeted_expenses * random.uniform(-0.05, 0.05), 2)
                variance_net_profit = round(variance_revenue - variance_expenses, 2)

                records.append({
                    "country": country,
                    "department": dept,
                    "month": current_date,
                    "budgeted_revenue": budgeted_revenue,
                    "budgeted_expenses": budgeted_expenses,
                    "budgeted_net_income": budgeted_net_income,
                    "budgeted_tax": budgeted_tax,
                    "budgeted_net_profit_after_tax": budgeted_net_profit_after_tax,
                    "variance_revenue": variance_revenue,
                    "variance_expenses": variance_expenses,
                    "variance_net_profit": variance_net_profit
                })

    return pd.DataFrame(records)

if __name__ == "__main__":
    print("Generating employee data...")
    employees = generate_employees()
    employees.to_csv("data/employees.csv", index=False)
    print(f"✅ Generated {len(employees)} employees")

    print("Generating P&L actual data...")
    pnl_actual = generate_pnl_actual()
    pnl_actual.to_csv("data/pnl_actual.csv", index=False)
    print(f"✅ Generated {len(pnl_actual)} P&L actual rows")

    print("Generating P&L budget data...")
    pnl_budget = generate_pnl_budget()
    pnl_budget.to_csv("data/pnl_budget.csv", index=False)
    print(f"✅ Generated {len(pnl_budget)} P&L budget rows")

    print("✅ All data generated successfully!")
