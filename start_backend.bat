@echo off
title Community Food Rescue Network - Backend Server
color 0A
echo ===================================================================
echo   COMMUNITY FOOD RESCUE NETWORK - FASTAPI BACKEND SERVER
echo ===================================================================
echo.

cd /d "%~dp0"

REM 1. Check Python virtual environment
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment 'venv' was not found!
    echo Please run 'setup.bat' first to install all dependencies.
    echo.
    pause
    exit /b 1
)

REM 2. Check if MySQL is accessible
echo [1/3] Checking MySQL connection...
set MYSQL_ACTIVE=0
if exist "C:\xampp\mysql\bin\mysql.exe" (
    "C:\xampp\mysql\bin\mysql.exe" -u root -e "SELECT 1;" >nul 2>&1
    if %ERRORLEVEL% equ 0 set MYSQL_ACTIVE=1
)
if %MYSQL_ACTIVE% equ 0 (
    mysql -u root -e "SELECT 1;" >nul 2>&1
    if %ERRORLEVEL% equ 0 set MYSQL_ACTIVE=1
)

if %MYSQL_ACTIVE% equ 1 (
    echo [OK] MySQL server is active on port 3306.
) else (
    echo [WARNING] MySQL does not seem to be running on port 3306!
    echo Please ensure MySQL is started in XAMPP Control Panel.
    echo.
)

REM 3. Check port 5000 status
echo [2/3] Checking port 5000 availability...
set BK_STATUS=FREE
set BK_PORT=5000
set BK_PID=0

for /f "tokens=1,2,3" %%A in ('venv\Scripts\python.exe scripts\check_service.py backend') do (
    set BK_STATUS=%%A
    set BK_PORT=%%B
    set BK_PID=%%C
)

if "%BK_STATUS%"=="HEALTHY" goto :already_running
if "%BK_STATUS%"=="CONFLICT" goto :port_conflict
goto :start_server

:already_running
echo.
echo ===================================================================
echo [INFO] FastAPI backend is ALREADY running and healthy!
echo [INFO] URL: http://127.0.0.1:5000  (PID: %BK_PID%)
echo [INFO] API Documentation: http://127.0.0.1:5000/api/docs
echo ===================================================================
echo.
echo Options:
echo   [1] Keep existing backend running (Default)
echo   [2] Stop existing backend (PID %BK_PID%) and restart fresh
echo.
set USER_ACTION=1
set /p USER_ACTION="Enter choice [1 or 2, default=1]: "
if "%USER_ACTION%"=="2" (
    echo Terminating existing backend process tree PID %BK_PID%...
    taskkill /F /T /PID %BK_PID% >nul 2>&1
    timeout /t 1 /nobreak >nul
    goto :start_server
)
echo Active backend preserved. You can access http://127.0.0.1:5000/api/docs
exit /b 0

:port_conflict
echo.
echo [WARNING] Port 5000 is occupied by process PID %BK_PID%, but it is not responding to health checks.
echo Do you want to terminate PID %BK_PID% to clear port 5000?
set KILL_CHOICE=Y
set /p KILL_CHOICE="Terminate process PID %BK_PID%? (Y/N, default=Y): "
if /i "%KILL_CHOICE%"=="N" (
    echo [ERROR] Port 5000 is occupied. Cannot start backend.
    echo Please free port 5000 or change PORT in backend\.env.
    pause
    exit /b 1
)
echo Terminating process tree for PID %BK_PID%...
taskkill /F /T /PID %BK_PID% >nul 2>&1
timeout /t 1 /nobreak >nul
goto :start_server

:start_server
echo [OK] Port 5000 is ready.

REM 4. Launch FastAPI Server
echo [3/3] Launching FastAPI backend on http://127.0.0.1:5000 ...
echo Documentation available at: http://127.0.0.1:5000/api/docs
echo.

set PYTHONPATH=backend
call venv\Scripts\activate.bat
python -m uvicorn app.main:app --host 127.0.0.1 --port 5000 --reload --reload-dir backend\app

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Backend server stopped unexpectedly with code %ERRORLEVEL%.
    pause
)
