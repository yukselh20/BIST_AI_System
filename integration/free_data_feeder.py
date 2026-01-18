import socket
import time
import json
import datetime
import sys

# Kütüphane kontrolü ve yükleme talimatı
try:
    import yfinance as yf
except ImportError:
    print("[!] 'yfinance' kütüphanesi bulunamadı.")
    print("Lütfen yüklemek için şu komutu çalıştırın: pip install yfinance")
    sys.exit(1)

# Resolve Import Path
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

from core.config_symbols import ALL_SYMBOLS

# Konfigürasyon
HOST = '127.0.0.1'
PORT = 5555

# Yahoo Finance requires .IS suffix for BIST stocks
WATCHLIST = [f"{s}.IS" for s in ALL_SYMBOLS]

INTERVAL_SECONDS = 60  # Tüm liste döndükten sonra ne kadar beklenecek
SYMBOL_DELAY = 2       # Her hisse sorgusu arası bekleme (Engel yememek için)

def connect_to_server():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
            print(f"[+] Sunucuya bağlanıldı: {HOST}:{PORT}")
            return s
        except ConnectionRefusedError:
            print("[!] Sunucu bulunamadı. Tekrar deneniyor... (socket_server.py çalışıyor mu?)")
            time.sleep(5)

def fetch_and_send():
    s = connect_to_server()
    
    print(f"--- Yahoo Finance Veri Akışı Başlatılıyor ({len(WATCHLIST)} Hisse) ---")
    
    first_run = True
    
    while True:
        try:
            for yahoo_symbol in WATCHLIST:
                # Sistem sembolü: ".IS" uzantısını kaldır
                sys_symbol = yahoo_symbol.replace('.IS', '')
                
                # Yahoo Finance'den veri çek
                ticker = yf.Ticker(yahoo_symbol)
                
                # İlk turda geçmiş verileri de doldur (Backfill)
                # Böylece sistem boş veritabanı ile başlamaz, direk analiz yapabilir.
                if first_run:
                    print(f"[{sys_symbol}] Geriye dönük 2 günlük veri yükleniyor...")
                    df = ticker.history(period='2d', interval='1m')
                else:
                    # Normal mod: Sadece son veriyi al
                    df = ticker.history(period='1d', interval='1m')

                if not df.empty:
                    # İlk turda tüm geçmişi gönder
                    if first_run:
                        records_sent = 0
                        for index, row in df.iterrows():
                            # Timestamp timezone convert
                            ts_str = index.strftime("%Y-%m-%d %H:%M:%S")
                            
                            data = {
                                "symbol": sys_symbol,
                                "price": float(row['Close']),
                                "volume": int(row['Volume']),
                                "timestamp": ts_str,
                                "source": "YahooFinance"
                            }
                            s.sendall((json.dumps(data) + "\n").encode('utf-8'))
                            records_sent += 1
                        print(f"[{sys_symbol}] {records_sent} adet geçmiş veri yüklendi. ✅")
                        # Sunucuyu boğmamak için kısa bekleme
                        time.sleep(0.1) 
                    
                    else:
                        # Canlı Mod: Sadece son veriyi gönder
                        last_quote = df.iloc[-1]
                        # Timestamp timezone'suz gelebilir, o anı alalım
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        data = {
                            "symbol": sys_symbol,
                            "price": float(last_quote['Close']),
                            "volume": int(last_quote['Volume']),
                            "timestamp": timestamp,
                            "source": "YahooFinance"
                        }
                        
                        json_str = json.dumps(data)
                        s.sendall((json_str + "\n").encode('utf-8'))
                        print(f"[{timestamp}] {sys_symbol} Canlı Veri Gönderildi -> {float(last_quote['Close']):.2f} TL")
                    
                else:
                    print(f"[!] {sys_symbol} verisi alınamadı.")

                if not first_run:
                    time.sleep(SYMBOL_DELAY)
            
            # İlk tur bitti
            if first_run:
                print("\n✅ TÜM HİSSELER İÇİN GEÇMİŞ VERİ YÜKLENDİ. SİSTEM HAZIR.\n")
                first_run = False

            print(f"--- Liste tamamlandı. {INTERVAL_SECONDS} saniye bekleniyor... ---")
            time.sleep(INTERVAL_SECONDS)

            print(f"--- Liste tamamlandı. {INTERVAL_SECONDS} saniye bekleniyor... ---")
            time.sleep(INTERVAL_SECONDS)
            
        except (BrokenPipeError, ConnectionResetError):
            print("[!] Bağlantı koptu. Yeniden bağlanılıyor...")
            s.close()
            s = connect_to_server()
        except Exception as e:
            print(f"[!] Hata: {e}")
            time.sleep(5)

if __name__ == "__main__":
    fetch_and_send()
