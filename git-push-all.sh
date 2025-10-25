#!/bin/bash

# ============================================
# TX Predictive Intelligence - Git Push All Changes
# ============================================

set -e  # Exit on error

echo "📦 TX Predictive Intelligence - Git Push All"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if git is initialized
if [ ! -d .git ]; then
    echo -e "${RED}❌ Error: Not a git repository${NC}"
    echo ""
    echo "Initialize git first:"
    echo "  git init"
    echo "  git remote add origin <your-repo-url>"
    echo ""
    exit 1
fi

# Check for uncommitted changes
if [[ -z $(git status -s) ]]; then
    echo -e "${YELLOW}⚠️  No changes to commit${NC}"
    echo ""
    read -p "Do you want to push anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
else
    echo -e "${BLUE}Changes detected:${NC}"
    git status -s
    echo ""
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: ${CURRENT_BRANCH}"
echo ""

# Ask for commit message
echo -e "${BLUE}Enter commit message:${NC}"
read -p "> " COMMIT_MESSAGE

if [ -z "$COMMIT_MESSAGE" ]; then
    COMMIT_MESSAGE="Update: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Using default message: $COMMIT_MESSAGE"
fi

echo ""
echo -e "${BLUE}Staging all changes...${NC}"
git add .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Changes staged${NC}"
else
    echo -e "${RED}❌ Failed to stage changes${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Committing changes...${NC}"
git commit -m "$COMMIT_MESSAGE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Changes committed${NC}"
else
    echo -e "${YELLOW}⚠️  Nothing to commit or commit failed${NC}"
fi

echo ""
echo -e "${BLUE}Pushing to remote...${NC}"
git push origin "$CURRENT_BRANCH"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Successfully pushed to origin/${CURRENT_BRANCH}!${NC}"
    echo ""
    
    # Show last commit
    echo "Last commit:"
    git log -1 --oneline
    echo ""
    
    # Show remote URL
    REMOTE_URL=$(git config --get remote.origin.url)
    echo "Remote: $REMOTE_URL"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Failed to push to remote${NC}"
    echo ""
    echo "Possible issues:"
    echo "  - No remote configured"
    echo "  - Authentication failed"
    echo "  - Network issues"
    echo "  - Branch doesn't exist on remote"
    echo ""
    echo "Try:"
    echo "  git remote -v  # Check remote"
    echo "  git push -u origin $CURRENT_BRANCH  # Set upstream"
    echo ""
    exit 1
fi
