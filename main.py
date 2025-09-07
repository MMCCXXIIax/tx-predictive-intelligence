# --- Standard library ---
import os
import csv
import io
import json
import subprocess
import time
import threading
import uuid
import traceback
from datetime import datetime, timedelta, timezone

# --- Third‑party libraries ---
from flask import Flask, request, jsonify, make_response, send_from_directory, Response
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text

# --- Local services ---
# Shared engine (same as other services) — used for detections and optional paper_trades
from services.db import engine

# Optional imports with safety (no user/profile writes anywhere)
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

# Supabase client (v2.x) — service role only (no per-user JWT)
from supabase import create_client

load_dotenv()

# --- Flask app ---
app = Flask(__name__, static_folder="client/dist", static_url_path="")

# --- CORS (explicit) ---
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
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

class TXConfig:
    ASSET_TYPES = {
        "bitcoin": "crypto",
        "ethereum": "crypto",
        "solana": "crypto",
        "AAPL": "stock",
        "TSLA": "stock"
    }
    BACKEND_SCAN_INTERVAL = int(os.getenv("BACKEND_SCAN_INTERVAL", "30"))
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

    # Restore this so DataRouter doesn't crash
    DEFAULT_USER_REFRESH = int(os.getenv("DEFAULT_USER_REFRESH", "120"))

# --- Bootstrap only essential tables (no users/visitors/profiles/portfolio) ---
with engine.begin() as conn:
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
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS paper_trades (
            id UUID PRIMARY KEY,
            user_id UUID,
            symbol TEXT,
            side TEXT,
            qty NUMERIC,
            price NUMERIC,
            opened_at TIMESTAMP DEFAULT NOW(),
            closed_at TIMESTAMP
        )
    """))

# --- In-memory state ---
app_state = {
    "last_scan": {"id": 0, "time": None, "results": []},
    "alerts": [],
    "paper_trades": [],  # in-memory feed from PaperTrader if available
    "last_signal": None
}

# --- Helpers ---
def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

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

# --- Cache for candles ---
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

            scan_payload = {
                "id": self.scan_id,
                "time": scan_time,
                "results": list(consolidated.values())
            }
            app_state["last_scan"] = scan_payload
            return scan_payload

# --- Background scanner ---
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

start_background_scanner()

@app.before_request
def _ensure_scanner():
    start_background_scanner()

# =========================================================
# Minimal UI
# =========================================================
@app.route("/")
def index():
    # No visitor tracking, no DB writes — just a simple status page
    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>TX Beta</title>
        <style>
          body {{ font-family: Inter, system-ui, Arial, sans-serif; margin: 40px; color: #111; }}
          .ok {{ color: #2ecc71; font-size: 24px; }}
          .box {{ margin-top: 16px; padding: 12px 16px; border: 1px solid #eee; border-radius: 8px; }}
          code {{ background: #f6f8fa; padding: 2px 6px; border-radius: 4px; }}
        </style>
      </head>
      <body>
        <div class="ok">✅ TX Beta is running</div>
        <div class="box">
          <div>Time: <code>{datetime.utcnow().isoformat()}</code></div>
          <div>Scan loop: <code>enabled</code></div>
          <div>Profile/visitor writes: <code>disabled</code></div>
          <div>Auth: <code>Supabase Service Role</code></div>
        </div>
      </body>
    </html>
    """
    resp = make_response(html, 200)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    return resp

# =========================================================
# Frontend-aligned API
# =========================================================

# Core Detection & Alerts
@app.route("/api/get_active_alerts", methods=["GET"])
def api_get_active_alerts():
    return jsonify({"alerts": app_state.get("alerts", [])})

@app.route("/api/scan", methods=["GET"])
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
        app.logger.exception("scan error")
        return jsonify({"error": str(e)}), 500

