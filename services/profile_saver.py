import os
import uuid
import traceback
from flask import Flask, request, jsonify, render_template_string, make_response
from flask_cors import CORS
from sqlalchemy import text
from services.profile_saver import save_profile
from services.db import engine
from supabase import create_client
from psycopg2 import errors as pg_errors

app = Flask(__name__)

# --- CORS ---
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

# --- Supabase client ---
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(supabase_url, supabase_service_key)

# --- Utils ---
def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

def track_visit(req):
    """Insert visitor row, anonymizing IP if pgcrypto missing."""
    visitor_id = str(uuid.uuid4())
    ip = req.remote_addr
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO visitors (id, ip)
                VALUES (:id, :ip)
                ON CONFLICT (id) DO NOTHING
            """), {"id": visitor_id, "ip": ip})
    except pg_errors.UndefinedFunction:
        app.logger.warning("pgcrypto.digest() missing — falling back to md5 in hash_ip()")
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO visitors (id, ip_hash)
                VALUES (:id, md5(:ip || 'salt_for_privacy_protection'))
                ON CONFLICT (id) DO NOTHING
            """), {"id": visitor_id, "ip": ip})
    except Exception as e:
        app.logger.error(f"track_visit() failed: {e}")
    return visitor_id

# --- Routes ---
@app.route("/")
def dashboard():
    visitor_id = track_visit(request)
    resp = make_response(render_template_string("<h1>TX Predictive Intelligence — API</h1>"))
    resp.set_cookie("visitor_id", visitor_id, max_age=60*60*24*30)
    return resp

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

        username = (data.get("username") or name or email.split("@")[0] or f"user_{user_id[:8]}").strip()

        # Ensure user exists in auth.users
        auth_user = supabase.table("users", schema="auth").select("id").eq("id", user_id).execute()
        if not auth_user.data:
            supabase.table("users", schema="auth").insert({"id": user_id, "email": email}).execute()

        # Ensure user exists in public.users
        public_user = supabase.table("users").select("id").eq("id", user_id).execute()
        if not public_user.data:
            supabase.table("users").insert({"id": user_id}).execute()

        # Save profile
        profile_result = save_profile(None, user_id, username, name, email, mode_value)
        app.logger.info("Profile save result: %s", profile_result)
        if not profile_result or profile_result.get("status") != "ok":
            return jsonify({"status": "error", "message": profile_result.get("message", "Unknown error")}), 500

        # Seed visitors
        visitors_check = supabase.table("visitors").select("id").eq("id", user_id).execute()
        if not visitors_check.data:
            supabase.table("visitors").insert({
                "id": user_id,
                "ip": request.remote_addr,
                "name": name,
                "email": email,
                "mode": mode_value
            }).execute()

        # Seed portfolio
        portfolio_check = supabase.table("portfolio").select("id").eq("user_id", user_id).execute()
        if not portfolio_check.data:
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

@app.route("/api/detections/latest", methods=["GET"])
def get_latest_detection():
    try:
        with engine.begin() as conn:
            row = conn.execute(text("""
                SELECT id
                FROM detections
                ORDER BY timestamp DESC NULLS LAST, id DESC
                LIMIT 1
            """)).fetchone()
        return jsonify({"detection_id": row[0] if row else None})
    except Exception as e:
        app.logger.error("Error fetching latest detection: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 500

# ... keep all your other /api/* routes here unchanged ...
@app.route("/api/log_outcome", methods=["GET" , "POST"])
def api_log_outcome():
    try:
        data = request.get_json(silent=True) or {}
        det_id = data.get("detection_id")
        outcome = data.get("outcome")

        if not det_id or not outcome:
            return jsonify({"status": "error", "message": "missing fields"}), 400

        with engine.begin() as conn:  # transaction-safe context
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


@app.route("/api/get_active_alerts", methods=["GET" , "POST"])
def api_get_active_alerts():
    return jsonify({"alerts": app_state["alerts"]})

@app.route("/api/handle_alert_response", methods=["GET" , "POST"])
def api_handle_alert_response():
    try:
        data = request.get_json() or {}
        action = data.get("action", "IGNORE")
        print(f"User alert response: {action}")
        return jsonify({"status": "recorded", "action": action})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/submit-feedback", methods=["GET" , "POST"])
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
                    "ts": datetime.now(timezone.utc).isoformat()
                }) + "\n")
            return jsonify({"status": "ok", "note": "stored_locally"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/backup", methods=["GET" , "POST"])
def api_backup():
    try:
        token = os.getenv("TOKEN")
        repo = os.getenv("BACKUP_REPO")
        if not token or not repo:
            return jsonify({"status": "error", "message": "Backup not configured"}), 400

        # Pull data from Postgres (no raw cursor usage)
        with engine.begin() as conn:
            visitors_rows = conn.execute(text("SELECT * FROM visitors")).mappings().all()
            detections_rows = conn.execute(text("SELECT * FROM detections")).mappings().all()

        visitors = [dict(r) for r in visitors_rows]
        detections = [dict(r) for r in detections_rows]

        # Write a JSON snapshot (timestamp ensures new commit each run)
        ts = datetime.now(timezone.utc).isoformat()
        snapshot = {
            "visitors": visitors,
            "detections": detections,
            "timestamp": ts
        }
        with open("tx_backup.json", "w", encoding="utf-8") as f:
            json.dump(snapshot, f, default=str, ensure_ascii=False, indent=2)

        # Commit and push backup
        subprocess.run(["git", "add", "tx_backup.json"], check=True)
        subprocess.run(["git", "commit", "-m", f"backup: {ts}"], check=True)
        subprocess.run(
            ["git", "push", f"https://{token}@github.com/{repo}.git", "HEAD:main"],
            check=True
        )

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


@app.get("/api/debug")
def debug():
    try:
        with engine.begin() as conn:
            # Fetch last_scan_id
            row = conn.execute(
                text("SELECT value FROM app_state WHERE key = 'last_scan_id'")
            ).fetchone()
            last_scan_id = row.value if row else None

            # Count AlphaVantage errors
            alpha_errors_row = conn.execute(
                text("""
                    SELECT COUNT(*) AS cnt
                    FROM error_logs
                    WHERE source = 'AlphaVantage'
                """)
            ).fetchone()
            alpha_errors = alpha_errors_row.cnt if alpha_errors_row else 0

        # Memory usage in MB
        memory_usage = psutil.Process().memory_info().rss // 1024 // 1024

        return jsonify({
            "last_scan_id": last_scan_id,
            "alpha_errors": alpha_errors,
            "memory_usage": memory_usage
        })

    except Exception:
        app.logger.exception("Debug route failed")
        return jsonify({"status": "error", "message": "internal_error"}), 500



@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>", methods=["GET" , "POST"])
def serve_spa(path):
    import os
    full_path = os.path.join(app.static_folder, path)
    if os.path.isfile(full_path):
        return send_from_directory(app.static_folder, path)
    if path.startswith("api/"):  # Don’t intercept API calls
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(app.static_folder, "index.html")


# --- Startup route logging ---
@app.before_first_request
def log_routes():
    app.logger.info("Registered routes:")
    for rule in app.url_map.iter_rules():
        app.logger.info(f"{rule} -> {rule.endpoint} [{','.join(rule.methods)}]")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
