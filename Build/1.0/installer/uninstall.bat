@echo off
rem ============================================================
rem  Expense Ledger - Uninstall
rem  Removes the program that the .msi installed.
rem  Your entries (Desktop\ExpenseLedger) and your sub-heads
rem  (%APPDATA%\ExpenseLedger) are NOT removed. Your login is removed,
rem  so the next install asks for a new user and password.
rem  No administrator rights are needed (per-user install).
rem ============================================================
setlocal
title Expense Ledger - Uninstall

rem The uninstaller deletes the program folder, which contains this file. So the
rem work is done from a copy in the temp folder, in its own window.
if /i not "%~1"=="--from-temp" (
    copy /y "%~f0" "%TEMP%\ExpenseLedger-uninstall.bat" >nul
    start "Expense Ledger - Uninstall" "%TEMP%\ExpenseLedger-uninstall.bat" --from-temp
    exit /b 0
)

echo This removes Expense Ledger from this PC.
echo Your entries and sub-heads are kept. Your login is removed.
echo.
set /p CONFIRM=Type Y and press Enter to uninstall, or press Enter to cancel:
if /i not "%CONFIRM%"=="Y" (
    echo Uninstall cancelled. Nothing was changed.
    pause
    exit /b 0
)

rem An install made with the setup program also registers a bundle entry. When it exists,
rem uninstall through that entry: it removes the program and its own entry together.
set "BUNDLE_UNINSTALL="
for /f "usebackq delims=" %%G in (`powershell -NoProfile -Command "Get-ChildItem 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall','HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall' -ErrorAction SilentlyContinue | Get-ItemProperty | Where-Object { $_.BundleUpgradeCode -eq '{7A1C0E2D-5B3F-4D6A-8E9F-1A2B3C4D5E60}' } | Select-Object -First 1 -ExpandProperty UninstallString"`) do set "BUNDLE_UNINSTALL=%%G"

rem Otherwise find the product code of the .msi install, registered as a Windows Installer product.
rem It is looked up in the current user's list, the machine list and the 32-bit machine list.
set "PRODUCT_CODE="
if not defined BUNDLE_UNINSTALL (
    for /f "usebackq delims=" %%G in (`powershell -NoProfile -Command "Get-ChildItem 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall','HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall' -ErrorAction SilentlyContinue | Get-ItemProperty | Where-Object { $_.DisplayName -eq 'Expense Ledger' -and $_.WindowsInstaller -eq 1 } | Select-Object -First 1 -ExpandProperty PSChildName"`) do set "PRODUCT_CODE=%%G"
)

if not defined BUNDLE_UNINSTALL if not defined PRODUCT_CODE (
    echo Expense Ledger is not registered as an installed program on this PC.
    echo If you run it from a folder without installing, just delete that folder.
    pause
    exit /b 1
)

if defined BUNDLE_UNINSTALL (
    echo Uninstalling Expense Ledger ...
    call %BUNDLE_UNINSTALL% /quiet /norestart
) else (
    echo Uninstalling %PRODUCT_CODE% ...
    msiexec /x "%PRODUCT_CODE%"
)
set "RESULT=%errorlevel%"

rem Decide by looking at the result, not only the code: Windows can report an error
rem code after the program has already been removed.
set "LEFT="
for /f "usebackq delims=" %%G in (`powershell -NoProfile -Command "Get-ChildItem 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall','HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall' -ErrorAction SilentlyContinue | Get-ItemProperty | Where-Object { $_.DisplayName -eq 'Expense Ledger' } | Select-Object -First 1 -ExpandProperty PSChildName"`) do set "LEFT=%%G"

if not defined LEFT (
    echo.
    echo Expense Ledger has been uninstalled. Your entries were kept and the login was removed.
    set "RESULT=0"
) else if "%RESULT%"=="1602" (
    echo.
    echo Uninstall was cancelled. Nothing was removed.
) else (
    echo.
    echo The uninstall did not finish. Windows returned code %RESULT%.
    echo Try again, or use Settings ^> Apps ^> Installed apps ^> Expense Ledger ^> Uninstall.
)

pause
exit /b %RESULT%
