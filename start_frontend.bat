@echo off
title Community Food Rescue Network - Frontend Web App
color 0B
echo ===================================================================
echo   COMMUNITY FOOD RESCUE NETWORK - REACT VITE FRONTEND
echo ===================================================================
echo.

cd /d "%~dp0"

REM 1. Verify Node.js
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not found in your PATH!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM 2. Check node_modules in frontend
if not exist "frontend\node_modules\" (
    echo [INFO] Installing frontend dependencies first...
    cd frontend
    call npm.cmd install
    cd ..
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install npm packages.
        pause
        exit /b 1
    )
)

REM 3. Check port 3000 status
echo [1/2] Checking port 3000 availability...
set FR_STATUS=FREE
set FR_PORT=3000
set FR_PID=0

for /f "tokens=1,2,3" %%A in ('venv\Scripts\python.exe scripts\check_service.py frontend 3000') do (
    set FR_STATUS=%%A
    set FR_PORT=%%B
    set FR_PID=%%C
)

if "%FR_STATUS%"=="HEALTHY" goto :frontend_already_running
if "%FR_STATUS%"=="CONFLICT" goto :frontend_conflict
goto :start_frontend_server

:frontend_already_running
echo.
echo ===================================================================
echo [INFO] Frontend dev server is ALREADY running and responsive!
echo [INFO] URL: http://localhost:3000  (PID: %FR_PID%)
echo ===================================================================
echo.
echo Options:
echo   [1] Keep current frontend and open browser (Default)
echo   [2] Stop existing frontend (PID %FR_PID%) and restart fresh
echo   [3] Start on fallback port 3001
echo.
set USER_FR_CHOICE=1
set /p USER_FR_CHOICE="Enter choice [1, 2, or 3, default=1]: "
if "%USER_FR_CHOICE%"=="2" (
    echo Terminating existing frontend PID %FR_PID%...
    taskkill /F /T /PID %FR_PID% >nul 2>&1
    timeout /t 1 /nobreak >nul
    goto :start_frontend_server
)
if "%USER_FR_CHOICE%"=="3" (
    set VITE_PORT=3001
    set FR_PORT=3001
    goto :start_frontend_server
)
echo Opening http://localhost:3000 in your browser...
start http://localhost:3000
exit /b 0

:frontend_conflict
echo.
echo [WARNING] Port 3000 is occupied by process PID %FR_PID%, but it is not responding to web requests.
echo Options:
echo   [1] Run frontend on fallback port 3001 (Recommended)
echo   [2] Terminate PID %FR_PID% to clear port 3000
echo   [3] Cancel
echo.
set EXT_CHOICE=1
set /p EXT_CHOICE="Enter choice [1, 2, or 3, default=1]: "
if "%EXT_CHOICE%"=="2" (
    echo Terminating PID %FR_PID% ...
    taskkill /F /T /PID %FR_PID% >nul 2>&1
    timeout /t 1 /nobreak >nul
    goto :start_frontend_server
)
if "%EXT_CHOICE%"=="3" (
    echo Startup cancelled by user.
    pause
    exit /b 0
)
set VITE_PORT=3001
set FR_PORT=3001
goto :start_frontend_server

:start_frontend_server
echo [OK] Using frontend port: %FR_PORT%

REM 4. Launch Vite dev server
echo.
echo [2/2] Starting frontend development server on http://localhost:%FR_PORT% ...
echo API proxy target: http://127.0.0.1:5000
echo.

cd frontend
call npm.cmd run dev

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Frontend dev server stopped unexpectedly with code %ERRORLEVEL%.
    pause
)
