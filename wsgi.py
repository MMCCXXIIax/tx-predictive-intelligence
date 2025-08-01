from main import app
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 808))
    print(f"🚀 Starting on port {port}")  # Debug line
    app.run(host='0.0.0.0', port=port)