import torch
import torch.nn as nn

class iTransformer(nn.Module):
    """
    iTransformer: Inverted Transformer.
    Instead of embedding time steps (t1, t2...), we embed the entire series of a variate (Price, Volume...).
    This allows the Attention mechanism to learn correlations BETWEEN variates.
    """
    def __init__(self, num_variates, lookback_len, pred_len, d_model=512, n_heads=8, n_layers=2, dropout=0.1):
        super(iTransformer, self).__init__()
        self.lookback_len = lookback_len
        self.pred_len = pred_len
        self.num_variates = num_variates # Number of channels (e.g. 5 for OHLCV)
        
        # 1. Embedding: Maps the time-series of length 'lookback_len' to 'd_model'
        # Essentially, each variate becomes a token of size d_model.
        self.enc_embedding = nn.Linear(lookback_len, d_model)
        
        # 2. Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=n_heads, dropout=dropout, batch_first=True)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        
        # 3. Projection: Maps 'd_model' back to 'pred_len'
        self.projection = nn.Linear(d_model, pred_len)
        
    def forward(self, x):
        # x shape: [Batch, Lookback, Variates] -> Standard Time Series format
        
        # Step 1: Invert Dimensions -> [Batch, Variates, Lookback]
        # Now each "row" is one variate's entire history.
        x = x.permute(0, 2, 1)
        
        # Step 2: Embed -> [Batch, Variates, d_model]
        # Each variate is now a vector of size d_model.
        enc_out = self.enc_embedding(x)
        
        # Step 3: Transformer Encoder -> [Batch, Variates, d_model]
        # Attention is calculated between Variates (e.g. Price attends to Volume).
        # This is where the magic happens: "Multivariate Correlation".
        enc_out = self.encoder(enc_out)
        
        # Step 4: Project/Predict -> [Batch, Variates, Pred_Len]
        dec_out = self.projection(enc_out)
        
        # Step 5: Revert Dimensions -> [Batch, Pred_Len, Variates]
        dec_out = dec_out.permute(0, 2, 1)
        
        return dec_out
