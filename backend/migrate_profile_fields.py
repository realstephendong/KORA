#!/usr/bin/env python3
"""
Migration script to add profile fields to the User model.
Adds budget, interests, and profile_picture columns to the users table.
"""

import sqlite3
import os
from app import create_app, db

def migrate_profile_fields():
    """Add new profile fields to the users table."""
    app = create_app()
    
    with app.app_context():
        try:
            # Add new columns to the users table using text() for raw SQL
            from sqlalchemy import text
            
            with db.engine.connect() as connection:
                connection.execute(text("""
                    ALTER TABLE users ADD COLUMN budget VARCHAR(50);
                """))
                connection.commit()
                print("✓ Added budget column")
                
                connection.execute(text("""
                    ALTER TABLE users ADD COLUMN interests TEXT;
                """))
                connection.commit()
                print("✓ Added interests column")
                
                connection.execute(text("""
                    ALTER TABLE users ADD COLUMN profile_picture VARCHAR(255);
                """))
                connection.commit()
                print("✓ Added profile_picture column")
            
            print("✅ Profile fields migration completed successfully!")
            
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  Profile fields already exist in the database")
            else:
                print(f"❌ Error during migration: {e}")
                raise

if __name__ == "__main__":
    migrate_profile_fields()
