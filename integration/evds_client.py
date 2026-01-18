import requests
import json
from datetime import datetime, timedelta

class EvdsClient:
    """
    Client for TCMB EVDS (Elektronik Veri Dağıtım Sistemi).
    """
    BASE_URL = "https://evds2.tcmb.gov.tr/service/evds"
    
    # Series Codes
    SERIES_INFLATION = "TP.FG.J0" # TÜFE (Yıllık Değişim) - Consumer Price Index
    SERIES_POLICY_RATE = "TP.KTF10" # Haftalık Repo Faizi
    SERIES_USD_TRY = "TP.DK.USD.A.YTL" # Dolar Kuru (Alış)
    
    def __init__(self, api_key):
        self.api_key = api_key
        
    def _fetch_series(self, series_code, start_date, end_date):
        """
        Generic method to fetch data from EVDS.
        Dates should be in DD-MM-YYYY format.
        """
        headers = {
            "key": self.api_key
        }
        
        # frequency=1 (Monthly), 5 (Daily) - depends on series.
        # type=json
        url = f"{self.BASE_URL}/series={series_code}&startDate={start_date}&endDate={end_date}&type=json"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'items' in data:
                    return data['items']
                else:
                    print(f"[!] EVDS Empty Response for {series_code}: {data}")
                    return []
            else:
                print(f"[!] EVDS HTTP Error {response.status_code}")
                return []
        except Exception as e:
            print(f"[!] EVDS Request Error: {e}")
            return []

    def get_macro_indicators(self):
        """
        Fetches the latest available macro indicators.
        Returns a dict.
        """
        # Fetch data for the last 60 days to ensure we catch the latest monthly release
        end_date = datetime.now().strftime("%d-%m-%Y")
        start_date = (datetime.now() - timedelta(days=60)).strftime("%d-%m-%Y")
        
        results = {}
        
        # 1. Inflation (CPI)
        cpi_items = self._fetch_series(self.SERIES_INFLATION, start_date, end_date)
        if cpi_items:
            # Get the last non-null value
            for item in reversed(cpi_items):
                val = item.get(self.SERIES_INFLATION.replace('.', '_')) # EVDS returns keys like TP_FG_J0
                if val:
                    results['inflation_cpi'] = float(val)
                    results['inflation_date'] = item.get('Tarih')
                    break
                    
        # 2. Policy Rate
        rate_items = self._fetch_series(self.SERIES_POLICY_RATE, start_date, end_date)
        if rate_items:
             for item in reversed(rate_items):
                val = item.get(self.SERIES_POLICY_RATE.replace('.', '_'))
                if val:
                    results['policy_rate'] = float(val)
                    break
        
        # 3. USD/TRY (Daily)
        # Fetch just last 3 days
        short_start = (datetime.now() - timedelta(days=5)).strftime("%d-%m-%Y")
        usd_items = self._fetch_series(self.SERIES_USD_TRY, short_start, end_date)
        if usd_items:
             for item in reversed(usd_items):
                val = item.get(self.SERIES_USD_TRY.replace('.', '_'))
                if val:
                    results['usd_try'] = float(val)
                    break
                    
        return results

if __name__ == "__main__":
    # Test
    # KEY provided by user
    key = "qr7BBmch3C" 
    client = EvdsClient(key)
    print("Fetching EVDS Data...")
    data = client.get_macro_indicators()
    print(json.dumps(data, indent=2))
