import pandas as pd
import numpy as np
import sys
import os

# Resolve imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.portfolio_optimizer import PortfolioOptimizer

def test_optimization():
    print("Optimization Test Initiated...")
    
    # 1. Generate Synthetic Data (Simulating BIST Stocks)
    # THYAO & PGSUS (Aviation - Correlated)
    # KCHOL & SAHOL (Holding - Correlated)
    # ASELS (Defense - Independent)
    
    np.random.seed(42)
    dates = pd.date_range(start="2025-01-01", periods=200)
    
    # Random Walks
    thyao = np.cumsum(np.random.normal(0, 0.02, 200)) + 100
    pgsus = thyao * 1.1 + np.random.normal(0, 2, 200) # Correlated
    
    kchol = np.cumsum(np.random.normal(0, 0.015, 200)) + 50
    sahol = kchol * 0.9 + np.random.normal(0, 1, 200) # Correlated
    
    asels = np.cumsum(np.random.normal(0, 0.025, 200)) + 40 # Volatile & Independent
    
    df = pd.DataFrame({
        'THYAO': thyao,
        'PGSUS': pgsus,
        'KCHOL': kchol,
        'SAHOL': sahol,
        'ASELS': asels
    }, index=dates)
    
    print("[*] Synthetic Data Generated.")
    print(df.tail())
    
    # 2. Run HRP Optimization
    opt = PortfolioOptimizer()
    weights = opt.calculate_hrp_weights(df)
    
    print("\n[+] Recommended Portfolio Weights (HRP):")
    print("="*30)
    for sym, w in weights.items():
        print(f"{sym}: {w:.4f} ({w*100:.1f}%)")
    print("="*30)
    
    # Explanation: HRP should penalize correlated clusters. 
    # Since THYAO/PGSUS are correlated, their combined weight shouldn't dominate.
    
    # 3. VaR Calculation
    portfolio_val = 1_000_000 # 1 Million TL
    var_amount, var_pct = opt.calculate_var(portfolio_val, weights, df)
    
    print(f"\n[!] Value at Risk (VaR 95% - 1 Day):")
    print(f"Loss Amount: {var_amount:,.2f} TL")
    print(f"Loss %: {var_pct*100:.2f}%")

if __name__ == "__main__":
    test_optimization()
