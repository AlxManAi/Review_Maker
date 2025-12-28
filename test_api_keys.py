"""
Проверка API ключей
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Получить ключи
PERPLEXITY_KEY = os.getenv("PERPLEXITY_API_KEY")
MISTRAL_KEY = os.getenv("MISTRAL_API_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")

print("=== Проверка API ключей ===\n")

# 1. Perplexity
print("1. Perplexity:")
print(f"   Ключ: {PERPLEXITY_KEY[:20]}..." if PERPLEXITY_KEY else "   ❌ Ключ не найден")
if PERPLEXITY_KEY:
    try:
        import requests
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {PERPLEXITY_KEY}"},
            json={
                "model": "sonar",  # Быстрая модель с вебом
                "messages": [{"role": "user", "content": "test"}]
            },
            timeout=10
        )
        if response.status_code == 200:
            print("   ✅ Работает")
        else:
            print(f"   ⚠ Статус: {response.status_code}")
            print(f"   Ответ: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Ошибка: {str(e)}")

# 2. Mistral
print("\n2. Mistral:")
print(f"   Ключ: {MISTRAL_KEY[:20]}..." if MISTRAL_KEY else "   ❌ Ключ не найден")
if MISTRAL_KEY:
    try:
        from mistralai.client import MistralClient
        client = MistralClient(api_key=MISTRAL_KEY)
        response = client.chat(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": "test"}]
        )
        print("   ✅ Работает")
    except Exception as e:
        print(f"   ❌ Ошибка: {str(e)}")

# 3. DeepSeek
print("\n3. DeepSeek:")
print(f"   Ключ: {DEEPSEEK_KEY[:20]}..." if DEEPSEEK_KEY else "   ❌ Ключ не найден")
if DEEPSEEK_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=DEEPSEEK_KEY,
            base_url="https://api.deepseek.com"
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=10
        )
        print("   ✅ Работает")
    except Exception as e:
        print(f"   ❌ Ошибка: {str(e)}")

print("\n=== Проверка завершена ===")
