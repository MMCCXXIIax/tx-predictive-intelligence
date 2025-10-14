# ============================================
# TX BACKEND HEALTH CHECK
# Comprehensive diagnostic script
# ============================================

$baseUrl = "https://tx-predictive-intelligence.onrender.com"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TX BACKEND HEALTH DIAGNOSTIC" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: Basic connectivity
Write-Host "Test 1: Basic Connectivity" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $baseUrl -Method GET -TimeoutSec 30
    Write-Host "✅ Server is reachable (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ Server unreachable: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   This could mean:" -ForegroundColor Yellow
    Write-Host "   - Render service is spinning down (free tier)" -ForegroundColor Yellow
    Write-Host "   - Application crashed on startup" -ForegroundColor Yellow
    Write-Host "   - Network connectivity issue" -ForegroundColor Yellow
    exit 1
}

# Test 2: Health endpoint
Write-Host "`nTest 2: Health Endpoint" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET -TimeoutSec 30
    Write-Host "✅ Health check passed" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor Gray
    Write-Host "   Timestamp: $($response.timestamp)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 3: Root endpoint
Write-Host "`nTest 3: Root Endpoint" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $baseUrl -Method GET -TimeoutSec 30
    Write-Host "✅ Root endpoint accessible (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Root endpoint issue: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 4: Database connectivity (via health endpoint)
Write-Host "`nTest 4: Database Status" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/health/system" -Method GET -TimeoutSec 30
    if ($response.success) {
        Write-Host "✅ System health check passed" -ForegroundColor Green
        if ($response.data.database) {
            Write-Host "   Database: Connected" -ForegroundColor Gray
        }
    } else {
        Write-Host "⚠️  System health check returned success=false" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  System health endpoint unavailable: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 5: Workers status
Write-Host "`nTest 5: Background Workers" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/health/workers" -Method GET -TimeoutSec 30
    if ($response.success) {
        Write-Host "✅ Workers health check passed" -ForegroundColor Green
        Write-Host "   Response: $($response.data | ConvertTo-Json -Compress)" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  Workers health endpoint unavailable: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DIAGNOSTIC COMPLETE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. If server is unreachable, check Render dashboard" -ForegroundColor White
Write-Host "2. If health check fails, check Render logs for errors" -ForegroundColor White
Write-Host "3. If all tests pass, try specific API endpoints" -ForegroundColor White
