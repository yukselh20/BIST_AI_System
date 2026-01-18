import torch
from torch.utils.data import Dataset
import numpy as np
import pandas as pd

class BISTDataset(Dataset):
    """
    PyTorch Dataset for Time Series Sliding Window.
    """
    def __init__(self, dataframe, sequence_length=60):
        """
        Args:
            dataframe (pd.DataFrame): Dataframe containing features (OHLC + Indicators).
            sequence_length (int): History window size.
        """
        self.sequence_length = sequence_length
        self.data = dataframe
        
        # Convert DataFrame to Float Tensor
        # Note: In a real training pipeline, you MUST normalize this data using MinMaxScaler/StandardScaler 
        # BEFORE creating the dataset. We assume data passed here is ready-to-process or raw values.
        # For pure architecture testing, raw values are fine, but for convergence, scaling is mandatory.
        # We will convert to float32 for PyTorch compability.
        self.features_np = dataframe.values.astype(np.float32)
        
        # We also need the 'close' price column index to determine the target
        # Assuming 'close' is one of the columns. We need to find its index.
        try:
            self.close_idx = dataframe.columns.get_loc('close')
        except KeyError:
            # Fallback if specific column not found (e.g. testing with random tensor)
            self.close_idx = 3 # 4th column typically in OHLC
            
    def __len__(self):
        # We need (sequence_length) history + 1 future point.
        # So acceptable indices i are: 0 to len - sequence_length - 1
        # Example: len=100, seq=60.
        # last i = 100 - 60 - 1 = 39.
        # Window: 39..98 (len 60). Target: 99.
        # Valid.
        if len(self.data) < self.sequence_length + 1:
            return 0
        return len(self.data) - self.sequence_length

    def __getitem__(self, idx):
        # Window range: [idx, idx + sequence_length)
        x_window = self.features_np[idx : idx + self.sequence_length]
        
        # Target: Price movement at (idx + sequence_length) vs (idx + sequence_length - 1)
        # Note: x_window[-1] is the (idx + sequence_length - 1) data point.
        # We need the 'future' point which is features_np[idx + sequence_length]
        
        current_price = self.features_np[idx + self.sequence_length - 1][self.close_idx]
        future_price = self.features_np[idx + self.sequence_length][self.close_idx]
        
        # Binary Classification: 1 if Up, 0 if Down/Flat
        if future_price > current_price:
            y_label = 1.0
        else:
            y_label = 0.0
            
        return torch.tensor(x_window), torch.tensor([y_label])
