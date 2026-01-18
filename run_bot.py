import time
import sys
import os
import torch
import numpy as np
from datetime import datetime

sys.path.append(os.getcwd())

from core.feature_engine import fetch_and_process_data
from models.lstm_price.definitions import BISTLSTM
from core.trader import PaperTrader
from core.news_agent import NewsAgent

# Config
# Portfolio List (Stripped .IS)
# Portfolio List (Stripped .IS)
from core.config_symbols import ALL_SYMBOLS as SYMBOLS

MODEL_PATH = "models/checkpoints/lstm_model.pth"
SEQUENCE_LENGTH = 60
CONFIDENCE_BUY = 0.60
CONFIDENCE_SELL = 0.40

# Optimization Settings
SLEEP_BETWEEN_CYCLES = 60    # 1 Minute (Matches bar close)
NEWS_UPDATE_INTERVAL = 15    # Update news every 15 cycles (15 mins)

def load_ai_model():
    if not os.path.exists(MODEL_PATH):
        print(f"[!] Model not found at {MODEL_PATH}")
        return None, None
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    try:
        checkpoint = torch.load(MODEL_PATH, map_location=device)
        input_size = checkpoint.get('input_size', 15)
        model = BISTLSTM(input_size=input_size).to(device)
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()
        return model, device
    except Exception as e:
        print(f"[!] AI Load Error: {e}")
        return None, None

def run_bot():
    print("--- BIST AI HİBRİT BOT (OPTIMIZED) BAŞLATILIYOR ---")
    print(f"[*] Takip Edilen Hisseler: {', '.join(SYMBOLS)}")
    print(f"[*] Döngü Hızı: {SLEEP_BETWEEN_CYCLES}sn | Haber Güncelleme: Her {NEWS_UPDATE_INTERVAL} döngüde bir")
    
    # 1. Initialize Components
    trader = PaperTrader()
    model, device = load_ai_model()
    
    # Initialize News Agent
    news_agent = NewsAgent()
    
    if not model:
        return

    print(f"[*] Trader Initialized. Balance: {trader.balance:.2f} TL")

    # State Variables
    cycle_count = 0
    news_scores_cache = {symbol: 0.0 for symbol in SYMBOLS} # Default neutral
    
    while True:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n--- Tarama Döngüsü: {timestamp} (Tur: {cycle_count+1}) ---")
        
        # Check if we should update news this cycle
        should_update_news = (cycle_count % NEWS_UPDATE_INTERVAL == 0)
        
        if should_update_news:
             print(">> [INFO] Haberler ve Duygu Analizleri Güncelleniyor...")

        try:
            for symbol in SYMBOLS:
                # --- MARKET DATA & TECHNICAL ---
                df = fetch_and_process_data(symbol, timeframe='1s', limit=2000)
                
                if len(df) < SEQUENCE_LENGTH:
                    continue
                    
                last_price = df['close'].iloc[-1]
                
                # LSTM Inference
                last_window = df.tail(SEQUENCE_LENGTH)
                input_np = last_window.values.astype(np.float32)
                input_tensor = torch.tensor(input_np).unsqueeze(0).to(device)
                
                with torch.no_grad():
                    lstm_prob = model(input_tensor).item()
                
                # --- FUNDAMENTAL (NEWS) ---
                if should_update_news:
                    # Fetch fresh score
                    # Note: We silence the internal print of news_agent here or accept it
                    # To keep logs clean, we just call it.
                    score = news_agent.get_sentiment_score(symbol)
                    news_scores_cache[symbol] = score
                
                # Use cached score
                news_score = news_scores_cache.get(symbol, 0.0)
                
                # --- HYBRID DECISION ---
                # Log format: [SYMBOL] Tech: 75% | News: +0.4 -> DECISION
                log_prefix = f"[{symbol}] Fiyat: {last_price:>7.2f} | Teknik: {lstm_prob:>6.2%} | Haber: {news_score:>5.2f}"
                
                decision = "BEKLE"
                action_color = ""
                
                # BUY SIGNAL
                if (lstm_prob > CONFIDENCE_BUY) and (news_score > -0.2):
                    decision = "AL (BUY)"
                    action_color = "\033[92m" # Green
                    
                    if trader.balance > last_price:
                        # Max 20% invest
                        invest_amount = trader.balance * 0.20
                        if invest_amount < last_price: invest_amount = trader.balance 
                        qty = int(invest_amount / last_price)
                        
                        if qty > 0:
                            print(f"{log_prefix} -> {action_color}ALIM SİNYALİ{'\033[0m'}")
                            trader.buy(symbol, last_price, qty)
                        else:
                            print(f"{log_prefix} -> ALIM SİNYALİ (Bakiye Yetersiz)")
                    else:
                        print(f"{log_prefix} -> ALIM SİNYALİ (Bakiye Yok)")
                        
                # SELL SIGNAL
                elif (lstm_prob < CONFIDENCE_SELL) or (news_score < -0.5):
                    decision = "SAT (SELL)"
                    action_color = "\033[91m" # Red
                    
                    if symbol in trader.positions:
                        qty = trader.positions[symbol]
                        print(f"{log_prefix} -> {action_color}SATIŞ SİNYALİ{'\033[0m'}")
                        trader.sell(symbol, last_price, qty)
                    else:
                        # Only log sell signal if we actually have position or if debug
                        # To reduce spam for non-held stocks:
                        # print(f"{log_prefix} -> SATIŞ SİNYALİ (Pozisyon Yok)")
                        pass
                        
                # HOLD
                else:
                    # Reduce spam: Don't print "HOLD" for every single stock every minute if requested
                    # But user wanted "Skor ve Karar satırını bas".
                    print(f"{log_prefix} -> BEKLE")
            
            # End of Cycle Summary
            print("-" * 50)
            print(f"Bakiye: {trader.balance:.2f} TL | Portföy: {trader.positions}")
            print("-" * 50)
            
            cycle_count += 1
            time.sleep(SLEEP_BETWEEN_CYCLES)
            
        except KeyboardInterrupt:
            print("\n[*] Bot durduruldu.")
            break
        except Exception as e:
            print(f"\n[!] Hata oluştu: {e}")
            time.sleep(SLEEP_BETWEEN_CYCLES)

if __name__ == "__main__":
    run_bot()
