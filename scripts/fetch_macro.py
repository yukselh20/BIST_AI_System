import sys
import os
from datetime import datetime

# Resolve project imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from integration.evds_client import EvdsClient
from core.database import SessionLocal, MacroData, init_db

# USER API KEY
API_KEY = "qr7BBmch3C"

def save_macro_data(data):
    session = SessionLocal()
    try:
        # 1. Inflation
        if 'inflation_cpi' in data:
            # Check duplicates or just append? Appending is safer for history, 
            # but we should check if this month already exists to avoid spam.
            # Simplified: Just insert.
            
            # Date from EVDS usually textual: '01-11-2023' or '2023-11'
            # EvdsClient returns raw date string in 'inflation_date' if available, 
            # but let's just use current month start as approximation if parsing fails,
            # or better: rely on what client parsed.
            
            # For simplicity in this phase, we timestamp it with now() or specific date if critical.
            # Let's assume the value represents the "latest known".
            
            macro_inf = MacroData(
                indicator_name='inflation_cpi',
                value=data['inflation_cpi'],
                frequency='M',
                timestamp=datetime.now() # Ideally should be data's reference date
            )
            session.add(macro_inf)
            print(f"[+] Saved Inflation: {data['inflation_cpi']}%")

        # 2. Policy Rate
        if 'policy_rate' in data:
            macro_rate = MacroData(
                indicator_name='policy_rate',
                value=data['policy_rate'],
                frequency='W',
                timestamp=datetime.now()
            )
            session.add(macro_rate)
            print(f"[+] Saved Policy Rate: {data['policy_rate']}%")

        # 3. USD/TRY
        if 'usd_try' in data:
            macro_usd = MacroData(
                indicator_name='usd_try',
                value=data['usd_try'],
                frequency='D',
                timestamp=datetime.now()
            )
            session.add(macro_usd)
            print(f"[+] Saved USD/TRY: {data['usd_try']}")

        session.commit()
        print("[*] Database updated successfully.")
        
    except Exception as e:
        print(f"[!] DB Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    # Ensure tables exist
    init_db()
    
    print("--- Fetching Macro Data from TCMB EVDS ---")
    client = EvdsClient(API_KEY)
    data = client.get_macro_indicators()
    
    if data:
        print(f"[*] Data Received: {data}")
        save_macro_data(data)
    else:
        print("[!] No data received from EVDS (Check Key or Connection).")
