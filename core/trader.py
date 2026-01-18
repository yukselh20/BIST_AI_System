import pandas as pd
import os
from datetime import datetime

class PaperTrader:
    def __init__(self, initial_capital=100000.0, commission_rate=0.002, log_file='data/trade_log.csv'):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.log_file = log_file
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        self.positions = {} # {symbol: quantity}
        
        # Load or Initialize state
        if os.path.exists(log_file):
            self.trade_log = pd.read_csv(log_file)
            self._reconstruct_portfolio()
        else:
            self.trade_log = pd.DataFrame(columns=['timestamp', 'action', 'symbol', 'price', 'quantity', 'commission', 'balance_after'])
            self.balance = initial_capital

    def _reconstruct_portfolio(self):
        """Reconstructs balance and positions from trade log."""
        self.balance = self.initial_capital
        self.positions = {}
        
        for _, row in self.trade_log.iterrows():
            action = row['action']
            symbol = row['symbol']
            qty = row['quantity']
            # Last row balance is sufficient if log is ordered, but let's trust the last row for balance
            
        if not self.trade_log.empty:
            self.balance = self.trade_log.iloc[-1]['balance_after']
            
            # Recalculate positions
            # This is a bit inefficient for huge logs but safe for consistency
            self.positions = {}
            for _, row in self.trade_log.iterrows():
                sym = row['symbol']
                qty = row['quantity']
                if row['action'] == 'BUY':
                    self.positions[sym] = self.positions.get(sym, 0) + qty
                elif row['action'] == 'SELL':
                    self.positions[sym] = self.positions.get(sym, 0) - qty
                    if self.positions[sym] <= 0:
                        del self.positions[sym]

    def buy(self, symbol, price, quantity):
        cost = price * quantity
        commission = cost * self.commission_rate
        total_cost = cost + commission
        
        if total_cost > self.balance:
            print(f"[!] Insufficient funds. Need: {total_cost:.2f}, Have: {self.balance:.2f}")
            return False
        
        self.balance -= total_cost
        self.positions[symbol] = self.positions.get(symbol, 0) + quantity
        
        self._log_trade('BUY', symbol, price, quantity, commission)
        print(f"[+] BOUGHT {quantity} {symbol} @ {price:.2f}. Comm: {commission:.2f}")
        return True

    def sell(self, symbol, price, quantity):
        if symbol not in self.positions or self.positions[symbol] < quantity:
            print(f"[!] Not enough shares to sell. Have: {self.positions.get(symbol, 0)}")
            return False
        
        revenue = price * quantity
        commission = revenue * self.commission_rate
        net_revenue = revenue - commission
        
        self.balance += net_revenue
        self.positions[symbol] -= quantity
        if self.positions[symbol] == 0:
            del self.positions[symbol]
            
        self._log_trade('SELL', symbol, price, quantity, commission)
        print(f"[-] SOLD {quantity} {symbol} @ {price:.2f}. Comm: {commission:.2f}")
        return True

    def _log_trade(self, action, symbol, price, quantity, commission):
        new_row = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'symbol': symbol,
            'price': price,
            'quantity': quantity,
            'commission': commission,
            'balance_after': self.balance
        }
        
        # Use concat instead of append
        new_df = pd.DataFrame([new_row])
        self.trade_log = pd.concat([self.trade_log, new_df], ignore_index=True)
        self.trade_log.to_csv(self.log_file, index=False)

    def get_portfolio_value(self, current_prices):
        """
        Calculates total portfolio value (Cash + Stock Value).
        current_prices: dict {symbol: price}
        """
        stock_value = 0.0
        for sym, qty in self.positions.items():
            price = current_prices.get(sym, 0.0)
            stock_value += qty * price
            
        return self.balance + stock_value

    def get_summary(self):
        return {
            'balance': self.balance,
            'positions': self.positions,
            'initial_capital': self.initial_capital
        }
