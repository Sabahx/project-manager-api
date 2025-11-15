@echo off
echo ========================================
echo Project Manager API - Quick Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

echo [1/6] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/6] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/6] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo .env file created. Please update it with your settings.
)

echo [5/6] Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Migration failed
    pause
    exit /b 1
)

echo [6/6] Creating superuser...
echo Please create an admin account:
python manage.py createsuperuser

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the development server, run:
echo    venv\Scripts\activate
echo    python manage.py runserver
echo.
echo Then visit:
echo - API: http://localhost:8000/api/
echo - Docs: http://localhost:8000/api/docs/
echo - Admin: http://localhost:8000/admin/
echo.
pause
