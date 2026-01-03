#!/usr/bin/env python3
import sys
import os

# Добавляем корень проекта в Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from web.backend.main import app
    print("✅ FastAPI app imported successfully")
    
    # Проверяем роуты
    routes = [route.path for route in app.routes]
    print(f"📋 Available routes: {routes}")
    
    # Проверяем базу данных
    from core.database import db
    print("✅ Database imported successfully")
    
    # Создаём таблицы
    try:
        db.create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    print("🚀 Ready to start server!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ General error: {e}")
    import traceback
    traceback.print_exc()
