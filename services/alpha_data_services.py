# services/alpha_data_service.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ALPHA_VANTAGE_KEY")

class AlphaDataService:
    def __init__(self, candle_limit=100):
        self.candle_limit = candle_limit

    def get_latest_candles(self, symbol, market_type="stock"):
        try:
            if market_type == "stock":
                function = "TIME_SERIES_INTRADAY"
                interval = "5min"
                url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&apikey={API_KEY}&outputsize=compact"
                response = requests.get(url)
                data = response.json().get(f"Time Series ({interval})", {})
            elif market_type == "forex":
                from_symbol, to_symbol = symbol[:3], symbol[3:]
                function = "FX_INTRADAY"
                interval = "5min"
                url = f"https://www.alphavantage.co/query?function={function}&from_symbol={from_symbol}&to_symbol={to_symbol}&interval={interval}&apikey={API_KEY}&outputsize=compact"
                response = requests.get(url)
                data = response.json().get(f"Time Series FX ({interval})", {})
            else:
                raise ValueError("Unsupported market_type")

            candles = []
            for timestamp, values in sorted(data.items())[-self.candle_limit:]:
                candles.append({
                    "timestamp": int(self._to_unix(timestamp)),
                    "open": float(values["1. open"]),
                    "high": float(values["2. high"]),
                    "low": float(values["3. low"]),
                    "close": float(values["4. close"]),
                })
            return candles
        except Exception as e:
            print(f"⚠️ Alpha Vantage error for {symbol}: {e}")
            return []

    def _to_unix(self, timestr):
        from datetime import datetime
        dt = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
        return dt.timestamp()