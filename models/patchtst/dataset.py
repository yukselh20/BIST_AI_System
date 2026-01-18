import torch
from torch.utils.data import Dataset
import pandas as pd
import numpy as np

class BISTDataset(Dataset):
    """
    PyTorch Dataset for BIST Data, prepared for PatchTST.
    
    Args:
        dataframe (pd.DataFrame): Data with columns ['open', 'high', 'low', 'close', 'volume']
        context_length (int): Lookback window size (e.g. 512).
        prediction_length (int): Forecast horizon (e.g. 64).
    """
    def __init__(self, dataframe, context_length=512, prediction_length=64):
        self.context_length = context_length
        self.prediction_length = prediction_length
        
        # Ensure data is sorted
        # We assume dataframe is already clean (no NaNs) and sorted
        self.data = dataframe[['open', 'high', 'low', 'close', 'volume']].values.astype(np.float32)
        
        # Simple Standardization (Z-Score)
        # In a real pipeline, we should save these mean/std to apply to new data!
        self.mean = np.mean(self.data, axis=0)
        self.std = np.std(self.data, axis=0) + 1e-5 # Avoid div by zero
        self.data = (self.data - self.mean) / self.std
        
    def __len__(self):
        # We need (context + prediction) rows for one sample
        if len(self.data) < (self.context_length + self.prediction_length):
            return 0
        return len(self.data) - self.context_length - self.prediction_length + 1

    def __getitem__(self, idx):
        # Window: [idx : idx + context]
        # Target: [idx + context : idx + context + prediction]
        
        past_values = self.data[idx : idx + self.context_length]
        future_values = self.data[idx + self.context_length : idx + self.context_length + self.prediction_length]
        
        # PatchTST expects dictionary
        return {
            "past_values": torch.tensor(past_values),
            "future_values": torch.tensor(future_values)
        }
