#!/usr/bin/env python
"""
Test script to verify the language sync API endpoints work correctly.
Run this after creating the user profile.
"""

import os
import django
import json
from django.test import Client
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_bot.settings')
django.setup()

from emergency_bot.accounts.models import UserProfile

def test_language_sync_api():
    print("Testing Language Sync API Endpoints")
    print("=" * 40)
    
    telegram_id = "386787633"
    client = Client()
    
    try:
        # Ensure user profile exists
        user_profile, created = UserProfile.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={'language': 'en'}
        )
        print(f"✅ User profile ready: {user_profile.telegram_id} (language: {user_profile.language})")
        
        # Test 1: Check language sync endpoint
        print("\n🔍 Test 1: check_language_sync endpoint")
        response = client.get('/api/frontend/check-language-sync/', {
            'user_id': telegram_id
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   📊 Response: {response.content}")
        
        # Test 2: Update language via API
        print("\n🔄 Test 2: update_language endpoint")
        response = client.post('/api/frontend/update-language/', 
            json.dumps({
                'language': 'am',
                'telegram_id': telegram_id
            }),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   📊 Response: {response.content}")
        
        # Test 3: Check sync after update
        print("\n🔍 Test 3: check_language_sync after update")
        response = client.get('/api/frontend/check-language-sync/', {
            'user_id': telegram_id
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Response: {json.dumps(data, indent=2)}")
            
            if data.get('language') == 'am':
                print("   🎉 Language update successful!")
            else:
                print("   ⚠️  Language not updated correctly")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   📊 Response: {response.content}")
        
        # Refresh user profile from database
        user_profile.refresh_from_db()
        print(f"\n📊 Final user profile state:")
        print(f"   Language: {user_profile.language}")
        print(f"   Changed at: {user_profile.language_changed_at}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_language_sync_api()