@app.route("/api/handle_alert_response", methods=["POST"])
def api_handle_alert_response():
    try:
        data = request.get_json() or {}
        action = data.get("action", "IGNORE")
        return jsonify({"status": "recorded", "action": action})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/get_latest_detection_id", methods=["GET"])
def api_get_latest_detection_id():
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
        return jsonify({"detection_id": row[0] if row else None}), 200
    except Exception:
        app.logger.exception("get_latest_detection_id failed")
        return jsonify({"error": "internal_error"}), 500

@app.route("/api/log_outcome", methods=["POST"])
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
        app.logger.exception("log_outcome failed")
        return jsonify({"status": "error", "message": "internal_error"}), 500

# Paper Trading
@app.route("/api/paper-trades", methods=["GET"])
def api_get_paper_trades():
    try:
        tx_engine = TXEngine()
        if hasattr(tx_engine, 'trader') and tx_engine.trader and hasattr(tx_engine.trader, "get_positions"):
            return jsonify({"positions": tx_engine.trader.get_positions()}), 200
        # Optional: also return persisted paper_trades
        with engine.begin() as conn:
            rows = conn.execute(text("""
                SELECT id, user_id, symbol, side, qty, price, opened_at, closed_at
                FROM paper_trades
                ORDER BY opened_at DESC NULLS LAST
            """)).mappings().all()
        return jsonify({"positions": [dict(r) for r in rows]}), 200
    except Exception as e:
        app.logger.exception("paper-trades GET failed")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/paper-trades", methods=["POST"])
