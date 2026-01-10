"""
Smart Prompt Service - Умный сервис контекстуальных промптов
"""
import json
import re
import os
from typing import Dict, List, Optional
from core.logger import app_logger


class SmartPromptService:
    """Сервис для работы с умными промптами и агентскими инструкциями."""
    
    def __init__(self):
        self.smart_prompts = self._load_smart_prompts()
        self.knowledge_base = self._load_knowledge_base()
        self.current_project_context = None
    
    def _load_knowledge_base(self) -> Dict:
        """Загрузить базу знаний проекта."""
        try:
            with open("config/knowledge_base.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            app_logger.error(f"Ошибка загрузки базы знаний: {e}")
            return {}
    
    def get_product_knowledge(self, product_name: str) -> Dict:
        """Получить знания о конкретном товаре из базы."""
        name_lower = product_name.lower()
        kb = self.knowledge_base
        
        # Ищем категорию товара
        for category, info in kb.get("product_categories", {}).items():
            if "бак" in name_lower and "душев" in name_lower and category == "баки_душевые":
                return info
            elif "крышка" in name_lower and category == "крышки":
                return info
            elif "ящик" in name_lower and category == "ящики":
                return info
            elif "рукомойник" in name_lower and category == "рукомойники":
                return info
            elif "биотуалет" in name_lower or "торфяной" in name_lower and category == "биотуалеты":
                return info
            elif ("емкость" in name_lower or "бак" in name_lower) and ("v " in name_lower or "t " in name_lower) and category == "емкости_VT":
                return info
        
        return {}
    
    def _load_smart_prompts(self) -> Dict:
        """Загрузить умные промпты из файла."""
        try:
            with open("config/smart_prompts.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            app_logger.error(f"Ошибка загрузки умных промптов: {e}")
            return self._get_fallback_prompts()
    
    def _get_fallback_prompts(self) -> Dict:
        """Запасные промпты если файл не найден."""
        return {
            "system_instructions": {
                "role_definition": "Ты - эксперт по сантехнике и емкостным изделиям.",
                "expertise_areas": ["пластиковые баки", "крышки", "ящики"],
                "product_context": {
                    "materials": ["пластик", "полипропилен"],
                    "characteristics": ["объем", "габариты", "температурный диапазон"]
                }
            },
            "review_generation": {
                "base_prompt": "Ты - AI эксперт по анализу товаров и созданию реалистичных отзывов. Твоя задача - проанализировать товар и создать правдоподобные отзывы.\n\nПРИНЦИПЫ РАБОТЫ:\n1. Проанализируй название товара и определи его тип, назначение, характеристики\n2. Используй ТОЛЬКО информацию из названия товара, карточки товара и логические выводы\n3. НЕ придумывай характеристики которых нет\n4. Создавай реалистичные сценарии использования\n\nТОВАР: {product_name}\n\n{examples_section}\n\nЗАДАНИЕ: Создай {count} уникальных отзывов в формате JSON.\n\nВАЖНО: Каждый отзыв должен быть логичным и соответствовать реальным характеристикам товара!"
            }
        }
    
    def analyze_product_name(self, product_name: str) -> Dict:
        """Анализировать название товара и определить его характеристики."""
        name_lower = product_name.lower()
        
        # Определяем тип изделия
        product_type = "other"
        if "бак" in name_lower or "душев" in name_lower:
            product_type = "бак_душевой"
        elif "крышка" in name_lower:
            product_type = "крышка"
        elif "ящик" in name_lower:
            product_type = "ящик"
        elif "рукомойник" in name_lower:
            product_type = "рукомойник"
        elif "торфяной" in name_lower or "биотуалет" in name_lower:
            product_type = "биотуалет"
        elif "v " in name_lower or "t " in name_lower:
            product_type = "v_t_series"
        
        # Определяем материал
        material = "пластик"  # по умолчанию
        if "нержаве" in name_lower or "нерж" in name_lower:
            material = "нержавейка"
        
        # Определяем характеристики
        characteristics = []
        if "объем" in name_lower or "л" in name_lower:
            characteristics.append("объем")
        if "температур" in name_lower:
            characteristics.append("температурный диапазон")
        if "прочн" in name_lower:
            characteristics.append("прочность")
        
        return {
            "type": product_type,
            "material": material,
            "characteristics": characteristics,
            "name": product_name
        }
    
    def build_contextual_prompt(self, product_name: str, examples: List[Dict], count: int, product_info: Dict = None) -> str:
        """Построить контекстуальный промпт на основе анализа товара."""
        # Анализируем товар
        product_analysis = self.analyze_product_name(product_name)
        
        # Получаем базовый промпт
        base_prompt = self.smart_prompts["review_generation"]["base_prompt"]
        
        # Добавляем контекстные инструкции
        context_instructions = self._build_context_instructions(product_analysis)
        
        # Добавляем информацию из карточки товара
        product_card_info = ""
        if product_info:
            product_card_info = "ИНФОРМАЦИЯ ИЗ КАРТОЧКИ ТОВАРА:\n"
            if product_info.get("description"):
                product_card_info += f"Описание: {product_info['description']}\n"
            if product_info.get("volume"):
                product_card_info += f"Объем: {product_info['volume']}\n"
            if product_info.get("weight"):
                product_card_info += f"Вес: {product_info['weight']}\n"
            if product_info.get("purpose"):
                product_card_info += f"Назначение: {product_info['purpose']}\n"
            if product_info.get("material"):
                product_card_info += f"Материал: {product_info['material']}\n"
            product_card_info += "\n"
        
        # Анализируем примеры
        examples_analysis = self._analyze_examples(examples)

        # Заполняем переменные для базового промпта
        examples_text = ""
        if examples:
            examples_text = "Примеры реальных отзывов:\n"
            for i, ex in enumerate(examples, 1):
                examples_text += f"{i}. {ex.get('author', 'Аноним')} ({ex.get('rating', 5)}★): {ex.get('text', '')}\n"

        # ВАЖНО: base_prompt может содержать JSON-пример с фигурными скобками.
        # Используем безопасную подстановку только наших плейсхолдеров без .format().
        base_prompt_rendered = str(base_prompt)
        base_prompt_rendered = base_prompt_rendered.replace("{product_name}", str(product_name))
        base_prompt_rendered = base_prompt_rendered.replace("{examples_section}", str(examples_text))
        base_prompt_rendered = base_prompt_rendered.replace("{count}", str(count))
        
        rules_block = """
КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА:
- ИСПОЛЬЗУЙ ТОЛЬКО характеристики из названия товара, карточки товара и примеров
- ОБЯЗАТЕЛЬНО учитывай вес и объем из карточки товара
- НЕ ПРИДУМЫВАЙ назначение если оно не очевидно из названия или карточки
- Если "ящик 250л" - НЕ пиши про легкую переноску (250л = ~250кг!)
- Если "крышка для колодца" - НЕ пиши про емкости, баки, монтаж
- Если "крышка для емкости" - НЕ пиши про колодцы
- ПИШИ ТОЛЬКО про реальное использование товара с учетом характеристик

ТРЕБОВАНИЯ К СТРУКТУРЕ ОТЗЫВА:
- ОБЯЗАТЕЛЬНО включи плюсы (преимущества товара)
- ОБЯЗАТЕЛЬНО включи минусы (недостатки или мелкие неудобства)
- Плюсы и минусы должны быть реалистичными и краткими
- Примеры плюсов: "прочный", "легкий", "плотно прилегает", "долговечный"
- Примеры минусов: "требует аккуратного монтажа", "нет инструкции", "цена выше ожиданий"

ФОРМАТ JSON:
[
  {
    "author": "Имя",
    "rating": 5,
    "content": "Текст отзыва - описание опыта использования товара",
    "pros": "Плюсы через запятую: прочный, легкий, плотно прилегает",
    "cons": "Минусы через запятую: требует аккуратного монтажа, нет инструкции",
    "date": "2025-01-15"
  }
]

ВАЖНО:
- content: основной текст отзыва (50-150 слов)
- pros: отдельное поле с плюсами (2-3 пункта через запятую)
- cons: отдельное поле с минусами (1-2 пункта через запятую)
- НЕ включай плюсы/минусы в content - они в отдельных полях!
- НЕ ПИШИ "монтаж" если товар не монтируется (крышка на колодец просто кладется)
- ПРОВЕРЬ вес и объем перед написанием отзыва о переноске!
- ПРОВЕРЬ назначение товара перед написанием отзыва!
"""

        full_prompt = "\n".join(
            [
                base_prompt_rendered,
                "",
                product_card_info.rstrip(),
                "КОНТЕКСТ ИЗДЕЛИЯ:",
                context_instructions,
                "",
                "АНАЛИЗ ПРИМЕРОВ:",
                examples_analysis,
                "",
                rules_block.strip(),
            ]
        )

        app_logger.info(f"Построен контекстуальный промпт для товара: {product_name}")
        app_logger.info(f"Тип изделия: {product_analysis['type']}, Материал: {product_analysis['material']}")
        
        return full_prompt

    def get_cascade_settings(self) -> Dict:
        cascade = self.smart_prompts.get("review_cascade", {}) if isinstance(self.smart_prompts, dict) else {}
        try:
            max_iterations = int(cascade.get("max_iterations", 2))
        except Exception:
            max_iterations = 2
        if max_iterations < 0:
            max_iterations = 0

        generator_default = str(cascade.get("generator_model", "perplexity"))
        verifier_default = str(cascade.get("verifier_model", "deepseek"))
        repair_default = str(cascade.get("repair_model", ""))

        return {
            "max_iterations": max_iterations,
            "generator_model": generator_default,
            "verifier_model": verifier_default,
            "repair_model": repair_default,
            "validation_prompt": str(cascade.get("validation_prompt", "")),
            "repair_prompt": str(cascade.get("repair_prompt", "")),
        }

    def build_validation_prompt(self, product_name: str, review: Dict, product_info: Dict = None) -> str:
        product_analysis = self.analyze_product_name(product_name)
        context_instructions = self._build_context_instructions(product_analysis)

        product_card_info = ""
        if product_info:
            product_card_info = "ИНФОРМАЦИЯ ИЗ КАРТОЧКИ ТОВАРА:\n"
            if product_info.get("description"):
                product_card_info += f"Описание: {product_info['description']}\n"
            if product_info.get("volume"):
                product_card_info += f"Объем: {product_info['volume']}\n"
            if product_info.get("weight"):
                product_card_info += f"Вес: {product_info['weight']}\n"
            if product_info.get("purpose"):
                product_card_info += f"Назначение: {product_info['purpose']}\n"
            if product_info.get("material"):
                product_card_info += f"Материал: {product_info['material']}\n"

        cascade = self.get_cascade_settings()
        base = cascade.get("validation_prompt")

        if not base.strip():
            base = (
                "Ты - строгий валидатор качества отзывов. Твоя задача: проверить ОДИН отзыв на соответствие товару. "
                "НЕЛЬЗЯ добавлять новые факты. НЕЛЬЗЯ менять смысл товара.\n\n"
                "Входные данные: название товара, карточка товара, контекстные правила, отзыв.\n\n"
                "Проверь критерии:\n"
                "1) Только факты из названия/карточки/контекста (никаких выдумок)\n"
                "2) Нет смешивания с другими товарами\n"
                "3) Логика веса/объема/переноски корректна\n"
                "4) Нет запрещенных тем (электроника/нержавейка для пластика и т.п.)\n"
                "5) pros/cons отделены от content и краткие\n"
                "6) Нормальный русский, без маркетинговых штампов\n"
                "7) Реалистичность сценария использования\n"
                "8) Поля присутствуют: author,rating,content,pros,cons\n\n"
                "Ответ строго в JSON-объекте:\n"
                "{\n"
                "  \"ok\": true/false,\n"
                "  \"issues\": [\n"
                "    {\"code\": \"HALLUCINATION\"|\"MISMATCH\"|\"LOGIC\"|\"FORMAT\", \"field\": \"content\"|\"pros\"|\"cons\"|\"rating\"|\"author\", \"detail\": \"...\"}\n"
                "  ],\n"
                "  \"notes\": \"коротко\"\n"
                "}\n"
            )

        review_json = json.dumps(review, ensure_ascii=False)
        full_prompt = "\n".join(
            [
                base.strip(),
                "",
                f"ТОВАР: {product_name}",
                "",
                product_card_info.rstrip(),
                "КОНТЕКСТ ИЗДЕЛИЯ:",
                context_instructions,
                "",
                "ОТЗЫВ ДЛЯ ПРОВЕРКИ (JSON):",
                review_json,
            ]
        )
        return full_prompt

    def build_repair_prompt(self, product_name: str, review: Dict, issues: List[Dict], product_info: Dict = None) -> str:
        product_analysis = self.analyze_product_name(product_name)
        context_instructions = self._build_context_instructions(product_analysis)

        product_card_info = ""
        if product_info:
            product_card_info = "ИНФОРМАЦИЯ ИЗ КАРТОЧКИ ТОВАРА:\n"
            if product_info.get("description"):
                product_card_info += f"Описание: {product_info['description']}\n"
            if product_info.get("volume"):
                product_card_info += f"Объем: {product_info['volume']}\n"
            if product_info.get("weight"):
                product_card_info += f"Вес: {product_info['weight']}\n"
            if product_info.get("purpose"):
                product_card_info += f"Назначение: {product_info['purpose']}\n"
            if product_info.get("material"):
                product_card_info += f"Материал: {product_info['material']}\n"

        cascade = self.get_cascade_settings()
        base = cascade.get("repair_prompt")
        if not base.strip():
            base = (
                "Ты - редактор отзывов. Исправь отзыв строго по списку проблем. "
                "ЗАПРЕЩЕНО добавлять новые факты (никаких новых характеристик). "
                "Если факт не подтвержден карточкой/названием/контекстом — УДАЛИ его или перефразируй нейтрально.\n\n"
                "Требования:\n"
                "- Сохрани структуру полей: author,rating,content,pros,cons\n"
                "- content 50-150 слов, естественный русский\n"
                "- pros 2-3 пункта через запятую\n"
                "- cons 1-2 пункта через запятую\n"
                "- Не переносить pros/cons в content\n\n"
                "Ответ: строго JSON-объект отзыва (не массив, без markdown).\n"
            )

        review_json = json.dumps(review, ensure_ascii=False)
        issues_json = json.dumps(issues or [], ensure_ascii=False)
        full_prompt = "\n".join(
            [
                base.strip(),
                "",
                f"ТОВАР: {product_name}",
                "",
                product_card_info.rstrip(),
                "КОНТЕКСТ ИЗДЕЛИЯ:",
                context_instructions,
                "",
                "ПРОБЛЕМЫ (JSON):",
                issues_json,
                "",
                "ИСХОДНЫЙ ОТЗЫВ (JSON):",
                review_json,
            ]
        )
        return full_prompt
    
    def _build_context_instructions(self, product_analysis: Dict) -> str:
        """Построить контекстные инструкции с использованием базы знаний."""
        product_name = product_analysis["name"]
        product_knowledge = self.get_product_knowledge(product_name)
        common_rules = self.knowledge_base.get("common_rules", {})
        
        instructions = []
        
        # Добавляем знания из базы
        if product_knowledge:
            instructions.append(f"ТИП: {product_knowledge.get('description', '')}")
            
            # Особые правила для категорий
            if "ящики" in product_knowledge.get('description', '').lower():
                # Анализируем объем для ящиков
                volume_match = re.search(r'(\d+)\s*[лl]', product_name.lower())
                if volume_match:
                    volume = int(volume_match.group(1))
                    volume_logic = product_knowledge.get('volume_logic', {})
                    
                    if volume <= volume_logic.get('small', {}).get('max_volume', 50):
                        instructions.append(f"ОБЪЕМ {volume}л: можно переносить вручную")
                    elif volume <= volume_logic.get('medium', {}).get('max_volume', 99):
                        instructions.append(f"ОБЪЕМ {volume}л: требует усилий, можно вдвоем")
                    else:
                        weight = volume  # ~1кг на 1 литр
                        instructions.append(f"ОБЪЕМ {volume}л: вес ~{weight}кг, НУЖНА ТЕХНИКА")
                        instructions.append("ЗАПРЕТ: НЕ пиши про 'легкую переноску'!")
            
            elif "крышки" in product_knowledge.get('description', '').lower():
                # Определяем тип крышки
                name_lower = product_name.lower()
                if "колодц" in name_lower:
                    cover_type = product_knowledge.get('types', {}).get('для_колодца', {})
                    instructions.append(f"УСТАНОВКА: {cover_type.get('installation', '')}")
                    if not cover_type.get('mounting_required', True):
                        instructions.append("ЗАПРЕТ: НЕ пиши про монтаж!")
                elif "емкост" in name_lower or "бак" in name_lower:
                    cover_type = product_knowledge.get('types', {}).get('для_емкости', {})
                    instructions.append(f"УСТАНОВКА: {cover_type.get('installation', '')}")
            
            # Добавляем материалы
            materials = product_knowledge.get('materials', [])
            if materials:
                instructions.append(f"МАТЕРИАЛЫ: {', '.join(materials)}")
            
            # Добавляем сценарии использования
            scenarios = product_knowledge.get('usage_scenarios', [])
            if scenarios:
                instructions.append("СЦЕНАРИИ ИСПОЛЬЗОВАНИЯ:")
                for scenario in scenarios:
                    instructions.append(f"- {scenario}")
        
        # Добавляем общие правила
        if common_rules:
            instructions.append("\nОБЩИЕ ПРАВИЛА ПРОЕКТА:")
            
            # Материалы
            allowed_materials = common_rules.get('materials', {}).get('allowed', [])
            forbidden_materials = common_rules.get('materials', {}).get('forbidden', [])
            if allowed_materials:
                instructions.append(f"РАЗРЕШЕННЫЕ МАТЕРИАЛЫ: {', '.join(allowed_materials)}")
            if forbidden_materials:
                instructions.append(f"ЗАПРЕЩЕННЫЕ МАТЕРИАЛЫ: {', '.join(forbidden_materials)}")
            
            # Функции
            forbidden_features = common_rules.get('features', {}).get('forbidden', [])
            if forbidden_features:
                instructions.append(f"ЗАПРЕЩЕННЫЕ ХАРАКТЕРИСТИКИ: {', '.join(forbidden_features)}")
            
            # Логика использования
            usage_logic = common_rules.get('usage_logic', {})
            if usage_logic.get('large_containers'):
                instructions.append(f"ПРАВИЛО: {usage_logic.get('large_containers', '')}")
        
        return "\n".join(instructions)
    
    def _analyze_examples(self, examples: List[Dict]) -> str:
        """Анализировать примеры отзывов для извлечения инсайтов."""
        if not examples:
            return "Примеров нет. Создавай отзывы на основе базовых знаний о товаре."
        
        insights = []
        
        # Анализируем тематику
        all_texts = " ".join([ex.get('text', '') for ex in examples])
        
        if "дач" in all_texts.lower() or "сад" in all_texts.lower():
            insights.append("Покупатели используют на даче/саду")
        
        if "вод" in all_texts.lower():
            insights.append("Основное назначение - хранение/использование воды")
        
        if "прочн" in all_texts.lower() or "крепк" in all_texts.lower():
            insights.append("Важна прочность конструкции")
        
        if "объем" in all_texts.lower():
            insights.append("Важен объем емкости")
        
        return "ИНСАЙТЫ: " + "; ".join(insights) if insights else "ИНСАЙТЫ: Создавай общие отзывы о пластиковых изделиях"
    
    def set_project_context(self, project_context: Dict):
        """Установить контекст проекта."""
        self.current_project_context = project_context
        app_logger.info(f"Установлен контекст проекта: {project_context}")
    
    def get_validation_rules(self) -> List[str]:
        """Получить правила валидации."""
        return self.smart_prompts["review_generation"]["error_prevention"]["validation_rules"]
