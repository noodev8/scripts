<#
.SYNOPSIS
    Full deploy: build BrookfieldUpdate.zip, then publish it as a GitHub release.

.DESCRIPTION
    Front door for the whole flow. Exists so there is one place that accepts
    every flag and routes each to the step that understands it - build flags to
    build_update.ps1, publish flags to publish_release.ps1.

    Called by release.bat. See README.md in this folder.
#>

[CmdletBinding()]
param(
    # --- build flags ---
    [string]$Source,   # PowerBuilder output folder, this run only
    [switch]$Force,    # build even if a PBD is older than its PBL

    # --- publish flags ---
    [string]$Version,  # override the auto-computed tag
    [string]$Zip,      # publish a specific zip instead of the freshly built one
    [switch]$Yes       # skip the confirmation prompt
)

$ErrorActionPreference = "Stop"

# --- Build ---------------------------------------------------------------
$buildArgs = @{ FromRelease = $true }
if ($Source) { $buildArgs.Source = $Source }
if ($Force)  { $buildArgs.Force  = $true }

# Cleared first: a called script that returns without an explicit `exit` leaves
# whatever value was already there, which would be read as its result.
$global:LASTEXITCODE = 0
& (Join-Path $PSScriptRoot "build_update.ps1") @buildArgs
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Build failed - nothing published." -ForegroundColor Red
    Write-Host ""
    exit $LASTEXITCODE
}

# --- Publish -------------------------------------------------------------
$publishArgs = @{}
if ($Version) { $publishArgs.Version = $Version }
if ($Zip)     { $publishArgs.Zip     = $Zip }
if ($Yes)     { $publishArgs.Yes     = $true }

$global:LASTEXITCODE = 0
& (Join-Path $PSScriptRoot "publish_release.ps1") @publishArgs
exit $LASTEXITCODE
