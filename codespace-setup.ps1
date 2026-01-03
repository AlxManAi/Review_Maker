# Auto-setup for Review Generator in GitHub Codespace

echo "🚀 Setting up Review Generator..."

# Update pip
pip install --upgrade pip

# Install dependencies
pip install fastapi uvicorn requests

# Navigate to backend and run
cd web/backend
python simple_main.py
