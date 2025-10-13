# 🔒 CORS CONFIGURATION GUIDE

**TX Predictive Intelligence - Secure CORS Setup**

---

## ✅ WHAT WAS CHANGED

### Before (INSECURE):
```python
# Hardcoded URLs including:
- lovable.app domains
- recipevault domains
- tx-figma domains
- Wildcard regex patterns
- ALLOW_ALL_CORS flag
```

### After (SECURE):
```python
# Only uses environment variable
CORS_ORIGINS=your-frontend-domain.com
```

**Result:** No hardcoded URLs, full control via environment variables

---

## 🚀 HOW IT WORKS NOW

### Production (Render):
```bash
# Set this in Render Dashboard → Environment
CORS_ORIGINS=https://your-frontend-domain.com
```

**Backend allows ONLY:**
- `https://your-frontend-domain.com`

### Local Development:
```bash
# No environment variable needed
# Automatically defaults to:
```

**Backend allows ONLY:**
- `http://localhost:3000`
- `http://localhost:5173`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

---

## 📋 SETUP INSTRUCTIONS

### Step 1: Deploy Your Frontend

**Deploy to any platform:**
- Vercel: `https://your-app.vercel.app`
- Netlify: `https://your-app.netlify.app`
- Render: `https://your-app.onrender.com`
- Custom domain: `https://www.your-domain.com`

