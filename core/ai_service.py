"""
AI Service - Optimized AI models service for review generation
"""
import os
import json
import re
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
import time
import random
import traceback
import requests
from mistralai import Mistral
from openai import OpenAI
from dotenv import load_dotenv
from core.database import db
from core.models import ProductTask, Review, Period
from core.logger import app_logger
from core.smart_prompt_service import SmartPromptService
# from core.orchestrator import orchestrator  # Временно отключено

load_dotenv()


class AIService:
    """Сервис для генерации отзывов с помощью AI."""
    
    def __init__(self):
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.mistral_key = os.getenv("MISTRAL_API_KEY")
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        
        # Инициализируем клиентов
        self.smart_prompt_service = SmartPromptService()
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
            return """Ты - опытный покупатель который пишет реалистичные отзывы о товарах.

Товар: {product_name}

{examples_section}

ЗАДАНИЕ: Напиши {count} реалистичных отзывов от лица разных покупателей.

ПРИНЦИПЫ:
- Пиши как реальный человек - с эмоциями, деталями, личным опытом
- Используй разные стили: восторженный, спокойный, разочарованный, нейтральный
- Упоминай конкретные детали использования товара
- Рейтинги: 4-5 звезд (в основном), иногда 3 звезды для баланса
- Длина: от коротких до развернутых, как у настоящих покупателей

ВАЖНО:
- Это демонстрационные примеры для тестирования системы
- Все данные вымышленные
- Создай РОВНО {count} отзывов

ФОРМАТ (JSON):
[
  {
    "author": "Имя",
    "rating": 5,
    "text": "Текст отзыва",
    "date": "2025-01-15"
  }
]"""
    
    # Временно отключено
    def generate_reviews_cascade(self, product_task_id: int) -> tuple[int, str]:
        """
        Генерировать отзывы с использованием каскадной архитектуры AI.
        
        Args:
            product_task_id: ID товара
            
        Returns:
            Tuple of (count, message)
        """
        return 0, "Каскадная генерация временно отключена"
        # try:
        #     with db.get_session() as session:
        #         product = session.query(ProductTask).get(product_task_id)
        #         if not product:
        #             return 0, "Товар не найден"
        #         
        #         if not product.review_count or product.review_count <= 0:
        #             return 0, "Укажите количество отзывов для товара"
        #         
        #         app_logger.info(f"Запуск каскадной генерации для товара: {product.product_name}")
        #         
        #         # Используем каскадную архитектуру
        #         try:
        #             reviews = orchestrator.generate_reviews(
        #                 query=product.product_name,
        #                 total_count=product.review_count,
        #                 start_date=session.query(Period).get(product.period_id).start_date,
        #                 end_date=session.query(Period).get(product.period_id).end_date,
        #                 url=product.product_url
        #             )
        #             
        #             # Сохраняем отзывы
        #             saved_count = 0
        #             for review_data in reviews:
        #                 # Проверяем обязательные поля
        #                 if not review_data.get("content"):
        #                     continue
        #                 
        #                 review = Review(
        #                     period_id=product.period_id,
        #                     product_task_id=product_task_id,
        #                     product_name=product.product_name,
        #                     product_url=product.product_url,
        #                     content=review_data.get("content", ""),
        #                     author=review_data.get("author", "Аноним"),
        #                     rating=review_data.get("rating", 5),
        #                     pros=review_data.get("pros", ""),
        #                     cons=review_data.get("cons", ""),
        #                     source="cascade_ai",
        #                     is_generated=True,
        #                     generated_at=datetime.utcnow(),
        #                     ai_model="cascade",
        #                     target_date=review_data.get("target_date", datetime.utcnow())
        #                 )
        #                 session.add(review)
        #                 saved_count += 1
        #             
        #             session.commit()
        #             app_logger.info(f"Каскадная генерация завершена: {saved_count} отзывов")
        #             return saved_count, f"Успешно сгенерировано {saved_count} отзывов через каскад"
        #             
        #         except Exception as cascade_error:
        #             app_logger.error(f"Ошибка каскадной генерации: {cascade_error}")
        #             # Fallback к обычной генерации
        #             return self.generate_reviews(product_task_id, "perplexity")
        #             
        # except Exception as e:
        #     error_details = traceback.format_exc()
        #     app_logger.error(f"Ошибка каскадной генерации: {error_details}")
        #     return 0, f"Ошибка генерации: {str(e)}"
    
    def generate_reviews(
        self, 
        product_task_id: int, 
        model: str = "perplexity"
    ) -> tuple[int, str]:
        """
        Генерировать отзывы для товара с human-like delays.
        
        Args:
            product_task_id: ID товара
            model: Модель AI (perplexity, mistral, deepseek)
        
        Returns:
            (count, message): Количество сгенерированных отзывов и сообщение
        """
        try:
            # Human-like delay before starting (2-5 seconds)
            delay = random.uniform(2, 5)
            app_logger.info(f"Human delay before AI generation: {delay:.1f} seconds")
            time.sleep(delay)
            
            with db.get_session() as session:
                # Получить товар
                product = session.query(ProductTask).get(product_task_id)
                if not product:
                    return 0, "Товар не найден"
                
                if not product.review_count or product.review_count <= 0:
                    return 0, "Укажите количество отзывов для товара"
                
                # Сохраняем данные товара до закрытия сессии
                product_data = {
                    'period_id': product.period_id,
                    'product_name': product.product_name,
                    'product_url': product.product_url,
                    'review_count': product.review_count
                }
                
                # Проверяем существующие отзывы для этого товара
                existing_reviews = session.query(Review).filter(Review.product_task_id == product_task_id).count()
                approved_reviews = session.query(Review).filter(
                    Review.product_task_id == product_task_id,
                    Review.is_approved == True
                ).count()
                needed_reviews = product.review_count
                
                if existing_reviews > 0:
                    if existing_reviews >= needed_reviews:
                        return 0, f"Уже есть {existing_reviews} отзывов, нужно {needed_reviews}. Генерация не требуется."
                    
                    # Дополняем до нужного количества
                    reviews_to_generate = needed_reviews - existing_reviews
                    print(f"Дополнение отзывов: есть {existing_reviews}, нужно еще {reviews_to_generate}")
                else:
                    # Генерируем все отзывы
                    reviews_to_generate = needed_reviews
                    print(f"Генерация новых отзывов: {reviews_to_generate}")
                
                # Human-like delay before AI call (3-8 seconds)
                delay = random.uniform(3, 8)
                app_logger.info(f"Human delay before AI call: {delay:.1f} seconds")
                time.sleep(delay)
                
                # Получаем период для распределения дат
                from core.models import Period
                period = session.query(Period).get(product_data['period_id'])
                if period and period.start_date and period.end_date:
                    # Сохраняем period_id для использования в распределении
                    self._current_period_id = product_data['period_id']
                    # Генерируем распределение дат
                    dates = self._generate_date_distribution(
                        period.start_date, 
                        period.end_date, 
                        product_data['review_count'],
                        product_data['product_name'],
                        product_task_id
                    )
                else:
                    dates = None
                
                # Получить примеры (может быть 0)
                examples = self._get_example_reviews(product_task_id)
                
                # Собираем информацию о товаре из карточки
                product_info = {
                    "description": product_data.get('description', ''),
                    "volume": product_data.get('volume', ''),
                    "weight": product_data.get('weight', ''),
                    "purpose": product_data.get('purpose', ''),
                    "material": product_data.get('material', '')
                }
                
                # Построить промпт
                prompt = self.smart_prompt_service.build_contextual_prompt(
                    product_data['product_name'],
                    examples,
                    reviews_to_generate,  # Используем количество для дополнения
                    product_info
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
                    
                    # Обрезаем до нужного количества
                    if reviews_data and len(reviews_data) > reviews_to_generate:
                        app_logger.warning(f"AI сгенерировал {len(reviews_data)} отзывов, нужно {reviews_to_generate}. Обрезаем до нужного количества.")
                        reviews_data = reviews_data[:reviews_to_generate]
                    
                    # Пост-обработка для обеспечения правильного формата
                    for review in reviews_data:
                        # Убедимся, что pros и cons - это строки, а не списки
                        if isinstance(review.get("pros"), list):
                            review["pros"] = ", ".join(review["pros"])
                        if isinstance(review.get("cons"), list):
                            review["cons"] = ", ".join(review["cons"])
                        
                        # Убедимся, что автор не пустой
                        if not review.get("author") or review["author"].strip() == "":
                            review["author"] = "Покупатель"
                        
                        # Простая очистка контента
                        if review.get("content"):
                            # Убираем цифры в скобках и другие артефакты
                            import re
                            # Последовательно убираем все варианты
                            content = review["content"]
                            content = re.sub(r"\[\d+\]", "", content)  # [1]
                            content = re.sub(r"\[\d+\]\[\d+\]", "", content)  # [1][5]
                            content = re.sub(r"\[\d+\]\[\d+\]\[\d+\]", "", content)  # [1][5][8]
                            review["content"] = re.sub(r"\s+", " ", content).strip()
                        elif review.get("text"):
                            # Если поле называется text, копируем в content
                            review["content"] = review["text"]
                            # Убираем цифры в скобках и другие артефакты
                            import re
                            content = review["content"]
                            content = re.sub(r"\[\d+\]", "", content)
                            content = re.sub(r"\[\d+\]\[\d+\]", "", content)
                            content = re.sub(r"\[\d+\]\[\d+\]\[\d+\]", "", content)
                            review["content"] = re.sub(r"\s+", " ", content).strip()
                        
                        # Очистка pros и cons от артефактов
                        if review.get("pros"):
                            if isinstance(review["pros"], str):
                                pros = review["pros"]
                                pros = re.sub(r"\[\d+\]", "", pros)
                                pros = re.sub(r"\[\d+\]\[\d+\]", "", pros)
                                pros = re.sub(r"\[\d+\]\[\d+\]\[\d+\]", "", pros)
                                review["pros"] = pros.strip()
                        if review.get("cons"):
                            if isinstance(review["cons"], str):
                                cons = review["cons"]
                                cons = re.sub(r"\[\d+\]", "", cons)
                                cons = re.sub(r"\[\d+\]\[\d+\]", "", cons)
                                cons = re.sub(r"\[\d+\]\[\d+\]\[\d+\]", "", cons)
                                review["cons"] = cons.strip()

                        # Каскад качества: validate -> repair -> revalidate
                        try:
                            cascaded = self._apply_cascade_quality(
                                product_name=product_data["product_name"],
                                review=review,
                                generator_model=str(model),
                                product_info=product_info,
                            )
                            if isinstance(cascaded, dict):
                                review.clear()
                                review.update(cascaded)
                        except Exception as cascade_error:
                            app_logger.error(f"Ошибка каскада качества: {cascade_error}")
                            app_logger.exception("Full traceback:")
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
                
                # Сохранить отзывы в той же сессии
                saved_count = 0
                app_logger.info(f"Начало сохранения {len(reviews_data)} отзывов")
                
                for idx, review_data in enumerate(reviews_data):
                    app_logger.info(f"Обработка отзыва {idx+1}: {review_data}")
                    
                    # Убедимся что все необходимые поля есть
                    author = review_data.get("author", review_data.get("name", "Аноним"))
                    if not author or str(author).strip() == "":
                        author = "Покупатель"
                    
                    app_logger.info(f"Автор определен: '{author}'")
                    
                    content = review_data.get("content", review_data.get("text", ""))
                    if not content or str(content).strip() == "":
                        app_logger.warning(f"Пропуск отзыва {idx+1} - нет контента")
                        continue  # Пропускаем отзывы без текста
                    
                    rating = review_data.get("rating", 5)
                    try:
                        rating = int(rating) if rating else 5
                        rating = max(1, min(5, rating))  # Ограничиваем диапазон 1-5
                    except (ValueError, TypeError):
                        rating = 5
                    
                    app_logger.info(f"Создание отзыва с автором: '{author}'")
                    
                    try:
                        review = Review(
                            period_id=product_data['period_id'],
                            product_task_id=product_task_id,
                            product_name=product_data['product_name'],
                            product_url=product_data['product_url'],
                            content=content,
                            author=str(author).strip(),
                            rating=rating,
                            pros=review_data.get("pros", ""),
                            cons=review_data.get("cons", ""),
                            source=f"ai_{model}",
                            is_generated=True,
                            generated_at=datetime.utcnow(),
                            ai_model=model,
                            # Распределяем отзывы по датам периода
                            target_date=datetime.combine(dates[idx], datetime.min.time()) if dates and idx < len(dates) else None 
                        )
                        session.add(review)
                        saved_count += 1
                        app_logger.info(f"Отзыв {idx+1} успешно сохранен")
                    except Exception as e:
                        app_logger.error(f"Ошибка сохранения отзыва {idx+1}: {e}")
                        app_logger.exception("Full traceback:")
                        continue  # Пропускаем проблемный отзыв и продолжаем
                
                session.commit()
                app_logger.info(f"Сохранено {saved_count} отзывов")
                
                # Показываем общее количество
                total_reviews = session.query(Review).filter(Review.product_task_id == product_task_id).count()
                return saved_count, f"Добавлено {saved_count} отзывов. Всего: {total_reviews}"
                
        except Exception as e:
            error_details = traceback.format_exc()
            print(f"ОШИБКА ГЕНЕРАЦИИ:\n{error_details}")
            return 0, f"Ошибка генерации: {str(e)}"

    def _clean_llm_json(self, text: str) -> str:
        if not text:
            return ""
        cleaned = str(text).strip()
        if "```json" in cleaned:
            start = cleaned.find("```json") + 7
            end = cleaned.find("```", start)
            if end != -1:
                cleaned = cleaned[start:end].strip()
        elif "```" in cleaned:
            start = cleaned.find("```") + 3
            end = cleaned.find("```", start)
            if end != -1:
                cleaned = cleaned[start:end].strip()
        return cleaned.strip()

    def _validate_review(
        self,
        product_name: str,
        review: Dict,
        verifier_model: str,
        product_info: Dict = None,
        fallback_model: str = "",
    ) -> Dict:
        prompt = self.smart_prompt_service.build_validation_prompt(
            product_name=product_name,
            review=review,
            product_info=product_info,
        )
        models_to_try = []
        if verifier_model:
            models_to_try.append(str(verifier_model))
        if fallback_model:
            fm = str(fallback_model)
            if fm and fm not in models_to_try:
                models_to_try.append(fm)

        last_error = None
        for m in models_to_try:
            try:
                resp = self._call_api(prompt, m)
                data = json.loads(self._clean_llm_json(resp))
                if isinstance(data, dict) and "ok" in data:
                    if not isinstance(data.get("issues"), list):
                        data["issues"] = []
                    data.setdefault("notes", "")
                    return data
            except Exception as e:
                last_error = e

        app_logger.warning(f"Валидация не удалась (fallback ok=true): {last_error}")
        return {"ok": True, "issues": [], "notes": "validator_failed"}

    def _repair_review(self, product_name: str, review: Dict, issues: List[Dict], repair_model: str, product_info: Dict = None) -> Dict:
        prompt = self.smart_prompt_service.build_repair_prompt(
            product_name=product_name,
            review=review,
            issues=issues,
            product_info=product_info,
        )
        try:
            resp = self._call_api(prompt, repair_model)
            data = json.loads(self._clean_llm_json(resp))
            if isinstance(data, dict):
                return data
        except Exception as e:
            app_logger.warning(f"Repair не удался, оставляем исходный отзыв: {e}")
        return review

    def _apply_cascade_quality(self, product_name: str, review: Dict, generator_model: str, product_info: Dict = None) -> Dict:
        settings = self.smart_prompt_service.get_cascade_settings()

        max_iterations = int(settings.get("max_iterations", 2) or 0)
        verifier_model = str(settings.get("verifier_model") or "deepseek")
        repair_model = str(settings.get("repair_model") or "")
        if not repair_model:
            repair_model = generator_model

        if max_iterations <= 0:
            return review

        current = dict(review or {})

        last_issues = []
        for iteration in range(1, max_iterations + 1):
            verdict = self._validate_review(
                product_name=product_name,
                review=current,
                verifier_model=verifier_model,
                product_info=product_info,
                fallback_model=generator_model,
            )

            ok = bool(verdict.get("ok"))
            issues = verdict.get("issues") if isinstance(verdict.get("issues"), list) else []
            last_issues = issues

            if ok:
                if iteration > 1:
                    app_logger.info(f"Каскад качества: OK после {iteration} итераций")
                return current

            current = self._repair_review(
                product_name=product_name,
                review=current,
                issues=issues,
                repair_model=repair_model,
                product_info=product_info,
            )

            # Минимальная нормализация результата repair (на случай если модель "сломала" ключи)
            if isinstance(current, dict):
                if "text" in current and "content" not in current:
                    current["content"] = current.get("text")
                if "content" in current and current.get("content") is None:
                    current["content"] = ""
                if "author" not in current or not str(current.get("author") or "").strip():
                    current["author"] = "Покупатель"
                if "pros" not in current:
                    current["pros"] = ""
                if "cons" not in current:
                    current["cons"] = ""
            else:
                current = dict(review or {})

        app_logger.warning(f"Каскад качества: не удалось добиться OK за {max_iterations} итераций. Последние issues: {last_issues}")
        return current
    
    def _get_example_reviews(self, product_task_id: int) -> List[Dict]:
        """Получить примеры отзывов для товара (может быть 0)."""
        examples = []
        try:
            with db.get_session() as session:
                # Получаем любые отзывы для примера
                reviews = session.query(Review).filter_by(
                    product_task_id=product_task_id
                ).limit(10).all()
                
                for review in reviews:
                    examples.append({
                        "author": review.author or "Аноним",
                        "rating": review.rating or 5,
                        "text": review.content
                    })
                    
        except Exception as e:
            app_logger.error(f"Ошибка получения примеров: {e}")
        
        return examples
    
    def _generate_date_distribution(self, start_date, end_date, count, product_name=None, product_task_id=None):
        """
        Генерировать распределение дат для отзывов с учетом похожих товаров.
        
        Args:
            start_date: Начальная дата периода
            end_date: Конечная дата периода  
            count: Количество отзывов
            product_name: Название товара для группировки
            product_task_id: ID товара для исключения из анализа
        """
        if not start_date or not end_date or count <= 0:
            return None
        
        total_days = (end_date - start_date).days + 1
        if total_days <= 0:
            return None
        
        # Получаем все товары для этого периода
        from core.database import db
        from core.models import ProductTask
        with db.get_session() as session:
            products = session.query(ProductTask).filter_by(period_id=getattr(self, '_current_period_id', None)).all()
            
            # Группируем похожие товары по ключевым словам
            product_groups = {}
            for product in products:
                if product.id == product_task_id:  # Пропускаем текущий товар
                    continue
                name = product.product_name.lower()
                group_key = None
                
                # Определяем группу по ключевым словам
                if 'бак' in name or 'душев' in name:
                    group_key = 'бак_душевой'
                elif 'крышка' in name:
                    group_key = 'крышка'
                elif 'ящик' in name:
                    group_key = 'ящик'
                elif 'рукомойник' in name:
                    group_key = 'рукомойник'
                elif 'торфяной' in name or 'биотуалет' in name:
                    group_key = 'биотуалет'
                elif 'v ' in name or 't ' in name:
                    group_key = 'v_t_series'
                else:
                    group_key = 'other'
                
                if group_key not in product_groups:
                    product_groups[group_key] = []
                product_groups[group_key].append(product)
            
            # Определяем группу текущего товара
            current_group = 'other'
            if product_name:
                name_lower = product_name.lower()
                if 'бак' in name_lower or 'душев' in name_lower:
                    current_group = 'бак_душевой'
                elif 'крышка' in name_lower:
                    current_group = 'крышка'
                elif 'ящик' in name_lower:
                    current_group = 'ящик'
                elif 'рукомойник' in name_lower:
                    current_group = 'рукомойник'
        
            # Инициализация слотов для дат
            day_slots = {}
            current_date = start_date
            while current_date <= end_date:
                day_slots[current_date] = 0
                current_date += timedelta(days=1)
            
            # Распределяем отзывы по датам
            dates = []
            for i in range(count):
                # Ищем лучший день для текущей группы
                best_date = None
                min_slots = float('inf')
                
                # Для товаров из той же группы стараемся разместить рядом
                if current_group in product_groups and len(product_groups[current_group]) > 1:
                    group_products = product_groups[current_group]
                    existing_reviews = session.query(Review).filter(
                        Review.product_task_id.in_([p.id for p in group_products])
                    ).all()
                    existing_dates = [r.target_date for r in existing_reviews if r.target_date]
                    
                    # Ищем даты рядом с уже существующими
                    for existing_date in existing_dates:
                        for offset in range(-2, 3):  # ±2 дня
                            check_date = existing_date + timedelta(days=offset)
                            if check_date in day_slots and day_slots[check_date] < 3:
                                if day_slots[check_date] < min_slots:
                                    min_slots = day_slots[check_date]
                                    best_date = check_date
                
                # Если не нашли подходящий день, берем с минимальным количеством
                if best_date is None:
                    recent_dates_for_group = set()
                    if dates:
                        for j in range(max(0, len(dates) - 5), len(dates)):
                            recent_dates_for_group.add(dates[j])
                    
                    # Ищем лучший день
                    for date in day_slots:
                        if day_slots[date] < 3 and date not in recent_dates_for_group:
                            if day_slots[date] < min_slots:
                                min_slots = day_slots[date]
                                best_date = date
                
                # Если не нашли подходящий день, берем с минимальным количеством
                if best_date is None:
                    for date in day_slots:
                        if day_slots[date] < 3:
                            if day_slots[date] < min_slots:
                                min_slots = day_slots[date]
                                best_date = date
                
                if best_date:
                    dates.append(best_date)
                    day_slots[best_date] += 1
            
            # Если осталось место, равномерно распределяем
            if len(dates) < count:
                remaining = count - len(dates)
                available_dates = [date for date, slots in day_slots.items() if slots < 3]
                
                for j in range(min(remaining, len(available_dates))):
                    dates.append(available_dates[j % len(available_dates)])
            
            # Сортируем и ограничиваем
            dates.sort()
            return dates[:count]
    
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
                "messages": [
                    {"role": "system", "content": "You are an NLP researcher creating educational examples for sentiment analysis. These are NOT real reviews, but training samples for machine learning models."},
                    {"role": "user", "content": prompt}
                ]
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
            model="mistral-large-latest",
            messages=[
                {"role": "system", "content": "You are an NLP researcher creating educational examples for sentiment analysis. These are NOT real reviews, but training samples for machine learning models."},
                {"role": "user", "content": prompt}
            ]
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
                messages=[
                    {"role": "system", "content": "You are an NLP researcher creating educational examples for sentiment analysis. These are NOT real reviews, but training samples for machine learning models."},
                    {"role": "user", "content": prompt}
                ]
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
