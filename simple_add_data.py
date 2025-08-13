#!/usr/bin/env python
"""
Simple script to add sample data to the database using raw SQL.
This avoids dependencies on Django REST framework.
"""

import os
import sys
import sqlite3
import json

# Path to the SQLite database
DB_PATH = 'db.sqlite3'

def clear_existing_data(conn):
    """Clear existing data from the tables"""
    print("Clearing existing data...")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bot_service")
    cursor.execute("DELETE FROM bot_location")
    conn.commit()
    print("✓ Data cleared")

def add_sample_data(conn):
    """Add sample data for locations and services"""
    print("Adding sample data...")
    
    # Create locations and services for Addis Ababa
    services_data = [
        # Police Stations
        {
            'location_name': 'Bole Police Station',
            'latitude': 8.9936,
            'longitude': 38.7870,
            'service_type': 'police',
            'name': 'Bole Police Station',
            'description': 'Main police station in Bole area with 24/7 service',
            'phone_number': '+251114670001',
        },
        {
            'location_name': 'Arada Police Station',
            'latitude': 9.0370,
            'longitude': 38.7510,
            'service_type': 'police',
            'name': 'Arada Police Station',
            'description': 'Police station serving Arada sub-city',
            'phone_number': '+251114456789',
        },
        {
            'location_name': 'Kirkos Police Station',
            'latitude': 9.0125,
            'longitude': 38.7425,
            'service_type': 'police',
            'name': 'Kirkos Police Station',
            'description': 'Police station in Kirkos sub-city',
            'phone_number': '+251114567890',
        },
        
        # Hospitals
        {
            'location_name': 'Black Lion Hospital',
            'latitude': 9.0107,
            'longitude': 38.7476,
            'service_type': 'hospital',
            'name': 'Black Lion Hospital',
            'description': 'Major referral hospital with emergency services',
            'phone_number': '+251115517011',
        },
        {
            'location_name': 'St. Paul\'s Hospital',
            'latitude': 9.0036,
            'longitude': 38.7468,
            'service_type': 'hospital',
            'name': 'St. Paul\'s Hospital',
            'description': 'Millennium Medical College with 24/7 emergency care',
            'phone_number': '+251115533666',
        },
        {
            'location_name': 'Yekatit 12 Hospital',
            'latitude': 9.0382,
            'longitude': 38.7611,
            'service_type': 'hospital',
            'name': 'Yekatit 12 Hospital',
            'description': 'Government hospital with emergency department',
            'phone_number': '+251111223344',
        },
        
        # Ambulance Services
        {
            'location_name': 'Red Cross Ambulance',
            'latitude': 9.0249,
            'longitude': 38.7622,
            'service_type': 'ambulance',
            'name': 'Red Cross Ambulance Service',
            'description': 'Emergency ambulance service by Red Cross',
            'phone_number': '+251907',
        },
        {
            'location_name': 'Tebita Ambulance',
            'latitude': 9.0180,
            'longitude': 38.7890,
            'service_type': 'ambulance',
            'name': 'Tebita Ambulance Service',
            'description': 'Private ambulance service with trained paramedics',
            'phone_number': '+251911505050',
        },
        
        # Women and Child Affairs
        {
            'location_name': 'Ethiopian Women Lawyers Association',
            'latitude': 9.0145,
            'longitude': 38.7632,
            'service_type': 'women_child_affair',
            'name': 'Ethiopian Women Lawyers Association',
            'description': 'Legal aid and support for women and children',
            'phone_number': '+251115505050',
        },
        {
            'location_name': 'Women and Children Affairs Bureau',
            'latitude': 9.0336,
            'longitude': 38.7504,
            'service_type': 'women_child_affair',
            'name': 'Women and Children Affairs Bureau',
            'description': 'Government office for women and children protection',
            'phone_number': '+251115252525',
        },
        {
            'location_name': 'Safe Haven Women Shelter',
            'latitude': 9.0220,
            'longitude': 38.7705,
            'service_type': 'women_child_affair',
            'name': 'Safe Haven Women Shelter',
            'description': 'Emergency shelter for women and children',
            'phone_number': '+251115606060',
        },
    ]
    
    cursor = conn.cursor()
    created_services = 0
    
    for data in services_data:
        # Insert location
        cursor.execute(
            "INSERT INTO bot_location (name, latitude, longitude) VALUES (?, ?, ?)",
            (data['location_name'], data['latitude'], data['longitude'])
        )
        location_id = cursor.lastrowid
        
        # Insert service
        cursor.execute(
            "INSERT INTO bot_service (location_id, service_type, name, description, phone_number) VALUES (?, ?, ?, ?, ?)",
            (location_id, data['service_type'], data['name'], data['description'], data['phone_number'])
        )
        created_services += 1
    
    conn.commit()
    print(f"✓ Added {created_services} services")
    return created_services

def count_records(conn):
    """Count records in tables"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bot_location")
    location_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM bot_service")
    service_count = cursor.fetchone()[0]
    
    return location_count, service_count

def get_sample_services(conn):
    """Get sample services from the database"""
    cursor = conn.cursor()
    cursor.execute("SELECT name, service_type, phone_number FROM bot_service LIMIT 3")
    return cursor.fetchall()

def main():
    """Main function to run the script"""
    print("🚀 Starting database population...")
    print("=" * 50)
    
    # Connect to the database
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file {DB_PATH} not found!")
        return 1
    
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Clear existing data
        clear_existing_data(conn)
        
        # Add sample data
        services = add_sample_data(conn)
        
        # Count records
        location_count, service_count = count_records(conn)
        
        print("=" * 50)
        print("✅ Database population completed successfully!")
        print(f"📊 Summary:")
        print(f"   • {location_count} Locations")
        print(f"   • {service_count} Services")
        print()
        print("🎯 The database is now ready for testing!")
        
        # Print some sample data
        print("\nSample Services:")
        for service in get_sample_services(conn):
            print(f" - {service[0]} ({service[1]}): {service[2]}")
        
        conn.close()
        return 0
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 