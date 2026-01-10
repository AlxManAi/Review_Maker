"""
Orchestrator - Manages the generation pipeline and business logic
"""
import random
from datetime import timedelta, date, datetime
from typing import List, Dict

from core.search_engine import search_engine
from core.generator_engine import generator_engine
from core.verifier_engine import verifier_engine
from core.models import Review
from core.database import db

class Orchestrator:
    """
    Orchestrates the review generation pipeline:
    1. Search (Perplexity)
    2. Draft (Mistral)
    3. Verify (DeepSeek)
    4. Post-process (Date assignment)
    """
    
    def generate_reviews(self, 
                         query: str, 
                         total_count: int, 
                         start_date: date, 
                         end_date: date,
                         url: str = None) -> List[Review]:
        """
        Run the full generation pipeline.
        """
        # Step 1: Search & Context
        print(f"Step 1: Searching for {query}...")
        search_result = search_engine.search_product(query, url)
        
        if "error" in search_result:
            raise Exception(f"Search failed: {search_result['error']}")
            
        product_info = search_result.get("raw_data", "")
        
        # Step 2: Draft Generation
        # We generate slightly more drafts to allow for filtering/uniqueness checks if needed
        print(f"Step 2: Generating {total_count} drafts...")
        drafts = generator_engine.generate_draft(product_info, count=total_count)
        
        if not drafts:
             raise Exception("Draft generation failed")

        # Step 3: Verification & Refinement
        print("Step 3: Verifying and refining reviews...")
        refined_reviews = []
        for draft in drafts:
            refined = verifier_engine.verify_and_refine(draft, product_info)
            refined_reviews.append(refined)
            
        # Step 4: Date Distribution
        print("Step 4: Distributing dates...")
        dates = self._generate_date_distribution(start_date, end_date, len(refined_reviews))
        
        # Step 5: DB Conversion
        db_reviews = []
        with db.get_session() as session:
            for i, review_data in enumerate(refined_reviews):
                # Map to DB model
                review = Review(
                    product_name=query,
                    product_url=url,
                    content=review_data.get("content", ""),
                    pros=review_data.get("pros", ""), # Handle list vs string
                    cons=review_data.get("cons", ""),
                    author=review_data.get("author") or "Аноним",
                    rating=review_data.get("rating", 5),
                    target_date=datetime.combine(dates[i], datetime.min.time()),
                    source="AI Generated",
                    is_generated=True,
                    is_used=False
                )
                
                # Simple list to string conversion if needed
                if isinstance(review.pros, list): review.pros = ", ".join(review.pros)
                if isinstance(review.cons, list): review.cons = ", ".join(review.cons)
                
                session.add(review)
                db_reviews.append(review) # Note: ID might not be available until commit/refresh
            
            session.commit()
            
        return db_reviews

    def _generate_date_distribution(self, start_date: date, end_date: date, count: int) -> List[date]:
        """
        Distribute 'count' events uniformly between start_date and end_date.
        """
        days_diff = (end_date - start_date).days + 1
        if days_diff <= 0:
            return [start_date] * count
            
        # Uniform distribution
        dates = []
        for _ in range(count):
            random_days = random.randint(0, days_diff - 1)
            dates.append(start_date + timedelta(days=random_days))
        
        # Sort dates logic can be added here if we want sequential order, 
        # but random order is usually more natural for "posting".
        # However, TDD asks for uniform distribution. 
        # A simple random.randint is statistically uniform.
        # To be STRICTLY uniform (e.g. exactly 2 per day), we would need a different algo.
        # For now, random uniform is a good start.
        dates.sort()
        return dates

# Global instance
orchestrator = Orchestrator()
