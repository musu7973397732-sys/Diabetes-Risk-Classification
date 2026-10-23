@echo off
title DiaRisk AI - Healthcare Platform
cd /d "%~dp0"

echo ============================================================
echo           DiaRisk AI - Medical Prediction System
echo ============================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found in: %~dp0venv
    echo Please ensure dependencies are installed.
    pause
    exit /b 1
)

echo [INFO] Launching server on http://127.0.0.1:5000 ...
echo [INFO] Opening default browser automatically...
echo [INFO] Press Ctrl+C in this window anytime to stop the app.
echo.

:: Automatically open browser after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"

:: Run the Flask server
venv\Scripts\python.exe app.py

pause
