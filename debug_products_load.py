"""
Debug script to test product loading and display
"""
from core.database import db
from core.models import ProductTask, Period

print("Testing product loading...")

with db.get_session() as session:
    # Get period
    period = session.query(Period).first()
    if not period:
        print("No period found!")
        exit()
    
    print(f"Period ID: {period.id}")
    
    # Load products
    products = session.query(ProductTask).filter_by(period_id=period.id).all()
    print(f"Found {len(products)} products")
    
    for product in products:
        print(f"\nProduct {product.id}:")
        print(f"  Name: {product.product_name}")
        print(f"  Review count: {product.review_count}")
        print(f"  URL: {product.product_url}")
        print(f"  Parsed URL: {product.parsed_url}")
        print(f"  Parse status: {product.parse_status}")
        print(f"  Is used: {product.is_used}")
        
        # Try to access relationships
        try:
            print(f"  Period: {product.period.id if product.period else 'None'}")
        except Exception as e:
            print(f"  ERROR accessing period: {e}")
        
        try:
            print(f"  Reviews: {len(product.reviews)}")
        except Exception as e:
            print(f"  ERROR accessing reviews: {e}")

print("\n✓ Test completed")
