# scripts/check-local.ps1
# Purpose: Full local stack health check + schema auto-fix + drift logging

# --- CONFIG ---
$endpoint     = "http://127.0.0.1:54321/graphql/v1"
$apikey       = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpxcmVsZmRtZHJ3d3hyZm9jbHpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ1MTU1MDAsImV4cCI6MjA3MDA5MTUwMH0.Uebb9Xk8AESgapG95JbX0LoxlO-XCFUlTn6nrXCe1c8"
$goldenSchema = ".\migrations\schema_V1_0_beta.sql"
$driftLog     = ".\migrations\applied.log"

Write-Host "=== Local Stack Health Check ===" -ForegroundColor Cyan

function Fail($msg) {
    Write-Host "❌ $msg" -ForegroundColor Red
    exit 1
}

function Write-DriftLog($message) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $driftLog -Value "[$timestamp] $message"
}

# Ensure drift log path exists
$driftDir = Split-Path -Path $driftLog -Parent
if ($driftDir -and -not (Test-Path $driftDir)) {
    New-Item -ItemType Directory -Path $driftDir -Force | Out-Null
}
if (-not (Test-Path $driftLog)) {
    New-Item -ItemType File -Path $driftLog -Force | Out-Null
}

# 1. Docker Engine running
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Fail "Docker CLI not found in PATH. Please install Docker Desktop or add docker to PATH."
}
if (-not (docker info --format '{{.ServerVersion}}' 2>$null)) {
    Fail "Docker Engine is not running."
}
Write-Host "✅ Docker Engine is running." -ForegroundColor Green

# 2. GraphQL readiness
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
            -Body $pingBody -UseBasicParsing

        if ($resp.StatusCode -eq 200 -and $resp.Content -match '__typename') {
            Write-Host "✅ GraphQL is ready."
            $graphqlHealthy = $true
            break
        }
    } catch {}
    Write-Host "⏳ GraphQL not ready yet... retry $i/$maxRetries"
    Start-Sleep -Seconds $delaySeconds
}

if (-not $graphqlHealthy) {
    Fail "GraphQL endpoint not responding after $($maxRetries * $delaySeconds) seconds."
}

# 3. Check 'profiles' table exists
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

# 4. Schema drift check + auto-apply + logging
if (-Not (Test-Path $goldenSchema)) {
    Write-Host "⚠ Golden schema file not found at $goldenSchema"
} else {
    Write-Host "`n📊 Comparing live DB schema to golden file..."
    try {
        $tempDump = "temp_schema.sql"
        docker exec supabase_db_tx-predictive-intelligence pg_dump `
            -U postgres `
            --schema-only `
            --no-owner `
            --no-privileges postgres | Out-File $tempDump -Encoding UTF8

        $diff = Compare-Object (Get-Content $tempDump) (Get-Content $goldenSchema)

        if ($diff) {
            Write-Host "⚠ Database schema differs from golden reference." -ForegroundColor Yellow
            Write-DriftLog "Schema drift detected."

            $choice = Read-Host "Apply golden schema now? (y/N)"
            if ($choice -match '^[Yy]$') {
                try {
                    Write-Host "📥 Applying $goldenSchema to DB..."
                    Get-Content -Raw $goldenSchema | docker exec -i supabase_db_tx-predictive-intelligence psql `
                        -U postgres -d postgres
                    Write-Host "✅ Schema updated to golden reference." -ForegroundColor Green
                    Write-DriftLog "Applied golden schema."
                } catch {
                    Fail "Error applying golden schema: $_"
                }
            } else {
                Write-DriftLog "Drift detected — not applied by user."
                Fail "Schema drift detected. Aborting."
            }
        } else {
            Write-Host "✅ Database schema matches golden file." -ForegroundColor Green
        }

        Remove-Item $tempDump -ErrorAction SilentlyContinue
    } catch {
        Fail "Could not perform schema diff: $_"
    }
}

Write-Host "`n=== All checks (and fixes) complete! ===" -ForegroundColor Cyan
exit 0
