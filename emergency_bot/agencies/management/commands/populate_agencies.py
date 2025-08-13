"""
Management command to populate the database with sample agencies.
Usage: python manage.py populate_agencies
"""

from django.core.management.base import BaseCommand
from emergency_bot.agencies.models import Agency


class Command(BaseCommand):
    help = 'Populate the database with sample agencies for testing'

    def handle(self, *args, **options):
        # Sample agencies data
        agencies_data = [
            {
                'name': 'Bole Police Station',
                'type': 'police',
                'description': 'Main police station in Bole area with 24/7 service',
                'region': 'Addis Ababa',
                'zone': 'Bole',
                'phone': '+251114670001',
                'address': 'Bole Road, near Edna Mall, Addis Ababa',
                'latitude': 8.9806,
                'longitude': 38.7578,
                'hours_of_operation': '24/7',
                'services': 'Emergency response, Crime reporting, Traffic issues',
                'verified': True,
                'active': True
            },
            {
                'name': 'Arada Police Station',
                'type': 'police',
                'description': 'Police station serving Arada sub-city',
                'region': 'Addis Ababa',
                'zone': 'Arada',
                'phone': '+251114456789',
                'address': 'Piazza, Churchill Ave, Addis Ababa',
                'latitude': 9.0370,
                'longitude': 38.7467,
                'hours_of_operation': '24/7',
                'services': 'Emergency response, Crime reporting',
                'verified': True,
                'active': True
            },
            {
                'name': 'Black Lion Hospital',
                'type': 'hospital',
                'description': 'Major referral hospital with emergency services',
                'region': 'Addis Ababa',
                'zone': 'Lideta',
                'phone': '+251115517011',
                'address': 'Zambia St, Addis Ababa',
                'latitude': 9.0092,
                'longitude': 38.7441,
                'hours_of_operation': '24/7 Emergency',
                'services': 'Emergency care, General medicine, Surgery',
                'verified': True,
                'active': True
            },
            {
                'name': 'St. Paul Hospital',
                'type': 'hospital',
                'description': 'Millennium Medical College with 24/7 emergency care',
                'region': 'Addis Ababa',
                'zone': 'Gulele',
                'phone': '+251115533666',
                'address': 'Swaziland St, Addis Ababa',
                'latitude': 9.0499,
                'longitude': 38.7662,
                'hours_of_operation': '24/7 Emergency',
                'services': 'Emergency care, Specialized medicine',
                'verified': True,
                'active': True
            },
            {
                'name': 'Ethiopian Women Lawyers Association',
                'type': 'ngo',
                'description': 'Legal aid and support for women and children',
                'region': 'Addis Ababa',
                'zone': 'Kirkos',
                'phone': '+251115505050',
                'address': 'Kirkos, Addis Ababa',
                'latitude': 9.0095,
                'longitude': 38.7612,
                'hours_of_operation': 'Mon-Fri 8:00-17:00',
                'services': 'Legal consultation, Women rights advocacy',
                'verified': True,
                'active': True
            },
            {
                'name': 'Amanuel Mental Specialized Hospital',
                'type': 'hospital',
                'description': 'Specialized mental health hospital',
                'region': 'Addis Ababa',
                'zone': 'Addis Ketema',
                'phone': '+251111223344',
                'address': 'Mexico Square, Addis Ababa',
                'latitude': 9.0349,
                'longitude': 38.7525,
                'hours_of_operation': '24/7 Emergency, Mon-Fri 8:00-17:00 Outpatient',
                'services': 'Mental health services, Psychiatric care',
                'verified': True,
                'active': True
            }
        ]

        created_count = 0
        for agency_data in agencies_data:
            agency, created = Agency.objects.get_or_create(
                name=agency_data['name'],
                defaults=agency_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {agency.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Already exists: {agency.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {created_count} new agencies. '
                f'Total agencies in database: {Agency.objects.count()}'
            )
        )