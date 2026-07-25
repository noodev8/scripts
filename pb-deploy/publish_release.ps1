<#
.SYNOPSIS
    Publishes BrookfieldUpdate.zip as a new GitHub release on
    brookfielduser1/BrookfieldApp.

.DESCRIPTION
    Works out the next version tag from the existing releases, creates the
    release, and uploads the zip as its single asset. Authenticates with
    GITHUB_TOKEN from the repo-root .env.

    See README.md in this folder.
#>

[CmdletBinding()]
param(
    # Zip to upload. Defaults to the one build_update.ps1 writes.
    [string]$Zip,

    # Override the auto-computed tag, e.g. -Version v3.00
    [string]$Version,

    # Skip the confirmation prompt (for unattended use).
    [switch]$Yes
)

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Owner     = "brookfielduser1"
$Repo      = "BrookfieldApp"
$AssetName = "BrookfieldUpdate.zip"   # fixed - clients fetch this exact name

# Anchor on this file, never the working directory (cron/double-click safe).
$RepoRoot = Split-Path -Parent $PSScriptRoot
$EnvFile  = Join-Path $RepoRoot ".env"
. (Join-Path $PSScriptRoot "env_util.ps1")

function Write-Head($text) { Write-Host ""; Write-Host $text -ForegroundColor Cyan }

# Setup problems are the user's to fix, not bugs - print them plainly and stop,
# rather than burying the instructions in a PowerShell stack trace.
function Fail($text) { Write-Host ""; Write-Host $text -ForegroundColor Yellow; Write-Host ""; exit 1 }

# --- Token ---------------------------------------------------------------
if (-not (Test-Path -LiteralPath $EnvFile)) { Fail ".env not found at $EnvFile" }

$token = Get-DotEnvValue -Name "GITHUB_TOKEN" -Path $EnvFile
if (-not $token) {
    Fail @"
GITHUB_TOKEN not found in $EnvFile

Create a fine-grained personal access token on the '$Owner' account:
  github.com/settings/personal-access-tokens  ->  Generate new token
  Repository access: only $Owner/$Repo
  Permissions: Contents = Read and write
Then add this line to .env:
  GITHUB_TOKEN=github_pat_...
"@
}

$headers = @{
    Authorization          = "Bearer $token"
    Accept                 = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
    "User-Agent"           = "pb-deploy"
}

# --- The zip -------------------------------------------------------------
if (-not $Zip) {
    $sourceDir = Get-SourceFolder -EnvFile $EnvFile
    if (-not $sourceDir) { Fail "Could not find the PowerBuilder folder on this machine. Set PB_SOURCE_DIR in $EnvFile" }
    $Zip = Join-Path $sourceDir $AssetName
}
if (-not (Test-Path -LiteralPath $Zip)) {
    Fail "Zip not found: $Zip`nRun release.bat, which builds the zip before publishing it."
}
$zipFile = Get-Item -LiteralPath $Zip

# --- Work out the next tag ----------------------------------------------
Write-Head "Reading existing releases from $Owner/$Repo"
try {
    $releases = Invoke-RestMethod -Uri "https://api.github.com/repos/$Owner/$Repo/releases?per_page=100" -Headers $headers
}
catch {
    Fail "Could not read releases: $($_.Exception.Message)`nCheck GITHUB_TOKEN is valid and has Contents access to $Owner/$Repo."
}

# Tags look like v2.16 - major.minor with a zero-padded 2-digit minor.
$parsed = @($releases |
    Where-Object { $_.tag_name -match '^v(\d+)\.(\d+)$' } |
    ForEach-Object {
        $null = $_.tag_name -match '^v(\d+)\.(\d+)$'
        [pscustomobject]@{
            Tag       = $_.tag_name
            Major     = [int]$Matches[1]
            Minor     = [int]$Matches[2]
            Published = $_.published_at
        }
    } | Sort-Object Major, Minor)

$latest = $parsed | Select-Object -Last 1
if ($latest) { Write-Host "  Latest release: $($latest.Tag)" }

if ($Version) {
    $tag = $Version
}
elseif (-not $latest) {
    Fail "No existing vN.NN release found to increment from. Pass -Version explicitly."
}
elseif ($latest.Minor -ge 99) {
    # Padding to 2 digits breaks past 99; a major bump is a human decision.
    Fail "Latest tag is $($latest.Tag) - minor is at its limit. Pass -Version explicitly, e.g. -Version v$($latest.Major + 1).00"
}
else {
    $tag = "v{0}.{1:d2}" -f $latest.Major, ($latest.Minor + 1)
}

if ($releases | Where-Object { $_.tag_name -eq $tag }) {
    Fail "Release $tag already exists. Pass a different -Version."
}

# --- Has anything been compiled since the last release? -------------------
# The zip's own timestamp is useless here - it is rebuilt every run, so it is
# always "now". The compiled output is what carries the answer: if no PBD is
# newer than the last release, nothing has been compiled since, so there is
# nothing new to ship.
#
# One-directional on purpose. It can prove nothing changed; it cannot prove
# something did, because recompiling untouched source still bumps the PBD
# timestamps. So it warns and lets you decide - it never blocks.
$nothingNew = $false
if ($latest -and $latest.Published) {
    $compiled = @(Get-ChildItem -LiteralPath (Split-Path -Parent $zipFile.FullName) -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -in @(".pbd", ".exe") })
    if ($compiled.Count -gt 0) {
        $newestBuild = ($compiled | Measure-Object LastWriteTime -Maximum).Maximum
        $lastRelease = ([datetime]$latest.Published).ToLocalTime()
        if ($newestBuild -le $lastRelease) { $nothingNew = $true }
    }
}

