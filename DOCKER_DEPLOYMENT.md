# 🐳 TX PREDICTIVE INTELLIGENCE - DOCKER DEPLOYMENT GUIDE

**Date:** October 25, 2025  
**Version:** 2.1 (Dual-Mode with Sentiment Analysis)  
**Status:** ✅ Production Ready

---

## 📋 TABLE OF CONTENTS

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Docker Setup](#docker-setup)
4. [Docker Compose Setup](#docker-compose-setup)
5. [Environment Configuration](#environment-configuration)
6. [Building Images](#building-images)
7. [Running Containers](#running-containers)
8. [Deployment Options](#deployment-options)
9. [Monitoring & Logs](#monitoring--logs)
10. [Troubleshooting](#troubleshooting)

---

## 🚀 QUICK START

### **Option 1: Docker Compose (Recommended)**

```bash
# 1. Clone repository
git clone <your-repo-url>
cd tx-predictive-intelligence

# 2. Create environment file
cp env.example .env
# Edit .env with your configuration

# 3. Start all services
docker-compose up -d

# 4. Check health
curl http://localhost:5000/health
```

### **Option 2: Standalone Docker**

```bash
# 1. Build image
./docker-build.sh

# 2. Run container
./docker-run.sh

# 3. Check health
curl http://localhost:5000/health
```

---

## 📦 PREREQUISITES

### **Required:**
- Docker 20.10+ installed
- Docker Compose 2.0+ installed
- 2GB+ RAM available
- 10GB+ disk space

### **Optional:**
- Docker Hub account (for pushing images)
- GitHub Container Registry access
- API keys for enhanced features

### **Installation:**

**Linux/Mac:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**Windows:**
- Download Docker Desktop from https://www.docker.com/products/docker-desktop

---

## 🐳 DOCKER SETUP

### **Files Overview:**

```
tx-predictive-intelligence/
├── Dockerfile                  # Main application Dockerfile
├── Dockerfile.full            # Full build (alternative)
├── docker-compose.yml         # Multi-service orchestration
├── .dockerignore              # Files to exclude from build
├── docker-build.sh            # Build script
├── docker-push.sh             # Push script
├── docker-run.sh              # Run script
├── env.example                # Environment template
└── requirements.txt           # Python dependencies
```

---

## 🏗️ DOCKER COMPOSE SETUP

### **Services Included:**

1. **tx-backend** - Main Flask application
2. **postgres** - PostgreSQL database
3. **redis** - Caching and Celery broker
4. **celery-worker** - Background task processing
5. **celery-beat** - Scheduled tasks

### **Architecture:**

```
┌─────────────────┐
│   tx-backend    │ ← Main API (Port 5000)
│   (Flask App)   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼──────┐
│Postgres│ │  Redis  │
│  DB    │ │ Cache   │
└────────┘ └────┬────┘
                │
         ┌──────┴──────┐
         │             │
    ┌────▼────┐   ┌────▼────┐
    │ Celery  │   │ Celery  │
    │ Worker  │   │  Beat   │
    └─────────┘   └─────────┘
```

---

## ⚙️ ENVIRONMENT CONFIGURATION

### **1. Create .env File:**

```bash
cp env.example .env
```

### **2. Required Variables:**

```bash
# Flask
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-here

# Database
DATABASE_URL=postgresql://txuser:txpassword@postgres:5432/tx_intelligence

# Redis
REDIS_URL=redis://redis:6379/0
```

### **3. Optional API Keys (for enhanced features):**

```bash
# Sentiment Analysis Enhancement
FINNHUB_API_KEY=your_finnhub_key
NEWS_API_KEY=your_newsapi_key
ALPHA_VANTAGE_API_KEY=your_alphavantage_key

# Error Tracking
SENTRY_DSN=your_sentry_dsn
```

### **4. Feature Flags:**

```bash
# Enable/disable features
SENTIMENT_ANALYSIS_ENABLED=true
AI_ELITE_MODE_ENABLED=true
BACKTESTING_ENABLED=true
PAPER_TRADING_ENABLED=true
```

---

## 🔨 BUILDING IMAGES

### **Method 1: Using Build Script (Recommended)**

```bash
# Make script executable
chmod +x docker-build.sh

# Build image
./docker-build.sh
```

**Features:**
- ✅ Automatic versioning (timestamp-based)
- ✅ Tags both versioned and latest
- ✅ Shows image size
- ✅ Optional push to registry

### **Method 2: Manual Build**

```bash
# Build with Docker
docker build -t tx-predictive-intelligence:latest .

# Build with Docker Compose
docker-compose build
```

### **Method 3: Build for Specific Platform**

```bash
# For ARM64 (Apple Silicon, AWS Graviton)
docker build --platform linux/arm64 -t tx-predictive-intelligence:latest .

# For AMD64 (Intel/AMD)
docker build --platform linux/amd64 -t tx-predictive-intelligence:latest .

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t tx-predictive-intelligence:latest .
```

---

## 🚀 RUNNING CONTAINERS

### **Method 1: Docker Compose (Recommended)**

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart tx-backend
```

### **Method 2: Using Run Script**

```bash
# Make script executable
chmod +x docker-run.sh

# Run container
./docker-run.sh
```

### **Method 3: Manual Docker Run**

```bash
docker run -d \
  --name tx-backend \
  --env-file .env \
  -p 5000:5000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/models:/app/models \
  --restart unless-stopped \
  tx-predictive-intelligence:latest
```

---

## 🌐 DEPLOYMENT OPTIONS

### **Option 1: Single Server Deployment**

**Best for:** Small to medium scale, development, testing

```bash
# On your server
git clone <repo>
cd tx-predictive-intelligence
cp env.example .env
# Edit .env
docker-compose up -d
```

**Pros:**
- ✅ Simple setup
- ✅ All services on one machine
- ✅ Easy to manage

**Cons:**
- ❌ Single point of failure
- ❌ Limited scalability

---

### **Option 2: Cloud Platform Deployment**

#### **A. AWS ECS/Fargate**

```bash
# 1. Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag tx-predictive-intelligence:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/tx-predictive-intelligence:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/tx-predictive-intelligence:latest

# 2. Create ECS task definition
# 3. Create ECS service
# 4. Configure load balancer
```

#### **B. Google Cloud Run**

```bash
# 1. Build and push to GCR
gcloud builds submit --tag gcr.io/<project-id>/tx-predictive-intelligence

# 2. Deploy to Cloud Run
gcloud run deploy tx-backend \
  --image gcr.io/<project-id>/tx-predictive-intelligence \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "FLASK_ENV=production"
```

#### **C. Azure Container Instances**

```bash
# 1. Push to ACR
az acr login --name <registry-name>
docker tag tx-predictive-intelligence:latest <registry-name>.azurecr.io/tx-predictive-intelligence:latest
docker push <registry-name>.azurecr.io/tx-predictive-intelligence:latest

# 2. Deploy to ACI
az container create \
  --resource-group tx-rg \
  --name tx-backend \
  --image <registry-name>.azurecr.io/tx-predictive-intelligence:latest \
  --cpu 2 --memory 4 \
  --ports 5000 \
  --environment-variables FLASK_ENV=production
```

#### **D. DigitalOcean App Platform**

```bash
# 1. Push to Docker Hub or GHCR
docker tag tx-predictive-intelligence:latest <username>/tx-predictive-intelligence:latest
docker push <username>/tx-predictive-intelligence:latest

# 2. Create app via DigitalOcean dashboard
# 3. Configure environment variables
# 4. Deploy
```

---

### **Option 3: Kubernetes Deployment**

**Best for:** Large scale, high availability, auto-scaling

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tx-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tx-backend
  template:
    metadata:
      labels:
        app: tx-backend
    spec:
      containers:
      - name: tx-backend
        image: tx-predictive-intelligence:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: tx-secrets
              key: database-url
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: tx-backend-service
spec:
  selector:
    app: tx-backend
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f deployment.yaml
```

---

## 📊 MONITORING & LOGS

### **View Logs:**

```bash
# Docker Compose
docker-compose logs -f tx-backend
docker-compose logs -f postgres
docker-compose logs -f redis

# Standalone Docker
docker logs -f tx-backend

# Last 100 lines
docker logs --tail 100 tx-backend

# Since specific time
docker logs --since 2024-01-01T00:00:00 tx-backend
```

### **Health Checks:**

```bash
# Application health
curl http://localhost:5000/health

# Database health
docker-compose exec postgres pg_isready

# Redis health
docker-compose exec redis redis-cli ping
```

### **Resource Usage:**

```bash
# All containers
docker stats

# Specific container
docker stats tx-backend

# Disk usage
docker system df
```

### **Prometheus Metrics:**

```bash
# Metrics endpoint
curl http://localhost:5000/metrics
```

---

## 🔧 TROUBLESHOOTING

### **Issue 1: Container Won't Start**

```bash
# Check logs
docker logs tx-backend

# Common causes:
# - Missing .env file
# - Invalid DATABASE_URL
# - Port already in use
# - Insufficient resources

# Solution:
docker-compose down
docker-compose up -d
```

### **Issue 2: Database Connection Failed**

```bash
# Check if postgres is running
docker-compose ps postgres

# Check postgres logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U txuser -d tx_intelligence

# Solution:
# - Verify DATABASE_URL in .env
# - Ensure postgres container is healthy
# - Check network connectivity
```

### **Issue 3: Out of Memory**

```bash
# Check memory usage
docker stats

# Solution:
# - Increase Docker memory limit
# - Reduce number of workers
# - Add swap space
# - Scale horizontally
```

### **Issue 4: Port Already in Use**

```bash
# Find process using port 5000
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Solution:
# - Kill the process
# - Change PORT in .env
# - Use different port mapping
```

### **Issue 5: Image Build Fails**

```bash
# Clear Docker cache
docker builder prune -a

# Rebuild without cache
docker build --no-cache -t tx-predictive-intelligence:latest .

# Check disk space
docker system df
docker system prune -a
```

---

## 🔐 SECURITY BEST PRACTICES

### **1. Environment Variables:**
- ✅ Never commit .env to version control
- ✅ Use strong SECRET_KEY (32+ random characters)
- ✅ Use strong database passwords
- ✅ Rotate API keys regularly

### **2. Network Security:**
- ✅ Use internal Docker networks
- ✅ Don't expose database ports publicly
- ✅ Use HTTPS in production
- ✅ Configure firewall rules

### **3. Container Security:**
- ✅ Run as non-root user
- ✅ Use minimal base images
- ✅ Scan images for vulnerabilities
- ✅ Keep images updated

### **4. Data Security:**
- ✅ Encrypt data at rest
- ✅ Encrypt data in transit
- ✅ Regular backups
- ✅ Secure backup storage

---

## 📈 SCALING

### **Vertical Scaling (Single Container):**

```yaml
# docker-compose.yml
services:
  tx-backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### **Horizontal Scaling (Multiple Containers):**

```bash
# Scale to 3 instances
docker-compose up -d --scale tx-backend=3

# With load balancer
# Add nginx or traefik for load balancing
```

---

## 🔄 UPDATES & MAINTENANCE

### **Update Application:**

```bash
# 1. Pull latest code
git pull origin main

# 2. Rebuild image
docker-compose build tx-backend

# 3. Restart with new image
docker-compose up -d tx-backend

# 4. Verify health
curl http://localhost:5000/health
```

### **Database Migrations:**

```bash
# Run migrations
docker-compose exec tx-backend python -c "from services.db import init_db; init_db()"
```

### **Backup Database:**

```bash
# Backup
docker-compose exec postgres pg_dump -U txuser tx_intelligence > backup.sql

# Restore
docker-compose exec -T postgres psql -U txuser tx_intelligence < backup.sql
```

---

## 📚 USEFUL COMMANDS

### **Container Management:**

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Remove all
docker-compose down -v

# View running containers
docker-compose ps

# Execute command in container
docker-compose exec tx-backend bash
```

### **Image Management:**

```bash
# List images
docker images

# Remove image
docker rmi tx-predictive-intelligence:latest

# Remove unused images
docker image prune -a

# Tag image
docker tag tx-predictive-intelligence:latest myregistry/tx:v1.0
```

### **Network Management:**

```bash
# List networks
docker network ls

# Inspect network
docker network inspect tx-network

# Create network
docker network create tx-network
```

---

## 🎯 PRODUCTION CHECKLIST

Before deploying to production:

- [ ] Set FLASK_ENV=production
- [ ] Use strong SECRET_KEY
- [ ] Configure DATABASE_URL with production credentials
- [ ] Set up HTTPS/SSL
- [ ] Configure CORS_ORIGINS properly
- [ ] Set up monitoring (Sentry, Prometheus)
- [ ] Configure log aggregation
- [ ] Set up automated backups
- [ ] Configure health checks
- [ ] Set up load balancer (if scaling)
- [ ] Configure firewall rules
- [ ] Set up CI/CD pipeline
- [ ] Test disaster recovery
- [ ] Document deployment process

---

## 📞 SUPPORT

**Issues?**
- Check logs: `docker-compose logs -f`
- Check health: `curl http://localhost:5000/health`
- Review this guide
- Check GitHub issues

**Need Help?**
- Create GitHub issue
- Contact support team
- Check documentation

---

**Last Updated:** October 25, 2025  
**Version:** 2.1  
**Status:** ✅ Production Ready
