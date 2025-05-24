#!/usr/bin/env python3
"""
Database schema update script
Adds missing columns to existing database
"""

import sqlite3
import os

def update_database_schema():
    """Update the database schema to match current models"""
    db_path = "health_tracker.db"
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if medical_specialty column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Current columns in users table: {columns}")
        
        # Add missing columns if they don't exist
        if 'medical_specialty' not in columns:
            print("Adding medical_specialty column...")
            cursor.execute("ALTER TABLE users ADD COLUMN medical_specialty VARCHAR(100) NULL")
        
        if 'is_available_for_booking' not in columns:
            print("Adding is_available_for_booking column...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_available_for_booking BOOLEAN DEFAULT 1")
        
        # Commit changes
        conn.commit()
        print("Database schema updated successfully!")
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(users)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"Updated columns in users table: {updated_columns}")
        
        return True
        
    except Exception as e:
        print(f"Error updating database schema: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    update_database_schema() 