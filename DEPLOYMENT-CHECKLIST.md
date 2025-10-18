# 🚀 TX Backend Deployment Checklist

## ✅ Pre-Deployment Checklist

- [ ] All fixes applied to code
- [ ] Docker installed and running
- [ ] Logged into Docker Hub
- [ ] Railway account ready

---

## 📋 Step-by-Step Deployment

### STEP 1: Clean Everything (WSL2 Terminal)
```bash
cd "/mnt/c/Users/S/TX BACK/tx-predictive-intelligence"
bash rebuild-clean.sh
```

**Expected output:**
```
[1/5] Cleaning old images...
✓ Old images removed

[2/5] Cleaning build cache...
✓ Build cache cleaned

[3/5] Building new image (this will take 5-10 minutes)...
✓ Image built successfully

[4/5] Tagging image as v1.0.3...
✓ Image tagged

[5/5] Pushing to Docker Hub...
✓ Image pushed to Docker Hub

✓ REBUILD COMPLETE!
```

**Time:** 10-15 minutes

---

### STEP 2: Update Railway

1. **Go to Railway Dashboard**
   - URL: https://railway.app

2. **Click on your service**
   - Name: `tx-backend-production`

3. **Go to Settings**
   - Click "Settings" tab

4. **Update Docker Image**
   - Find "Docker Image" field
   - Change to: `jeanpaulkadusimanegaberobert1/tx-backend:v1.0.3`
   - Click "Save" or it will auto-save

5. **Verify Environment Variables**
   - Go to "Variables" tab
   - Ensure these are set:
     - `PORT=5000`
     - `ENVIRONMENT=production`
     - `DATABASE_URL=your_database_url`
     - `SUPABASE_URL=your_supabase_url`
     - `SUPABASE_KEY=your_supabase_key`

6. **Deploy**
   - Click "Deploy" button
   - OR it will auto-deploy after saving

---

### STEP 3: Monitor Deployment

1. **Watch Logs**
   - Go to "Deployments" tab
   - Click on latest deployment
   - Watch logs in real-time

2. **Look for Success Indicators:**
   - ✅ `Starting gunicorn 21.2.0`
   - ✅ `Listening at: http://0.0.0.0:5000`
   - ✅ `Server initialized for threading`
   - ✅ `Background scanner started`
   - ✅ `GET /health HTTP/1.1" 200`

3. **Check for Errors:**
   - ❌ Should NOT see: "Series ambiguity" errors
   - ⚠️ OK to see: Yahoo Finance warnings (non-critical)
   - ⚠️ OK to see: Twitter rate limits (non-critical)

---

### STEP 4: Test the Deployment

#### Test 1: Health Check
```bash
curl https://tx-backend-production.up.railway.app/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-18T...",
  "version": "1.0.0",
  "database": "connected",
  "services": {
    "pattern_detection": "running",
    "market_scanner": "running",
    "websocket": "running"
  }
}
```

#### Test 2: API Endpoint
```bash
curl https://tx-backend-production.up.railway.app/api/alerts
```

**Expected:** JSON array of alerts

#### Test 3: WebSocket (Optional)
Use a WebSocket client to connect to:
```
wss://tx-backend-production.up.railway.app
```

---

### STEP 5: Share with Frontend Team

**Send this information:**

```
🚀 TX Backend is Live!

Backend URL: https://tx-backend-production.up.railway.app

Health Check: GET /health
WebSocket: wss://tx-backend-production.up.railway.app

Status: ✅ Production Ready

All 67 endpoints are live and documented in the API docs.

Known minor issues:
- Yahoo Finance uses daily data fallback (non-critical)
- Twitter API uses fallback sentiment (non-critical)

Let me know if you need anything!
```

---

## 🔍 Troubleshooting

### Issue: "Series ambiguity" error still appears
**Solution:** 
1. Verify you're using `v1.0.3` image
2. Check Docker Hub to confirm image was pushed
3. Force Railway to pull fresh image by changing tag

### Issue: Healthcheck failing
**Solution:**
1. Check PORT environment variable is set
2. Verify Docker image is using `${PORT:-5000}`
3. Check Railway logs for startup errors

### Issue: Build takes too long
**Solution:**
1. This is normal (10-15 minutes)
2. Most layers should be cached
3. Only new code layers rebuild

---

## ✅ Final Verification

After deployment, verify:

- [ ] Health check returns HTTP 200
- [ ] No "Series ambiguity" errors in logs
- [ ] Background scanner running
- [ ] Alerts generating
- [ ] WebSocket events emitting
- [ ] All API endpoints accessible

---

## 🎯 Success Criteria

Your deployment is successful when:

1. ✅ Healthcheck passing (HTTP 200)
2. ✅ Clean logs (no Series errors)
3. ✅ All services running
4. ✅ Frontend team can connect
5. ✅ Real-time data flowing

---

## 📞 Need Help?

If anything goes wrong:
1. Check Railway logs first
2. Verify Docker image digest matches
3. Confirm environment variables are set
4. Test health endpoint manually

---

**Ready to deploy? Start with STEP 1!** 🚀
