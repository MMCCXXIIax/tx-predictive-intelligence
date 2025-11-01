#!/bin/bash

# ============================================
# TX Predictive Intelligence - Docker Cleanup
# Removes all old images to free up space
# ============================================

set -e

echo "🧹 TX Predictive Intelligence - Docker Cleanup"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}⚠️  WARNING: This will delete ALL Docker images!${NC}"
echo ""
echo "This will free up storage by removing:"
echo "  - All TX backend images (old versions)"
echo "  - All dangling/unused images"
echo "  - All build cache"
echo ""
echo -n "Are you sure you want to continue? (yes/no): "
read CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${BLUE}Cleanup cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Starting cleanup...${NC}"
echo ""

# Stop all running containers (optional, uncomment if needed)
# echo "Stopping all running containers..."
# docker stop $(docker ps -aq) 2>/dev/null || true

# Remove all containers
echo "Removing all containers..."
docker rm $(docker ps -aq) 2>/dev/null || true
echo -e "${GREEN}✅ Containers removed${NC}"
echo ""

# Remove all images
echo "Removing all images..."
docker rmi $(docker images -q) -f 2>/dev/null || true
echo -e "${GREEN}✅ Images removed${NC}"
echo ""

# Remove dangling images
echo "Removing dangling images..."
docker image prune -f
echo -e "${GREEN}✅ Dangling images removed${NC}"
echo ""

# Remove all unused images
echo "Removing all unused images..."
docker image prune -a -f
echo -e "${GREEN}✅ Unused images removed${NC}"
echo ""

# Remove build cache
echo "Removing build cache..."
docker builder prune -a -f
echo -e "${GREEN}✅ Build cache removed${NC}"
echo ""

# Remove volumes (optional, uncomment if needed)
# echo "Removing all volumes..."
# docker volume prune -f
# echo -e "${GREEN}✅ Volumes removed${NC}"
# echo ""

# Show disk space freed
echo ""
echo -e "${GREEN}🎉 Cleanup complete!${NC}"
echo ""
echo "Disk space status:"
docker system df
echo ""
echo -e "${BLUE}You can now build the fresh TX image with all new features!${NC}"
echo ""
