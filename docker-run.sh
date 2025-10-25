#!/bin/bash

# ============================================
# TX Predictive Intelligence - Docker Run Script
# ============================================

set -e  # Exit on error

echo "🐳 TX Predictive Intelligence - Docker Run"
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
CONTAINER_NAME="tx-backend"
PORT="${PORT:-5000}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Warning: .env file not found${NC}"
    echo ""
    echo "Creating .env from env.example..."
    cp env.example .env
    echo -e "${GREEN}✅ Created .env file${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Please edit .env file with your configuration before running${NC}"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit..."
fi

# Stop and remove existing container if running
if docker ps -a | grep -q "$CONTAINER_NAME"; then
    echo -e "${BLUE}Stopping existing container...${NC}"
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    echo -e "${GREEN}✅ Existing container removed${NC}"
    echo ""
fi

# Check if image exists
if ! docker images | grep -q "$IMAGE_NAME"; then
    echo -e "${RED}❌ Image not found: $IMAGE_NAME${NC}"
    echo ""
    echo "Please build the image first:"
    echo "  ./docker-build.sh"
    echo ""
    exit 1
fi

echo -e "${BLUE}Starting TX Predictive Intelligence...${NC}"
echo ""

# Run the container
docker run -d \
    --name "$CONTAINER_NAME" \
    --env-file .env \
    -p "$PORT:5000" \
    --restart unless-stopped \
    -v "$(pwd)/logs:/app/logs" \
    -v "$(pwd)/models:/app/models" \
    "$IMAGE_NAME:latest"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Container started successfully!${NC}"
    echo ""
    echo "Container: $CONTAINER_NAME"
    echo "Port: $PORT"
    echo ""
    
    # Wait for container to be healthy
    echo -e "${BLUE}Waiting for service to be ready...${NC}"
    sleep 5
    
    # Check health
    if curl -s "http://localhost:$PORT/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Service is healthy!${NC}"
        echo ""
        echo "🚀 TX Predictive Intelligence is running!"
        echo ""
        echo "API: http://localhost:$PORT"
        echo "Health: http://localhost:$PORT/health"
        echo ""
        echo "📊 Useful commands:"
        echo "  View logs: docker logs -f $CONTAINER_NAME"
        echo "  Stop: docker stop $CONTAINER_NAME"
        echo "  Restart: docker restart $CONTAINER_NAME"
        echo "  Remove: docker rm -f $CONTAINER_NAME"
        echo ""
    else
        echo -e "${YELLOW}⚠️  Service not responding yet${NC}"
        echo ""
        echo "Check logs with:"
        echo "  docker logs -f $CONTAINER_NAME"
        echo ""
    fi
else
    echo -e "${RED}❌ Failed to start container${NC}"
    exit 1
fi
