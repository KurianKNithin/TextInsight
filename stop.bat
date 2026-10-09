@echo off
title Stop TextInsight
cd /d "%~dp0"

echo ===================================================
echo               Stopping TextInsight
echo ===================================================
echo.
echo Stopping backend server (port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo Stopping frontend server (port 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo ===================================================
echo TextInsight servers have been stopped.
echo ===================================================
echo.
pause
