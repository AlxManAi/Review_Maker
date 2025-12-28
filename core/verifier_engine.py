"""
Verifier Engine - Powered by DeepSeek API
"""
from openai import OpenAI
from config.settings import settings
from typing import Dict
import json


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
        You are a Review Quality Assurance Expert.
        
        Task: Review and refine the following draft review for technical accuracy, logic, and "human-like" tone.
        
        Product Info:
        {product_info}
        
        Draft Review:
        {json.dumps(draft_review, ensure_ascii=False)}
        
        Checklist:
        1. **Technical Accuracy**: Ensure mentioned features exist in Product Info. Correct contradictions (e.g. if draft says 220W but product is 1500W).
        2. **Tone**: Remove robotic/marketing clichés (e.g., "I am delighted to purchase"). Make it sound like a real person.
        3. **Logic**: Ensure pros/cons match the rating.
        4. **Uniqueness**: Rephrase slightly to ensure distinctness.
        
        Output:
        Return the polished review as a JSON object with the same structure (author, rating, pros, cons, content).
        """
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a meticulous editor."},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            
            content = response.choices[0].message.content
            
            # Simple JSON cleanup (sometimes models wrap in ```json ... ```)
            cleaned_content = content.replace("```json", "").replace("```", "").strip()
            
            refined_review = json.loads(cleaned_content)
            return refined_review
            
        except Exception as e:
            print(f"DeepSeek verification error: {e}")
            return draft_review # Fallback to draft

# Global instance
verifier_engine = VerifierEngine()
