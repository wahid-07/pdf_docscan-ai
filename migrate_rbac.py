"""
Run this ONCE to add user_id column to existing tables.
Command: python migrate_rbac.py
"""

from database.connection import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        # Check and add user_id to pdf_master
        try:
            conn.execute(text("ALTER TABLE pdf_master ADD COLUMN user_id INTEGER REFERENCES users(id)"))
            print("pdf_master: user_id column added")
        except Exception:
            print("pdf_master: user_id already exists, skipping")

        # Check and add user_id to extracted_data
        try:
            conn.execute(text("ALTER TABLE extracted_data ADD COLUMN user_id INTEGER REFERENCES users(id)"))
            print("extracted_data: user_id column added")
        except Exception:
            print("extracted_data: user_id already exists, skipping")

        # Check and add user_id to rejected_uploads
        try:
            conn.execute(text("ALTER TABLE rejected_uploads ADD COLUMN user_id INTEGER REFERENCES users(id)"))
            print("rejected_uploads: user_id column added")
        except Exception:
            print("rejected_uploads: user_id already exists, skipping")

        conn.commit()
        print("\nMigration complete!")

if __name__ == "__main__":
    migrate()