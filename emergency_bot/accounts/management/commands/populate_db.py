"""
Django management command to populate the database with sample data.

Usage:
    python manage.py populate_db
    python manage.py populate_db --clear  # Clear existing data first
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import random

from emergency_bot.accounts.models import UserProfile
from emergency_bot.agencies.models import Agency
from emergency_bot.reports.models import IncidentReport
from emergency_bot.notifications.models import Notification, NotificationChannel


class Command(BaseCommand):
    help = 'Populate the database with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()

        with transaction.atomic():
            self.stdout.write('Creating sample data...')
            
            # Create users first (they're referenced by other models)
            users = self.create_users()
            self.stdout.write(self.style.SUCCESS(f'Created {len(users)} user profiles'))
            
            # Create agencies
            agencies = self.create_agencies()
            self.stdout.write(self.style.SUCCESS(f'Created {len(agencies)} agencies'))
            
            # Create reports
            reports = self.create_reports(users)
            self.stdout.write(self.style.SUCCESS(f'Created {len(reports)} incident reports'))
            
            # Create notifications
            notifications = self.create_notifications(users, reports, agencies)
            self.stdout.write(self.style.SUCCESS(f'Created {len(notifications)} notifications'))
            
            # Create notification channels
            channels = self.create_notification_channels(users)
            self.stdout.write(self.style.SUCCESS(f'Created {len(channels)} notification channels'))

        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )

    def clear_data(self):
        """Clear existing data from all models"""
        Notification.objects.all().delete()
        NotificationChannel.objects.all().delete()
        IncidentReport.objects.all().delete()
        Agency.objects.all().delete()
        UserProfile.objects.all().delete()

    def create_users(self):
        """Create sample user profiles"""
        users_data = [
            {
                'telegram_id': '123456789',
                'language': 'en',
                'latitude': 9.0054,
                'longitude': 38.7636,
                'location_permission_granted': True,
                'data_consent': True,
            },
            {
                'telegram_id': '234567890',
                'language': 'am',
                'latitude': 9.0365,
                'longitude': 38.7578,
                'location_permission_granted': True,
                'data_consent': True,
            },
            {
                'telegram_id': '345678901',
                'language': 'om',
                'latitude': 8.9806,
                'longitude': 38.7578,
                'location_permission_granted': False,
                'data_consent': True,
            },
            {
                'telegram_id': '456789012',
                'language': 'en',
                'latitude': 9.0123,
                'longitude': 38.7456,
                'location_permission_granted': True,
                'data_consent': False,
            },
            {
                'telegram_id': '567890123',
                'language': 'am',
                'latitude': 8.9890,
                'longitude': 38.7890,
                'location_permission_granted': True,
                'data_consent': True,
            },
            {
                'telegram_id': '678901234',
                'language': 'om',
                'latitude': 9.0200,
                'longitude': 38.7600,
                'location_permission_granted': False,
                'data_consent': True,
            },
        ]

        users = []
        for user_data in users_data:
            user = UserProfile.objects.create(**user_data)
            if user.location_permission_granted:
                user.update_location(user_data['latitude'], user_data['longitude'])
            if user.data_consent:
                user.grant_consent()
            users.append(user)

        return users

    def create_agencies(self):
        """Create sample agencies"""
        agencies_data = [
            # Police Stations
            {
                'name': 'Bole Police Station',
                'type': 'police',
                'description': 'Main police station serving the Bole area with 24/7 emergency response.',
                'region': 'Addis Ababa',
                'zone': 'Bole',
                'woreda': '03',
                'kebele': '07',
                'phone': '+251114670001',
                'alt_phone': '+251911123456',
                'email': 'bole.police@addisababa.gov.et',
                'address': 'Bole Road, near Edna Mall, Addis Ababa',
                'latitude': 8.9936,
                'longitude': 38.7870,
                'hours_of_operation': '24/7',
                'services': 'Emergency response, crime reporting, investigation, traffic control',
                'verified': True,
            },
            {
                'name': 'Arada Police Station',
                'type': 'police',
                'description': 'Central police station in Arada sub-city serving Piazza area.',
                'region': 'Addis Ababa',
                'zone': 'Arada',
                'woreda': '02',
                'kebele': '01',
                'phone': '+251114456001',
                'alt_phone': '+251911234567',
                'email': 'arada.police@addisababa.gov.et',
                'address': 'Piazza, Churchill Avenue, Addis Ababa',
                'latitude': 9.0370,
                'longitude': 38.7510,
                'hours_of_operation': '24/7',
                'services': 'Law enforcement, emergency response, crime investigation',
                'verified': True,
            },
            {
                'name': 'Kirkos Police Station',
                'type': 'police',
                'description': 'Police station serving Kirkos sub-city and surrounding areas.',
                'region': 'Addis Ababa',
                'zone': 'Kirkos',
                'woreda': '01',
                'kebele': '05',
                'phone': '+251114789001',
                'alt_phone': '+251911345678',
                'email': 'kirkos.police@addisababa.gov.et',
                'address': 'Mexico Square, Kirkos, Addis Ababa',
                'latitude': 9.0125,
                'longitude': 38.7425,
                'hours_of_operation': '24/7',
                'services': 'Emergency services, patrol, community policing',
                'verified': True,
            },
            
            # Hospitals
            {
                'name': 'Black Lion Hospital',
                'type': 'hospital',
                'description': 'Major referral hospital with comprehensive emergency services.',
                'region': 'Addis Ababa',
                'zone': 'Lideta',
                'woreda': '07',
                'kebele': '02',
                'phone': '+251115517011',
                'alt_phone': '+251911456789',
                'email': 'emergency@blacklion.gov.et',
                'address': 'Arat Kilo, near Addis Ababa University, Addis Ababa',
                'latitude': 9.0417,
                'longitude': 38.7612,
                'hours_of_operation': '24/7 Emergency, 8:00-17:00 Regular services',
                'services': 'Emergency medicine, surgery, trauma care, obstetrics, pediatrics',
                'verified': True,
            },
            {
                'name': 'St. Paul Hospital',
                'type': 'hospital',
                'description': 'Specialized hospital with excellent emergency and maternity services.',
                'region': 'Addis Ababa',
                'zone': 'Gulele',
                'woreda': '09',
                'kebele': '04',
                'phone': '+251115533666',
                'alt_phone': '+251911567890',
                'email': 'info@stpaul.gov.et',
                'address': 'Gulele, near Entoto Road, Addis Ababa',
                'latitude': 9.0736,
                'longitude': 38.7599,
                'hours_of_operation': '24/7 Emergency, 8:00-16:30 Regular services',
                'services': 'Emergency care, maternity, surgery, internal medicine',
                'verified': True,
            },
            {
                'name': 'Zewditu Memorial Hospital',
                'type': 'hospital',
                'description': 'Public hospital providing comprehensive medical services.',
                'region': 'Addis Ababa',
                'zone': 'Arada',
                'woreda': '01',
                'kebele': '03',
                'phone': '+251115513355',
                'alt_phone': '+251911678901',
                'email': 'info@zewditu.gov.et',
                'address': 'Arada, near Red Cross, Addis Ababa',
                'latitude': 9.0298,
                'longitude': 38.7478,
                'hours_of_operation': '24/7 Emergency, 8:00-17:00 Outpatient',
                'services': 'General medicine, emergency care, laboratory, radiology',
                'verified': True,
            },
            
            # NGO/Support Organizations
            {
                'name': 'Ethiopian Women Lawyers Association',
                'type': 'ngo',
                'description': 'Legal aid and support for women facing gender-based violence.',
                'region': 'Addis Ababa',
                'zone': 'Bole',
                'woreda': '05',
                'kebele': '08',
                'phone': '+251115505050',
                'alt_phone': '+251911789012',
                'email': 'info@ewla.org.et',
                'address': 'Bole Sub-city, Atlas Hotel Area, Addis Ababa',
                'latitude': 8.9978,
                'longitude': 38.7854,
                'hours_of_operation': 'Mon-Fri 8:30-17:30, Emergency hotline 24/7',
                'services': 'Legal aid, counseling, advocacy, shelter referrals, court support',
                'verified': True,
            },
            {
                'name': 'Association for Women in Development',
                'type': 'ngo',
                'description': 'Support services for women and children in crisis situations.',
                'region': 'Addis Ababa',
                'zone': 'Kirkos',
                'woreda': '03',
                'kebele': '07',
                'phone': '+251115454545',
                'alt_phone': '+251911890123',
                'email': 'support@awid.org.et',
                'address': 'Kirkos, near Stadium, Addis Ababa',
                'latitude': 9.0089,
                'longitude': 38.7398,
                'hours_of_operation': 'Mon-Fri 8:00-17:00, Hotline 24/7',
                'services': 'Psychosocial support, economic empowerment, emergency assistance',
                'verified': True,
            },
            
            # Government Offices
            {
                'name': 'Women and Children Affairs Bureau',
                'type': 'government',
                'description': 'Government office handling women and children protection cases.',
                'region': 'Addis Ababa',
                'zone': 'Addis Ketema',
                'woreda': '05',
                'kebele': '02',
                'phone': '+251115252525',
                'alt_phone': '+251911901234',
                'email': 'info@wcab.addis.gov.et',
                'address': 'Addis Ketema, near City Hall, Addis Ababa',
                'latitude': 9.0245,
                'longitude': 38.7523,
                'hours_of_operation': 'Mon-Fri 8:30-17:30',
                'services': 'Child protection, women affairs, family mediation, legal support',
                'verified': True,
            },
            
            # Shelters
            {
                'name': 'Safe Haven Women Shelter',
                'type': 'shelter',
                'description': 'Emergency shelter and rehabilitation center for women in crisis.',
                'region': 'Addis Ababa',
                'zone': 'Nifas Silk',
                'woreda': '02',
                'kebele': '06',
                'phone': '+251115606060',
                'alt_phone': '+251912012345',
                'email': 'intake@safehaven.org.et',
                'address': 'Nifas Silk, Confidential Location, Addis Ababa',
                'latitude': 8.9567,
                'longitude': 38.7234,
                'hours_of_operation': '24/7 Admission, Support services 8:00-18:00',
                'services': 'Emergency shelter, counseling, legal aid, skills training, childcare',
                'verified': True,
            },
        ]

        agencies = []
        for agency_data in agencies_data:
            agency = Agency.objects.create(**agency_data)
            agencies.append(agency)

        return agencies

    def create_reports(self, users):
        """Create sample incident reports"""
        incident_types = ['rape', 'assault', 'domestic_violence', 'harassment', 'other']
        status_choices = ['submitted', 'processing', 'resolved', 'closed']
        
        descriptions = {
            'rape': [
                'Incident occurred late at night while walking home',
                'Attacked by unknown person in isolated area',
                'Need immediate medical and legal assistance',
                'Incident reported to seek justice and support',
                'Seeking help and counseling services'
            ],
            'assault': [
                'Physical attack by known individual',
                'Unprovoked assault in public place',
                'Sustained injuries requiring medical attention',
                'Witness assault on another person',
                'Group attack in neighborhood area'
            ],
            'domestic_violence': [
                'Ongoing abuse at home by family member',
                'Physical violence by intimate partner',
                'Escalating threats and intimidation',
                'Children also at risk in household',
                'Need immediate safe accommodation'
            ],
            'harassment': [
                'Persistent unwanted contact and messages',
                'Workplace harassment by supervisor',
                'Street harassment while commuting',
                'Online harassment and threats',
                'Stalking behavior causing fear'
            ],
            'other': [
                'Suspicious activity in neighborhood',
                'Feeling unsafe due to recent incidents',
                'Witnessed crime but afraid to report elsewhere',
                'Need information about safety resources',
                'General safety concerns for family'
            ]
        }

        reports = []
        for i in range(12):  # Create 12 reports
            user = random.choice(users)
            incident_type = random.choice(incident_types)
            description = random.choice(descriptions[incident_type])
            
            # Generate location near user's location if they have one
            if user.latitude and user.longitude:
                lat_offset = random.uniform(-0.01, 0.01)
                lng_offset = random.uniform(-0.01, 0.01)
                latitude = user.latitude + lat_offset
                longitude = user.longitude + lng_offset
                location = f"GPS: {latitude}, {longitude}"
            else:
                # Default Addis Ababa coordinates
                latitude = 9.0054 + random.uniform(-0.05, 0.05)
                longitude = 38.7636 + random.uniform(-0.05, 0.05)
                location = f"GPS: {latitude}, {longitude}"

            # Create report with some submitted in the past
            submitted_at = timezone.now() - timedelta(days=random.randint(0, 30))
            
            report = IncidentReport.objects.create(
                user=user,
                type=incident_type,
                description=description,
                location=location,
                latitude=latitude,
                longitude=longitude,
                status=random.choice(status_choices),
                submitted_at=submitted_at,
                ip_address=f"192.168.1.{random.randint(1, 255)}",
                device_info=random.choice([
                    'Telegram/Android 12',
                    'Telegram/iOS 16.2',
                    'Telegram/Android 11',
                    'Telegram/iOS 15.5'
                ])
            )
            reports.append(report)

        return reports

    def create_notifications(self, users, reports, agencies):
        """Create sample notifications"""
        notification_types = ['report_status', 'nearby_agency', 'system', 'safety_tip']
        priorities = ['low', 'medium', 'high', 'urgent']
        
        notification_data = {
            'report_status': [
                ('Report Received', 'Your incident report has been received and assigned ID #{report_id}'),
                ('Report Under Review', 'Your report is currently being reviewed by our team'),
                ('Additional Information Needed', 'Please provide additional details for your report'),
                ('Report Resolved', 'Your incident report has been successfully resolved'),
                ('Report Closed', 'Your report has been closed. Contact us if you need further assistance'),
            ],
            'nearby_agency': [
                ('Emergency Services Nearby', 'A police station is located 0.5km from your current location'),
                ('Hospital Alert', 'Black Lion Hospital is the nearest medical facility to you'),
                ('Support Center Available', 'Women support services available within 1km of your area'),
                ('Legal Aid Office', 'Legal assistance is available at nearby women lawyers association'),
                ('Shelter Information', 'Emergency shelter services are available in your area'),
            ],
            'system': [
                ('System Maintenance', 'The system will undergo maintenance tonight from 2-4 AM'),
                ('New Feature Available', 'Voice recording feature is now available for reports'),
                ('Language Support Added', 'The app now supports Afaan Oromo language'),
                ('Privacy Update', 'Our privacy policy has been updated to better protect your data'),
                ('Security Enhancement', 'New security measures have been implemented for your protection'),
            ],
            'safety_tip': [
                ('Personal Safety Tip', 'Always inform someone you trust about your whereabouts when going out'),
                ('Digital Safety', 'Keep your personal information private on social media platforms'),
                ('Emergency Contacts', 'Keep emergency contact numbers easily accessible on your phone'),
                ('Safe Transportation', 'Use reliable transportation and avoid traveling alone at night'),
                ('Home Security', 'Ensure your doors and windows are properly secured when at home'),
            ]
        }

        notifications = []
        for i in range(20):  # Create 20 notifications
            user = random.choice(users)
            notification_type = random.choice(notification_types)
            title, message_template = random.choice(notification_data[notification_type])
            
            # Customize message based on type
            if notification_type == 'report_status' and reports:
                related_report = random.choice([r for r in reports if r.user == user] or [random.choice(reports)])
                message = message_template.format(report_id=str(related_report.id)[:8])
            else:
                related_report = None
                message = message_template

            # Randomly assign related agency for nearby_agency notifications
            related_agency = None
            if notification_type == 'nearby_agency':
                related_agency = random.choice(agencies)

            # Create notification with some in the past
            created_at = timezone.now() - timedelta(hours=random.randint(0, 72))
            
            notification = Notification.objects.create(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=random.choice(priorities),
                related_report=related_report,
                related_agency=related_agency,
                is_read=random.choice([True, False]),
                is_sent=True,
                created_at=created_at
            )
            
            # Mark as read for some notifications
            if notification.is_read:
                notification.read_at = created_at + timedelta(minutes=random.randint(5, 120))
                notification.save(update_fields=['read_at'])

            notifications.append(notification)

        return notifications

    def create_notification_channels(self, users):
        """Create notification channels for users"""
        channel_types = ['telegram', 'websocket', 'email']
        
        channels = []
        for user in users:
            # Create telegram channel for all users
            telegram_channel = NotificationChannel.objects.create(
                user=user,
                channel_type='telegram',
                is_enabled=True,
                telegram_chat_id=user.telegram_id
            )
            channels.append(telegram_channel)
            
            # Create websocket channel for most users
            if random.choice([True, True, False]):  # 2/3 probability
                websocket_channel = NotificationChannel.objects.create(
                    user=user,
                    channel_type='websocket',
                    is_enabled=True
                )
                channels.append(websocket_channel)
            
            # Create email channel for some users
            if random.choice([True, False]):  # 1/2 probability
                email_channel = NotificationChannel.objects.create(
                    user=user,
                    channel_type='email',
                    is_enabled=random.choice([True, False]),
                    email_address=f"user{user.telegram_id}@example.com"
                )
                channels.append(email_channel)

        return channels