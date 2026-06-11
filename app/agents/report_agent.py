import anthropic
from sqlalchemy import text
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_report_data(db: Session, country: str = None) -> dict:
    # P&L summary
    pnl_query = """
        SELECT
            country,
            department,
            ROUND(SUM(revenue)::numeric, 2) as total_revenue,
            ROUND(SUM(operating_expenses)::numeric, 2) as total_expenses,
            ROUND(SUM(net_profit_after_tax)::numeric, 2) as total_net_profit,
            ROUND(AVG(loan_loss_provisions)::numeric, 2) as avg_loan_loss
        FROM pnl_actual
        WHERE 1=1
    """
    if country:
        pnl_query += f" AND country = '{country}'"
    pnl_query += " GROUP BY country, department ORDER BY total_net_profit DESC"

    # budget summary
    budget_query = """
        SELECT
            country,
            ROUND(SUM(budgeted_revenue)::numeric, 2) as total_budgeted_revenue,
            ROUND(SUM(budgeted_net_profit_after_tax)::numeric, 2) as total_budgeted_profit,
            ROUND(SUM(variance_net_profit)::numeric, 2) as total_variance
        FROM pnl_budget
        WHERE 1=1
    """
    if country:
        budget_query += f" AND country = '{country}'"
    budget_query += " GROUP BY country ORDER BY total_budgeted_profit DESC"

    # workforce summary
    workforce_query = """
        SELECT
            department,
            COUNT(*) as headcount,
            ROUND(AVG(salary)::numeric, 2) as avg_salary,
            ROUND(SUM(total_compensation)::numeric, 2) as total_comp_cost
        FROM employees
        WHERE 1=1
    """
    if country:
        workforce_query += f" AND country = '{country}'"
    workforce_query += " GROUP BY department ORDER BY headcount DESC"

    pnl_data = [dict(row) for row in db.execute(text(pnl_query)).mappings().all()]
    budget_data = [dict(row) for row in db.execute(text(budget_query)).mappings().all()]
    workforce_data = [dict(row) for row in db.execute(text(workforce_query)).mappings().all()]

    return {
        "pnl": pnl_data,
        "budget": budget_data,
        "workforce": workforce_data
    }

def report_agent(db: Session, country: str = None, report_type: str = "full") -> dict:
    try:
        # step 1 - get data
        data = get_report_data(db, country)

        # step 2 - ask Claude to generate report
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    You are a senior financial analyst at Atlas Commercial Bank.
                    Generate a professional financial report based on this data.
                    
                    Country Filter: {country or 'All Countries'}
                    Report Type: {report_type}
                    Report Date: {datetime.now().strftime('%B %d, %Y')}
                    
                    Data:
                    P&L Summary: {data['pnl']}
                    Budget Summary: {data['budget']}
                    Workforce Summary: {data['workforce']}
                    
                    Generate a professional report with these sections:
                    1. Executive Summary (3-4 sentences)
                    2. Financial Performance (revenue, expenses, profit highlights)
                    3. Budget vs Actual Analysis (variance highlights)
                    4. Workforce Analysis (headcount, compensation costs)
                    5. Key Risks and Opportunities
                    6. Recommendations (3-5 bullet points)
                    
                    Use professional banking language.
                    Include specific numbers and percentages.
                    Format it clearly with headers and bullet points.
                    """
                }
            ]
        )

        return {
            "report_date": datetime.now().strftime('%B %d, %Y'),
            "country": country or "All Countries",
            "report": response.content[0].text.strip()
        }

    except Exception as e:
        return {"error": str(e)}
