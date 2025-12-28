"""
Test script for parser service
"""
from core.parser_service import parser_service

# Test URL from user
test_url = "https://polimer-group.com/catalog/emkosti_dlya_vody_i_drugikh_zhidkostey/uzkie_emkosti/emkost_n_200_litrov"

print(f"Testing parser on: {test_url}")
print("="*80)

reviews = parser_service._parse_reviews_from_page(test_url)

print(f"\nFound {len(reviews)} reviews")
print("="*80)

for i, review in enumerate(reviews, 1):
    print(f"\n--- Review {i} ---")
    print(f"Author: {review.get('author', 'N/A')}")
    print(f"Rating: {review.get('rating', 'N/A')}")
    print(f"Content: {review.get('content', 'N/A')[:200]}...")
    print(f"Pros: {review.get('pros', 'N/A')}")
    print(f"Cons: {review.get('cons', 'N/A')}")
    print(f"Date: {review.get('date', 'N/A')}")
