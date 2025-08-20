# Define variables
$endpoint = "http://127.0.0.1:54321/graphql/v1"
$apikey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpxcmVsZmRtZHJ3d3hyZm9jbHpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ1MTU1MDAsImV4cCI6MjA3MDA5MTUwMH0.Uebb9Xk8AESgapG95JbX0LoxlO-XCFUlTn6nrXCe1c8"
$query = '{ "__schema": { "types": { "name": true } } }'

# Format payload
$body = @{
    query = "{ __schema { types { name } } }"
} | ConvertTo-Json -Compress

# Send request
$response = Invoke-RestMethod -Uri $endpoint -Method Post -Headers @{
    "apikey" = $apikey
    "Content-Type" = "application/json"
} -Body $body

# Output result
$response | ConvertTo-Json -Depth 10
