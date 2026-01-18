import torch
import torch.nn as nn

class BISTLSTM(nn.Module):
    """
    LSTM Model for binary classification (Up/Down Prediction).
    """
    def __init__(self, input_size, hidden_size=128, num_layers=2, dropout=0.2):
        super(BISTLSTM, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM Layer
        # batch_first=True means input shape is (batch, seq_len, features)
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Dropout layer to prevent overfitting
        self.dropout = nn.Dropout(dropout)
        
        # Fully Connected Layer: Maps LSTM output to 1 value
        self.fc = nn.Linear(hidden_size, 1)
        
        # Sigmoid Activation: Outputs probability (0 to 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x shape: (batch_size, sequence_length, input_size)
        
        # Initialize hidden state and cell state with zeros
        # This is optional as PyTorch does it by default, but good for clarity
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        # LSTM Forward Pass
        # out shape: (batch_size, sequence_length, hidden_size)
        out, _ = self.lstm(x, (h0, c0))
        
        # We only need the output of the LAST time step
        # shape: (batch_size, hidden_size)
        out = out[:, -1, :]
        
        # Apply Dropout
        out = self.dropout(out)
        
        # Fully Connected
        out = self.fc(out)
        
        # Activation
        out = self.sigmoid(out)
        
        return out
