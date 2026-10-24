@echo off
rem ============================================================
rem  Expense Ledger - Uninstall
rem  Removes the program that the .msi installed.
rem  Your entries (Documents\ExpenseLedger) and your login
rem  (%APPDATA%\ExpenseLedger) are NOT removed. Delete them by
rem  hand only if you no longer need them.
rem  Windows asks for administrator permission (UAC) when needed.
rem ============================================================
setlocal
title Expense Ledger - Uninstall

echo This removes Expense Ledger from this PC.
echo Your entries and your login are kept.
echo.
set /p CONFIRM=Type Y and press Enter to uninstall, or press Enter to cancel:
if /i not "%CONFIRM%"=="Y" (
    echo Uninstall cancelled. Nothing was changed.
    pause
    exit /b 0
)

rem Find the product code that the installer registered for "Expense Ledger".
rem It is looked up in both the 64-bit and 32-bit uninstall lists.
set "PRODUCT_CODE="
for /f "usebackq delims=" %%G in (`powershell -NoProfile -Command "Get-ChildItem 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall' -ErrorAction SilentlyContinue | Get-ItemProperty | Where-Object { $_.DisplayName -eq 'Expense Ledger' } | Select-Object -First 1 -ExpandProperty PSChildName"`) do set "PRODUCT_CODE=%%G"

if not defined PRODUCT_CODE (
    echo Expense Ledger is not registered as an installed program on this PC.
    echo If you run it from a folder without installing, just delete that folder.
    pause
    exit /b 1
)

echo Uninstalling %PRODUCT_CODE% ...
start /wait msiexec /x %PRODUCT_CODE%
set "RESULT=%errorlevel%"

if "%RESULT%"=="0" (
    echo.
    echo Expense Ledger has been uninstalled. Your data was kept.
) else if "%RESULT%"=="1605" (
    echo.
    echo Expense Ledger was already removed.
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
