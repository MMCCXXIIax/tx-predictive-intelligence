# main.py
from flask_cors import CORS
import time
import os
import json
import threading
import random
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request, make_response

from detectors.ai_pattern_logic import detect_all_patterns
from services.data_router import DataRouter
from services.paper_trader import PaperTrader
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env fil
#  Define Flask app first
app = Flask(__name__)
CORS(app,
     origins=[
         "https://23172b0b-3460-43d6-96ee-0ae883210c36.lovableproject.com"
     ])

#

# Your other code (config, engine, db setup, etc.)
# ====================== INITIALIZE REPLIT DB ======================
try:
    from replit import db
except:
    # Fallback for local testing
    class MockDB:

        def __init__(self):
            self.data = {}

        def __getitem__(self, key):
            return self.data.get(key)

        def __setitem__(self, key, value):
            self.data[key] = value

        def get(self, key, default=None):
            return self.data.get(key, default)

    db = MockDB()

# Initialize database collections if they don't exist
if 'visitors' not in db:
    db['visitors'] = {}
if 'detections' not in db:
    db['detections'] = []
if 'user_count' not in db:
    db['user_count'] = 12  # Initial count


# ====================== TRACKING SYSTEM ======================
def track_visit(request):
    """Record a visit and return visitor ID"""
    visitor_id = request.cookies.get('visitor_id')

    if not visitor_id:
        # New visitor
        visitor_id = str(uuid.uuid4())
        db['visitors'][visitor_id] = {
            'first_seen': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip': request.remote_addr,
            'visit_count': 1
        }
        db['user_count'] = len(db['visitors'])
    else:
        # Returning visitor
        if visitor_id in db['visitors']:
            db['visitors'][visitor_id]['last_seen'] = datetime.now().isoformat(
            )
            db['visitors'][visitor_id]['visit_count'] += 1

    return visitor_id


def log_detection(symbol, pattern, confidence, price):
    """Store pattern detection for future AI training"""
    detection_id = str(uuid.uuid4())

    db['detections'].append({
        'id': detection_id,
        'timestamp': datetime.now().isoformat(),
        'symbol': symbol,
        'pattern': pattern,
        'confidence': confidence,
        'price': price,
        'outcome': None,  # To be set later
        'verified': False
    })

    # Keep only last 10,000 detections
    if len(db['detections']) > 10000:
        db['detections'] = db['detections'][-10000:]

    return detection_id


# ====================== CONFIG ======================
class TXConfig:
    ASSET_TYPES = {
        "bitcoin": "crypto",
        "ethereum": "crypto",
        "solana": "crypto",
        "AAPL": "stock",
        "TSLA": "stock"
    }
    REFRESH_INTERVAL = 120
    CANDLE_LIMIT = 100
    ALERT_CONFIDENCE_THRESHOLD = 0.85
    ALERT_TYPES = ["CONSOLE", "WEB"]

    CACHE_FILE = "tx_cache.json"
    CACHE_DURATION = 180

    PATTERN_WATCHLIST = [
        "Bullish Engulfing", "Bearish Engulfing", "Morning Star",
        "Evening Star", "Three White Soldiers", "Three Black Crows", "Hammer",
        "Inverted Hammer", "Shooting Star", "Shooting Star", "Piercing Line",
        "Dark Cloud Cover"
    ]

    ENABLE_PAPER_TRADING = True


# ====================== GLOBAL STATE ======================
app_state = {
    "last_scan": [],
    "alerts": [],
    "paper_trades": [],
    "last_signal": None
}


# ====================== ALERT SYSTEM ======================
class AlertSystem:

    @staticmethod
    def trigger_alert(symbol, detection, last_price):
        confidence = detection.get("confidence", 0.0)
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
            "explanation": detection.get("explanation",
                                         "No explanation available"),
            "action": action
        }

        app_state["alerts"].insert(0, alert)
        if len(app_state["alerts"]) > 20:
            app_state["alerts"].pop()

        # Update last signal whenever new alert triggers
        app_state["last_signal"] = {
            "symbol": symbol,
            "pattern": pattern_name,
            "confidence": f"{confidence:.0%}",
            "time": timestamp,
            "timeframe": "5m"
        }

        # Log this detection for AI training
        log_detection(symbol=symbol,
                      pattern=pattern_name,
                      confidence=confidence,
                      price=last_price)

        if "CONSOLE" in TXConfig.ALERT_TYPES:
            print(f"""
    🚨 ALERT: {symbol} {pattern_name} ({confidence:.0%})
    Price: ${last_price:,.2f} | Time: {timestamp}
    ---""")

        if confidence < TXConfig.ALERT_CONFIDENCE_THRESHOLD:
            return


