# Quick Start Guide

## 🚀 GitHub Codespace Quick Start

1. **Create Codespace**
   - Go to GitHub repo → Code → Codespaces → New codespace
   - Wait 2-5 minutes for setup

2. **Run the app**
   ```bash
   # Linux/Mac
   ./start.sh

   # Windows
   .\start.ps1

   # Or manually:
   cd web
   docker-compose up
   ```

3. **Access the app**
   - Check Ports tab → Click on port 8000
   - Or use the provided public URL

## 🤖 AI Agents Commands

### Continue (SWE-1.5 alternative)
```bash
continue chat
continue "Add export button to Products"
continue "Fix double-click bug in table"
```

### Amazon Q
```bash
q chat
q "Help optimize Docker image"
q "Review code for security issues"
```

### Tabnine
- Autocomplete works automatically
- `Ctrl+Shift+P` → "Tabnine: Ask Tabnine"

### GitHub Copilot (if available)
- `Ctrl+I` for inline chat
- `Ctrl+Shift+I` for workspace chat

## 📋 Script Options

```bash
# Full setup and run
./start.sh

# Install dependencies only
./start.sh deps

# Run only
./start.sh run

# Stop
./start.sh stop

# Show logs
./start.sh logs

# Clean up
./start.sh clean

# Development mode
./start.sh dev

# AI commands help
./start.sh ai

# Check status
./start.sh status

# Help
./start.sh help
```

## 🔧 Development Mode

For development with hot reload:

```bash
# Terminal 1 - Backend
uvicorn web.backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd web/frontend && npm start
```

## 📝 Notes

- The app runs on port 8000
- Database is SQLite (stored in container)
- All AI agents are pre-installed in Codespace
- Free tier: 60 hours/month per GitHub account
