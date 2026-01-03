#!/bin/bash

# Auto-setup script for Review Generator in GitHub Codespace
echo "🚀 Review Generator Auto-Setup for Codespace"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_command() {
    echo -e "${BLUE}[CMD]${NC} $1"
}

# Check current directory
print_status "Current directory: $(pwd)"
print_status "Listing files:"
ls -la

# Update pip
print_status "Updating pip..."
print_command "pip install --upgrade pip"
pip install --upgrade pip

# Install FastAPI and dependencies
print_status "Installing FastAPI and dependencies..."
print_command "pip install fastapi uvicorn requests"
pip install fastapi uvicorn requests

# Check if web/backend exists
if [ -d "web/backend" ]; then
    print_status "Navigating to backend directory..."
    cd web/backend
else
    print_status "Backend directory not found, checking current directory..."
    ls -la
    if [ -d "backend" ]; then
        cd backend
    else
        print_status "Backend directory not found. Creating it..."
        mkdir -p web/backend
        cd web/backend
    fi
fi

# Run the API
print_status "Starting FastAPI server..."
print_command "python simple_main.py"
python simple_main.py
