import sqlite3
import pandas as pd
import os

# Database path
# Database path
# Resolve project root from the script's location (assuming scripts/check_db.py)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'database', 'market_data.db')

def check_database():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    print(f"Checking database: {DB_PATH}")
    
    try:
        # Use pandas for pretty table printing
        conn = sqlite3.connect(DB_PATH)
        query = "SELECT * FROM tick_data ORDER BY id DESC LIMIT 5"
        
        df = pd.read_sql_query(query, conn)
        
        # Check specific symbol count
        count_query = "SELECT COUNT(*) as count FROM tick_data WHERE symbol='THYAO'"
        count_df = pd.read_sql_query(count_query, conn)
        thyao_count = count_df['count'].iloc[0]
        print(f"\nRecord count for THYAO: {thyao_count}")

        if df.empty:
            print("Database is empty.")
        else:
            print("\nLast 5 Records:")
            print(df.to_string(index=False))
            print(f"\nTotal Rows (Last 5 view): {len(df)}")
            
        conn.close()
        
    except Exception as e:
        print(f"Error reading database: {e}")

if __name__ == "__main__":
    check_database()
