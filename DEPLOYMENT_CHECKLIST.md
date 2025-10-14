# 🚀 TX BACKEND DEPLOYMENT CHECKLIST

## ✅ PRE-DEPLOYMENT

### 1. Environment Variables (Render Dashboard)
- [ ] `DATABASE_URL` - Supabase connection string
- [ ] `SUPABASE_URL` - Your Supabase project URL
- [ ] `SUPABASE_KEY` - Your Supabase anon/service key
- [ ] `SENTRY_DSN` - Sentry error tracking (optional)
- [ ] `FRONTEND_URL` - Your frontend URL for CORS
- [ ] `TWITTER_BEARER_TOKEN` - Twitter API (optional)
- [ ] `ENABLE_BACKGROUND_WORKERS` - Set to `true`

### 2. Database Setup (Supabase)
- [ ] Run `supabase_complete_setup.sql` in Supabase SQL Editor
- [ ] Verify tables created: `pattern_detections`, `alerts`, `paper_trades`, `model_predictions`
- [ ] (Optional) Run `add_trade_outcomes_table.sql` for ML training

### 3. Code Status
- [ ] All fixes pushed to GitHub
- [ ] No syntax errors
- [ ] All imports available in `requirements.txt`

---

## 🔧 COMMON ISSUES & FIXES

### Issue 1: 503 Server Unavailable

**Causes:**
1. **Render free tier spin-down** - Service sleeps after 15 min inactivity
2. **Application crash on startup** - Check Render logs
3. **Missing environment variables** - Check Render dashboard

**Fix:**
1. Go to Render dashboard → Your service → Logs
2. Look for startup errors
3. If "spinning down", just wait 30-60 seconds and retry
4. If crash, check error message and fix code

### Issue 2: Database Connection Errors

**Error:** `relation "X" does not exist`

**Fix:**
1. Go to Supabase SQL Editor
2. Run `supabase_complete_setup.sql`
3. Verify tables exist in Supabase Table Editor

### Issue 3: Import Errors

**Error:** `No module named 'X'`

**Fix:**
1. Check `requirements.txt` has the package
2. Trigger Render redeploy (push a commit)
3. Check Render build logs for install errors

### Issue 4: CORS Errors (Frontend)

**Error:** `Access-Control-Allow-Origin`

**Fix:**
1. Set `FRONTEND_URL` environment variable in Render
2. Value should be your frontend URL (e.g., `https://tx-figma-frontend.onrender.com`)
3. Redeploy

### Issue 5: Rate Limiting

**Error:** `429 Too Many Requests`

**Fix:**
- Wait 1 minute
- Reduce request frequency
- Endpoints have different limits (check main.py)

---

## 🧪 TESTING PROCEDURE

### Step 1: Wait for Service to Wake Up
```powershell
# Run this first - it will wake up the service
Invoke-RestMethod -Uri "https://tx-predictive-intelligence.onrender.com/health"
```

**Expected:** `{"status":"ok","timestamp":"..."}`

**If 503:** Wait 30-60 seconds (service is waking up from sleep)

### Step 2: Run Health Diagnostic
```powershell
.\check_backend_health.ps1
```

**Expected:** All tests pass ✅

### Step 3: Run API Tests
```powershell
.\test_api.ps1
```

**Expected:** Most tests pass (some may fail if no data yet)

---

## 📊 MONITORING

### Check Render Logs
```
Render Dashboard → Your Service → Logs
```

**Look for:**
- ✅ `Sentry initialized`
- ✅ `Database connection established`
- ✅ `Background scanner started`
- ✅ `ML retrain worker started`
- ✅ `Listening at: http://0.0.0.0:10000`
- ✅ `Your service is live 🎉`

**Red flags:**
- ❌ `Failed to create database engine`
- ❌ `No module named 'X'`
- ❌ `relation "X" does not exist`
- ❌ Python traceback errors

### Check Sentry (if configured)
```
https://sentry.io → Your Project → Issues
```

**Look for:**
- New errors after deployment
- Error frequency
- Error patterns

---

## 🚨 EMERGENCY FIXES

### If Backend Won't Start

1. **Check Render Logs** - Find the error
2. **Fix locally** - Test with `python main.py`
3. **Push fix** - `git push origin main`
4. **Wait for redeploy** - 2-5 minutes

### If Database Errors

1. **Verify DATABASE_URL** - Check Render environment variables
2. **Test connection** - Use Supabase dashboard
3. **Recreate tables** - Run `supabase_complete_setup.sql` again

### If Still Broken

1. **Check requirements.txt** - All packages listed?
2. **Check Python version** - Should be 3.11+
3. **Check Render build logs** - Any install failures?
4. **Rollback** - Revert to last working commit

---

## ✅ SUCCESS CRITERIA

Your backend is working if:

- [ ] Health endpoint returns 200 OK
- [ ] Render logs show "Your service is live 🎉"
- [ ] No errors in Render logs
- [ ] Database connected (check logs)
- [ ] Workers started (check logs)
- [ ] API endpoints respond (test with PowerShell)
- [ ] No 503 errors (after wake-up period)

---

## 📞 QUICK REFERENCE

### Render Dashboard
https://dashboard.render.com

### Supabase Dashboard
https://supabase.com/dashboard

### Backend URL
https://tx-predictive-intelligence.onrender.com

### Test Commands
```powershell
# Health check
Invoke-RestMethod -Uri "https://tx-predictive-intelligence.onrender.com/health"

# Full diagnostic
.\check_backend_health.ps1

# API tests
.\test_api.ps1
```

---

## 🎯 NEXT STEPS AFTER DEPLOYMENT

1. **Connect Frontend** - Update frontend API URL
2. **Test Integration** - Frontend → Backend communication
3. **Monitor Errors** - Check Sentry for issues
4. **Optimize** - Add caching, improve performance
5. **Scale** - Upgrade Render plan if needed
