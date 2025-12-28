"""
Parser Service - Service for parsing reviews from product pages
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin, urlparse
from core.database import db
from core.models import ReviewExample, ProductTask, Project


class ParserService:
    """Service for parsing product reviews from websites."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def parse_product_reviews(self, product_task_id: int) -> Tuple[int, str]:
        """
        Parse reviews for a product task.
        
        Args:
            product_task_id: ID of the product task
            
        Returns:
            Tuple of (count of parsed reviews, status message)
        """
        with db.get_session() as session:
            product_task = session.query(ProductTask).filter_by(id=product_task_id).first()
            if not product_task:
                return 0, "Product task not found"
            
            # Get project through period relationship
            period = product_task.period
            if not period:
                return 0, "Period not found for product task"
            
            project = period.project
            if not project:
                return 0, "Project not found for period"
            
            # Determine URL to parse
            url = product_task.product_url
            if not url:
                # Search for product on site
                url = self._find_product_url(project.site_url, product_task.product_name)
                if not url:
                    product_task.parse_status = "failed"
                    product_task.parsed_at = datetime.utcnow()

                    session.commit()
                    return 0, f"Could not find product '{product_task.product_name}' on site"
                
                product_task.parsed_url = url
            
            
            # Parse reviews from URL
            try:
                print(f"Parsing reviews from: {url}")
                reviews = self._parse_reviews_from_page(url)
                
                # Save reviews to ReviewExample (even if 0)
                count = 0
                for review_data in reviews:
                    example = ReviewExample(
                        product_name=product_task.product_name,
                        content=review_data.get('content', ''),
                        pros=review_data.get('pros'),
                        cons=review_data.get('cons'),
                        author=review_data.get('author'),
                        rating=review_data.get('rating'),
                        review_date=review_data.get('date'),
                        source='parsed',
                        source_url=url,
                        is_good_example=True
                    )
                    session.add(example)
                    count += 1
                
                # Mark as success even if no reviews found
                # (product characteristics can still be used for AI)
                product_task.parse_status = "success" if count > 0 else "no_reviews"
                product_task.parsed_at = datetime.utcnow()
                session.commit()
                
                if count > 0:
                    return count, f"Successfully parsed {count} reviews"
                else:
                    return 0, "No reviews found (will use product characteristics for AI generation)"
                
            except Exception as e:
                print(f"Exception during parsing: {e}")
                import traceback
                traceback.print_exc()

                product_task.parse_status = "failed"
                product_task.parsed_at = datetime.utcnow()
                session.commit()
                return 0, f"Error parsing reviews: {str(e)}"
    
    def _find_product_url(self, site_url: str, product_name: str) -> Optional[str]:
        """
        Search for product URL on site.
        
        Args:
            site_url: Base site URL
            product_name: Name of the product to search
            
        Returns:
            Product URL if found, None otherwise
        """
        try:
            # Try to search on site
            search_url = f"{site_url}/search?q={product_name}"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Look for product links (common patterns)
            # This is site-specific and may need adjustment
            product_links = soup.find_all('a', href=re.compile(r'/catalog/|/product/|/tovar/'))
            
            if product_links:
                # Return first non-duplicate link
                first_link = product_links[0].get('href')
                return urljoin(site_url, first_link)
            
            return None
            
        except Exception as e:
            print(f"Error searching for product: {e}")
            return None
    
    def _parse_reviews_from_page(self, url: str) -> List[Dict]:
        """
        Parse reviews from a product page.
        
        Args:
            url: URL of the product page
            
        Returns:
            List of review dictionaries
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            reviews = []
            
            # Strategy 1: Look for schema.org markup (often hidden but contains structured data)
            schema_reviews = soup.find_all(
                ['div', 'article'],
                attrs={'itemprop': 'review'}
            )
            
            if schema_reviews:
                print(f"Found {len(schema_reviews)} schema.org reviews")
                for element in schema_reviews:
                    review_data = self._extract_schema_review(element)
                    if review_data and review_data.get('content'):
                        reviews.append(review_data)
            
            # Strategy 2: Look for elements with "review" in class or id (visible reviews)
            if not reviews:
                review_elements = soup.find_all(
                    ['div', 'article', 'section'],
                    class_=re.compile(r'review|отзыв', re.IGNORECASE)
                )
                
                for element in review_elements:
                    # Skip hidden elements
                    if 'hidden' in element.get('class', []):
                        continue
                    review_data = self._extract_review_data(element)
                    if review_data and review_data.get('content'):
                        reviews.append(review_data)
            
            # Strategy 3: Look for elements with data-review or similar attributes
            if not reviews:
                review_elements = soup.find_all(
                    ['div', 'article'],
                    attrs={'data-review': True}
                )
                
                for element in review_elements:
                    review_data = self._extract_review_data(element)
                    if review_data and review_data.get('content'):
                        reviews.append(review_data)
            
            print(f"Total reviews extracted: {len(reviews)}")
            return reviews
            
        except Exception as e:
            print(f"Error parsing page {url}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _extract_schema_review(self, element) -> Optional[Dict]:
        """
        Extract review data from schema.org markup.
        
        Args:
            element: BeautifulSoup element with itemprop="review"
            
        Returns:
            Dictionary with review data
        """
        try:
            review_data = {}
            
            # Extract author
            author_elem = element.find(attrs={'itemprop': 'author'})
            if author_elem:
                review_data['author'] = author_elem.get('content', author_elem.get_text(strip=True))
            
            # Extract review body
            body_elem = element.find(attrs={'itemprop': 'reviewBody'})
            if body_elem:
                # Look for specific tags within reviewBody
                comment_elem = body_elem.find('comment')
                virtues_elem = body_elem.find('virtues')
                limitations_elem = body_elem.find('limitations')
                
                if comment_elem:
                    review_data['content'] = comment_elem.get_text(strip=True)
                else:
                    review_data['content'] = body_elem.get_text(strip=True)
                
                if virtues_elem:
                    review_data['pros'] = virtues_elem.get_text(strip=True)
                
                if limitations_elem:
                    review_data['cons'] = limitations_elem.get_text(strip=True)
            
            # Extract rating
            rating_elem = element.find(attrs={'itemprop': 'reviewRating'})
            if rating_elem:
                rating_value = rating_elem.find(attrs={'itemprop': 'ratingValue'})
                if rating_value:
                    try:
                        review_data['rating'] = int(rating_value.get('content', rating_value.get_text(strip=True)))
                    except:
                        pass
            
            return review_data if review_data.get('content') else None
            
        except Exception as e:
            print(f"Error extracting schema review: {e}")
            return None

    
    def _extract_review_data(self, element) -> Optional[Dict]:
        """
        Extract review data from a review element.
        
        Args:
            element: BeautifulSoup element containing review
            
        Returns:
            Dictionary with review data
        """
        try:
            review_data = {}
            
            # Extract content (main review text)
            content_elem = element.find(['p', 'div', 'span'], class_=re.compile(r'text|content|body|описание', re.IGNORECASE))
            if content_elem:
                review_data['content'] = content_elem.get_text(strip=True)
            else:
                # Fallback: get all text from element
                review_data['content'] = element.get_text(strip=True)
            
            # Extract author
            author_elem = element.find(['span', 'div', 'p'], class_=re.compile(r'author|name|user|автор|имя', re.IGNORECASE))
            if author_elem:
                review_data['author'] = author_elem.get_text(strip=True)
            
            # Extract rating (look for stars, numbers, etc.)
            rating_elem = element.find(['span', 'div'], class_=re.compile(r'rating|star|оценка|рейтинг', re.IGNORECASE))
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                # Try to extract number from text
                rating_match = re.search(r'(\d+)', rating_text)
                if rating_match:
                    review_data['rating'] = int(rating_match.group(1))
            
            # Extract date
            date_elem = element.find(['span', 'time', 'div'], class_=re.compile(r'date|time|дата|время', re.IGNORECASE))
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                # Try to parse date (basic attempt)
                try:
                    # This is a simple parser, may need improvement
                    review_data['date'] = datetime.strptime(date_text, '%d.%m.%Y')
                except:
                    pass
            
            # Extract pros/cons if available
            pros_elem = element.find(['div', 'p', 'span'], class_=re.compile(r'pros|plus|достоинства|плюсы', re.IGNORECASE))
            if pros_elem:
                review_data['pros'] = pros_elem.get_text(strip=True)
            
            cons_elem = element.find(['div', 'p', 'span'], class_=re.compile(r'cons|minus|недостатки|минусы', re.IGNORECASE))
            if cons_elem:
                review_data['cons'] = cons_elem.get_text(strip=True)
            
            return review_data if review_data.get('content') else None
            
        except Exception as e:
            print(f"Error extracting review data: {e}")
            return None


# Singleton instance
parser_service = ParserService()
