#!/usr/bin/env python3
import sys
import os
import requests

# Добавляем корень проекта в Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Тестируем базовые эндпоинты
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 Testing API endpoints...")
    
    # Тест корня
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ GET / -> {response.status_code}")
    except Exception as e:
        print(f"❌ GET / -> {e}")
    
    # Тест API
    try:
        response = requests.get(f"{base_url}/api", timeout=5)
        print(f"✅ GET /api -> {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ GET /api -> {e}")
    
    # Тест projects
    try:
        response = requests.get(f"{base_url}/api/projects", timeout=5)
        print(f"✅ GET /api/projects -> {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ GET /api/projects -> {e}")
        
except Exception as e:
    print(f"❌ General error: {e}")
    import traceback
    traceback.print_exc()
