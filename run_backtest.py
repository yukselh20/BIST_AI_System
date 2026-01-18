import sys
import argparse
from simulation.engine import run_simulation
from simulation.strategies.base import BaseStrategy
from backtesting.lib import crossover

# Example Simple Strategy for Testing
class RsiStrategy(BaseStrategy):
    upper_bound = 70
    lower_bound = 30
    
    def init(self):
        super().init()
        # Ensure we use the RSI calculated in feature_engine if available, 
        # or calculate it here if not. 
        # Our feature_engine adds 'RSI_14'. Backtesting.py accesses columns as self.data.ColumnName
        # So we can use self.data.RSI_14 if it exists.
        
        # Let's double check if RSI_14 is in the data passed to engine.
        # If not, we calculate it using a helper wrapper or pandas_ta manually (but self.I is preferred).
        
        # For this example, we assume feature_engine provided 'RSI_14'. 
        # But Backtesting `self.data` requires access via attribute, and `RSI_14` is a valid attribute.
        pass

    def next(self):
        # self.data.RSI_14 is a numpy array of the whole series, we need the last values.
        # Actually in Backtesting.py:
        # self.data.Close is an array.
        # But inside next(), we usually use self.data.Close[-1] etc.
        # However, for Indicator (self.I), it is handled differently.
        
        # Since 'RSI_14' comes from external DF, it is treated as an extra column.
        # accessing it: self.data.RSI_14[-1]
        
        rsi_val = self.data.RSI_14[-1]
        
        if rsi_val < self.lower_bound:
            if not self.position:
                self.buy()
                
        elif rsi_val > self.upper_bound:
            if self.position:
                self.sell()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run BIST AI Strategies')
    parser.add_argument('--symbol', type=str, default='THYAO', help='Stock Symbol')
    parser.add_argument('--strategy', type=str, default='RSI', help='Strategy Name')
    args = parser.parse_args()
    
    stats = run_simulation(args.symbol, RsiStrategy)
    
    if stats is not None:
        print("\n--- PERFORMANCE SUMMARY ---")
        print(stats)
        print("---------------------------")
