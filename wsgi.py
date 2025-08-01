from dotenv import load_dotenv
from main import app
import os

load_dotenv()  # Load environment variables

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 808))
    print(f"🚀 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)