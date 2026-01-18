import sys
import os
import torch
from transformers import PatchTSTConfig, PatchTSTForPrediction
from torch.utils.data import DataLoader
from torch.optim import AdamW

# Resolve project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

from core.feature_engine import fetch_and_process_data
from models.patchtst.dataset import BISTDataset

# CONFIG
SYMBOL = "THYAO"
CONTEXT_LENGTH = 512
PREDICTION_LENGTH = 64
PATCH_LENGTH = 16
BATCH_SIZE = 16
EPOCHS = 5

def train_model():
    print(f"[*] Fetching Data for {SYMBOL}...")
    # Fetch ample history
    df = fetch_and_process_data(SYMBOL, timeframe='1min', limit=10000)
    
    if len(df) < (CONTEXT_LENGTH + PREDICTION_LENGTH + 100):
        print("[!] Not enough data for training.")
        return

    print(f"[*] Data Shape: {df.shape}")
    
    # Init Dataset
    dataset = BISTDataset(df, context_length=CONTEXT_LENGTH, prediction_length=PREDICTION_LENGTH)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    # Configure PatchTST
    # num_input_channels = 5 (OHLCV)
    config = PatchTSTConfig(
        num_input_channels=5,
        context_length=CONTEXT_LENGTH,
        patch_length=PATCH_LENGTH,
        prediction_length=PREDICTION_LENGTH,
        num_hidden_layers=2, # Keep it small for now
        d_model=128,
        n_heads=4,
        scaling="std", # Model handles internal scaling too
        loss="mse",
        task_mode="forecast" # Usually 'prediction' or 'forecast' depending on version
    )
    
    # Initialize Model from valid HF config
    # Note: 'PatchTSTForPrediction' might need specific instantiation
    model = PatchTSTForPrediction(config)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    optimizer = AdamW(model.parameters(), lr=1e-4)
    
    print(f"[*] Starting Training on {device}...")
    
    model.train()
    for epoch in range(EPOCHS):
        total_loss = 0
        for batch in dataloader:
            optimizer.zero_grad()
            
            # Move to device
            past_values = batch["past_values"].to(device)
            future_values = batch["future_values"].to(device)
            
            # Forward
            # HF Output: outputs.loss, outputs.prediction_logits etc.
            outputs = model(past_values=past_values, future_values=future_values)
            
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {avg_loss:.6f}")
        
    # Save Model
    save_path = os.path.join(project_root, "models", "checkpoints", "patchtst_thyao.pth")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    torch.save(model.state_dict(), save_path)
    print(f"[+] Model Saved to {save_path}")

if __name__ == "__main__":
    train_model()
