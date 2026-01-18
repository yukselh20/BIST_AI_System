import sys
from datetime import datetime, timedelta
from tefas import Crawler

class TefasClient:
    """
    Client for TEFAS (Turkey Electronic Fund Distribution Platform).
    Uses 'tefas-crawler' library.
    """
    
    def __init__(self):
        self.crawler = Crawler()
        
    def get_fund_asset_allocation(self, fund_code, date=None):
        """
        Fetches asset allocation for a specific fund.
        TEFAS data might be 1 day delayed.
        """
        if date is None:
            # Default to yesterday as today's data might not be ready
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
        try:
            # tefas-crawler fetch returns a DataFrame
            # Fetch all columns to avoid KeyError if names changed
            df = self.crawler.fetch(start=date, end=date)
            
            if df is None or df.empty:
                print(f"[!] No TEFAS data found for {date}")
                return None
                
            # Filter for specific fund
            fund_data = df[df['code'] == fund_code]
            
            if fund_data.empty:
                print(f"[!] Fund {fund_code} not found.")
                return None
                
            # Return dict
            row = fund_data.iloc[0]
            
            # Map columns (Handling potential name variations)
            return {
                'fund_code': row['code'],
                'date': row['date'],
                'stock_allocation_pct': float(row.get('stock', 0.0)), 
                'total_value': float(row.get('market_cap', 0.0)) # market_cap is usually total value
            }
            
        except Exception as e:
            print(f"[!] TEFAS Fetch Error: {e}")
            return None

    def get_institutional_stock_sentiment(self):
        """
        Analyzes major stock-heavy funds (Hisse Senedi Fonları) to gauge sentiment.
        Selected Funds: MAC (Marmara Capital), HKH (Hedef), TI2 (Is Portfoy)
        """
        target_funds = ['MAC', 'HKH', 'TI2', 'NNF']
        results = []
        
        for code in target_funds:
            data = self.get_fund_asset_allocation(code)
            if data:
                results.append(data)
                
        return results

if __name__ == "__main__":
    client = TefasClient()
    print("--- Fetching TEFAS Data ---")
    data = client.get_institutional_stock_sentiment()
    print(data)
