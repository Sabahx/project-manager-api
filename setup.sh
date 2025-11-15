#!/bin/bash

echo "========================================"
echo "Project Manager API - Quick Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10+ first"
    exit 1
fi

echo "[1/6] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo "[2/6] Activating virtual environment..."
source venv/bin/activate

echo "[3/6] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "[4/6] Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env file created. Please update it with your settings."
fi

echo "[5/6] Running database migrations..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "ERROR: Migration failed"
    exit 1
fi

echo "[6/6] Creating superuser..."
echo "Please create an admin account:"
python manage.py createsuperuser

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To start the development server, run:"
echo "   source venv/bin/activate"
echo "   python manage.py runserver"
echo ""
echo "Then visit:"
echo "- API: http://localhost:8000/api/"
echo "- Docs: http://localhost:8000/api/docs/"
echo "- Admin: http://localhost:8000/admin/"
echo ""
