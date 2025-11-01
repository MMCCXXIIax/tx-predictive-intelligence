#!/bin/bash

# ============================================
# TX Predictive Intelligence - Build & Push to Docker Hub
# For Render Deployment
# ============================================

set -e  # Exit on error

echo "🐳 TX Predictive Intelligence - Docker Build & Push for Render"
echo "================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
DOCKER_USERNAME="${DOCKER_USERNAME:-}"
IMAGE_NAME="tx-predictive-intelligence"
VERSION=$(date +%Y%m%d-%H%M%S)
LATEST_TAG="latest"

# Check if Docker username is set
if [ -z "$DOCKER_USERNAME" ]; then
    echo -e "${YELLOW}Docker Hub username not set in environment.${NC}"
    echo -n "Enter your Docker Hub username: "
    read DOCKER_USERNAME
    
    if [ -z "$DOCKER_USERNAME" ]; then
        echo -e "${RED}❌ Docker Hub username is required${NC}"
        exit 1
    fi
fi

FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}"

echo -e "${BLUE}Configuration:${NC}"
echo "  Docker Hub User: ${DOCKER_USERNAME}"
echo "  Image Name: ${IMAGE_NAME}"
echo "  Full Image: ${FULL_IMAGE_NAME}"
echo "  Version Tag: ${VERSION}"
echo "  Latest Tag: ${LATEST_TAG}"
echo ""

# Check if logged in to Docker Hub
echo -e "${BLUE}Checking Docker Hub login...${NC}"
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

# Build the Docker image
echo -e "${BLUE}Building Docker image...${NC}"
echo "This may take 5-10 minutes..."
echo ""

docker build \
    --tag "${FULL_IMAGE_NAME}:${VERSION}" \
    --tag "${FULL_IMAGE_NAME}:${LATEST_TAG}" \
    --platform linux/amd64 \
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

# Push to Docker Hub
echo -e "${BLUE}Pushing to Docker Hub...${NC}"
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
echo -e "${GREEN}🎉 Successfully pushed to Docker Hub!${NC}"
echo ""
echo "Images available at:"
echo "  - ${FULL_IMAGE_NAME}:${VERSION}"
echo "  - ${FULL_IMAGE_NAME}:${LATEST_TAG}"
echo ""
echo "📋 For Render deployment:"
echo "  1. Go to Render Dashboard"
echo "  2. Create New Web Service"
echo "  3. Select 'Deploy an existing image from a registry'"
echo "  4. Enter image URL: ${FULL_IMAGE_NAME}:${LATEST_TAG}"
echo "  5. Set environment variables (see env.example)"
echo "  6. Deploy!"
echo ""
echo "🔗 Docker Hub URL:"
echo "  https://hub.docker.com/r/${DOCKER_USERNAME}/${IMAGE_NAME}"
echo ""
