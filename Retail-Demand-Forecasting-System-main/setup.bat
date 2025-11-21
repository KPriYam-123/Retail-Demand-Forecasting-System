@echo off
REM Setup Script for Retail Forecasting System (Windows)
REM This script automates the setup process

echo ================================================
echo Retail Forecasting System - Setup Script
echo ================================================
echo.

REM Check Python
echo Checking Python version...
python --version
echo.

REM Check Node
echo Checking Node.js version...
node --version
echo.

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv
echo Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
echo Virtual environment activated
echo.

REM Install Python dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Python dependencies installed
echo.

REM Setup backend
echo Setting up backend...
mkdir backend\saved_models 2>nul
mkdir backend\data\uploads 2>nul
copy .env.example .env
echo Backend directories created
echo.

REM Setup frontend
echo Setting up frontend...
cd frontend
call npm install
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
echo Frontend dependencies installed
cd ..
echo.

REM Create additional directories
echo Creating additional directories...
mkdir ml_pipeline\models 2>nul
mkdir logs 2>nul
echo Directories created
echo.

echo ================================================
echo Setup Complete! 🎉
echo ================================================
echo.
echo Next steps:
echo 1. Train models: python ml_pipeline\train.py --data YOUR_DATA.csv --top-n 20
echo 2. Start backend: cd backend\app ^&^& python main.py
echo 3. Start frontend: cd frontend ^&^& npm run dev
echo.
echo Then open http://localhost:3000 in your browser
echo.
pause
