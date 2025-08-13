#!/usr/bin/env python3
"""
Database Schema Diagnostic Tool
==============================

This script helps diagnose database schema issues by checking:
1. Which database file is being used
2. What tables exist in the database
3. What columns exist in the UserProfile table
4. Migration status
"""

import os
import sys
import sqlite3
import django
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_bot.settings')
django.setup()

from django.conf import settings
from django.db import connection
from django.core.management import execute_from_command_line

def get_database_info():
    """Get information about the database being used"""
    print("="*60)
    print("DATABASE CONFIGURATION ANALYSIS")
    print("="*60)
    
    # Get database settings
    db_settings = settings.DATABASES['default']
    print(f"Database Engine: {db_settings['ENGINE']}")
    print(f"Database Name: {db_settings['NAME']}")
    
    if 'sqlite' in db_settings['ENGINE'].lower():
        db_path = Path(db_settings['NAME'])
        print(f"Database Path: {db_path}")
        print(f"Database Exists: {db_path.exists()}")
        if db_path.exists():
            print(f"Database Size: {db_path.stat().st_size} bytes")
            print(f"Last Modified: {db_path.stat().st_mtime}")
    
    print()

def check_table_schema():
    """Check the actual table schema in the database"""
    print("="*60)
    print("TABLE SCHEMA ANALYSIS")
    print("="*60)
    
    try:
        with connection.cursor() as cursor:
            # Check if accounts_userprofile table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='accounts_userprofile'
            """)
            
            table_exists = cursor.fetchone()
            if table_exists:
                print("✓ accounts_userprofile table EXISTS")
                
                # Get table schema
                cursor.execute("PRAGMA table_info(accounts_userprofile)")
                columns = cursor.fetchall()
                
                print("\nColumns in accounts_userprofile table:")
                print("-" * 40)
                expected_columns = [
                    'id', 'telegram_id', 'language', 'last_active', 'created_at', 
                    'updated_at', 'latitude', 'longitude', 'location_updated_at', 
                    'location_permission_granted', 'data_consent', 'consent_date'
                ]
                
                existing_columns = []
                for column in columns:
                    cid, name, col_type, notnull, default, pk = column
                    existing_columns.append(name)
                    print(f"  {name:<25} {col_type:<15} {'NOT NULL' if notnull else 'NULL'}")
                
                print("\nColumn Check:")
                print("-" * 40)
                for expected in expected_columns:
                    if expected in existing_columns:
                        print(f"  ✓ {expected}")
                    else:
                        print(f"  ✗ {expected} (MISSING)")
                
                missing_columns = set(expected_columns) - set(existing_columns)
                if missing_columns:
                    print(f"\n❌ MISSING COLUMNS: {', '.join(missing_columns)}")
                else:
                    print(f"\n✅ All expected columns are present")
                    
            else:
                print("❌ accounts_userprofile table does NOT exist")
                
    except Exception as e:
        print(f"❌ Error checking table schema: {e}")
    
    print()

def check_migrations():
    """Check migration status"""
    print("="*60)
    print("MIGRATION STATUS")
    print("="*60)
    
    try:
        with connection.cursor() as cursor:
            # Check if django_migrations table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='django_migrations'
            """)
            
            if cursor.fetchone():
                # Get applied migrations for accounts app
                cursor.execute("""
                    SELECT name, applied FROM django_migrations 
                    WHERE app = 'accounts' 
                    ORDER BY applied DESC
                """)
                
                migrations = cursor.fetchall()
                if migrations:
                    print("Applied migrations for 'accounts' app:")
                    print("-" * 40)
                    for name, applied in migrations:
                        print(f"  {name} - {applied}")
                else:
                    print("❌ No migrations found for 'accounts' app")
            else:
                print("❌ django_migrations table does not exist")
                
    except Exception as e:
        print(f"❌ Error checking migrations: {e}")
    
    print()

def check_multiple_databases():
    """Check for multiple database files"""
    print("="*60)
    print("MULTIPLE DATABASE FILES CHECK")
    print("="*60)
    
    # Look for common database file names
    search_paths = [
        Path.cwd(),
        Path.cwd() / "emergency_bot",
        Path.cwd().parent,
    ]
    
    db_files = []
    for search_path in search_paths:
        if search_path.exists():
            for pattern in ["*.db", "*.sqlite", "*.sqlite3", "db.sqlite3"]:
                db_files.extend(search_path.glob(pattern))
    
    if db_files:
        print("Found database files:")
        print("-" * 40)
        for db_file in set(db_files):  # Remove duplicates
            print(f"  {db_file}")
            print(f"    Size: {db_file.stat().st_size} bytes")
            print(f"    Modified: {db_file.stat().st_mtime}")
    else:
        print("No database files found in common locations")
    
    print()

def test_user_profile_query():
    """Test querying UserProfile directly"""
    print("="*60)
    print("USER PROFILE QUERY TEST")
    print("="*60)
    
    try:
        from emergency_bot.accounts.models import UserProfile
        
        # Test basic query
        count = UserProfile.objects.count()
        print(f"✓ UserProfile.objects.count() = {count}")
        
        # Test creating a test user
        test_user, created = UserProfile.objects.get_or_create(
            telegram_id="test_schema_check",
            defaults={'language': 'en'}
        )
        
        if created:
            print("✓ Successfully created test user")
        else:
            print("✓ Test user already exists")
        
        # Test accessing new fields
        try:
            print(f"✓ test_user.latitude = {test_user.latitude}")
            print(f"✓ test_user.longitude = {test_user.longitude}")
            print(f"✓ test_user.data_consent = {test_user.data_consent}")
            print("✅ All new fields are accessible")
        except AttributeError as e:
            print(f"❌ Error accessing new fields: {e}")
        
        # Clean up
        if created:
            test_user.delete()
            print("✓ Cleaned up test user")
            
    except Exception as e:
        print(f"❌ Error testing UserProfile: {e}")
        import traceback
        print(traceback.format_exc())
    
    print()

def main():
    """Run all diagnostic checks"""
    print("DATABASE SCHEMA DIAGNOSTIC TOOL")
    print("Starting analysis...")
    print()
    
    get_database_info()
    check_table_schema()
    check_migrations()
    check_multiple_databases()
    test_user_profile_query()
    
    print("="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60)
    print()
    print("If the schema is missing columns:")
    print("1. Check if you're using the correct database file")
    print("2. Run: python manage.py migrate")
    print("3. If migrations exist but weren't applied, run: python manage.py migrate --fake-initial")
    print("4. If still failing, consider recreating migrations")

if __name__ == "__main__":
    main()