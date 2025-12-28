import sys
import os

print("DEBUG: Script started.")

print("DEBUG: Importing dotenv...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("DEBUG: dotenv loaded.")
except ImportError:
    print("DEBUG: dotenv not found.")

print("DEBUG: Importing sqlalchemy...")
import sqlalchemy
print("DEBUG: sqlalchemy imported.")

print("DEBUG: Importing PyQt6...")
from PyQt6.QtWidgets import QApplication
print("DEBUG: PyQt6 imported.")

print("DEBUG: Importing core.database...")
from core.database import db
print("DEBUG: core.database imported.")

print("DEBUG: Creating tables...")
try:
    db.create_tables()
    print("DEBUG: Tables created.")
except Exception as e:
    print(f"DEBUG: Failed to create tables: {e}")

print("DEBUG: Importing core.orchestrator...")
try:
    from core.orchestrator import orchestrator
    print("DEBUG: orchestrator imported.")
except Exception as e:
    print(f"DEBUG: orchestrator import failed: {e}")

print("DEBUG: Importing ui.main_window...")
try:
    from ui.main_window import MainWindow
    print("DEBUG: MainWindow imported.")
except Exception as e:
    print(f"DEBUG: MainWindow import failed: {e}")

print("DEBUG: Initializing QApplication...")
app = QApplication(sys.argv)
print("DEBUG: QApplication initialized.")

print("DEBUG: Creating MainWindow instance...")
window = MainWindow()
window.show()
print("DEBUG: Window shown.")

print("DEBUG: Exiting successfully (test only).")
# We don't run app.exec() here to avoid blocking, just want to see if we get here.
