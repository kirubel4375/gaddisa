"""
Management command to populate the database with sample agencies.
Usage: python manage.py populate_agencies
"""

from django.core.management.base import BaseCommand
from emergency_bot.agencies.models import Agency


class Command(BaseCommand):
    help = 'Populate the database with sample agencies for testing'

    def handle(self, *args, **options):
        # Comprehensive agencies data for demo
        agencies_data = [
            # ========== POLICE STATIONS ==========
            # Addis Ababa Police
            {
                'name': 'Bole Police Station',
                'type': 'police',
                'description': 'Main police station in Bole area with 24/7 service',
                'region': 'Addis Ababa',
                'zone': 'Bole',
                'woreda': '01',
                'kebele': '01',
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
                'woreda': '01',
                'kebele': '02',
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
                'name': 'Kirkos Police Station',
                'type': 'police',
                'description': 'Police station in Kirkos sub-city',
                'region': 'Addis Ababa',
                'zone': 'Kirkos',
                'woreda': '02',
                'kebele': '01',
                'phone': '+251114887766',
                'address': 'Arat Kilo, Addis Ababa',
                'latitude': 9.0349,
                'longitude': 38.7612,
                'hours_of_operation': '24/7',
                'services': 'Emergency response, Crime reporting, Traffic control',
                'verified': True,
                'active': True
            },
            # Oromia Police
            {
                'name': 'Adama Police Station',
                'type': 'police',
                'description': 'Main police station in Adama city',
                'region': 'Oromia',
                'zone': 'East Shewa',
                'woreda': 'Adama',
                'kebele': '01',
                'phone': '+251221112233',
                'address': 'Main Street, Adama, Oromia',
                'latitude': 8.5407,
                'longitude': 39.2677,
                'hours_of_operation': '24/7',
                'services': 'Emergency response, Crime reporting, Highway patrol',
                'verified': True,
                'active': True
            },
            {
                'name': 'Jimma Police Station',
                'type': 'police',
                'description': 'Police station serving Jimma town',
                'region': 'Oromia',
                'zone': 'Jimma',
                'woreda': 'Jimma',
                'kebele': '01',
                'phone': '+251471123456',
                'address': 'Commercial Bank Street, Jimma',
                'latitude': 7.6739,
                'longitude': 36.8341,
                'hours_of_operation': '24/7',
                'services': 'Emergency response, Crime reporting',
                'verified': True,
                'active': True
            },

            # ========== HOSPITALS ==========
            # Addis Ababa Hospitals
            {
                'name': 'Black Lion Hospital',
                'type': 'hospital',
                'description': 'Major referral hospital with emergency services',
                'region': 'Addis Ababa',
                'zone': 'Lideta',
                'woreda': '04',
                'kebele': '05',
                'phone': '+251115517011',
                'address': 'Zambia St, Addis Ababa',
                'latitude': 9.0092,
                'longitude': 38.7441,
                'hours_of_operation': '24/7 Emergency',
                'services': 'Emergency care, General medicine, Surgery, ICU',
                'verified': True,
                'active': True
            },
            {
                'name': 'St. Paul Hospital',
                'type': 'hospital',
                'description': 'Millennium Medical College with 24/7 emergency care',
                'region': 'Addis Ababa',
                'zone': 'Gulele',
                'woreda': '01',
                'kebele': '02',
                'phone': '+251115533666',
                'address': 'Swaziland St, Addis Ababa',
                'latitude': 9.0499,
                'longitude': 38.7662,
                'hours_of_operation': '24/7 Emergency',
                'services': 'Emergency care, Specialized medicine, Cardiac care',
                'verified': True,
                'active': True
            },
            {
                'name': 'Amanuel Mental Specialized Hospital',
                'type': 'hospital',
                'description': 'Specialized mental health hospital',
                'region': 'Addis Ababa',
                'zone': 'Addis Ketema',
                'woreda': '01',
                'kebele': '03',
                'phone': '+251111223344',
                'address': 'Mexico Square, Addis Ababa',
                'latitude': 9.0349,
                'longitude': 38.7525,
                'hours_of_operation': '24/7 Emergency, Mon-Fri 8:00-17:00 Outpatient',
                'services': 'Mental health services, Psychiatric care, Counseling',
                'verified': True,
                'active': True
            },
            {
                'name': 'Yekatit 12 Hospital',
                'type': 'hospital',
                'description': 'General hospital with emergency and maternity services',
                'region': 'Addis Ababa',
                'zone': 'Arada',
                'woreda': '02',
                'kebele': '01',
                'phone': '+251115551234',
                'address': 'Yekatit 12 Square, Addis Ababa',
                'latitude': 9.0301,
                'longitude': 38.7379,
                'hours_of_operation': '24/7 Emergency',
                'services': 'Emergency care, Maternity, Pediatrics, Surgery',
                'verified': True,
                'active': True
            },
            # Regional Hospitals
            {
                'name': 'Adama Hospital Medical College',
                'type': 'hospital',
                'description': 'Regional referral hospital in Adama',
                'region': 'Oromia',
                'zone': 'East Shewa',
                'woreda': 'Adama',
                'kebele': '02',
                'phone': '+251221556677',
                'address': 'Hospital Road, Adama',
                'latitude': 8.5389,
                'longitude': 39.2705,
                'hours_of_operation': '24/7 Emergency',
                'services': 'Emergency care, Surgery, Internal medicine',
                'verified': True,
                'active': True
            },
            {
                'name': 'Jimma University Medical Center',
                'type': 'hospital',
                'description': 'University teaching hospital',
                'region': 'Oromia',
                'zone': 'Jimma',
                'woreda': 'Jimma',
                'kebele': '02',
                'phone': '+251471789012',
                'address': 'University Campus, Jimma',
                'latitude': 7.6832,
                'longitude': 36.8341,
                'hours_of_operation': '24/7 Emergency',
                'services': 'Emergency care, Teaching hospital, Research',
                'verified': True,
                'active': True
            },

            # ========== NGOs & SUPPORT ORGANIZATIONS ==========
            {
                'name': 'Ethiopian Women Lawyers Association',
                'type': 'ngo',
                'description': 'Legal aid and support for women and children',
                'region': 'Addis Ababa',
                'zone': 'Kirkos',
                'woreda': '01',
                'kebele': '04',
                'phone': '+251115505050',
                'address': 'Kirkos, Addis Ababa',
                'latitude': 9.0095,
                'longitude': 38.7612,
                'hours_of_operation': 'Mon-Fri 8:00-17:00',
                'services': 'Legal consultation, Women rights advocacy, Court representation',
                'verified': True,
                'active': True
            },
            {
                'name': 'Association for Women in Development',
                'type': 'ngo',
                'description': 'Empowerment and support for women',
                'region': 'Addis Ababa',
                'zone': 'Bole',
                'woreda': '02',
                'kebele': '01',
                'phone': '+251116677889',
                'address': 'Bole Sub-city, Addis Ababa',
                'latitude': 8.9876,
                'longitude': 38.7643,
                'hours_of_operation': 'Mon-Fri 8:30-17:30',
                'services': 'Skills training, Microfinance, Legal support',
                'verified': True,
                'active': True
            },
            {
                'name': 'Children and Family Services',
                'type': 'ngo',
                'description': 'Child protection and family support services',
                'region': 'Addis Ababa',
                'zone': 'Gulele',
                'woreda': '02',
                'kebele': '03',
                'phone': '+251117788990',
                'address': 'Gulele Sub-city, Addis Ababa',
                'latitude': 9.0567,
                'longitude': 38.7589,
                'hours_of_operation': 'Mon-Sat 8:00-18:00',
                'services': 'Child protection, Family counseling, Foster care',
                'verified': True,
                'active': True
            },
            {
                'name': 'Oromia Women and Children Support Center',
                'type': 'ngo',
                'description': 'Regional support center for women and children',
                'region': 'Oromia',
                'zone': 'East Shewa',
                'woreda': 'Adama',
                'kebele': '03',
                'phone': '+251221334455',
                'address': 'Central Adama, Oromia',
                'latitude': 8.5423,
                'longitude': 39.2698,
                'hours_of_operation': 'Mon-Fri 8:00-17:00',
                'services': 'Counseling, Legal aid, Shelter services',
                'verified': True,
                'active': True
            },

            # ========== GOVERNMENT OFFICES ==========
            {
                'name': 'Women and Children Affairs Bureau - Addis Ababa',
                'type': 'government',
                'description': 'Government office for women and children protection',
                'region': 'Addis Ababa',
                'zone': 'Arada',
                'woreda': '01',
                'kebele': '01',
                'phone': '+251115252525',
                'address': 'Arada Sub-city Administration, Addis Ababa',
                'latitude': 9.0336,
                'longitude': 38.7504,
                'hours_of_operation': 'Mon-Fri 8:30-17:30',
                'services': 'Policy implementation, Child protection, Legal support',
                'verified': True,
                'active': True
            },
            {
                'name': 'Ministry of Women and Social Affairs',
                'type': 'government',
                'description': 'Federal ministry office',
                'region': 'Addis Ababa',
                'zone': 'Kirkos',
                'woreda': '03',
                'kebele': '02',
                'phone': '+251115161718',
                'address': 'Ministry Building, Kirkos, Addis Ababa',
                'latitude': 9.0278,
                'longitude': 38.7543,
                'hours_of_operation': 'Mon-Fri 8:30-17:30',
                'services': 'Policy development, National programs, Coordination',
                'verified': True,
                'active': True
            },
            {
                'name': 'Oromia Women and Children Affairs Bureau',
                'type': 'government',
                'description': 'Regional government office',
                'region': 'Oromia',
                'zone': 'East Shewa',
                'woreda': 'Adama',
                'kebele': '01',
                'phone': '+251221445566',
                'address': 'Regional Government Building, Adama',
                'latitude': 8.5445,
                'longitude': 39.2721,
                'hours_of_operation': 'Mon-Fri 8:30-17:30',
                'services': 'Regional coordination, Policy implementation',
                'verified': True,
                'active': True
            },

            # ========== SHELTERS ==========
            {
                'name': 'Safe Haven Women Shelter',
                'type': 'shelter',
                'description': 'Emergency shelter for women and children',
                'region': 'Addis Ababa',
                'zone': 'Lideta',
                'woreda': '02',
                'kebele': '04',
                'phone': '+251118899001',
                'address': 'Confidential Location, Lideta, Addis Ababa',
                'latitude': 9.0156,
                'longitude': 38.7389,
                'hours_of_operation': '24/7',
                'services': 'Emergency shelter, Counseling, Legal support, Job training',
                'verified': True,
                'active': True
            },
            {
                'name': 'Hope Center for Women',
                'type': 'shelter',
                'description': 'Transitional housing and support services',
                'region': 'Addis Ababa',
                'zone': 'Kolfe Keranio',
                'woreda': '01',
                'kebele': '02',
                'phone': '+251119900112',
                'address': 'Kolfe Keranio, Addis Ababa',
                'latitude': 8.9789,
                'longitude': 38.7123,
                'hours_of_operation': '24/7',
                'services': 'Transitional housing, Skills training, Childcare',
                'verified': True,
                'active': True
            },
            {
                'name': 'Regional Family Support Center',
                'type': 'shelter',
                'description': 'Regional shelter and support services',
                'region': 'Oromia',
                'zone': 'Jimma',
                'woreda': 'Jimma',
                'kebele': '03',
                'phone': '+251471556677',
                'address': 'Confidential Location, Jimma',
                'latitude': 7.6756,
                'longitude': 36.8378,
                'hours_of_operation': '24/7',
                'services': 'Emergency shelter, Counseling, Reintegration support',
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