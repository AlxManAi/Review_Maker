import sys
from PyQt6.QtWidgets import QApplication
from core.database import db
from core.models import Project, Period
from ui.tabs.periods_tab import PeriodsTab
from datetime import datetime, timedelta

def init_db():
    print("Initializing DB...")
    db.create_tables()
    project_id = 1
    with db.get_session() as session:
        # Ensure project exists
        project = session.query(Project).first()
        if not project:
            print("Creating test project...")
            project = Project(name="Test Project", site_url="http://test.com")
            session.add(project)
            session.commit()
        project_id = project.id
        print(f"Using Project ID: {project_id}")
        
        # Ensure at least one period exists
        period_count = session.query(Period).filter_by(project_id=project_id).count()
        if period_count == 0:
            print("Creating test period...")
            period = Period(
                project_id=project_id,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30),
                total_reviews_count=50,
                status="draft"
            )
            session.add(period)
            session.commit()
            
    print("DB initialized.")
    return project_id

def main():
    app = QApplication(sys.argv)
    project_id = init_db()
    

    print("Launching PeriodsTab...")
    window = PeriodsTab()
    window.setWindowTitle(f"Debug Periods Tab (Project {project_id})")
    window.resize(800, 600)
    
    # Connect signal to verification function
    def on_period_selected(pid):
        print(f"SUCCESS: Signal period_selected emitted with ID: {pid}")
    
    window.period_selected.connect(on_period_selected)
    
    print(f"Setting project to {project_id}...")
    window.set_project(project_id)
    window.show()
    
    # Simulate user interaction
    from PyQt6.QtCore import QTimer
    def simulate_interaction():
        print("Simulating row selection and open...")
        if window.table.rowCount() > 0:
            window.table.selectRow(0)
            print("Row 0 selected.")
            print("Calling open_period()...")
            window.open_period()
        else:
            print("FAILURE: No rows in table to select!")
            
    QTimer.singleShot(1000, simulate_interaction)
    
    print("PeriodsTab launched. Waiting for simulation...")
    
    QTimer.singleShot(3000, app.quit)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
