# services/data_router.py

import threading
import time
from services.crypto_data_services import CryptoDataService
from services.alpha_data_services import AlphaDataService

class DataRouter:
    def __init__(self, config):
        self.config = config
        self.crypto_service = CryptoDataService(
            symbols=[s for s, t in config.ASSET_TYPES.items() if t == "crypto"],
            refresh_interval=config.REFRESH_INTERVAL,
            candle_limit=config.CANDLE_LIMIT
        )
        self.alpha_service = AlphaDataService(candle_limit=config.CANDLE_LIMIT)

        # Store stock/forex symbols separately
        self.stock_symbols = [s for s, t in config.ASSET_TYPES.items() if t == "stock"]
        self.forex_symbols = [s for s, t in config.ASSET_TYPES.items() if t == "forex"]

    def get_latest_candles(self, symbol):
        asset_type = self.config.ASSET_TYPES.get(symbol)
        if asset_type == "crypto":
            return self.crypto_service.get_latest_candles(symbol)
        elif asset_type == "stock":
            return self.alpha_service.get_latest_candles(symbol, market_type="stock")
        elif asset_type == "forex":
            return self.alpha_service.get_latest_candles(symbol, market_type="forex")
        else:
            print(f"⚠️ Unknown asset type for symbol: {symbol}")
            return []

    def start_alpha_vantage_loop(self, refresh_interval=60):
        def refresh_loop():
            while True:
                print("🔄 Refreshing Alpha Vantage OHLC data (stocks + forex)...")
                for symbol in self.stock_symbols:
                    self.alpha_service.get_latest_candles(symbol, market_type="stock")
                for symbol in self.forex_symbols:
                    self.alpha_service.get_latest_candles(symbol, market_type="forex")
                time.sleep(refresh_interval)

        thread = threading.Thread(target=refresh_loop, daemon=True)
        thread.start()
        print("✅ Alpha Vantage background updater started.")