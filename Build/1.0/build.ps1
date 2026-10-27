<#
  Builds the whole release: tests, dependency audit, PyInstaller, MSI files, setup EXE, and signing.
  Run from Build\1.0:   .\build.ps1 -Thumbprint <sha1>      (add -SkipSign for an unsigned test build)
  Needs: .venv with requirements-dev.txt, WiX 4 (dotnet tool "wix"), and the Windows SDK signtool for signing.
#>
param(
    [string]$Thumbprint,
    [string]$PfxPath,
    [string]$PfxPassword,
    [string]$AzureDlib,
    [string]$AzureMetadata,
    [switch]$SkipSign,
    [string]$Version = '1.0.0'
)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$py = '.\.venv\Scripts\python.exe'
$wix = (Get-Command wix -ErrorAction SilentlyContinue).Source
if (-not $wix) { $wix = Join-Path $env:USERPROFILE '.dotnet\tools\wix.exe' }
$out = 'installer\output'
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
New-Item -ItemType Directory -Force $out | Out-Null

Step 'Tests' { & $py -m pytest -q }
Step 'Dependency audit' { & $py -m pip_audit -r requirements.txt }
Step 'PyInstaller' { & $py -m PyInstaller ExpenseLedger.spec --noconfirm }
Sign 'Exe'

Push-Location installer
try {
    Step 'Files.wxs' { & ..\$py generate_files.py }
    Step 'MSI (all users choice)' { & $wix build Product.wxs Files.wxs -arch x64 -ext WixToolset.UI.wixext -d Mode=Dual -d PackageScope=perMachine -bindpath ..\assets -bindpath . -o "output\ExpenseLedger-$Version.msi" }
    Step 'MSI (current user)' { & $wix build Product.wxs Files.wxs -arch x64 -d Mode=User -d PackageScope=perUser -bindpath ..\assets -bindpath . -o "output\ExpenseLedger-$Version-CurrentUser.msi" }
} finally { Pop-Location }
Sign 'Msi'

Push-Location installer
try {
    Step 'Setup EXE' { & $wix build Bundle.wxs -ext WixToolset.Bal.wixext -bindpath . -bindpath output -bindpath ..\assets -o "output\ExpenseLedger-Setup-$Version.exe" }
} finally { Pop-Location }
Sign 'Setup'
if (-not $SkipSign) { & .\installer\sign.ps1 -Stage Verify @signArgs }

Get-ChildItem $out -Include *.msi, *Setup*.exe -Recurse | Get-FileHash -Algorithm SHA256 | ForEach-Object { '{0}  {1}' -f $_.Hash, (Split-Path -Leaf $_.Path) }
