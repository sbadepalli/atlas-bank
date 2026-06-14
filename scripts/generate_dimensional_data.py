import pandas as pd
import numpy as np
import random
from datetime import date

np.random.seed(42)
random.seed(42)

# ── Dimension Data ──────────────────────────────────────

ENTITIES = [
    {"entity_id": 1, "entity_name": "Atlas USA", "country": "USA", "currency": "USD"},
    {"entity_id": 2, "entity_name": "Atlas UK", "country": "UK", "currency": "GBP"},
    {"entity_id": 3, "entity_name": "Atlas Germany", "country": "Germany", "currency": "EUR"},
    {"entity_id": 4, "entity_name": "Atlas Singapore", "country": "Singapore", "currency": "SGD"},
    {"entity_id": 5, "entity_name": "Atlas UAE", "country": "UAE", "currency": "AED"},
]

DEPARTMENTS = [
    {"department_id": 1, "department_name": "Finance"},
    {"department_id": 2, "department_name": "Accounting"},
    {"department_id": 3, "department_name": "Human Resources"},
    {"department_id": 4, "department_name": "Facilities"},
    {"department_id": 5, "department_name": "Cloud Ops"},
    {"department_id": 6, "department_name": "Modeling"},
    {"department_id": 7, "department_name": "Engineering"},
    {"department_id": 8, "department_name": "Platform & Software"},
]

ACCOUNTS = [
    {"account_id": 1, "account_code": "4000", "account_name": "Interest Income", "account_group": "Lending Income", "account_category": "Income", "account_type": "Revenue"},
    {"account_id": 2, "account_code": "4010", "account_name": "Investment Income", "account_group": "Lending Income", "account_category": "Income", "account_type": "Revenue"},
    {"account_id": 3, "account_code": "4100", "account_name": "Transaction Fees", "account_group": "Fee Income", "account_category": "Income", "account_type": "Revenue"},
    {"account_id": 4, "account_code": "4110", "account_name": "Advisory & Service Fees", "account_group": "Fee Income", "account_category": "Income", "account_type": "Revenue"},
    {"account_id": 5, "account_code": "5000", "account_name": "Salaries & Wages", "account_group": "Compensation", "account_category": "Operating Expense", "account_type": "Expense"},
    {"account_id": 6, "account_code": "5010", "account_name": "Bonuses & Incentives (IC/RSU)", "account_group": "Compensation", "account_category": "Operating Expense", "account_type": "Expense"},
    {"account_id": 7, "account_code": "5100", "account_name": "Software Licenses", "account_group": "Technology", "account_category": "Operating Expense", "account_type": "Expense"},
    {"account_id": 8, "account_code": "5110", "account_name": "Cloud Infrastructure", "account_group": "Technology", "account_category": "Operating Expense", "account_type": "Expense"},
    {"account_id": 9, "account_code": "5200", "account_name": "Rent & Utilities", "account_group": "Occupancy", "account_category": "Operating Expense", "account_type": "Expense"},
    {"account_id": 10, "account_code": "5210", "account_name": "Office Maintenance", "account_group": "Occupancy", "account_category": "Operating Expense", "account_type": "Expense"},
    {"account_id": 11, "account_code": "5300", "account_name": "Consulting & Legal", "account_group": "Professional Services", "account_category": "Operating Expense", "account_type": "Expense"},
    {"account_id": 12, "account_code": "5400", "account_name": "Travel & Entertainment", "account_group": "General & Admin", "account_category": "Operating Expense", "account_type": "Expense"},
    {"account_id": 13, "account_code": "5410", "account_name": "Marketing & Advertising", "account_group": "General & Admin", "account_category": "Operating Expense", "account_type": "Expense"},
    {"account_id": 14, "account_code": "6000", "account_name": "Loan Loss Provisions", "account_group": "Credit Risk", "account_category": "Credit Risk", "account_type": "Expense"},
    {"account_id": 15, "account_code": "7000", "account_name": "Income Tax Expense", "account_group": "Tax", "account_category": "Tax", "account_type": "Expense"},
]

SCENARIOS = [
    {"scenario_id": 1, "scenario_name": "Actual"},
    {"scenario_id": 2, "scenario_name": "Budget"},
    {"scenario_id": 3, "scenario_name": "Forecast"},
]

# Periods: Actual = 2020-2024 (60 months), Budget/Forecast = 2025-2026 (24 months)
def build_periods():
    periods = []
    period_id = 1
    for year in range(2020, 2027):
        for month in range(1, 13):
            if year == 2026 and month > 12:
                continue
            periods.append({
                "period_id": period_id,
                "year": year,
                "month": month,
                "period_date": date(year, month, 1)
            })
            period_id += 1
    return periods

PERIODS = build_periods()

# FX base rates (local currency per 1 USD)
FX_BASE = {"USD": 1.0, "GBP": 0.79, "EUR": 0.92, "SGD": 1.35, "AED": 3.67}

