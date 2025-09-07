# --- Standard library ---
import os
import json
import subprocess
import time
import threading
import uuid
import traceback
from datetime import datetime, timedelta, timezone

# --- Third‑party libraries ---
import psutil
from flask import Flask, request, jsonify, make_response, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text, bindparam

# --- Local services ---
# Use the shared engine from services.db so it's consistent with profile_saver.py
from services.db import engine
from services.profile_saver import save_profile

# Optional imports with safety
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

# Supabase client (v2.x)
from supabase import create_client

load_dotenv()

# --- Flask app ---
app = Flask(__name__, static_folder="client/dist", static_url_path="")

# --- CORS (clean, explicit) ---
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://tx-tradingx.onrender.com",
            "https://tx-predictive-intelligence.onrender.com",
            "http://localhost:3000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "supports_credentials": True
    }
})

# --- Configuration ---
SAVE_PROFILE_MODE = os.getenv("SAVE_PROFILE_MODE", "db").lower()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

print(f"[config] Save Profile Mode: {SAVE_PROFILE_MODE}")

# --- TXConfig ---
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

# --- Bootstrap minimal tables if missing (visitors/app_state/detections) ---
with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS visitors (
            id UUID PRIMARY KEY,
            first_seen TIMESTAMP,
            last_seen TIMESTAMP,
            user_agent TEXT,
            ip TEXT,
            visit_count INT,
            refresh_interval INT,
            name TEXT,
            email TEXT,
            mode TEXT
        )
    """))
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS app_state (
            key TEXT PRIMARY KEY,
            value JSONB,
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS detections (
            id UUID PRIMARY KEY,
            timestamp TIMESTAMP,
            symbol TEXT,
            pattern TEXT,
            confidence FLOAT,
            price NUMERIC,
            outcome TEXT,
            verified BOOLEAN
        )
    """))

# --- In-memory state ---
app_state = {
    "last_scan": {"id": 0, "time": None, "results": []},
    "alerts": [],
    "paper_trades": [],
    "last_signal": None
}

# --- Helpers ---
def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

def track_visit(req) -> str:
    visitor_id = req.cookies.get("visitor_id")
    user_agent = req.headers.get("User-Agent", "")
    ip_addr = req.remote_addr
    refresh_interval = TXConfig.DEFAULT_USER_REFRESH

    with engine.begin() as conn:
        if not visitor_id:
            visitor_id = str(uuid.uuid4())
            conn.execute(
                text("""
                    INSERT INTO visitors (id, first_seen, last_seen, user_agent, ip, visit_count, refresh_interval)
                    VALUES (:id, NOW(), NOW(), :ua, :ip, :count, :refresh)
                    ON CONFLICT (id) DO NOTHING
                """),
                {"id": visitor_id, "ua": user_agent, "ip": ip_addr, "count": 1, "refresh": refresh_interval}
            )
        else:
            row = conn.execute(
                text("SELECT 1 FROM visitors WHERE id = :id"),
                {"id": visitor_id}
            ).fetchone()

            if row:
                conn.execute(
                    text("""
                        UPDATE visitors
                        SET last_seen = NOW(), visit_count = visit_count + 1
                        WHERE id = :id
                    """),
                    {"id": visitor_id}
                )
            else:
                conn.execute(
                    text("""
                        INSERT INTO visitors (id, first_seen, last_seen, user_agent, ip, visit_count, refresh_interval)
                        VALUES (:id, NOW(), NOW(), :ua, :ip, :count, :refresh)
                    """),
                    {"id": visitor_id, "ua": user_agent, "ip": ip_addr, "count": 1, "refresh": refresh_interval}
                )

    return visitor_id

