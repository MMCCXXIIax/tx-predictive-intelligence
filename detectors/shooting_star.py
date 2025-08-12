# detectors/shooting_star.py

def is_shooting_star(candles):
    """
    Detects a Shooting Star candlestick pattern and returns detailed info.
    """
    if len(candles) < 1:
        return {
            "pattern": "Shooting Star",
            "detected": False,
            "confidence": 0.0,
            "explanation": "At least 1 candle is required to detect a Shooting Star pattern."
        }

    c = candles[-1]
    open_price = c["open"]
    close_price = c["close"]
    high = c["high"]
    low = c["low"]

    body = abs(close_price - open_price)
    upper_shadow = high - max(open_price, close_price)
    lower_shadow = min(open_price, close_price) - low
    total_range = high - low

    body_ratio = body / total_range if total_range else 0
    upper_shadow_ratio = upper_shadow / (body + 1e-6)
    lower_shadow_ratio = lower_shadow / (body + 1e-6)

    is_small_body = body_ratio <= 0.2
    is_long_upper_shadow = upper_shadow >= 2 * body
    is_short_lower_shadow = lower_shadow <= body

    if is_small_body and is_long_upper_shadow and is_short_lower_shadow:
        confidence = round(min(1.0, upper_shadow_ratio), 2)
        explanation = (
            f"Shooting Star detected — small body ({body:.2f}) with long upper shadow ({upper_shadow:.2f}) "
            f"and short lower shadow ({lower_shadow:.2f}). Indicates bearish reversal."
        )
        return {
            "pattern": "Shooting Star",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Shooting Star",
        "detected": False,
        "confidence": 0.0,
        "explanation": (
            f"Pattern conditions not met — body={body:.2f}, upper_shadow={upper_shadow:.2f}, "
            f"lower_shadow={lower_shadow:.2f}, body_ratio={body_ratio:.2f}."
        )
    }

#pip install flask flask-cors python-dotenv requests waitress

#Environment variables

#ALPHA_VANTAGE_KEY — optional (for stock/forex).

#SLACK_WEBHOOK_URL — optional (for feedback/alerts).

#TOKEN and BACKUP_REPO — optional if you want automatic backups to GitHub.

#PORT — port to bind (Render/Replit will provide this).

#BACKEND_SCAN_INTERVAL — seconds between engine scans (default 30).

#DEFAULT_USER_REFRESH — frontend default refresh (default 120).

#CORS_EXTRA_ORIGINS — comma-separated additional origins to allow.



#3. Files required (must be present in project):

#detectors/ folder (all pattern detectors) and detectors/ai_pattern_logic.py

#services/data_router.py, services/crypto_data_services.py, services/alpha_data_services.py

#services/paper_trader.py If any of those are missing the server will still start but detection or data features will return helpful errors.



#4. Run

#Locally / Replit: python main.py

#For a multi-worker server in production (if you use gunicorn):

#gunicorn main:app -w 4 -b 0.0.0.0:$PORT



#5. Front-end integration

#Use /api/scan to power the dashboard. It returns refresh_seconds per visitor — the front-end should poll at that interval (or user override via /api/set-refresh).

#For portfolio view call /api/portfolio.

#To place paper trades POST to /api/paper-trades (see code payload example in earlier messages).

#To fetch alerts: /api/get_active_alerts.

#To list detections for study or ML: /api/logs/detections.