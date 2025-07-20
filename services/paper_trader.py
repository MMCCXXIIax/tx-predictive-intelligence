# services/paper_trader.py

class PaperTrader:
    def __init__(self, starting_balance=10000.0, default_qty=1, stop_loss_pct=0.03, take_profit_pct=0.06):
        self.balance = starting_balance
        self.default_qty = default_qty
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

        self.positions = {}  # symbol -> {entry_price, qty, pattern}
        self.trades = []     # full trade history
        self.total_profit = 0.0

    def can_buy(self, symbol):
        return symbol not in self.positions

    def can_sell(self, symbol, current_price):
        return symbol in self.positions and current_price > 0

    def buy(self, symbol, price, pattern, confidence):
        qty = self.default_qty
        cost = price * qty

        self.positions[symbol] = {
            "entry_price": price,
            "qty": qty,
            "pattern": pattern,
            "confidence": confidence,
            "buy_time": None  # Optional: Add datetime.now() if needed
        }

        trade = {
            "symbol": symbol,
            "action": "BUY",
            "price": round(price, 2),
            "qty": qty,
            "pattern": pattern,
            "confidence": f"{confidence:.0%}",
            "pnl": None
        }
        self.trades.append(trade)
        return trade

    def sell(self, symbol, price, reason="manual"):
        if symbol not in self.positions:
            return None

        position = self.positions.pop(symbol)
        entry_price = position["entry_price"]
        qty = position["qty"]
        pattern = position["pattern"]

        pnl = round((price - entry_price) * qty, 2)
        self.total_profit += pnl

        trade = {
            "symbol": symbol,
            "action": "SELL",
            "price": round(price, 2),
            "qty": qty,
            "pattern": pattern,
            "pnl": pnl,
            "reason": reason
        }

        self.trades.append(trade)
        return trade

    def check_auto_sell(self, symbol, current_price):
        """
        Checks if a symbol should be sold due to stop loss or take profit.
        If so, it triggers a sell and returns the trade dictionary.
        """
        if symbol not in self.positions:
            return None

        entry = self.positions[symbol]["entry_price"]
        sl_price = entry * (1 - self.stop_loss_pct)
        tp_price = entry * (1 + self.take_profit_pct)

        if current_price <= sl_price:
            return self.sell(symbol, current_price, reason="stop_loss")
        elif current_price >= tp_price:
            return self.sell(symbol, current_price, reason="take_profit")
        return None

    def get_open_positions(self):
        return self.positions

    def get_trade_log(self):
        return self.trades

    def get_total_pnl(self):
        return self.total_profit