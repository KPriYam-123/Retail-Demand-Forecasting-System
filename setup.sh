#!/bin/bash

# Setup Script for Retail Forecasting System
# This script automates the setup process

set -e

echo "================================================"
echo "Retail Forecasting System - Setup Script"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check Node version
echo "Checking Node.js version..."
node_version=$(node --version)
echo "Found Node.js $node_version"
echo ""

# Create virtual environment
echo "Creating Python virtual environment..."
python -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo "✓ Virtual environment activated"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Python dependencies installed"
echo ""

# Setup backend
echo "Setting up backend..."
mkdir -p backend/saved_models
mkdir -p backend/data/uploads
cp .env.example .env
echo "✓ Backend directories created"
echo ""

# Setup frontend
echo "Setting up frontend..."
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "✓ Frontend dependencies installed"
cd ..
echo ""

# Create necessary directories
echo "Creating additional directories..."
mkdir -p ml_pipeline/models
mkdir -p logs
echo "✓ Directories created"
echo ""

echo "================================================"
echo "Setup Complete! 🎉"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Train models: python ml_pipeline/train.py --data YOUR_DATA.csv --top-n 20"
echo "2. Start backend: cd backend/app && python main.py"
echo "3. Start frontend: cd frontend && npm run dev"
echo ""
echo "Then open http://localhost:3000 in your browser"
echo ""
