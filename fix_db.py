import sqlite3
import os

DB_NAMES = ["review_generator.db", "Review_Maker/review_generator.db"]

def fix_db():
    target_db = None
    for db in DB_NAMES:
        if os.path.exists(db):
            target_db = db
            break
            
    if not target_db:
        print("Database file not found!")
        return

    print(f"Fixing database: {target_db}")
    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE reviews ADD COLUMN pros TEXT")
        print("Added column 'pros'")
    except sqlite3.OperationalError as e:
        print(f"Skipped 'pros': {e}")
        
    try:
        cursor.execute("ALTER TABLE reviews ADD COLUMN cons TEXT")
        print("Added column 'cons'")
    except sqlite3.OperationalError as e:
        print(f"Skipped 'cons': {e}")
        
    conn.commit()
    conn.close()
    print("Database fixed successfully.")

if __name__ == "__main__":
    fix_db()
