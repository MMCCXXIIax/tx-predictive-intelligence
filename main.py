# main.py
import time
import os
import json
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify
from detectors.ai_pattern_logic import detect_all_patterns
from services.data_router import DataRouter
from services.paper_trader import PaperTrader

# ====================== CONFIG ======================
class TXConfig:
    ASSET_TYPES = {
        "bitcoin": "crypto",
        "ethereum": "crypto",
        "solana": "crypto",
        "AAPL": "stock",
        "TSLA": "stock"
    }
    REFRESH_INTERVAL = 300
    CANDLE_LIMIT = 100
    ALERT_CONFIDENCE_THRESHOLD = 0.85
    ALERT_TYPES = ["CONSOLE", "WEB"]

    CACHE_FILE = "tx_cache.json"
    CACHE_DURATION = 300

    PATTERN_WATCHLIST = [
        "Bullish Engulfing",
        "Bearish Engulfing",
        "Morning Star",
        "Evening Star",
        "Three White Soldiers",
        "Three Black Crows"
    ]

    ENABLE_PAPER_TRADING = True

# ====================== GLOBAL STATE ======================
app_state = {
    "last_scan": [],
    "alerts": [],
    "paper_trades": []
}

# ====================== ALERT SYSTEM ======================
class AlertSystem:
    @staticmethod
    def trigger_alert(symbol, detection, last_price):
        confidence = detection.get("confidence", 0.0)
        if confidence < TXConfig.ALERT_CONFIDENCE_THRESHOLD:
            return

        pattern_name = detection.get("name")
        explanation = detection.get("explanation", "")
        action = detection.get("action", "Validate before trading.")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        alert = {
            "symbol": symbol,
            "pattern": pattern_name,
            "confidence": f"{confidence:.0%}",
            "price": f"${last_price:,.2f}",
            "time": timestamp,
            "explanation": explanation,
            "action": action
        }

        app_state["alerts"].insert(0, alert)
        if len(app_state["alerts"]) > 20:
            app_state["alerts"].pop()

        if "CONSOLE" in TXConfig.ALERT_TYPES:
            print(f"""
🚨 ALERT: {symbol} {pattern_name} ({confidence:.0%})
Price: ${last_price:,.2f} | Time: {timestamp}
---""")

