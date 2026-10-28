<#
  Signs the Daily Fresh release files with Authenticode (SHA-256 + timestamp).

  Order matters: each file must be signed before anything that wraps it is built.
    1. dist\ExpenseLedger\ExpenseLedger.exe   (sign, then rebuild the MSI files from it)
    2. installer\output\<version>\*.msi                 (sign, then rebuild the Burn setup from the User MSI)
    3. Burn engine inside ExpenseLedger-Setup-*.exe (detach, sign, reattach)
    4. ExpenseLedger-Setup-*.exe              (sign the final file)

  Usage:
    .\sign.ps1 -Stage Exe                       # step 1
    .\sign.ps1 -Stage Msi                       # step 2
    .\sign.ps1 -Stage Setup                     # steps 3 and 4
    .\sign.ps1 -Stage Verify                    # check every signature, print SHA-256 hashes

  Certificate (pick one):
    -Thumbprint <sha1>      certificate in the Windows store (also works for EV hardware tokens)
    -PfxPath <file> -PfxPassword <text>
    -AzureDlib <path to Azure.CodeSigning.Dlib.dll> -AzureMetadata <metadata.json>   (Azure Artifact Signing)
#>
param(
    [Parameter(Mandatory)][ValidateSet('Exe', 'Msi', 'Setup', 'Verify')][string]$Stage,
    [string]$Thumbprint,
    [string]$PfxPath,
    [string]$PfxPassword,
    [string]$AzureDlib,
    [string]$AzureMetadata,
    [string]$TimestampUrl = 'http://timestamp.acs.microsoft.com',
    [string]$Version = ''   # default: APP_VERSION in app\core\config.py
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
if (-not $Version) { $Version = (Select-String -Path (Join-Path $root 'app\core\config.py') -Pattern '^APP_VERSION = "([0-9.]+)"').Matches[0].Groups[1].Value }
$exe = Join-Path $root 'dist\ExpenseLedger\ExpenseLedger.exe'
$out = Join-Path $PSScriptRoot "output\$Version"
$msis = @("$out\ExpenseLedger-$Version.msi", "$out\ExpenseLedger-$Version-CurrentUser.msi", "$out\ExpenseLedger-$Version-AllUsers.msi")
$setup = "$out\ExpenseLedger-Setup-$Version.exe"

function Find-SignTool {
    $cmd = Get-Command signtool.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $found = Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin" -Recurse -Filter signtool.exe -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -like '*\x64\*' } | Sort-Object FullName -Descending | Select-Object -First 1
    if (-not $found) { throw 'signtool.exe not found. Install the Windows SDK (Signing Tools).' }
    return $found.FullName
}

function Sign-File([string]$file) {
    if (-not (Test-Path $file)) { throw "Missing file: $file" }
    $args = @('sign', '/fd', 'SHA256', '/d', 'Daily Fresh', '/td', 'SHA256', '/tr', $TimestampUrl)
    if ($AzureDlib) { $args += @('/dlib', $AzureDlib, '/dmdf', $AzureMetadata) }
    elseif ($Thumbprint) { $args += @('/sha1', $Thumbprint) }
    elseif ($PfxPath) { $args += @('/f', $PfxPath, '/p', $PfxPassword) }
    else { throw 'Give -Thumbprint, -PfxPath, or -AzureDlib.' }
    & $script:signtool @args $file
    if ($LASTEXITCODE -ne 0) { throw "Signing failed: $file" }
}

function Verify-File([string]$file) {
    # A self-signed certificate that this PC does not trust still counts as signed (status UnknownError).
    $sig = Get-AuthenticodeSignature $file
    $ok = ($sig.Status -eq 'Valid') -or ($sig.Status -eq 'UnknownError' -and $sig.SignerCertificate -and $sig.TimeStamperCertificate)
    $hash = (Get-FileHash $file -Algorithm SHA256).Hash
    Write-Host ('{0,-8} {1}  {2}' -f $(if ($sig.Status -eq 'Valid') { 'TRUSTED' } elseif ($ok) { 'SIGNED' } else { 'UNSIGNED' }), $hash, (Split-Path -Leaf $file))
    return $ok
}

$script:signtool = Find-SignTool

switch ($Stage) {
    'Exe' {
        Sign-File $exe
        Write-Host 'Next: rebuild the MSI files from the signed exe (generate_files.py, wix build), then run -Stage Msi.'
    }
    'Msi' {
        $msis | ForEach-Object { Sign-File $_ }
        Write-Host 'Next: rebuild the Burn setup from the signed AllUsers MSI (wix build Bundle.wxs), then run -Stage Setup.'
    }
    'Setup' {
        $engine = Join-Path $env:TEMP 'ExpenseLedger-burn-engine.exe'
        $tmp = Join-Path $env:TEMP 'ExpenseLedger-Setup-unsigned.exe'
        wix burn detach $setup -engine $engine
        if ($LASTEXITCODE -ne 0) { throw 'wix burn detach failed.' }
        Sign-File $engine
        wix burn reattach $setup -engine $engine -o $tmp
        if ($LASTEXITCODE -ne 0) { throw 'wix burn reattach failed.' }
        Move-Item $tmp $setup -Force
        Sign-File $setup
        Remove-Item $engine -ErrorAction SilentlyContinue
    }
    'Verify' {
        $all = @($exe) + $msis + @($setup)
        $bad = 0
        foreach ($f in $all) { if (-not (Verify-File $f)) { $bad++ } }
        if ($bad) { throw "$bad file(s) not signed correctly." }
    }
}
