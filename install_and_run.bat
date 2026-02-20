@echo off
setlocal
title NetSim Industrial - Setup & Run

echo ===================================================
echo   NetSim Industrial Simulator - Installer
echo ===================================================

:: 1. Create Virtual Environment
if not exist venv (
    echo [1/3] Creating Virtual Environment...
    python -m venv venv
) else (
    echo [1/3] Virtual Environment already exists.
)

:: 2. Install dependencies
echo [2/3] Installing Dependencies...
venv\Scripts\python.exe -m pip install flask flask-socketio networkx eventlet pydantic reportlab svglib

:: 3. Run Simulator
echo [3/3] Launching Industrial Network Simulator...
echo.
echo Dashboard available at: http://localhost:5000
echo.
venv\Scripts\python.exe app.py

pause
