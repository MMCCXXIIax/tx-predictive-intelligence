#https://github.com/MMCCXXIIax/tx-copilot-bot.git

# main.py
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
            db['visitors'][visitor_id]['last_seen'] = datetime.now().isoformat()
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
    REFRESH_INTERVAL = 180
    CANDLE_LIMIT = 100
    ALERT_CONFIDENCE_THRESHOLD = 0.85
    ALERT_TYPES = ["CONSOLE", "WEB"]

    CACHE_FILE = "tx_cache.json"
    CACHE_DURATION = 180

    PATTERN_WATCHLIST = [
        "Bullish Engulfing",
        "Bearish Engulfing",
        "Morning Star",
        "Evening Star",
        "Three White Soldiers",
        "Three Black Crows",
        "Hammer",
        "Inverted Hammer", 
        "Shooting Star"
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
            "explanation": detection.get("explanation", "No explanation available"),
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
        log_detection(
            symbol=symbol,
            pattern=pattern_name,
            confidence=confidence,
            price=last_price
        )

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

                # Auto SELL logic
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

                    # Buy logic
                    if TXConfig.ENABLE_PAPER_TRADING and self.trader:
                        trade = self.trader.buy(
                            symbol,
                            last_price,
                            best_pattern["name"],
                            best_pattern["confidence"]
                        )
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
    response = make_response(render_template_string(
        '''
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
        scan=app_state.get("last_scan", {"results": []}),
        last_signal=app_state.get("last_signal"),
        user_count=db['user_count'],
        refresh_seconds=TXConfig.REFRESH_INTERVAL
    ))
    response.set_cookie('visitor_id', visitor_id, max_age=60*60*24*30)
    response.set_cookie('personalization', 'GPT-4o enabled', max_age=60*60*24*30)
    return response

@app.route('/api/scan')
def api_scan():
    return jsonify(app_state)

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
            return jsonify({"status": "error", "message": "Missing outcome or detection_id"}), 400

        # Find the detection in the database
        for idx, detection in enumerate(db.get('detections', [])):
            if detection['id'] == detection_id:
                db['detections'][idx]['outcome'] = outcome
                db['detections'][idx]['verified'] = True
                return jsonify({"status": "success"})

        return jsonify({"status": "detection_not_found"}), 404
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
            os.system('git remote add origin ' +
                     f'https://{os.getenv("TOKEN")}@github.com/MMCCXXIIax/tx-backups.git')

        # Push to GitHub
        os.system('git config --global user.name "TX-AutoBackup"')
        os.system('git config --global user.email "backup@tx.com"')
        os.system('git add tx_backup.json')
        os.system('git commit -m "Auto backup"')
        os.system('git push origin main')

        print("✅ Backup completed!")
    except Exception as e:
        print(f"⚠️ Backup failed: {str(e)}")

# ====================== MAIN ======================
if __name__ == "__main__":
    engine = TXEngine()
    engine.run_scan()

    def scan_scheduler():
        while True:
            time.sleep(TXConfig.REFRESH_INTERVAL)
            engine.run_scan()

    threading.Thread(target=scan_scheduler, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    print(f"✅ TX Copilot running on port {port}")
    app.run(host="0.0.0.0", port=port)