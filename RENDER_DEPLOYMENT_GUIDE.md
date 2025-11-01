# 🚀 TX PREDICTIVE INTELLIGENCE - RENDER DEPLOYMENT GUIDE

**Date:** October 25, 2025  
**Version:** 2.1  
**Deployment Method:** Docker Image from Docker Hub

---

## 🎯 DEPLOYMENT STRATEGY

**Simple & Reliable:**
1. Build Docker image in WSL (Linux)
2. Push to Docker Hub
3. Deploy on Render using the Docker image
4. No GitHub builds, no complications!

---

## 📋 PREREQUISITES

### **1. Docker Hub Account**
- Create account at: https://hub.docker.com/
- Remember your username (you'll need it)

### **2. WSL with Docker**
- ✅ Already installed and working
- Docker version: 28.5.1

### **3. Render Account**
- Create account at: https://render.com/
- Free tier available

---

## 🔨 STEP 1: BUILD & PUSH DOCKER IMAGE

### **In Windows (PowerShell or CMD):**

```powershell
# Navigate to project directory
cd "C:\Users\S\TX BACK\tx-predictive-intelligence"

# Run build script in WSL
wsl ./build-and-push-docker.sh
```

### **What the script does:**
1. ✅ Asks for your Docker Hub username
2. ✅ Checks Docker login (prompts if needed)
3. ✅ Builds Docker image (takes 5-10 minutes)
4. ✅ Tags image with version and 'latest'
5. ✅ Pushes to Docker Hub
6. ✅ Shows deployment instructions

### **Expected Output:**
```
🐳 TX Predictive Intelligence - Docker Build & Push for Render
================================================================

Configuration:
  Docker Hub User: YOUR_USERNAME
  Image Name: tx-predictive-intelligence
  Full Image: YOUR_USERNAME/tx-predictive-intelligence
  Version Tag: 20251025-162000
  Latest Tag: latest

✅ Docker Hub login confirmed

Building Docker image...
This may take 5-10 minutes...

✅ Docker image built successfully!

Image size: 1.2GB

Pushing to Docker Hub...

🎉 Successfully pushed to Docker Hub!

Images available at:
  - YOUR_USERNAME/tx-predictive-intelligence:20251025-162000
  - YOUR_USERNAME/tx-predictive-intelligence:latest
```

---

## 🌐 STEP 2: DEPLOY ON RENDER

### **A. Create New Web Service**

1. Go to https://render.com/dashboard
2. Click **"New +"** → **"Web Service"**
3. Select **"Deploy an existing image from a registry"**

### **B. Configure Docker Image**

**Image URL:**
```
YOUR_USERNAME/tx-predictive-intelligence:latest
```

Replace `YOUR_USERNAME` with your Docker Hub username.

**Example:**
```
johndoe/tx-predictive-intelligence:latest
```

### **C. Configure Service**

**Name:** `tx-predictive-intelligence`

**Region:** Choose closest to your users
- Oregon (US West)
- Ohio (US East)
- Frankfurt (Europe)
- Singapore (Asia)

**Instance Type:**
- **Free:** 512MB RAM (for testing)
- **Starter:** $7/month - 512MB RAM
- **Standard:** $25/month - 2GB RAM ⭐ **Recommended**
- **Pro:** $85/month - 4GB RAM

**Port:** `5000`

### **D. Environment Variables**

Click **"Add Environment Variable"** and add these:

#### **Required:**

```bash
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-change-this
PORT=5000
```

#### **Database (Render PostgreSQL):**

If using Render's PostgreSQL:
```bash
DATABASE_URL=${{postgres.DATABASE_URL}}
```

Or external database:
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

#### **Optional API Keys (for enhanced features):**

```bash
FINNHUB_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here
```

#### **Optional Monitoring:**

```bash
SENTRY_DSN=your_sentry_dsn
```

#### **CORS Configuration:**

```bash
CORS_ORIGINS=*
```

Or specific domains:
```bash
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### **E. Health Check Path**

```
/health
```

### **F. Deploy!**

Click **"Create Web Service"**

Render will:
1. Pull your Docker image from Docker Hub
2. Start the container
3. Run health checks
4. Assign a URL (e.g., `https://tx-predictive-intelligence.onrender.com`)

---

## 🔄 UPDATING YOUR DEPLOYMENT

### **When you make code changes:**

```powershell
# 1. Navigate to project
cd "C:\Users\S\TX BACK\tx-predictive-intelligence"

# 2. Commit changes to Git (optional but recommended)
git add .
git commit -m "Your changes"
git push origin main

# 3. Build and push new Docker image
wsl ./build-and-push-docker.sh

# 4. In Render dashboard:
#    - Go to your service
#    - Click "Manual Deploy" → "Deploy latest commit"
#    - Or enable "Auto-Deploy" to deploy on image updates
```

---

## 📊 MONITORING YOUR DEPLOYMENT

### **Render Dashboard:**
- View logs in real-time
- Monitor CPU/Memory usage
- Check deployment history
- View metrics

### **Health Check:**
```bash
curl https://your-app.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-25T16:00:00",
  "version": "2.1"
}
```

### **API Endpoints:**
```bash
# Test pattern detection
curl -X POST https://your-app.onrender.com/api/patterns/detect-dual-mode \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "timeframe": "1d",
    "mode": "hybrid_pro"
  }'
```

---

## 🗄️ DATABASE SETUP (OPTIONAL)

### **Option 1: Render PostgreSQL (Recommended)**

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Choose plan:
   - **Free:** 90 days, 1GB storage
   - **Starter:** $7/month, 1GB storage
   - **Standard:** $20/month, 10GB storage
3. Copy the **Internal Database URL**
4. Add to your web service environment variables:
   ```bash
   DATABASE_URL=${{postgres.DATABASE_URL}}
   ```

### **Option 2: External Database**

Use any PostgreSQL provider:
- Supabase (free tier available)
- ElephantSQL
- AWS RDS
- DigitalOcean Managed Database

Add connection string:
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

---

## 💰 COST ESTIMATION

### **Render Pricing:**

**Free Tier:**
- Web Service: Free (spins down after 15 min inactivity)
- PostgreSQL: Free for 90 days
- **Total:** $0/month

**Starter:**
- Web Service: $7/month (always on)
- PostgreSQL: $7/month
- **Total:** $14/month

**Production (Recommended):**
- Web Service: $25/month (2GB RAM)
- PostgreSQL: $20/month (10GB)
- **Total:** $45/month

**High Traffic:**
- Web Service: $85/month (4GB RAM)
- PostgreSQL: $50/month (50GB)
- **Total:** $135/month

---

## 🔐 SECURITY CHECKLIST

Before going live:

- [ ] Changed SECRET_KEY to random string
- [ ] Set strong database password
- [ ] Configured CORS_ORIGINS (not *)
- [ ] Added API keys securely
- [ ] Enabled HTTPS (automatic on Render)
- [ ] Set up monitoring (Sentry)
- [ ] Configured rate limiting
- [ ] Reviewed environment variables
- [ ] Tested all endpoints
- [ ] Set up database backups

---

## 🐛 TROUBLESHOOTING

### **Issue: Build fails in WSL**

```bash
# Check Docker is running
wsl docker ps

# If not running, start Docker Desktop on Windows
# Make sure "Use WSL 2 based engine" is enabled in Docker Desktop settings
```

### **Issue: Push to Docker Hub fails**

```bash
# Login to Docker Hub
wsl docker login

# Enter your Docker Hub username and password
# Then run build script again
```

### **Issue: Render deployment fails**

1. Check logs in Render dashboard
2. Verify image URL is correct
3. Check environment variables are set
4. Verify port is set to 5000
5. Check health check path is `/health`

### **Issue: Service is slow on free tier**

- Free tier spins down after 15 min inactivity
- First request after spin-down takes 30-60 seconds
- Upgrade to Starter ($7/month) for always-on service

### **Issue: Database connection fails**

```bash
# Check DATABASE_URL format
# Should be: postgresql://user:pass@host:5432/dbname

# For Render PostgreSQL, use:
DATABASE_URL=${{postgres.DATABASE_URL}}
```

---

## 📈 SCALING

### **Vertical Scaling (More Resources):**
- Upgrade instance type in Render dashboard
- Standard ($25/month) → Pro ($85/month) → Pro Plus ($185/month)

### **Horizontal Scaling (Multiple Instances):**
- Render doesn't support multiple instances on same service
- Use load balancer with multiple services
- Or upgrade to Render Teams/Enterprise

### **Database Scaling:**
- Upgrade PostgreSQL plan
- Add read replicas (Enterprise)
- Use connection pooling

---

## 🎯 QUICK REFERENCE

### **Build & Deploy:**
```powershell
# Build and push
wsl ./build-and-push-docker.sh

# Then in Render: Manual Deploy → Deploy latest commit
```

### **View Logs:**
```bash
# In Render dashboard: Logs tab
# Or use Render CLI
```

### **Update Environment Variables:**
```bash
# Render dashboard → Environment → Add/Edit variables
# Click "Save Changes" to redeploy
```

### **Custom Domain:**
```bash
# Render dashboard → Settings → Custom Domain
# Add your domain (e.g., api.yourdomain.com)
# Update DNS records as instructed
```

---

## 📞 SUPPORT

### **Render Support:**
- Documentation: https://render.com/docs
- Community: https://community.render.com/
- Status: https://status.render.com/

### **Docker Hub:**
- Documentation: https://docs.docker.com/
- Support: https://hub.docker.com/support/

### **TX Backend Issues:**
- Check logs in Render dashboard
- Review DOCKER_DEPLOYMENT.md
- Check GitHub repository

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] Docker Hub account created
- [ ] Docker image built and pushed
- [ ] Render account created
- [ ] Web service created on Render
- [ ] Docker image URL configured
- [ ] Environment variables set
- [ ] Database configured (if needed)
- [ ] Health check configured
- [ ] Service deployed successfully
- [ ] Health endpoint tested
- [ ] API endpoints tested
- [ ] Custom domain configured (optional)
- [ ] Monitoring set up (optional)

---

## 🎉 SUCCESS!

Once deployed, your TX Predictive Intelligence backend will be live at:

```
https://your-service-name.onrender.com
```

**Test it:**
```bash
curl https://your-service-name.onrender.com/health
```

**Use it:**
- Connect your frontend
- Start making API calls
- Serve real users!

---

**Last Updated:** October 25, 2025  
**Version:** 2.1  
**Status:** ✅ Ready to Deploy
