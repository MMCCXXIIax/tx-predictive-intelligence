# ============================================
# WAKE UP TX BACKEND
# Use this to wake up Render free tier service
# ============================================

$baseUrl = "https://tx-predictive-intelligence.onrender.com"

Write-Host "`n🌅 Waking up TX Backend..." -ForegroundColor Cyan
Write-Host "This may take 30-60 seconds on first request`n" -ForegroundColor Yellow

$maxAttempts = 12
$attempt = 1
$sleepSeconds = 5

while ($attempt -le $maxAttempts) {
    Write-Host "Attempt $attempt/$maxAttempts..." -ForegroundColor Gray
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET -TimeoutSec 30
        
        if ($response.status -eq "ok") {
            Write-Host "`n✅ Backend is AWAKE and READY!" -ForegroundColor Green
            Write-Host "   Status: $($response.status)" -ForegroundColor Gray
            Write-Host "   Timestamp: $($response.timestamp)" -ForegroundColor Gray
            Write-Host "`nYou can now run: .\test_api.ps1`n" -ForegroundColor Cyan
            exit 0
        }
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        
        if ($statusCode -eq 503) {
            Write-Host "   Service is spinning up... (503)" -ForegroundColor Yellow
        } else {
            Write-Host "   Waiting for response... ($($_.Exception.Message))" -ForegroundColor Yellow
        }
    }
    
    if ($attempt -lt $maxAttempts) {
        Write-Host "   Waiting $sleepSeconds seconds...`n" -ForegroundColor Gray
        Start-Sleep -Seconds $sleepSeconds
    }
    
    $attempt++
}

Write-Host "`n❌ Backend did not wake up after $($maxAttempts * $sleepSeconds) seconds" -ForegroundColor Red
Write-Host "   Check Render dashboard for errors: https://dashboard.render.com`n" -ForegroundColor Yellow
exit 1
