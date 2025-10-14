# ⚡ QUICK DEPLOY - 5 Minutes

## 🎯 Goal
Enable frontend at `https://tx-figma-frontend.onrender.com` to connect to backend.

---

## 📋 3-Step Deploy

### Step 1: Set Environment Variable (2 min)
1. Go to: https://dashboard.render.com
2. Find: **tx-predictive-intelligence**
3. Click: **Environment** tab
4. Add variable:
   ```
   Key:   CORS_ORIGINS
   Value: https://tx-figma-frontend.onrender.com,http://localhost:3000,http://localhost:5173
   ```
5. Click: **Save Changes**

### Step 2: Deploy (1 min)
Click: **Manual Deploy** → **Deploy latest commit**

### Step 3: Verify (2 min)
```bash
curl https://tx-predictive-intelligence.onrender.com/health
```

Expected: `{"status":"ok","timestamp":"..."}`

---

## ✅ Success Indicators

- Render status: **Live** (green)
- Health check: **Passing** (green checkmark)
- Logs: No errors
- Test: `curl` returns 200

---

## 🧪 Quick Test

Run PowerShell script:
```powershell
.\test_cors_integration.ps1
```

Or manual test:
```bash
curl -H "Origin: https://tx-figma-frontend.onrender.com" \
  https://tx-predictive-intelligence.onrender.com/api/market-scan?type=trending
```

---

## 🎉 Done!

Frontend will now:
- ✅ Connect to backend
- ✅ No CORS errors
- ✅ WebSocket working
- ✅ Real-time data

---

## 📚 Full Documentation

- **Detailed Guide:** FRONTEND_INTEGRATION_GUIDE.md
- **Changes Summary:** CORS_CHANGES_SUMMARY.md
- **Deploy Instructions:** DEPLOYMENT_INSTRUCTIONS.md
- **Test Script:** test_cors_integration.ps1

---

**Total Time:** 5 minutes
**Difficulty:** Easy
**Risk:** Low

**Deploy now! 🚀**
