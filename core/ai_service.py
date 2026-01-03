"""
AI Service - Optimized AI models service for review generation
"""
import os
import json
import re
import traceback
from datetime import datetime
from typing import List, Dict, Optional
import requests
from mistralai import Mistral
from openai import OpenAI
from dotenv import load_dotenv
from core.database import db
from core.models import ProductTask, Review
from core.logger import app_logger

load_dotenv()


class AIService:
    """Сервис для генерации отзывов с помощью AI."""
    
    def __init__(self):
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.mistral_key = os.getenv("MISTRAL_API_KEY")
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        
        # Инициализируем клиентов
        self.mistral_client = Mistral(api_key=self.mistral_key) if self.mistral_key else None
        
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
        try:
            with db.get_session() as session:
                # Получить товар
                product = session.query(ProductTask).get(product_task_id)
                if not product:
                    return 0, "Товар не найден"
                
                if not product.review_count or product.review_count <= 0:
                    return 0, "Укажите количество отзывов для товара"
                
                # Проверяем и очищаем существующие отзывы для этого товара
                from sqlalchemy import delete
                existing_reviews = session.query(Review).filter(Review.product_task_id == product_task_id).count()
                if existing_reviews > 0:
                    # Удаляем существующие отзывы перед генерацией
                    delete_stmt = delete(Review).where(Review.product_task_id == product_task_id)
                    session.execute(delete_stmt)
                    session.commit()
                    print(f"Очищено {existing_reviews} существующих отзывов для товара {product.product_name}")
                
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
                
                app_logger.info(f"=== DEBUG: Получен ответ от AI ===")
                app_logger.info(f"Модель: {model}")
                app_logger.info(f"Длина ответа: {len(response_text) if response_text else 0}")
                app_logger.info(f"Первые 500 символов ответа: {response_text[:500] if response_text else 'EMPTY'}")
                app_logger.info(f"=== END DEBUG ===")
                
                # Парсить ответ с безопасной обработкой
                try:
                    reviews_data = self._parse_response(response_text)
                    app_logger.info(f"Парсинг успешен, получено {len(reviews_data) if reviews_data else 0} отзывов")
                except Exception as parse_error:
                    app_logger.error(f"!!! КРАШ ПАРСИНГА !!!")
                    app_logger.error(f"Ошибка: {parse_error}")
                    app_logger.error(f"Тип ошибки: {type(parse_error)}")
                    app_logger.exception("Full traceback:")
                    app_logger.error(f"Ответ AI: {response_text}")
                    return 0, f"Критическая ошибка парсинга: {str(parse_error)}"
                
                if not reviews_data:
                    app_logger.warning(f"Не удалось распарсить ответ AI")
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
            error_details = traceback.format_exc()
            print(f"ОШИБКА ГЕНЕРАЦИИ:\n{error_details}")
            return 0, f"Ошибка генерации: {str(e)}"
    
    def _get_example_reviews(self, product_task_id: int) -> List[Dict]:
        """Получить примеры отзывов для товара (может быть 0)."""
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
        if not self.mistral_client:
            raise ValueError("Mistral API ключ не найден")
        
        response = self.mistral_client.chat.complete(
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
        """Парсить JSON ответ от AI с улучшенной обработкой ошибок."""
        app_logger.info(f"=== НАЧАЛО ПАРСИНГА ===")
        app_logger.info(f"Длина входного текста: {len(response_text)}")
        
        try:
            app_logger.info(f"Ответ AI (первые 500 символов): {response_text[:500]}")
            
            # Убрать markdown если есть
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
                app_logger.info("Удален markdown ```json")
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
                app_logger.info("Удален markdown ```")
            
            # Очистка текста
            response_text = response_text.strip()
            app_logger.info(f"Текст после очистки: {response_text[:200]}...")
            
            # Метод 1: Попробовать найти JSON массив
            app_logger.info("Пробуем метод 1: JSON массив")
            data = self._try_parse_json_array(response_text)
            if data:
                app_logger.info(f"Распарсено {len(data)} отзывов (метод 1)")
                return data
            
            # Метод 2: Попробовать найти JSON объект
            app_logger.info("Пробуем метод 2: JSON объект")
            data = self._try_parse_json_object(response_text)
            if data:
                app_logger.info(f"Распарсено {len(data)} отзывов (метод 2)")
                return data
            
            # Метод 3: Попробовать извлечь отзывы из текста
            app_logger.info("Пробуем метод 3: извлечение из текста")
            data = self._try_extract_reviews_from_text(response_text)
            if data:
                app_logger.info(f"Извлечено {len(data)} отзывов (метод 3)")
                return data
            
            # Метод 4: Создать отзыв из текста
            app_logger.info("Пробуем метод 4: создание из текста")
            data = self._try_create_review_from_text(response_text)
            if data:
                app_logger.info(f"Создан 1 отзыв (метод 4)")
                return data
            
            app_logger.warning("Не удалось распарсить ответ ни одним из методов")
            return []
                
        except Exception as e:
            app_logger.error(f"ОШИБКА ПАРСИНГА: {e}")
            app_logger.error(f"Тип ошибки: {type(e)}")
            app_logger.exception("Full traceback:")
            app_logger.error(f"Полный ответ AI:\n{response_text}")
            return []
    
    def _try_parse_json_array(self, text: str) -> List[Dict]:
        """Попытка распарсить JSON массив."""
        try:
            start = text.find("[")
            end = text.rfind("]") + 1
            
            if start == -1 or end == 0:
                return None
            
            json_text = text[start:end]
            data = json.loads(json_text)
            
            if isinstance(data, list):
                # Валидация структуры
                valid_reviews = []
                for item in data:
                    if self._validate_review_structure(item):
                        valid_reviews.append(item)
                return valid_reviews
            
            return None
        except:
            return None
    
    def _try_parse_json_object(self, text: str) -> List[Dict]:
        """Попытка распарсить JSON объект и найти в нем массив."""
        try:
            data = json.loads(text)
            
            # Ищем массив в объекте
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list):
                        valid_reviews = []
                        for item in value:
                            if self._validate_review_structure(item):
                                valid_reviews.append(item)
                        return valid_reviews
            
            return None
        except:
            return None
    
    def _try_extract_reviews_from_text(self, text: str) -> List[Dict]:
        """Извлечь отзывы из текста по паттернам."""
        reviews = []
        
        # Паттерны для извлечения
        patterns = [
            r'(\d+\.\s*["\']?([^"\']+)["\']?\s*[:\-]\s*["\']?([^"\']+)["\']?\s*[:\-]\s*["\']?([^"\']+)["\']?)',
            r'Автор:\s*([^\n]+)\nРейтинг:\s*(\d+)\nОтзыв:\s*([^\n]+)',
            r'["\']?([^"\']+)["\']?\s*\(\s*(\d+)\s*звезд?\s*\)\s*[:\-]\s*["\']?([^"\']+)["\']?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                if len(match) >= 3:
                    review = {
                        "author": match[0].strip() if match[0] else "Покупатель",
                        "rating": self._extract_rating(match[1]),
                        "content": match[2].strip() if match[2] else "",
                        "text": match[2].strip() if match[2] else "",
                        "pros": "",
                        "cons": ""
                    }
                    if self._validate_review_structure(review):
                        reviews.append(review)
            
            if reviews:
                return reviews
        
        return None
    
    def _try_create_review_from_text(self, text: str) -> List[Dict]:
        """Создать отзыв из всего текста."""
        # Извлекаем рейтинг
        rating = self._extract_rating(text)
        if not rating:
            rating = 5  # По умолчанию
        
        # Ищем автора
        author_match = re.search(r'(?:автор|пользователь|имя)[:\s]*([^\n,\.]+)', text, re.IGNORECASE)
        author = author_match.group(1).strip() if author_match else "Покупатель"
        
        # Используем весь текст как отзыв
        content = text[:500]  # Ограничиваем длину
        
        review = {
            "author": author,
            "rating": rating,
            "content": content,
            "text": content,
            "pros": "",
            "cons": ""
        }
        
        return [review] if self._validate_review_structure(review) else None
    
    def _validate_review_structure(self, review: Dict) -> bool:
        """Валидировать структуру отзыва."""
        if not isinstance(review, dict):
            return False
        
        # Проверяем обязательные поля
        content = review.get("text", "") or review.get("content", "")
        if not content or len(content.strip()) < 10:
            return False
        
        rating = review.get("rating")
        if rating is not None:
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    return False
            except:
                return False
        
        return True
    
    def _extract_rating(self, text: str) -> int:
        """Извлечь рейтинг из текста."""
        # Ищем цифры от 1 до 5
        rating_patterns = [
            r'(\d)[\s*звезд?]',
            r'оценка[:\s]*(\d)',
            r'рейтинг[:\s]*(\d)',
            r'(\d)[\s*/\s*5]',
            r'(\d+)(?=\s|$|\n)'
        ]
        
        for pattern in rating_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    rating = int(match.group(1))
                    if 1 <= rating <= 5:
                        return rating
                except:
                    continue
        
        return 5  # По умолчанию


# Singleton instance
ai_service = AIService()
