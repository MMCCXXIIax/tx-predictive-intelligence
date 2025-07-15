# services/paper_trader.py

import os
import csv
from datetime import datetime

class PaperTrader:
    def __init__(self, starting_balance=100000.0, log_file="tx_paper_trade_log.csv"):
        self.balance = starting_balance
        self.positions = {}  # e.g., { "bitcoin": { "avg_entry": 30000, "quantity": 0.1, "invested": 3000 } }
        self.log_file = log_file

        if not os.path.exists(self.log_file):
            with open(self.log_file, mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp", "Symbol", "Action", "Pattern", "Confidence",
                    "Price", "Quantity", "Amount", "Balance", "Realized_PnL"
                ])

    def can_buy(self, symbol):
        return True  # Will later allow config for max positions, etc.

    def buy(self, symbol, price, pattern, confidence, amount_usd=1000.0):
        if self.balance < amount_usd:
            return f"❌ Insufficient balance to buy {symbol} for ${amount_usd:.2f}"

        quantity = amount_usd / price

        if symbol in self.positions:
            # Update average entry price and quantity
            pos = self.positions[symbol]
            total_cost = pos["avg_entry"] * pos["quantity"] + price * quantity
            total_qty = pos["quantity"] + quantity
            pos["avg_entry"] = total_cost / total_qty
            pos["quantity"] = total_qty
            pos["invested"] += amount_usd
        else:
            self.positions[symbol] = {
                "avg_entry": price,
                "quantity": quantity,
                "invested": amount_usd,
                "pattern": pattern,
                "confidence": confidence
            }

        self.balance -= amount_usd
        self._log_trade("BUY", symbol, pattern, confidence, price, quantity, amount_usd, pnl=None)
        return f"✅ Simulated BUY: {symbol} | Qty: {quantity:.6f} @ ${price:.2f} | Cost: ${amount_usd:.2f}"

    def can_sell(self, symbol):
        return symbol in self.positions and self.positions[symbol]["quantity"] > 0

    def sell(self, symbol, price, pattern="Exit", confidence=1.0, quantity=None):
        if not self.can_sell(symbol):
            return f"⚠️ No position in {symbol} to sell."

        pos = self.positions[symbol]
        qty_to_sell = quantity or pos["quantity"]
        qty_to_sell = min(qty_to_sell, pos["quantity"])
        amount = qty_to_sell * price
        cost_basis = pos["avg_entry"] * qty_to_sell
        realized_pnl = amount - cost_basis

        # Update or close position
        pos["quantity"] -= qty_to_sell
        pos["invested"] -= cost_basis
        if pos["quantity"] <= 0:
            del self.positions[symbol]

        self.balance += amount
        self._log_trade("SELL", symbol, pattern, confidence, price, qty_to_sell, amount, pnl=realized_pnl)

        return (
            f"✅ Simulated SELL: {symbol} | Qty: {qty_to_sell:.6f} @ ${price:.2f} "
            f"| Proceeds: ${amount:.2f} | PnL: ${realized_pnl:.2f}"
        )

    def _log_trade(self, action, symbol, pattern, confidence, price, quantity, amount_usd, pnl=None):
        with open(self.log_file, mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                symbol,
                action,
                pattern,
                round(confidence, 2),
                round(price, 4),
                round(quantity, 6),
                round(amount_usd, 2),
                round(self.balance, 2),
                "" if pnl is None else round(pnl, 2)
            ])

    def get_portfolio_snapshot(self):
        snapshot = {
            "balance": round(self.balance, 2),
            "positions": {}
        }
        for symbol, pos in self.positions.items():
            snapshot["positions"][symbol] = {
                "avg_entry": round(pos["avg_entry"], 4),
                "quantity": round(pos["quantity"], 6),
                "invested": round(pos["invested"], 2)
            }
        return snapshot