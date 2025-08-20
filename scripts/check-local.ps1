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

# 1. Docker Engine running
if (-not (docker info --format '{{.ServerVersion}}' 2>$null)) {
    Fail "Docker Engine is not running."
}
Write-Host "✅ Docker Engine is running." -ForegroundColor Green

# 2. GraphQL readiness check with retries
Write-Host "`n🔎 Checking GraphQL endpoint..."
$pingBody = '{"query":"{ __typename }"}'
$maxRetries = 10
$delaySeconds = 3
$graphqlHealthy = $false

for ($i = 1; $i -le $maxRetries; $i++) {
    try {
        $resp = Invoke-WebRequest $endpoint `
            -Method POST `
            -Headers @{ "apikey" = $apikey; "Content-Type" = "application/json" } `
            -Body $pingBody `
            -UseBasicParsing

        if ($resp.StatusCode -eq 200 -and $resp.Content -match '__typename') {
            Write-Host "✅ GraphQL is ready."
            $graphqlHealthy = $true
            break
        }
    } catch {
        # ignore and retry
    }
    Write-Host "⏳ GraphQL not ready yet... retry $i/$maxRetries"
    Start-Sleep -Seconds $delaySeconds
}

if (-not $graphqlHealthy) {
    Fail "GraphQL endpoint not responding after $($maxRetries * $delaySeconds) seconds."
}

# 3. Check 'profiles' table exists in schema
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
} catch { Fail "GraphQL schema query failed." }

if (-not $graphql.data.__type) {
    Fail "'profiles' type not found - did migrations run?"
}
Write-Host "✅ 'profiles' table present in GraphQL schema." -ForegroundColor Green

# 4. Migration status check inside DB container
Write-Host "`n📜 Checking migrations..."
try {
    $migrationStatus = docker exec supabase_db_tx-predictive-intelligence psql -U postgres -d postgres -tAc "
        SELECT COUNT(*) FROM supabase_migrations.schema_migrations WHERE NOT applied;" 2>$null

    if ($migrationStatus -eq 0) {
        Write-Host "✅ All migrations applied."
    } else {
        Fail "$migrationStatus unapplied migration(s) detected."
    }
} catch {
    Fail "Could not verify migrations: $_"
}

# 5. Optional: migration folder sanity check
if (-Not (Test-Path $goldenSchema)) {
    Write-Host "⚠ Golden schema not found, skipping DB diff."
} else {
    $latestMigration = Get-ChildItem .\migrations\*.sql -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestMigration) {
        Write-Host "✅ Latest migration file: $($latestMigration.Name)" -ForegroundColor Green
    } else {
        Write-Host "⚠ No migration files found." -ForegroundColor Yellow
    }
}

Write-Host "`n=== All checks passed! ===" -ForegroundColor Cyan
exit 0