def build_fx_rates():
    rates = []
    for currency, base_rate in FX_BASE.items():
        for p in PERIODS:
            # add small monthly variation (+/- 3%)
            variation = 1 + random.uniform(-0.03, 0.03)
            rates.append({
                "currency": currency,
                "period_id": p["period_id"],
                "rate_to_usd": round(base_rate * variation, 4)
            })
    return rates

FX_RATES = build_fx_rates()
FX_LOOKUP = {(r["currency"], r["period_id"]): r["rate_to_usd"] for r in FX_RATES}

# ── Fact Data Generation ─────────────────────────────────

# base monthly amount ranges per account (in USD, before entity scaling)
ACCOUNT_BASE_RANGES = {
    1: (3000000, 15000000),   # Interest Income
    2: (500000, 3000000),     # Investment Income
    3: (1000000, 6000000),    # Transaction Fees
    4: (500000, 3000000),     # Advisory & Service Fees
    5: (1500000, 6000000),    # Salaries & Wages
    6: (300000, 1500000),     # Bonuses (IC/RSU)
    7: (100000, 600000),      # Software Licenses
    8: (200000, 1000000),     # Cloud Infrastructure
    9: (150000, 700000),      # Rent & Utilities
    10: (50000, 250000),      # Office Maintenance
    11: (100000, 500000),     # Consulting & Legal
    12: (50000, 300000),      # Travel & Entertainment
    13: (100000, 500000),     # Marketing & Advertising
    14: (200000, 1500000),    # Loan Loss Provisions
    15: (500000, 3000000),    # Income Tax Expense
}

# entity scaling factor (some entities are bigger than others)
ENTITY_SCALE = {1: 1.0, 2: 0.85, 3: 0.80, 4: 0.65, 5: 0.55}

def generate_facts():
    records = []
    actual_periods = [p for p in PERIODS if p["year"] <= 2024]
    plan_periods = [p for p in PERIODS if p["year"] >= 2025]

    for entity in ENTITIES:
        entity_scale = ENTITY_SCALE[entity["entity_id"]]
        currency = entity["currency"]

        for dept in DEPARTMENTS:
            for account in ACCOUNTS:
                base_min, base_max = ACCOUNT_BASE_RANGES[account["account_id"]]
                base_amount = random.uniform(base_min, base_max) * entity_scale / len(DEPARTMENTS) * 4  # spread across depts

                # ACTUAL data (2020-2024)
                for i, p in enumerate(actual_periods):
                    growth = 1 + (i * 0.0015)
                    seasonality = 1 + 0.08 * np.sin(2 * np.pi * i / 12)
                    noise = random.uniform(0.95, 1.05)
                    amount_usd = round(base_amount * growth * seasonality * noise, 2)

                    fx_rate = FX_LOOKUP[(currency, p["period_id"])]
                    amount_local = round(amount_usd * fx_rate, 2)

                    records.append({
                        "entity_id": entity["entity_id"],
                        "department_id": dept["department_id"],
                        "account_id": account["account_id"],
                        "scenario_id": 1,  # Actual
                        "period_id": p["period_id"],
                        "amount_local": amount_local,
                        "amount_usd": amount_usd
                    })

                # BUDGET and FORECAST data (2025-2026)
                last_actual_amount = base_amount * (1 + (len(actual_periods) - 1) * 0.0015)
                for i, p in enumerate(plan_periods):
                    growth = 1 + (i * 0.002)
                    
                    for scenario_id in [2, 3]:  # Budget, Forecast
                        variation = random.uniform(0.97, 1.03) if scenario_id == 2 else random.uniform(0.95, 1.06)
                        amount_usd = round(last_actual_amount * growth * variation, 2)

                        fx_rate = FX_LOOKUP[(currency, p["period_id"])]
                        amount_local = round(amount_usd * fx_rate, 2)

                        records.append({
                            "entity_id": entity["entity_id"],
                            "department_id": dept["department_id"],
                            "account_id": account["account_id"],
                            "scenario_id": scenario_id,
                            "period_id": p["period_id"],
                            "amount_local": amount_local,
                            "amount_usd": amount_usd
                        })

    return pd.DataFrame(records)

if __name__ == "__main__":
    print("Generating dimension tables...")
    pd.DataFrame(ENTITIES).to_csv("data/dim_entity.csv", index=False)
    pd.DataFrame(DEPARTMENTS).to_csv("data/dim_department.csv", index=False)
    pd.DataFrame(ACCOUNTS).to_csv("data/dim_account.csv", index=False)
    pd.DataFrame(SCENARIOS).to_csv("data/dim_scenario.csv", index=False)
    pd.DataFrame(PERIODS).to_csv("data/dim_period.csv", index=False)
    pd.DataFrame(FX_RATES).to_csv("data/dim_fx_rate.csv", index=False)
    print("✅ Dimension tables generated")

    print("Generating fact table (this may take a moment)...")
    facts = generate_facts()
    facts.to_csv("data/fact_financials.csv", index=False)
    print(f"✅ Generated {len(facts)} fact rows")

    print("✅ All dimensional data generated successfully!")
