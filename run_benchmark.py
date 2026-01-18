import sys
import os
import torch
import torch.nn as nn
import numpy as np
import time
from tabulate import tabulate

# Resolve project imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from core.feature_engine import fetch_and_process_data
from models.itransformer.model import iTransformer
from models.timemixer.model import TimeMixer
# Assuming LSTM definition is in models/lstm_price/definitions.py or similar, 
# but for benchmark we will mock the LSTM load to keep it simple if file structure is complex,
# or better: Define a simple LSTM here matching the project one for fair comparison if exact import is tricky.
# Checking loaded files: models.lstm_price.definitions.BISTLSTM was viewed.
from models.lstm_price.definitions import BISTLSTM

# PatchTST might need HF import
from transformers import PatchTSTConfig, PatchTSTForPrediction

SYMBOL = "THYAO"
LOOKBACK = 96
PREDICTION = 24
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def get_test_data():
    df = fetch_and_process_data(SYMBOL, limit=2000)
    data = df[['open', 'high', 'low', 'close', 'volume']].values.astype(np.float32)
    
    # Normalize
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0) + 1e-5
    data = (data - mean) / std
    
    # Create windows
    x, y = [], []
    for i in range(len(data) - LOOKBACK - PREDICTION):
        x.append(data[i : i+LOOKBACK])
        y.append(data[i+LOOKBACK : i+LOOKBACK+PREDICTION])
        
    return torch.tensor(np.array(x)).to(DEVICE), torch.tensor(np.array(y)).to(DEVICE)

def benchmark_models():
    print(f"[*] Benchmarking Models on {SYMBOL} (Device: {DEVICE})...")
    X_test, y_test = get_test_data()
    print(f"[*] Test Set Size: {len(X_test)} samples")
    
    results = []
    criterion = nn.MSELoss()
    
    # --- 1. LSTM (Baseline) ---
    try:
        # LSTM usually takes short seq, but we'll adapt or just feed last 60
        lstm = BISTLSTM(input_size=5, hidden_size=128, num_layers=2, output_size=1, dropout_prob=0).to(DEVICE)
        # Load weights if available, else random init (Benchmark architecture potential)
        start = time.time()
        with torch.no_grad():
            # LSTM expects [Batch, Seq, Feat]
            # Our defined LSTM predicts next STEP's Close price usually, not full 24 steps
            # benchmarking 'Architecture Speed' and 'Convergence Potential' mostly here
            out = lstm(X_test)
        infer_time = (time.time() - start) * 1000 / len(X_test)
        results.append(["LSTM (Baseline)", "N/A (Arch Only)", f"{infer_time:.2f} ms"])
    except Exception as e:
        results.append(["LSTM", f"Error: {e}", "-"])

    # --- 2. PatchTST ---
    try:
        config = PatchTSTConfig(num_input_channels=5, context_length=LOOKBACK, patch_length=16, prediction_length=PREDICTION)
        model = PatchTSTForPrediction(config).to(DEVICE)
        # Load Checkpoint if exists
        path = "models/checkpoints/patchtst_thyao.pth"
        if os.path.exists(path): model.load_state_dict(torch.load(path, map_location=DEVICE))
        
        start = time.time()
        with torch.no_grad():
             out = model(past_values=X_test).prediction_outputs
        infer_time = (time.time() - start) * 1000 / len(X_test)
        
        loss = criterion(out, y_test).item()
        results.append(["PatchTST", f"{loss:.4f}", f"{infer_time:.2f} ms"])
    except Exception as e:
        results.append(["PatchTST", f"Error: {e}", "-"])

    # --- 3. iTransformer ---
    try:
        model = iTransformer(num_variates=5, lookback_len=LOOKBACK, pred_len=PREDICTION).to(DEVICE)
        path = "models/checkpoints/itransformer_thyao.pth"
        if os.path.exists(path): model.load_state_dict(torch.load(path, map_location=DEVICE))
        
        start = time.time()
        with torch.no_grad():
            out = model(X_test)
        infer_time = (time.time() - start) * 1000 / len(X_test)
        
        loss = criterion(out, y_test).item()
        results.append(["iTransformer", f"{loss:.4f}", f"{infer_time:.2f} ms"])
    except Exception as e:
        results.append(["iTransformer", f"Error: {e}", "-"])

    # --- 4. TimeMixer ---
    try:
        model = TimeMixer(num_variates=5, lookback_len=LOOKBACK, pred_len=PREDICTION).to(DEVICE)
        path = "models/checkpoints/timemixer_thyao.pth"
        if os.path.exists(path): model.load_state_dict(torch.load(path, map_location=DEVICE))
        
        start = time.time()
        with torch.no_grad():
            out = model(X_test)
        infer_time = (time.time() - start) * 1000 / len(X_test)
        
        loss = criterion(out, y_test).item()
        results.append(["TimeMixer", f"{loss:.4f}", f"{infer_time:.2f} ms"])
    except Exception as e:
        results.append(["TimeMixer", f"Error: {e}", "-"])

    print("\n" + tabulate(results, headers=["Model", "Test MSE Loss", "Inference Time (ms/sample)"], tablefmt="grid"))
    
    # Recommendation
    losses = [float(r[1]) for r in results if r[1].replace('.','',1).isdigit()]
    if losses:
        best_idx = np.argmin(losses)
        best_model = results[len(results) - len(losses) + best_idx][0]
        print(f"\n🏆 WINNER: {best_model} seems to be the most accurate for this dataset.")

if __name__ == "__main__":
    benchmark_models()
