# services/crypto_data_services.py

import requests
import time
import threading

class CryptoDataService:
    def __init__(self, symbols, refresh_interval=30, candle_limit=100):
        self.symbols = symbols
        self.refresh_interval = refresh_interval
        self.candle_limit = candle_limit
        self.candles = {symbol: [] for symbol in symbols}
        self.running = True

        for symbol in symbols:
            threading.Thread(target=self._update_data, args=(symbol,), daemon=True).start()
            time.sleep(0.2)

    def _update_data(self, symbol):
        url = f"https://api.coingecko.com/api/v3/coins/{symbol}/ohlc?vs_currency=usd&days=1"
        while self.running:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    raw = response.json()
                    formatted = [{
                        "timestamp": item[0] // 1000,
                        "open": item[1],
                        "high": item[2],
                        "low": item[3],
                        "close": item[4]
                    } for item in raw[-self.candle_limit:]]
                    self.candles[symbol] = formatted
            except Exception as e:
                print(f"⚠️ Error fetching {symbol} (crypto): {e}")
            time.sleep(self.refresh_interval)

    def get_latest_candles(self, symbol):
        return self.candles.get(symbol, [])