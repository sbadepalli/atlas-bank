from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

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

class PnLActual(Base):
    __tablename__ = "pnl_actual"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String)
    department = Column(String)
    month = Column(Date)
    revenue = Column(Float)
    interest_income = Column(Float)
    fee_income = Column(Float)
    operating_expenses = Column(Float)
    loan_loss_provisions = Column(Float)
    net_income = Column(Float)
    tax = Column(Float)
    net_profit_after_tax = Column(Float)

class PnLBudget(Base):
    __tablename__ = "pnl_budget"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String)
    department = Column(String)
    month = Column(Date)
    budgeted_revenue = Column(Float)
    budgeted_expenses = Column(Float)
    budgeted_net_income = Column(Float)
    budgeted_tax = Column(Float)
    budgeted_net_profit_after_tax = Column(Float)
    variance_revenue = Column(Float)
    variance_expenses = Column(Float)
    variance_net_profit = Column(Float)
