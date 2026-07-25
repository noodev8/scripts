@echo off
REM Batch file to run update_orders2.py script
REM This script handles order synchronization and pick allocation

echo ========================================
echo Order Update Script Runner
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if the Python script exists
if not exist "update_orders2.py" (
    echo ERROR: update_orders2.py not found in current directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found
    echo Make sure your environment variables are properly configured
    echo.
)

REM Show menu options
echo Select an option:
echo 1. Run full order sync and pick allocation (default)
echo 2. Run pick allocation only
echo 3. Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="2" (
    echo Running pick allocation only...
    echo.
    python update_orders2.py --picks
) else if "%choice%"=="3" (
    echo Exiting...
    exit /b 0
) else (
    echo Running full order sync and pick allocation...
    echo.
    python update_orders2.py
)

echo.
echo ========================================
echo Script execution completed
echo ========================================

REM Check the exit code
if %errorlevel% equ 0 (
    echo Script completed successfully
) else (
    echo Script completed with errors (Exit code: %errorlevel%)
)

echo.
echo Press any key to close this window...
pause >nul
