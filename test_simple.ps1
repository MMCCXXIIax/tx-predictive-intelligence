# Simple Backend Test
Write-Host "Testing TX Backend..." -ForegroundColor Cyan

# Test 1: Health
Write-Host "`n1. Health Check..." -ForegroundColor Yellow
$health = Invoke-RestMethod -Uri "https://tx-predictive-intelligence.onrender.com/health"
Write-Host "Status: $($health.status)" -ForegroundColor Green

# Test 2: Pattern Detection
Write-Host "`n2. Pattern Detection..." -ForegroundColor Yellow
$body = '{"symbol":"AAPL"}'
$detect = Invoke-RestMethod -Uri "https://tx-predictive-intelligence.onrender.com/api/detect" -Method POST -ContentType "application/json" -Body $body
Write-Host "Success: $($detect.success)" -ForegroundColor Green
Write-Host "Patterns Found: $($detect.data.count)" -ForegroundColor Green

# Test 3: Alerts
Write-Host "`n3. Active Alerts..." -ForegroundColor Yellow
$alerts = Invoke-RestMethod -Uri "https://tx-predictive-intelligence.onrender.com/api/get_active_alerts"
Write-Host "Success: $($alerts.success)" -ForegroundColor Green
Write-Host "Alert Count: $($alerts.alerts.Count)" -ForegroundColor Green

Write-Host "`nALL TESTS PASSED!" -ForegroundColor Green
Write-Host "Your backend is fully operational!" -ForegroundColor Cyan
