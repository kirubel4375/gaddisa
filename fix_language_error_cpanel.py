#!/usr/bin/env python
"""
Non-interactive script to diagnose and fix the "Error updating language preference" issue on cPanel.
This script automatically checks database connections, schema, and migrations and applies fixes.
"""
import os
import sys
import sqlite3
import datetime
import traceback

def print_header(message):
    """Print a header with the given message."""
    print("\n" + "=" * 80)
    print(f" {message}")
    print("=" * 80)

def check_environment():
    """Check the Python environment and system information."""
    print_header("ENVIRONMENT INFORMATION")
    print(f"Python version: {sys.version}")
    print(f"Script location: {os.path.abspath(__file__)}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Platform: {sys.platform}")

def find_database_files():
    """Find all SQLite database files in the current directory and subdirectories."""
    print_header("SEARCHING FOR DATABASE FILES")
    found_files = []
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.sqlite3') or file.endswith('.db'):
                full_path = os.path.join(root, file)
                size = os.path.getsize(full_path)
                found_files.append((full_path, size))
                print(f"Found database: {full_path}, Size: {size} bytes")
    
    if not found_files:
        print("No SQLite database files found.")
    
    return found_files

def check_database_schema(db_path):
    """Check the schema of the UserProfile table in the database."""
    print_header(f"CHECKING DATABASE SCHEMA: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accounts_userprofile'")
        if not cursor.fetchone():
            print("Table 'accounts_userprofile' does not exist in the database.")
            conn.close()
            return False
        
        # Check the schema
        print("\nUserProfile table schema:")
        cursor.execute("PRAGMA table_info(accounts_userprofile)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"Column: {col[1]}, Type: {col[2]}, Nullable: {col[3]}, Default: {col[4]}")
        
        # Check for latitude and longitude
        has_latitude = any(col[1] == 'latitude' for col in columns)
        has_longitude = any(col[1] == 'longitude' for col in columns)
        
        print(f"\nLatitude column exists: {has_latitude}")
        print(f"Longitude column exists: {has_longitude}")
        
        # Check migration history
        print("\nAccounts migration history:")
        cursor.execute("SELECT id, app, name, applied FROM django_migrations WHERE app='accounts' ORDER BY id")
        migrations = cursor.fetchall()
        for migration in migrations:
            print(f"ID: {migration[0]}, Name: {migration[2]}, Applied: {migration[3]}")
        
        # Check for our specific migration
        cursor.execute("SELECT id FROM django_migrations WHERE app='accounts' AND name='0002_userprofile_latitude_and_more'")
        result = cursor.fetchone()
        has_migration = result is not None
        print(f"\nMigration '0002_userprofile_latitude_and_more' is recorded: {has_migration}")
        
        conn.close()
        return has_latitude and has_longitude and has_migration
    except Exception as e:
        print(f"Error checking database schema: {e}")
        traceback.print_exc()
        return False

def fix_migration_history(db_path):
    """Add the missing migration record to the database."""
    print_header(f"FIXING MIGRATION HISTORY: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the migration is already recorded
        cursor.execute("SELECT id FROM django_migrations WHERE app='accounts' AND name='0002_userprofile_latitude_and_more'")
        if cursor.fetchone():
            print("Migration is already recorded in the database.")
            conn.close()
            return True
        
        # Get the current timestamp
        now = datetime.datetime.now().isoformat()
        
        # Insert the migration record
        print(f"Adding migration record with timestamp: {now}")
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES (?, ?, ?)",
            ('accounts', '0002_userprofile_latitude_and_more', now)
        )
        conn.commit()
        print("Successfully added migration record.")
        
        # Verify the migration was added
        cursor.execute("SELECT id FROM django_migrations WHERE app='accounts' AND name='0002_userprofile_latitude_and_more'")
        if cursor.fetchone():
            print("Verified: Migration record was added successfully.")
            conn.close()
            return True
        else:
            print("Failed to add migration record.")
            conn.close()
            return False
    except Exception as e:
        print(f"Error fixing migration history: {e}")
        traceback.print_exc()
        return False

def add_missing_columns(db_path):
    """Add missing latitude and longitude columns if they don't exist."""
    print_header(f"ADDING MISSING COLUMNS: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute("PRAGMA table_info(accounts_userprofile)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add latitude if missing
        if 'latitude' not in columns:
            print("Adding latitude column...")
            cursor.execute("ALTER TABLE accounts_userprofile ADD COLUMN latitude REAL")
            print("Latitude column added.")
        else:
            print("Latitude column already exists.")
        
        # Add longitude if missing
        if 'longitude' not in columns:
            print("Adding longitude column...")
            cursor.execute("ALTER TABLE accounts_userprofile ADD COLUMN longitude REAL")
            print("Longitude column added.")
        else:
            print("Longitude column already exists.")
        
        # Add location_updated_at if missing
        if 'location_updated_at' not in columns:
            print("Adding location_updated_at column...")
            cursor.execute("ALTER TABLE accounts_userprofile ADD COLUMN location_updated_at DATETIME")
            print("location_updated_at column added.")
        else:
            print("location_updated_at column already exists.")
        
        # Add location_permission_granted if missing
        if 'location_permission_granted' not in columns:
            print("Adding location_permission_granted column...")
            cursor.execute("ALTER TABLE accounts_userprofile ADD COLUMN location_permission_granted BOOLEAN DEFAULT 0")
            print("location_permission_granted column added.")
        else:
            print("location_permission_granted column already exists.")
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding missing columns: {e}")
        traceback.print_exc()
        return False

def check_django_connection():
    """Try to connect to the database using Django settings."""
    print_header("CHECKING DJANGO DATABASE CONNECTION")
    
    try:
        # Set up Django environment
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_bot.settings')
        
        import django
        django.setup()
        
        from django.conf import settings
        from django.db import connection
        
        # Print the database path being used by Django
        db_path = settings.DATABASES['default']['NAME']
        print(f"Django database path: {db_path}")
        
        # Check if the file exists
        if os.path.exists(db_path):
            print(f"Database file exists. Size: {os.path.getsize(db_path)} bytes")
        else:
            print(f"WARNING: Database file does not exist at {db_path}")
        
        # Try a simple query
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM accounts_userprofile")
            count = cursor.fetchone()[0]
            print(f"Number of user profiles in database: {count}")
        
        print("Django database connection successful.")
        return True
    except Exception as e:
        print(f"Error connecting to database via Django: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function to run all checks and fixes."""
    print_header("LANGUAGE PREFERENCE ERROR FIXER (NON-INTERACTIVE)")
    print("This script will automatically diagnose and fix the 'Error updating language preference' issue.")
    
    # Check environment
    check_environment()
    
    # Try Django connection first
    try:
        django_ok = check_django_connection()
    except:
        django_ok = False
    
    # Find database files
    db_files = find_database_files()
    
    # Default database path
    default_db = 'db.sqlite3'
    
    # If we found database files, use the first one as default
    if db_files:
        default_db = db_files[0][0]
    
    # Check if the file exists
    if not os.path.exists(default_db):
        print(f"Error: Database file '{default_db}' not found.")
        return
    
    # Check the database schema
    schema_ok = check_database_schema(default_db)
    
    if schema_ok:
        print("\nGood news! The database schema looks correct:")
        print("- The accounts_userprofile table exists")
        print("- The latitude and longitude columns exist")
        print("- The migration is recorded in the database")
        print("\nThe issue might be with database connections or permissions.")
        print("Try restarting the bot to see if that resolves the issue.")
    else:
        print("\nIssues were found with the database schema. Attempting to fix...")
        
        # Fix migration history
        fix_migration_history(default_db)
        
        # Add missing columns
        add_missing_columns(default_db)
        
        # Check the schema again
        print("\nChecking database schema again after fixes...")
        schema_ok = check_database_schema(default_db)
        
        if schema_ok:
            print("\nSuccess! The database schema has been fixed.")
            print("Try restarting the bot to see if the issue is resolved.")
        else:
            print("\nWarning: There are still issues with the database schema.")
            print("You may need to manually fix the database or rebuild it.")
    
    print_header("COMPLETED")
    print("Next steps:")
    print("1. Restart the Telegram bot")
    print("2. Test changing the language preference")
    print("3. If the issue persists, check the bot logs for more details")

if __name__ == "__main__":
    main() 