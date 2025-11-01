#!/bin/bash

# Simple build script with optimized Dockerfile
# Handles network timeouts better

echo "🚀 TX - Simple Build with Network Optimization"
echo "=============================================="
echo ""

DOCKER_USERNAME="jeanpaulkadusimanegaberobert1"
IMAGE_NAME="tx-predictive-intelligence"
VERSION=$(date +%Y%m%d-%H%M%S)

echo "Building with optimized Dockerfile..."
echo "This splits package installation into smaller batches"
echo "to avoid network timeouts."
echo ""

# Build with optimized Dockerfile
docker build \
    --tag "${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}" \
    --tag "${DOCKER_USERNAME}/${IMAGE_NAME}:latest" \
    --platform linux/amd64 \
    --file Dockerfile.optimized \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "Pushing to Docker Hub..."
    docker push "${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"
    docker push "${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 SUCCESS!"
        echo ""
        echo "Image: ${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
        echo ""
    fi
else
    echo ""
    echo "❌ Build failed. Try again - network issues are often temporary."
fi
