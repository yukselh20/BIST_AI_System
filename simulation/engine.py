import sys
import os
import pandas as pd
from backtesting import Backtest

# Ensure project root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

from core.feature_engine import fetch_and_process_data

def run_simulation(symbol, strategy_class, cash=100000, commission=0.002, timeframe='1min', limit=5000):
    """
    Runs a backtest simulation for a given symbol and strategy.
    
    Args:
        symbol (str): Stock symbol (e.g., 'THYAO').
        strategy_class (class): The strategy class to run (must inherit from Backtesting.Strategy).
        cash (int): Initial capital.
        commission (float): Transaction cost (e.g., 0.002 for 0.2%).
        timeframe (str): Data timeframe.
        limit (int): Amount of historical data to fetch.
        
    Returns:
        stats (pd.Series): Backtest performance statistics.
    """
    print(f"[*] Fetching data for {symbol}...")
    
    # 1. Fetch Data
    df = fetch_and_process_data(symbol, timeframe=timeframe, limit=limit)
    
    if df.empty:
        print(f"[!] No data found for {symbol}. Aborting simulation.")
        return None

    # 2. Prepare Data for Backtesting.py
    # Backtesting.py expects columns: 'Open', 'High', 'Low', 'Close', 'Volume' (Capitalized)
    # Our DF has: 'open', 'high', 'low', 'close', 'volume' (Lowercase)
    
    df_bt = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    
    # Ensure index is datetime (already done in feature_engine but double check)
    if not isinstance(df_bt.index, pd.DatetimeIndex):
        df_bt.index = pd.to_datetime(df_bt.index)

    # 3. Initialize Backtest
    bt = Backtest(
        df_bt, 
        strategy_class,
        cash=cash,
        commission=commission,
        exclusive_orders=True # Closes previous trade before opening new one (good for simple strategies)
    )
    
    print(f"[*] Running Simulation: {strategy_class.__name__} on {symbol}...")
    stats = bt.run()
    
    # 4. Generate Plot (Optional - saves to HTML)
    plot_filename = f"simulation_report_{symbol}_{strategy_class.__name__}.html"
    try:
        bt.plot(filename=plot_filename, open_browser=False)
        print(f"[+] Report saved to {plot_filename}")
    except Exception as e:
        print(f"[!] Plot generation failed (Headless environment?): {e}")
        
    return stats
