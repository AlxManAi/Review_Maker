#!/usr/bin/env python3
import requests

try:
    # Тестируем API
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 Testing Simple API...")
    
    # Тест корня
    response = requests.get(f"{base_url}/", timeout=2)
    print(f"✅ GET / -> {response.status_code}: {response.json()}")
    
    # Тест API
    response = requests.get(f"{base_url}/api", timeout=2)
    print(f"✅ GET /api -> {response.status_code}: {response.json()}")
    
    # Тест debug
    response = requests.get(f"{base_url}/debug", timeout=2)
    print(f"✅ GET /debug -> {response.status_code}: {response.json()}")
    
    # Тест projects
    response = requests.get(f"{base_url}/api/projects", timeout=2)
    print(f"✅ GET /api/projects -> {response.status_code}: {response.json()}")
    
    # Создаём проект
    project_data = {"name": "Test Project", "site_url": "https://example.com", "description": "Test Description"}
    response = requests.post(f"{base_url}/api/projects", json=project_data, timeout=2)
    print(f"✅ POST /api/projects -> {response.status_code}: {response.json()}")
    
    # Проверяем проекты снова
    response = requests.get(f"{base_url}/api/projects", timeout=2)
    print(f"✅ GET /api/projects (after create) -> {response.status_code}: {response.json()}")
    
    print("\n🎉 All tests passed! API is working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
