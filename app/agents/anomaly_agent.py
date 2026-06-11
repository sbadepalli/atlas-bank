import anthropic
from sqlalchemy import text
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_pnl_data(db: Session, country: str = None, department: str = None) -> list:
    query = """
        SELECT 
            country,
            department,
            month,
            revenue,
            operating_expenses,
            net_profit_after_tax,
            loan_loss_provisions
        FROM pnl_actual
        WHERE 1=1
    """
    if country:
        query += f" AND country = '{country}'"
    if department:
        query += f" AND department = '{department}'"
    query += " ORDER BY country, department, month"
    
    result = db.execute(text(query))
    return [dict(row) for row in result.mappings().all()]

def anomaly_agent(db: Session, country: str = None, department: str = None) -> dict:
    try:
        # step 1 - get P&L data
        data = get_pnl_data(db, country, department)

        if not data:
            return {"error": "No data found for the given filters"}

        # step 2 - ask Claude to detect anomalies
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    You are a financial risk analyst for Atlas Commercial Bank.
                    Analyze this monthly P&L data and detect any anomalies or unusual patterns.
                    
                    Data: {data}
                    
                    Look for:
                    1. Sudden revenue drops or spikes (more than 20% change month over month)
                    2. Unusual increases in loan loss provisions
                    3. Operating expenses growing faster than revenue
                    4. Months where net profit turned negative
                    5. Any other unusual patterns
                    
                    Format your response as:
                    - Number of anomalies found
                    - List each anomaly with: month, country, department, what happened, severity (Low/Medium/High)
                    - Overall risk assessment
                    
                    Be specific with numbers and dates.
                    """
                }
            ]
        )

        return {
            "filters": {
                "country": country or "All",
                "department": department or "All"
            },
            "anomalies": response.content[0].text.strip()
        }

    except Exception as e:
        return {"error": str(e)}
