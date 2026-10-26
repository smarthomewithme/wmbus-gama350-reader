# Windows PowerShell 5.1+ / PowerShell 7; no firmware flashing.
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Sha = 'a732dd0e52c48973fad57e4950a11d8e2f2d6820'
$Dest = Join-Path $Root 'vendor\upstream'
$Patch = Join-Path $Root 'patches\0001-safe-packet-decoder-and-cc1101-fifo.patch'
if (Test-Path -LiteralPath $Dest) { throw "Refusing to modify existing directory: $Dest" }
New-Item -ItemType Directory -Path (Join-Path $Root 'vendor') -Force | Out-Null
& git clone 'https://github.com/SzczepanLeon/esphome-components.git' $Dest
if ($LASTEXITCODE -ne 0) { throw 'Git clone failed' }
& git -C $Dest checkout --detach $Sha
if ($LASTEXITCODE -ne 0) { throw 'Pinned checkout failed' }
$Actual = (& git -C $Dest rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $Actual -ne $Sha) { throw "Unexpected upstream SHA: $Actual" }
& git -C $Dest apply --check $Patch
if ($LASTEXITCODE -ne 0) { throw 'Patch preflight failed' }
& git -C $Dest apply $Patch
if ($LASTEXITCODE -ne 0) { throw 'Patch apply failed' }
Write-Host "Candidate prepared using upstream: $Actual" -ForegroundColor Green
& git -C $Dest diff --stat
