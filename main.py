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

    # Load neon theme stylesheet
    import os
    from PyQt6.QtGui import QFont, QFontDatabase

    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    style_path = os.path.join(base_dir, "styles", "neon_theme.qss")
    try:
        with open(style_path, "r", encoding="utf-8") as f:
            stylesheet = f.read()
            app.setStyleSheet(stylesheet)
            print(f"Stylesheet loaded from: {style_path}")
    except FileNotFoundError:
        print(f"Warning: neon_theme.qss not found at {style_path}, using default style")
    
    # Force default font for desktop app
    default_font = QFont("Segoe UI", 11)
    default_font.setWeight(400)
    app.setFont(default_font)
    print("Default font set to Segoe UI 11px")
    
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

