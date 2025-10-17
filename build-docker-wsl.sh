#!/bin/bash
# ============================================
# TX BACKEND - FULL SOURCE DOCKER BUILD
# Run this in WSL2 Ubuntu for best results
# ============================================

set -e  # Exit on error

echo "========================================"
echo "TX BACKEND - FULL SOURCE BUILD"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================
# PRE-BUILD CHECKS
# ============================================

echo -e "${YELLOW}[1/6] Pre-build checks...${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Docker is not running!${NC}"
    echo "Start Docker with: sudo service docker start"
    exit 1
fi

# Check available disk space (need at least 10GB)
AVAILABLE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$AVAILABLE" -lt 10 ]; then
    echo -e "${RED}WARNING: Low disk space (${AVAILABLE}GB available)${NC}"
    echo "Recommended: At least 10GB free"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check available RAM
TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
if [ "$TOTAL_RAM" -lt 4 ]; then
    echo -e "${YELLOW}WARNING: Low RAM (${TOTAL_RAM}GB total)${NC}"
    echo "Recommended: At least 8GB RAM for PyTorch build"
fi

echo -e "${GREEN}✓ Pre-build checks passed${NC}"
echo ""

# ============================================
# CLEAN PREVIOUS BUILDS
# ============================================

echo -e "${YELLOW}[2/6] Cleaning previous builds...${NC}"

# Remove old images and containers
docker system prune -f > /dev/null 2>&1 || true

echo -e "${GREEN}✓ Cleanup complete${NC}"
echo ""

# ============================================
# BUILD DOCKER IMAGE
# ============================================

echo -e "${YELLOW}[3/6] Building Docker image from source...${NC}"
echo ""
echo "This will take 30-45 minutes on Linux (WSL2)"
echo "Progress will be shown below:"
echo ""
echo "Expected timeline:"
echo "  - Layers 1-3 (NumPy, SciPy, Pandas): 5-10 min"
echo "  - Layer 4 (PyTorch from source): 20-30 min ⏳"
echo "  - Layers 5-14 (Everything else): 5-10 min"
echo ""
echo "Starting build..."
echo ""

# Build with progress output
docker build \
    -f Dockerfile.full \
    -t tx-backend:latest \
    --progress=plain \
    . 2>&1 | tee build.log

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Docker image built successfully!${NC}"
else
    echo ""
    echo -e "${RED}✗ Build failed! Check build.log for details${NC}"
    exit 1
fi

echo ""

# ============================================
# VERIFY IMAGE
# ============================================

echo -e "${YELLOW}[4/6] Verifying image...${NC}"

# Check image size
IMAGE_SIZE=$(docker images tx-backend:latest --format "{{.Size}}")
echo "Image size: $IMAGE_SIZE"

# List installed packages
echo ""
echo "Verifying critical packages..."
docker run --rm tx-backend:latest python -c "
import sys
packages = {
    'Flask': 'flask',
    'PyTorch': 'torch',
    'NumPy': 'numpy',
    'Pandas': 'pandas',
    'scikit-learn': 'sklearn',
    'SQLAlchemy': 'sqlalchemy',
    'yfinance': 'yfinance',
}

print('Package verification:')
for name, module in packages.items():
    try:
        mod = __import__(module)
        version = getattr(mod, '__version__', 'unknown')
        print(f'  ✓ {name}: {version}')
    except ImportError:
        print(f'  ✗ {name}: NOT FOUND')
        sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ All packages verified${NC}"
else
    echo ""
    echo -e "${RED}✗ Package verification failed${NC}"
    exit 1
fi

echo ""

# ============================================
# TEST LOCALLY
# ============================================

echo -e "${YELLOW}[5/6] Testing locally...${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}WARNING: .env file not found${NC}"
    echo "Creating minimal .env for testing..."
    cat > .env << EOF
FLASK_ENV=development
DATABASE_URL=postgresql://test:test@localhost:5432/test
SUPABASE_URL=https://example.supabase.co
SUPABASE_SERVICE_ROLE_KEY=test-key
CORS_ORIGINS=*
EOF
fi

# Stop any existing test container
docker stop tx-test 2>/dev/null || true
docker rm tx-test 2>/dev/null || true

# Run container
echo "Starting test container..."
docker run -d \
    -p 5000:5000 \
    --env-file .env \
    --name tx-test \
    tx-backend:latest

# Wait for startup
echo "Waiting for application to start..."
sleep 15

# Test health endpoint
echo "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:5000/health || echo "FAILED")

if [[ $HEALTH_RESPONSE == *"ok"* ]]; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}✗ Health check failed${NC}"
    echo "Response: $HEALTH_RESPONSE"
    echo ""
    echo "Container logs:"
    docker logs tx-test
    docker stop tx-test
    docker rm tx-test
    exit 1
fi

# Show container logs
echo ""
echo "Container logs (last 20 lines):"
docker logs --tail 20 tx-test

# Stop test container
echo ""
echo "Stopping test container..."
docker stop tx-test > /dev/null
docker rm tx-test > /dev/null

echo -e "${GREEN}✓ Local test passed${NC}"
echo ""

# ============================================
# SUMMARY
# ============================================

echo -e "${YELLOW}[6/6] Build Summary${NC}"
echo ""
echo "========================================"
echo -e "${GREEN}BUILD SUCCESSFUL!${NC}"
echo "========================================"
echo ""
echo "Image: tx-backend:latest"
echo "Size: $IMAGE_SIZE"
echo "Built from: SOURCE (no pre-built wheels)"
echo "Capabilities: FULL (100%)"
echo ""
echo "Next steps:"
echo ""
echo "1. Tag for Docker Hub:"
echo "   docker tag tx-backend:latest YOUR-USERNAME/tx-backend:latest"
echo ""
echo "2. Login to Docker Hub:"
echo "   docker login"
echo ""
echo "3. Push to Docker Hub:"
echo "   docker push YOUR-USERNAME/tx-backend:latest"
echo ""
echo "4. Deploy to Railway:"
echo "   - Go to railway.app"
echo "   - New Project → Deploy from Docker Image"
echo "   - Enter: YOUR-USERNAME/tx-backend:latest"
echo "   - Add PostgreSQL database"
echo "   - Add environment variables"
echo "   - Deploy!"
echo ""
echo "========================================"
echo ""
echo "Build log saved to: build.log"
echo ""
