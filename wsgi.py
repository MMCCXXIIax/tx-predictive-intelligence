from main import app
import os

@app.route('/health')
def health_check():
    """Render-compatible health check endpoint"""
    return {
        "status": "healthy",
        "version": os.getenv("RENDER_GIT_COMMIT", "dev")
    }, 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))