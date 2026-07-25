@echo off
REM Double-click this, or run it from cmd from any folder.
REM %~dp0 is this file's own folder, so the working directory does not matter.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_update.ps1" %*
echo.
echo Exit code: %errorlevel%
echo.
pause
