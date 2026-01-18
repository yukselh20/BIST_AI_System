import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
import sys
import os
import pandas as pd
import numpy as np

# Resolve project root
sys.path.append(os.getcwd())

from core.feature_engine import fetch_and_process_data
from models.lstm_price.definitions import BISTLSTM
from models.lstm_price.dataset import BISTDataset

# Hyperparameters
SYMBOL = "THYAO"
SEQUENCE_LENGTH = 60
BATCH_SIZE = 16
EPOCHS = 10
LEARNING_RATE = 0.001
CHECKPOINT_DIR = "models/checkpoints"
MODEL_PATH = os.path.join(CHECKPOINT_DIR, "lstm_model.pth")

def train_model():
    print("--- Starting Training Pipeline ---")
    
    # 1. Fetch Data
    print(f"Fetching data for {SYMBOL}...")
    # Use '1min' for production (Yahoo Finance Data)
    # The user is running free_data_feeder.py which provides 1-minute interval data.
    # Training on 1s would cause a domain mismatch.
    df = fetch_and_process_data(SYMBOL, timeframe='1min', limit=5000)
    
    if len(df) < 200:
        print(f"[!] Insufficient data ({len(df)} rows). Need at least 200.")
        print("Advice: Run 'mock_data_feeder.py' for a few minutes.")
        return

    print(f"[+] Data loaded: {len(df)} rows. Features: {df.shape[1]}")

    # 2. Prepare Dataset
    dataset = BISTDataset(df, sequence_length=SEQUENCE_LENGTH)
    
    # Split Train/Val (80/20)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    # val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE) # Optional for validation checking

    print(f"[+] Dataset split: {train_size} Train, {val_size} Validation samples.")

    # 3. Initialize Model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Training on: {device}")
    
    input_size = df.shape[1] # Number of columns
    model = BISTLSTM(input_size=input_size).to(device)
    
    criterion = nn.BCELoss() # Binary Cross Entropy for Probability (0-1)
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # 4. Training Loop
    model.train()
    
    for epoch in range(EPOCHS):
        total_loss = 0
        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            
            # Forward
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            
            # Backward
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        avg_loss = total_loss / len(train_loader)
        print(f"Epoch [{epoch+1}/{EPOCHS}], Loss: {avg_loss:.4f}")

    # 5. Save Model
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    torch.save({
        'model_state_dict': model.state_dict(),
        'input_size': input_size, # Save input dimension for safe loading
        'symbol': SYMBOL
    }, MODEL_PATH)
    
    print(f"[+] Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_model()
