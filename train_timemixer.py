import sys
import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torch.optim import Adam
import numpy as np

# Resolve project imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

from core.feature_engine import fetch_and_process_data
from models.timemixer.model import TimeMixer

# --- CONFIG ---
SYMBOL = "THYAO"
LOOKBACK = 96   
PREDICTION = 24 
BATCH_SIZE = 32
EPOCHS = 10
LR = 0.001

class TimeSeriesDataset(Dataset):
    def __init__(self, df, lookback, prediction):
        self.data = df[['open', 'high', 'low', 'close', 'volume']].values.astype(np.float32)
        self.lookback = lookback
        self.prediction = prediction
        
        # Simple Norm
        self.mean = np.mean(self.data, axis=0)
        self.std = np.std(self.data, axis=0) + 1e-5
        self.data = (self.data - self.mean) / self.std
        
    def __len__(self):
        return len(self.data) - self.lookback - self.prediction + 1
        
    def __getitem__(self, idx):
        x = self.data[idx : idx + self.lookback]
        y = self.data[idx + self.lookback : idx + self.lookback + self.prediction]
        return torch.tensor(x), torch.tensor(y)

def train():
    print(f"[*] Fetching Data for {SYMBOL}...")
    df = fetch_and_process_data(SYMBOL, limit=5000)
    
    dataset = TimeSeriesDataset(df, LOOKBACK, PREDICTION)
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Init Model
    # 5 Variates: Open, High, Low, Close, Volume
    model = TimeMixer(num_variates=5, lookback_len=LOOKBACK, pred_len=PREDICTION)
    model.to(device)
    
    optimizer = Adam(model.parameters(), lr=LR)
    criterion = nn.MSELoss()
    
    print(f"[*] Starting TimeMixer Training on {device}...")
    model.train()
    
    for epoch in range(EPOCHS):
        total_loss = 0
        for batch_x, batch_y in loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            
            optimizer.zero_grad()
            output = model(batch_x)
            
            loss = criterion(output, batch_y)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {total_loss/len(loader):.6f}")
        
    # Save
    save_path = os.path.join(project_root, "models", "checkpoints", "timemixer_thyao.pth")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    torch.save(model.state_dict(), save_path)
    print(f"[+] Model Saved: {save_path}")

if __name__ == "__main__":
    train()
