# 🚀 URGENT: Deploy Backend for Frontend Integration

## ⚡ Quick Deploy (5 Minutes)

### Step 1: Set Environment Variable on Render

1. Go to: https://dashboard.render.com
2. Find service: **tx-predictive-intelligence**
3. Click **Environment** tab
4. Add new variable:
   - **Key:** `CORS_ORIGINS`
   - **Value:** `https://tx-figma-frontend.onrender.com,http://localhost:3000,http://localhost:5173`
5. Click **Save Changes**

### Step 2: Deploy

**Option A: Manual Deploy (Fastest)**
1. Go to **Manual Deploy** section
2. Click **Deploy latest commit**
3. Wait 3-5 minutes

**Option B: Git Push**
```bash
git add .
git commit -m "feat: Add CORS support for production frontend"
git push origin main
```

### Step 3: Verify

Run this command:
```bash
curl https://tx-predictive-intelligence.onrender.com/health
```

Expected response:
```json
{"status":"ok","timestamp":"2024-10-14T..."}
```

---

## ✅ What Was Changed

### 1. CORS Configuration (main.py)
- Added `https://tx-figma-frontend.onrender.com` to allowed origins
- Configured proper CORS headers for all requests
- Added support for credentials and all HTTP methods

### 2. WebSocket Support (main.py)
- Enhanced Socket.IO with CORS support
- Added logging for WebSocket connections
- Configured for production use

### 3. Gunicorn Worker (Procfile, render.yaml, gunicorn.conf.py)
- Changed from `gthread` to `geventwebsocket` worker
- Enables proper WebSocket support
- Increased timeout for long-running requests

### 4. Environment Variables (render.yaml)
- Added `CORS_ORIGINS` configuration
- Supports multiple origins (comma-separated)

---

## 🧪 Test After Deployment

Run the test script:
```powershell
.\test_cors_integration.ps1
```

Or test manually:
```bash
# Test health
curl https://tx-predictive-intelligence.onrender.com/health

# Test CORS
curl -H "Origin: https://tx-figma-frontend.onrender.com" \
  https://tx-predictive-intelligence.onrender.com/api/market-scan?type=trending

# Test pattern detection
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Origin: https://tx-figma-frontend.onrender.com" \
  -d '{"symbol":"AAPL"}' \
  https://tx-predictive-intelligence.onrender.com/api/detect-enhanced
```

---

## 🔍 Verify on Render Dashboard

After deployment, check:

1. **Status:** Should show "Live" (green)
2. **Logs:** No errors, should see:
   ```
   Booting worker with pid: ...
   Starting gevent on 0.0.0.0:10000
   ```
3. **Health Check:** Passing (green checkmark)
4. **Environment:** `CORS_ORIGINS` variable is set

---

## 🎯 Expected Frontend Behavior

Once deployed, the frontend will:
- ✅ Connect to backend successfully
- ✅ No more "ERR_NETWORK" errors
- ✅ WebSocket connection established
- ✅ Real-time alerts working
- ✅ Live market data displayed
- ✅ Pattern detection functional

---

## 🚨 If Issues Persist

### Issue: Still getting CORS errors

**Solution:**
1. Clear browser cache completely
2. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
3. Check Render logs for errors
4. Verify `CORS_ORIGINS` environment variable is set

### Issue: WebSocket not connecting

**Solution:**
1. Check Render logs for WebSocket errors
2. Verify Gunicorn is using `geventwebsocket` worker
3. Ensure `gevent-websocket` is in requirements.txt
4. Check if service restarted successfully

### Issue: Backend not responding

**Solution:**
1. Check Render Dashboard - is service "Live"?
2. Check logs for Python errors
3. Verify database connection (SUPABASE_URL, SUPABASE_KEY)
4. Try manual restart from Render Dashboard

---

## 📞 Communication with Frontend Team

Once deployed, notify frontend team:

**Message:**
```
✅ Backend deployed with CORS support
✅ Frontend domain whitelisted: https://tx-figma-frontend.onrender.com
✅ WebSocket support enabled
✅ All endpoints tested and working

Please:
1. Clear browser cache
2. Reload frontend application
3. Test connection
4. Report any issues

Backend URL: https://tx-predictive-intelligence.onrender.com
Health Check: https://tx-predictive-intelligence.onrender.com/health
```

---

## 📋 Deployment Checklist

- [ ] Environment variable `CORS_ORIGINS` added on Render
- [ ] Service deployed (manual or git push)
- [ ] Service status shows "Live"
- [ ] Health check passing
- [ ] No errors in Render logs
- [ ] Test script passes all tests
- [ ] Frontend team notified
- [ ] Browser cache cleared
- [ ] Frontend tested with live backend

---

## 🎉 Success Criteria

Deployment is successful when:
1. All curl tests return 200 status
2. CORS headers present in responses
3. WebSocket connects successfully
4. Frontend loads without errors
5. Real-time features working

---

**Time to Deploy:** ~5 minutes
**Priority:** 🔴 HIGH
**Status:** Ready to deploy

Deploy now and notify frontend team!
