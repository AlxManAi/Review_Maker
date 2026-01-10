"""
Generator Engine - Powered by Mistral API
"""
from mistralai import Mistral
from config.settings import settings
from typing import Dict, List
import json


class GeneratorEngine:
    """
    Generator Engine utilizing Mistral API to draft initial reviews.
    """
    
    def __init__(self):
        self.api_key = settings.mistral_api_key
        if not self.api_key:
            print("Warning: MISTRAL_API_KEY is not set.")
        else:
            self.client = Mistral(api_key=self.api_key)
    
    def _get_few_shot_examples(self, limit: int = 3) -> str:
        """Fetch approved reviews to use as style examples."""
        try:
            from core.database import db
            from core.models import Review
            
            examples_text = ""
            with db.get_session() as session:
                # Get last approved reviews
                examples = session.query(Review).filter_by(is_approved=True).order_by(Review.id.desc()).limit(limit).all()
                
                if not examples:
                    return ""
                
                examples_text = "\nHere are examples of GOOD reviews (copy their style, length, and tone):\n"
                for i, ex in enumerate(examples, 1):
                    examples_text += f"""
                    Example {i}:
                    Author: {ex.author}
                    Rating: {ex.rating}
                    Pros: {ex.pros}
                    Cons: {ex.cons}
                    Review: {ex.content}
                    """
            return examples_text
        except Exception as e:
            print(f"Error fetching examples: {e}")
            return ""

    def generate_draft(self, product_info: str, count: int = 1) -> List[Dict]:
        """
        Generate draft reviews based on product info.
        
        Args:
            product_info: Raw text/JSON from SearchEngine containing specs and context.
            count: Number of drafts to generate.
            
        Returns:
            List of dictionaries representing draft reviews.
        """
        if not self.api_key:
            return [{"error": "Mistral API key missing"}]
            
        # Get few-shot examples
        examples_section = self._get_few_shot_examples(limit=3)
            
        prompt = f"""
        Based on the following product information, generate {count} UNIQUE draft reviews.
        
        Product Info:
        {product_info}
        
        {examples_section}
        
        Requirements:
        1. "author": A realistic Russian name.
        2. "rating": An integer between 1 and 5 (vary them realistically, mostly 4-5, occasional 3).
        3. "pros": A short list of pros.
        4. "cons": A short list of cons (if rating < 5).
        5. "content": The main review text. It should be natural, "human-like", mentioning specific features from the Product Info. Avoid marketing clichés.
        
        Output format: A JSON array of objects.
        """
        
        try:
            chat_response = self.client.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {"role": "system", "content": "You are an NLP researcher creating educational examples for sentiment analysis. These are NOT real reviews, but training samples for machine learning models."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = chat_response.choices[0].message.content
            # Parse JSON response
            reviews = json.loads(content)
            
            # Ensure it's a list (Mistral might wrap it in a key)
            if isinstance(reviews, dict):
                # Look for a list value
                for key, value in reviews.items():
                    if isinstance(value, list):
                        reviews = value
                        break
            
            # Ensure all reviews have required fields
            processed_reviews = []
            for review in reviews:
                processed_review = {
                    "author": review.get("author", "Покупатель"),
                    "rating": review.get("rating", 5),
                    "pros": review.get("pros", ""),
                    "cons": review.get("cons", ""),
                    "content": review.get("content", "")
                }
                processed_reviews.append(processed_review)
            
            return processed_reviews
            
        except Exception as e:
            print(f"Mistral generation error: {e}")
            return []

# Global instance
generator_engine = GeneratorEngine()
