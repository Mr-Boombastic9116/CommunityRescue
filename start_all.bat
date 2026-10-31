@echo off
title Community Food Rescue Network - Master Launcher
color 0E
echo ===================================================================
echo   COMMUNITY FOOD RESCUE NETWORK - LAUNCHING ALL SERVICES
echo ===================================================================
echo.

cd /d "%~dp0"

REM 1. Check MySQL
echo [1/3] Checking MySQL database service...
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

REM 2. Start Backend in separate window
echo [2/3] Launching FastAPI Backend Server (http://127.0.0.1:5000) ...
start "Community Food Rescue - Backend Server" cmd.exe /k "start_backend.bat"

REM 3. Start Frontend in separate window
echo [3/3] Launching React Vite Frontend Server (http://localhost:3000) ...
start "Community Food Rescue - Frontend Web App" cmd.exe /k "start_frontend.bat"

echo.
echo ===================================================================
echo   ALL SERVICES LAUNCHED SUCCESSFULLY!
echo ===================================================================
echo.
echo Backend API URL:      http://127.0.0.1:5000
echo API Documentation:    http://127.0.0.1:5000/api/docs
echo Frontend Web App:     http://localhost:3000
echo.
echo Waiting 3 seconds before opening browser...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo This launcher window will now close. Use the server windows to monitor logs.
timeout /t 2 /nobreak >nul
exit /b 0

