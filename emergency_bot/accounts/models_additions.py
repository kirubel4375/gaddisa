"""
Additional model methods for language synchronization on shared hosting.
Add these methods to your UserProfile model.
"""

from django.utils import timezone
from datetime import timedelta

# Add these methods to your UserProfile model in emergency_bot/accounts/models.py

def update_language_with_sync(self, language_code):
    """Update language and mark for sync notification"""
    if self.language != language_code:
        self.language = language_code
        self.language_changed_at = timezone.now()
        self.save(update_fields=['language', 'language_changed_at'])
        return True
    return False

def get_language_changes_since(self, timestamp):
    """Check if language was changed since given timestamp"""
    if hasattr(self, 'language_changed_at') and self.language_changed_at:
        return self.language_changed_at > timestamp
    return False

def get_current_language_info(self):
    """Get current language with timestamp"""
    return {
        'language': self.language or 'en',
        'changed_at': self.language_changed_at.isoformat() if hasattr(self, 'language_changed_at') and self.language_changed_at else None,
        'timestamp': timezone.now().isoformat()
    }