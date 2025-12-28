import sys
from PyQt6.QtWidgets import QApplication
from core.database import db
from core.models import Project, Period, ProductTask
from ui.widgets.work_area import WorkArea
from datetime import datetime, timedelta

def init_db():
    print("Initializing DB...")
    db.create_tables()
    project_id = 1
    period_id = 1
    
    with db.get_session() as session:
        # Ensure project exists
        project = session.query(Project).first()
        if not project:
            print("Creating test project...")
            project = Project(name="Test Project", site_url="http://test.com")
            session.add(project)
            session.commit()
        
        # Ensure period exists
        period = session.query(Period).first()
        if not period:
            print("Creating test period...")
            period = Period(
                project_id=project.id,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30),
                total_reviews_count=50,
                status="draft"
            )
            session.add(period)
            session.commit()
        period_id = period.id
        
        # Ensure at least one product exists
        if session.query(ProductTask).filter_by(period_id=period_id).count() == 0:
             print("Creating test product...")
             session.add(ProductTask(period_id=period_id, product_name="Test Product", review_count=5, product_url="http://example.com"))
             session.commit()
             
    print(f"DB initialized. Using Period ID: {period_id}")
    return period_id

def main():
    app = QApplication(sys.argv)
    try:
        period_id = init_db()
        
        print("Launching WorkArea...")
        window = WorkArea()
        window.setWindowTitle(f"Debug Work Area (Period {period_id})")
        window.resize(1000, 700)
        
        print(f"Setting period to {period_id}...")
        window.set_period(period_id)
        
        window.show()
        print("WorkArea launched. Check if tabs (Products, Reviews) are visible and populated.")
        
        # Auto-close after 5 seconds to avoid hanging if user is just watching output
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(5000, app.quit)
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"CRITICAL ERROR in debug script: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
