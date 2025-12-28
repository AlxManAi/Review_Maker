"""
Database migration script - recreate database with new schema
"""
import os
from core.database import db

# Remove old database
db_path = "review_generator.db"
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Removed old database: {db_path}")

# Create new tables
db.create_tables()
print("Created new database with updated schema!")
print("\nNew tables created:")
print("- projects")
print("- periods (with total_reviews_count, is_archived)")
print("- product_tasks (with parsed_url, parse_status, parsed_at)")
print("- reviews (with is_approved, is_published, period_id, product_task_id)")
print("- templates")
print("- api_keys")
print("- review_examples (NEW)")
