#!/usr/bin/env python
"""
Quick script to create user profile for testing language sync.
Run this on your server to create the missing user profile.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_bot.settings')
django.setup()

from emergency_bot.accounts.models import UserProfile

def create_user_profile():
    telegram_id = "386787633"
    
    try:
        # Check if user already exists
        user_profile, created = UserProfile.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={'language': 'en'}
        )
        
        if created:
            print(f"✅ Created new user profile for telegram_id: {telegram_id}")
        else:
            print(f"✅ User profile already exists for telegram_id: {telegram_id}")
            print(f"   Current language: {user_profile.language}")
        
        # Test the sync methods
        print("\n🔄 Testing language sync methods:")
        
        # Test update_language_with_sync
        result = user_profile.update_language_with_sync('am')
        print(f"   update_language_with_sync('am'): {result}")
        
        # Test get_current_language_info
        info = user_profile.get_current_language_info()
        print(f"   get_current_language_info(): {info}")
        
        print(f"\n✅ User profile is ready for language sync!")
        print(f"   User ID: {user_profile.telegram_id}")
        print(f"   Language: {user_profile.language}")
        print(f"   Changed at: {user_profile.language_changed_at}")
        
        return user_profile
        
    except Exception as e:
        print(f"❌ Error creating user profile: {e}")
        return None

if __name__ == "__main__":
    print("Creating user profile for language sync testing...")
    print("=" * 50)
    create_user_profile()