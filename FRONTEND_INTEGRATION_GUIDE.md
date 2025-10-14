# 🔗 Frontend Integration - Deployment Guide

## ✅ Changes Made

### 1. CORS Configuration Updated
**File:** `main.py` (lines 216-247)

**Added production frontend domain:**
```python
cors_origins = [
    "https://tx-figma-frontend.onrender.com",  # Production frontend
    "http://localhost:3000",                    # Local development
    "http://localhost:5173",                    # Vite dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173"
]

cors = CORS(
    app,
    origins=cors_origins,
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)
```

### 2. Socket.IO CORS Configured
**File:** `main.py` (lines 241-247)

**Enhanced WebSocket support:**
```python
socketio = SocketIO(
    app, 
    cors_allowed_origins=socketio_origins, 
    async_mode='threading',
    logger=True,
    engineio_logger=True
)
```

### 3. Gunicorn Worker Updated
**Files:** `Procfile`, `render.yaml`, `gunicorn.conf.py`

**Changed from gthread to geventwebsocket for WebSocket support:**
```bash
gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 -b 0.0.0.0:$PORT main:app
```

### 4. Environment Variables Added
**File:** `render.yaml`

**Added CORS_ORIGINS environment variable:**
```yaml
- key: CORS_ORIGINS
  value: https://tx-figma-frontend.onrender.com,http://localhost:3000,http://localhost:5173
```

---

## 🚀 Deployment Steps

### Option 1: Deploy via Render Dashboard (Recommended)

1. **Go to Render Dashboard:**
   - Navigate to: https://dashboard.render.com
   - Find your service: `tx-predictive-intelligence`

2. **Add Environment Variable:**
   - Go to "Environment" tab
   - Add new variable:
     - **Key:** `CORS_ORIGINS`
     - **Value:** `https://tx-figma-frontend.onrender.com,http://localhost:3000,http://localhost:5173`
   - Click "Save Changes"

3. **Trigger Manual Deploy:**
   - Go to "Manual Deploy" section
   - Click "Deploy latest commit"
   - Wait 3-5 minutes for deployment

4. **Verify Deployment:**
   - Check "Logs" tab for any errors
   - Service should show "Live" status
   - Health check should pass

### Option 2: Deploy via Git Push

1. **Commit Changes:**
   ```bash
   git add .
   git commit -m "feat: Add CORS support for production frontend"
   git push origin main
   ```

2. **Render Auto-Deploy:**
   - Render will automatically detect the push
   - Build will start automatically
   - Wait 3-5 minutes for deployment

---

## 🧪 Testing After Deployment

### Test 1: Health Check
```bash
curl https://tx-predictive-intelligence.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-10-14T19:57:00.000Z"
}
```

### Test 2: CORS Preflight
```bash
curl -X OPTIONS \
  -H "Origin: https://tx-figma-frontend.onrender.com" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v \
  https://tx-predictive-intelligence.onrender.com/health
```

**Expected Headers:**
```
Access-Control-Allow-Origin: https://tx-figma-frontend.onrender.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
```

### Test 3: Market Scan Endpoint
```bash
curl -H "Origin: https://tx-figma-frontend.onrender.com" \
  https://tx-predictive-intelligence.onrender.com/api/market-scan?type=trending
```

### Test 4: Pattern Detection
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Origin: https://tx-figma-frontend.onrender.com" \
  -d '{"symbol":"AAPL"}' \
  https://tx-predictive-intelligence.onrender.com/api/detect-enhanced
```

### Test 5: Active Alerts
```bash
curl -H "Origin: https://tx-figma-frontend.onrender.com" \
  https://tx-predictive-intelligence.onrender.com/api/get_active_alerts
