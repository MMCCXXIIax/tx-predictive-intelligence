# services/trade_executor.py

from datetime import datetime

class TradeExecutor:
    LOG_PATH = "tx_trade_log.txt"

    @staticmethod
    def execute(symbol, pattern_name, confidence, price):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"""
💼 TX TRADE EXECUTION
===========================
Asset: {symbol}
Pattern: {pattern_name}
Confidence: {confidence:.0%}
Executed Price: ${price:,.2f}
Time: {timestamp}
Strategy: Paper Trade (Simulation)
===========================
""")

        # Save simulated trade to log
        with open(TradeExecutor.LOG_PATH, "a") as log:
            log.write(f"{timestamp} | {symbol} | {pattern_name} | {confidence:.2f} | ${price:.2f} | SIMULATED\n")