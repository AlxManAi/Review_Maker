import sys
from PyQt6.QtWidgets import QApplication
from core.database import db
from core.models import Project, Period, Review, ProductTask
from ui.tabs.generated_reviews_tab import GeneratedReviewsTab
from datetime import datetime

def check_reviews_rendering():
    print("Launching Reviews Tab Debugger...")
    app = QApplication(sys.argv)
    
    # Setup DB and Data
    db.create_tables()
    period_id = 1
    
    with db.get_session() as session:
        # Check actual dates
        reviews = session.query(Review).filter_by(period_id=period_id).all()
        print(f"DEBUG: Found {len(reviews)} reviews in DB.")
        for r in reviews:
            print(f" - Review {r.id}: {r.product_name} -> {r.target_date}")

    # Create UI
    window = GeneratedReviewsTab()
    window.resize(1000, 800)
    window.setWindowTitle("Debug Reviews Tab")
    
    print(f"Setting Period {period_id}...")
    window.set_period(period_id)
    window.show()
    
    print("Window shown. Do you see all 4 reviews?")
    
    # Timer to close
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(7000, app.quit)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    check_reviews_rendering()
