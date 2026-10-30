@echo off
rem Double-click to unblock ExpenseLedger-Setup-*.exe in this folder. See Unblock-Setup.ps1.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Unblock-Setup.ps1" %*
echo.
pause
