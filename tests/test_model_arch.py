import torch
import pandas as pd
import numpy as np
import sys
import os

# Add root to python path
sys.path.append(os.getcwd())

from models.lstm_price.definitions import BISTLSTM
from models.lstm_price.dataset import BISTDataset

def test_architecture():
    print("--- Testing Model Architecture ---")
    
    # 1. Mock Data Creation
    # Create valid columns for Dataset to find 'close'
    cols = ['open', 'high', 'low', 'close', 'volume'] + [f'feat_{i}' for i in range(10)]
    num_rows = 200
    num_features = len(cols)
    
    # Random data
    data_np = np.random.rand(num_rows, num_features).astype(np.float32)
    df_mock = pd.DataFrame(data_np, columns=cols)
    
    print(f"Mock Data Shape: {df_mock.shape}")
    
    # 2. Test Dataset
    seq_len = 60
    dataset = BISTDataset(df_mock, sequence_length=seq_len)
    
    print(f"Dataset Length: {len(dataset)}")
    
    if len(dataset) > 0:
        x_sample, y_sample = dataset[0]
        print(f"Sample X shape: {x_sample.shape}") # Should be (60, num_features)
        print(f"Sample y shape: {y_sample.shape}") # Should be (1,)
        print(f"Sample y value: {y_sample}")
    else:
        print("[!] Dataset calculation incorrect or insufficient rows.")
        return

    # 3. Test Model
    print("\nInitializing LSTM Model...")
    model = BISTLSTM(input_size=num_features, hidden_size=64, num_layers=2)
    
    # Create a batch of size 1 
    # Must unsqueeze to add batch dimension: (1, 60, num_features)
    input_tensor = x_sample.unsqueeze(0)
    
    print(f"Input Tensor Shape: {input_tensor.shape}")
    
    # Forward Pass
    try:
        output = model(input_tensor)
        print(f"Output Shape: {output.shape}") # Should be (1, 1)
        print(f"Output Probability: {output.item():.4f}")
        
        if 0.0 <= output.item() <= 1.0:
            print("[+] Test Passed: Model produced a valid probability.")
        else:
            print("[-] Test Failed: Output out of range [0, 1].")
            
    except Exception as e:
        print(f"[-] Forward Pass Failed: {e}")

if __name__ == "__main__":
    test_architecture()
