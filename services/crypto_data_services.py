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
        self.max_retries = 5
        self.rate_limit_backoff = {symbol: 0 for symbol in symbols}  # Track rate limit backoff
        self.last_success = {symbol: 0 for symbol in symbols}  # Track last successful fetch

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
            result = self._fetch_data(symbol)
            
            if result == "success":
                # Reset all counters on success
                with self.lock:
                    self.retry_count[symbol] = 0
                    self.rate_limit_backoff[symbol] = 0
                    self.last_success[symbol] = time.time()
                time.sleep(self.refresh_interval)
                
            elif result == "rate_limited":
                # Handle rate limiting gracefully
                with self.lock:
                    self.rate_limit_backoff[symbol] = min(self.rate_limit_backoff[symbol] + 60, 600)  # Max 10 min backoff
                
                # Only print rate limit message occasionally to avoid spam
                if self.rate_limit_backoff[symbol] <= 120:  # Only log first few rate limits
                    print(f"ℹ️ {symbol}: Rate limited by CoinGecko, backing off for {self.rate_limit_backoff[symbol]}s")
                
                time.sleep(self.rate_limit_backoff[symbol])
                
            else:  # Other errors
                with self.lock:
                    self.retry_count[symbol] += 1
                    retry_count = self.retry_count[symbol]
                
                # Only print full traceback for non-rate-limit errors and not too frequently
                if retry_count <= 2:  # Limit error spam
                    print(f"⚠️ {symbol}: Network error (attempt {retry_count}/{self.max_retries})")
                
                # Exponential backoff for network errors
                if retry_count >= self.max_retries:
                    print(f"⚠️ {symbol}: Max retries reached, sleeping 10 minutes")
                    time.sleep(600)  # 10 minute pause after max retries
                    with self.lock:
                        self.retry_count[symbol] = 0
                else:
                    time.sleep(min(30 * retry_count, 300))  # Max 5 min backoff

    def _fetch_data(self, symbol):
        """Actual data fetching without recursion - returns status instead of raising exceptions"""
        try:
            url = f"https://api.coingecko.com/api/v3/coins/{symbol}/ohlc?vs_currency=usd&days=1"
            
            # Use session for better connection handling
            with requests.Session() as session:
                session.headers.update({
                    'User-Agent': 'TX-Trading-Intelligence/1.0',
                    'Accept': 'application/json'
                })
                
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
                        return "success"
                    else:
                        return "error"  # Invalid data format
                        
                elif response.status_code == 429:
                    return "rate_limited"
                    
                else:
                    return "error"  # Other HTTP errors
                    
        except requests.exceptions.RequestException:
            return "error"  # Network/connection errors
        except Exception:
            return "error"  # Any other errors

    def get_latest_candles(self, symbol):
        """Thread-safe access to candles data"""
        with self.lock:
            return self.candles.get(symbol, []).copy()
    
    def stop(self):
        """Gracefully stop all threads"""
        self.running = False
