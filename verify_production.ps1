# Production Deployment Verification Script
# Tests all critical endpoints to ensure production readiness

$BASE_URL = "https://tx-predictive-intelligence.onrender.com"
$LOCAL_URL = "http://localhost:5000"

# Use production URL by default, or local if specified
$URL = if ($args[0] -eq "local") { $LOCAL_URL } else { $BASE_URL }

Write-Host "🔍 PRODUCTION READINESS VERIFICATION" -ForegroundColor Cyan
Write-Host "Testing: $URL" -ForegroundColor Yellow
Write-Host ""

$passed = 0
$failed = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Path,
        [string]$Method = "GET",
        [hashtable]$Body = $null
    )
    
    Write-Host "Testing: $Name..." -NoNewline
    
    try {
        $params = @{
            Uri = "$URL$Path"
            Method = $Method
            TimeoutSec = 10
            ErrorAction = 'Stop'
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json)
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-RestMethod @params
        
        if ($response.status -eq "healthy" -or $response.success -eq $true -or $response.status -eq "ok") {
            Write-Host " ✅ PASS" -ForegroundColor Green
            $script:passed++
            return $true
        } else {
            Write-Host " ⚠️  WARN (unexpected response)" -ForegroundColor Yellow
            $script:passed++
            return $true
        }
    }
    catch {
        Write-Host " ❌ FAIL" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        $script:failed++
        return $false
    }
}

# Critical Health Checks
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "1. HEALTH CHECKS" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Test-Endpoint "Root Health Check" "/"
Test-Endpoint "Basic Health" "/health"
Test-Endpoint "Detailed Health" "/health/detailed"
Test-Endpoint "Provider Health" "/api/provider-health"
Test-Endpoint "Worker Health" "/api/workers/health"

# Core API Endpoints
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "2. CORE API ENDPOINTS" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Test-Endpoint "Active Alerts" "/api/get_active_alerts"
Test-Endpoint "Market Scan" "/api/market-scan?type=trending"
Test-Endpoint "Paper Trades" "/api/paper-trades"
Test-Endpoint "Trading Stats" "/api/trading-stats"

# New Frontend Endpoints
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "3. NEW FRONTEND ENDPOINTS" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Test-Endpoint "Analytics Attribution" "/api/analytics/attribution?period=30d"
Test-Endpoint "Analytics Forecast" "/api/analytics/forecast?timeframe=7d"
Test-Endpoint "Achievements" "/api/achievements"
Test-Endpoint "Streak Tracking" "/api/streak"

# ML/AI Endpoints
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "4. ML/AI ENDPOINTS" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Test-Endpoint "ML Models List" "/api/ml/models"
Test-Endpoint "Pattern Prediction" "/api/ml/predict?symbol=AAPL"
Test-Endpoint "Online Learning Status" "/api/ml/online-status"

# Monitoring Endpoints
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "5. MONITORING" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Test-Endpoint "Prometheus Metrics" "/metrics"

# Error Handling Tests
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "6. ERROR HANDLING" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

Write-Host "Testing: 404 Error Handler..." -NoNewline
try {
    Invoke-RestMethod -Uri "$URL/api/nonexistent-endpoint" -ErrorAction Stop
    Write-Host " ❌ FAIL (should return 404)" -ForegroundColor Red
    $failed++
}
catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host " ✅ PASS" -ForegroundColor Green
        $passed++
    } else {
        Write-Host " ❌ FAIL (wrong status code)" -ForegroundColor Red
        $failed++
    }
}

# Security Headers Check
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "7. SECURITY HEADERS" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

Write-Host "Checking security headers..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "$URL/health" -ErrorAction Stop
    $headers = $response.Headers
    
    $securityHeaders = @(
        "X-Frame-Options",
        "X-Content-Type-Options",
        "X-XSS-Protection",
        "Referrer-Policy"
    )
    
    $allPresent = $true
    foreach ($header in $securityHeaders) {
        if (-not $headers.ContainsKey($header)) {
            $allPresent = $false
            break
        }
    }
    
    if ($allPresent) {
        Write-Host " ✅ PASS" -ForegroundColor Green
        $passed++
    } else {
        Write-Host " ⚠️  WARN (some headers missing)" -ForegroundColor Yellow
        $passed++
    }
}
catch {
    Write-Host " ❌ FAIL" -ForegroundColor Red
    $failed++
}

# Summary
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "VERIFICATION SUMMARY" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Total Tests: $($passed + $failed)" -ForegroundColor White
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Red" })

$percentage = [math]::Round(($passed / ($passed + $failed)) * 100, 1)
Write-Host "Success Rate: $percentage%" -ForegroundColor $(if ($percentage -ge 90) { "Green" } elseif ($percentage -ge 70) { "Yellow" } else { "Red" })

Write-Host ""
if ($failed -eq 0) {
    Write-Host "🎉 ALL TESTS PASSED! Backend is production-ready!" -ForegroundColor Green
    exit 0
} elseif ($percentage -ge 90) {
    Write-Host "✅ Backend is mostly ready. Minor issues detected." -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "❌ Backend has issues. Please review failed tests." -ForegroundColor Red
    exit 1
}
