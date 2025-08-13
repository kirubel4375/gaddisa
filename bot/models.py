from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Location(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name

class Service(models.Model):
    SERVICE_TYPES = [
        ('hospital', 'Hospital'),
        ('police', 'Police'),
        ('ambulance', 'Ambulance'),
        ('women_child_affair', 'Women and Child Affair'),
    ]

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='services')
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.get_service_type_display()} - {self.name}"

class UserRequestLog(models.Model):
    chat_id = models.BigIntegerField()
    command = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.chat_id} - {self.command} at {self.timestamp}"

class Role(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Permission(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('role', 'permission')

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_roles')

    class Meta:
        unique_together = ('user', 'role')

class SystemReport(models.Model):
    REPORT_TYPES = [
        ('DAILY', 'Daily Report'),
        ('WEEKLY', 'Weekly Report'),
        ('MONTHLY', 'Monthly Report'),
        ('CUSTOM', 'Custom Report'),
    ]

    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    report_data = models.JSONField()
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.generated_at.strftime('%Y-%m-%d')}"