def api_place_paper_trade():
    try:
        data = request.get_json(force=True) or {}
        user_id = data.get("user_id")  # optional; trusted as-is in beta
        symbol = data.get("symbol")
        side = (data.get("side") or "buy").lower()
        qty = data.get("qty", 1)
        if not symbol:
            return jsonify({"status": "error", "message": "missing symbol"}), 400

        tx_engine = TXEngine()
        if hasattr(tx_engine, "trader") and tx_engine.trader:
            price = tx_engine.get_market_price(symbol)
            if price is None:
                return jsonify({"status": "error", "message": "no_price"}), 400
            if side == "buy":
                trade = tx_engine.trader.buy(symbol, price, "manual", 1.0, amount_usd=None, qty=qty)
            else:
                trade = tx_engine.trader.sell(symbol, price, "manual", 1.0, qty=qty)
            app_state["paper_trades"].insert(0, trade)
            return jsonify({"status": "ok", "trade": trade}), 200

        # Persist minimally if trader not present (optional)
        with engine.begin() as conn:
            tid = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO paper_trades (id, user_id, symbol, side, qty, price)
                VALUES (:id, :user_id, :symbol, :side, :qty, 0)
            """), {"id": tid, "user_id": user_id, "symbol": symbol, "side": side, "qty": qty})
        return jsonify({"status": "ok", "trade": {"id": tid, "symbol": symbol, "side": side, "qty": qty}}), 200
    except Exception as e:
        app.logger.exception("paper-trades POST failed")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/close-position", methods=["POST"])
def api_close_position():
    try:
        data = request.get_json(force=True) or {}
        symbol = data.get("symbol")
        if not symbol:
            return jsonify({"status": "error", "message": "missing symbol"}), 400

        tx_engine = TXEngine()
        if hasattr(tx_engine, "trader") and tx_engine.trader:
            price = tx_engine.get_market_price(symbol)
            if price is None:
                return jsonify({"status": "error", "message": "no_price"}), 400
            result = tx_engine.trader.close(symbol, price)
            return jsonify({"status": "ok", "result": result}), 200

        # Stub fallback
        return jsonify({"status": "ok", "result": "closed"}), 200
    except Exception as e:
        app.logger.exception("close-position failed")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/trading-stats", methods=["GET"])
def api_trading_stats():
    try:
        tx_engine = TXEngine()
        if hasattr(tx_engine, "trader") and tx_engine.trader and hasattr(tx_engine.trader, "get_stats"):
            stats = tx_engine.trader.get_stats()
            return jsonify({"stats": stats}), 200

        # Minimal aggregate from persisted paper_trades
        with engine.begin() as conn:
            rows = conn.execute(text("""
                SELECT symbol, side, qty, price, opened_at, closed_at
                FROM paper_trades
            """)).mappings().all()
        stats = {
            "total_trades": len(rows),
            "open_positions": sum(1 for r in rows if r["closed_at"] is None)
        }
        return jsonify({"stats": stats}), 200
    except Exception as e:
        app.logger.exception("trading-stats failed")
        return jsonify({"status": "error", "message": str(e)}), 500

# Detection Logs & Analytics
@app.route("/api/detection_stats", methods=["GET"])
def api_detection_stats():
    try:
        with engine.begin() as conn:
            row = conn.execute(text("""
                SELECT
                    COUNT(*)::int AS total,
                    SUM(CASE WHEN verified THEN 1 ELSE 0 END)::int AS verified_count
                FROM detections
            """)).mappings().fetchone()
        return jsonify({"stats": dict(row) if row else {"total": 0, "verified_count": 0}}), 200
    except Exception as e:
        app.logger.exception("detection_stats failed")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/export_detection_logs", methods=["GET"])
def api_export_detection_logs():
    try:
        with engine.begin() as conn:
            rows = conn.execute(text("""
                SELECT id, timestamp, symbol, pattern, confidence, price, outcome, verified
                FROM detections
                ORDER BY timestamp DESC NULLS LAST
            """)).mappings().all()

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["id","timestamp","symbol","pattern","confidence","price","outcome","verified"])
        writer.writeheader()
        for r in rows:
            writer.writerow(dict(r))
        csv_data = output.getvalue()
        output.close()

        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=detection_logs.csv"}
        )
    except Exception as e:
        app.logger.exception("export_detection_logs failed")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/detection_logs", methods=["GET"])
def api_detection_logs():
    try:
        with engine.begin() as conn:
            rows = conn.execute(
                text("SELECT * FROM detections ORDER BY timestamp DESC NULLS LAST LIMIT 1000")
            ).mappings().all()
        return jsonify({"logs": [dict(r) for r in rows]})
    except Exception as e:
        app.logger.exception("detection_logs failed")
        return jsonify({"status": "error", "message": str(e)}), 500

# User Profile — disabled in beta (no DB writes)
@app.route("/api/save-profile", methods=["POST"])
def api_save_profile_disabled():
    return jsonify({"status": "ok", "note": "Profile saving disabled in beta — Supabase Auth handles users."}), 200

# Market Data
@app.route("/api/candles", methods=["GET"])
def api_get_candles():
    try:
        symbol = request.args.get("symbol")
        timeframe = request.args.get("timeframe", "5m")
        if not symbol:
            return jsonify({"status": "error", "message": "missing symbol"}), 400

        candles = DataCache.get_cached(symbol)
        if (not candles) and DataRouter is not None:
            try:
                router = DataRouter(TXConfig)
                candles = router.get_latest_candles(symbol) or []
                if candles:
                    DataCache.update_cache(symbol, candles)
            except Exception as e:
                app.logger.warning(f"candles router error for {symbol}: {e}")

        return jsonify({"symbol": symbol, "timeframe": timeframe, "candles": candles[:TXConfig.CANDLE_LIMIT]})
    except Exception as e:
        app.logger.exception("candles failed")
        return jsonify({"status": "error", "message": str(e)}), 500

# Health
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})

# --- SPA static passthrough (optional; no visitor tracking) ---
@app.route("/<path:path>", methods=["GET", "POST"])
def serve_spa(path):
    full_path = os.path.join(app.static_folder, path)
    if os.path.isfile(full_path):
        return send_from_directory(app.static_folder, path)
    if path.startswith("api/"):  # Don’t intercept API calls
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(app.static_folder, "index.html")

# --- Route listing once ---
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
