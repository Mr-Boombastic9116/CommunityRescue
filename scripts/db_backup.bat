@echo off
setlocal
echo ========================================================
echo Community Food Rescue Network - Database Backup Utility
echo ========================================================

set BACKUP_DIR=%~dp0..\backups
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ("%TIME%") do (set mytime=%%a%%b)
set mytime=%mytime: =0%

set BACKUP_FILE=%BACKUP_DIR%\community_food_rescue_%mydate%_%mytime%.sql

echo Backing up database 'community_food_rescue' to %BACKUP_FILE% ...

if exist "C:\xampp\mysql\bin\mysqldump.exe" (
    "C:\xampp\mysql\bin\mysqldump.exe" -u root --routines --triggers --databases community_food_rescue > "%BACKUP_FILE%"
) else (
    mysqldump -u root --routines --triggers --databases community_food_rescue > "%BACKUP_FILE%"
)

if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Backup completed: %BACKUP_FILE%
) else (
    echo [ERROR] Backup failed. Please ensure MySQL is running in XAMPP.
)
pause

