# Generated migration for language sync field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userprofile_latitude_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='language_changed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]