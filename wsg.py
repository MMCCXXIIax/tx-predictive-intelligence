import os
from main import app

# This is required for Render's health checks
@app.route('/health')
def health_check():
    return "OK", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 9000)))