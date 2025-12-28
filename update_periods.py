"""
Update existing period with total_reviews_count
"""
from core.database import db
from core.models import Period

with db.get_session() as session:
    periods = session.query(Period).all()
    
    for period in periods:
        if period.total_reviews_count == 0:
            # Set default value
            period.total_reviews_count = 100
            print(f"Updated period {period.id}: total_reviews_count = 100")
    
    session.commit()
    print("\n✓ All periods updated!")
