from django.db import models
from django.utils.text import slugify
import uuid


class Agency(models.Model):
    AGENCY_TYPES = (
        ('police', 'Police Station'),
        ('hospital', 'Hospital/Health Center'),
        ('ngo', 'NGO/Support Organization'),
        ('government', 'Government Office'),
        ('shelter', 'Shelter'),
        ('other', 'Other'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    type = models.CharField(max_length=50, choices=AGENCY_TYPES)
    description = models.TextField(blank=True, null=True)
    
    # Location details
    region = models.CharField(max_length=100)
    zone = models.CharField(max_length=100, blank=True, null=True)
    woreda = models.CharField(max_length=100, blank=True, null=True)
    kebele = models.CharField(max_length=100, blank=True, null=True)
    
    # Contact information
    phone = models.CharField(max_length=20)
    alt_phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    
    # Geographic coordinates
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    # Operational details
    hours_of_operation = models.TextField(blank=True, null=True)
    services = models.TextField(blank=True, null=True)
    
    # Metadata
    verified = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Agency"
        verbose_name_plural = "Agencies"
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['region']),
            models.Index(fields=['zone']),
            models.Index(fields=['active']),
        ]
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()}) - {self.region}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.region}")
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('agency-detail', kwargs={'slug': self.slug})
        
    def calculate_distance(self, latitude, longitude):
        """Calculate distance between agency and given coordinates"""
        import math
        
        # Convert latitude and longitude from degrees to radians
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(latitude), math.radians(longitude)
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Radius of earth in kilometers
        
        # Return distance in kilometers
        return c * r 