def log_detection(symbol, pattern, confidence, price):
    detection_id = str(uuid.uuid4())
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO detections (id, timestamp, symbol, pattern, confidence, price, outcome, verified)
                VALUES (:id, NOW(), :symbol, :pattern, :confidence, :price, NULL, FALSE)
            """),
            {"id": detection_id, "symbol": symbol, "pattern": pattern,
             "confidence": float(confidence) if confidence is not None else None, "price": price}
        )
    return detection_id

# --- Cache ---
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
                if datetime.now(timezone.utc) - cache_time < timedelta(seconds=TXConfig.CACHE_DURATION):
                    return data.get("candles", [])
            except Exception:
                return data.get("candles", [])
        return []

    @staticmethod
    def update_cache(symbol: str, candles):
        cache = DataCache.load_cache()
        cache[symbol] = {
            "candles": candles,
            "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        }
        DataCache.save_cache(cache)

# --- Alerts ---
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
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

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


# --- Engine ---
class TXEngine:
    def __init__(self):
        self.scan_id = 0
        self.router = DataRouter(TXConfig) if DataRouter is not None else None
        self.trader = PaperTrader() if (PaperTrader is not None and TXConfig.ENABLE_PAPER_TRADING) else None
        self.recent_alerts = {}
        self.lock = threading.Lock()

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
            candles = DataCache.get_cached(symbol)
            if candles and len(candles) > 0 and isinstance(candles[-1], dict):
                last = candles[-1]
                return last.get("close") or last.get("price") or None

            if self.router and hasattr(self.router, "get_latest_candles"):
                candles = self.router.get_latest_candles(symbol)
                if isinstance(candles, list) and candles:
                    DataCache.update_cache(symbol, candles)
                    last = candles[-1]
                    return last.get("close") or last.get("price")
        except Exception as e:
            print("⚠️ get_market_price error:", e)
        return None

    def get_market_prices(self):
        prices = {}
        for symbol in TXConfig.ASSET_TYPES.keys():
            prices[symbol] = self.get_market_price(symbol)
        return prices

    def run_scan(self):
        with self.lock:
            self.scan_id += 1
            scan_time = datetime.now(timezone.utc).strftime('%H:%M:%S')
            results = []

            for symbol in TXConfig.ASSET_TYPES.keys():
                try:
                    candles = DataCache.get_cached(symbol)

                    if (not isinstance(candles, list) or len(candles) < 3) and self.router and hasattr(self.router, "get_latest_candles"):
                        try:
                            candles = self.router.get_latest_candles(symbol) or []
                            if isinstance(candles, list) and candles:
                                DataCache.update_cache(symbol, candles)
                        except Exception as e:
                            print(f"⚠️ DataRouter error for {symbol}: {e}")
                            candles = []

                    if not isinstance(candles, list) or len(candles) < 3:
                        results.append({"symbol": symbol, "status": "no_data"})
                        continue

                    last = candles[-1] if isinstance(candles[-1], dict) else {}
                    last_price = last.get("close") or last.get("price")

                    if self.trader:
                        try:
                            sell_trade = self.trader.check_auto_sell(symbol, last_price)
                            if sell_trade:
                                sell_trade["time"] = scan_time
                                app_state["paper_trades"].insert(0, sell_trade)
                        except Exception as e:
                            print(f"⚠️ trader.check_auto_sell error for {symbol}: {e}")

                    if detect_all_patterns is None:
                        results.append({"symbol": symbol, "status": "no_detectors", "price": last_price})
                        continue

                    detections = detect_all_patterns(candles) or []
                    best = None
                    for d in detections:
                        if not isinstance(d, dict):
                            continue
                        conf = d.get("confidence")
                        name = d.get("name")
                        if conf is None or name is None:
                            continue
                        if conf >= TXConfig.ALERT_CONFIDENCE_THRESHOLD and (
                            not TXConfig.PATTERN_WATCHLIST or name in TXConfig.PATTERN_WATCHLIST
                        ):
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
                            try:
                                trade = self.trader.buy(
                                    symbol,
                                    last_price,
                                    best.get("name"),
                                    best.get("confidence"),
                                    amount_usd=50
                                )
                                trade["time"] = scan_time
                                app_state["paper_trades"].insert(0, trade)
                            except Exception as e:
                                print(f"⚠️ trader.buy error for {symbol}: {e}")
                    else:
                        results.append({"symbol": symbol, "status": "no_pattern", "price": last_price})

                except Exception as e:
                    print(f"⚠️ run_scan error for {symbol}: {e}")
                    print(traceback.format_exc())
                    results.append({"symbol": symbol, "status": "error", "message": str(e)})

            # Consolidate by symbol, prefer pattern results
            consolidated = {}
            for r in results:
                s = r["symbol"]
                current = consolidated.get(s)
                if not current:
                    consolidated[s] = r
                else:
                    if r.get("status") == "pattern" and current.get("status") != "pattern":
                        consolidated[s] = r

            # Persist last_scan in memory
            scan_payload = {
                "id": self.scan_id,
                "time": scan_time,
                "results": list(consolidated.values())
            }
            app_state["last_scan"] = scan_payload
            return scan_payload

# --- Background scanner (start once) ---
SCANNER_STARTED = False
SCANNER_THREAD = None

def background_scan_loop():
    tx_engine = TXEngine()
    print("✅ background_scan_loop: thread running")
    while True:
        start_time = time.time()
        try:
            scan = tx_engine.run_scan()
            scan_id = scan.get("id") if isinstance(scan, dict) else None
            scan_time = scan.get("time") if isinstance(scan, dict) else None
            results_len = len(scan.get("results", [])) if isinstance(scan, dict) else 0
            print(f"🛰️ scan #{scan_id} at {scan_time} with {results_len} results")
            elapsed = time.time() - start_time
            sleep_time = max(1, TXConfig.BACKEND_SCAN_INTERVAL - elapsed)
            if sleep_time < 1:
                print(f"⚠️ Scan took {elapsed:.1f}s (longer than interval)")
            time.sleep(sleep_time)
        except Exception as e:
            print("⚠️ Scan loop crashed:", e)
            print(traceback.format_exc())
            time.sleep(min(30, TXConfig.BACKEND_SCAN_INTERVAL))

def start_background_scanner():
    global SCANNER_STARTED, SCANNER_THREAD
    if SCANNER_STARTED:
        return
    SCANNER_THREAD = threading.Thread(
        target=background_scan_loop,
        daemon=True,
        name="tx-scan-loop"
    )
    SCANNER_THREAD.start()
    SCANNER_STARTED = True
    print("✅ Background scan thread started")

# Start on import and guard on each request
start_background_scanner()

@app.before_request
def _ensure_scanner():
    start_background_scanner()

# --- API routes ---
@app.route("/api/scan", methods=["GET", "POST"])
def api_scan():
    try:
        tx_engine = TXEngine()
        scan = tx_engine.run_scan()
        return jsonify({
            "last_scan": scan,
            "alerts": app_state.get("alerts", []),
            "paper_trades": app_state.get("paper_trades", []),
            "last_signal": app_state.get("last_signal")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def save_last_scan(state):
    with engine.begin() as conn:
        stmt = text("""
            INSERT INTO app_state (key, value)
            VALUES (:key, :value::jsonb)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()
        """).bindparams(
            bindparam("key", type_=str),
            bindparam("value", type_=str)
        )
        conn.execute(stmt, {"key": "last_scan", "value": json.dumps(state["last_scan"])})
    return state["last_scan"]

@app.route("/api/debug_scan", methods=["GET", "POST"])
def debug_scan():
    try:
        print("⚡ Running debug_scan()")
        tx_engine = TXEngine()
        scan = tx_engine.run_scan()
        app_state["last_scan"] = scan
        print(f"✅ debug_scan success: id={scan.get('id')} with {len(scan.get('results', []))} results")
        return jsonify({"debug_scan": scan})
    except Exception as e:
        tb = traceback.format_exc()
        print("❌ debug_scan error:", e)
        print(tb)
        return jsonify({"error": str(e), "trace": tb}), 500

@app.route("/api/profile", methods=["GET", "POST"])
def get_profile():
    visitor_id = request.cookies.get("visitor_id")
    if not visitor_id:
        return jsonify({"error": "No visitor_id cookie"}), 401
    try:
        with engine.begin() as conn:
            row = conn.execute(
                text("""
                    SELECT id, first_seen, last_seen, user_agent, ip, visit_count, refresh_interval, name, email, mode
                    FROM visitors
                    WHERE id = :id
                """),
                {"id": visitor_id}
            ).mappings().fetchone()

        if not row:
            return jsonify({"error": "Profile not found"}), 404

        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500

@app.route("/api/save-profile", methods=["POST"])
def api_save_profile():
    try:
        data = request.get_json(force=True) or {}
        required = ["id", "name", "email", "mode"]
        missing = [k for k in required if not data.get(k)]
        if missing:
            return jsonify({"status": "error", "message": f"Missing: {', '.join(missing)}"}), 400

        user_id = str(data["id"]).strip()
        name = str(data["name"]).strip()
        email = str(data["email"]).strip().lower()
        mode_value = str(data["mode"]).strip().lower()

        if not is_valid_uuid(user_id):
            return jsonify({"status": "error", "message": "Invalid user ID format"}), 400
        if mode_value not in ("demo", "live"):
            return jsonify({"status": "error", "message": "Invalid mode. Must be 'demo' or 'live'."}), 400

        username = (data.get("username") or name or (email.split("@")[0] if email else "") or f"user_{user_id[:8]}").strip()

        # Ensure user exists in auth.users
        auth_user = supabase.table("auth.users").select("id").eq("id", user_id).execute()
        if not auth_user.data:
            #ddd
            app.logger.info(f"User {user_id} not found in auth.users — inserting.")
            supabase.table("users", schema="auth").insert({"id": user_id, "email": email}).execute()

        # Ensure user exists in public.users (if you have that table for FKs)
        public_user = supabase.table("users").select("id").eq("id", user_id).execute()
        if not public_user.data:
            # empty list means no match
            app.logger.info(f"User {user_id} not found in public.users — inserting.")
            supabase.table("users").insert({"id": user_id}).execute()

        # Save profile via chosen mode (db or rest)
        profile_result = save_profile(None, user_id, username, name, email, mode_value)
        app.logger.info("Profile save result: %s", profile_result)
        if not profile_result or profile_result.get("status") != "ok":
            return jsonify({"status": "error", "message": profile_result.get("message", "Unknown error")}), 500

        # Seed visitors row if missing
        visitors_check = supabase.table("visitors").select("id").eq("id", user_id).execute()
        if not getattr(visitors_check, "data", None):
            supabase.table("visitors").insert({
                "id": user_id,
                "ip": request.remote_addr,
                "name": name,
                "email": email,
                "mode": mode_value
            }).execute()

        # Seed portfolio if empty
        portfolio_check = supabase.table("portfolio").select("id").eq("user_id", user_id).execute()
        if not getattr(portfolio_check, "data", None):
            supabase.table("portfolio").insert({
                "user_id": user_id,
                "asset": "bitcoin",
                "quantity": 10,
                "avg_price": 150.00
            }).execute()

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        app.logger.error("ERROR in /api/save-profile: %s", e)
        app.logger.error(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/set-refresh", methods=["GET", "POST"])
def api_set_refresh():
    try:
        try:
            secs = int((request.json or {}).get("seconds", TXConfig.DEFAULT_USER_REFRESH))
        except (ValueError, TypeError):
            secs = TXConfig.DEFAULT_USER_REFRESH
        secs = max(5, min(3600, secs))

        visitor_id = request.cookies.get("visitor_id") or str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()

        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO visitors (id, refresh_interval, last_seen)
                    VALUES (:id, :refresh_interval, :last_seen)
                    ON CONFLICT (id)
                    DO UPDATE SET
                        refresh_interval = EXCLUDED.refresh_interval,
                        last_seen = EXCLUDED.last_seen
                """),
                {"id": visitor_id, "refresh_interval": secs, "last_seen": now_iso}
            )

        resp = make_response(jsonify({"status": "ok", "refresh_seconds": secs}), 200)
        resp.set_cookie("visitor_id", visitor_id,
                        max_age=60 * 60 * 24 * 30, httponly=True, secure=True, samesite="Lax")
        return resp
    except Exception:
        app.logger.exception("Failed to set refresh interval")
        return jsonify({"error": "internal_error"}), 500

