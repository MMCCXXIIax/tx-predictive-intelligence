# TX Backend - CORS & Frontend Integration Test Script
# Tests all critical endpoints with CORS headers

$baseUrl = "https://tx-predictive-intelligence.onrender.com"
$frontendOrigin = "https://tx-figma-frontend.onrender.com"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TX Backend Integration Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test counter
$passed = 0
$failed = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Body = $null,
        [bool]$CheckCORS = $true
    )
    
    Write-Host "Testing: $Name" -ForegroundColor Yellow
    Write-Host "  URL: $Url" -ForegroundColor Gray
    
    try {
        $headers = @{
            "Origin" = $frontendOrigin
            "Content-Type" = "application/json"
        }
        
        if ($Method -eq "GET") {
            $response = Invoke-WebRequest -Uri $Url -Method GET -Headers $headers -UseBasicParsing
        } else {
            $bodyJson = $Body | ConvertTo-Json -Depth 10
            $response = Invoke-WebRequest -Uri $Url -Method POST -Headers $headers -Body $bodyJson -UseBasicParsing
        }
        
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ Status: 200 OK" -ForegroundColor Green
            
            # Check CORS headers
            if ($CheckCORS) {
                $corsHeader = $response.Headers["Access-Control-Allow-Origin"]
                if ($corsHeader) {
                    Write-Host "  ✅ CORS Header: $corsHeader" -ForegroundColor Green
                } else {
                    Write-Host "  ⚠️  CORS Header: Missing" -ForegroundColor Yellow
                }
            }
            
            # Show response preview
            $content = $response.Content
            if ($content.Length -gt 200) {
                $preview = $content.Substring(0, 200) + "..."
            } else {
                $preview = $content
            }
            Write-Host "  Response: $preview" -ForegroundColor Gray
            
            $script:passed++
            return $true
        } else {
            Write-Host "  ❌ Status: $($response.StatusCode)" -ForegroundColor Red
            $script:failed++
            return $false
        }
    } catch {
        Write-Host "  ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        $script:failed++
        return $false
    }
    
    Write-Host ""
}

# Test 1: Health Check
Test-Endpoint -Name "Health Check" -Url "$baseUrl/health"

# Test 2: Detailed Health
Test-Endpoint -Name "Detailed Health" -Url "$baseUrl/health/detailed"

# Test 3: Provider Health
Test-Endpoint -Name "Provider Health" -Url "$baseUrl/api/provider-health"

# Test 4: Market Scan - Trending
Test-Endpoint -Name "Market Scan (Trending)" -Url "$baseUrl/api/market-scan?type=trending"

# Test 5: Market Scan - Volume
Test-Endpoint -Name "Market Scan (Volume)" -Url "$baseUrl/api/market-scan?type=volume"

# Test 6: Pattern Detection
Test-Endpoint -Name "Pattern Detection" -Url "$baseUrl/api/detect-enhanced" -Method "POST" -Body @{symbol="AAPL"}

# Test 7: Active Alerts
Test-Endpoint -Name "Active Alerts" -Url "$baseUrl/api/get_active_alerts"

# Test 8: Scan Status
Test-Endpoint -Name "Scan Status" -Url "$baseUrl/api/scan/status"

# Test 9: Pattern Stats
Test-Endpoint -Name "Pattern Stats" -Url "$baseUrl/api/pattern-stats"

# Test 10: Pattern List
Test-Endpoint -Name "Pattern List" -Url "$baseUrl/api/patterns/list"

# Test 11: Paper Trades
Test-Endpoint -Name "Paper Trades" -Url "$baseUrl/api/paper-trades"

# Test 12: Trading Stats
Test-Endpoint -Name "Trading Stats" -Url "$baseUrl/api/stats/trading"

# Test 13: ML Models
Test-Endpoint -Name "ML Models" -Url "$baseUrl/api/ml/models"

# Test 14: Online Learning Status
Test-Endpoint -Name "Online Learning Status" -Url "$baseUrl/api/ml/online-status"

# Test 15: Detection Stats
Test-Endpoint -Name "Detection Stats" -Url "$baseUrl/api/detection_stats"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Results" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red
Write-Host ""

if ($failed -eq 0) {
    Write-Host "🎉 All tests passed! Backend is ready for frontend integration." -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests failed. Check the errors above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. If all tests passed, clear browser cache" -ForegroundColor White
Write-Host "2. Reload frontend: https://tx-figma-frontend.onrender.com" -ForegroundColor White
Write-Host "3. Check browser console for connection status" -ForegroundColor White
Write-Host "4. Test all features with live backend" -ForegroundColor White
Write-Host ""

# Test CORS Preflight (OPTIONS)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing CORS Preflight (OPTIONS)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    $headers = @{
        "Origin" = $frontendOrigin
        "Access-Control-Request-Method" = "POST"
        "Access-Control-Request-Headers" = "Content-Type"
    }
    
    $response = Invoke-WebRequest -Uri "$baseUrl/api/detect-enhanced" -Method OPTIONS -Headers $headers -UseBasicParsing
    
    Write-Host "✅ OPTIONS request successful" -ForegroundColor Green
    Write-Host "CORS Headers:" -ForegroundColor Yellow
    
    $corsHeaders = @(
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Methods",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Credentials"
    )
    
    foreach ($header in $corsHeaders) {
        $value = $response.Headers[$header]
        if ($value) {
            Write-Host "  $header : $value" -ForegroundColor Green
        } else {
            Write-Host "  $header : Missing" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "❌ OPTIONS request failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
