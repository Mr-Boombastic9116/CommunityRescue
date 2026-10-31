@echo off
title Community Food Rescue Network - Local Automated Setup
color 0F
echo ===================================================================
echo   COMMUNITY FOOD RESCUE NETWORK - COMPLETE LOCAL SETUP
echo ===================================================================
echo.

cd /d "%~dp0"

echo [Step 1/6] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH!
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)
python --version

echo.
echo [Step 2/6] Checking Node.js installation...
node --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not installed or not in your PATH!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
node --version

echo.
echo [Step 3/6] Setting up Python virtual environment...
if not exist "venv\" (
    echo Creating virtual environment in 'venv' ...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo Upgrading pip and installing backend dependencies...
python -m pip install -r backend\requirements.txt

echo.
echo [Step 4/6] Setting up environment variables...
if not exist "backend\.env" (
    copy "backend\.env.example" "backend\.env"
    echo Created backend\.env from example.
)

echo.
echo [Step 5/6] Initializing MySQL Database & Schema...
set PYTHONPATH=backend
python -m app.database.init_db
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Database initialization encountered an issue.
    echo Please verify MySQL is running in XAMPP on port 3306.
) else (
    echo Seeding realistic demonstration data...
    python scripts\seed_data.py
)

echo.
echo [Step 6/6] Installing frontend dependencies...
cd frontend
call npm install
cd ..

echo.
echo ===================================================================
echo [SUCCESS] SETUP COMPLETED SUCCESSFULLY!
echo ===================================================================
echo.
echo To run the application:
echo   1. Double-click "start_backend.bat"  (FastAPI on http://localhost:5000)
echo   2. Double-click "start_frontend.bat" (React UI on http://localhost:3000)
echo.
echo Built with Python 3.11, FastAPI, React, TypeScript, and MySQL.
echo.
pause

