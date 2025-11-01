#!/bin/bash

# ============================================
# TX Predictive Intelligence - Build with Retry
# Handles network timeouts during package installation
# ============================================

set -e

echo "🚀 TX Predictive Intelligence - Optimized Build"
echo "================================================"
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

# Check Docker Hub login
echo -e "${BLUE}Checking Docker Hub login...${NC}"
if ! docker info | grep -q "Username: ${DOCKER_USERNAME}"; then
    echo -e "${YELLOW}Not logged in to Docker Hub${NC}"
    docker login
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Docker login failed${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✅ Docker Hub login confirmed${NC}"
echo ""

# Build with optimized settings
echo -e "${YELLOW}Building Docker image with network optimizations...${NC}"
echo "This may take 10-15 minutes..."
echo ""

# Use BuildKit with increased timeout and parallel downloads
export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain

docker build \
    --tag "${FULL_IMAGE_NAME}:${VERSION}" \
    --tag "${FULL_IMAGE_NAME}:${LATEST_TAG}" \
    --platform linux/amd64 \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --build-arg PIP_DEFAULT_TIMEOUT=300 \
    --build-arg PIP_RETRIES=5 \
    --network=host \
    --file Dockerfile \
    .

BUILD_EXIT_CODE=$?

if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
    echo ""
    
    # Show image size
    IMAGE_SIZE=$(docker images "${FULL_IMAGE_NAME}:${LATEST_TAG}" --format "{{.Size}}")
    echo "Image size: ${IMAGE_SIZE}"
    echo ""
    
    # Push to Docker Hub
    echo -e "${YELLOW}Pushing to Docker Hub...${NC}"
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
    
    echo ""
    echo -e "${GREEN}🎉 SUCCESS! TX image deployed!${NC}"
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
    echo "✨ Deploy to Render:"
    echo "  Image URL: ${FULL_IMAGE_NAME}:${LATEST_TAG}"
    echo ""
    
else
    echo ""
    echo -e "${RED}❌ Docker build failed!${NC}"
    echo ""
    echo -e "${YELLOW}Common fixes:${NC}"
    echo "1. Check your internet connection"
    echo "2. Try again (network timeouts are temporary)"
    echo "3. Run: docker system prune -a (if disk space is low)"
    echo ""
    exit 1
fi
