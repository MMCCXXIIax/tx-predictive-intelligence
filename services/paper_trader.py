# services/paper_trader.py
import os
import csv
import threading
from datetime import datetime
from typing import Optional, Dict, Any

class PaperTrader:
    """
    Paper trading engine for TX.
    - Supports buys by qty or USD amount
    - Supports partial sells
    - Tracks positions, realized/unrealized PnL, trade history
    - Stop loss & take profit (percentages)
    - Thread-safe (simple Lock)
    """

    def __init__(
        self,
        starting_balance: float = 100000.0,
        default_qty: float = 1.0,
        stop_loss_pct: float = 0.03,
        take_profit_pct: float = 0.06,
        log_file: str = "tx_paper_trade_log.csv",
    ):
        self.lock = threading.Lock()
        self.balance = float(starting_balance)
        self.default_qty = float(default_qty)
        self.stop_loss_pct = float(stop_loss_pct)
        self.take_profit_pct = float(take_profit_pct)

        # positions: symbol -> { avg_entry, quantity, invested, pattern, confidence, last_update }
        self.positions: Dict[str, Dict[str, Any]] = {}

        # trades history: list of trade dicts
        self.trades = []

        # cumulative realized profit (USD)
        self.realized_profit = 0.0

        # file logging
        self.log_file = log_file
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp", "Symbol", "Action", "Pattern", "Confidence",
                    "Price", "Quantity", "Amount", "PnL", "Reason", "Balance"
                ])

    # ---------------------------
    # Core operations
    # ---------------------------
    def can_buy(self, symbol: str) -> bool:
        # Currently allow averaging into same symbol
        return True

    def buy(
        self,
        symbol: str,
        price: float,
        pattern: str = "Manual",
        confidence: float = 1.0,
        qty: Optional[float] = None,
        amount_usd: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Execute a simulated buy.
        - qty: units to buy (preferred)
        - amount_usd: USD to spend (if qty not provided)
        Returns trade dict or error dict on insufficient balance.
        """
        with self.lock:
            price = float(price)
            confidence = float(confidence)

            if qty is None:
                if amount_usd is None:
                    qty = float(self.default_qty)
                else:
                    amount_usd = float(amount_usd)
                    if amount_usd > self.balance:
                        return {"error": "insufficient_balance", "message": f"Not enough balance to buy ${amount_usd:.2f}"}
                    qty = amount_usd / price

            amount_spent = qty * price
            if amount_spent > self.balance:
                return {"error": "insufficient_balance", "message": f"Not enough balance to buy ${amount_spent:.2f}"}

            # update/create position
            if symbol in self.positions:
                pos = self.positions[symbol]
                total_cost = pos["avg_entry"] * pos["quantity"] + amount_spent
                total_qty = pos["quantity"] + qty
                pos["avg_entry"] = total_cost / total_qty if total_qty else pos["avg_entry"]
                pos["quantity"] = total_qty
                pos["invested"] += amount_spent
                pos["pattern"] = pattern
                pos["confidence"] = confidence
                pos["last_update"] = datetime.utcnow().isoformat()
            else:
                self.positions[symbol] = {
                    "avg_entry": price,
                    "quantity": qty,
                    "invested": amount_spent,
                    "pattern": pattern,
                    "confidence": confidence,
                    "last_update": datetime.utcnow().isoformat()
                }

            self.balance -= amount_spent

            trade = {
                "symbol": symbol,
                "action": "BUY",
                "price": round(price, 6),
                "qty": round(qty, 8),
                "pattern": pattern,
                "confidence": round(confidence, 4),
                "amount": round(amount_spent, 2),
                "pnl": None,
                "reason": "buy",
                "time": datetime.now().strftime("%H:%M:%S")
            }

            self.trades.append(trade)
            self._log_trade(trade)
            return trade

    def sell(
        self,
        symbol: str,
        price: float,
        qty: Optional[float] = None,
        reason: str = "manual"
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a simulated sell. Supports partial/full sells.
        Returns trade dict or None if no position exists.
        """
        with self.lock:
            price = float(price)
            if symbol not in self.positions:
                return None

            pos = self.positions[symbol]
            available_qty = float(pos["quantity"])
            sell_qty = qty if qty is not None else available_qty
            sell_qty = min(sell_qty, available_qty)
            if sell_qty <= 0:
                return None

            amount_received = sell_qty * price
            cost_basis = sell_qty * pos["avg_entry"]
            profit = round(amount_received - cost_basis, 2)

            # update position
            pos["quantity"] = round(pos["quantity"] - sell_qty, 8)
            pos["invested"] = round(pos["invested"] - cost_basis, 2)
            if pos["quantity"] <= 0.00000001:
                # fully closed
                del self.positions[symbol]

            # update account
            self.balance += amount_received
            self.realized_profit += profit

            trade = {
                "symbol": symbol,
                "action": "SELL",
                "price": round(price, 6),
                "qty": round(sell_qty, 8),
                "pattern": pos.get("pattern", "Exit") if "pos" in locals() else "Exit",
                "confidence": round(pos.get("confidence", 0.0), 4) if "pos" in locals() else 0.0,
                "amount": round(amount_received, 2),
                "pnl": profit,
                "reason": reason,
                "time": datetime.now().strftime("%H:%M:%S")
            }

            self.trades.append(trade)
            self._log_trade(trade)
            return trade

    # convenience wrapper used by API: explicit close
    def close_position(self, symbol: str, price: float, qty: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Close (sell) position manually. Returns trade dict or None."""
        return self.sell(symbol, price, qty=qty, reason="manual_close")

    # ---------------------------
    # Auto sell checks (SL/TP)
    # ---------------------------
    def check_auto_sell(self, symbol: str, current_price: float) -> Optional[Dict[str, Any]]:
        """
        If position exists and current price hits SL/TP, execute sell and return trade.
        """
        with self.lock:
            if symbol not in self.positions:
                return None
            entry = float(self.positions[symbol]["avg_entry"])
            sl_price = entry * (1 - self.stop_loss_pct)
            tp_price = entry * (1 + self.take_profit_pct)
            # If current_price <= SL -> sell, if >= TP -> sell (TP priority can be reversed)
            if current_price <= sl_price:
                return self.sell(symbol, current_price, reason="stop_loss")
            if current_price >= tp_price:
                return self.sell(symbol, current_price, reason="take_profit")
            return None

    # ---------------------------
    # Portfolio / reporting
    # ---------------------------
    def get_open_positions(self) -> Dict[str, Dict[str, Any]]:
        with self.lock:
            # return a deep-ish copy to avoid accidental mutation
            return {s: dict(v) for s, v in self.positions.items()}

    def get_trade_log(self) -> list:
        with self.lock:
            return list(self.trades)

    def get_total_realized_pnl(self) -> float:
        with self.lock:
            return round(self.realized_profit, 2)

    def get_portfolio_value(self, market_prices: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Compute portfolio snapshot.
        - market_prices: dict symbol -> current_price (float). If not provided, unrealized = 0.
        Returns:
            {
              "balance": float,
              "invested": float,
              "open_positions": {symbol: {..., "market_value":..., "unrealized_pnl":...}},
              "total_equity": float,
              "realized_pnl": float
            }
        """
        with self.lock:
            invested = 0.0
            open_positions = {}
            unrealized_total = 0.0

            for symbol, pos in self.positions.items():
                qty = float(pos["quantity"])
                invested_amount = float(pos["invested"])
                invested += invested_amount

                market_price = None
                market_value = None
                unrealized = None
                if market_prices and symbol in market_prices and market_prices[symbol] is not None:
                    market_price = float(market_prices[symbol])
                    market_value = round(qty * market_price, 2)
                    unrealized = round(market_value - invested_amount, 2)
                    unrealized_total += unrealized

                open_positions[symbol] = {
                    "avg_entry": round(pos["avg_entry"], 6),
                    "quantity": round(qty, 8),
                    "invested": round(invested_amount, 2),
                    "pattern": pos.get("pattern"),
                    "confidence": pos.get("confidence"),
                    "market_price": market_price,
                    "market_value": market_value,
                    "unrealized_pnl": unrealized
                }

            total_equity = round(self.balance + (unrealized_total if unrealized_total else 0.0), 2)

            return {
                "balance": round(self.balance, 2),
                "invested": round(invested, 2),
                "open_positions": open_positions,
                "total_equity": total_equity,
                "realized_pnl": round(self.realized_profit, 2),
                "unrealized_pnl": round(unrealized_total, 2)
            }

    # ---------------------------
    # Logging
    # ---------------------------
    def _log_trade(self, trade: Dict[str, Any]):
        try:
            with open(self.log_file, mode="a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    trade.get("symbol"),
                    trade.get("action"),
                    trade.get("pattern", ""),
                    round(trade.get("confidence", 0.0), 4),
                    trade.get("price"),
                    trade.get("qty"),
                    trade.get("amount"),
                    trade.get("pnl"),
                    trade.get("reason", ""),
                    round(self.balance, 2)
                ])
        except Exception:
            # Logging failure shouldn't break the engine
            pass