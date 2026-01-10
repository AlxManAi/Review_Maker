"""
Search Engine - Powered by Perplexity API
"""
import requests
from typing import Dict, List, Optional
from config.settings import settings


class SearchEngine:
    """
    Search Engine utilizing Perplexity API to gather product information.
    """
    BASE_URL = "https://api.perplexity.ai/chat/completions"
    
    def __init__(self):
        self.api_key = settings.perplexity_api_key
        if not self.api_key:
            print("Warning: PERPLEXITY_API_KEY is not set.")
    
    def search_product(self, query: str, url: Optional[str] = None) -> Dict:
        """
        Search for product details and reviews.
        
        Args:
            query: Product name/search query.
            url: Optional specific URL to analyze.
            
        Returns:
            Dict containing product info (name, specs, description) and context.
        """
        if not self.api_key:
            return {"error": "API key missing"}

        # Construct a prompt that asks Perplexity to act as a parser/scraper
        prompt = f"""
        Analyze the following product: '{query}'.
        {'URL: ' + url if url else 'Find the official product page or a major retailer page.'}
        
        Please extract the following details in a structured JSON format:
        1. "product_name": exact model name.
        2. "description": brief marketing description.
        3. "specs": key technical specifications (dimensions, power, materials, etc.).
        4. "existing_reviews": a summary of 3-5 real user reviews (if available) to understand the sentiment and typical pros/cons.
        5. "pros": list of common advantages.
        6. "cons": list of common disadvantages.
        
        ENSURE technical accuracy. Do NOT hallucinate features.
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-pro", # Using the 'online' model for search capabilities
            "messages": [
                {"role": "system", "content": "You are a precise product researcher agent."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1 # Low temp for factual accuracy
        }
        
        try:
            response = requests.post(self.BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Extract content from the first choice
            content = data["choices"][0]["message"]["content"]
            
            # Simple "parsing" since Perplexity returns text. 
            # In a real simplified version, we just return the text block 
            # or try to parse JSON if we enforced it strictly.
            # For now, we return the raw content to be processed by the Generator.
            
            return {
                "raw_data": content,
                "source": "perplexity"
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

# Global instance
search_engine = SearchEngine()
