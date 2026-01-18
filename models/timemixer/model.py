import torch
import torch.nn as nn
import torch.nn.functional as F

class TimeMixerBlock(nn.Module):
    """
    Core building block of TimeMixer.
    Mixes features across Time and Channels.
    """
    def __init__(self, seq_len, num_channels, dropout=0.1):
        super().__init__()
        # Time Mixing (Mixes steps within a channel)
        self.time_mix = nn.Linear(seq_len, seq_len)
        
        # Channel Mixing (Mixes channels at a time step)
        self.channel_mix = nn.Linear(num_channels, num_channels)
        
        self.dropout = nn.Dropout(dropout)
        self.norm = nn.LayerNorm(num_channels)
        self.activation = nn.GELU()

    def forward(self, x):
        # x: [Batch, Time, Channels]
        
        # 1. Time Mixing
        # Transpose to apply Linear on Time dim
        x_t = x.permute(0, 2, 1) # [B, C, T]
        x_t = self.activation(self.time_mix(x_t))
        x_t = x_t.permute(0, 2, 1) # [B, T, C]
        x = x + self.dropout(x_t) # Skip Connection
        
        # 2. Channel Mixing
        x_c = self.activation(self.channel_mix(x))
        x = x + self.dropout(x_c) # Skip Connection
        
        return self.norm(x)

class TimeMixer(nn.Module):
    """
    Multi-Scale TimeMixer.
    Processes data at specific scales (Original, 1/2 resolution) to separate noise from trend.
    """
    def __init__(self, num_variates, lookback_len, pred_len, d_model=64, n_layers=2):
        super().__init__()
        self.pred_len = pred_len
        
        # Scale 0: Original Resolution
        self.mixer_s0 = nn.Sequential(*[
            TimeMixerBlock(lookback_len, num_variates) for _ in range(n_layers)
        ])
        self.proj_s0 = nn.Linear(lookback_len, pred_len)
        
        # Scale 1: 1/2 Resolution (Downsampled)
        self.pool = nn.AvgPool1d(kernel_size=2, stride=2)
        len_s1 = lookback_len // 2
        self.mixer_s1 = nn.Sequential(*[
            TimeMixerBlock(len_s1, num_variates) for _ in range(n_layers)
        ])
        self.proj_s1 = nn.Linear(len_s1, pred_len)
        
        # Final Projection (combining mixed features to output)
        # We process each variate independently in the final layer or together
        # Simple approach: Sum the projections from scales
        self.final_linear = nn.Linear(num_variates, num_variates)

    def forward(self, x):
        # x: [Batch, Lookback, Variates]
        
        # --- Scale 0 Flow ---
        out_s0 = self.mixer_s0(x) # [B, L, V]
        # Project Time dimension L -> Pred_Len
        out_s0 = out_s0.permute(0, 2, 1) # [B, V, L]
        out_s0 = self.proj_s0(out_s0)    # [B, V, Pred]
        out_s0 = out_s0.permute(0, 2, 1) # [B, Pred, V]
        
        # --- Scale 1 Flow (Coarse Grain / Trend) ---
        # Permute for Pooling (needs [B, V, L])
        x_p = x.permute(0, 2, 1)
        x_s1 = self.pool(x_p) 
        x_s1 = x_s1.permute(0, 2, 1) # Back to [B, L/2, V]
        
        out_s1 = self.mixer_s1(x_s1)
        
        out_s1 = out_s1.permute(0, 2, 1) # [B, V, L/2]
        out_s1 = self.proj_s1(out_s1)    # [B, V, Pred]
        out_s1 = out_s1.permute(0, 2, 1) # [B, Pred, V]
        
        # --- Aggregation ---
        # Summing multi-scale outputs implies decomposing:
        # Final = Fine_Detail + Coarse_Trend
        output = out_s0 + out_s1
        
        return output
