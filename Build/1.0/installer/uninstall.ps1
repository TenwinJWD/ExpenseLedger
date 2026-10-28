<#
  Daily Fresh - Uninstall (no console window: every question and result is a message box).
  Removes the program that the setup or the .msi installed.
  Your entries (your chosen data folder) and your sub-heads (%APPDATA%\ExpenseLedger) are NOT removed.
  Your login is removed, so the next install asks for a new user and password.
  An all-users install asks for administrator approval (the Windows prompt).
#>
param([switch]$FromTemp)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms

function Show-Box([string]$text, [string]$buttons = 'OK', [string]$icon = 'Information') {
    [System.Windows.Forms.MessageBox]::Show($text, 'Daily Fresh - Uninstall', $buttons, $icon)
}

# The uninstaller deletes the program folder, which contains this file. So the work is done from a copy in the temp folder.
if (-not $FromTemp) {
    $copy = Join-Path $env:TEMP 'ExpenseLedger-uninstall.ps1'
    Copy-Item -LiteralPath $PSCommandPath -Destination $copy -Force
    Start-Process powershell.exe -WindowStyle Hidden -ArgumentList '-NoProfile', '-WindowStyle', 'Hidden', '-ExecutionPolicy', 'Bypass', '-File', "`"$copy`"", '-FromTemp'
    exit 0
}

$question = "Do you want to remove Daily Fresh from this PC?`n`nYour entries and sub-heads are kept. Your login is removed, so the next install asks for a new user and password."
if ((Show-Box $question 'YesNo' 'Question') -ne 'Yes') { exit 0 }

$bundleCode = '{7A1C0E2D-5B3F-4D6A-8E9F-1A2B3C4D5E60}'
$keys = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall',
        'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall',
        'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'

function Get-Entries { Get-ChildItem $keys -ErrorAction SilentlyContinue | Get-ItemProperty -ErrorAction SilentlyContinue }

# An install made with the setup program also registers a bundle entry. When it exists, uninstall through it:
# it removes the program and its own entry together. Otherwise use the .msi's own product entry.
$entries = @(Get-Entries)
$bundle = $entries | Where-Object { @($_.BundleUpgradeCode) -contains $bundleCode } | Select-Object -First 1
$product = $entries | Where-Object { $_.DisplayName -eq 'Daily Fresh' -and $_.WindowsInstaller -eq 1 } | Select-Object -First 1

if (-not $bundle -and -not $product) {
    Show-Box "Daily Fresh is not registered as an installed program on this PC.`n`nIf you run it from a folder without installing, just delete that folder." 'OK' 'Warning' | Out-Null
    exit 1
}

$exitCode = 0
$declined = $false
try {
    if ($bundle) {
        $command = "$($bundle.UninstallString) /quiet /norestart"
        $process = Start-Process cmd.exe -ArgumentList '/c', "`"$command`"" -WindowStyle Hidden -Wait -PassThru
    } else {
        $code = $product.PSChildName
        $machine = $product.PSPath -like '*HKEY_LOCAL_MACHINE*'
        $arguments = @('/x', $code, '/qb', '/norestart')
        if ($machine) { $process = Start-Process msiexec.exe -ArgumentList $arguments -Verb RunAs -Wait -PassThru }
        else { $process = Start-Process msiexec.exe -ArgumentList $arguments -Wait -PassThru }
    }
    $exitCode = $process.ExitCode
} catch {
    $declined = $true   # the administrator prompt was refused
}

# Decide by looking at the result, not only the code: Windows can report an error code after the program has been removed.
$left = @(Get-Entries | Where-Object { $_.DisplayName -eq 'Daily Fresh' })
if ($left.Count -eq 0) {
    Show-Box "Daily Fresh has been uninstalled.`n`nYour entries were kept and the login was removed." 'OK' 'Information' | Out-Null
    exit 0
}
if ($declined -or $exitCode -eq 1602 -or $exitCode -eq 1223) {
    Show-Box 'Uninstall was cancelled. Nothing was removed.' 'OK' 'Information' | Out-Null
    exit 1602
}
Show-Box "The uninstall did not finish (Windows code $exitCode).`n`nTry again, or use Settings > Apps > Installed apps > Daily Fresh > Uninstall." 'OK' 'Warning' | Out-Null
exit $exitCode
