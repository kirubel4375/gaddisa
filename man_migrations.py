import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_bot.settings')
django.setup()

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),  # You might need to adjust this to your latest migration
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='location_updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='location_permission_granted',
            field=models.BooleanField(default=False),
        ),
    ]

# Run the migration
from django.core.management import call_command
call_command('makemigrations', 'accounts')
call_command('migrate', 'accounts')

print("Migration completed successfully.")