@app.route('/api/paper-trades', methods=['GET'])
def get_paper_trades():
    return jsonify({"paper_trades": app_state["paper_trades"]})


@app.route('/api/paper-trades', methods=['POST'])
def place_paper_trade():
    try:
        data = request.json or {}
        symbol = data.get('symbol')
        side = (data.get('side') or '').lower()  # 'buy' or 'sell'
        price = float(
            data.get('price')) if data.get('price') is not None else None
        pattern = data.get('pattern', 'Manual')
        confidence = float(data.get('confidence', 1.0))
        qty = data.get('qty')  # optional
        amount_usd = data.get('amount_usd')  # optional

        if not all([symbol, side, price is not None]):
            return jsonify({
                "status":
                "error",
                "message":
                "Missing required fields (symbol, side, price)"
            }), 400

        if not engine.trader:
            return jsonify({
                "status": "error",
                "message": "Paper trading disabled"
            }), 400

        if side == 'buy':
            # allow qty or amount_usd
            if qty is not None:
                qty = float(qty)
                trade = engine.trader.buy(symbol,
                                          price,
                                          pattern,
                                          confidence,
                                          qty=qty)
            elif amount_usd is not None:
                amount_usd = float(amount_usd)
                trade = engine.trader.buy(symbol,
                                          price,
                                          pattern,
                                          confidence,
                                          amount_usd=amount_usd)
            else:
                # default to default_qty inside PaperTrader
                trade = engine.trader.buy(symbol, price, pattern, confidence)
        elif side == 'sell':
            # optional qty for partial sells
            if qty is not None:
                qty = float(qty)
                trade = engine.trader.sell(symbol,
                                           price,
                                           qty=qty,
                                           reason="manual")
            else:
                trade = engine.trader.sell(symbol, price, reason="manual")
        else:
            return jsonify({
                "status": "error",
                "message": "Invalid trade side"
            }), 400

        if isinstance(trade, dict) and trade.get("error"):
            return jsonify({
                "status": "error",
                "message": trade.get("message")
            }), 400

        trade["time"] = datetime.now().strftime('%H:%M:%S')
        app_state["paper_trades"].insert(0, trade)
        return jsonify({"status": "success", "trade": trade})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/close-position', methods=['POST'])
