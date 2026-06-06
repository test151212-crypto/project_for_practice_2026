@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo   Freelance Marketplace — Project Setup
echo ===================================================
echo.

REM ------------------- Check Python -------------------
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.11+ and add to PATH.
    pause
    exit /b 1
)

REM ------------------- Virtual Environment -------------------
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists.
)

call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

REM ------------------- Install Dependencies -------------------
echo Updating pip and installing setuptools...
pip install --upgrade pip
pip install setuptools

if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found.
    pause
    exit /b 1
)

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements.
    echo Try manually: pip install -r requirements.txt
    pause
    exit /b 1
)

echo Installing setuptools and djangorestframework-simplejwt (for safety)...
pip install --upgrade setuptools djangorestframework-simplejwt

REM ------------------- Playwright Browsers -------------------
echo Installing Playwright browsers...
python -m playwright install chromium
if %errorlevel% neq 0 (
    echo [WARNING] Failed to install Playwright browsers.
)

REM ------------------- Create logs directory -------------------
if not exist "logs" mkdir logs

REM ------------------- PostgreSQL Setup (manual only) -------------------
echo.
echo ===== PostgreSQL Setup =====
echo Please ensure the following BEFORE running migrations:
echo   - PostgreSQL is installed and running
echo   - Database "freelance" exists
echo   - User "freelance_user" with password "freelance_pass" exists
echo   - User has all privileges on database "freelance"
echo.
echo If not, create them using pgAdmin or psql with these SQL commands:
echo   CREATE DATABASE freelance;
echo   CREATE USER freelance_user WITH PASSWORD 'freelance_pass';
echo   GRANT ALL PRIVILEGES ON DATABASE freelance TO freelance_user;
echo.
echo After that, press any key to continue.
pause >nul

REM ------------------- Grant schema privileges (fix for public schema) -------------------
echo Granting schema privileges to freelance_user...
set "PGPASSWORD=freelance_pass"
psql -U freelance_user -h localhost -d freelance -c "GRANT ALL ON SCHEMA public TO freelance_user;" 2>nul
psql -U freelance_user -h localhost -d freelance -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO freelance_user;" 2>nul
set "PGPASSWORD="

REM ------------------- Migrations (critical order: users first) -------------------
echo Creating migrations for users app...
python manage.py makemigrations users
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create migrations for users.
    pause
    exit /b 1
)

echo Applying users migrations...
python manage.py migrate users
if %errorlevel% neq 0 (
    echo [ERROR] Failed to apply users migrations.
    echo Check database connection and privileges.
    pause
    exit /b 1
)

echo Creating migrations for all apps...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create migrations.
    pause
    exit /b 1
)

echo Applying all migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo [ERROR] Failed to apply migrations.
    echo Check database connection in .env and ensure PostgreSQL is running.
    pause
    exit /b 1
)

REM ------------------- Static Files -------------------
echo Collecting static files (optional)...
python manage.py collectstatic --noinput
if %errorlevel% neq 0 (
    echo [WARNING] Static files collection failed. This is not critical for development.
)
pause
REM ------------------- Superuser -------------------
echo.
echo Creating superuser (admin):
python manage.py createsuperuser

echo.
echo ===================================================
echo   Setup completed successfully!
echo   Run start.bat to launch the project.
echo ===================================================
pause