"""
Review Generator - Main Entry Point
"""
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """Initialize and run the application."""
    print("Starting application...")
    app = QApplication(sys.argv)
    
    # Init DB
    print("Initializing database...")
    from core.database import db
    try:
        db.create_tables()
        print("Tables created/verified.")
    except Exception as e:
        print(f"Database error: {e}")

    # Load dark theme stylesheet
    # Load dark theme stylesheet
    try:
        with open("styles/dark_theme.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Warning: dark_theme.qss not found, using default style")
    
    print("Creating main window...")
    try:
        window = MainWindow()
        window.show()
        print("Window shown.")
    except Exception as e:
        print(f"Window creation error: {e}")
        import traceback
        traceback.print_exc()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

