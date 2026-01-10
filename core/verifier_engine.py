"""
Verifier Engine - Powered by DeepSeek API
"""
from openai import OpenAI
from config.settings import settings
from typing import Dict
import json
import re


class VerifierEngine:
    """
    Verifier Engine utilizing DeepSeek API to refine and validate reviews.
    """
    
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        if not self.api_key:
            print("Warning: DEEPSEEK_API_KEY is not set.")
        else:
            # DeepSeek is OpenAI-compatible
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
    
    def verify_and_refine(self, draft_review: Dict, product_info: str) -> Dict:
        """
        Verify and refine a single draft review.
        
        Args:
            draft_review: Dictionary containing draft review data (content, rating, etc.).
            product_info: Original product info for fact-checking.
            
        Returns:
            Refined review dictionary.
        """
        if not self.api_key:
            return draft_review # Return as-is if no key
            
        prompt = f"""
        You are an NLP researcher refining educational examples for sentiment analysis.
        
        Task: Review and refine the following draft example to ensure it's suitable for machine learning training.
        
        Product Info:
        {product_info}
        
        Draft Example:
        {json.dumps(draft_review, ensure_ascii=False)}
        
        Checklist:
        1. **Educational Purpose**: Ensure this is clearly a training sample, not a real review
        2. **Technical Accuracy**: Ensure mentioned features exist in Product Info
        3. **Natural Language**: Make it sound like authentic text for NLP training
        4. **Complete Structure**: Ensure all fields (author, rating, pros, cons, content) are present
        
        Output:
        Return the refined example as a JSON object with the same structure.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are an NLP researcher refining educational examples for sentiment analysis."},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            
            content = response.choices[0].message.content
            
            # Simple JSON cleanup (sometimes models wrap in ```json ... ```)
            cleaned_content = content.replace("```json", "").replace("```", "").strip()
            
            refined_review = json.loads(cleaned_content)
            
            # Ensure author field exists
            if "author" not in refined_review or not refined_review["author"]:
                refined_review["author"] = draft_review.get("author", "Покупатель")
            
            # Ensure pros and cons are strings, not lists
            if isinstance(refined_review.get("pros"), list):
                refined_review["pros"] = ", ".join(refined_review["pros"])
            if isinstance(refined_review.get("cons"), list):
                refined_review["cons"] = ", ".join(refined_review["cons"])
            
            # Remove emojis and stars from content
            if refined_review.get("content"):
                # Убираем цифры в скобках [1], [2], [3] и т.д.
                refined_review["content"] = re.sub(r"\[\d+\]", "", refined_review["content"])
                # Убираем звездочки и эмодзи
                refined_review["content"] = re.sub(r"[★⭐🌟✨💫⭕❌✓✔]", "", refined_review["content"])
                # Убираем множественные пробелы
                refined_review["content"] = re.sub(r"\s+", " ", refined_review["content"])
                # Убираем лишние символы пунктуации
                refined_review["content"] = re.sub(r"[^\w\s\.\,\!\?\-\:\;\(\)\[\]\"]", "", refined_review["content"])
                # Убедимся, что текст заканчивается на точку
                refined_review["content"] = refined_review["content"].strip()
                if refined_review["content"] and not refined_review["content"].endswith(('.','!','?')):
                    refined_review["content"] += '.'
            
            # Заменяем "Покупатель" на реальное имя
            if refined_review.get("author") == "Покупатель":
                import random
                names = ["Иван Петров", "Мария Сидорова", "Алексей Козлов", "Елена Иванова", 
                        "Дмитрий Смирнов", "Ольга Попова", "Сергей Новиков", "Наталья Волкова"]
                refined_review["author"] = random.choice(names)
            
            return refined_review
            
        except Exception as e:
            print(f"DeepSeek verification error: {e}")
            return draft_review # Fallback to draft

# Global instance
verifier_engine = VerifierEngine()
