from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    telegram_id = models.CharField(max_length=50, unique=True)
    language = models.CharField(
        max_length=10, 
        default="en",
        choices=(
            ("en", "English"),
            ("am", "Amharic"),
            ("om", "Afaan Oromo"),
        )
    )
    last_active = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Location data fields
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_updated_at = models.DateTimeField(null=True, blank=True)
    location_permission_granted = models.BooleanField(default=False)
    
    # Additional fields for GDPR compliance
    data_consent = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)
    
    # Language sync tracking for shared hosting
    language_changed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        indexes = [
            models.Index(fields=["telegram_id"]),
        ]
    
    def __str__(self):
        return f"User {self.telegram_id}"
    
    def update_last_active(self):
        self.last_active = timezone.now()
        self.save(update_fields=["last_active"])
    
    def grant_consent(self):
        self.data_consent = True
        self.consent_date = timezone.now()
        self.save(update_fields=["data_consent", "consent_date"])
    
    def revoke_consent(self):
        self.data_consent = False
        self.save(update_fields=["data_consent"])
    
    def update_location(self, latitude, longitude):
        """Update user location and mark permission as granted"""
        self.latitude = latitude
        self.longitude = longitude
        self.location_updated_at = timezone.now()
        self.location_permission_granted = True
        self.save(update_fields=["latitude", "longitude", "location_updated_at", "location_permission_granted"])
    
    def has_recent_location(self, max_age_hours=24):
        """Check if user has location data that's less than max_age_hours old"""
        if not self.latitude or not self.longitude or not self.location_updated_at:
            return False
        
        age = timezone.now() - self.location_updated_at
        return age.total_seconds() < (max_age_hours * 3600)
    
    def needs_location_permission(self):
        """Check if we need to ask for location permission"""
        return not self.location_permission_granted or not self.has_recent_location()
    
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
        if self.language_changed_at:
            return self.language_changed_at > timestamp
        return False
    
    def get_current_language_info(self):
        """Get current language with timestamp"""
        return {
            'language': self.language or 'en',
            'changed_at': self.language_changed_at.isoformat() if self.language_changed_at else None,
            'timestamp': timezone.now().isoformat()
        } 