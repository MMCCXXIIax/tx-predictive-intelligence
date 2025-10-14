# ============================================
# TX PREDICTIVE INTELLIGENCE - API TESTS
# PowerShell test script for Windows
# ============================================

$baseUrl = "https://tx-predictive-intelligence.onrender.com"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TX BACKEND API TESTS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "Test 1: Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "✅ SUCCESS: $($response | ConvertTo-Json -Compress)" -ForegroundColor Green
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Pattern Detection
Write-Host "`nTest 2: Pattern Detection (AAPL)" -ForegroundColor Yellow
try {
    $body = @{
        symbol = "AAPL"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/detect" -Method POST -ContentType "application/json" -Body $body
    Write-Host "✅ SUCCESS: Found $($response.data.patterns.Count) patterns" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Depth 3)" -ForegroundColor Gray
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Get Active Alerts
Write-Host "`nTest 3: Get Active Alerts" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/get_active_alerts" -Method GET
    Write-Host "✅ SUCCESS: Found $($response.data.Count) alerts" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Depth 2)" -ForegroundColor Gray
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Market Scan
Write-Host "`nTest 4: Market Scan" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/market-scan" -Method GET
    Write-Host "✅ SUCCESS: Market scan complete" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Depth 2)" -ForegroundColor Gray
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Enhanced Detection
Write-Host "`nTest 5: Enhanced Detection (TSLA)" -ForegroundColor Yellow
try {
    $body = @{
        symbol = "TSLA"
        timeframe = "1h"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/detect-enhanced" -Method POST -ContentType "application/json" -Body $body
    Write-Host "✅ SUCCESS: Enhanced detection complete" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Depth 3)" -ForegroundColor Gray
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Get Candlestick Data
Write-Host "`nTest 6: Get Candlestick Data (BTC-USD)" -ForegroundColor Yellow
try {
    $body = @{
        symbol = "BTC-USD"
        timeframe = "1h"
        limit = 100
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/candles" -Method POST -ContentType "application/json" -Body $body
    Write-Host "✅ SUCCESS: Retrieved $($response.data.Count) candles" -ForegroundColor Green
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 7: Get Trading Statistics
Write-Host "`nTest 7: Get Trading Statistics" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/stats/trading" -Method GET
    Write-Host "✅ SUCCESS: Stats retrieved" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Depth 2)" -ForegroundColor Gray
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 8: Get Risk Metrics
Write-Host "`nTest 8: Get Risk Metrics (AAPL)" -ForegroundColor Yellow
try {
    $body = @{
        symbol = "AAPL"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/risk/metrics" -Method POST -ContentType "application/json" -Body $body
    Write-Host "✅ SUCCESS: Risk metrics calculated" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Depth 2)" -ForegroundColor Gray
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 9: Get Entry Signals
Write-Host "`nTest 9: Get Entry Signals (ETH-USD)" -ForegroundColor Yellow
try {
    $body = @{
        symbol = "ETH-USD"
        timeframe = "1h"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/signals/entry" -Method POST -ContentType "application/json" -Body $body
    Write-Host "✅ SUCCESS: Entry signals generated" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Depth 2)" -ForegroundColor Gray
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 10: Get System Health
Write-Host "`nTest 10: Get System Health" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/health/system" -Method GET
    Write-Host "✅ SUCCESS: System health retrieved" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Depth 2)" -ForegroundColor Gray
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TESTS COMPLETE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