**Copy the URL** (you'll need it in Step 2)

---

### Step 2: Add CORS_ORIGINS to Render

1. Go to https://dashboard.render.com
2. Click your backend service (tx-predictive-intelligence)
3. Go to "Environment" tab
4. Click "Add Environment Variable"
5. Add:

```bash
Key: CORS_ORIGINS
Value: https://your-frontend-domain.com
```

**For multiple domains (comma-separated):**
```bash
Key: CORS_ORIGINS
Value: https://your-app.vercel.app,https://www.your-domain.com,https://your-domain.com
```

6. Click "Save Changes"
7. Render will auto-redeploy

---

### Step 3: Verify CORS is Working

**Test from your frontend:**

```javascript
// In your frontend code
fetch('https://your-backend.onrender.com/api/alerts')
  .then(res => res.json())
  .then(data => console.log('Success!', data))
  .catch(err => console.error('CORS Error:', err));
```

**Expected result:**
- ✅ Success: Data returned
- ❌ CORS Error: Check CORS_ORIGINS value

---

## 🧪 TESTING CORS

### Test 1: From Allowed Origin (Should Work)

```bash
# From your frontend domain
curl -H "Origin: https://your-frontend-domain.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     https://your-backend.onrender.com/api/alerts

# Expected response headers:
# Access-Control-Allow-Origin: https://your-frontend-domain.com
# Access-Control-Allow-Credentials: true
```

---

### Test 2: From Blocked Origin (Should Fail)

```bash
# From random domain
curl -H "Origin: https://evil-site.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     https://your-backend.onrender.com/api/alerts

# Expected: No Access-Control-Allow-Origin header
# Browser will block the request
```

---

## 🔧 COMMON SCENARIOS

### Scenario 1: Single Frontend Domain

```bash
# Production only
CORS_ORIGINS=https://tx-app.vercel.app
```

**Allows:**
- ✅ `https://tx-app.vercel.app`

**Blocks:**
- ❌ `http://tx-app.vercel.app` (http vs https)
- ❌ `https://www.tx-app.vercel.app` (www subdomain)
- ❌ All other domains

---

### Scenario 2: Multiple Domains (Production + Staging)

```bash
CORS_ORIGINS=https://tx-app.vercel.app,https://tx-staging.vercel.app
```

**Allows:**
- ✅ `https://tx-app.vercel.app`
- ✅ `https://tx-staging.vercel.app`

**Blocks:**
- ❌ All other domains

---

### Scenario 3: Custom Domain + Subdomain

```bash
CORS_ORIGINS=https://tx-app.com,https://www.tx-app.com,https://app.tx-app.com
```

**Allows:**
- ✅ `https://tx-app.com`
- ✅ `https://www.tx-app.com`
- ✅ `https://app.tx-app.com`

**Blocks:**
- ❌ All other domains

---

### Scenario 4: Local Development Only

```bash
# Don't set CORS_ORIGINS at all
# Uses default localhost
```

**Allows:**
- ✅ `http://localhost:3000`
- ✅ `http://localhost:5173`
- ✅ `http://127.0.0.1:3000`
- ✅ `http://127.0.0.1:5173`

**Blocks:**
- ❌ All production domains

---

## 🚨 TROUBLESHOOTING

### Issue: "CORS Error: No 'Access-Control-Allow-Origin' header"

**Cause:** Your frontend domain is not in CORS_ORIGINS

**Fix:**
1. Check your frontend URL (exact match required)
2. Add to CORS_ORIGINS in Render
3. Redeploy backend
4. Test again

---

### Issue: "CORS works on localhost but not production"

**Cause:** CORS_ORIGINS not set in Render

**Fix:**
1. Go to Render Dashboard → Environment
2. Add CORS_ORIGINS with your production frontend URL
3. Save (auto-redeploys)
4. Test from production frontend

---

### Issue: "CORS works for GET but not POST"

**Cause:** Preflight OPTIONS request failing

**Fix:**
1. Verify CORS_ORIGINS includes your domain
2. Check browser console for exact error
3. Ensure `supports_credentials=True` in main.py (already set)
4. Test OPTIONS request manually (see Testing section)

---

### Issue: "www.domain.com works but domain.com doesn't"

**Cause:** CORS requires exact match (including www)

**Fix:**
```bash
# Add both versions
CORS_ORIGINS=https://domain.com,https://www.domain.com
```

---

### Issue: "CORS error only on WebSocket"

**Cause:** WebSocket uses same CORS_ORIGINS

**Fix:**
1. Verify CORS_ORIGINS is set correctly
2. WebSocket URL must match: `wss://backend.com` not `ws://`
3. Check browser console for exact error

---

## 🔒 SECURITY BEST PRACTICES

### ✅ DO:
- Use HTTPS in production (not HTTP)
- List only your actual frontend domains
- Use exact domain matches (no wildcards)
- Keep CORS_ORIGINS in environment variables (not code)
- Update CORS_ORIGINS when frontend domain changes

### ❌ DON'T:
- Don't use `ALLOW_ALL_CORS=true` in production
- Don't use wildcards (`*.domain.com`)
- Don't hardcode domains in code
- Don't include http:// in production CORS_ORIGINS
- Don't forget to add www and non-www versions if needed

---

## 📊 CURRENT CONFIGURATION

### Code Location:
`main.py` lines 215-230

### Logic:
```python
if CORS_ORIGINS environment variable is set:
    Use those domains (comma-separated)
else:
    Use localhost only (local development)
```

### No Hardcoded URLs:
- ✅ All lovable.app URLs removed
- ✅ All recipevault URLs removed
- ✅ All tx-figma URLs removed
- ✅ All wildcard regex removed
- ✅ ALLOW_ALL_CORS flag removed

### Result:
**100% controlled by environment variables** 🔒

---

## 🎯 QUICK REFERENCE

### Environment Variable Format:
```bash
# Single domain
CORS_ORIGINS=https://frontend.com

# Multiple domains (comma-separated, no spaces)
CORS_ORIGINS=https://frontend.com,https://www.frontend.com

# Multiple domains (with spaces - will be trimmed)
CORS_ORIGINS=https://frontend.com, https://www.frontend.com
```

### Where to Set:
- **Render:** Dashboard → Service → Environment → Add Variable
- **Local:** Don't set (uses localhost default)

### When to Update:
- Frontend domain changes
- Add staging environment
- Add custom domain
- Add www subdomain

---

## ✅ VERIFICATION CHECKLIST

**After setting CORS_ORIGINS:**

- [ ] Environment variable added in Render
- [ ] Value includes https:// (not http://)
- [ ] Value matches exact frontend URL
- [ ] Multiple domains separated by commas
- [ ] Backend redeployed (auto after env change)
- [ ] Tested from frontend (fetch/axios works)
- [ ] No CORS errors in browser console
- [ ] WebSocket connects successfully

---

## 🎉 YOU'RE SECURE!

**Your CORS configuration is now:**
- ✅ Secure (no hardcoded URLs)
- ✅ Flexible (environment variable)
- ✅ Production-ready (exact domain matching)
- ✅ Easy to update (just change env var)

**No more security risks from hardcoded domains!** 🔒
