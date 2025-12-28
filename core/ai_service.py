"""
AI Service - Генерация отзывов с помощью AI моделей
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import requests
from mistralai.client import MistralClient
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class AIService:
    """Сервис для генерации отзывов с помощью AI."""
    
    def __init__(self):
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.mistral_key = os.getenv("MISTRAL_API_KEY")
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        
        # Загрузить промпт из конфига
        self.prompt_template = self._load_prompt()
    
    def _load_prompt(self) -> str:
        """Загрузить промпт из config/prompts.json"""
        try:
            with open("config/prompts.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("review_generation", "")
        except Exception as e:
            print(f"Ошибка загрузки промпта: {e}")
            # Промпт по умолчанию
            return """Ты - генератор отзывов для маркетплейса.

Товар: {product_name}

{examples_section}

Задача: Сгенерируй {count} уникальных отзывов.

Требования:
- Разные авторы (русские имена)
- Разные стили (краткие/подробные)
- Реалистичность
- Рейтинг: 4-5 звезд
- Длина: 50-300 символов

Формат (JSON):
[
  {"author": "Имя", "rating": 5, "text": "Текст", "date": "2025-01-15"}
]"""
    
    def generate_reviews(
        self, 
        product_task_id: int, 
        model: str = "perplexity"
    ) -> tuple[int, str]:
        """
        Генерировать отзывы для товара.
        
        Args:
            product_task_id: ID товара
            model: Модель AI (perplexity, mistral, deepseek)
        
        Returns:
            (count, message): Количество сгенерированных отзывов и сообщение
        """
        from core.database import db
        from core.models import ProductTask, Review
        
        try:
            with db.get_session() as session:
                # Получить товар
                product = session.query(ProductTask).get(product_task_id)
                if not product:
                    return 0, "Товар не найден"
                
                if not product.review_count or product.review_count <= 0:
                    return 0, "Укажите количество отзывов для товара"
                
                # Получить примеры (может быть 0)
                examples = self._get_example_reviews(product_task_id)
                
                # Построить промпт
                prompt = self._build_prompt(
                    product.product_name,
                    examples,
                    product.review_count
                )
                
                # Вызвать API
                response_text = self._call_api(prompt, model)
                
                # Парсить ответ
                reviews_data = self._parse_response(response_text)
                
                if not reviews_data:
                    return 0, "Не удалось распарсить ответ AI"
                
                # Сохранить отзывы
                saved_count = 0
                for review_data in reviews_data:
                    review = Review(
                        period_id=product.period_id,
                        product_task_id=product_task_id,
                        product_name=product.product_name,
                        product_url=product.product_url,
                        content=review_data.get("text", ""),
                        author=review_data.get("author", "Аноним"),
                        rating=review_data.get("rating", 5),
                        pros=review_data.get("pros", ""),
                        cons=review_data.get("cons", ""),
                        source=f"ai_{model}",
                        is_generated=True,
                        generated_at=datetime.utcnow(),
                        ai_model=model,
                        # Если AI вернул дату, можно попробовать использовать её (опционально)
                        # target_date=... 
                    )
                    session.add(review)
                    saved_count += 1
                
                session.commit()
                return saved_count, f"Успешно сгенерировано {saved_count} отзывов"
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"ОШИБКА ГЕНЕРАЦИИ:\n{error_details}")
            return 0, f"Ошибка генерации: {str(e)}"
    
    def _get_example_reviews(self, product_task_id: int) -> List[Dict]:
        """Получить примеры отзывов для товара (может быть 0)."""
        from core.database import db
        from core.models import Review
        
        examples = []
        try:
            with db.get_session() as session:
                reviews = session.query(Review).filter_by(
                    product_task_id=product_task_id,
                    is_generated=False
                ).limit(10).all()
                
                for review in reviews:
                    examples.append({
                        "author": review.author or "Аноним",
                        "rating": review.rating or 5,
                        "text": review.content
                    })
        except Exception as e:
            print(f"Ошибка получения примеров: {e}")
        
        return examples
    
    def _build_prompt(
        self, 
        product_name: str, 
        examples: List[Dict], 
        count: int
    ) -> str:
        """Построить промпт для AI."""
        # Секция с примерами
        if examples:
            examples_text = "Примеры реальных отзывов от покупателей:\n"
            for i, ex in enumerate(examples, 1):
                examples_text += f"{i}. {ex['author']} ({ex['rating']}★): {ex['text']}\n"
        else:
            examples_text = ""
        
        # Заполнить шаблон
        prompt = self.prompt_template.format(
            product_name=product_name,
            examples_section=examples_text,
            count=count
        )
        
        return prompt
    
    def _call_api(self, prompt: str, model: str) -> str:
        """Вызвать API выбранной модели."""
        if model == "perplexity":
            return self._call_perplexity(prompt)
        elif model == "mistral":
            return self._call_mistral(prompt)
        elif model == "deepseek":
            return self._call_deepseek(prompt)
        else:
            raise ValueError(f"Неизвестная модель: {model}")
    
    def _call_perplexity(self, prompt: str) -> str:
        """Вызов Perplexity API."""
        if not self.perplexity_key:
            raise ValueError("Perplexity API ключ не найден")
        
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {self.perplexity_key}"},
            json={
                "model": "sonar",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Perplexity API error: {response.status_code} - {response.text}")
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    def _call_mistral(self, prompt: str) -> str:
        """Вызов Mistral API."""
        if not self.mistral_key:
            raise ValueError("Mistral API ключ не найден")
        
        client = MistralClient(api_key=self.mistral_key)
        response = client.chat(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content
    
    def _call_deepseek(self, prompt: str) -> str:
        """Вызов DeepSeek API."""
        if not self.deepseek_key:
            raise ValueError("DeepSeek API ключ не найден")
        
        try:
            client = OpenAI(
                api_key=self.deepseek_key,
                base_url="https://api.deepseek.com"
            )
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            # Если DeepSeek не работает - сообщаем но не падаем
            raise Exception(f"DeepSeek недоступен: {str(e)}")
    
    def _parse_response(self, response_text: str) -> List[Dict]:
        """Парсить JSON ответ от AI."""
        try:
            print(f"Ответ AI (первые 500 символов): {response_text[:500]}")
            
            # Убрать markdown если есть
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            
            # Попробовать найти JSON массив в ответе
            start = response_text.find("[")
            end = response_text.rfind("]") + 1
            
            if start == -1 or end == 0:
                # JSON массив не найден, попробовать весь текст
                data = json.loads(response_text)
            else:
                # Извлечь JSON часть
                json_text = response_text[start:end]
                data = json.loads(json_text)
            
            if isinstance(data, list):
                print(f"Распарсено {len(data)} отзывов")
                return data
            else:
                print(f"Распарсен 1 отзыв (не массив)")
                return [data]
                
        except Exception as e:
            print(f"ОШИБКА ПАРСИНГА: {e}")
            print(f"Полный ответ AI:\n{response_text}")
            return []


# Singleton instance
ai_service = AIService()
