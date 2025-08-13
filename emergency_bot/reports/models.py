from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid
from cryptography.fernet import Fernet
import base64

# For encryption of sensitive data
def get_encryption_key():
    from django.conf import settings
    key = getattr(settings, 'ENCRYPTION_KEY', None)
    if key:
        try:
            # Make sure the key is valid
            decoded_key = base64.urlsafe_b64decode(key)
            if len(decoded_key) == 32:
                return decoded_key
            else:
                # Log warning but don't crash
                import logging
                logging.warning("ENCRYPTION_KEY is not 32 bytes long. Encryption disabled.")
        except Exception as e:
            # Log error but don't crash
            import logging
            logging.error(f"Invalid ENCRYPTION_KEY: {e}. Encryption disabled.")
    return None

def encrypt_text(text):
    key = get_encryption_key()
    if key and text:
        try:
            f = Fernet(key)
            return f.encrypt(text.encode()).decode()
        except Exception as e:
            # Log error but don't crash
            import logging
            logging.error(f"Encryption error: {e}. Storing text unencrypted.")
    return text

def decrypt_text(encrypted_text):
    key = get_encryption_key()
    if key and encrypted_text:
        try:
            f = Fernet(key)
            return f.decrypt(encrypted_text.encode()).decode()
        except Exception as e:
            # Log error but don't crash
            import logging
            logging.error(f"Decryption error: {e}. Returning original text.")
    return encrypted_text


class IncidentReport(models.Model):
    INCIDENT_TYPES = (
        ('rape', 'Rape'),
        ('assault', 'Assault'),
        ('domestic_violence', 'Domestic Violence'),
        ('harassment', 'Harassment'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('processing', 'Processing'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.UserProfile', on_delete=models.CASCADE, related_name='reports')
    type = models.CharField(max_length=50, choices=INCIDENT_TYPES)
    description = models.TextField(null=True, blank=True)
    description_encrypted = models.TextField(null=True, blank=True)
    voice_note_url = models.URLField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    submitted_at = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Audit fields
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_info = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        verbose_name = "Incident Report"
        verbose_name_plural = "Incident Reports"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['type']),
            models.Index(fields=['status']),
            models.Index(fields=['submitted_at']),
        ]
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.submitted_at}"
    
    def save(self, *args, **kwargs):
        # Encrypt description if provided
        if self.description and not self.description_encrypted:
            try:
                encrypted = encrypt_text(self.description)
                # Only set encrypted text if encryption actually worked
                if encrypted != self.description:
                    self.description_encrypted = encrypted
                    # For GDPR compliance, we can optionally clear the plaintext
                    # self.description = None
            except Exception as e:
                # Log error but continue saving
                import logging
                logging.error(f"Error encrypting description: {e}")
        
        super().save(*args, **kwargs)
    
    def get_decrypted_description(self):
        if self.description_encrypted:
            return decrypt_text(self.description_encrypted)
        return self.description
        
    @property
    def time_since_submission(self):
        return timezone.now() - self.submitted_at 