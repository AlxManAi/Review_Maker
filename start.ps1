# Quick Start Script for Review Generator
# Usage: .\start.ps1 [option]

param(
    [string]$option = "all"
)

Write-Host "🚀 Review Generator Quick Start" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

function Write-Status {
    param([string]$message)
    Write-Host "[INFO] $message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$message)
    Write-Host "[WARN] $message" -ForegroundColor Yellow
}

function Write-Command {
    param([string]$message)
    Write-Host "[CMD] $message" -ForegroundColor Blue
}

# Check if we're in the right directory
if (-not (Test-Path "web")) {
    Write-Warning "Please run this script from the project root directory"
    exit 1
}

switch ($option.ToLower()) {
    "deps" {
        Write-Status "Installing dependencies..."
        Write-Command "pip install -r web/backend/requirements.txt"
        pip install -r web/backend/requirements.txt
        Write-Command "cd web/frontend && npm install"
        Set-Location web/frontend
        npm install
        Set-Location ../..
    }
    "build" {
        Write-Status "Building Docker image..."
        Write-Command "docker build -t review-generator ."
        docker build -t review-generator .
    }
    "run" {
        Write-Status "Starting application..."
        Write-Command "docker-compose up"
        docker-compose up
    }
    "stop" {
        Write-Status "Stopping application..."
        Write-Command "docker-compose down"
        docker-compose down
    }
    "logs" {
        Write-Status "Showing logs..."
        Write-Command "docker-compose logs -f"
        docker-compose logs -f
    }
    "clean" {
        Write-Status "Cleaning up..."
        Write-Command "docker-compose down -v"
        docker-compose down -v
        Write-Command "docker system prune -f"
        docker system prune -f
    }
    "dev" {
        Write-Status "Starting development mode..."
        Write-Command "Backend: uvicorn web.backend.main:app --reload --host 0.0.0.0 --port 8000"
        Write-Command "Frontend: cd web/frontend && npm start"
        Write-Host "Run these commands in separate terminals:" -ForegroundColor Cyan
        Write-Host "1) uvicorn web.backend.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
        Write-Host "2) cd web/frontend && npm start" -ForegroundColor White
    }
    "ai" {
        Write-Status "AI Agents Commands:"
        Write-Host ""
        Write-Host "Continue (SWE-1.5 alternative):" -ForegroundColor Cyan
        Write-Host "  continue chat" -ForegroundColor White
        Write-Host "  continue `"Add export button to Products`"" -ForegroundColor White
        Write-Host ""
        Write-Host "Amazon Q:" -ForegroundColor Cyan
        Write-Host "  q chat" -ForegroundColor White
        Write-Host "  q `"Help optimize Docker image`"" -ForegroundColor White
        Write-Host ""
        Write-Host "Tabnine:" -ForegroundColor Cyan
        Write-Host "  Ctrl+Shift+P → Tabnine: Ask Tabnine" -ForegroundColor White
        Write-Host ""
        Write-Host "GitHub Copilot (if available):" -ForegroundColor Cyan
        Write-Host "  Ctrl+I for inline chat" -ForegroundColor White
        Write-Host "  Ctrl+Shift+I for workspace chat" -ForegroundColor White
    }
    "status" {
        Write-Status "Checking status..."
        Write-Command "docker ps"
        docker ps
        Write-Host ""
        Write-Command "docker images"
        docker images
    }
    "all" {
        Write-Status "Full setup and start..."
        Write-Command "Installing dependencies..."
        pip install -r web/backend/requirements.txt
        Set-Location web/frontend
        npm install
        Set-Location ../..
        
        Write-Command "Building and starting..."
        docker-compose up --build
    }
    "help" {
        Write-Host "Usage: .\start.ps1 [option]" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Options:" -ForegroundColor Yellow
        Write-Host "  all     - Install deps, build and run (default)" -ForegroundColor White
        Write-Host "  deps    - Install dependencies only" -ForegroundColor White
        Write-Host "  build   - Build Docker image only" -ForegroundColor White
        Write-Host "  run     - Run application only" -ForegroundColor White
        Write-Host "  stop    - Stop application" -ForegroundColor White
        Write-Host "  logs    - Show logs" -ForegroundColor White
        Write-Host "  clean   - Clean up containers and images" -ForegroundColor White
        Write-Host "  dev     - Development mode instructions" -ForegroundColor White
        Write-Host "  ai      - Show AI agents commands" -ForegroundColor White
        Write-Host "  status  - Check status" -ForegroundColor White
        Write-Host "  help    - Show this help" -ForegroundColor White
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Yellow
        Write-Host "  .\start.ps1          # Full setup and run" -ForegroundColor White
        Write-Host "  .\start.ps1 deps     # Install dependencies" -ForegroundColor White
        Write-Host "  .\start.ps1 run      # Run only" -ForegroundColor White
        Write-Host "  .\start.ps1 ai       # Show AI commands" -ForegroundColor White
    }
    default {
        Write-Warning "Unknown option: $option"
        Write-Command ".\start.ps1 help"
        exit 1
    }
}

Write-Host ""
Write-Status "Done! 🎉"
Write-Host ""
Write-Host "Access the app at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Check ports in Codespace panel for public URL" -ForegroundColor Cyan
