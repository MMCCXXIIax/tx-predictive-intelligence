#!/bin/bash

# ============================================
# TX Predictive Intelligence - Docker Push Script
# ============================================

set -e  # Exit on error

echo "🚀 TX Predictive Intelligence - Docker Push"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="tx-predictive-intelligence"
LATEST_TAG="latest"

# Check if registry is set
if [ -z "$DOCKER_REGISTRY" ]; then
    echo -e "${RED}❌ Error: DOCKER_REGISTRY not set${NC}"
    echo ""
    echo "Please set your Docker registry:"
    echo "  export DOCKER_REGISTRY=docker.io/yourusername"
    echo "  export DOCKER_REGISTRY=ghcr.io/yourusername"
    echo "  export DOCKER_REGISTRY=your-registry.com/yourusername"
    echo ""
    exit 1
fi

FULL_IMAGE_NAME="${DOCKER_REGISTRY}/${IMAGE_NAME}"

echo -e "${BLUE}Checking if image exists locally...${NC}"
if ! docker images "${FULL_IMAGE_NAME}:${LATEST_TAG}" | grep -q "${IMAGE_NAME}"; then
    echo -e "${RED}❌ Image not found locally: ${FULL_IMAGE_NAME}:${LATEST_TAG}${NC}"
    echo ""
    echo "Please build the image first:"
    echo "  ./docker-build.sh"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Image found locally${NC}"
echo ""

# Check if logged in to registry
echo -e "${BLUE}Checking Docker registry login...${NC}"
if [[ "$DOCKER_REGISTRY" == *"docker.io"* ]]; then
    REGISTRY_URL="docker.io"
elif [[ "$DOCKER_REGISTRY" == *"ghcr.io"* ]]; then
    REGISTRY_URL="ghcr.io"
else
    REGISTRY_URL="$DOCKER_REGISTRY"
fi

# Test registry access
if ! docker login "$REGISTRY_URL" --username "$DOCKER_USERNAME" --password-stdin <<< "$DOCKER_PASSWORD" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to registry${NC}"
    echo ""
    echo "Please login first:"
    echo "  docker login $REGISTRY_URL"
    echo ""
    read -p "Press Enter after logging in..."
fi

echo -e "${GREEN}✅ Registry access confirmed${NC}"
echo ""

# Get all tags for this image
TAGS=$(docker images "${FULL_IMAGE_NAME}" --format "{{.Tag}}" | grep -v "<none>")

echo -e "${BLUE}Pushing images to registry...${NC}"
echo "Registry: ${DOCKER_REGISTRY}"
echo "Image: ${IMAGE_NAME}"
echo ""

# Push all tags
for TAG in $TAGS; do
    echo -e "${BLUE}Pushing ${FULL_IMAGE_NAME}:${TAG}...${NC}"
    docker push "${FULL_IMAGE_NAME}:${TAG}"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Pushed ${FULL_IMAGE_NAME}:${TAG}${NC}"
    else
        echo -e "${RED}❌ Failed to push ${FULL_IMAGE_NAME}:${TAG}${NC}"
        exit 1
    fi
    echo ""
done

echo ""
echo -e "${GREEN}🎉 All images pushed successfully!${NC}"
echo ""
echo "Images available at:"
for TAG in $TAGS; do
    echo "  - ${FULL_IMAGE_NAME}:${TAG}"
done
echo ""
echo "🚀 Deploy with:"
echo "  docker pull ${FULL_IMAGE_NAME}:${LATEST_TAG}"
echo "  docker run -p 5000:5000 ${FULL_IMAGE_NAME}:${LATEST_TAG}"
echo ""