# --- Confirm -------------------------------------------------------------
Write-Head "About to publish"
Write-Host "  Repo    : $Owner/$Repo"
Write-Host "  Tag     : $tag"
Write-Host ("  Asset   : {0}  ({1:n0} KB, built {2:dd/MM HH:mm})" -f $AssetName, ($zipFile.Length / 1KB), $zipFile.LastWriteTime)

if ($nothingNew) {
    Write-Host ""
    Write-Host ("  NOTE: nothing has been compiled since {0} went out ({1:dd/MM HH:mm})." -f $latest.Tag, ([datetime]$latest.Published).ToLocalTime()) -ForegroundColor Yellow
    Write-Host "        This would republish the same build under a new version number." -ForegroundColor Yellow
}

if (-not $Yes) {
    Write-Host ""
    $answer = Read-Host "Publish this release? (y/N)"
    if ($answer -notmatch '^[Yy]') {
        Write-Host "Cancelled - nothing was published." -ForegroundColor Yellow
        exit 2
    }
}

# --- Create the release --------------------------------------------------
$body = @{
    tag_name = $tag
    name     = $tag
    body     = ""
    draft    = $false
    prerelease = $false
} | ConvertTo-Json

Write-Head "Creating release $tag"
$release = Invoke-RestMethod -Method Post -Uri "https://api.github.com/repos/$Owner/$Repo/releases" `
    -Headers $headers -Body $body -ContentType "application/json"

# --- Upload the asset ----------------------------------------------------
# If this fails the release exists but is empty, which would look like a valid
# release with nothing to download - so delete it rather than leave that behind.
Write-Host "Uploading $AssetName ..."
try {
    $uploadUri = "https://uploads.github.com/repos/$Owner/$Repo/releases/$($release.id)/assets?name=$AssetName"
    $asset = Invoke-RestMethod -Method Post -Uri $uploadUri -Headers $headers `
        -InFile $zipFile.FullName -ContentType "application/zip"
}
catch {
    Write-Host "Upload failed - removing the empty release $tag" -ForegroundColor Yellow
    try {
        Invoke-RestMethod -Method Delete -Uri "https://api.github.com/repos/$Owner/$Repo/releases/$($release.id)" -Headers $headers | Out-Null
        Write-Host "Empty release removed." -ForegroundColor Yellow
    }
    catch {
        Write-Host "Could not remove release $tag - delete it by hand at $($release.html_url)" -ForegroundColor Red
    }
    throw
}

# --- Verify ---------------------------------------------------------------
# Read the release back from GitHub rather than trusting the upload response,
# so the pass/fail below reflects what is actually on the releases page. This is
# the answer to "did it work?" - no need to go and look.
Write-Head "Verifying on GitHub"
$checks = @()
try {
    $live = Invoke-RestMethod -Uri "https://api.github.com/repos/$Owner/$Repo/releases/tags/$tag" -Headers $headers
    $liveAsset = $live.assets | Where-Object { $_.name -eq $AssetName } | Select-Object -First 1

    $checks += [pscustomobject]@{ Check = "Release $tag exists"; Result = if ($live.tag_name -eq $tag) { "PASS" } else { "FAIL" } }
    $checks += [pscustomobject]@{ Check = "Not a draft"; Result = if (-not $live.draft) { "PASS" } else { "FAIL" } }
    $checks += [pscustomobject]@{ Check = "Asset $AssetName present"; Result = if ($liveAsset) { "PASS" } else { "FAIL" } }
    $checks += [pscustomobject]@{ Check = "Asset fully uploaded"; Result = if ($liveAsset -and $liveAsset.state -eq "uploaded") { "PASS" } else { "FAIL" } }
    $checks += [pscustomobject]@{ Check = "Size matches local zip"; Result = if ($liveAsset -and $liveAsset.size -eq $zipFile.Length) { "PASS" } else { "FAIL" } }
}
catch {
    $checks += [pscustomobject]@{ Check = "Read release back"; Result = "FAIL - $($_.Exception.Message)" }
}

$checks | Format-Table -AutoSize | Out-String -Width 200 | Write-Host

if ($checks | Where-Object { $_.Result -ne "PASS" }) {
    Write-Host "PUBLISH INCOMPLETE - check the release page by hand:" -ForegroundColor Red
    Write-Host "  $($release.html_url)"
    Write-Host ""
    exit 1
}

Write-Host "$tag published and verified." -ForegroundColor Green
Write-Host ("  {0}  ({1:n0} KB)" -f $asset.name, ($asset.size / 1KB))
Write-Host "  $($release.html_url)"
Write-Host ""

# Explicit, so a caller reading $LASTEXITCODE sees this script's result rather
# than a stale value left by whatever ran before it.
exit 0
