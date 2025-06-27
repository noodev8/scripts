@echo off
REM Simple batch file to run full order sync and pick allocation
cd /d "%~dp0"
echo Running full order sync and pick allocation...
python update_orders2.py
echo.
echo Script completed. Press any key to close...
pause >nul
