import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Proje kök dizinini ekle
sys.path.append(os.getcwd())

from core.database import SessionLocal, TickData

# Yahoo Finance Sembolleri
SYMBOLS = [
    'THYAO.IS', 'ASELS.IS', 'EREGL.IS', 'KAREL.IS', 'KCHOL.IS', 
    'ENKAI.IS', 'FROTO.IS', 'KRDMD.IS', 'CIMSA.IS', 'SAHOL.IS', 'OTKAR.IS'
]

def populate_real_data():
    print("--- GERÇEK GEÇMİŞ VERİ YÜKLEME BAŞLATILIYOR (YAHOO FINANCE) ---")
    
    session = SessionLocal()
    total_added = 0
    
    for yahoo_symbol in SYMBOLS:
        # Sistemdeki sembol adı (.IS olmadan)
        sys_symbol = yahoo_symbol.replace('.IS', '')
        print(f"\n[*] {sys_symbol} verileri indiriliyor...")
        
        try:
            # 1. Yahoo Finance'den son 7 günün 1 dakikalık verisini çek
            # Not: Yahoo Finance API kısıtlamaları nedeniyle 1m verisi en fazla 7 gün geriye gider.
            df = yf.download(tickers=yahoo_symbol, period='7d', interval='1m', progress=False)
            
            if df.empty:
                print(f"[!] {sys_symbol} için veri bulunamadı.")
                continue
                
            # 2. Verileri Dönüştür ve Kaydet
            ticks_to_save = []
            
            # DataFrame index'i datetime'dır
            for index, row in df.iterrows():
                # Timestamp timezone bilgisini temizle (SQLite karmaşasını önlemek için)
                ts = index.replace(tzinfo=None) if index.tzinfo else index
                
                # Fiyat ve Hacim
                # yfinance bazen MultiIndex döndürür, tek sembol indirdiğimiz için .iloc gerekebilir 
                # ama download tek sembolse düz kolon gelir. Garanti olsun diye float çeviriyoruz.
                try:
                    price = float(row['Close'])
                    volume = int(row['Volume'])
                except:
                    # Bazen Series olarak gelebilir
                    price = float(row['Close'].iloc[0]) if hasattr(row['Close'], 'iloc') else float(row['Close'])
                    volume = int(row['Volume'].iloc[0]) if hasattr(row['Volume'], 'iloc') else int(row['Volume'])

                # DB Objesi
                tick = TickData(
                    symbol=sys_symbol,
                    price=price,
                    volume=volume,
                    timestamp=ts,
                    received_at=datetime.utcnow()
                )
                ticks_to_save.append(tick)
            
            # 3. Toplu Kayıt (Bulk Save)
            if ticks_to_save:
                session.bulk_save_objects(ticks_to_save)
                session.commit()
                count = len(ticks_to_save)
                print(f" -> {count} adet veri eklendi.")
                total_added += count
            else:
                print(" -> Eklenecek veri yok.")
                
        except Exception as e:
            print(f"[!] Hata ({sys_symbol}): {e}")
            session.rollback()

    session.close()
    print("-" * 50)
    print(f"TAMAMLANDI. Toplam {total_added} satır veri veritabanına işlendi.")
    print("-" * 50)

if __name__ == "__main__":
    populate_real_data()
