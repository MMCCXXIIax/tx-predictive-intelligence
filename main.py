# main.py
import time
from datetime import datetime
from detectors.ai_pattern_logic import detect_all_patterns
from services.data_router import DataRouter
from services.paper_trader import PaperTrader
import os

# TX Copilot v0.9 — Multi-Asset Real-Time Scanner (Crypto + Stocks + Forex)

class TXConfig:
    ASSET_TYPES = {
        "bitcoin": "crypto",
        "ethereum": "crypto",
        "solana": "crypto",
        "AAPL": "stock",
        "TSLA": "stock",
        "EURUSD": "forex",
        "GBPUSD": "forex"
    }
    REFRESH_INTERVAL = 30
    CANDLE_LIMIT = 100
    ALERT_CONFIDENCE_THRESHOLD = 0.9
    ALERT_TYPES = ["CONSOLE"]

    # ✅ Pattern watchlist
    PATTERN_WATCHLIST = [
        "Doji",
        "Hammer",
        "Bullish Engulfing",
        "Morning Star",
        "Spinning Top",
        "Inverted Hammer",
        "Bearish Engulfing",
        "Evening Star",
        "Three White Soldiers",
        "Three Black Crows",
        "Piercing Line",
        "Dark Cloud Cover",
        "Harami Bullish",
        "Harami Bearish",
        "Tweezer Top",
        "Tweezer Bottom",
        "Dragonfly Doji",
        "Hanging Man",
        "Marubozu",
        "Shooting Star"
    ]

    # ✅ Enable/disable paper trading
    ENABLE_PAPER_TRADING = True

class AlertSystem:
    LOG_PATH = "tx_alert_log.txt"

    @staticmethod
    def trigger_alert(symbol, detection, last_price):
        pattern_name = detection.get("name")
        confidence = detection.get("confidence", 0.0)
        explanation = detection.get("explanation", "")
        action = detection.get("action", "Use discretion. Validate before trading.")

        if confidence < TXConfig.ALERT_CONFIDENCE_THRESHOLD:
            return

        if TXConfig.PATTERN_WATCHLIST and pattern_name not in TXConfig.PATTERN_WATCHLIST:
            return

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        alert_msg = f"""
🚨 TX REAL-TIME ALERT 🚨
===========================
Asset: {symbol}
Pattern: {pattern_name}
Confidence: {confidence:.0%}
Last Price: ${last_price:,.2f}
Time: {timestamp}
---------------------------
{explanation}
Action: {action}
===========================
🔔 Sent to: {', '.join(TXConfig.ALERT_TYPES)}
"""
        print(alert_msg)

        with open(AlertSystem.LOG_PATH, "a") as log_file:
            log_file.write(f"{timestamp} | {symbol} | {pattern_name} | {confidence:.2f} | ${last_price:.2f} | {action}\n")

class TXEngine:
    def __init__(self):
        self.router = DataRouter(TXConfig)
        self.scan_id = 0
        self.trader = PaperTrader() if TXConfig.ENABLE_PAPER_TRADING else None
        self.recent_alerts = {}  # Track recent alerts to prevent spam

    def run(self):
        print("=" * 60)
        print("🚀 TX Copilot v0.9 — Multi-Asset Real-Time Scanner + Paper Trading")
        print(f"Monitoring: {', '.join(TXConfig.ASSET_TYPES.keys())}")
        print("=" * 60)

        try:
            while True:
                self.scan()
                time.sleep(TXConfig.REFRESH_INTERVAL)
        except KeyboardInterrupt:
            print("🛑 TX Copilot stopped manually.")

    def scan(self):
        self.scan_id += 1
        print(f"\n🔍 TX Scan #{self.scan_id} @ {datetime.now().strftime('%H:%M:%S')}")

        for symbol in TXConfig.ASSET_TYPES.keys():
            candles = self.router.get_latest_candles(symbol)
            if not candles or len(candles) < 4:
                print(f"  ⏳ {symbol}: Not enough data yet.")
                continue

            try:
                result = detect_all_patterns(candles)

                high_conf = [
                    r for r in result
                    if r["confidence"] is not None
                    and r["confidence"] >= TXConfig.ALERT_CONFIDENCE_THRESHOLD
                    and (not TXConfig.PATTERN_WATCHLIST or r["name"] in TXConfig.PATTERN_WATCHLIST)
                ]

                if high_conf:
                    strongest = sorted(high_conf, key=lambda x: x["confidence"], reverse=True)[0]
                    last_price = candles[-1]["close"]
                    print(f"  ✅ {symbol}: {strongest['name']} ({strongest['confidence']:.0%})")

                    # 🔔 Alert logic with cooldown (prevent spam for same pattern)
                    alert_key = f"{symbol}_{strongest['name']}"
                    current_time = time.time()
                    
                    # Only alert if pattern hasn't been seen in last 5 minutes (300 seconds)
                    if alert_key not in self.recent_alerts or (current_time - self.recent_alerts[alert_key]) > 300:
                        AlertSystem.trigger_alert(symbol, strongest, last_price)
                        self.recent_alerts[alert_key] = current_time
                    else:
                        print(f"   🔇 {symbol}: {strongest['name']} (alert cooldown active)")

                    # 🧠 Paper trading logic
                    if TXConfig.ENABLE_PAPER_TRADING and self.trader:
                        if self.trader.can_buy(symbol):
                            trade_msg = self.trader.buy(
                                symbol=symbol,
                                price=last_price,
                                pattern=strongest["name"],
                                confidence=strongest["confidence"]
                            )
                            print("   📈 PAPER TRADE:", trade_msg)

                        # 🧪 In future: add self.trader.sell(...) here when pattern indicates reversal

                else:
                    print(f"  ✅ {symbol}: No strong pattern detected.")
            except Exception as e:
                print(f"  ⚠️ {symbol} detection error: {e}")

if __name__ == "__main__":
    TXEngine().run()