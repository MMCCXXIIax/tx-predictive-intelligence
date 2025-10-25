# ============================================
# TX Predictive Intelligence - Git Push All Changes (PowerShell)
# ============================================

Write-Host "📦 TX Predictive Intelligence - Git Push All" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is initialized
if (-not (Test-Path .git)) {
    Write-Host "❌ Error: Not a git repository" -ForegroundColor Red
    Write-Host ""
    Write-Host "Initialize git first:"
    Write-Host "  git init"
    Write-Host "  git remote add origin YOUR-REPO-URL"
    Write-Host ""
    exit 1
}

# Check for uncommitted changes
$status = git status -s
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "⚠️  No changes to commit" -ForegroundColor Yellow
    Write-Host ""
    $push = Read-Host "Do you want to push anyway? (y/n)"
    if ($push -ne "y" -and $push -ne "Y") {
        exit 0
    }
} else {
    Write-Host "Changes detected:" -ForegroundColor Blue
    git status -s
    Write-Host ""
}

# Get current branch
$currentBranch = git branch --show-current
Write-Host "Current branch: $currentBranch"
Write-Host ""

# Ask for commit message
Write-Host "Enter commit message:" -ForegroundColor Blue
$commitMessage = Read-Host ">"

if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = "Update: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host "Using default message: $commitMessage"
}

Write-Host ""
Write-Host "Staging all changes..." -ForegroundColor Blue
git add .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Changes staged" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to stage changes" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Committing changes..." -ForegroundColor Blue
git commit -m "$commitMessage"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Changes committed" -ForegroundColor Green
} else {
    Write-Host "⚠️  Nothing to commit or commit failed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Pushing to remote..." -ForegroundColor Blue
git push origin $currentBranch

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 Successfully pushed to origin/$currentBranch!" -ForegroundColor Green
    Write-Host ""
    
    # Show last commit
    Write-Host "Last commit:"
    git log -1 --oneline
    Write-Host ""
    
    # Show remote URL
    $remoteUrl = git config --get remote.origin.url
    Write-Host "Remote: $remoteUrl"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Failed to push to remote" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible issues:"
    Write-Host "  - No remote configured"
    Write-Host "  - Authentication failed"
    Write-Host "  - Network issues"
    Write-Host "  - Branch does not exist on remote"
    Write-Host ""
    Write-Host "Try:"
    Write-Host "  git remote -v  # Check remote"
    Write-Host "  git push -u origin $currentBranch  # Set upstream"
    Write-Host ""
    exit 1
}
