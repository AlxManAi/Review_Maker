import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from core.database import db
from core.models import Project, Period, ProductTask
from ui.main_window import MainWindow
from datetime import datetime, timedelta

def init_db():
    print("Initializing DB for integration test...")
    db.create_tables()
    project_id = 1
    period_id = 1
    
    with db.get_session() as session:
        # Ensure project exists
        project = session.query(Project).first()
        if not project:
            project = Project(name="Test Project", site_url="http://test.com")
            session.add(project)
            session.commit()
        
        # Ensure period exists
        period = session.query(Period).first()
        if not period:
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
             
    print(f"DB initialized using Period ID: {period_id}")
    return period_id

def main():
    app = QApplication(sys.argv)
    target_period_id = init_db()
    
    print("Creating MainWindow...")
    window = MainWindow()
    window.resize(1000, 700)
    window.show()
    
    print("Integration Test Started")
    
    # Step 1: Check if starts at Projects (Index 0)
    def check_projects_view():
        idx = window.stack.currentIndex()
        print(f"Current Stack Index: {idx}")
        if idx == 0:
            print("SUCCESS: Starts at Projects Tab.")
            # Auto-select project and go to periods
            print("Simulating Project Selection...")
            window.show_periods(1) # Bypass click, test slot directly first
        else:
            print(f"FAILURE: Expected Index 0, got {idx}")
            
    # Step 2: Check if switched to Periods (Index 1)
    def check_periods_view():
        idx = window.stack.currentIndex()
        print(f"Current Stack Index: {idx}")
        if idx == 1:
            print("SUCCESS: Switched to Periods Tab.")
            # Auto-select period and go to WorkArea
            print("Simulating Period Selection (via signal emission from tab)...")
            # We select row 0 in periods tab and click open usually, 
            # here we will emit signal artificially from the tab object to verify MainWindow wiring
            print(f"Emitting period_selected({target_period_id}) from periods_tab...")
            window.periods_tab.period_selected.emit(target_period_id)
        else:
            print(f"FAILURE: Expected Index 1 (Periods), got {idx}")

    # Step 3: Check if switched to WorkArea (Index 2)
    def check_work_area_view():
        idx = window.stack.currentIndex()
        print(f"Current Stack Index: {idx}")
        if idx == 2:
            print("SUCCESS: Switched to WorkArea.")
            print("Verifying WorkArea content...")
            # Check if title updated
            print(f"WorkArea Title: {window.work_area.title_label.text()}")
        else:
            print(f"FAILURE: Expected Index 2 (WorkArea), got {idx}")

    # Schedule steps
    QTimer.singleShot(1000, check_projects_view)
    QTimer.singleShot(2000, check_periods_view)
    QTimer.singleShot(3000, check_work_area_view)
    QTimer.singleShot(5000, app.quit)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
