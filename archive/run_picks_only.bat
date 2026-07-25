@echo off
REM Simple batch file to run pick allocation only
cd /d "%~dp0"
echo Running pick allocation only...
python update_orders2.py --picks
echo.
echo Script completed. Press any key to close...
pause >nul