@app.route("/api/portfolio", methods=["GET", "POST"])
def api_portfolio():
    try:
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"status": "error", "message": "Missing user_id"}), 400

        db_result = supabase.table("portfolio").select("*").eq("user_id", user_id).execute()
        if getattr(db_result, "error", None):
            app.logger.error(f"Supabase portfolio query error: {db_result.error}")
        elif getattr(db_result, "data", None):
            return jsonify({"source": "supabase", "portfolio": db_result.data}), 200

        engine_tx = TXEngine()
        if hasattr(engine_tx, 'trader') and engine_tx.trader:
            prices = engine_tx.get_market_prices()
            snapshot = engine_tx.trader.get_portfolio_value(prices)
            snapshot["market_prices"] = prices
            return jsonify({"source": "engine", "portfolio": snapshot}), 200

        return jsonify({
            "source": "empty",
            "portfolio": {
                "balance": 0.0,
                "invested": 0.0,
                "open_positions": {},
                "total_equity": 0.0,
                "realized_pnl": 0.0,
                "unrealized_pnl": 0.0,
                "market_prices": {}
            }
        }), 200

    except Exception as e:
        app.logger.error(f"Portfolio API error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/logs/detections", methods=["GET", "POST"])
def api_logs_detections():
    try:
        with engine.begin() as conn:
            rows = conn.execute(
                text("SELECT * FROM detections ORDER BY timestamp DESC NULLS LAST LIMIT 1000")
            ).mappings().all()
        return jsonify({"detections": [dict(r) for r in rows]})
    except Exception as e:
        app.logger.exception("Failed to fetch detection logs")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/logs/trades", methods=["GET", "POST"])
