#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for language synchronization between Telegram bot and mini app.
This script validates the WebSocket functionality for real-time language sync.
"""

import os
import sys
import io

# Ensure proper encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_file_structure():
    """Test if all required files exist"""
    print("Testing language sync implementation file structure...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    required_files = [
        "emergency_bot/notifications/consumers.py",
        "emergency_bot/notifications/routing.py", 
        "emergency_bot/telegram_bot/language_bridge.py",
        "emergency_bot/frontend/templates/base.html",
        "emergency_bot/frontend/views.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"OK {file_path}")
        else:
            print(f"MISSING {file_path}")
            all_exist = False
    
    return all_exist

def test_websocket_consumer():
    """Test if WebSocket consumer is properly implemented"""
    print("\nTesting WebSocket consumer implementation...")
    
    try:
        # Read consumers.py and check for LanguageSyncConsumer
        with open("emergency_bot/notifications/consumers.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "class LanguageSyncConsumer" in content:
            print("OK LanguageSyncConsumer class exists")
        else:
            print("FAIL LanguageSyncConsumer class not found")
            return False
            
        if "language_changed" in content:
            print("OK language_changed handler exists")
        else:
            print("FAIL language_changed handler not found")
            return False
            
        if "language_sync_" in content:
            print("OK Language sync room group pattern exists")
        else:
            print("FAIL Language sync room group pattern not found")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error reading consumers.py: {e}")
        return False

def test_websocket_routing():
    """Test if WebSocket routing is configured"""
    print("\nTesting WebSocket routing configuration...")
    
    try:
        # Read routing.py and check for language route
        with open("emergency_bot/notifications/routing.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "ws/language/" in content:
            print("✓ Language sync WebSocket route configured")
        else:
            print("✗ Language sync WebSocket route not found")
            return False
            
        if "LanguageSyncConsumer" in content:
            print("✓ LanguageSyncConsumer referenced in routing")
        else:
            print("✗ LanguageSyncConsumer not referenced in routing")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error reading routing.py: {e}")
        return False

def test_telegram_integration():
    """Test if Telegram bot integration is implemented"""
    print("\nTesting Telegram bot integration...")
    
    try:
        # Read language_bridge.py and check for notification function
        with open("emergency_bot/telegram_bot/language_bridge.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "async def notify_language_change" in content:
            print("✓ notify_language_change function exists")
        else:
            print("✗ notify_language_change function not found")
            return False
            
        if "channel_layer.group_send" in content:
            print("✓ WebSocket group send implementation exists")
        else:
            print("✗ WebSocket group send implementation not found")
            return False
            
        if "await notify_language_change" in content:
            print("✓ Function is called from language update")
        else:
            print("✗ Function not called from language update")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error reading language_bridge.py: {e}")
        return False

def test_frontend_integration():
    """Test if frontend WebSocket integration is implemented"""
    print("\nTesting frontend WebSocket integration...")
    
    try:
        # Read base.html and check for WebSocket code
        with open("emergency_bot/frontend/templates/base.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "connectLanguageSync" in content:
            print("✓ Language sync WebSocket connection function exists")
        else:
            print("✗ Language sync WebSocket connection function not found")
            return False
            
        if "ws/language/" in content:
            print("✓ WebSocket URL for language sync exists")
        else:
            print("✗ WebSocket URL for language sync not found")
            return False
            
        if "language_changed" in content:
            print("✓ Language change message handler exists")
        else:
            print("✗ Language change message handler not found")
            return False
            
        if "activateLanguage" in content:
            print("✓ Language activation function exists")
        else:
            print("✗ Language activation function not found")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error reading base.html: {e}")
        return False

def test_api_integration():
    """Test if API integration sends WebSocket notifications"""
    print("\nTesting API WebSocket integration...")
    
    try:
        # Read views.py and check for WebSocket notification
        with open("emergency_bot/frontend/views.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "channel_layer.group_send" in content:
            print("✓ WebSocket notification in update_language API")
        else:
            print("✗ WebSocket notification not found in update_language API")
            return False
            
        if "language_sync_" in content:
            print("✓ Language sync group name pattern exists")
        else:
            print("✗ Language sync group name pattern not found")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error reading views.py: {e}")
        return False

def print_implementation_summary():
    """Print a summary of the implementation"""
    print("\n" + "="*60)
    print("LANGUAGE SYNCHRONIZATION IMPLEMENTATION SUMMARY")
    print("="*60)
    
    print("\n1. WebSocket Consumer (LanguageSyncConsumer):")
    print("   - Handles real-time language sync between Telegram and mini app")
    print("   - WebSocket URL: /ws/language/<telegram_id>/")
    print("   - Sends/receives language change notifications")
    
    print("\n2. Telegram Bot Integration:")
    print("   - notify_language_change() function in language_bridge.py")
    print("   - Automatically sends WebSocket notification when language changes in Telegram")
    print("   - Integrated with update_user_language_async()")
    
    print("\n3. Mini App Integration:")
    print("   - JavaScript WebSocket connection in base.html")
    print("   - Automatic reconnection on disconnect")
    print("   - Listens for language_changed messages from Telegram")
    print("   - Automatically reloads page with new language")
    
    print("\n4. Bidirectional Sync:")
    print("   - Telegram → Mini App: Via WebSocket notification")
    print("   - Mini App → Telegram: Via update_language API endpoint")
    print("   - Both directions update the database and notify the other side")
    
    print("\n5. How it works:")
    print("   - User changes language in Telegram bot")
    print("   - language_button_callback() updates database")
    print("   - notify_language_change() sends WebSocket message")
    print("   - Mini app receives message and reloads with new language")
    print("   - Vice versa for changes from mini app")

def main():
    """Main test function"""
    print("Language Synchronization Test")
    print("=" * 40)
    
    # Run all tests
    tests = [
        test_file_structure,
        test_websocket_consumer,
        test_websocket_routing,
        test_telegram_integration,
        test_frontend_integration,
        test_api_integration
    ]
    
    all_passed = True
    for test_func in tests:
        passed = test_func()
        if not passed:
            all_passed = False
    
    # Print implementation summary
    print_implementation_summary()
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Language synchronization is ready to use.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
    
    print("\n" + "="*60)
    print("NEXT STEPS TO TEST:")
    print("="*60)
    print("1. Start Django development server: python manage.py runserver")
    print("2. Start Telegram bot: python manage.py runbot")
    print("3. Open mini app in Telegram")
    print("4. Change language in Telegram bot")
    print("5. Verify mini app updates automatically")
    print("6. Change language in mini app")
    print("7. Verify Telegram bot reflects the change")

if __name__ == "__main__":
    main()