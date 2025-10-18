#!/bin/bash
# ============================================
# TX BACKEND - CLEAN REBUILD SCRIPT
# ============================================

set -e  # Exit on any error

echo "=========================================="
echo "TX BACKEND - CLEAN REBUILD"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Clean old images
echo -e "${YELLOW}[1/5] Cleaning old images...${NC}"
docker rmi -f tx-backend:latest 2>/dev/null || true
docker rmi -f jeanpaulkadusimanegaberobert1/tx-backend:latest 2>/dev/null || true
docker rmi -f jeanpaulkadusimanegaberobert1/tx-backend:v1.0.1 2>/dev/null || true
docker rmi -f jeanpaulkadusimanegaberobert1/tx-backend:v1.0.2 2>/dev/null || true
docker rmi -f jeanpaulkadusimanegaberobert1/tx-backend:v1.0.3 2>/dev/null || true
echo -e "${GREEN}✓ Old images removed${NC}"
echo ""

# Step 2: Clean build cache
echo -e "${YELLOW}[2/5] Cleaning build cache...${NC}"
docker builder prune -af
echo -e "${GREEN}✓ Build cache cleaned${NC}"
echo ""

# Step 3: Build new image
echo -e "${YELLOW}[3/5] Building new image (this will take 5-10 minutes)...${NC}"
docker build --no-cache -t tx-backend:latest -f Dockerfile.full .
echo -e "${GREEN}✓ Image built successfully${NC}"
echo ""

# Step 4: Tag image
echo -e "${YELLOW}[4/5] Tagging image as v1.0.3...${NC}"
docker tag tx-backend:latest jeanpaulkadusimanegaberobert1/tx-backend:v1.0.3
docker tag tx-backend:latest jeanpaulkadusimanegaberobert1/tx-backend:latest
echo -e "${GREEN}✓ Image tagged${NC}"
echo ""

# Step 5: Push to Docker Hub
echo -e "${YELLOW}[5/5] Pushing to Docker Hub...${NC}"
docker push jeanpaulkadusimanegaberobert1/tx-backend:v1.0.3
docker push jeanpaulkadusimanegaberobert1/tx-backend:latest
echo -e "${GREEN}✓ Image pushed to Docker Hub${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}✓ REBUILD COMPLETE!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Go to Railway dashboard"
echo "2. Update Docker image to: jeanpaulkadusimanegaberobert1/tx-backend:v1.0.3"
echo "3. Deploy"
echo ""
echo "Your image digest:"
docker images --digests jeanpaulkadusimanegaberobert1/tx-backend:v1.0.3 | grep v1.0.3
