import sys
import os
import time

# Ensure imports work
sys.path.append(os.getcwd())

from core.feature_engine import fetch_and_process_data

def test_indicators():
    print("--- Testing Feature Engine ---")
    
    symbol = "THYAO" 
    # Use '1s' (1 second) timeframe for testing since we are generating mock data rapidly (0.1s interval).
    # '1min' would require too long to wait to get enough bars for indicators.
    timeframe = "1s" 
    
    print(f"Fetching data for {symbol}, resample={timeframe}...")
    
    df = fetch_and_process_data(symbol, timeframe=timeframe, limit=10000)
    
    if df.empty:
        print("[!] Resulting DataFrame is empty.")
        print("Reason: Probably not enough data points yet.")
        print(f"Advice: Please run 'mock_data_feeder.py' for at least a few minutes to generate > 200 {timeframe} bars.")
    else:
        print("\n[+] Success! Data processed with indicators.")
        print(f"Headers: {list(df.columns)}")
        print("\nLast 5 Rows:")
        # Select key columns to display
        cols = ['close', 'RSI_14', 'MACD_12_26_9', 'MACDs_12_26_9', 'BBM_20_2.0']
        # Filter only existing columns
        cols = [c for c in cols if c in df.columns]
        
        print(df[cols].tail(5))
        print(f"\nTotal Bars: {len(df)}")

if __name__ == "__main__":
    test_indicators()
