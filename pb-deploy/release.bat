@echo off
REM Full deploy: build the zip, then publish it as a new GitHub release.
REM Double-click this, or run it from cmd from any folder.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0release.ps1" %*
echo.
echo Exit code: %errorlevel%
echo.
pause
