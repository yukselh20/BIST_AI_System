import pandas as pd
import numpy as np
try:
    from pypfopt import HRPOpt
except ImportError:
    from pypfopt.hierarchical_risk_parity import HRPOpt
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns

class PortfolioOptimizer:
    """
    Advanced Risk Management & Portfolio Optimization.
    Uses PyPortfolioOpt to calculate optimal weights.
    """
    def __init__(self):
        pass

    def calculate_hrp_weights(self, prices_df: pd.DataFrame):
        """
        Calculates weights using Hierarchical Risk Parity (HRP).
        HRP is robust against noise and works well with correlated assets (like BIST).
        
        prices_df: DataFrame where columns are Stock Symbols and index is Datetime.
        """
        try:
            # 1. Calculate Returns
            returns = prices_df.pct_change().dropna()
            
            # 2. HRP Optimization
            optimizer = HRPOpt(returns)
            weights = optimizer.optimize()
            
            # Clean weights (round small vals to 0)
            clean_weights = optimizer.clean_weights()
            return clean_weights
        except Exception as e:
            print(f"[!] HRP Optimization Error: {e}")
            # Fallback: Equal Weights
            n = len(prices_df.columns)
            return {col: 1.0/n for col in prices_df.columns}

    def calculate_var(self, portfolio_value, weights, prices_df, confidence=0.95):
        """
        Calculates Value at Risk (VaR) using the Variance-Covariance method.
        Calculates "Per Period" VaR relative to the input data frequency.
        """
        try:
            returns = prices_df.pct_change().dropna()
            
            # Use raw returns to avoid annualization assumptions
            mean_returns = returns.mean()
            cov_matrix = returns.cov()
            
            # Dict to Array (ensure order matches keys)
            w_list = [weights.get(col, 0) for col in prices_df.columns]
            w = np.array(w_list)
            
            # Portfolio Mean & Std (Per Period)
            port_mean = np.sum(mean_returns * w)
            port_std = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
            
            # Z-score for confidence
            from scipy.stats import norm
            z_score = norm.ppf(confidence)
            
            # VaR = -(Mean - Z * Std)
            # If returns are daily, this is 1-Day VaR.
            var_pct = -(port_mean - z_score * port_std)
            
            # If the calculated VaR is negative (meaning we expect profit), clamp to 0 or treat as risk-free
            if var_pct < 0:
                var_pct = 0.0
                
            var_amount = portfolio_value * var_pct
            
            return var_amount, var_pct
        except Exception as e:
            print(f"[!] VaR Calculation Error: {e}")
            return 0.0, 0.0

if __name__ == "__main__":
    # Test
    # Create fake data
    dates = pd.date_range(start="2023-01-01", periods=100)
    data = np.random.normal(10, 0.1, size=(100, 5)) 
    # Make them correlated and trending to simulate stocks
    data[:, 0] += np.linspace(0, 2, 100) # Stock A Up
    data[:, 1] += np.linspace(0, -1, 100) # Stock B Down
    data[:, 2] = data[:, 0] * 0.8 + np.random.normal(0, 0.05, 100) # Stock C correlated to A
    
    df = pd.DataFrame(data, index=dates, columns=['THYAO', 'GARAN', 'AKBNK', 'SASA', 'KCHOL'])
    
    opt = PortfolioOptimizer()
    w = opt.calculate_hrp_weights(df)
    print("HRP Weights:", w)
