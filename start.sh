#!/bin/bash

# Quick Start Script for Review Generator in GitHub Codespace
# Usage: ./start.sh [option]

set -e

echo "🚀 Review Generator Quick Start"
echo "================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_command() {
    echo -e "${BLUE}[CMD]${NC} $1"
}

# Check if we're in the right directory
if [ ! -d "web" ]; then
    print_warning "Please run this script from the project root directory"
    exit 1
fi

# Parse command line argument
case "${1:-all}" in
    "deps")
        print_status "Installing dependencies..."
        print_command "pip install -r web/backend/requirements.txt"
        pip install -r web/backend/requirements.txt
        print_command "cd web/frontend && npm install"
        cd web/frontend && npm install && cd ../..
        ;;
    "build")
        print_status "Building Docker image..."
        print_command "docker build -t review-generator ."
        docker build -t review-generator .
        ;;
    "run")
        print_status "Starting application..."
        print_command "docker-compose up"
        docker-compose up
        ;;
    "stop")
        print_status "Stopping application..."
        print_command "docker-compose down"
        docker-compose down
        ;;
    "logs")
        print_status "Showing logs..."
        print_command "docker-compose logs -f"
        docker-compose logs -f
        ;;
    "clean")
        print_status "Cleaning up..."
        print_command "docker-compose down -v"
        docker-compose down -v
        print_command "docker system prune -f"
        docker system prune -f
        ;;
    "dev")
        print_status "Starting development mode..."
        print_command "Backend: uvicorn web.backend.main:app --reload --host 0.0.0.0 --port 8000"
        print_command "Frontend: cd web/frontend && npm start"
        echo "Run these commands in separate terminals:"
        echo "1) uvicorn web.backend.main:app --reload --host 0.0.0.0 --port 8000"
        echo "2) cd web/frontend && npm start"
        ;;
    "ai")
        print_status "AI Agents Commands:"
        echo ""
        echo "Continue (SWE-1.5 alternative):"
        echo "  continue chat"
        echo "  continue \"Add export button to Products\""
        echo ""
        echo "Amazon Q:"
        echo "  q chat"
        echo "  q \"Help optimize Docker image\""
        echo ""
        echo "Tabnine:"
        echo "  Ctrl+Shift+P → Tabnine: Ask Tabnine"
        echo ""
        echo "GitHub Copilot (if available):"
        echo "  Ctrl+I for inline chat"
        echo "  Ctrl+Shift+I for workspace chat"
        ;;
    "status")
        print_status "Checking status..."
        print_command "docker ps"
        docker ps
        echo ""
        print_command "docker images"
        docker images
        ;;
    "all")
        print_status "Full setup and start..."
        print_command "Installing dependencies..."
        pip install -r web/backend/requirements.txt
        cd web/frontend && npm install && cd ../..
        
        print_command "Building and starting..."
        docker-compose up --build
        ;;
    "help"|"-h"|"--help")
        echo "Usage: ./start.sh [option]"
        echo ""
        echo "Options:"
        echo "  all     - Install deps, build and run (default)"
        echo "  deps    - Install dependencies only"
        echo "  build   - Build Docker image only"
        echo "  run     - Run application only"
        echo "  stop    - Stop application"
        echo "  logs    - Show logs"
        echo "  clean   - Clean up containers and images"
        echo "  dev     - Development mode instructions"
        echo "  ai      - Show AI agents commands"
        echo "  status  - Check status"
        echo "  help    - Show this help"
        echo ""
        echo "Examples:"
        echo "  ./start.sh          # Full setup and run"
        echo "  ./start.sh deps     # Install dependencies"
        echo "  ./start.sh run      # Run only"
        echo "  ./start.sh ai       # Show AI commands"
        ;;
    *)
        print_warning "Unknown option: $1"
        print_command "./start.sh help"
        exit 1
        ;;
esac

echo ""
print_status "Done! 🎉"
echo ""
echo "Access the app at: http://localhost:8000"
echo "Check ports in Codespace panel for public URL"
