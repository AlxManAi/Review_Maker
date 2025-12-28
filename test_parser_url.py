"""
Test parser on specific URL to debug review extraction
"""
from core.parser_service import parser_service

# URL from user
url = "https://polimer-group.com/catalog/tovary_dlya_doma_i_sada/dushevye_baki/novyy_bak_dushevoy_130_litrov_s_podogrevom"

print(f"Testing parser on: {url}")
print("="*80)

reviews = parser_service._parse_reviews_from_page(url)

print(f"\n{'='*80}")
print(f"RESULT: Found {len(reviews)} reviews")
print("="*80)

for i, review in enumerate(reviews, 1):
    print(f"\n--- Review {i} ---")
    print(f"Author: {review.get('author', 'N/A')}")
    print(f"Rating: {review.get('rating', 'N/A')}")
    print(f"Pros: {review.get('pros', 'N/A')}")
    print(f"Cons: {review.get('cons', 'N/A')}")
    print(f"Content: {review.get('content', 'N/A')[:300]}...")
    print(f"Date: {review.get('date', 'N/A')}")