```

---

## 🔍 Troubleshooting

### Issue 1: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Cause:** Environment variable not set on Render

**Solution:**
1. Go to Render Dashboard → Environment
2. Add `CORS_ORIGINS` variable
3. Redeploy service

### Issue 2: "WebSocket connection failed"

**Cause:** Gunicorn worker not supporting WebSockets

**Solution:**
1. Verify `Procfile` uses `geventwebsocket.gunicorn.workers.GeventWebSocketWorker`
2. Check Render logs for worker errors
3. Ensure `gevent-websocket` is in `requirements.txt`

### Issue 3: "Backend not responding"

**Cause:** Service not running or crashed

**Solution:**
1. Check Render Dashboard → Logs
2. Look for Python errors or crashes
3. Verify all environment variables are set
4. Check database connection (SUPABASE_URL, SUPABASE_KEY)

### Issue 4: "OPTIONS request returns 404"

**Cause:** Flask not handling OPTIONS requests

**Solution:**
- Already handled by Flask-CORS middleware
- Verify CORS middleware is initialized before routes

---

## 📊 Endpoint Verification Checklist

After deployment, verify these critical endpoints:

- [ ] `GET /health` - Basic health check
- [ ] `GET /api/provider-health` - Data providers status
- [ ] `GET /api/market-scan?type=trending` - Market scan
- [ ] `POST /api/detect-enhanced` - Pattern detection
- [ ] `GET /api/get_active_alerts` - Active alerts
- [ ] `GET /api/scan/status` - Scan status
- [ ] `GET /api/paper-trades` - Paper trades
- [ ] `GET /api/pattern-stats` - Pattern statistics
- [ ] WebSocket connection to `/socket.io/`

---

## 🔐 Environment Variables Required on Render

Ensure these are set in Render Dashboard:

### Required
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase service role key
- `CORS_ORIGINS` - Frontend domains (comma-separated)

### Optional
- `FLASK_ENV` - Set to `production`
- `SENTRY_DSN` - For error tracking
- `BACKEND_SCAN_INTERVAL` - Scan interval in seconds (default: 180)
- `ALERT_CONFIDENCE_THRESHOLD` - Minimum confidence for alerts (default: 0.85)
- `ENABLE_PAPER_TRADING` - Enable paper trading (default: true)

---

## 🎯 Frontend Connection Test

Once backend is deployed, test from frontend:

### JavaScript Test
```javascript
// Test API connection
fetch('https://tx-predictive-intelligence.onrender.com/health')
  .then(r => r.json())
  .then(data => console.log('✅ Backend connected:', data))
  .catch(err => console.error('❌ Backend error:', err));

// Test WebSocket connection
import { io } from 'socket.io-client';

const socket = io('https://tx-predictive-intelligence.onrender.com', {
  transports: ['websocket', 'polling']
});

socket.on('connect', () => {
  console.log('✅ WebSocket connected:', socket.id);
});

socket.on('connect_error', (error) => {
  console.error('❌ WebSocket error:', error.message);
});
```

---

## 📝 Render Dashboard Configuration

### Service Settings
- **Name:** tx-predictive-intelligence
- **Environment:** Python 3.11
- **Region:** Oregon (US West) or closest to your users
- **Plan:** Starter ($7/month) or Free

### Build Settings
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 -b 0.0.0.0:$PORT main:app`

### Health Check
- **Path:** `/health`
- **Expected Status:** 200

---

## 🚨 Common Deployment Errors

### Error: "Worker failed to boot"
**Solution:** Check requirements.txt includes `gevent-websocket`

### Error: "Address already in use"
**Solution:** Ensure only 1 worker (`-w 1`) in Gunicorn command

### Error: "Database connection failed"
**Solution:** Verify SUPABASE_URL and SUPABASE_KEY are set

### Error: "Module not found"
**Solution:** Ensure all dependencies in requirements.txt

---

## ✅ Success Indicators

After deployment, you should see:

1. **Render Dashboard:**
   - Status: "Live" (green)
   - Health Check: Passing
   - No errors in logs

2. **Browser Console (Frontend):**
   - No CORS errors
   - WebSocket connected
   - API calls returning data

3. **Test Endpoints:**
   - All curl tests return 200 status
   - JSON responses with expected data

---

## 📞 Next Steps

1. **Deploy backend changes to Render**
2. **Verify all tests pass**
3. **Clear frontend browser cache**
4. **Reload frontend application**
5. **Test all features with live backend**

---

## 🎉 Expected Result

Once deployed, your frontend at `https://tx-figma-frontend.onrender.com` will:
- ✅ Successfully connect to backend
- ✅ Receive real-time WebSocket updates
- ✅ Display live market data
- ✅ Show pattern detections
- ✅ Handle alerts properly
- ✅ Execute paper trades

**No more demo mode! 🚀**