def close_position():
    try:
        data = request.json
        symbol = data.get('symbol')
        price = float(data.get('price'))

        if not all([symbol, price]):
            return jsonify({
                "status": "error",
                "message": "Missing symbol or price"
            }), 400

        if not engine.trader:
            return jsonify({
                "status": "error",
                "message": "Paper trading disabled"
            }), 400

        closed_trade = engine.trader.sell(symbol, price, reason="manual")
        if not closed_trade:
            return jsonify({
                "status": "error",
                "message": "No open position for symbol"
            }), 404

        closed_trade["time"] = datetime.now().strftime('%H:%M:%S')
        app_state["paper_trades"].insert(0, closed_trade)
        return jsonify({"status": "success", "trade": closed_trade})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


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
            cache_time = datetime.strptime(data["timestamp"],
                                           '%Y-%m-%d %H:%M:%S')
            if datetime.now() - cache_time < timedelta(
                    seconds=TXConfig.CACHE_DURATION):
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
        threading.Thread(target=self.router.start_alpha_vantage_loop,
                         daemon=True).start()

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

                # Auto SELL logic
                if TXConfig.ENABLE_PAPER_TRADING and self.trader:
                    sell_trade = self.trader.check_auto_sell(
                        symbol, last_price)
                    if sell_trade:
                        sell_trade["time"] = scan_time
                        app_state["paper_trades"].insert(0, sell_trade)

                result = detect_all_patterns(candles)
                best_pattern = None
                for r in result:
                    if (r["confidence"] >= TXConfig.ALERT_CONFIDENCE_THRESHOLD
                            and r["name"] in TXConfig.PATTERN_WATCHLIST):
                        if not best_pattern or r["confidence"] > best_pattern[
                                "confidence"]:
                            best_pattern = r

                if best_pattern:
                    alert_key = f"{symbol}_{best_pattern['name']}"
                    current_time = time.time()
                    if (alert_key not in self.recent_alerts or
                        (current_time - self.recent_alerts[alert_key]) > 300):
                        AlertSystem.trigger_alert(symbol, best_pattern,
                                                  last_price)
                        self.recent_alerts[alert_key] = current_time

                    scan_results.append({
                        "symbol": symbol,
                        "status": "pattern",
                        "pattern": best_pattern["name"],
                        "confidence": f"{best_pattern['confidence']:.0%}",
                        "price": f"${last_price:,.2f}"
                    })

                    # Buy logic
                    if TXConfig.ENABLE_PAPER_TRADING and self.trader:
                        trade = self.trader.buy(symbol, last_price,
                                                best_pattern["name"],
                                                best_pattern["confidence"])
                        trade["time"] = scan_time
                        app_state["paper_trades"].insert(0, trade)

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

        def consolidate_asset_status(scan_results):
            """Consolidate asset patterns and IDLE statuses."""
            consolidated = {}
            for result in scan_results:
                symbol = result["symbol"]
                if symbol not in consolidated:
                    consolidated[symbol] = result
                else:
                    # Prefer detected patterns over idle, based on confidence
                    if result["status"] == "pattern" and consolidated[symbol][
                            "status"] != "pattern":
                        consolidated[symbol] = result

            return list(consolidated.values())

        def run_scan(self):
            self.scan_id += 1
            scan_time = datetime.now().strftime('%H:%M:%S')
            scan_results = []

            # Your existing logic to populate scan_results...

            # Consolidate scan results before updating app_state
            scan_results = consolidate_asset_status(scan_results)

            app_state["last_scan"] = {
                "id": self.scan_id,
                "time": scan_time,
                "results": scan_results
            }

            return scan_results

        app_state["last_scan"] = {
            "id": self.scan_id,
            "time": scan_time,
            "results": scan_results
        }

        return scan_results


# ====================== FLASK SERVER ======================
app = Flask(__name__)


