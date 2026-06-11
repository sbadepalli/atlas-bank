import anthropic
from sqlalchemy import text
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SCHEMA_INFO = """
You are a financial data analyst for Atlas Commercial Bank.
You have access to these PostgreSQL tables:

1. employees (employee_id, full_name, department, job_title, country, 
   location, salary, ic, rsu, total_compensation, hire_date, manager_id)

2. pnl_actual (id, country, department, month, revenue, interest_income,
   fee_income, operating_expenses, loan_loss_provisions, net_income, 
   tax, net_profit_after_tax)

3. pnl_budget (id, country, department, month, budgeted_revenue, 
   budgeted_expenses, budgeted_net_income, budgeted_tax,
   budgeted_net_profit_after_tax, variance_revenue, 
   variance_expenses, variance_net_profit)

Countries: USA, UK, Germany, Singapore, UAE
Departments: Finance, Accounting, Human Resources, Facilities, 
             Cloud Ops, Modeling, Engineering, Platform & Software

Your job is to convert natural language questions into PostgreSQL queries.
Return ONLY the SQL query, nothing else. No explanation, no markdown, no backticks.
"""

def generate_sql(question: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": f"{SCHEMA_INFO}\n\nQuestion: {question}\n\nSQL Query:"
            }
        ]
    )
    sql = response.content[0].text.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql

def query_agent(question: str, db: Session) -> dict:
    try:
        # step 1 - generate SQL from question
        sql = generate_sql(question)
        print(f"Generated SQL: {sql}")

        # step 2 - execute SQL
        result = db.execute(text(sql))
        rows = result.mappings().all()

        # step 3 - format results as list of dicts
        data = [dict(row) for row in rows]

        # step 4 - ask Claude to summarize the results
        summary_response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    Question: {question}
                    Data: {data}
                    
                    Please provide a clear, concise answer to the question based on the data.
                    Keep it to 2-3 sentences maximum.
                    """
                }
            ]
        )

        return {
            "question": question,
            "sql": sql,
            "data": data,
            "summary": summary_response.content[0].text.strip()
        }

    except Exception as e:
        return {
            "question": question,
            "error": str(e)
        }
