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

# Update pip
print_status "Updating pip..."
print_command "pip install --upgrade pip"
pip install --upgrade pip

# Install FastAPI and dependencies
print_status "Installing FastAPI and dependencies..."
print_command "pip install fastapi uvicorn"
pip install fastapi uvicorn

# Install additional dependencies if needed
print_status "Installing additional dependencies..."
print_command "pip install requests"
pip install requests

# Go to backend directory
print_status "Navigating to backend directory..."
cd web/backend

# Run the API
print_status "Starting FastAPI server..."
print_command "python simple_main.py"
python simple_main.py
