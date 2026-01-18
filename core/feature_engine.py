import pandas as pd
import pandas_ta as ta
import sys
import os
from sqlalchemy.orm import Session

# Ensure we can import from core
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

from core.database import SessionLocal, TickData, engine

def fetch_and_process_data(symbol, timeframe='1min', limit=5000):
    """
    Fetches raw tick data from DB, resamples to OHLC, and calculates indicators.
    
    Args:
        symbol (str): Stock symbol (e.g., 'THYAO')
        timeframe (str): Resample timeframe (e.g., '1min')
        limit (int): Number of tick records to fetch
        
    Returns:
        pd.DataFrame: Processed dataframe with OHLCV and indicators.
    """
    # 1. Fetch Data
    query = f"SELECT * FROM tick_data WHERE symbol = '{symbol}' ORDER BY timestamp DESC LIMIT {limit}"
    
    try:
        df = pd.read_sql(query, engine)
    except Exception as e:
        print(f"[!] Error fetching data: {e}")
        return pd.DataFrame()

    if df.empty:
        print(f"[!] No data found for {symbol}")
        return pd.DataFrame()

    # Sort by time ascending for proper resampling
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    df.set_index('timestamp', inplace=True)

    # 2. Resample (Tick -> OHLCV)
    # Open: first, High: max, Low: min, Close: last, Volume: sum
    ohlc_dict = {
        'price': ['first', 'max', 'min', 'last'],
        'volume': 'sum'
    }
    
    # Resample
    df_resampled = df.resample(timeframe).agg(ohlc_dict)
    
    # Flatten multi-index columns
    df_resampled.columns = ['open', 'high', 'low', 'close', 'volume']
    
    # Drop empty bins (minutes with no trades)
    # Using dropna() changes the timeline continuity, but fills are dangerous for indicators if gap is huge.
    # For now, we drop empty bars.
    df_resampled.dropna(inplace=True)

    if df_resampled.empty:
        print("[!] Resampling resulted in empty dataframe (not enough density?)")
        return pd.DataFrame()

    # 3. Calculate Indicators
    try:
        # RSI 14
        df_resampled['RSI_14'] = ta.rsi(df_resampled['close'], length=14)
        
        # SMA 50
        df_resampled['SMA_50'] = ta.sma(df_resampled['close'], length=50)
        
        # EMA 200 (Trend)
        df_resampled['EMA_200'] = ta.ema(df_resampled['close'], length=200)
        
        # MACD (12, 26, 9)
        macd = ta.macd(df_resampled['close'], fast=12, slow=26, signal=9)
        if macd is not None:
             # macd returns 3 columns: MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
             # We rename them for simpler access
            df_resampled = pd.concat([df_resampled, macd], axis=1)

        # Bollinger Bands (20, 2)
        bbands = ta.bbands(df_resampled['close'], length=20, std=2.0)
        if bbands is not None:
            df_resampled = pd.concat([df_resampled, bbands], axis=1)
            
    except Exception as e:
        print(f"[!] Indicator calculation error: {e}")

    # 4. Cleaning (dropna)
    # Drops rows where indicators are NaN (e.g. first 200 rows for EMA_200)
    # Note: If data is insufficient (< 200 bars), this might result in empty DF.
    df_final = df_resampled.dropna()

    return df_final
