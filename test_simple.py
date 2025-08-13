"""
Simple test for language synchronization implementation
"""

import os

def test_implementation():
    print("Testing Language Synchronization Implementation")
    print("=" * 50)
    
    # Check if files exist
    files_to_check = [
        "emergency_bot/notifications/consumers.py",
        "emergency_bot/notifications/routing.py",
        "emergency_bot/telegram_bot/language_bridge.py", 
        "emergency_bot/frontend/templates/base.html",
        "emergency_bot/frontend/views.py"
    ]
    
    print("\n1. Checking file structure:")
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"   OK: {file_path}")
        else:
            print(f"   MISSING: {file_path}")
            all_exist = False
    
    if not all_exist:
        return False
    
    # Check WebSocket consumer
    print("\n2. Checking WebSocket consumer:")
    try:
        with open("emergency_bot/notifications/consumers.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = [
            ("LanguageSyncConsumer class", "class LanguageSyncConsumer"),
            ("language_changed handler", "language_changed"),
            ("WebSocket room groups", "language_sync_")
        ]
        
        for name, pattern in checks:
            if pattern in content:
                print(f"   OK: {name}")
            else:
                print(f"   MISSING: {name}")
                return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    # Check routing
    print("\n3. Checking WebSocket routing:")
    try:
        with open("emergency_bot/notifications/routing.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "ws/language/" in content and "LanguageSyncConsumer" in content:
            print("   OK: Language sync route configured")
        else:
            print("   MISSING: Language sync route")
            return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    # Check Telegram integration
    print("\n4. Checking Telegram integration:")
    try:
        with open("emergency_bot/telegram_bot/language_bridge.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = [
            ("notify_language_change function", "async def notify_language_change"),
            ("WebSocket notification", "channel_layer.group_send"),
            ("Function call", "await notify_language_change")
        ]
        
        for name, pattern in checks:
            if pattern in content:
                print(f"   OK: {name}")
            else:
                print(f"   MISSING: {name}")
                return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    # Check frontend integration
    print("\n5. Checking frontend integration:")
    try:
        with open("emergency_bot/frontend/templates/base.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = [
            ("WebSocket connection", "connectLanguageSync"),
            ("WebSocket URL", "ws/language/"),
            ("Message handler", "language_changed"),
            ("Language activation", "activateLanguage")
        ]
        
        for name, pattern in checks:
            if pattern in content:
                print(f"   OK: {name}")
            else:
                print(f"   MISSING: {name}")
                return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    # Check API integration
    print("\n6. Checking API integration:")
    try:
        with open("emergency_bot/frontend/views.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "channel_layer.group_send" in content and "language_sync_" in content:
            print("   OK: WebSocket notification in API")
        else:
            print("   MISSING: WebSocket notification in API")
            return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    return True

def main():
    if test_implementation():
        print("\n" + "="*50)
        print("SUCCESS: All components are properly implemented!")
        print("="*50)
        
        print("\nHow it works:")
        print("1. User changes language in Telegram bot")
        print("2. language_button_callback() updates database")
        print("3. notify_language_change() sends WebSocket message")
        print("4. Mini app receives message and reloads with new language")
        print("5. Works in reverse for mini app -> Telegram changes")
        
        print("\nNext steps:")
        print("1. Start Django server: python manage.py runserver")
        print("2. Start Telegram bot: python manage.py runbot")
        print("3. Test language change in Telegram")
        print("4. Verify mini app updates automatically")
    else:
        print("\nFAILED: Some components are missing or incomplete.")

if __name__ == "__main__":
    main()