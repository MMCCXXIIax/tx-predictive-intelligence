# scripts/check-local.ps1
# Purpose: One-stop health check for local Supabase + GraphQL + migrations

# --- CONFIG ---
$endpoint     = "http://127.0.0.1:54321/graphql/v1"
$apikey       = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpxcmVsZmRtZHJ3d3hyZm9jbHpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ1MTU1MDAsImV4cCI6MjA3MDA5MTUwMH0.Uebb9Xk8AESgapG95JbX0LoxlO-XCFUlTn6nrXCe1c8"
$goldenSchema = ".\db\golden_schema.sql"

Write-Host "=== Local Stack Health Check ===" -ForegroundColor Cyan

function Fail($msg) {
    Write-Host "❌ $msg" -ForegroundColor Red
    exit 1
}

# 1. Docker Desktop running
if (-not (Get-Process -Name "com.docker.desktop" -ErrorAction SilentlyContinue)) {
    Fail "Docker Desktop is not running."
}
Write-Host "✅ Docker Desktop is running." -ForegroundColor Green

# 2. Supabase API reachable
try {
    Invoke-WebRequest -Uri $endpoint -Method Head -Headers @{ "apikey" = $apikey } -TimeoutSec 2 | Out-Null
    Write-Host "✅ Supabase API reachable." -ForegroundColor Green
}
catch { Fail "Supabase API not reachable at $endpoint" }

# 3. GraphQL introspection for custom table (profiles)
$gqlQuery = @'
{
  __type(name: "profiles") {
    name
    fields { name }
  }
}
'@

$body = @{ query = $gqlQuery } | ConvertTo-Json -Compress

try {
    $graphql = Invoke-RestMethod -Uri $endpoint -Method Post -Headers @{
        "apikey"       = $apikey
        "Content-Type" = "application/json"
    } -Body $body
}
catch { Fail "GraphQL query failed." }

if (-not $graphql.data.__type) {
    Fail "'profiles' type not found - did migrations run?"
}
Write-Host "✅ 'profiles' table present in GraphQL schema." -ForegroundColor Green

# 4. Migration folder sanity check
if (-Not (Test-Path $goldenSchema)) {
    Write-Host "⚠ Golden schema not found, skipping DB diff."
} else {
    $latestMigration = Get-ChildItem .\migrations\*.sql -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestMigration) {
        Write-Host "✅ Latest migration: $($latestMigration.Name)" -ForegroundColor Green
    } else {
        Write-Host "⚠ No migration files found." -ForegroundColor Yellow
    }
}

Write-Host "=== All checks passed! ===" -ForegroundColor Cyan
exit 0
