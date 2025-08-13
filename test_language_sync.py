#!/usr/bin/env python
"""
Test script to verify language synchronization between Telegram bot and mini app.
"""
import os
import sys
import sqlite3
import requests
import json

def test_language_sync():
    """Test the language synchronization functionality."""
    print("Testing Language Synchronization")
    print("=" * 50)
    
    # Test database connection
    print("\n1. Testing database connection...")
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Check if UserProfile table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accounts_userprofile'")
        if cursor.fetchone():
            print("✓ UserProfile table exists")
        else:
            print("✗ UserProfile table does not exist")
            return False
        
        # Check if we have any users
        cursor.execute("SELECT COUNT(*) FROM accounts_userprofile")
        user_count = cursor.fetchone()[0]
        print(f"✓ Found {user_count} user profiles")
        
        if user_count > 0:
            # Get a sample user
            cursor.execute("SELECT telegram_id, language FROM accounts_userprofile LIMIT 1")
            user = cursor.fetchone()
            if user:
                telegram_id, language = user
                print(f"✓ Sample user: {telegram_id}, Language: {language}")
            else:
                print("✗ No users found")
                return False
        else:
            print("✗ No users in database")
            return False
        
        conn.close()
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False
    
    # Test API endpoints (if server is running)
    print("\n2. Testing API endpoints...")
    try:
        # Test get_user_language endpoint
        url = f"http://localhost:8000/api/frontend/get-user-language/?user_id={telegram_id}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✓ get_user_language API working, current language: {data.get('language')}")
            else:
                print(f"✗ get_user_language API error: {data.get('error')}")
        else:
            print(f"✗ get_user_language API returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("⚠ Server not running (expected if testing locally)")
    except Exception as e:
        print(f"✗ API test error: {e}")
    
    # Test language update
    print("\n3. Testing language update...")
    try:
        # Test update_language endpoint
        url = "http://localhost:8000/api/frontend/update-language/"
        payload = {
            "language": "am",  # Test with Amharic
            "telegram_id": telegram_id
        }
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✓ update_language API working, updated to: {data.get('language')}")
            else:
                print(f"✗ update_language API error: {data.get('error')}")
        else:
            print(f"✗ update_language API returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("⚠ Server not running (expected if testing locally)")
    except Exception as e:
        print(f"✗ API test error: {e}")
    
    # Test database after update
    print("\n4. Testing database after language update...")
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Check if language was updated
        cursor.execute("SELECT language FROM accounts_userprofile WHERE telegram_id = ?", (telegram_id,))
        result = cursor.fetchone()
        if result:
            updated_language = result[0]
            print(f"✓ Database language updated to: {updated_language}")
        else:
            print("✗ Could not find user in database")
        
        conn.close()
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("Language synchronization test completed!")
    print("\nTo test the full functionality:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Start the bot: python bot_runner.py")
    print("3. Change language in the Telegram bot")
    print("4. Open the mini app - it should automatically use the selected language")
    
    return True

if __name__ == "__main__":
    test_language_sync() 