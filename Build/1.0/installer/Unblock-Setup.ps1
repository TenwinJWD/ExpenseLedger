<#
  Lets Windows run the Daily Fresh setup without the SmartScreen "unknown publisher" block, on a PC you control.

  Put this file (and Unblock-Setup.bat) in the same folder as ExpenseLedger-Setup-<version>.exe and run
  Unblock-Setup.bat, or from PowerShell:
      .\Unblock-Setup.ps1                          # unblock the setup EXE next to this script
      .\Unblock-Setup.ps1 -Path D:\Share\ExpenseLedger-Setup-1.0.2.exe
      .\Unblock-Setup.ps1 -TrustCertificate        # also trust TenwinJames-CodeSigning.cer (needs Administrator)

  Unblocking removes the "downloaded from the internet" mark from that one file, the same as ticking Unblock in
  the file's Properties. It does not change any Windows security setting.

  -TrustCertificate adds the developer's certificate to this PC's Trusted Publishers and Trusted Root stores, so a
  setup signed with it shows "Tenwin James" as the publisher. Use it only for a .cer you received from the
  developer yourself, and only on PCs you manage: anything signed with that certificate is then trusted.
#>
param(
    [string]$Path,
    [switch]$TrustCertificate
)

$ErrorActionPreference = 'Stop'

if (-not $Path) {
    $found = Get-ChildItem $PSScriptRoot -Filter 'ExpenseLedger-Setup-*.exe' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $found) { throw "No ExpenseLedger-Setup-*.exe next to this script. Give the file with -Path." }
    $Path = $found.FullName
}
if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "File not found: $Path" }

Unblock-File -LiteralPath $Path
$stillBlocked = $null -ne (Get-Item -LiteralPath $Path -Stream Zone.Identifier -ErrorAction SilentlyContinue)
if ($stillBlocked) { throw "Windows still marks the file as downloaded. Right-click it > Properties > Unblock." }
Write-Host "Unblocked: $Path" -ForegroundColor Green

if ($TrustCertificate) {
    $admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $admin) { throw 'Trusting the certificate needs Administrator. Open PowerShell as administrator and run: .\Unblock-Setup.ps1 -TrustCertificate' }
    $cer = Join-Path $PSScriptRoot 'TenwinJames-CodeSigning.cer'
    if (-not (Test-Path $cer)) { throw "Certificate file not found: $cer" }
    $thumb = (New-Object System.Security.Cryptography.X509Certificates.X509Certificate2 $cer).Thumbprint
    Write-Host "Certificate thumbprint: $thumb"
    Write-Host 'Check it matches the thumbprint the developer gave you before continuing.' -ForegroundColor Yellow
    if ((Read-Host 'Type YES to trust this certificate') -ne 'YES') { Write-Host 'Certificate not added.'; return }
    foreach ($store in 'TrustedPublisher', 'Root') {
        Import-Certificate -FilePath $cer -CertStoreLocation "Cert:\LocalMachine\$store" | Out-Null
    }
    Write-Host 'Certificate trusted on this PC.' -ForegroundColor Green
}
