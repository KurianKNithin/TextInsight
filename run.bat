@echo off
title TextInsight Launcher
cd /d "%~dp0"

echo ===================================================
echo               Launching TextInsight
echo ===================================================
echo.
echo [1/3] Starting FastAPI Backend server on port 8000...
start "TextInsight Backend (Port 8000)" cmd /k "python -m uvicorn backend.main:app --reload --port 8000"

echo [2/3] Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

echo [3/3] Starting React Frontend server on port 5173...
start "TextInsight Frontend (Port 5173)" cmd /k "cd frontend && npm run dev"

echo.
echo Waiting for frontend to start...
timeout /t 3 /nobreak >nul

echo.
echo Launching TextInsight in your default web browser...
start http://localhost:5173

echo.
echo ===================================================
echo TextInsight is now running!
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:5173
echo.
echo To stop TextInsight, close the two opened CMD windows
echo or run stop.bat.
echo ===================================================
echo.
pause
