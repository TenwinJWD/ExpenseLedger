<#
  Builds the whole release: tests, dependency audit, PyInstaller, MSI files, the setup wizard, and signing.
  Run from Build\1.0:   .\build.ps1 -Thumbprint <sha1>      (add -SkipSign for an unsigned test build)
  Needs: .venv with requirements-dev.txt, WiX 4 (dotnet tool "wix") for the MSI files, Inno Setup 6 for the setup wizard
  (winget install JRSoftware.InnoSetup), and the Windows SDK signtool for signing.
#>
param(
    [string]$Thumbprint,
    [string]$PfxPath,
    [string]$PfxPassword,
    [string]$AzureDlib,
    [string]$AzureMetadata,
    [switch]$SkipSign,
    [string]$Version = ''   # default: APP_VERSION in app\core\config.py, the one place the version is set
)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$utf8 = New-Object System.Text.UTF8Encoding($false)
function Read-Text([string]$path) { [System.IO.File]::ReadAllText((Resolve-Path $path), $utf8) }
function Write-Text([string]$path, [string]$text) { [System.IO.File]::WriteAllText((Join-Path $PWD $path), $text, $utf8) }

# The version comes from -Version, or from APP_VERSION in app\core\config.py when -Version is not given.
if (-not $Version) {
    $match = Select-String -Path 'app\core\config.py' -Pattern '^APP_VERSION = "([0-9.]+)"'
    if (-not $match) { throw 'APP_VERSION not found in app\core\config.py' }
    $Version = $match.Matches[0].Groups[1].Value
}
if ($Version -notmatch '^\d+\.\d+\.\d+$') { throw "Version must look like 1.2.3, not '$Version'." }
Write-Host "Building version $Version" -ForegroundColor Cyan

# Make every place that carries the version agree with it, so the app, the exe properties, the installers and the tests match.
$config = Read-Text 'app\core\config.py'
$config = $config -replace '(?m)^APP_VERSION = "[0-9.]+"', "APP_VERSION = `"$Version`""
Write-Text 'app\core\config.py' $config

$v4 = "$Version.0"
$info = Read-Text 'version_info.txt'
$info = $info -replace '(filevers|prodvers)=\([0-9, ]+\)', ('$1=(' + ($v4 -replace '\.', ', ') + ')')
$info = $info -replace "(FileVersion|ProductVersion)', u'[0-9.]+'", ('$1' + "', u'$v4'")
Write-Text 'version_info.txt' $info

# A release needs a changelog entry (a test checks it). If there is none yet, add a short one to fill in.
$changelogPath = '..\..\CHANGELOG.md'
$changelog = Read-Text $changelogPath
if ($changelog -notmatch "(?m)^## $([regex]::Escape($Version))\b") {
    $today = (Get-Date).ToString('dd-MMM-yyyy', [System.Globalization.CultureInfo]::InvariantCulture)
    $dash = [string][char]0x2013
    $newline = if ($changelog.Contains("`r`n")) { "`r`n" } else { "`n" }
    $stub = "## $Version $dash $today$newline${newline}### Changed$newline- Release $Version.$newline$newline"
    $changelog = [regex]::Replace($changelog, '(?m)^## ', { param($m) $stub + '## ' }, 1)
    Write-Text $changelogPath $changelog
    Write-Host "Added a stub entry for $Version to CHANGELOG.md. Edit it to describe what changed." -ForegroundColor Yellow
}
$py = '.\.venv\Scripts\python.exe'
$iscc = (Get-Command ISCC.exe -ErrorAction SilentlyContinue).Source
if (-not $iscc) {
    $iscc = @("$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe", "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe", "$env:ProgramFiles\Inno Setup 6\ISCC.exe") |
        Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $iscc) { throw 'Inno Setup 6 not found. Install it with: winget install JRSoftware.InnoSetup' }
$wix = (Get-Command wix -ErrorAction SilentlyContinue).Source
if (-not $wix) { $wix = Join-Path $env:USERPROFILE '.dotnet\tools\wix.exe' }
# Each version has its own folder, created by the build: the installers go in it, and so do the build files
# (the PyInstaller output and work files, and the .wixpdb files) in its work subfolder.
# Building the same version again replaces that folder; other versions are left alone.
$out = "installer\output\$Version"
$work = "$out\work"
$all = @{ Thumbprint = $Thumbprint; PfxPath = $PfxPath; PfxPassword = $PfxPassword; AzureDlib = $AzureDlib; AzureMetadata = $AzureMetadata; Version = $Version }
$signArgs = @{}
foreach ($k in $all.Keys) { if ($all[$k]) { $signArgs[$k] = $all[$k] } }

function Step([string]$name, [scriptblock]$run) {
    Write-Host "== $name" -ForegroundColor Cyan
    & $run
    if ($LASTEXITCODE -ne 0) { throw "Step failed: $name" }
}
function Sign([string]$stage) { if (-not $SkipSign) { & .\installer\sign.ps1 -Stage $stage @signArgs } }

if (-not $SkipSign -and -not ($Thumbprint -or $PfxPath -or $AzureDlib)) { throw 'Give a certificate option, or use -SkipSign.' }
if (Test-Path $out) { Remove-Item $out -Recurse -Force }
New-Item -ItemType Directory -Force $out, $work | Out-Null
$dist = Join-Path (Resolve-Path $work) 'dist'

Step 'Tests' { & $py -m pytest -q }
Step 'Dependency audit' { & $py -m pip_audit -r requirements.txt }
Step 'PyInstaller' { & $py -m PyInstaller ExpenseLedger.spec --noconfirm --distpath $dist --workpath (Join-Path (Resolve-Path $work) 'pyinstaller') }
Sign 'Exe'

Push-Location installer
try {
    Step 'Files.wxs' { & ..\$py generate_files.py (Join-Path $dist 'ExpenseLedger') }
    Step 'MSI (all users choice)' { & $wix build Product.wxs Files.wxs -arch x64 -ext WixToolset.UI.wixext -d Mode=Dual -d PackageScope=perMachine -d AppVersion=$Version -bindpath ..\assets -bindpath . -o "output\$Version\ExpenseLedger-$Version.msi" }
    Step 'MSI (all users)' { & $wix build Product.wxs Files.wxs -arch x64 -d Mode=Machine -d PackageScope=perMachine -d AppVersion=$Version -bindpath ..\assets -bindpath . -o "output\$Version\ExpenseLedger-$Version-AllUsers.msi" }
    Step 'MSI (current user)' { & $wix build Product.wxs Files.wxs -arch x64 -d Mode=User -d PackageScope=perUser -d AppVersion=$Version -bindpath ..\assets -bindpath . -o "output\$Version\ExpenseLedger-$Version-CurrentUser.msi" }
} finally { Pop-Location }
Sign 'Msi'

Push-Location installer
try {
    Step 'Setup wizard' { & $iscc /Qp "/DAppVersion=$Version" "/DDistDir=$(Join-Path $dist 'ExpenseLedger')" "/O$((Resolve-Path "output\$Version").Path)" DailyFresh.iss }
} finally { Pop-Location }
Sign 'Setup'
Get-ChildItem $out -Filter *.wixpdb | Move-Item -Destination $work -Force
if (-not $SkipSign) { & .\installer\sign.ps1 -Stage Verify @signArgs }

Get-ChildItem $out -Include *.msi, *Setup*.exe -Recurse | Get-FileHash -Algorithm SHA256 | ForEach-Object { '{0}  {1}' -f $_.Hash, (Split-Path -Leaf $_.Path) }
