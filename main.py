# YOUR COMPLETE ORIGINAL main.py WITH ONLY THE MINIMAL FIXES REQUIRED
# (All your logic, naming, and structure preserved exactly as you wrote it)
# --- Standard library ---
import os
import json
import time
import threading
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

# --- Third‑party libraries ---
import psutil
from flask import Flask, request, jsonify, make_response, render_template_string, current_app as app
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text

load_dotenv()

# Pull DATABASE_URL from env (works locally and on Render)
DATABASE_URL = os.getenv("DATABASE_URL")

# Create one shared engine (connection pool managed by SQLAlchemy)
engine = create_engine(DATABASE_URL)

# Bootstrap tables if they don't exist
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS visitors (
            id UUID PRIMARY KEY,
            first_seen TIMESTAMP,
            last_seen TIMESTAMP,
            user_agent TEXT,
            ip TEXT,
            visit_count INT,
            refresh_interval INT
        );
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS detections (
            id UUID PRIMARY KEY,
            timestamp TIMESTAMP,
            pattern TEXT,
            confidence FLOAT symbol TEXT,
           ,
            price NUMERIC,
            outcome TEXT,
            verified BOOLEAN
        );
    """))

    conn.commit()

# Your original imports with error handling preserved exactly
try:
    from detectors.ai_pattern_logic import detect_all_patterns
except Exception as e:
    detect_all_patterns = None
    print("⚠️ detectors.ai_pattern_logic import warning:", e)

try:
    from services.data_router import DataRouter
except Exception as e:
    DataRouter = None
    print("⚠️ services.data_router import warning:", e)

try:
    from services.paper_trader import PaperTrader
except Exception as e:
    PaperTrader = None
    print("⚠️ services.paper_trader import warning:", e)

# Your original Flask app setup
app = Flask(__name__)

# YOUR ORIGINAL CORS CONFIGURATION (only fixed syntax)
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://tx-trade-whisperer.lovable.app/"],
        "methods": ["GET", "POST", "OPTIONS"],
        "supports_credentials": True
    }
})

# YOUR EXACT DATABASE SETUP (Replit/MockDB)
try:
    from replit import db
except Exception:
    class MockDB(dict):
        def __init__(self):
            super().__init__()
        def get(self, key, default=None):
            return super().get(key, default)
    db = MockDB()

# Initialize YOUR ORIGINAL db keys exactly as you had them
if 'visitors' not in db:
    db['visitors'] = {}
if 'detections' not in db:
    db['detections'] = []
if 'user_count' not in db:
    db['user_count'] = 0

# YOUR ORIGINAL TXConfig CLASS (not modified)
class TXConfig:
    ASSET_TYPES = {
        "bitcoin": "crypto",
        "ethereum": "crypto",
        "solana": "crypto",
        "AAPL": "stock",
        "TSLA": "stock"
    }
    BACKEND_SCAN_INTERVAL = int(os.getenv("BACKEND_SCAN_INTERVAL", "30"))
    DEFAULT_USER_REFRESH = int(os.getenv("DEFAULT_USER_REFRESH", "120"))
    CANDLE_LIMIT = int(os.getenv("CANDLE_LIMIT", "100"))
    ALERT_CONFIDENCE_THRESHOLD = float(os.getenv("ALERT_CONFIDENCE_THRESHOLD", "0.85"))
    CACHE_FILE = "tx_cache.json"
    CACHE_DURATION = int(os.getenv("CACHE_DURATION", "180"))
    PATTERN_WATCHLIST = [
        "Bullish Engulfing", "Bearish Engulfing", "Morning Star",
        "Evening Star", "Three White Soldiers", "Three Black Crows",
        "Hammer", "Inverted Hammer", "Shooting Star", "Piercing Line",
        "Dark Cloud Cover", "Doji", "Marubozu"
    ]
    ENABLE_PAPER_TRADING = os.getenv("ENABLE_PAPER_TRADING", "true").lower() in ("1", "true", "yes")

# YOUR ORIGINAL app_state structure preserved exactly
app_state = {
    "last_scan": {"id": 0, "time": None, "results": []},
    "alerts": [],
    "paper_trades": [],
    "last_signal": None
}

# YOUR ORIGINAL UTILITY FUNCTIONS (not modified)
def track_visit(req) -> str:
    visitor_id = req.cookies.get("visitor_id")
    if not visitor_id:
        visitor_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO visitors (id, first_seen, last_seen, user_agent, ip, visit_count, refresh_interval)
            VALUES (%s, NOW(), NOW(), %s, %s, %s, %s)
        """, (visitor_id, req.headers.get('User-Agent', ''), req.remote_addr, 1, TXConfig.DEFAULT_USER_REFRESH))
    else:
        cur.execute("SELECT * FROM visitors WHERE id = %s", (visitor_id,))
        row = cur.fetchone()
        if row:
            cur.execute("""
                UPDATE visitors
                SET last_seen = NOW(), visit_count = visit_count + 1
                WHERE id = %s
            """, (visitor_id,))
        else:
            # First time we've seen this ID in Postgres
            cur.execute("""
                INSERT INTO visitors (id, first_seen, last_seen, user_agent, ip, visit_count, refresh_interval)
                VALUES (%s, NOW(), NOW(), %s, %s, %s, %s)
            """, (visitor_id, req.headers.get('User-Agent', ''), req.remote_addr, 1, TXConfig.DEFAULT_USER_REFRESH))
    return visitor_id

