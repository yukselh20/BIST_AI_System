import sys
import os
from datetime import datetime

# Resolve project imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from integration.tefas_client import TefasClient
from core.database import SessionLocal, FundFlow, init_db

def save_fund_data(data_list):
    if not data_list:
        return

    session = SessionLocal()
    try:
        for item in data_list:
            # Parse date string "YYYY-MM-DD" -> datetime
            dt = datetime.strptime(item['date'], "%Y-%m-%d")
            
            # Check duplicate (Fund + Date)
            exists = session.query(FundFlow).filter_by(
                fund_code=item['fund_code'], 
                date=dt
            ).first()
            
            if not exists:
                fund_row = FundFlow(
                    fund_code=item['fund_code'],
                    stock_allocation_pct=item['stock_allocation_pct'],
                    total_value=item['total_value'],
                    date=dt
                )
                session.add(fund_row)
                print(f"[+] Saved {item['fund_code']}: {item['stock_allocation_pct']}% Stock Alloc.")
            else:
                print(f"[*] {item['fund_code']} for {item['date']} already exists. Skipping.")

        session.commit()
    except Exception as e:
        print(f"[!] DB Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_db()
    
    print("--- Fetching TEFAS Flow Data ---")
    client = TefasClient()
    
    # Get data for key institutional funds
    data = client.get_institutional_stock_sentiment()
    
    if data:
        save_fund_data(data)
    else:
        print("[!] No TEFAS data retrieved.")
