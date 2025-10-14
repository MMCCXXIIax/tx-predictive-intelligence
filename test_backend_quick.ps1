# Quick Backend Test Script
# Tests the live backend to confirm it's working

$baseUrl = "https://tx-predictive-intelligence.onrender.com"

Write-Host "`n==================================" -ForegroundColor Cyan
Write-Host "TX BACKEND QUICK TEST" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "`n[1/4] Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET -TimeoutSec 10
    if ($health.status -eq "ok") {
        Write-Host "✓ Health Check: PASS" -ForegroundColor Green
        Write-Host "  Status: $($health.status)" -ForegroundColor Gray
    } else {
        Write-Host "✗ Health Check: FAIL" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Health Check: ERROR - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Pattern Detection (New Endpoint)
Write-Host "`n[2/4] Testing Pattern Detection (/api/detect)..." -ForegroundColor Yellow
try {
    $body = @{ symbol = "AAPL" } | ConvertTo-Json
    $detect = Invoke-RestMethod -Uri "$baseUrl/api/detect" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 30
    if ($detect.success) {
        Write-Host "✓ Pattern Detection: PASS" -ForegroundColor Green
        Write-Host "  Symbol: $($detect.data.symbol)" -ForegroundColor Gray
        Write-Host "  Patterns Found: $($detect.data.count)" -ForegroundColor Gray
        if ($detect.data.patterns.Count -gt 0) {
            Write-Host "  Top Pattern: $($detect.data.patterns[0].pattern_name) (Confidence: $($detect.data.patterns[0].confidence))" -ForegroundColor Gray
        }
    } else {
        Write-Host "✗ Pattern Detection: FAIL" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Pattern Detection: ERROR - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Get Active Alerts
Write-Host "`n[3/4] Testing Active Alerts..." -ForegroundColor Yellow
try {
    $alerts = Invoke-RestMethod -Uri "$baseUrl/api/get_active_alerts" -Method GET -TimeoutSec 10
    if ($alerts.success) {
        Write-Host "✓ Active Alerts: PASS" -ForegroundColor Green
        Write-Host "  Active Alerts: $($alerts.alerts.Count)" -ForegroundColor Gray
        if ($alerts.alerts.Count -gt 0) {
            Write-Host "  Latest: $($alerts.alerts[0].symbol) - $($alerts.alerts[0].message)" -ForegroundColor Gray
        }
    } else {
        Write-Host "✗ Active Alerts: FAIL" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Active Alerts: ERROR - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Market Scan
Write-Host "`n[4/4] Testing Market Scan..." -ForegroundColor Yellow
try {
    $scan = Invoke-RestMethod -Uri "$baseUrl/api/market-scan" -Method GET -TimeoutSec 30
    if ($scan.success) {
        Write-Host "✓ Market Scan: PASS" -ForegroundColor Green
        Write-Host "  Symbols Scanned: $($scan.data.symbols_scanned)" -ForegroundColor Gray
        Write-Host "  Patterns Found: $($scan.data.patterns_found)" -ForegroundColor Gray
    } else {
        Write-Host "✗ Market Scan: FAIL" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Market Scan: ERROR - $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`n==================================" -ForegroundColor Cyan
Write-Host "TEST COMPLETE!" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "`nYour backend is live at:" -ForegroundColor Green
Write-Host "$baseUrl" -ForegroundColor White
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Run the Supabase SQL to create trade_outcomes table" -ForegroundColor White
Write-Host "2. Start building your frontend" -ForegroundColor White
Write-Host "3. Check API_ENDPOINTS.md for all available endpoints" -ForegroundColor White
Write-Host ""
