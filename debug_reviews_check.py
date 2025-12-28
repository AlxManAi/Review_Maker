import sys
from core.database import db
from core.models import Review, ProductTask, Period

def check_db():
    print("Checking database for reviews...")
    db.create_tables() # Ensure connection
    
    with db.get_session() as session:
        # 1. List all periods
        periods = session.query(Period).all()
        print(f"Total Periods: {len(periods)}")
        for p in periods:
            print(f"Period ID: {p.id}, Project ID: {p.project_id}")
            
        # 2. List all products
        products = session.query(ProductTask).all()
        print(f"\nTotal Products: {len(products)}")
        for p in products:
            print(f"Product ID: {p.id}, Name: {p.product_name}, Period ID: {p.period_id}")
            
        # 3. List all reviews
        reviews = session.query(Review).all()
        print(f"\nTotal Reviews: {len(reviews)}")
        for r in reviews:
            print(f"Review ID: {r.id}")
            print(f"  Product: {r.product_name}")
            print(f"  Period ID: {r.period_id}")
            print(f"  Is Generated: {r.is_generated}")
            print(f"  Date: {r.target_date}")
            print(f"  Content Snippet: {r.content[:30]}...")
            
if __name__ == "__main__":
    check_db()
