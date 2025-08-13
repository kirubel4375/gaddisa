#!/usr/bin/env python
"""
Script to test if the services data is correctly accessible.
"""

import os
import sys
import sqlite3

# Path to the SQLite database
DB_PATH = 'db.sqlite3'

def test_database_connection():
    """Test if the database connection works"""
    print("Testing database connection...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()
        print(f"✓ Connected to SQLite version: {version[0]}")
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"❌ Error connecting to database: {e}")
        return False

def count_services_by_type():
    """Count services by type"""
    print("\nCounting services by type...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT service_type, COUNT(*) FROM bot_service GROUP BY service_type")
        results = cursor.fetchall()
        
        if not results:
            print("❌ No services found in the database!")
        else:
            print("✓ Services by type:")
            for service_type, count in results:
                print(f"   • {service_type}: {count}")
        
        conn.close()
        return results
    except sqlite3.Error as e:
        print(f"❌ Error counting services: {e}")
        return []

def list_all_services():
    """List all services in the database"""
    print("\nListing all services...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.name, s.service_type, s.phone_number, l.latitude, l.longitude 
            FROM bot_service s
            JOIN bot_location l ON s.location_id = l.id
        """)
        services = cursor.fetchall()
        
        if not services:
            print("❌ No services found in the database!")
        else:
            print(f"✓ Found {len(services)} services:")
            for i, (name, service_type, phone, lat, lng) in enumerate(services, 1):
                print(f"   {i}. {name} ({service_type})")
                print(f"      Phone: {phone}")
                print(f"      Location: {lat:.6f}, {lng:.6f}")
                print(f"      Maps: https://maps.google.com/?q={lat},{lng}")
                print()
        
        conn.close()
        return services
    except sqlite3.Error as e:
        print(f"❌ Error listing services: {e}")
        return []

def main():
    """Main function"""
    print("🔍 Testing Services Database")
    print("=" * 50)
    
    # Check if database file exists
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file {DB_PATH} not found!")
        return 1
    
    # Test database connection
    if not test_database_connection():
        return 1
    
    # Count services by type
    service_counts = count_services_by_type()
    if not service_counts:
        return 1
    
    # List all services
    services = list_all_services()
    if not services:
        return 1
    
    print("=" * 50)
    print("✅ Database tests completed successfully!")
    print(f"📊 Summary: {len(services)} services available in {len(service_counts)} categories")
    
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 