<#
Shared helpers for pb-deploy. Dot-sourced by build_update.ps1 and
publish_release.ps1 - not run directly.

Everything here exists so the same scripts work unchanged on both machines
(laptop and PC), which mount the Google Drive folder at different paths.
#>

# Read one key from the repo-root .env. Last occurrence wins. Returns $null if
# absent or blank, so callers can fall back with `??`-style logic.
function Get-DotEnvValue {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$Path
    )
    if (-not (Test-Path -LiteralPath $Path)) { return $null }

    $value = $null
    foreach ($line in Get-Content -LiteralPath $Path) {
        if ($line -match "^\s*$([regex]::Escape($Name))\s*=\s*(.*?)\s*$") {
            $value = $Matches[1].Trim([char]34, [char]39)
        }
    }
    if ([string]::IsNullOrWhiteSpace($value)) { return $null }
    return $value
}

# Where PowerBuilder drops the compiled exe and PBDs.
# Machine-dependent: the laptop has it under the user profile, a drive-letter
# Google Drive mount puts it under something like G:\My Drive\...
function Get-SourceFolder {
    param([string]$EnvFile)

    $fromEnv = Get-DotEnvValue -Name "PB_SOURCE_DIR" -Path $EnvFile
    if ($fromEnv) { return $fromEnv }

    $tail = "Business\Brookfield Comfort\Powerbuilder"
    $candidates = New-Object System.Collections.Generic.List[string]

    # Mirrored-into-profile layout (this laptop).
    $candidates.Add((Join-Path $env:USERPROFILE "My Drive (noodev8@gmail.com)\$tail"))

    # Drive-letter mounts, e.g. G:\My Drive\... - check every fixed/removable root.
    foreach ($drive in (Get-PSDrive -PSProvider FileSystem -ErrorAction SilentlyContinue)) {
        foreach ($myDrive in @("My Drive", "My Drive (noodev8@gmail.com)")) {
            $candidates.Add((Join-Path $drive.Root "$myDrive\$tail"))
        }
    }

    # A folder only counts if the exe is actually in it - guards against
    # matching an empty or stale copy of the tree.
    foreach ($c in $candidates) {
        if (Test-Path -LiteralPath (Join-Path $c "brookfieldcomfort.exe")) { return $c }
    }

    return $null
}