@app.route('/')
def dashboard():
    visitor_id = track_visit(request)
    response = make_response(
        render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>TX PREDICTIVE INTELLIGENCE - Your Trading Co-Pilot</title>
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
                <div class="tx-header">
                    <div class="tx-logo">TX PREDICTIVE INTELLIGENCE</div>
                    <div class="tx-tagline">AI-Powered Market Anticipation System | Kampala, Uganda</div>
                </div>

                <div class="asset-grid">
                    {% for r in scan.results %}
                    <div class="asset-row">
                        <span class="asset-name">{{ r.symbol }}</span>
                        <span class="asset-price">{{ r.price if r.price else 'N/A' }}</span>
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

                <div style="margin-top: 20px; color: #666;">
                    Next scan in: <span id="countdown">{{ refresh_seconds }}</span>s
                </div>

                {% if last_signal %}
                <div style="background: #0d1a26; padding: 10px; border-radius: 4px; margin: 20px 0;">
                    <div style="color: var(--tx-green); font-weight: bold;">🚨 Latest Signal</div>
                    <div>{{ last_signal.symbol }} {{ last_signal.timeframe }}: {{ last_signal.pattern }} ({{ last_signal.confidence }})</div>
                    <div style="font-size: 12px; color: #777;">{{ last_signal.time }}</div>
                </div>
                {% endif %}

                <div style="margin-top: 15px; display: flex; gap: 10px;">
                    <button onclick="logOutcome('win')" 
                            style="background: var(--tx-green); border: none; padding: 5px 10px; border-radius: 4px;">
                        ✅ Trade Won
                    </button>
                    <button onclick="logOutcome('loss')" 
                            style="background: var(--tx-red); border: none; padding: 5px 10px; border-radius: 4px;">
                        ❌ Trade Lost
                    </button>
                </div>

                <script>
                function logOutcome(outcome) {
                    // Get the latest detection ID from the most recent detection
                    fetch('/api/get_latest_detection_id')
                        .then(response => response.json())
                        .then(data => {
                            if (data.detection_id) {
                                return fetch('/api/log_outcome', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                    },
                                    body: JSON.stringify({
                                        detection_id: data.detection_id,
                                        outcome: outcome
                                    })
                                });
                            } else {
                                throw new Error('No recent detection found');
                            }
                        })
                        .then(response => {
                            if (response.ok) {
                                alert('Outcome logged! Thank you.');
                            } else {
                                alert('Failed to log outcome.');
                            }
                        })
                        .catch(error => {
                            alert('No recent detection to log outcome for.');
                        });
                }
                </script>
                <div style="margin: 15px 0; font-size: 12px; color: #555;">
                    ⚡ <strong>{{ user_count }} traders</strong> live
                </div>

                <!-- TX Alert Interface -->
                <div id="alertInterface" style="background: #1a0a0a; border: 2px solid var(--tx-red); padding: 15px; border-radius: 8px; margin: 20px 0; display: none;">
                    <div style="color: var(--tx-red); font-weight: bold; font-size: 18px;">🚨 TX ALERT ACTIVATED</div>
                    <div id="alertMessage" style="margin: 10px 0; color: white;"></div>
                    <div style="display: flex; gap: 10px; margin: 15px 0;">
                        <button onclick="handleAlert('IGNORE')" style="background: #666; border: none; padding: 8px 12px; border-radius: 4px; color: white;">😴 Ignore</button>
                        <button onclick="handleAlert('SIMULATE')" style="background: #0066ff; border: none; padding: 8px 12px; border-radius: 4px; color: white;">📊 Simulate</button>
                        <button onclick="handleAlert('EXECUTE')" style="background: var(--tx-green); border: none; padding: 8px 12px; border-radius: 4px; color: white;">⚡ Execute</button>
                        <button onclick="handleAlert('SNOOZE')" style="background: #ff9900; border: none; padding: 8px 12px; border-radius: 4px; color: white;">⏰ Snooze 5m</button>
                    </div>
                    <div style="font-size: 12px; color: #aaa;">Suggested amounts: $100 | $250 | $500 | $1000</div>
                </div>

                <!-- TX Personality Section -->
                <div style="background: var(--tx-gray); padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid var(--tx-green);">
                    <div style="color: var(--tx-green); font-weight: bold;">💭 TX Says:</div>
                    <div id="txPersonality" style="font-style: italic; color: #ccc;">
                        "Like that overprotective friend who won't let you make bad decisions... but for trading."
                    </div>
                </div>

                <div style="margin-top: 30px; background: #000; padding: 15px; border-radius: 4px;">
                    <h3 style="margin-top: 0; color: var(--tx-green);">🚀 TX PRO ACCESS</h3>
                    <p>Unlock the full "Jealous Ex" experience:</p>
                    <ul>
                        <li>🔔 Multi-device sound alerts (phone, tablet, desktop)</li>
                        <li>📱 Telegram/WhatsApp notifications</li>
                        <li>🎯 Strategy Builder (no-code)</li>
                        <li>📊 15+ assets including forex</li>
                        <li>🧠 AI sentiment overlay</li>
                        <li>📈 Performance analytics & journaling</li>
                    </ul>
                    <p><strong>$24.99/month flat rate</strong> | No profit sharing, pure SaaS</p>
                    <p>DM on IG @robert.manejk</p>
                </div>

                <div class="powered-by">
                    TX Engine v0.9 | Data: Alpha Vantage
                </div>
            </div>

            <script>
                let seconds = {{ refresh_seconds }};
                let alertSound = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAcBT2a2+/QfCsELYbR7/DPQAUF');

                function updateCountdown() {
                    document.getElementById('countdown').textContent = seconds;
                    seconds--;
                    if (seconds < 0) location.reload();
                }

                function checkForAlerts() {
                    fetch('/api/get_active_alerts')
                        .then(response => response.json())
                        .then(data => {
                            if (data.alerts && data.alerts.length > 0) {
                                showAlert(data.alerts[0]);
                            }
                        });
                }

                function showAlert(alert) {
                    // Play sound
                    alertSound.play().catch(e => console.log('Audio play failed'));

                    // Show alert interface
                    document.getElementById('alertInterface').style.display = 'block';
                    document.getElementById('alertMessage').innerHTML = 
                        `<strong>${alert.symbol}</strong>: ${alert.pattern} (${alert.confidence})<br>
                         Price: $${alert.price}<br>
                         <em>${alert.message}</em>`;
                         console.info("Informational message");

                    // Update TX personality
                    const personalities = [
                        "I told you to watch this one! 👀",
                        "See? I'm always watching your back.",
                        "This is why you need me... *sips tea*",
                        "Another pattern caught! You're welcome.",
                        "I'm like Velma but for your portfolio 🔍"
                    ];
                    document.getElementById('txPersonality').textContent = 
                        personalities[Math.floor(Math.random() * personalities.length)];
                }

                function handleAlert(action) {
                    // Hide alert interface
                    document.getElementById('alertInterface').style.display = 'none';

                    // Send response to server
                    fetch('/api/handle_alert_response', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({action: action})
                    });

                    // Update TX personality based on action
                    const responses = {
                        'IGNORE': "Fine, ignore me. I'll just be here... watching... 😒",
                        'SIMULATE': "Smart choice! Let's paper trade this first 📊",
                        'EXECUTE': "YOLO! I hope you know what you're doing 🚀",
                        'SNOOZE': "Okay, but I'll be back in 5 minutes. SET YOUR ALARM ⏰"
                    };
                    document.getElementById('txPersonality').textContent = responses[action];
                }

                // Check for alerts every 10 seconds
                setInterval(checkForAlerts, 10000);
                setInterval(updateCountdown, 1000);
            </script>
        </body>
        </html>
        ''',
                               scan=app_state.get("last_scan",
                                                  {"results": []}),
                               last_signal=app_state.get("last_signal"),
                               user_count=db['user_count'],
                               refresh_seconds=TXConfig.REFRESH_INTERVAL))
    response.set_cookie('visitor_id', visitor_id, max_age=60 * 60 * 24 * 30)
    response.set_cookie('personalization',
                        'GPT-4o enabled',
                        max_age=60 * 60 * 24 * 30)
    return response


@app.route('/api/scan')
def api_scan():
    portfolio = None
    if engine.trader:
        # Optionally pass market prices if you have them from last scan
        market_prices = {}
        if "last_scan" in app_state and "results" in app_state["last_scan"]:
            for result in app_state["last_scan"]["results"]:
                if "price" in result and result["price"].startswith("$"):
                    try:
                        market_prices[result["symbol"]] = float(
                            result["price"].replace("$", "").replace(",", ""))
                    except:
                        pass
        portfolio = engine.trader.get_portfolio_value(market_prices)

    return jsonify({"app_state": app_state, "portfolio": portfolio})


@app.after_request
def apply_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers[
        "Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


@app.route('/api/get_latest_detection_id')
def get_latest_detection_id():
    try:
        detections = db.get('detections', [])
        if detections:
            # Get the most recent detection
            latest_detection = detections[-1]
            return jsonify({"detection_id": latest_detection['id']})
        else:
            return jsonify({"error": "No detections found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/log_outcome', methods=['POST'])
def log_outcome():
    try:
        data = request.json
        outcome = data.get('outcome')
        detection_id = data.get('detection_id')

        if not outcome or not detection_id:
            return jsonify({
                "status": "error",
                "message": "Missing outcome or detection_id"
            }), 400

        # Find the detection in the database
        for idx, detection in enumerate(db.get('detections', [])):
            if detection['id'] == detection_id:
                db['detections'][idx]['outcome'] = outcome
                db['detections'][idx]['verified'] = True
                return jsonify({"status": "success"})

        return jsonify({"status": "detection_not_found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    try:
        if not engine.trader:
            return jsonify({
                "status": "error",
                "message": "Paper trading disabled"
            }), 400

        # Optionally fetch live prices for unrealized PnL
        market_prices = {}
        for symbol in TXConfig.ASSET_TYPES.keys():
            candles = DataCache.get_cached(symbol)
            if candles:
                market_prices[symbol] = candles[-1]["close"]

        portfolio_data = engine.trader.get_portfolio_value(market_prices)
        return jsonify({"status": "success", "portfolio": portfolio_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/get_active_alerts')
def get_active_alerts():
    """Get currently active alerts"""
    return jsonify({"alerts": app_state["alerts"]})


@app.route('/api/handle_alert_response', methods=['POST'])
def handle_alert_response():
    """Handle user response to alerts"""
    data = request.get_json()
    action = data.get('action', 'IGNORE')

    # Just log the response
    print(f"User responded to alert with: {action}")
    return jsonify({"status": "recorded", "action": action})


# ====================== DATA BACKUP SYSTEM ======================
def backup_to_github():
    """Automatically exports data to GitHub"""
    try:
        print("⏳ Starting GitHub backup...")
        export = {
            'timestamp': datetime.now().isoformat(),
            'data': {
                'visitors': dict(db['visitors']),
                'detections': list(db['detections'])
            }
        }

        with open('tx_backup.json', 'w') as f:
            json.dump(export, f, indent=2)

        # Configure git (only needs to run once)
        if not os.path.exists('.git/config'):
            os.system('git init')
            os.system(
                'git remote add origin ' +
                f'https://{os.getenv("TOKEN")}@github.com/MMCCXXIIax/tx-backups.git'
            )

        # Push to GitHub
        os.system('git config --global user.name "TX-AutoBackup"')
        os.system('git config --global user.email "backup@tx.com"')
        os.system('git add tx_backup.json')
        os.system('git commit -m "Auto backup"')
        os.system('git push origin main')

        print("✅ Backup completed!")
    except Exception as e:
        print(f"⚠️ Backup failed: {str(e)}")

    import requests

    @app.route('/api/submit-feedback', methods=['POST'])
    def submit_feedback():
        try:
            data = request.json
            feedback = data.get('feedback')
            account_details = data.get('account_details', 'Anonymous')

            # Send feedback to Slack or any other service
            # Slack webhook example:
            slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
            if slack_webhook_url:
                message = {
                    "text": f"New Feedback from {account_details}:\n{feedback}"
                }
                response = requests.post(slack_webhook_url, json=message)

                if response.status_code == 200:
                    return jsonify(
                        {"message": "Feedback submitted successfully!"})
                else:
                    return jsonify({"message":
                                    "Failed to forward feedback."}), 500
            else:
                return jsonify(
                    {"message": "Slack webhook URL not configured."}), 500

        except Exception as e:
            return jsonify({"message": str(e)}), 500989


#====================== MAIN ======================
# ... (keep all your existing imports and code until the if __name__ == "__main__" block)

# ====================== MAIN ===================
# ====================== MAIN ======================
if __name__ == "__main__":
    # Initialize engine
    engine = TXEngine()
    engine.run_scan()

    @app.before_request
    def before_request():
        if request.path != '/health':
            print(f"Incoming request: {request.method} {request.path}")

    # Start background scanner
    def scan_loop():
        while True:
            time.sleep(TXConfig.REFRESH_INTERVAL)
            engine.run_scan()

    threading.Thread(target=scan_loop, daemon=True).start()

    # Replit-specific setup
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)), debug=True)









git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"

git init

git remote add origin https://YOUR_GITHUB_USERNAME:GITHUB_TOKEN@github.com/YOUR_GITHUB_USERNAME/REPO_NAME.git

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




git remote add origin https://YOUR_GITHUB_USERNAME:GITHUB_TOKEN@github.com/YOUR_GITHUB_USERNAME/REPO_NAME.git
git add .

git commit -m "Initial commit"

    git push origin main

https://github.com/MMCCXXIIax/tx-predictive-intelligence.git


    git remote remove origin