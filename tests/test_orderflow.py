import unittest
import sys
import os

# Resolve project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from core.orderflow import calculate_imbalance, calculate_weighted_imbalance

class TestOrderFlow(unittest.TestCase):
    
    def test_calculate_imbalance_buy_pressure(self):
        # Bids > Asks -> Positive
        # Bids: 1000 lots @ 100, Asks: 100 lots @ 101
        bids = [[100, 1000]]
        asks = [[101, 100]]
        
        # (1000 - 100) / (1000 + 100) = 900 / 1100 = 0.818
        result = calculate_imbalance(bids, asks)
        self.assertGreater(result, 0)
        self.assertAlmostEqual(result, 0.81818181, places=4)
        
    def test_calculate_imbalance_sell_pressure(self):
        # Asks > Bids -> Negative
        bids = [[100, 100]]
        asks = [[101, 1000]]
        
        result = calculate_imbalance(bids, asks)
        self.assertLess(result, 0)
        
    def test_weighted_imbalance(self):
        # Level 1 has more weight than Level 2
        # Bid L1: 100, Bid L2: 100
        # Ask L1: 100, Ask L2: 100
        # Logic: If L1 volume doubles, imbalance should jump more than if L5 doubles
        
        bids = [[100, 1000], [99, 10]] 
        asks = [[101, 100], [102, 10]]
        
        # Should be strong buy
        result = calculate_weighted_imbalance(bids, asks)
        self.assertGreater(result, 0.5)

if __name__ == '__main__':
    unittest.main()