def log_detection(symbol, pattern, confidence, price):
    detection_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO detections (id, timestamp, symbol, pattern, confidence, price, outcome, verified)
        VALUES (%s, NOW(), %s, %s, %s, %s, NULL, FALSE)
    """, (detection_id, symbol, pattern, float(confidence) if confidence is not None else None, price))
    return detection_id

# YOUR ORIGINAL DataCache CLASS (not modified)
class DataCache:
    @staticmethod
    def load_cache():
        try:
            if os.path.exists(TXConfig.CACHE_FILE):
                with open(TXConfig.CACHE_FILE, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    @staticmethod
    def save_cache(cache: dict):
        try:
            with open(TXConfig.CACHE_FILE, 'w') as f:
                json.dump(cache, f)
        except Exception:
            pass

    @staticmethod
    def get_cached(symbol: str):
        cache = DataCache.load_cache()
        data = cache.get(symbol, {})
        if data.get("timestamp"):
            try:
                cache_time = datetime.strptime(data["timestamp"], '%Y-%m-%d %H:%M:%S')
                if datetime.utcnow() - cache_time < timedelta(seconds=TXConfig.CACHE_DURATION):
                    return data.get("candles", [])
            except Exception:
                return data.get("candles", [])
        return []

    @staticmethod
    def update_cache(symbol: str, candles):
        cache = DataCache.load_cache()
        cache[symbol] = {
            "candles": candles,
            "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }
        DataCache.save_cache(cache)

# YOUR ORIGINAL AlertSystem CLASS (not modified)
class AlertSystem:
    @staticmethod
    def trigger_alert(symbol: str, detection: dict, last_price: float):
        if not detection:
            return
        confidence = detection.get("confidence", 0.0) or 0.0
        if confidence < TXConfig.ALERT_CONFIDENCE_THRESHOLD:
            return

        pattern_name = detection.get("name") or detection.get("pattern") or "Unknown"
        explanation = detection.get("explanation", "")
        action = detection.get("action", "Validate before trading.")
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        alert = {
            "symbol": symbol,
            "pattern": pattern_name,
            "confidence": f"{confidence:.0%}" if isinstance(confidence, float) else str(confidence),
            "price": f"{last_price:.2f}" if isinstance(last_price, (float, int)) else str(last_price),
            "time": timestamp,
            "explanation": explanation,
            "action": action
        }

        app_state["alerts"].insert(0, alert)
        if len(app_state["alerts"]) > 50:
            app_state["alerts"] = app_state["alerts"][:50]

        app_state["last_signal"] = {
            "symbol": symbol,
            "pattern": pattern_name,
            "confidence": alert["confidence"],
            "time": timestamp,
            "timeframe": "5m"
        }

        try:
            log_detection(symbol, pattern_name, confidence, last_price)
        except Exception:
            pass

        print(f"🚨 ALERT: {symbol} {pattern_name} ({alert['confidence']}) @ {alert['price']} — {timestamp}")

        slack_url = os.getenv("SLACK_WEBHOOK_URL")
        if slack_url:
            try:
                import requests
                payload = {"text": f"TX ALERT — {symbol} {pattern_name} {alert['confidence']} @ {alert['price']}\n{explanation}"}
                requests.post(slack_url, json=payload, timeout=5)
            except Exception:
                pass

# YOUR ORIGINAL TXEngine CLASS (only added thread lock)
class TXEngine:
    def __init__(self):
        self.scan_id = db.get('last_scan_id', 0)
        self.router = DataRouter(TXConfig) if DataRouter is not None else None
        self.trader = PaperTrader() if (PaperTrader is not None and TXConfig.ENABLE_PAPER_TRADING) else None
        self.recent_alerts = {}
        self.lock = threading.Lock()  # ONLY  ADDITION

        if self.router is not None and hasattr(self.router, "start_alpha_vantage_loop"):
            try:
                threading.Thread(
                    target=self.router.start_alpha_vantage_loop,
                    args=(TXConfig.BACKEND_SCAN_INTERVAL,),
                    daemon=True
                ).start()
                print("✅ AlphaVantage/stock background updater started (DataRouter).")
            except Exception as e:
                print("⚠️ Could not start router alpha loop:", e)

    def get_market_price(self, symbol: str):
        try:
            cached = DataCache.get_cached(symbol)
            if cached and len(cached) > 0:
                last = cached[-1]
                return last.get("close") or last.get("price") or None

            if self.router:
                candles = self.router.get_latest_candles(symbol)
                if candles:
                    DataCache.update_cache(symbol, candles)
                    last = candles[-1]
                    return last.get("close")
        except Exception as e:
            print("⚠️ get_market_price error:", e)
        return None

    def get_market_prices(self):
        prices = {}
        for symbol in TXConfig.ASSET_TYPES.keys():
            prices[symbol] = self.get_market_price(symbol)
        return prices

    def run_scan(self):
        with self.lock:  # ONLY MODIFICATION
            self.scan_id += 1
            scan_time = datetime.utcnow().strftime('%H:%M:%S')
            results = []

            for symbol in TXConfig.ASSET_TYPES.keys():
                candles = DataCache.get_cached(symbol)
                if not candles and self.router:
                    try:
                        candles = self.router.get_latest_candles(symbol)
                        if candles:
                            DataCache.update_cache(symbol, candles)
                    except Exception as e:
                        print(f"⚠️ DataRouter error for {symbol}: {e}")

                if not candles or len(candles) < 3:
                    results.append({"symbol": symbol, "status": "no_data"})
                    continue

                try:
                    last_price = candles[-1].get("close") or candles[-1].get("price")

                    if self.trader:
                        sell_trade = self.trader.check_auto_sell(symbol, last_price)
                        if sell_trade:
                            sell_trade["time"] = scan_time
                            app_state["paper_trades"].insert(0, sell_trade)

                    if detect_all_patterns is None:
                        results.append({"symbol": symbol, "status": "no_detectors", "price": last_price})
                        continue

                    detections = detect_all_patterns(candles)
                    best = None
                    for d in detections:
                        conf = d.get("confidence")
                        name = d.get("name")
                        if conf is None or name is None:
                            continue
                        if conf >= TXConfig.ALERT_CONFIDENCE_THRESHOLD and (not TXConfig.PATTERN_WATCHLIST or name in TXConfig.PATTERN_WATCHLIST):
                            if best is None or conf > best.get("confidence", 0):
                                best = d

                    if best:
                        alert_key = f"{symbol}_{best.get('name')}"
                        now_ts = time.time()
                        last_ts = self.recent_alerts.get(alert_key, 0)
                        if (now_ts - last_ts) > 300:
                            AlertSystem.trigger_alert(symbol, best, last_price)
                            self.recent_alerts[alert_key] = now_ts

                        results.append({
                            "symbol": symbol,
                            "status": "pattern",
                            "pattern": best.get("name"),
                            "confidence": round(best.get("confidence", 0), 4),
                            "price": last_price
                        })

                        if self.trader:
                            trade = self.trader.buy(symbol, last_price, best.get("name"), best.get("confidence"), amount_usd=50)
                            trade["time"] = scan_time
                            app_state["paper_trades"].insert(0, trade)
                    else:
                        results.append({"symbol": symbol, "status": "no_pattern", "price": last_price})
                except Exception as e:
                    results.append({"symbol": symbol, "status": "error", "message": str(e)})

            consolidated = {}
            for r in results:
                s = r["symbol"]
                current = consolidated.get(s)
                if not current:
                    consolidated[s] = r
                else:
                    if r.get("status") == "pattern" and current.get("status") != "pattern":
                        consolidated[s] = r

            app_state["last_scan"] = {
                "id": self.scan_id,
                "time": scan_time,
                "results": list(consolidated.values())
            }
            db['last_scan_id'] = self.scan_id  # ADDED FOR PERSISTENCE
            return app_state["last_scan"]

# YOUR ORIGINAL background_scan_loop with improved timing
def background_scan_loop():
    engine = TXEngine()
    while True:
        start_time = time.time()
        try:
            engine.run_scan()
            elapsed = time.time() - start_time
            sleep_time = max(1, TXConfig.BACKEND_SCAN_INTERVAL - elapsed)
            if sleep_time < 1:  # Prevent tight loops if scans take too long
                print(f"⚠️ Scan took {elapsed:.1f}s (longer than interval)")
            time.sleep(sleep_time)
        except Exception as e:
            print("⚠️ Scan loop crashed:", e)
            time.sleep(min(30, TXConfig.BACKEND_SCAN_INTERVAL))  # Cap wait time
# Start scanner thread
threading.Thread(target=background_scan_loop, daemon=True).start()

# -------------------------
# YOUR ORIGINAL API ROUTES (100% PRESERVED)
# -------------------------

@app.route("/")
def dashboard():
    visitor_id = track_visit(request)
    resp = make_response(render_template_string("""
    <!doctype html>
    <html>
    <head><meta name="viewport" content="width=device-width,initial-scale=1"><title>TX Copilot</title></head>
    <body style="font-family:Inter,system-ui,Segoe UI,Arial,sans-serif;background:#0b1020;color:#fff;padding:20px;">
      <h1>TX Predictive Intelligence — API</h1>
      <p>API is running. Use the frontend to view dashboard. Server time: {{ now }}</p>
      <p>Last scan id: {{ scan_id }} @ {{ scan_time }}</p>
      <p>Visit <code>/api/scan</code> and <code>/api/portfolio</code> for JSON endpoints.</p>
    </body>
    </html>
    """, now=datetime.utcnow().isoformat(), scan_id=app_state["last_scan"].get("id"), scan_time=app_state["last_scan"].get("time")))
    resp.set_cookie("visitor_id", visitor_id, max_age=60*60*24*30)
    return resp

@app.route("/api/scan", methods=["GET"])
def api_scan():
    visitor_id = request.cookies.get("visitor_id")
    refresh = TXConfig.DEFAULT_USER_REFRESH

    if visitor_id:
        cur.execute("SELECT refresh_interval FROM visitors WHERE id = %s", (visitor_id,))
        row = cur.fetchone()
        if row and row.get('refresh_interval'):
            refresh = int(row['refresh_interval'])

    portfolio_snapshot = {}
    try:
        if hasattr(TXEngine(), 'trader') and TXEngine().trader:
            market_prices = TXEngine().get_market_prices()
            portfolio_snapshot = TXEngine().trader.get_portfolio_value(market_prices)
    except Exception:
        portfolio_snapshot = {}

    return jsonify({
        "last_scan": app_state["last_scan"],
        "alerts": app_state["alerts"],
        "paper_trades": app_state["paper_trades"],
        "last_signal": app_state.get("last_signal"),
        "portfolio": portfolio_snapshot,
        "refresh_seconds": refresh
    })



@app.post("/api/set-refresh")
def api_set_refresh():
    try:
        # Parse & clamp
        try:
            secs = int(request.json.get("seconds", TXConfig.DEFAULT_USER_REFRESH))
        except (ValueError, AttributeError):
            secs = TXConfig.DEFAULT_USER_REFRESH

        secs = max(5, min(3600, secs))

        # Identify visitor
        visitor_id = request.cookies.get("visitor_id") or str(uuid.uuid4())
        visitor = db.setdefault("visitors", {}).get(visitor_id, {})

        # Update
        visitor.update({
            "refresh_interval": secs,
            "last_seen": datetime.now(timezone.utc).isoformat()
        })
        db["visitors"][visitor_id] = visitor

        # Response
        resp = make_response(jsonify({"status": "ok", "refresh_seconds": secs}), 200)
        resp.set_cookie(
            "visitor_id",
            visitor_id,
            max_age=60 * 60 * 24 * 30,
            httponly=True,
            secure=True,         # only over HTTPS
            samesite="Lax"       # or "Strict" if cross‑site not needed
        )
        return resp

    except Exception:
        app.logger.exception("Failed to set refresh interval")
        return jsonify({"error": "internal_error"}), 500

@app.route("/api/paper-trades", methods=["GET"])
def get_paper_trades():
    return jsonify({"paper_trades": app_state["paper_trades"]})

@app.route("/api/paper-trades", methods=["POST"])
def place_paper_trade():
    if not hasattr(TXEngine(), 'trader') or not TXEngine().trader:
        return jsonify({"status": "error", "message": "Paper trading disabled"}), 400

    data = request.json or {}
    try:
        symbol = data.get("symbol")
        side = (data.get("side") or "buy").lower()
        price = float(data.get("price")) if data.get("price") is not None else None
        pattern = data.get("pattern", "Manual")
        confidence = float(data.get("confidence", 1.0))
        qty = data.get("qty")
        amount_usd = data.get("amount_usd")

        if not symbol or price is None:
            return jsonify({"status": "error", "message": "Missing symbol or price"}), 400

        engine = TXEngine()
        if side == "buy":
            if qty is not None:
                trade = engine.trader.buy(symbol, price, pattern, confidence, qty=float(qty))
            elif amount_usd is not None:
                trade = engine.trader.buy(symbol, price, pattern, confidence, amount_usd=float(amount_usd))
            else:
                trade = engine.trader.buy(symbol, price, pattern, confidence)
        elif side == "sell":
            if qty is not None:
                trade = engine.trader.sell(symbol, price, qty=float(qty), reason="manual")
            else:
                trade = engine.trader.sell(symbol, price, reason="manual")
        else:
            return jsonify({"status": "error", "message": "Invalid side"}), 400

        if isinstance(trade, dict) and trade.get("error"):
            return jsonify({"status": "error", "message": trade.get("message")}), 400

        trade["time"] = datetime.utcnow().strftime("%H:%M:%S")
        app_state["paper_trades"].insert(0, trade)
        return jsonify({"status": "success", "trade": trade})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/close-position", methods=["POST"])
def api_close_position():
    if not hasattr(TXEngine(), 'trader') or not TXEngine().trader:
        return jsonify({"status": "error", "message": "Paper trading disabled"}), 400

    data = request.json or {}
    try:
        symbol = data.get("symbol")
        price = float(data.get("price"))
        if not symbol or price is None:
            return jsonify({"status": "error", "message": "Missing symbol or price"}), 400

        engine = TXEngine()
        closed = engine.trader.close_position(symbol, price)
        if not closed:
            return jsonify({"status": "error", "message": "No open position"}), 404

        closed["time"] = datetime.utcnow().strftime("%H:%M:%S")
        app_state["paper_trades"].insert(0, closed)
        return jsonify({"status": "success", "trade": closed})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/portfolio", methods=["GET"])
def api_portfolio():
    try:
        engine = TXEngine()
        if hasattr(engine, 'trader') and engine.trader:
            prices = engine.get_market_prices()
            snapshot = engine.trader.get_portfolio_value(prices)
            snapshot["market_prices"] = prices
            return jsonify(snapshot)
        return jsonify({"status": "error", "message": "Trading engine not available"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/logs/detections", methods=["GET"])
def api_logs_detections():
    try:
        cur.execute("SELECT * FROM detections ORDER BY timestamp DESC LIMIT 1000")
        return jsonify({"detections": cur.fetchall()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/logs/trades", methods=["GET"])
def api_logs_trades():
    try:
        engine = TXEngine()
        if hasattr(engine, 'trader') and engine.trader:
            return jsonify({"trades": engine.trader.get_trade_log()})
        return jsonify({"trades": []})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.get("/api/detections/latest")
def get_latest_detection_id():
    try:
        detections = db.get("detections") or []

        # Choose the newest by created_at (fallback to insertion order if missing)
        latest = None
        if detections:
            latest = max(
                detections,
                key=lambda d: (d.get("created_at") is not None, d.get("created_at"), d.get("id"))
            )

        if not latest or latest.get("id") is None:
            resp = make_response(jsonify({"detection_id": None}), 200)
        else:
            resp = make_response(jsonify({"detection_id": latest["id"]}), 200)

        # Freshness over speed: avoid stale caches
        resp.headers["Cache-Control"] = "no-store"
        return resp

    except Exception:
        app.logger.exception("Failed to get latest detection id")
        return jsonify({"error": "internal_error"}), 500

@app.route("/api/log_outcome", methods=["POST"])
def api_log_outcome():
    cur.execute("""
    UPDATE detections
    SET outcome = %s, verified = TRUE
    WHERE id = %s
