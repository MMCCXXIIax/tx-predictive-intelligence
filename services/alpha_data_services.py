# services/alpha_data_service.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ALPHA_VANTAGE_KEY")

class AlphaDataService:
    def __init__(self, candle_limit=100):
        self.candle_limit = candle_limit
        self.cache = {}  # Cache to store recent data

    def get_latest_candles(self, symbol, market_type="stock"):
        try:
            if not API_KEY:
                print(f"⚠️ Alpha Vantage API key not found. Please set ALPHA_VANTAGE_KEY in your environment.")
                return []

            if market_type == "stock":
                function = "TIME_SERIES_INTRADAY"
                interval = "5min"
                url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&apikey={API_KEY}&outputsize=compact"
                response = requests.get(url, timeout=10)
                response_data = response.json()
                data = response_data.get(f"Time Series ({interval})", {})
                
                # Check for API errors
                if "Error Message" in response_data:
                    print(f"⚠️ Alpha Vantage API error for {symbol}: {response_data['Error Message']}")
                    return []
                if "Note" in response_data:
                    print(f"⚠️ Alpha Vantage rate limit for {symbol}: {response_data['Note']}")
                    return []
                    
            elif market_type == "forex":
                from_symbol, to_symbol = symbol[:3], symbol[3:]
                function = "FX_INTRADAY"
                interval = "5min"
                url = f"https://www.alphavantage.co/query?function={function}&from_symbol={from_symbol}&to_symbol={to_symbol}&interval={interval}&apikey={API_KEY}&outputsize=compact"
                response = requests.get(url, timeout=10)
                response_data = response.json()
                data = response_data.get(f"Time Series FX ({interval})", {})
                
                # Check for API errors
                if "Error Message" in response_data:
                    print(f"⚠️ Alpha Vantage API error for {symbol}: {response_data['Error Message']}")
                    return []
                if "Note" in response_data:
                    print(f"⚠️ Alpha Vantage rate limit for {symbol}: {response_data['Note']}")
                    return []
            else:
                raise ValueError("Unsupported market_type")

            if not data:
                print(f"⚠️ No data received from Alpha Vantage for {symbol}")
                return []

            candles = []
            for timestamp, values in sorted(data.items())[-self.candle_limit:]:
                candles.append({
                    "timestamp": int(self._to_unix(timestamp)),
                    "open": float(values["1. open"]),
                    "high": float(values["2. high"]),
                    "low": float(values["3. low"]),
                    "close": float(values["4. close"]),
                })
            # Cache the successful result
            cache_key = f"{symbol}_{market_type}"
            self.cache[cache_key] = candles
            return candles
        except Exception as e:
            print(f"⚠️ Alpha Vantage error for {symbol}: {e}")
            # Return cached data if available
            cache_key = f"{symbol}_{market_type}"
            if cache_key in self.cache:
                print(f"📦 Using cached data for {symbol}")
                return self.cache[cache_key]
            return []

    def _to_unix(self, timestr):
        from datetime import datetime
        dt = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
        return dt.timestamp()