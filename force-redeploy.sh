#!/bin/bash
# ============================================
# FORCE RAILWAY TO USE NEW IMAGE
# ============================================

set -e

echo "=========================================="
echo "FORCE REDEPLOY WITH UNIQUE TAG"
echo "=========================================="
echo ""

# Create unique tag with timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
NEW_TAG="v1.0.3-${TIMESTAMP}"

echo "New unique tag: ${NEW_TAG}"
echo ""

# Tag the existing image with new unique tag
echo "[1/2] Tagging image with unique timestamp..."
docker tag tx-backend:latest jeanpaulkadusimanegaberobert1/tx-backend:${NEW_TAG}
echo "✓ Tagged as ${NEW_TAG}"
echo ""

# Push to Docker Hub
echo "[2/2] Pushing to Docker Hub..."
docker push jeanpaulkadusimanegaberobert1/tx-backend:${NEW_TAG}
echo "✓ Pushed successfully"
echo ""

echo "=========================================="
echo "✓ DONE!"
echo "=========================================="
echo ""
echo "UPDATE RAILWAY TO USE THIS IMAGE:"
echo "jeanpaulkadusimanegaberobert1/tx-backend:${NEW_TAG}"
echo ""
