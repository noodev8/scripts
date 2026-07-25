<#
.SYNOPSIS
    Builds BrookfieldUpdate.zip from the PowerBuilder compile output.

.DESCRIPTION
    Collects brookfieldcomfort.exe plus every *.pbd from the PowerBuilder output
    folder, checks none of them are stale relative to their .pbl source, and
    writes BrookfieldUpdate.zip into that same folder.

    See README.md in this folder.
#>

[CmdletBinding()]
param(
    # PowerBuilder compile output folder. Auto-detected, or set PB_SOURCE_DIR in .env.
    [string]$Source,

    # Build the zip even if a PBD is older than its PBL.
    [switch]$Force,

    # Set by release.ps1 - suppresses the "nothing published" footer, since in
    # that case publishing is about to happen.
    [switch]$FromRelease
)

$ErrorActionPreference = "Stop"

# Anchor on this file, never the working directory (double-click safe).
$RepoRoot = Split-Path -Parent $PSScriptRoot
$EnvFile  = Join-Path $RepoRoot ".env"
. (Join-Path $PSScriptRoot "env_util.ps1")

$ZipName = "BrookfieldUpdate.zip"
$ExeName = "brookfieldcomfort.exe"

function Write-Head($text) { Write-Host ""; Write-Host $text -ForegroundColor Cyan }

# Setup problems are the user's to fix, not bugs - print them plainly and stop,
# rather than burying the instructions in a PowerShell stack trace.
function Fail($text) { Write-Host ""; Write-Host $text -ForegroundColor Yellow; Write-Host ""; exit 1 }

# --- Resolve the machine-dependent folder --------------------------------
if (-not $Source) { $Source = Get-SourceFolder -EnvFile $EnvFile }
if (-not $Source) {
    Fail @"
Could not find the PowerBuilder output folder on this machine.

Looked under your user profile and every drive letter for:
  <root>\My Drive [(noodev8@gmail.com)]\Business\Brookfield Comfort\Powerbuilder
containing $ExeName

Fix by adding the real path to $EnvFile :
  PB_SOURCE_DIR=G:\My Drive\Business\Brookfield Comfort\Powerbuilder
"@
}
if (-not (Test-Path -LiteralPath $Source)) { Fail "Source folder not found: $Source" }

Write-Host "Source: $Source" -ForegroundColor DarkGray

# --- Collect the payload -------------------------------------------------
$exe = Get-Item -LiteralPath (Join-Path $Source $ExeName) -ErrorAction SilentlyContinue
if (-not $exe) { Fail "$ExeName not found in $Source - has the build run?" }

$pbds = @(Get-ChildItem -LiteralPath $Source -Filter "*.pbd" | Sort-Object Name)
if ($pbds.Count -eq 0) { Fail "No .pbd files found in $Source" }

$payload = @($exe) + $pbds

# --- Staleness check -----------------------------------------------------
# A PBD older than its matching PBL means that library was not regenerated in
# this build, so the zip would ship last version's code for it. This is the
# failure mode worth catching: it is silent and only shows up on a client PC.
$stale = @()
foreach ($pbd in $pbds) {
    $pbl = Get-Item -LiteralPath (Join-Path $Source ([IO.Path]::ChangeExtension($pbd.Name, "pbl"))) -ErrorAction SilentlyContinue
    if ($pbl -and $pbd.LastWriteTime -lt $pbl.LastWriteTime) {
        $stale += [pscustomobject]@{
            Library = $pbd.BaseName
            PbdBuilt = $pbd.LastWriteTime
            PblChanged = $pbl.LastWriteTime
            Behind = "{0:n1} min" -f ($pbl.LastWriteTime - $pbd.LastWriteTime).TotalMinutes
        }
    }
}

Write-Head "Payload ($($payload.Count) files)"
$newest = ($payload | Measure-Object LastWriteTime -Maximum).Maximum
$payload |
    Select-Object Name,
        @{n = "Size"; e = { "{0:n0} KB" -f ($_.Length / 1KB) } },
        @{n = "Built"; e = { $_.LastWriteTime.ToString("dd/MM HH:mm:ss") } },
        @{n = "Age vs newest"; e = { $d = ($newest - $_.LastWriteTime).TotalMinutes; if ($d -lt 1) { "-" } else { "{0:n0} min older" -f $d } } } |
    Format-Table -AutoSize | Out-String -Width 200 | Write-Host

if ($stale.Count -gt 0) {
    Write-Head "STALE - these PBDs are older than their PBL source:"
    $stale | Format-Table -AutoSize | Out-String -Width 200 | Write-Host
    if (-not $Force) {
        Write-Host "Rebuild in PowerBuilder, or re-run with -Force to ship anyway." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "-Force given, continuing with stale PBDs." -ForegroundColor Yellow
}

# --- Build the zip -------------------------------------------------------
# Assembled in a temp folder so a failure part-way through never leaves a
# half-written BrookfieldUpdate.zip in the Drive folder. The temp folder is
# removed either way - the only zip kept on disk is the one below, which is
# overwritten on every build rather than accumulating.
$staging = Join-Path ([IO.Path]::GetTempPath()) ("pbdeploy_" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $staging -Force | Out-Null
try {
    foreach ($f in $payload) { Copy-Item -LiteralPath $f.FullName -Destination $staging }

    # Zip written outside the staging folder so it never packages itself.
    $tempZip = Join-Path ([IO.Path]::GetTempPath()) ("pbdeploy_" + [Guid]::NewGuid().ToString("N") + ".zip")
    Compress-Archive -Path (Join-Path $staging "*") -DestinationPath $tempZip -CompressionLevel Optimal

    $target = Join-Path $Source $ZipName
    if (Test-Path -LiteralPath $target) {
        $prev = Get-Item -LiteralPath $target
        Write-Host ("Replacing previous zip from {0:dd/MM HH:mm} ({1:n0} KB)" -f $prev.LastWriteTime, ($prev.Length / 1KB)) -ForegroundColor DarkGray
    }
    Move-Item -LiteralPath $tempZip -Destination $target -Force

    $built = Get-Item -LiteralPath $target
    Write-Head "Built"
    Write-Host ("  {0}  ({1:n0} KB)" -f $built.FullName, ($built.Length / 1KB))
}
finally {
    Remove-Item -LiteralPath $staging -Recurse -Force -ErrorAction SilentlyContinue
    if ($tempZip) { Remove-Item -LiteralPath $tempZip -Force -ErrorAction SilentlyContinue }
}

if (-not $FromRelease) {
    Write-Host ""
    Write-Host "Zip only - nothing published. Use release.bat to build and publish in one go." -ForegroundColor DarkGray
}

# Explicit, so a caller reading $LASTEXITCODE sees this script's result rather
# than a stale value left by whatever ran before it.
exit 0
