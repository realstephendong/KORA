#!/usr/bin/env python3
"""
Database migration script to add name and email columns to the users table.
This script updates the existing SQLite database to include the new user profile fields.
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add name and email columns to the users table if they don't exist."""
    
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'travel_planner.db')
    
    # Ensure the instance directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Users table doesn't exist. Creating it...")
            # Create the users table with all columns
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    auth0_sub VARCHAR(255) NOT NULL UNIQUE,
                    name VARCHAR(255),
                    email VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("Users table created successfully.")
        else:
            print("Users table exists. Checking for new columns...")
            
            # Check if name column exists
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'name' not in columns:
                print("Adding name column...")
                cursor.execute("ALTER TABLE users ADD COLUMN name VARCHAR(255)")
                print("Name column added successfully.")
            else:
                print("Name column already exists.")
            
            if 'email' not in columns:
                print("Adding email column...")
                cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255)")
                print("Email column added successfully.")
            else:
                print("Email column already exists.")
        
        # Create index on auth0_sub if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='ix_users_auth0_sub'")
        if not cursor.fetchone():
            print("Creating index on auth0_sub...")
            cursor.execute("CREATE INDEX ix_users_auth0_sub ON users (auth0_sub)")
            print("Index created successfully.")
        else:
            print("Index on auth0_sub already exists.")
        
        # Commit the changes
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting database migration...")
    migrate_database()
    print("Migration completed!")
