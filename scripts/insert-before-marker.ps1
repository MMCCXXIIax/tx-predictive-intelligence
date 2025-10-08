param(
    [Parameter(Mandatory=$true)][string]$FilePath,
    [Parameter(Mandatory=$true)][string]$Marker,
    [Parameter(Mandatory=$true)][string]$InsertPath
)
$ErrorActionPreference = 'Stop'
if (!(Test-Path -Path $FilePath)) { throw "File not found: $FilePath" }
if (!(Test-Path -Path $InsertPath)) { throw "Insert file not found: $InsertPath" }
$content = Get-Content -Path $FilePath -Raw -ErrorAction Stop
$idx = $content.IndexOf($Marker)
if ($idx -lt 0) { throw "Marker not found in file: $Marker" }
$before = $content.Substring(0, $idx)
$after  = $content.Substring($idx)
$block = Get-Content -Path $InsertPath -Raw -ErrorAction Stop
$new = $before + $block + [Environment]::NewLine + $after
[System.IO.File]::WriteAllText($FilePath, $new, [System.Text.Encoding]::UTF8)
Write-Host "Inserted block before marker successfully."
