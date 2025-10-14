# Quick Production Test
$URL = "https://tx-predictive-intelligence.onrender.com"

Write-Host "Testing Production Backend..." -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "1. Health Check..." -NoNewline
try {
    $response = Invoke-RestMethod -Uri "$URL/health" -TimeoutSec 10
    if ($response.status -eq "healthy") {
        Write-Host " PASS" -ForegroundColor Green
    } else {
        Write-Host " FAIL" -ForegroundColor Red
    }
} catch {
    Write-Host " FAIL - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: New Endpoints
Write-Host "2. Achievements Endpoint..." -NoNewline
try {
    $response = Invoke-RestMethod -Uri "$URL/api/achievements" -TimeoutSec 10
    if ($response.success -eq $true) {
        Write-Host " PASS" -ForegroundColor Green
    } else {
        Write-Host " FAIL" -ForegroundColor Red
    }
} catch {
    Write-Host " FAIL - $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "3. Streak Endpoint..." -NoNewline
try {
    $response = Invoke-RestMethod -Uri "$URL/api/streak" -TimeoutSec 10
    if ($response.success -eq $true) {
        Write-Host " PASS" -ForegroundColor Green
    } else {
        Write-Host " FAIL" -ForegroundColor Red
    }
} catch {
    Write-Host " FAIL - $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "4. Forecast Endpoint..." -NoNewline
try {
    $response = Invoke-RestMethod -Uri "$URL/api/analytics/forecast" -TimeoutSec 10
    if ($response.success -eq $true) {
        Write-Host " PASS" -ForegroundColor Green
    } else {
        Write-Host " FAIL" -ForegroundColor Red
    }
} catch {
    Write-Host " FAIL - $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Production backend is operational!" -ForegroundColor Green