# ====================== CACHING ======================
class DataCache:
    @staticmethod
    def load_cache():
        try:
            if os.path.exists(TXConfig.CACHE_FILE):
                with open(TXConfig.CACHE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}

    @staticmethod
    def save_cache(cache):
        try:
            with open(TXConfig.CACHE_FILE, 'w') as f:
                json.dump(cache, f)
        except:
            pass

    @staticmethod
    def get_cached(symbol):
        cache = DataCache.load_cache()
        data = cache.get(symbol, {})
        if data.get("timestamp"):
            cache_time = datetime.strptime(data["timestamp"], '%Y-%m-%d %H:%M:%S')
            if datetime.now() - cache_time < timedelta(seconds=TXConfig.CACHE_DURATION):
                return data.get("candles", [])
        return []

    @staticmethod
    def update_cache(symbol, candles):
        cache = DataCache.load_cache()
        cache[symbol] = {
            "candles": candles,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        DataCache.save_cache(cache)

# ====================== ENGINE ======================
class TXEngine:
    def __init__(self):
        self.router = DataRouter(TXConfig)
        self.scan_id = 0
        self.trader = PaperTrader() if TXConfig.ENABLE_PAPER_TRADING else None
        self.recent_alerts = {}
        threading.Thread(target=self.router.start_alpha_vantage_loop, daemon=True).start()

    def run_scan(self):
        self.scan_id += 1
        scan_time = datetime.now().strftime('%H:%M:%S')
        scan_results = []

        for symbol in TXConfig.ASSET_TYPES.keys():
            candles = DataCache.get_cached(symbol)
            if not candles:
                try:
                    candles = self.router.get_latest_candles(symbol)
                    if candles:
                        DataCache.update_cache(symbol, candles)
                except Exception as e:
                    print(f"⚠️ Data error for {symbol}: {str(e)}")

            if not candles or len(candles) < 4:
                scan_results.append({"symbol": symbol, "status": "no_data"})
                continue

            try:
                last_price = candles[-1]["close"]

                # ✅ Auto SELL logic
                if TXConfig.ENABLE_PAPER_TRADING and self.trader:
                    sell_trade = self.trader.check_auto_sell(symbol, last_price)
                    if sell_trade:
                        sell_trade["time"] = scan_time
                        app_state["paper_trades"].insert(0, sell_trade)

                result = detect_all_patterns(candles)
                best_pattern = None
                for r in result:
                    if (r["confidence"] >= TXConfig.ALERT_CONFIDENCE_THRESHOLD and
                        r["name"] in TXConfig.PATTERN_WATCHLIST):
                        if not best_pattern or r["confidence"] > best_pattern["confidence"]:
                            best_pattern = r

                

                else:
                    scan_results.append({
                        "symbol": symbol,
                        "status": "no_pattern",
                        "price": f"${last_price:,.2f}"
                    })

            except Exception as e:
                scan_results.append({
                    "symbol": symbol,
                    "status": "error",
                    "message": str(e)
                })

        app_state["last_scan"] = {
            "id": self.scan_id,
            "time": scan_time,
            "results": scan_results
        }

        
        if best_pattern:
                    alert_key = f"{symbol}_{best_pattern['name']}"
                    current_time = time.time()
                    if (alert_key not in self.recent_alerts or
                        (current_time - self.recent_alerts[alert_key]) > 300):
                        AlertSystem.trigger_alert(symbol, best_pattern, last_price)
                        self.recent_alerts[alert_key] = current_time

                    scan_results.append({
                        "symbol": symbol,
                        "status": "pattern",
                        "pattern": best_pattern["name"],
                        "confidence": f"{best_pattern['confidence']:.0%}",
                        "price": f"${last_price:,.2f}"
                    })

                    # Update global last_signal when pattern detected
                    app_state["last_signal"] = {
                        "symbol": symbol,
                        "pattern": best_pattern["name"],
                        "confidence": f"{best_pattern['confidence']:.0%}",
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "timeframe": "5m"  # Hardcoded for now
                    }

                    # Buy logic
                    if TXConfig.ENABLE_PAPER_TRADING and self.trader:
                        if self.trader.can_buy(symbol):
                            trade = self.trader.buy(
                                symbol,
                                last_price,
                                best_pattern["name"],
                                best_pattern["confidence"]
                            )
                            trade["time"] = scan_time
                            app_state["paper_trades"].insert(0, trade)

        return scan_results

# ====================== FLASK SERVER ======================
app = Flask(__name__)

# In your Flask app (main.py)
@app.route('/')
def dashboard():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>TX PREDICTIVE INTELLIGENCE</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --tx-green: #00ff88;
                --tx-black: #121212;
                --tx-gray: #1e1e1e;
                --tx-red: #ff5555;
            }
            body {
                font-family: 'Space Mono', monospace;
                background: var(--tx-black);
                color: white;
                margin: 0;
                padding: 20px;
            }
            .terminal {
                background: var(--tx-gray);
                border-radius: 8px;
                padding: 20px;
                max-width: 800px;
                margin: 0 auto;
                border: 1px solid #333;
            }
            .tx-header {
                color: var(--tx-green);
                border-bottom: 1px solid #333;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }
            .asset-row {
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #252525;
            }
            .asset-name {
                font-weight: bold;
                color: var(--tx-green);
            }
            .asset-price {
                font-feature-settings: "tnum";
            }
            .no-pattern {
                color: #777;
            }
            .pattern-detected {
                color: white;
                background: #0066ff;
                padding: 2px 6px;
                border-radius: 4px;
            }
            .tx-logo {
                font-size: 24px;
                letter-spacing: -1px;
            }
            .tx-tagline {
                color: #aaa;
                font-size: 14px;
            }
            .powered-by {
                text-align: right;
                font-size: 12px;
                color: #444;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="terminal">
            <!-- HEADER -->
            <div class="tx-header">
                <div class="tx-logo">TX PREDICTIVE INTELLIGENCE</div>
                <div class="tx-tagline">AI-Powered Market Anticipation System | Kampala, Uganda</div>
            </div>

            <!-- ASSET GRID -->
            <div class="asset-grid">
                {% for r in scan.results %}
                <div class="asset-row">
                    <span class="asset-name">{{ r.symbol }}</span>
                    <span class="asset-price">${{ r.price.split('$')[1] if r.price else 'N/A' }}</span>
                    <span class="{% if r.status == 'pattern' %}pattern-detected{% else %}no-pattern{% endif %}">
                        {% if r.status == 'pattern' %}
                            {{ r.pattern }} ({{ r.confidence }})
                        {% else %}
                            IDLE
                        {% endif %}
                    </span>
                </div>
                {% endfor %}
            </div>

            <!-- NEXT SCAN -->
            <div style="margin-top: 20px; color: #666;">
                Next scan in: <span id="countdown">300</span>s
            </div>

        <!-- Below "Next scan" counter -->
        <div style="margin: 15px 0; font-size: 12px; color: #555;">
            ⚡ <strong>12 traders</strong> live | Last signal: BTC Bullish Engulfing (2h ago)
        </div>

        <!-- Above PRO ACCESS -->
        <div style="background: #0d1a26; padding: 10px; border-radius: 4px; margin: 20px 0;">
            <div style="color: var(--tx-green); font-weight: bold;">🚨 Latest Signal</div>
            <div>ETH 5m TF: Morning Star (87%)</div>
            <div style="font-size: 12px; color: #777;">2025-07-20 19:45:22 UTC</div>
        </div>


            <!-- CTA -->
            <div style="margin-top: 30px; background: #000; padding: 15px; border-radius: 4px;">
                <h3 style="margin-top: 0; color: var(--tx-green);">🚀 PRO ACCESS</h3>
                <p>Unlock real-time AI predictions:</p>
                <ul>
                    <li>Telegram/WhatsApp alerts</li>
                    <li>15+ assets including forex</li>
                    <li>Historical backtesting</li>
                </ul>
                <p><strong>$5/month via USDT</strong> | DM @YourHandle</p>
            </div>

            <div class="powered-by">
                TX Engine v0.9 | Data: Alpha Vantage
            </div>
        </div>

        <script>
            // Auto-refresh countdown
            let seconds = {{ refresh_seconds }};
            function updateCountdown() {
                document.getElementById('countdown').textContent = seconds;
                seconds--;
                if (seconds < 0) location.reload();
            }
            setInterval(updateCountdown, 1000);
        </script>
    </body>
    </html>
    ''',
    scan=app_state.get("last_scan", {"results": []}),
    refresh_seconds=TXConfig.REFRESH_INTERVAL
    )

@app.route('/api/scan')
def api_scan():
    return jsonify(app_state)

# ====================== MAIN ======================
if __name__ == "__main__":
    engine = TXEngine()
    engine.run_scan()

    def scan_scheduler():
        while True:
            time.sleep(TXConfig.REFRESH_INTERVAL)
            engine.run_scan()

    threading.Thread(target=scan_scheduler, daemon=True).start()
    print("✅ TX Copilot running at http://localhost:8080 ...")
    app.run(host='0.0.0.0', port=8080)