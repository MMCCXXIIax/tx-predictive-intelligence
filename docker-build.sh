#!/bin/bash

# ============================================
# TX Predictive Intelligence - Docker Build Script
# ============================================

set -e  # Exit on error

echo "🐳 TX Predictive Intelligence - Docker Build"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="tx-predictive-intelligence"
VERSION=$(date +%Y%m%d-%H%M%S)
LATEST_TAG="latest"

# Docker registry (change this to your registry)
REGISTRY="${DOCKER_REGISTRY:-}"  # e.g., "docker.io/yourusername" or "ghcr.io/yourusername"

if [ -n "$REGISTRY" ]; then
    FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}"
else
    FULL_IMAGE_NAME="${IMAGE_NAME}"
fi

echo -e "${BLUE}Building Docker image...${NC}"
echo "Image: ${FULL_IMAGE_NAME}:${VERSION}"
echo "Image: ${FULL_IMAGE_NAME}:${LATEST_TAG}"
echo ""

# Build the Docker image
docker build \
    --tag "${FULL_IMAGE_NAME}:${VERSION}" \
    --tag "${FULL_IMAGE_NAME}:${LATEST_TAG}" \
    --file Dockerfile \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
    echo ""
    echo "Tagged as:"
    echo "  - ${FULL_IMAGE_NAME}:${VERSION}"
    echo "  - ${FULL_IMAGE_NAME}:${LATEST_TAG}"
    echo ""
    
    # Show image size
    IMAGE_SIZE=$(docker images "${FULL_IMAGE_NAME}:${LATEST_TAG}" --format "{{.Size}}")
    echo "Image size: ${IMAGE_SIZE}"
    echo ""
    
    # Ask if user wants to push
    if [ -n "$REGISTRY" ]; then
        read -p "Do you want to push to registry? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}Pushing to registry...${NC}"
            docker push "${FULL_IMAGE_NAME}:${VERSION}"
            docker push "${FULL_IMAGE_NAME}:${LATEST_TAG}"
            echo -e "${GREEN}✅ Images pushed successfully!${NC}"
        fi
    else
        echo "ℹ️  No registry configured. Set DOCKER_REGISTRY to push images."
        echo "   Example: export DOCKER_REGISTRY=docker.io/yourusername"
    fi
    
    echo ""
    echo "🚀 Next steps:"
    echo "  1. Test locally: docker-compose up"
    echo "  2. Or run standalone: docker run -p 5000:5000 ${FULL_IMAGE_NAME}:${LATEST_TAG}"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Docker build failed!${NC}"
    exit 1
fi