def api_logs_trades():
    try:
        engine_tx = TXEngine()
        if hasattr(engine_tx, 'trader') and engine_tx.trader:
            return jsonify({"trades": engine_tx.trader.get_trade_log()})
        return jsonify({"trades": []})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/detections/latest", methods=["GET", "POST"])
def get_latest_detection_id():
    try:
        with engine.begin() as conn:
            row = conn.execute(
                text("""
                    SELECT id
                    FROM detections
                    ORDER BY timestamp DESC NULLS LAST, id DESC
                    LIMIT 1
                """)
            ).fetchone()
        detection_id = row[0] if row else None
        resp = make_response(jsonify({"detection_id": detection_id}), 200)
        resp.headers["Cache-Control"] = "no-store"
        return resp
    except Exception:
        app.logger.exception("Failed to get latest detection id")
        return jsonify({"error": "internal_error"}), 500

@app.route("/api/log_outcome", methods=["GET", "POST"])
def api_log_outcome():
    try:
        data = request.get_json(silent=True) or {}
        det_id = data.get("detection_id")
        outcome = data.get("outcome")
        if not det_id or not outcome:
            return jsonify({"status": "error", "message": "missing fields"}), 400

        with engine.begin() as conn:
            result = conn.execute(
                text("""
                    UPDATE detections
                    SET outcome = :outcome, verified = TRUE
                    WHERE id = :id
                """),
                {"outcome": outcome, "id": det_id}
            )

        if result.rowcount > 0:
            return jsonify({"status": "ok"})
        else:
            return jsonify({"status": "error", "message": "detection_not_found"}), 404
    except Exception:
        app.logger.exception("Failed to update detection outcome")
        return jsonify({"status": "error", "message": "internal_error"}), 500

