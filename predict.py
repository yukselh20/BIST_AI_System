import torch
import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.getcwd())

from core.feature_engine import fetch_and_process_data
from models.lstm_price.definitions import BISTLSTM

# Configuration
SYMBOL = "THYAO"
SEQUENCE_LENGTH = 60
MODEL_PATH = "models/checkpoints/lstm_model.pth"

def predict_next_move():
    print("--- AI Prediction Engine ---")
    
    # 1. Load Model
    if not os.path.exists(MODEL_PATH):
        print(f"[!] Model file not found at {MODEL_PATH}")
        print("Advice: Run 'train.py' first.")
        return

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    try:
        checkpoint = torch.load(MODEL_PATH, map_location=device)
        input_size = checkpoint.get('input_size', 15) # Default fallback if missing
        
        model = BISTLSTM(input_size=input_size).to(device)
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()
        print("[+] Model loaded successfully.")
    except Exception as e:
        print(f"[!] Model loading failed: {e}")
        return

    # 2. Fetch Latest Data
    print(f"Fetching latest data for {SYMBOL}...")
    # Increase limit to ensure we have enough data for 200-period EMA + Sequence Length
    df = fetch_and_process_data(SYMBOL, timeframe='1s', limit=2000)
    
    if len(df) < SEQUENCE_LENGTH:
        print(f"[!] Not enough recent data ({len(df)} rows). Need last {SEQUENCE_LENGTH} bars.")
        return

    # 3. Prepare Input
    # Take the LAST 60 rows
    last_window = df.tail(SEQUENCE_LENGTH)
    current_price = last_window['close'].iloc[-1]
    
    # Convert to Tensor
    # (1, 60, Features)
    input_np = last_window.values.astype(np.float32)
    input_tensor = torch.tensor(input_np).unsqueeze(0).to(device)

    # 4. Inference
    with torch.no_grad():
        probability = model(input_tensor).item()

    # 5. Output Decision
    print("-" * 30)
    print(f"Stock: {SYMBOL}")
    print(f"Current Price: {current_price:.2f}")
    print(f"AI Probability (Up): {probability:.2%}")
    
    threshold = 0.52
    if probability > threshold:
        decision = "BUY (AL)"
    elif probability < (1.0 - threshold):
        decision = "SELL (SAT)"
    else:
        decision = "HOLD (BEKLE)"
        
    print(f"AI Decision: {decision}")
    print("-" * 30)

if __name__ == "__main__":
    predict_next_move()
