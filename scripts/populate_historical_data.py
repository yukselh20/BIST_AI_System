import random
from datetime import datetime, timedelta
import sys
import os
import numpy as np

# Resolve project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from core.database import SessionLocal, TickData
from core.config_symbols import ALL_SYMBOLS as SYMBOLS

# Starting prices for simulation (Approximate realistic values)
START_PRICES = {
    'THYAO': 250.0, 'ASELS': 60.0, 'EREGL': 50.0, 'KAREL': 15.0,
    'KCHOL': 180.0, 'ENKAI': 40.0, 'FROTO': 950.0, 'KRDMD': 28.0,
    'CIMSA': 35.0, 'SAHOL': 90.0, 'OTKAR': 450.0
}

def populate_data():
    print("--- Starting Historical Data Population (Portfolio Mode) ---")
    
    session = SessionLocal()
    
    # Time settings
    # UTC now is safer for database timestamps
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    
    total_ticks_all = 0
    
    for symbol in SYMBOLS:
        print(f"Generating data for {symbol}...")
        
        current_time = start_time
        current_price = START_PRICES.get(symbol, 100.0) # Default 100 if missing
        
        ticks_to_save = []
        symbol_ticks = 0
        
        while current_time < end_time:
            # Generate 3 to 5 ticks per minute per symbol (less density for portfolio performance)
            num_ticks = random.randint(3, 5)
            
            for _ in range(num_ticks):
                # Random time within the minute
                tick_time = current_time + timedelta(seconds=random.randint(0, 59), microseconds=random.randint(0, 999999))
                
                # Random Walk: +/- 0.5%
                change_pct = random.uniform(-0.005, 0.005)
                current_price *= (1.0 + change_pct)
                
                if current_price < 0.1: current_price = 0.1
                    
                tick = TickData(
                    symbol=symbol,
                    price=round(current_price, 2),
                    volume=random.randint(10, 10000),
                    timestamp=tick_time,
                    received_at=datetime.utcnow()
                )
                ticks_to_save.append(tick)
                
            # Bulk save periodically
            if len(ticks_to_save) >= 2000:
                session.bulk_save_objects(ticks_to_save)
                session.commit()
                symbol_ticks += len(ticks_to_save)
                ticks_to_save = []
                
            current_time += timedelta(minutes=1)
            
        # Save remaining for this symbol
        if ticks_to_save:
            session.bulk_save_objects(ticks_to_save)
            session.commit()
            symbol_ticks += len(ticks_to_save)
            
        print(f" -> {symbol_ticks} records added for {symbol}.")
        total_ticks_all += symbol_ticks

    session.close()
    print(f"\n[+] Veritabanına başarıyla toplam {total_ticks_all} adet geçmiş veri eklendi.")

if __name__ == "__main__":
    populate_data()
