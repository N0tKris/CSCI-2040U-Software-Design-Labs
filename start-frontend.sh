#!/bin/bash

# Quick Start Script for Catalog Management System
echo "=========================================="
echo "Catalog Management System - Quick Start"
echo "=========================================="
echo ""

# Check if backend is running
echo "Checking if backend is running..."
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "✓ Backend is already running on http://localhost:8080"
else
    echo "⚠ Backend is not running!"
    echo ""
    echo "Please start the backend in a separate terminal:"
    echo "  cd backend"
    echo "  ./mvnw spring-boot:run"
    echo ""
    read -p "Press Enter once the backend is running..."
fi

# Navigate to frontend directory
cd frontend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing/updating dependencies..."
pip install -q -r requirements.txt

# Run the CLI
echo ""
echo "=========================================="
echo "Starting Catalog Management System CLI..."
echo "=========================================="
echo ""
python app.py
