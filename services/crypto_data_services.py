import requests
import time
import threading
from threading import Lock

class CryptoDataService:
    def __init__(self, symbols, refresh_interval=180, candle_limit=100):
        self.symbols = symbols
        self.refresh_interval = max(refresh_interval, 60)  # Minimum 60 second interval
        self.candle_limit = candle_limit
        self.candles = {symbol: [] for symbol in symbols}
        self.running = True
        self.lock = Lock()  # Thread safety
        self.retry_count = {symbol: 0 for symbol in symbols}
        self.max_retries = 3

        # Start threads with more spacing to avoid conflicts
        for i, symbol in enumerate(symbols):
            threading.Thread(
                target=self._safe_update_data,
                args=(symbol,),
                daemon=True,
                name=f"crypto-{symbol}"
            ).start()
            time.sleep(1)  # More spacing between thread starts

    def _safe_update_data(self, symbol):
        """Safe wrapper to prevent recursion issues"""
        while self.running:
            try:
                self._fetch_data(symbol)
                # Reset retry count on success
                with self.lock:
                    self.retry_count[symbol] = 0
            except Exception as e:
                with self.lock:
                    self.retry_count[symbol] += 1
                    retry_count = self.retry_count[symbol]
                
                import traceback
                print(f"⚠️ Error fetching {symbol} (crypto): {str(e)[:100]}")
                print(f"⚠️ {symbol} traceback:")
                traceback.print_exc()
                
                # Exponential backoff for retries
                if retry_count >= self.max_retries:
                    print(f"⚠️ {symbol}: Max retries reached, sleeping longer")
                    time.sleep(300)  # 5 minute pause after max retries
                    with self.lock:
                        self.retry_count[symbol] = 0
                else:
                    time.sleep(30 * retry_count)  # 30, 60, 90 second backoff
            
            # Always sleep the full interval
            time.sleep(self.refresh_interval)

    def _fetch_data(self, symbol):
        """Actual data fetching without recursion"""
        url = f"https://api.coingecko.com/api/v3/coins/{symbol}/ohlc?vs_currency=usd&days=1"
        
        # Use session for better connection handling
        with requests.Session() as session:
            response = session.get(url, timeout=15)
            
            if response.status_code == 200:
                raw = response.json()
                if isinstance(raw, list) and raw:
                    formatted = [{
                        "timestamp": item[0] // 1000,
                        "open": float(item[1]),
                        "high": float(item[2]),
                        "low": float(item[3]),
                        "close": float(item[4])
                    } for item in raw[-self.candle_limit:]]
                    
                    with self.lock:
                        self.candles[symbol] = formatted
                else:
                    print(f"⚠️ {symbol}: Invalid data format from CoinGecko")
            elif response.status_code == 429:
                print(f"⚠️ {symbol}: Rate limited by CoinGecko")
                raise Exception("Rate limited")
            else:
                print(f"⚠️ {symbol}: HTTP {response.status_code} from CoinGecko")
                raise Exception(f"HTTP {response.status_code}")

    def get_latest_candles(self, symbol):
        """Thread-safe access to candles data"""
        with self.lock:
            return self.candles.get(symbol, []).copy()
    
    def stop(self):
        """Gracefully stop all threads"""
        self.running = False
