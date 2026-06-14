from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from app.database import Base

# ── Dimension Tables ────────────────────────────────────

class DimEntity(Base):
    __tablename__ = "dim_entity"
    entity_id = Column(Integer, primary_key=True)
    entity_name = Column(String)
    country = Column(String)
    currency = Column(String)

class DimDepartment(Base):
    __tablename__ = "dim_department"
    department_id = Column(Integer, primary_key=True)
    department_name = Column(String)

class DimAccount(Base):
    __tablename__ = "dim_account"
    account_id = Column(Integer, primary_key=True)
    account_code = Column(String)
    account_name = Column(String)
    account_group = Column(String)
    account_category = Column(String)
    account_type = Column(String)

class DimScenario(Base):
    __tablename__ = "dim_scenario"
    scenario_id = Column(Integer, primary_key=True)
    scenario_name = Column(String)

class DimPeriod(Base):
    __tablename__ = "dim_period"
    period_id = Column(Integer, primary_key=True)
    year = Column(Integer)
    month = Column(Integer)
    period_date = Column(Date)

class DimFxRate(Base):
    __tablename__ = "dim_fx_rate"
    id = Column(Integer, primary_key=True, autoincrement=True)
    currency = Column(String)
    period_id = Column(Integer, ForeignKey("dim_period.period_id"))
    rate_to_usd = Column(Float)

# ── Fact Table ──────────────────────────────────────────

class FactFinancials(Base):
    __tablename__ = "fact_financials"
    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(Integer, ForeignKey("dim_entity.entity_id"))
    department_id = Column(Integer, ForeignKey("dim_department.department_id"))
    account_id = Column(Integer, ForeignKey("dim_account.account_id"))
    scenario_id = Column(Integer, ForeignKey("dim_scenario.scenario_id"))
    period_id = Column(Integer, ForeignKey("dim_period.period_id"))
    amount_local = Column(Float)
    amount_usd = Column(Float)

# ── Existing Table (kept for employees) ─────────────────

class Employee(Base):
    __tablename__ = "employees"
    employee_id = Column(String, primary_key=True)
    full_name = Column(String)
    department = Column(String)
    job_title = Column(String)
    country = Column(String)
    location = Column(String)
    salary = Column(Float)
    ic = Column(Float)
    rsu = Column(Float)
    total_compensation = Column(Float)
    hire_date = Column(Date)
    manager_id = Column(String, nullable=True)
