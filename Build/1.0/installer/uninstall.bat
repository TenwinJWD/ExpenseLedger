@echo off
rem ============================================================
rem  Daily Fresh - Uninstall
rem  Starts uninstall.ps1, which asks for confirmation in a window
rem  (no terminal). Your entries (your chosen data folder) and your
rem  sub-heads (%APPDATA%\ExpenseLedger) are NOT removed. Your login is removed.
rem  An all-users install asks for administrator approval.
rem ============================================================
start "" powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0uninstall.ps1"
exit /b 0