@app.route("/api/get_active_alerts", methods=["GET", "POST"])
def api_get_active_alerts():
    return jsonify({"alerts": app_state["alerts"]})

@app.route("/api/handle_alert_response", methods=["GET", "POST"])
def api_handle_alert_response():
    try:
        data = request.get_json() or {}
        action = data.get("action", "IGNORE")
        print(f"User alert response: {action}")
        return jsonify({"status": "recorded", "action": action})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/submit-feedback", methods=["GET", "POST"])
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
                f.write(json.dumps({"who": who, "feedback": feedback,
                                    "ts": datetime.now(timezone.utc).isoformat()}) + "\n")
            return jsonify({"status": "ok", "note": "stored_locally"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/backup", methods=["GET", "POST"])
def api_backup():
    try:
        token = os.getenv("TOKEN")
        repo = os.getenv("BACKUP_REPO")
        if not token or not repo:
            return jsonify({"status": "error", "message": "Backup not configured"}), 400

        with engine.begin() as conn:
            visitors_rows = conn.execute(text("SELECT * FROM visitors")).mappings().all()
            detections_rows = conn.execute(text("SELECT * FROM detections")).mappings().all()

        visitors = [dict(r) for r in visitors_rows]
        detections = [dict(r) for r in detections_rows]

        ts = datetime.now(timezone.utc).isoformat()
        snapshot = {"visitors": visitors, "detections": detections, "timestamp": ts}
        with open("tx_backup.json", "w", encoding="utf-8") as f:
            json.dump(snapshot, f, default=str, ensure_ascii=False, indent=2)

        subprocess.run(["git", "add", "tx_backup.json"], check=True)
        subprocess.run(["git", "commit", "-m", f"backup: {ts}"], check=True)
        subprocess.run(["git", "push", f"https://{token}@github.com/{repo}.git", "HEAD:main"], check=True)

        return jsonify({"status": "ok"})
    except subprocess.CalledProcessError:
        app.logger.exception("Git backup command failed")
        return jsonify({"status": "error", "message": "internal_error"}), 500
    except Exception:
        app.logger.exception("Backup failed")
        return jsonify({"status": "error", "message": "internal_error"}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})


# --- SPA serving ---
@app.route("/")
def index():
    visitor_id = track_visit(request)
    resp = make_response(send_from_directory(app.static_folder, "index.html"))
    resp.set_cookie("visitor_id", visitor_id, max_age=60*60*24*30)
    return resp

@app.route("/<path:path>", methods=["GET", "POST"])
def serve_spa(path):
    full_path = os.path.join(app.static_folder, path)
    if os.path.isfile(full_path):
        return send_from_directory(app.static_folder, path)
    if path.startswith("api/"):  # Don’t intercept API calls
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(app.static_folder, "index.html")

# --- Route listing once at first request ---
_routes_logged = False
@app.before_request
def _log_routes_once():
    global _routes_logged
    if not _routes_logged:
        app.logger.info("Registered routes:")
        for rule in app.url_map.iter_rules():
            app.logger.info(f"{rule} -> {rule.endpoint} [{','.join(rule.methods)}]")
        _routes_logged = True

# --- Serve ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    try:
        from waitress import serve
        serve(app, host=host, port=port)
    except ImportError:
        app.run(host=host, port=port, debug=False)