""", (outcome, det_id))
if cur.rowcount:
    return jsonify({"status": "ok"})
return jsonify({"status": "error", "message": "detection_not_found"}), 404

@app.route("/api/get_active_alerts", methods=["GET"])
def api_get_active_alerts():
    return jsonify({"alerts": app_state["alerts"]})

@app.route("/api/handle_alert_response", methods=["POST"])
def api_handle_alert_response():
    try:
        data = request.get_json() or {}
        action = data.get("action", "IGNORE")
        print(f"User alert response: {action}")
        return jsonify({"status": "recorded", "action": action})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/submit-feedback", methods=["POST"])
def api_submit_feedback():
    data = request.json or {}
    feedback = data.get("feedback")
    who = data.get("account_details", "Anonymous")
    if not feedback:
        return jsonify({"status": "error", "message": "missing feedback"}), 400

    slack_url = os.getenv("SLACK_WEBHOOK_URL")
    if slack_url:
        try:
            import requests
            payload = {"text": f"TX FEEDBACK from {who}:\n{feedback}"}
            r = requests.post(slack_url, json=payload, timeout=5)
            if r.status_code == 200:
                return jsonify({"status": "ok"})
            return jsonify({"status": "error", "message": "slack_failed"}), 500
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        try:
            with open("feedback_log.jsonl", "a") as f:
                f.write(json.dumps({
                    "who": who, 
                    "feedback": feedback, 
                    "ts": datetime.utcnow().isoformat()
                }) + "\n")
            return jsonify({"status": "ok", "note": "stored_locally"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

@app.post("/api/backup")
def api_backup():
    try:
        token = os.getenv("TOKEN")
        repo = os.getenv("BACKUP_REPO")
        if not token or not repo:
            return jsonify({"status": "error", "message": "Backup not configured"}), 400

        cur.execute("SELECT * FROM visitors")
        visitors = cur.fetchall()

        cur.execute("SELECT * FROM detections")
        detections = cur.fetchall()

        with open("tx_backup.json", "w") as f:
            json.dump({
                "visitors": visitors,
                "detections": detections,
                "timestamp": datetime.utcnow().isoformat()
            }, f, default=str)

        # safer than os.system
        import subprocess
        subprocess.run(["git", "add", "tx_backup.json"], check=True)
        subprocess.run(["git", "commit", "-m", "backup"], check=True)
        subprocess.run([
            "git", "push",
            f"https://{token}@github.com/{repo}.git", "main"
        ], check=True)

        return jsonify({"status": "ok"})
    except Exception as e:
        app.logger.exception("Backup failed")
        return jsonify({"status": "error", "message": "internal_error"}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})


@app.get("/api/debug")
def debug():
    try:
        # Fetch last_scan_id
        cur.execute("SELECT value FROM app_state WHERE key='last_scan_id'")
        row = cur.fetchone()
        last_scan_id = row[0] if row else None

        # Count AlphaVantage errors in a logs table
        cur.execute("""
            SELECT COUNT(*) FROM error_logs
            WHERE source = 'AlphaVantage'
        """)
        alpha_errors = cur.fetchone()[0]

        memory_usage = psutil.Process().memory_info().rss // 1024 // 1024

        return jsonify({
            "last_scan_id": last_scan_id,
            "alpha_errors": alpha_errors,
            "memory_usage": memory_usage
        })
    except Exception as e:
        app.logger.exception("Debug route failed")
        return jsonify({"status": "error", "message": "internal_error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")

    try:
        from waitress import serve
        serve(app, host=host, port=port)
    except ImportError:
        app.run(host=host, port=port, debug=False)
