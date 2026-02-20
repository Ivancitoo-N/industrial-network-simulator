@echo off
setlocal
title NetSim Industrial - Startup

echo ===================================================
echo   NetSim Industrial Simulator - Startup
echo ===================================================

:: Check if virtual environment exists
if not exist venv (
    echo [ERROR] Virtual environment not found. 
    echo Please run 'install_and_run.bat' for the first-time setup.
    pause
    exit /b
)

:: Run Simulator
echo [INFO] Environment verified. Launching...
echo.
echo Dashboard available at: http://localhost:5000
echo Ctrl+C to stop.
echo.
venv\Scripts\python.exe app.py

pause
