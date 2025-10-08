param(
  [Parameter(Mandatory=$true)][string]$FilePath,
  [Parameter(Mandatory=$true)][string]$StartMarker,
  [Parameter(Mandatory=$true)][string]$EndMarker,
  [Parameter(Mandatory=$true)][string]$InsertPath
)
$ErrorActionPreference='Stop'
if (!(Test-Path $FilePath)) { throw "File not found: $FilePath" }
if (!(Test-Path $InsertPath)) { throw "Insert file not found: $InsertPath" }
$content = Get-Content -Path $FilePath -Raw
$startIdx = $content.IndexOf($StartMarker)
if ($startIdx -lt 0) { throw "Start marker not found: $StartMarker" }
$endIdx = $content.IndexOf($EndMarker, $startIdx)
if ($endIdx -lt 0) { throw "End marker not found: $EndMarker" }
$before = $content.Substring(0, $startIdx)
$after = $content.Substring($endIdx)
$block = Get-Content -Path $InsertPath -Raw
$new = $before + $block + $after
[System.IO.File]::WriteAllText($FilePath, $new, [System.Text.Encoding]::UTF8)
Write-Host "Replaced content between markers successfully."
