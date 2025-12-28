"""
Debug script to test product creation
"""
from core.database import db
from core.models import Project, Period, ProductTask
from datetime import datetime, timedelta

print("Testing product creation...")

with db.get_session() as session:
    # Get or create test project
    project = session.query(Project).first()
    if not project:
        project = Project(
            name="Test Project",
            site_url="https://polimer-group.com",
            description="Test"
        )
        session.add(project)
        session.commit()
        session.refresh(project)
    
    print(f"Project: {project.name} (ID: {project.id})")
    
    # Get or create test period
    period = session.query(Period).filter_by(project_id=project.id).first()
    if not period:
        period = Period(
            project_id=project.id,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            total_reviews_count=100,
            status="draft"
        )
        session.add(period)
        session.commit()
        session.refresh(period)
    
    print(f"Period: {period.id} ({period.start_date.date()} to {period.end_date.date()})")
    
    # Try to create product
    try:
        product = ProductTask(
            period_id=period.id,
            product_name="Test Product",
            review_count=None,
            product_url=""
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        print(f"✓ Product created successfully: {product.product_name} (ID: {product.id})")
        print(f"  - review_count: {product.review_count}")
        print(f"  - parsed_url: {product.parsed_url}")
        print(f"  - parse_status: {product.parse_status}")
    except Exception as e:
        print(f"✗ Error creating product: {e}")
        import traceback
        traceback.print_exc()
