#!/bin/bash

# ============================================
# TX Predictive Intelligence - Fresh Build & Deploy
# Cleans up old images, builds fresh, and pushes to Docker Hub
# ============================================

set -e

echo "🚀 TX Predictive Intelligence - Fresh Build & Deploy"
echo "====================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
DOCKER_USERNAME="${DOCKER_USERNAME:-jeanpaulkadusimanegaberobert1}"
IMAGE_NAME="tx-predictive-intelligence"
VERSION=$(date +%Y%m%d-%H%M%S)
LATEST_TAG="latest"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}"

echo -e "${BLUE}Configuration:${NC}"
echo "  Docker Hub User: ${DOCKER_USERNAME}"
echo "  Image Name: ${IMAGE_NAME}"
echo "  Full Image: ${FULL_IMAGE_NAME}"
echo "  Version Tag: ${VERSION}"
echo ""

# ============================================
# STEP 1: CLEANUP OLD IMAGES
# ============================================

echo -e "${YELLOW}STEP 1: Cleanup Old Docker Images${NC}"
echo "This will free up ~12GB of storage"
echo ""
echo -n "Delete all old Docker images? (yes/no): "
read CLEANUP_CONFIRM

if [ "$CLEANUP_CONFIRM" = "yes" ]; then
    echo ""
    echo -e "${BLUE}Cleaning up old images...${NC}"
    echo ""
    
    # Remove old TX images specifically
    echo "Removing old TX backend images..."
    docker rmi jeanpaulkadusimanegaberobert1/tx-backend:latest 2>/dev/null || true
    docker rmi jeanpaulkadusimanegaberobert1/tx-backend:v1.0.4-render 2>/dev/null || true
    docker rmi jeanpaulkadusimanegaberobert1/tx-backend:v1.0.3 2>/dev/null || true
    docker rmi jeanpaulkadusimanegaberobert1/tx-backend:v1.0.3-20251018-225528 2>/dev/null || true
    docker rmi tx-backend:latest 2>/dev/null || true
    docker rmi tx-backend:v1.0.6 2>/dev/null || true
    
    # Remove dangling images
    echo "Removing dangling images..."
    docker image prune -f
    
    # Remove all unused images
    echo "Removing all unused images..."
    docker image prune -a -f
    
    # Remove build cache
    echo "Removing build cache..."
    docker builder prune -a -f
    
    echo ""
    echo -e "${GREEN}✅ Cleanup complete!${NC}"
    echo ""
    echo "Disk space status:"
    docker system df
    echo ""
else
    echo -e "${YELLOW}Skipping cleanup...${NC}"
    echo ""
fi

# ============================================
# STEP 2: CHECK DOCKER HUB LOGIN
# ============================================

echo -e "${YELLOW}STEP 2: Docker Hub Login${NC}"
echo ""

if ! docker info | grep -q "Username: ${DOCKER_USERNAME}"; then
    echo -e "${YELLOW}Not logged in to Docker Hub${NC}"
    echo "Please login to Docker Hub:"
    docker login
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Docker login failed${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Docker Hub login confirmed${NC}"
echo ""

# ============================================
# STEP 3: BUILD FRESH IMAGE
# ============================================

echo -e "${YELLOW}STEP 3: Build Fresh Docker Image${NC}"
echo "Building with ALL new features:"
echo "  ✅ Advanced Raw Data Analysis (Correlation, Order Flow, Microstructure, Regime)"
echo "  ✅ Dual-Mode AI (HYBRID PRO + AI ELITE)"
echo "  ✅ Real-Time Sentiment Analysis"
echo "  ✅ 50+ Pattern Recognition"
echo "  ✅ 10 World-Class Trading Skills"
echo "  ✅ 72 API Endpoints"
echo ""
echo "This may take 5-10 minutes..."
echo ""

docker build \
    --tag "${FULL_IMAGE_NAME}:${VERSION}" \
    --tag "${FULL_IMAGE_NAME}:${LATEST_TAG}" \
    --platform linux/amd64 \
    --no-cache \
    --file Dockerfile \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
    echo ""
    
    # Show image size
    IMAGE_SIZE=$(docker images "${FULL_IMAGE_NAME}:${LATEST_TAG}" --format "{{.Size}}")
    echo "Image size: ${IMAGE_SIZE}"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Docker build failed!${NC}"
    exit 1
fi

# ============================================
# STEP 4: PUSH TO DOCKER HUB
# ============================================

echo -e "${YELLOW}STEP 4: Push to Docker Hub${NC}"
echo ""

echo "Pushing ${FULL_IMAGE_NAME}:${VERSION}..."
docker push "${FULL_IMAGE_NAME}:${VERSION}"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to push versioned image${NC}"
    exit 1
fi

echo ""
echo "Pushing ${FULL_IMAGE_NAME}:${LATEST_TAG}..."
docker push "${FULL_IMAGE_NAME}:${LATEST_TAG}"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to push latest image${NC}"
    exit 1
fi

# ============================================
# SUCCESS!
# ============================================

echo ""
echo -e "${GREEN}🎉 SUCCESS! Fresh TX image deployed!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📦 Images available at:"
echo "  - ${FULL_IMAGE_NAME}:${VERSION}"
echo "  - ${FULL_IMAGE_NAME}:${LATEST_TAG}"
echo ""
echo "🔗 Docker Hub URL:"
echo "  https://hub.docker.com/r/${DOCKER_USERNAME}/${IMAGE_NAME}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 RENDER DEPLOYMENT INSTRUCTIONS:"
echo ""
echo "1. Go to: https://dashboard.render.com/"
echo "2. Click 'New +' → 'Web Service'"
echo "3. Select 'Deploy an existing image from a registry'"
echo "4. Enter image URL: ${FULL_IMAGE_NAME}:${LATEST_TAG}"
echo "5. Configure:"
echo "   - Name: tx-predictive-intelligence"
echo "   - Region: Choose closest to your users"
echo "   - Instance Type: Starter (\$7/month) or higher"
echo "   - Port: 10000"
echo "6. Add Environment Variables:"
echo "   PORT=10000"
echo "   FLASK_ENV=production"
echo "   (Optional: POLYGON_API_KEY, FINNHUB_API_KEY, NEWS_API_KEY)"
echo "7. Click 'Deploy'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✨ NEW FEATURES IN THIS BUILD:"
echo ""
echo "🔥 Advanced Raw Data Analysis:"
echo "   • Multi-Asset Correlation (POST /api/analysis/correlations)"
echo "   • Order Flow Imbalance (GET /api/analysis/order-flow/<symbol>)"
echo "   • Market Microstructure (GET /api/analysis/microstructure/<symbol>)"
echo "   • Regime Detection (GET /api/analysis/regime/<symbol>)"
echo "   • Comprehensive Analysis (GET /api/analysis/comprehensive/<symbol>)"
echo ""
echo "🎯 Total: 72 API Endpoints"
echo "📊 100% Real-Time Data (Zero Mocks)"
echo "🚀 Production-Ready"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}Ready to dominate the market! 🎯${NC}"
echo ""
