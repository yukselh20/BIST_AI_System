from backtesting import Strategy
import pandas_ta as ta

class BaseStrategy(Strategy):
    """
    Base Strategy class with built-in risk management features.
    """
    stop_loss_pct = 0.02  # 2% Default Stop Loss
    take_profit_pct = 0.05 # 5% Default Take Profit
    
    def init(self):
        """
        Initialize indicators here.
        Example: self.rsi = self.I(ta.rsi, self.data.Close, 14)
        """
        pass

    def next(self):
        """
        Main strategy logic. Called for every candle.
        """
        pass

    def check_risk_management(self):
        """
        Checks for stop-loss and take-profit conditions for open trades.
        This is a simple implementation. Backtesting.py has built-in sl/tp params 
        in self.buy(), but managing it manually gives more control (e.g. trailing).
        """
        for trade in self.trades:
            if trade.is_long:
                # Simple Stop Loss
                if self.data.Close[-1] < trade.entry_price * (1 - self.stop_loss_pct):
                    trade.close()
                # Simple Take Profit
                elif self.data.Close[-1] > trade.entry_price * (1 + self.take_profit_pct):
                    trade.close()
