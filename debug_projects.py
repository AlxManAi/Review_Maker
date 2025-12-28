import sys
from PyQt6.QtWidgets import QApplication
from core.database import db
from core.models import Project
from ui.tabs.projects_tab import ProjectsTab

def init_db():
    print("Initializing DB...")
    db.create_tables()
    with db.get_session() as session:
        if session.query(Project).count() == 0:
            print("Creating test project...")
            session.add(Project(name="Test Project", site_url="http://test.com"))
            session.commit()
    print("DB initialized.")

def main():
    app = QApplication(sys.argv)
    init_db()
    
    print("Launching ProjectsTab...")
    window = ProjectsTab()
    window.setWindowTitle("Debug Projects Tab")
    window.resize(800, 600)
    window.show()
    
    print("ProjectsTab launched. Close window to finish.")
    # In a real automated environment we might not want to block, 
    # but here we want to verify it doesn't crash on start.
    # We will use a timer to auto-close for the tool run.
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(2000, app.quit)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
