"""
Generator Engine - Powered by Mistral API
"""
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
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
            self.client = MistralClient(api_key=self.api_key)
    
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
            
        prompt = f"""
        Based on the following product information, generate {count} UNIQUE draft reviews.
        
        Product Info:
        {product_info}
        
        Requirements:
        1. "author": A realistic Russian name.
        2. "rating": An integer between 1 and 5 (vary them realistically, mostly 4-5, occasional 3).
        3. "pros": A short list of pros.
        4. "cons": A short list of cons (if rating < 5).
        5. "content": The main review text. It should be natural, "human-like", mentioning specific features from the Product Info. Avoid marketing clichés.
        
        Output format: A JSON array of objects.
        """
        
        try:
            chat_response = self.client.chat(
                model="mistral-large-latest",
                messages=[
                    ChatMessage(role="system", content="You are a creative copywriter generating authentic product reviews."),
                    ChatMessage(role="user", content=prompt)
                ],
                response_format={"type": "json_object"}
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
            
            return reviews
            
        except Exception as e:
            print(f"Mistral generation error: {e}")
            return []

# Global instance
generator_engine = GeneratorEngine()
